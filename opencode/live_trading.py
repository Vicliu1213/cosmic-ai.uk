#!/usr/bin/env python3
"""
實盤交易模組 (Live Trading Module)
Comic AI Trading System - Real-time Trading Integration

Provides real-time market data integration, order execution,
position management, and risk control for live trading.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from abc import ABC, abstractmethod
import threading
from collections import deque

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order type enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PositionSide(Enum):
    """Position side enumeration."""
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


@dataclass
class MarketPrice:
    """Market price data structure."""
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class Order:
    """Order data structure."""
    order_id: str
    symbol: str
    order_type: OrderType
    price: float
    quantity: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'order_type': self.order_type.value,
            'price': self.price,
            'quantity': self.quantity,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'avg_fill_price': self.avg_fill_price,
        }


@dataclass
class Position:
    """Position data structure."""
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def position_value(self) -> float:
        """Calculate position value."""
        return self.quantity * self.current_price
    
    @property
    def return_rate(self) -> float:
        """Calculate return rate."""
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'position_value': self.position_value,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'return_rate': self.return_rate,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class AccountInfo:
    """Account information data structure."""
    account_id: str
    balance: float
    equity: float
    free_margin: float
    used_margin: float
    margin_ratio: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def margin_level(self) -> float:
        """Calculate margin level."""
        if self.used_margin == 0:
            return float('inf')
        return (self.equity / self.used_margin) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'balance': self.balance,
            'equity': self.equity,
            'free_margin': self.free_margin,
            'used_margin': self.used_margin,
            'margin_ratio': self.margin_ratio,
            'margin_level': self.margin_level,
            'timestamp': self.timestamp.isoformat(),
        }


class DataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to data source."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from data source."""
        pass
    
    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get current price for symbol."""
        pass
    
    @abstractmethod
    async def subscribe_price(self, symbol: str, callback: Callable) -> bool:
        """Subscribe to price updates."""
        pass


class MockDataSource(DataSource):
    """Mock data source for testing."""
    
    def __init__(self):
        """Initialize mock data source."""
        self.connected = False
        self.prices: Dict[str, MarketPrice] = {}
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.is_running = False
    
    async def connect(self) -> bool:
        """Connect to data source."""
        self.connected = True
        self.is_running = True
        logger.info("Mock data source connected")
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from data source."""
        self.connected = False
        self.is_running = False
        logger.info("Mock data source disconnected")
        return True
    
    async def get_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get current price for symbol."""
        if symbol not in self.prices:
            # Generate mock price
            import random
            base_price = 100.0 + random.random() * 50
            self.prices[symbol] = MarketPrice(
                symbol=symbol,
                open=base_price,
                high=base_price + random.random() * 5,
                low=base_price - random.random() * 5,
                close=base_price + random.random() * 2 - 1,
                volume=random.random() * 1000000,
            )
        
        return self.prices[symbol]
    
    async def subscribe_price(self, symbol: str, callback: Callable) -> bool:
        """Subscribe to price updates."""
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = []
        self.subscriptions[symbol].append(callback)
        logger.info(f"Subscribed to {symbol}")
        return True
    
    async def simulate_price_updates(self):
        """Simulate price updates."""
        import random
        while self.is_running:
            for symbol in list(self.subscriptions.keys()):
                price = await self.get_price(symbol)
                # Update price slightly
                price.close += random.uniform(-1, 1)
                price.high = max(price.high, price.close)
                price.low = min(price.low, price.close)
                
                # Notify subscribers
                for callback in self.subscriptions[symbol]:
                    try:
                        await callback(price)
                    except:
                        pass
            
            await asyncio.sleep(1)


class RiskManager:
    """Risk management system."""
    
    def __init__(self, 
                 max_position_size: float = 10000.0,
                 max_daily_loss: float = 5000.0,
                 max_leverage: float = 10.0,
                 stop_loss_percent: float = 2.0):
        """
        Initialize risk manager.
        
        Args:
            max_position_size: Maximum position size in base currency
            max_daily_loss: Maximum daily loss allowed
            max_leverage: Maximum leverage allowed
            stop_loss_percent: Default stop loss percentage
        """
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_leverage = max_leverage
        self.stop_loss_percent = stop_loss_percent
        self.daily_loss = 0.0
        self.daily_start_time = datetime.now()
    
    def check_position_size(self, position_value: float, account_equity: float) -> bool:
        """Check if position size is within limits."""
        if position_value > self.max_position_size:
            logger.warning(f"Position size {position_value} exceeds max {self.max_position_size}")
            return False
        
        leverage = position_value / account_equity if account_equity > 0 else 0
        if leverage > self.max_leverage:
            logger.warning(f"Leverage {leverage} exceeds max {self.max_leverage}")
            return False
        
        return True
    
    def check_daily_loss(self, current_loss: float) -> bool:
        """Check if daily loss is within limits."""
        # Reset if new day
        if (datetime.now() - self.daily_start_time).days > 0:
            self.daily_loss = 0.0
            self.daily_start_time = datetime.now()
        
        total_loss = self.daily_loss + abs(current_loss)
        if total_loss > self.max_daily_loss:
            logger.warning(f"Daily loss {total_loss} exceeds max {self.max_daily_loss}")
            return False
        
        return True
    
    def update_daily_loss(self, realized_pnl: float) -> None:
        """Update daily loss."""
        if realized_pnl < 0:
            self.daily_loss += abs(realized_pnl)
    
    def calculate_stop_loss(self, entry_price: float, order_type: OrderType) -> float:
        """Calculate stop loss price."""
        if order_type == OrderType.BUY:
            return entry_price * (1 - self.stop_loss_percent / 100)
        else:  # SELL
            return entry_price * (1 + self.stop_loss_percent / 100)


class OrderExecutor:
    """Order execution engine."""
    
    def __init__(self, data_source: DataSource):
        """
        Initialize order executor.
        
        Args:
            data_source: Data source for market prices
        """
        self.data_source = data_source
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.order_counter = 0
        self.lock = threading.RLock()
    
    async def submit_order(self, 
                          symbol: str,
                          order_type: OrderType,
                          price: float,
                          quantity: float) -> str:
        """
        Submit an order.
        
        Args:
            symbol: Trading symbol
            order_type: Buy or Sell
            price: Order price
            quantity: Order quantity
            
        Returns:
            Order ID
        """
        with self.lock:
            self.order_counter += 1
            order_id = f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.order_counter}"
            
            order = Order(
                order_id=order_id,
                symbol=symbol,
                order_type=order_type,
                price=price,
                quantity=quantity,
            )
            
            self.orders[order_id] = order
            logger.info(f"Order submitted: {order_id} - {order_type.value} {quantity} {symbol} @ {price}")
            
            # Simulate order filling
            asyncio.create_task(self._fill_order(order_id))
            
            return order_id
    
    async def _fill_order(self, order_id: str):
        """Simulate order filling."""
        order = self.orders.get(order_id)
        if not order:
            return
        
        order.status = OrderStatus.SUBMITTED
        await asyncio.sleep(0.5)  # Simulate latency
        
        # Get current price
        market_price = await self.data_source.get_price(order.symbol)
        if not market_price:
            order.status = OrderStatus.REJECTED
            return
        
        # Fill order
        if (order.order_type == OrderType.BUY and market_price.close <= order.price) or \
           (order.order_type == OrderType.SELL and market_price.close >= order.price):
            order.filled_quantity = order.quantity
            order.avg_fill_price = market_price.close
            order.status = OrderStatus.FILLED
            
            # Update position
            await self._update_position(order)
            logger.info(f"Order filled: {order_id} @ {market_price.close}")
        else:
            order.status = OrderStatus.CANCELLED
            logger.info(f"Order cancelled: {order_id}")
    
    async def _update_position(self, order: Order):
        """Update position after order fill."""
        with self.lock:
            symbol = order.symbol
            
            if symbol not in self.positions:
                # Create new position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side=PositionSide.LONG if order.order_type == OrderType.BUY else PositionSide.SHORT,
                    quantity=order.filled_quantity,
                    entry_price=order.avg_fill_price,
                    current_price=order.avg_fill_price,
                )
            else:
                # Update existing position
                pos = self.positions[symbol]
                if (pos.side == PositionSide.LONG and order.order_type == OrderType.BUY) or \
                   (pos.side == PositionSide.SHORT and order.order_type == OrderType.SELL):
                    # Add to position
                    total_cost = pos.quantity * pos.entry_price + order.filled_quantity * order.avg_fill_price
                    pos.quantity += order.filled_quantity
                    pos.entry_price = total_cost / pos.quantity if pos.quantity > 0 else 0
                else:
                    # Close position
                    pos.realized_pnl = (order.avg_fill_price - pos.entry_price) * pos.quantity
                    pos.quantity -= order.filled_quantity
                    if pos.quantity <= 0:
                        pos.side = PositionSide.FLAT
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.orders.get(order_id)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position by symbol."""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Position]:
        """Get all active positions."""
        return list(self.positions.values())


