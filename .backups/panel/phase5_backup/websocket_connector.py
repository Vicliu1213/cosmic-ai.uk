#!/usr/bin/env python3
"""
WebSocket Connector Module
WebSocket連接器模組

Provides real-time market data streaming for multiple crypto exchanges:
- Binance WebSocket
- Kraken WebSocket
- Coinbase WebSocket

This module handles:
1. WebSocket connection management
2. Real-time price stream subscriptions
3. Trade event notifications
4. Order book snapshot updates
5. Reconnection logic and error handling
6. Message parsing and data normalization
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
import threading
import time
from queue import Queue, Empty

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    websockets = None
    WebSocketClientProtocol = None

# ============================================================================
# Constants & Enums
# ============================================================================

class WebSocketStatus(Enum):
    """WebSocket connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    CLOSED = "closed"


class StreamType(Enum):
    """Types of real-time data streams."""
    TICKER = "ticker"  # Real-time price updates
    TRADE = "trade"  # Trade executions
    ORDER_BOOK = "order_book"  # Order book updates
    USER = "user"  # User account updates (orders, fills)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TickerData:
    """Real-time ticker price data."""
    symbol: str
    exchange: str
    timestamp: datetime
    bid: float
    ask: float
    last_price: float
    volume_24h: float
    high_24h: float
    low_24h: float
    change_24h: float
    change_percent_24h: float
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeData:
    """Real-time trade execution data."""
    symbol: str
    exchange: str
    timestamp: datetime
    trade_id: str
    price: float
    quantity: float
    side: str  # "buy" or "sell"
    maker: bool  # True if maker, False if taker
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrderBookUpdate:
    """Order book snapshot update."""
    symbol: str
    exchange: str
    timestamp: datetime
    bids: List[Tuple[float, float]]  # [(price, quantity), ...]
    asks: List[Tuple[float, float]]  # [(price, quantity), ...]
    sequence: int = 0  # For ordering updates
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserUpdate:
    """User account update (orders, fills, balances)."""
    exchange: str
    timestamp: datetime
    update_type: str  # "order_update", "fill", "balance_update"
    symbol: Optional[str] = None
    order_id: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebSocketConfig:
    """Configuration for WebSocket connection."""
    exchange: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    reconnect_attempts: int = 10
    reconnect_delay: float = 1.0
    heartbeat_interval: float = 30.0
    message_timeout: float = 10.0
    max_reconnect_delay: float = 60.0


# ============================================================================
# Base WebSocket Connector
# ============================================================================

