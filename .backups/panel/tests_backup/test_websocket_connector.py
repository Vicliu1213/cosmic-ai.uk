#!/usr/bin/env python3
"""
WebSocket Connector Tests
WebSocket連接器測試

Comprehensive tests for WebSocket connectors covering:
- Connection management
- Message parsing and handling
- Stream subscriptions
- Callback invocation
- Error handling and reconnection
- Factory pattern
"""

import asyncio
import json
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from src.phase5.websocket_connector import (
    BaseWebSocketConnector,
    BinanceWebSocketConnector,
    KrakenWebSocketConnector,
    CoinbaseWebSocketConnector,
    WebSocketConnectorFactory,
    WebSocketConfig,
    WebSocketStatus,
    StreamType,
    TickerData,
    TradeData,
    OrderBookUpdate,
    UserUpdate,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def binance_config():
    """Create Binance WebSocket configuration."""
    return WebSocketConfig(
        exchange="binance",
        reconnect_attempts=3,
        reconnect_delay=0.1,
        heartbeat_interval=5.0,
        message_timeout=5.0
    )


@pytest.fixture
def kraken_config():
    """Create Kraken WebSocket configuration."""
    return WebSocketConfig(
        exchange="kraken",
        reconnect_attempts=3,
        reconnect_delay=0.1,
        heartbeat_interval=5.0,
        message_timeout=5.0
    )


@pytest.fixture
def coinbase_config():
    """Create Coinbase WebSocket configuration."""
    return WebSocketConfig(
        exchange="coinbase",
        reconnect_attempts=3,
        reconnect_delay=0.1,
        heartbeat_interval=5.0,
        message_timeout=5.0
    )


# ============================================================================
# Binance WebSocket Tests
# ============================================================================

class TestBinanceWebSocketConnector:
    """Test cases for Binance WebSocket connector."""

    @pytest.mark.asyncio
    async def test_binance_websocket_creation(self, binance_config):
        """Test Binance connector creation."""
        connector = BinanceWebSocketConnector(binance_config)
        assert connector is not None
        assert connector.config.exchange == "binance"
        assert connector.status == WebSocketStatus.DISCONNECTED

    @pytest.mark.asyncio
    async def test_binance_get_websocket_url(self, binance_config):
        """Test Binance WebSocket URL generation."""
        connector = BinanceWebSocketConnector(binance_config)
        url = await connector._get_websocket_url()
        assert url == "wss://stream.binance.com:9443/ws"

    @pytest.mark.asyncio
    async def test_binance_parse_message(self, binance_config):
        """Test Binance message parsing."""
        connector = BinanceWebSocketConnector(binance_config)
        
        message_json = json.dumps({"e": "24hrTicker", "s": "BTCUSDT"})
        parsed = await connector._parse_message(message_json)
        
        assert parsed is not None
        assert parsed["e"] == "24hrTicker"
        assert parsed["s"] == "BTCUSDT"

    @pytest.mark.asyncio
    async def test_binance_parse_invalid_message(self, binance_config):
        """Test parsing invalid Binance message."""
        connector = BinanceWebSocketConnector(binance_config)
        
        parsed = await connector._parse_message("invalid json")
        assert parsed is None

    @pytest.mark.asyncio
    async def test_binance_handle_ticker(self, binance_config):
        """Test handling Binance ticker message."""
        connector = BinanceWebSocketConnector(binance_config)
        
        ticker_msg = {
            "e": "24hrTicker",
            "E": 1609459200000,
            "s": "BTCUSDT",
            "b": "45000.00",
            "a": "45001.00",
            "c": "45000.50",
            "v": "1000.00",
            "h": "46000.00",
            "l": "44000.00",
            "p": "1000.00",
            "P": "2.27"
        }
        
        callback_data = []
        connector.add_callback(StreamType.TICKER, lambda data: callback_data.append(data))
        
        await connector._handle_ticker(ticker_msg)
        
        assert len(callback_data) == 1
        ticker = callback_data[0]
        assert isinstance(ticker, TickerData)
        assert ticker.symbol == "BTCUSDT"
        assert ticker.last_price == 45000.50

    @pytest.mark.asyncio
    async def test_binance_handle_trade(self, binance_config):
        """Test handling Binance trade message."""
        connector = BinanceWebSocketConnector(binance_config)
        
        trade_msg = {
            "e": "trade",
            "E": 1609459200000,
            "T": 1609459200000,
            "s": "BTCUSDT",
            "t": 123456,
            "p": "45000.00",
            "q": "1.0",
            "m": False
        }
        
        callback_data = []
        connector.add_callback(StreamType.TRADE, lambda data: callback_data.append(data))
        
        await connector._handle_trade(trade_msg)
        
        assert len(callback_data) == 1
        trade = callback_data[0]
        assert isinstance(trade, TradeData)
        assert trade.symbol == "BTCUSDT"
        assert trade.price == 45000.00
        assert trade.quantity == 1.0

    @pytest.mark.asyncio
    async def test_binance_handle_order_book(self, binance_config):
        """Test handling Binance order book message."""
        connector = BinanceWebSocketConnector(binance_config)
        
        ob_msg = {
            "e": "depthUpdate",
            "E": 1609459200000,
            "s": "BTCUSDT",
            "U": 1,
            "b": [["45000.00", "1.0"], ["44999.00", "2.0"]],
            "a": [["45001.00", "1.5"], ["45002.00", "2.5"]]
        }
        
        callback_data = []
        connector.add_callback(StreamType.ORDER_BOOK, lambda data: callback_data.append(data))
        
        await connector._handle_order_book(ob_msg)
        
        assert len(callback_data) == 1
        ob = callback_data[0]
        assert isinstance(ob, OrderBookUpdate)
        assert len(ob.bids) == 2
        assert len(ob.asks) == 2
        assert ob.bids[0][0] == 45000.00

    @pytest.mark.asyncio
    async def test_binance_callback_management(self, binance_config):
        """Test Binance callback registration and removal."""
        connector = BinanceWebSocketConnector(binance_config)
        
        callback1 = Mock()
        callback2 = Mock()
        
        connector.add_callback(StreamType.TICKER, callback1)
        assert callback1 in connector.callbacks[StreamType.TICKER]
        
        connector.add_callback(StreamType.TICKER, callback2)
        assert len(connector.callbacks[StreamType.TICKER]) == 2
        
        connector.remove_callback(StreamType.TICKER, callback1)
        assert callback1 not in connector.callbacks[StreamType.TICKER]
        assert callback2 in connector.callbacks[StreamType.TICKER]

    @pytest.mark.asyncio
    async def test_binance_status_tracking(self, binance_config):
        """Test Binance status tracking."""
        connector = BinanceWebSocketConnector(binance_config)
        
        assert connector.get_status() == WebSocketStatus.DISCONNECTED
        connector.status = WebSocketStatus.CONNECTING
        assert connector.get_status() == WebSocketStatus.CONNECTING


# ============================================================================
# Kraken WebSocket Tests
# ============================================================================

class TestKrakenWebSocketConnector:
    """Test cases for Kraken WebSocket connector."""

    @pytest.mark.asyncio
    async def test_kraken_websocket_creation(self, kraken_config):
        """Test Kraken connector creation."""
        connector = KrakenWebSocketConnector(kraken_config)
        assert connector is not None
        assert connector.config.exchange == "kraken"

    @pytest.mark.asyncio
    async def test_kraken_get_websocket_url(self, kraken_config):
        """Test Kraken WebSocket URL generation."""
        connector = KrakenWebSocketConnector(kraken_config)
        url = await connector._get_websocket_url()
        assert url == "wss://ws.kraken.com"

    @pytest.mark.asyncio
    async def test_kraken_parse_message(self, kraken_config):
        """Test Kraken message parsing."""
        connector = KrakenWebSocketConnector(kraken_config)
        
        message_json = json.dumps({"event": "subscriptionStatus", "status": "subscribed"})
        parsed = await connector._parse_message(message_json)
        
        assert parsed is not None
        assert parsed["event"] == "subscriptionStatus"

    @pytest.mark.asyncio
    async def test_kraken_handle_system_message(self, kraken_config):
        """Test Kraken system message handling."""
        connector = KrakenWebSocketConnector(kraken_config)
        
        sys_msg = {
            "event": "subscriptionStatus",
            "status": "subscribed",
            "subscription": {"name": "ticker"}
        }
        
        # Should not raise exception
        await connector._handle_system_message(sys_msg)

    @pytest.mark.asyncio
    async def test_kraken_handle_ticker_message(self, kraken_config):
        """Test Kraken ticker message handling."""
        connector = KrakenWebSocketConnector(kraken_config)
        
        ticker_msg = [
            0,
            {
                "b": ["45000.00", 1],
                "a": ["45001.00", 1],
                "c": ["45000.50", 1],
                "v": ["1000.00", "2000.00"],
                "h": ["46000.00", "47000.00"],
                "l": ["44000.00", "43000.00"],
                "p": ["45500.00", "45500.00"],
            },
            "ticker,XBT/USD"
        ]
        
        callback_data = []
        connector.add_callback(StreamType.TICKER, lambda data: callback_data.append(data))
        
        await connector._handle_ticker_message(ticker_msg)
        
        assert len(callback_data) == 1
        ticker = callback_data[0]
        assert isinstance(ticker, TickerData)


# ============================================================================
# Coinbase WebSocket Tests
# ============================================================================

class TestCoinbaseWebSocketConnector:
    """Test cases for Coinbase WebSocket connector."""

    @pytest.mark.asyncio
    async def test_coinbase_websocket_creation(self, coinbase_config):
        """Test Coinbase connector creation."""
        connector = CoinbaseWebSocketConnector(coinbase_config)
        assert connector is not None
        assert connector.config.exchange == "coinbase"

    @pytest.mark.asyncio
    async def test_coinbase_get_websocket_url(self, coinbase_config):
        """Test Coinbase WebSocket URL generation."""
        connector = CoinbaseWebSocketConnector(coinbase_config)
        url = await connector._get_websocket_url()
        assert url == "wss://advanced-trade-ws.coinbase.com"

    @pytest.mark.asyncio
    async def test_coinbase_parse_message(self, coinbase_config):
        """Test Coinbase message parsing."""
        connector = CoinbaseWebSocketConnector(coinbase_config)
        
        message_json = json.dumps({"type": "ticker", "product_id": "BTC-USD"})
        parsed = await connector._parse_message(message_json)
        
        assert parsed is not None
        assert parsed["type"] == "ticker"

    @pytest.mark.asyncio
    async def test_coinbase_handle_ticker(self, coinbase_config):
        """Test Coinbase ticker handling."""
        connector = CoinbaseWebSocketConnector(coinbase_config)
        
        ticker_msg = {
            "type": "ticker",
            "product_id": "BTC-USD",
            "time": "2023-01-01T00:00:00Z",
            "best_bid": "45000.00",
            "best_ask": "45001.00",
            "price": "45000.50"
        }
        
        callback_data = []
        connector.add_callback(StreamType.TICKER, lambda data: callback_data.append(data))
        
        await connector._handle_ticker(ticker_msg)
        
        assert len(callback_data) == 1
        ticker = callback_data[0]
        assert isinstance(ticker, TickerData)
        assert ticker.symbol == "BTC-USD"

    @pytest.mark.asyncio
    async def test_coinbase_handle_trade(self, coinbase_config):
        """Test Coinbase trade handling."""
        connector = CoinbaseWebSocketConnector(coinbase_config)
        
        trade_msg = {
            "type": "match",
            "product_id": "BTC-USD",
            "time": "2023-01-01T00:00:00Z",
            "trade_id": "12345",
            "price": "45000.00",
            "size": "1.0",
            "side": "buy",
            "maker_order_id": "abc"
        }
        
        callback_data = []
        connector.add_callback(StreamType.TRADE, lambda data: callback_data.append(data))
        
        await connector._handle_trade(trade_msg)
        
        assert len(callback_data) == 1
        trade = callback_data[0]
        assert isinstance(trade, TradeData)


# ============================================================================
# WebSocket Factory Tests
# ============================================================================

class TestWebSocketConnectorFactory:
    """Test cases for WebSocket connector factory."""

    def test_factory_create_binance(self, binance_config):
        """Test factory creates Binance connector."""
        connector = WebSocketConnectorFactory.create("binance", binance_config)
        assert isinstance(connector, BinanceWebSocketConnector)

    def test_factory_create_kraken(self, kraken_config):
        """Test factory creates Kraken connector."""
        connector = WebSocketConnectorFactory.create("kraken", kraken_config)
        assert isinstance(connector, KrakenWebSocketConnector)

    def test_factory_create_coinbase(self, coinbase_config):
        """Test factory creates Coinbase connector."""
        connector = WebSocketConnectorFactory.create("coinbase", coinbase_config)
        assert isinstance(connector, CoinbaseWebSocketConnector)

    def test_factory_create_case_insensitive(self, binance_config):
        """Test factory is case insensitive."""
        connector1 = WebSocketConnectorFactory.create("BINANCE", binance_config)
        connector2 = WebSocketConnectorFactory.create("Binance", binance_config)
        
        assert isinstance(connector1, BinanceWebSocketConnector)
        assert isinstance(connector2, BinanceWebSocketConnector)

    def test_factory_unsupported_exchange(self, binance_config):
        """Test factory raises error for unsupported exchange."""
        with pytest.raises(ValueError):
            WebSocketConnectorFactory.create("invalid_exchange", binance_config)

    def test_factory_register_custom_connector(self, binance_config):
        """Test factory custom connector registration."""
        class CustomConnector(BaseWebSocketConnector):
            async def _get_websocket_url(self):
                return "wss://custom.example.com"
            
            async def _parse_message(self, message):
                return json.loads(message)
            
            async def _handle_message(self, parsed_msg):
                pass
            
            async def _subscribe_to_stream(self, stream_type, symbol):
                pass
            
            async def _unsubscribe_from_stream(self, stream_type, symbol):
                pass

        WebSocketConnectorFactory.register("custom", CustomConnector)
        
        connector = WebSocketConnectorFactory.create("custom", binance_config)
        assert isinstance(connector, CustomConnector)


# ============================================================================
# Data Structure Tests
# ============================================================================

class TestWebSocketDataStructures:
    """Test cases for WebSocket data structures."""

    def test_ticker_data_creation(self):
        """Test TickerData creation."""
        ticker = TickerData(
            symbol="BTCUSDT",
            exchange="binance",
            timestamp=datetime.now(tz=timezone.utc),
            bid=45000.0,
            ask=45001.0,
            last_price=45000.50,
            volume_24h=1000.0,
            high_24h=46000.0,
            low_24h=44000.0,
            change_24h=1000.0,
            change_percent_24h=2.27
        )
        
        assert ticker.symbol == "BTCUSDT"
        assert ticker.exchange == "binance"
        assert ticker.bid == 45000.0
        assert ticker.last_price == 45000.50

    def test_trade_data_creation(self):
        """Test TradeData creation."""
        trade = TradeData(
            symbol="BTCUSDT",
            exchange="binance",
            timestamp=datetime.now(tz=timezone.utc),
            trade_id="123456",
            price=45000.0,
            quantity=1.0,
            side="buy",
            maker=False
        )
        
        assert trade.symbol == "BTCUSDT"
        assert trade.price == 45000.0
        assert trade.side == "buy"

    def test_order_book_update_creation(self):
        """Test OrderBookUpdate creation."""
        ob = OrderBookUpdate(
            symbol="BTCUSDT",
            exchange="binance",
            timestamp=datetime.now(tz=timezone.utc),
            bids=[(45000.0, 1.0), (44999.0, 2.0)],
            asks=[(45001.0, 1.5), (45002.0, 2.5)],
            sequence=1
        )
        
        assert ob.symbol == "BTCUSDT"
        assert len(ob.bids) == 2
        assert len(ob.asks) == 2

    def test_user_update_creation(self):
        """Test UserUpdate creation."""
        update = UserUpdate(
            exchange="binance",
            timestamp=datetime.now(tz=timezone.utc),
            update_type="order_update",
            symbol="BTCUSDT",
            order_id="12345",
            status="NEW"
        )
        
        assert update.exchange == "binance"
        assert update.update_type == "order_update"
        assert update.order_id == "12345"


# ============================================================================
# Integration Tests
# ============================================================================

class TestWebSocketIntegration:
    """Integration tests for WebSocket connectors."""

    @pytest.mark.asyncio
    async def test_subscription_tracking(self, binance_config):
        """Test subscription tracking."""
        connector = BinanceWebSocketConnector(binance_config)
        
        connector.subscriptions.add("ticker:BTCUSDT")
        connector.subscriptions.add("trade:ETHUSDT")
        
        assert len(connector.subscriptions) == 2
        assert "ticker:BTCUSDT" in connector.subscriptions
        assert "trade:ETHUSDT" in connector.subscriptions

    @pytest.mark.asyncio
    async def test_async_context_manager(self, binance_config):
        """Test async context manager."""
        with patch.object(BinanceWebSocketConnector, 'connect', new_callable=AsyncMock) as mock_connect:
            with patch.object(BinanceWebSocketConnector, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
                connector = BinanceWebSocketConnector(binance_config)
                
                async with connector as conn:
                    assert conn is connector
                
                mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_callbacks(self, binance_config):
        """Test multiple callbacks for same stream."""
        connector = BinanceWebSocketConnector(binance_config)
        
        callback_results = []
        
        def callback1(data):
            callback_results.append(("callback1", data))
        
        def callback2(data):
            callback_results.append(("callback2", data))
        
        connector.add_callback(StreamType.TICKER, callback1)
        connector.add_callback(StreamType.TICKER, callback2)
        
        ticker = TickerData(
            symbol="BTCUSDT",
            exchange="binance",
            timestamp=datetime.now(tz=timezone.utc),
            bid=45000.0,
            ask=45001.0,
            last_price=45000.50,
            volume_24h=1000.0,
            high_24h=46000.0,
            low_24h=44000.0,
            change_24h=1000.0,
            change_percent_24h=2.27
        )
        
        asyncio.create_task(connector._invoke_callbacks(StreamType.TICKER, ticker))
        await asyncio.sleep(0.1)
        
        assert len(callback_results) >= 2


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestWebSocketErrorHandling:
    """Test error handling in WebSocket connectors."""

    @pytest.mark.asyncio
    async def test_parse_invalid_json(self, binance_config):
        """Test handling of invalid JSON."""
        connector = BinanceWebSocketConnector(binance_config)
        
        result = await connector._parse_message("{invalid json}")
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_malformed_ticker(self, binance_config):
        """Test handling of malformed ticker message."""
        connector = BinanceWebSocketConnector(binance_config)
        
        callback_data = []
        connector.add_callback(StreamType.TICKER, lambda data: callback_data.append(data))
        
        # Missing required fields
        malformed_msg = {
            "e": "24hrTicker",
            "s": "BTCUSDT"
        }
        
        # Should handle gracefully without raising exception
        await connector._handle_ticker(malformed_msg)

    @pytest.mark.asyncio
    async def test_subscribe_without_connection(self, binance_config):
        """Test subscribe fails without connection."""
        connector = BinanceWebSocketConnector(binance_config)
        
        with pytest.raises(RuntimeError):
            await connector._subscribe_to_stream(StreamType.TICKER, "BTCUSDT")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