class LiveTradingEngine:
    """Live trading engine."""
    
    def __init__(self, 
                 account_id: str,
                 initial_balance: float,
                 data_source: Optional[DataSource] = None):
        """
        Initialize live trading engine.
        
        Args:
            account_id: Account identifier
            initial_balance: Initial account balance
            data_source: Data source (uses mock if None)
        """
        self.account_id = account_id
        self.initial_balance = initial_balance
        self.data_source = data_source or MockDataSource()
        self.risk_manager = RiskManager()
        self.order_executor = OrderExecutor(self.data_source)
        
        # Account state
        self.account_info = AccountInfo(
            account_id=account_id,
            balance=initial_balance,
            equity=initial_balance,
            free_margin=initial_balance,
            used_margin=0.0,
            margin_ratio=0.0,
        )
        
        # Trading state
        self.is_running = False
        self.trades: List[Dict[str, Any]] = []
        self.callbacks: Dict[str, List[Callable]] = {
            'order_filled': [],
            'position_changed': [],
            'account_updated': [],
        }
    
    async def initialize(self) -> bool:
        """Initialize trading engine."""
        try:
            await self.data_source.connect()
            logger.info(f"Live trading engine initialized for {self.account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize trading engine: {e}")
            return False
    
    async def start_trading(self) -> None:
        """Start trading."""
        if self.is_running:
            logger.warning("Trading already running")
            return
        
        self.is_running = True
        logger.info("Trading started")
        
        # Start price update simulation if mock data source
        if isinstance(self.data_source, MockDataSource):
            asyncio.create_task(self.data_source.simulate_price_updates())
    
    async def stop_trading(self) -> None:
        """Stop trading."""
        self.is_running = False
        await self.data_source.disconnect()
        logger.info("Trading stopped")
    
    async def place_buy_order(self, symbol: str, price: float, quantity: float) -> str:
        """Place a buy order."""
        # Check risk
        position_value = quantity * price
        if not self.risk_manager.check_position_size(position_value, self.account_info.equity):
            raise RuntimeError("Order rejected: position size exceeds limit")
        
        # Submit order
        order_id = await self.order_executor.submit_order(symbol, OrderType.BUY, price, quantity)
        
        # Update account
        self.account_info.used_margin += position_value
        self.account_info.free_margin = self.account_info.balance - self.account_info.used_margin
        self._notify_callback('order_filled', order_id)
        
        return order_id
    
    async def place_sell_order(self, symbol: str, price: float, quantity: float) -> str:
        """Place a sell order."""
        # Check risk
        position_value = quantity * price
        if not self.risk_manager.check_position_size(position_value, self.account_info.equity):
            raise RuntimeError("Order rejected: position size exceeds limit")
        
        # Submit order
        order_id = await self.order_executor.submit_order(symbol, OrderType.SELL, price, quantity)
        
        # Update account
        self.account_info.used_margin += position_value
        self.account_info.free_margin = self.account_info.balance - self.account_info.used_margin
        self._notify_callback('order_filled', order_id)
        
        return order_id
    
    async def close_position(self, symbol: str) -> Optional[str]:
        """Close a position."""
        position = self.order_executor.get_position(symbol)
        if not position or position.side == PositionSide.FLAT:
            logger.warning(f"No open position for {symbol}")
            return None
        
        # Place closing order
        order_type = OrderType.SELL if position.side == PositionSide.LONG else OrderType.BUY
        market_price = await self.data_source.get_price(symbol)
        if not market_price:
            return None
        
        order_id = await self.order_executor.submit_order(
            symbol, order_type, market_price.close, position.quantity
        )
        
        # Record trade
        self._record_trade(symbol, position.realized_pnl)
        
        return order_id
    
    async def get_market_price(self, symbol: str) -> Optional[MarketPrice]:
        """Get current market price."""
        return await self.data_source.get_price(symbol)
    
    def update_positions_prices(self, prices: Dict[str, float]) -> None:
        """Update positions with current prices."""
        for symbol, price in prices.items():
            position = self.order_executor.get_position(symbol)
            if position:
                position.current_price = price
                position.unrealized_pnl = (price - position.entry_price) * position.quantity
                self._notify_callback('position_changed', symbol)
        
        # Update account equity
        self.account_info.equity = self._calculate_equity()
        self._notify_callback('account_updated', self.account_info.account_id)
    
    def _calculate_equity(self) -> float:
        """Calculate account equity."""
        equity = self.account_info.balance
        for position in self.order_executor.get_all_positions():
            equity += position.unrealized_pnl
        return equity
    
    def _record_trade(self, symbol: str, pnl: float) -> None:
        """Record a completed trade."""
        self.trades.append({
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'pnl': pnl,
        })
        self.risk_manager.update_daily_loss(pnl)
    
    def _notify_callback(self, event: str, data: Any) -> None:
        """Notify callbacks."""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in callback {event}: {e}")
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback."""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def get_account_info(self) -> AccountInfo:
        """Get account information."""
        return self.account_info
    
    def get_positions(self) -> List[Position]:
        """Get all positions."""
        return self.order_executor.get_all_positions()
    
    def get_trades(self) -> List[Dict[str, Any]]:
        """Get trade history."""
        return self.trades
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trading statistics."""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'roi': 0.0,
            }
        
        winning_trades = sum(1 for t in self.trades if t['pnl'] > 0)
        losing_trades = sum(1 for t in self.trades if t['pnl'] < 0)
        total_pnl = sum(t['pnl'] for t in self.trades)
        roi = (total_pnl / self.initial_balance) * 100
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / len(self.trades) * 100) if self.trades else 0,
            'total_pnl': total_pnl,
            'roi': roi,
        }