class BaseWebSocketConnector(ABC):
    """Abstract base class for exchange WebSocket connectors."""

    def __init__(self, config: WebSocketConfig):
        """Initialize WebSocket connector.
        
        Args:
            config: WebSocket configuration
        """
        self.config = config
        self.status = WebSocketStatus.DISCONNECTED
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.subscriptions: Set[str] = set()
        self.message_queue: Queue = Queue()
        self.callbacks: Dict[StreamType, List[Callable]] = {
            StreamType.TICKER: [],
            StreamType.TRADE: [],
            StreamType.ORDER_BOOK: [],
            StreamType.USER: []
        }
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._reconnect_count = 0
        self._last_heartbeat = time.time()
        self._receive_thread: Optional[threading.Thread] = None
        self._running = False

    @abstractmethod
    async def _get_websocket_url(self) -> str:
        """Get WebSocket URL for the exchange.
        
        Returns:
            WebSocket URL
        """
        pass

    @abstractmethod
    async def _parse_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse incoming WebSocket message.
        
        Args:
            message: Raw message from WebSocket
            
        Returns:
            Parsed message dict or None
        """
        pass

    @abstractmethod
    async def _handle_message(self, parsed_msg: Dict[str, Any]) -> None:
        """Handle parsed WebSocket message.
        
        Args:
            parsed_msg: Parsed message
        """
        pass

    @abstractmethod
    async def _subscribe_to_stream(self, stream_type: StreamType, 
                                   symbol: str) -> None:
        """Subscribe to a data stream.
        
        Args:
            stream_type: Type of stream to subscribe to
            symbol: Trading symbol
        """
        pass

    @abstractmethod
    async def _unsubscribe_from_stream(self, stream_type: StreamType,
                                       symbol: str) -> None:
        """Unsubscribe from a data stream.
        
        Args:
            stream_type: Type of stream to unsubscribe from
            symbol: Trading symbol
        """
        pass

    async def connect(self) -> bool:
        """Connect to WebSocket.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if websockets is None:
                self.logger.error("websockets library not installed")
                return False

            self.status = WebSocketStatus.CONNECTING
            ws_url = await self._get_websocket_url()
            
            self.websocket = await asyncio.wait_for(
                websockets.connect(ws_url),
                timeout=self.config.message_timeout
            )
            
            self.status = WebSocketStatus.CONNECTED
            self._reconnect_count = 0
            self._running = True
            
            self.logger.info(f"Connected to {self.config.exchange} WebSocket")
            
            # Start receive loop
            asyncio.create_task(self._receive_loop())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            self.status = WebSocketStatus.ERROR
            return False

    async def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        self._running = False
        self.subscriptions.clear()
        
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")
        
        self.websocket = None
        self.status = WebSocketStatus.DISCONNECTED
        self.logger.info(f"Disconnected from {self.config.exchange} WebSocket")

    async def subscribe(self, stream_type: StreamType, symbol: str) -> None:
        """Subscribe to a data stream.
        
        Args:
            stream_type: Type of stream
            symbol: Trading symbol
        """
        subscription_key = f"{stream_type.value}:{symbol}"
        
        if subscription_key not in self.subscriptions:
            try:
                await self._subscribe_to_stream(stream_type, symbol)
                self.subscriptions.add(subscription_key)
                self.logger.info(f"Subscribed to {subscription_key}")
            except Exception as e:
                self.logger.error(f"Failed to subscribe to {subscription_key}: {e}")

    async def unsubscribe(self, stream_type: StreamType, symbol: str) -> None:
        """Unsubscribe from a data stream.
        
        Args:
            stream_type: Type of stream
            symbol: Trading symbol
        """
        subscription_key = f"{stream_type.value}:{symbol}"
        
        if subscription_key in self.subscriptions:
            try:
                await self._unsubscribe_from_stream(stream_type, symbol)
                self.subscriptions.discard(subscription_key)
                self.logger.info(f"Unsubscribed from {subscription_key}")
            except Exception as e:
                self.logger.error(f"Failed to unsubscribe from {subscription_key}: {e}")

    def add_callback(self, stream_type: StreamType, callback: Callable) -> None:
        """Add callback for stream type.
        
        Args:
            stream_type: Type of stream
            callback: Callback function to invoke
        """
        self.callbacks[stream_type].append(callback)

    def remove_callback(self, stream_type: StreamType, callback: Callable) -> None:
        """Remove callback for stream type.
        
        Args:
            stream_type: Type of stream
            callback: Callback function to remove
        """
        if callback in self.callbacks[stream_type]:
            self.callbacks[stream_type].remove(callback)

    async def _receive_loop(self) -> None:
        """Main receive loop for WebSocket messages."""
        try:
            while self._running and self.websocket:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=self.config.message_timeout
                    )
                    
                    # Parse and handle message
                    parsed_msg = await self._parse_message(message)
                    if parsed_msg:
                        await self._handle_message(parsed_msg)
                    
                    self._last_heartbeat = time.time()
                    
                except asyncio.TimeoutError:
                    # Check if we need to reconnect
                    if time.time() - self._last_heartbeat > self.config.heartbeat_interval * 2:
                        self.logger.warning("Heartbeat timeout, reconnecting...")
                        await self._reconnect()
                        
                except Exception as e:
                    self.logger.error(f"Error in receive loop: {e}")
                    await self._reconnect()
                    
        except Exception as e:
            self.logger.error(f"Fatal error in receive loop: {e}")
            self.status = WebSocketStatus.ERROR

    async def _reconnect(self) -> None:
        """Attempt to reconnect to WebSocket."""
        if self._reconnect_count >= self.config.reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            self.status = WebSocketStatus.ERROR
            await self.disconnect()
            return

        self.status = WebSocketStatus.RECONNECTING
        self._reconnect_count += 1
        
        # Calculate backoff delay
        delay = min(
            self.config.reconnect_delay * (2 ** (self._reconnect_count - 1)),
            self.config.max_reconnect_delay
        )
        
        self.logger.info(f"Attempting reconnection {self._reconnect_count}/{self.config.reconnect_attempts} in {delay}s")
        await asyncio.sleep(delay)
        
        # Disconnect and reconnect
        await self.disconnect()
        
        if await self.connect():
            # Resubscribe to streams
            for subscription_key in list(self.subscriptions):
                parts = subscription_key.split(":")
                if len(parts) == 2:
                    stream_type_str, symbol = parts
                    stream_type = StreamType(stream_type_str)
                    await self._subscribe_to_stream(stream_type, symbol)

    async def _invoke_callbacks(self, stream_type: StreamType, data: Any) -> None:
        """Invoke callbacks for stream type.
        
        Args:
            stream_type: Type of stream
            data: Data to pass to callbacks
        """
        for callback in self.callbacks[stream_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                self.logger.error(f"Error invoking callback: {e}")

    def get_status(self) -> WebSocketStatus:
        """Get current WebSocket status.
        
        Returns:
            Current status
        """
        return self.status

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# ============================================================================
# Binance WebSocket Connector
# ============================================================================

class BinanceWebSocketConnector(BaseWebSocketConnector):
    """Binance WebSocket connector for real-time market data."""

    async def _get_websocket_url(self) -> str:
        """Get Binance WebSocket URL."""
        return "wss://stream.binance.com:9443/ws"

    async def _parse_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse Binance WebSocket message."""
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse message: {message}")
            return None

    async def _handle_message(self, parsed_msg: Dict[str, Any]) -> None:
        """Handle parsed Binance message."""
        msg_type = parsed_msg.get("e")

        if msg_type == "24hrTicker":
            await self._handle_ticker(parsed_msg)
        elif msg_type == "trade":
            await self._handle_trade(parsed_msg)
        elif msg_type == "depthUpdate":
            await self._handle_order_book(parsed_msg)

    async def _handle_ticker(self, msg: Dict[str, Any]) -> None:
        """Handle ticker update."""
        try:
            ticker = TickerData(
                symbol=msg["s"],
                exchange="binance",
                timestamp=datetime.fromtimestamp(msg["E"] / 1000, tz=timezone.utc),
                bid=float(msg["b"]),
                ask=float(msg["a"]),
                last_price=float(msg["c"]),
                volume_24h=float(msg["v"]),
                high_24h=float(msg["h"]),
                low_24h=float(msg["l"]),
                change_24h=float(msg["p"]),
                change_percent_24h=float(msg["P"]),
                raw_data=msg
            )
            await self._invoke_callbacks(StreamType.TICKER, ticker)
        except Exception as e:
            self.logger.error(f"Error handling ticker: {e}")

    async def _handle_trade(self, msg: Dict[str, Any]) -> None:
        """Handle trade update."""
        try:
            trade = TradeData(
                symbol=msg["s"],
                exchange="binance",
                timestamp=datetime.fromtimestamp(msg["T"] / 1000, tz=timezone.utc),
                trade_id=str(msg["t"]),
                price=float(msg["p"]),
                quantity=float(msg["q"]),
                side="buy" if msg["m"] is False else "sell",
                maker=not msg["m"],
                raw_data=msg
            )
            await self._invoke_callbacks(StreamType.TRADE, trade)
        except Exception as e:
            self.logger.error(f"Error handling trade: {e}")

    async def _handle_order_book(self, msg: Dict[str, Any]) -> None:
        """Handle order book update."""
        try:
            bids = [(float(price), float(qty)) for price, qty in msg.get("b", [])]
            asks = [(float(price), float(qty)) for price, qty in msg.get("a", [])]
            
            ob = OrderBookUpdate(
                symbol=msg["s"],
                exchange="binance",
                timestamp=datetime.fromtimestamp(msg["E"] / 1000, tz=timezone.utc),
                bids=bids,
                asks=asks,
                sequence=msg.get("U", 0),
                raw_data=msg
            )
            await self._invoke_callbacks(StreamType.ORDER_BOOK, ob)
        except Exception as e:
            self.logger.error(f"Error handling order book: {e}")

    async def _subscribe_to_stream(self, stream_type: StreamType,
                                   symbol: str) -> None:
        """Subscribe to Binance stream."""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")

        stream_names = {
            StreamType.TICKER: f"{symbol.lower()}@ticker",
            StreamType.TRADE: f"{symbol.lower()}@trade",
            StreamType.ORDER_BOOK: f"{symbol.lower()}@depth@100ms",
        }

        if stream_type == StreamType.USER:
            raise NotImplementedError("User stream subscription not yet implemented")

        stream_name = stream_names.get(stream_type)
        if not stream_name:
            raise ValueError(f"Unsupported stream type: {stream_type}")

        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [stream_name],
            "id": int(time.time() * 1000)
        }

        await self.websocket.send(json.dumps(subscribe_msg))

    async def _unsubscribe_from_stream(self, stream_type: StreamType,
                                       symbol: str) -> None:
        """Unsubscribe from Binance stream."""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")

        stream_names = {
            StreamType.TICKER: f"{symbol.lower()}@ticker",
            StreamType.TRADE: f"{symbol.lower()}@trade",
            StreamType.ORDER_BOOK: f"{symbol.lower()}@depth@100ms",
        }

        stream_name = stream_names.get(stream_type)
        if not stream_name:
            raise ValueError(f"Unsupported stream type: {stream_type}")

        unsubscribe_msg = {
            "method": "UNSUBSCRIBE",
            "params": [stream_name],
            "id": int(time.time() * 1000)
        }

        await self.websocket.send(json.dumps(unsubscribe_msg))


# ============================================================================
# Kraken WebSocket Connector
# ============================================================================

class KrakenWebSocketConnector(BaseWebSocketConnector):
    """Kraken WebSocket connector for real-time market data."""

    def __init__(self, config: WebSocketConfig):
        """Initialize Kraken connector."""
        super().__init__(config)
        self._subscription_id = 0

    async def _get_websocket_url(self) -> str:
        """Get Kraken WebSocket URL."""
        return "wss://ws.kraken.com"

    async def _parse_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse Kraken WebSocket message."""
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse message: {message}")
            return None

    async def _handle_message(self, parsed_msg: Dict[str, Any]) -> None:
        """Handle parsed Kraken message."""
        if isinstance(parsed_msg, dict):
            if "event" in parsed_msg:
                # System message
                await self._handle_system_message(parsed_msg)
            else:
                # Data message
                await self._handle_data_message(parsed_msg)

    async def _handle_system_message(self, msg: Dict[str, Any]) -> None:
        """Handle Kraken system message."""
        event = msg.get("event")
        if event == "subscriptionStatus":
            status = msg.get("status")
            if status == "error":
                self.logger.error(f"Subscription error: {msg.get('errorMessage')}")

    async def _handle_data_message(self, msg: Any) -> None:
        """Handle Kraken data message."""
        try:
            # Kraken sends array-format messages
            if isinstance(msg, list) and len(msg) >= 2:
                channel_name = msg[-1]
                
                if "ticker" in channel_name:
                    await self._handle_ticker_message(msg)
                elif "trade" in channel_name:
                    await self._handle_trade_message(msg)
                elif "book" in channel_name:
                    await self._handle_book_message(msg)
        except Exception as e:
            self.logger.error(f"Error handling data message: {e}")

    async def _handle_ticker_message(self, msg: Any) -> None:
        """Handle Kraken ticker message."""
        try:
            channel_parts = msg[-1].split(",")
            symbol = channel_parts[0]
            
            ticker_data = msg[1]
            if isinstance(ticker_data, dict):
                ticker = TickerData(
                    symbol=symbol,
                    exchange="kraken",
                    timestamp=datetime.now(tz=timezone.utc),
                    bid=float(ticker_data.get("b", [0])[0]),
                    ask=float(ticker_data.get("a", [0])[0]),
                    last_price=float(ticker_data.get("c", [0])[0]),
                    volume_24h=float(ticker_data.get("v", [0])[0]),
                    high_24h=float(ticker_data.get("h", [0])[0]),
                    low_24h=float(ticker_data.get("l", [0])[0]),
                    change_24h=float(ticker_data.get("p", [0])[0]),
                    change_percent_24h=float(ticker_data.get("p", [1])[0]) if len(ticker_data.get("p", [])) > 1 else 0.0,
                    raw_data=msg
                )
                await self._invoke_callbacks(StreamType.TICKER, ticker)
        except Exception as e:
            self.logger.error(f"Error handling Kraken ticker: {e}")

    async def _handle_trade_message(self, msg: Any) -> None:
        """Handle Kraken trade message."""
        try:
            channel_parts = msg[-1].split(",")
            symbol = channel_parts[0]
            
            trades = msg[1]
            if isinstance(trades, list):
                for trade_data in trades:
                    if isinstance(trade_data, list) and len(trade_data) >= 5:
                        trade = TradeData(
                            symbol=symbol,
                            exchange="kraken",
                            timestamp=datetime.fromtimestamp(float(trade_data[2]), tz=timezone.utc),
                            trade_id=f"{symbol}_{trade_data[2]}",
                            price=float(trade_data[0]),
                            quantity=float(trade_data[1]),
                            side="buy" if trade_data[3] == "b" else "sell",
                            maker=trade_data[4] == "m",
                            raw_data=trade_data
                        )
                        await self._invoke_callbacks(StreamType.TRADE, trade)
        except Exception as e:
            self.logger.error(f"Error handling Kraken trade: {e}")

    async def _handle_book_message(self, msg: Any) -> None:
        """Handle Kraken order book message."""
        try:
            channel_parts = msg[-1].split(",")
            symbol = channel_parts[0]
            
            book_data = msg[1]
            if isinstance(book_data, dict):
                bids = [(float(price), float(qty)) for price, qty in book_data.get("bs", [])]
                asks = [(float(price), float(qty)) for price, qty in book_data.get("as", [])]
                
                ob = OrderBookUpdate(
                    symbol=symbol,
                    exchange="kraken",
                    timestamp=datetime.now(tz=timezone.utc),
                    bids=bids,
                    asks=asks,
                    raw_data=msg
                )
                await self._invoke_callbacks(StreamType.ORDER_BOOK, ob)
        except Exception as e:
            self.logger.error(f"Error handling Kraken order book: {e}")

    async def _subscribe_to_stream(self, stream_type: StreamType,
                                   symbol: str) -> None:
        """Subscribe to Kraken stream."""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")

        self._subscription_id += 1

        subscription_types = {
            StreamType.TICKER: "ticker",
            StreamType.TRADE: "trade",
            StreamType.ORDER_BOOK: "book",
        }

        if stream_type == StreamType.USER:
            raise NotImplementedError("User stream subscription not yet implemented")

        sub_type = subscription_types.get(stream_type)
        if not sub_type:
            raise ValueError(f"Unsupported stream type: {stream_type}")

        subscribe_msg = {
            "event": "subscribe",
            "subscription": {"name": sub_type},
            "pair": [symbol]
        }

        await self.websocket.send(json.dumps(subscribe_msg))

    async def _unsubscribe_from_stream(self, stream_type: StreamType,
                                       symbol: str) -> None:
        """Unsubscribe from Kraken stream."""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")

        subscription_types = {
            StreamType.TICKER: "ticker",
            StreamType.TRADE: "trade",
            StreamType.ORDER_BOOK: "book",
        }

        sub_type = subscription_types.get(stream_type)
        if not sub_type:
            raise ValueError(f"Unsupported stream type: {stream_type}")

        unsubscribe_msg = {
            "event": "unsubscribe",
            "subscription": {"name": sub_type},
            "pair": [symbol]
        }

        await self.websocket.send(json.dumps(unsubscribe_msg))


# ============================================================================
# Coinbase WebSocket Connector
# ============================================================================

class CoinbaseWebSocketConnector(BaseWebSocketConnector):
    """Coinbase WebSocket connector for real-time market data."""

    async def _get_websocket_url(self) -> str:
        """Get Coinbase WebSocket URL."""
        return "wss://advanced-trade-ws.coinbase.com"

    async def _parse_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Parse Coinbase WebSocket message."""
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse message: {message}")
            return None

    async def _handle_message(self, parsed_msg: Dict[str, Any]) -> None:
        """Handle parsed Coinbase message."""
        msg_type = parsed_msg.get("type")

        if msg_type == "ticker":
            await self._handle_ticker(parsed_msg)
        elif msg_type == "match":
            await self._handle_trade(parsed_msg)
        elif msg_type == "snapshot" or msg_type == "l2update":
            await self._handle_order_book(parsed_msg)

    async def _handle_ticker(self, msg: Dict[str, Any]) -> None:
        """Handle Coinbase ticker update."""
        try:
            ticker = TickerData(
                symbol=msg["product_id"],
                exchange="coinbase",
                timestamp=datetime.fromisoformat(msg["time"].replace("Z", "+00:00")),
                bid=float(msg.get("best_bid", 0)),
                ask=float(msg.get("best_ask", 0)),
                last_price=float(msg.get("price", 0)),
                volume_24h=0.0,  # Not provided in ticker
                high_24h=0.0,    # Not provided in ticker
                low_24h=0.0,     # Not provided in ticker
                change_24h=0.0,  # Not provided in ticker
                change_percent_24h=0.0,  # Not provided in ticker
                raw_data=msg
            )
            await self._invoke_callbacks(StreamType.TICKER, ticker)
        except Exception as e:
            self.logger.error(f"Error handling Coinbase ticker: {e}")

    async def _handle_trade(self, msg: Dict[str, Any]) -> None:
        """Handle Coinbase trade update."""
        try:
            trade = TradeData(
                symbol=msg["product_id"],
                exchange="coinbase",
                timestamp=datetime.fromisoformat(msg["time"].replace("Z", "+00:00")),
                trade_id=msg.get("trade_id", ""),
                price=float(msg.get("price", 0)),
                quantity=float(msg.get("size", 0)),
                side=msg["side"],  # "buy" or "sell"
                maker=msg.get("maker_order_id") is not None,
                raw_data=msg
            )
            await self._invoke_callbacks(StreamType.TRADE, trade)
        except Exception as e:
            self.logger.error(f"Error handling Coinbase trade: {e}")

    async def _handle_order_book(self, msg: Dict[str, Any]) -> None:
        """Handle Coinbase order book update."""
        try:
            if msg["type"] == "snapshot":
                bids = [(float(price), float(qty)) for price, qty in msg.get("bids", [])]
                asks = [(float(price), float(qty)) for price, qty in msg.get("asks", [])]
            else:  # l2update
                changes = msg.get("changes", [])
                bids = [(float(price), float(qty)) for side, price, qty in changes if side == "buy"]
                asks = [(float(price), float(qty)) for side, price, qty in changes if side == "sell"]

            ob = OrderBookUpdate(
                symbol=msg["product_id"],
                exchange="coinbase",
                timestamp=datetime.now(tz=timezone.utc),
                bids=bids,
                asks=asks,
                raw_data=msg
            )
            await self._invoke_callbacks(StreamType.ORDER_BOOK, ob)
        except Exception as e:
            self.logger.error(f"Error handling Coinbase order book: {e}")

    async def _subscribe_to_stream(self, stream_type: StreamType,
                                   symbol: str) -> None:
        """Subscribe to Coinbase stream."""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")

        stream_types = {
            StreamType.TICKER: "ticker",
            StreamType.TRADE: "matches",
            StreamType.ORDER_BOOK: "level2",
        }

        if stream_type == StreamType.USER:
            raise NotImplementedError("User stream subscription not yet implemented")

        sub_type = stream_types.get(stream_type)
        if not sub_type:
            raise ValueError(f"Unsupported stream type: {stream_type}")

        subscribe_msg = {
            "type": "subscribe",
            "product_ids": [symbol],
            "channel": sub_type
        }

        await self.websocket.send(json.dumps(subscribe_msg))

    async def _unsubscribe_from_stream(self, stream_type: StreamType,
                                       symbol: str) -> None:
        """Unsubscribe from Coinbase stream."""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")

        stream_types = {
            StreamType.TICKER: "ticker",
            StreamType.TRADE: "matches",
            StreamType.ORDER_BOOK: "level2",
        }

        sub_type = stream_types.get(stream_type)
        if not sub_type:
            raise ValueError(f"Unsupported stream type: {stream_type}")

        unsubscribe_msg = {
            "type": "unsubscribe",
            "product_ids": [symbol],
            "channel": sub_type
        }

        await self.websocket.send(json.dumps(unsubscribe_msg))


# ============================================================================
# WebSocket Connector Factory
# ============================================================================

class WebSocketConnectorFactory:
    """Factory for creating WebSocket connectors."""

    _connectors = {
        "binance": BinanceWebSocketConnector,
        "kraken": KrakenWebSocketConnector,
        "coinbase": CoinbaseWebSocketConnector,
    }

    @classmethod
    def create(cls, exchange: str, config: WebSocketConfig) -> BaseWebSocketConnector:
        """Create a WebSocket connector for the specified exchange.
        
        Args:
            exchange: Exchange name
            config: WebSocket configuration
            
        Returns:
            WebSocket connector instance
            
        Raises:
            ValueError: If exchange is not supported
        """
        connector_class = cls._connectors.get(exchange.lower())
        if not connector_class:
            raise ValueError(f"Unsupported exchange: {exchange}")
        
        return connector_class(config)

    @classmethod
    def register(cls, exchange: str, connector_class: type) -> None:
        """Register a custom connector.
        
        Args:
            exchange: Exchange name
            connector_class: Connector class
        """
        cls._connectors[exchange.lower()] = connector_class


# Logging setup
logging.basicConfig(level=logging.INFO)