async def main():
    """Test live trading engine."""
    logger.info("=" * 70)
    logger.info("Comic AI - Live Trading Engine Test")
    logger.info("=" * 70)
    
    # Create trading engine
    engine = LiveTradingEngine(
        account_id="TEST_ACCOUNT_001",
        initial_balance=10000.0,
    )
    
    # Initialize
    if not await engine.initialize():
        logger.error("Initialization failed")
        return
    
    # Start trading
    await engine.start_trading()
    
    # Place some orders
    try:
        logger.info("\n📊 Placing test orders...")
        
        order1 = await engine.place_buy_order("BTC/USD", 50000, 0.1)
        logger.info(f"Buy order placed: {order1}")
        
        await asyncio.sleep(1)
        
        order2 = await engine.place_buy_order("ETH/USD", 3000, 1.0)
        logger.info(f"Buy order placed: {order2}")
        
        await asyncio.sleep(2)
        
        # Get positions
        logger.info("\n📈 Current positions:")
        for pos in engine.get_positions():
            logger.info(f"  {pos.symbol}: {pos.quantity} @ {pos.entry_price} (Value: {pos.position_value:.2f})")
        
        # Get account info
        logger.info("\n💰 Account information:")
        account = engine.get_account_info()
        logger.info(f"  Balance: ${account.balance:.2f}")
        logger.info(f"  Equity: ${account.equity:.2f}")
        logger.info(f"  Free Margin: ${account.free_margin:.2f}")
        
        # Close positions
        logger.info("\n❌ Closing positions...")
        for symbol in ["BTC/USD", "ETH/USD"]:
            await engine.close_position(symbol)
        
        await asyncio.sleep(1)
        
        # Get stats
        logger.info("\n📊 Trading statistics:")
        stats = engine.get_stats()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Trading error: {e}")
    finally:
        await engine.stop_trading()
    
    logger.info("\n" + "=" * 70)
    logger.info("Test completed")
    logger.info("=" * 70)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
