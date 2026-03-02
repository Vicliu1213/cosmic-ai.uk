#!/usr/bin/env python3
"""
Live Trading Module Tests
實盤交易模組測試

Comprehensive tests for the live trading engine, order execution, and risk management.
實盤交易引擎、訂單執行和風險管理的全面測試。
"""

import unittest
import asyncio
from datetime import datetime
import sys
import os
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from opencode.live_trading import (
    OrderType, OrderStatus, PositionSide,
    MarketPrice, Order, Position, AccountInfo,
    RiskManager, OrderExecutor, LiveTradingEngine,
    MockDataSource
)

class TestOrderTypes(unittest.TestCase):
    """Test order type enumerations."""
    
    def test_order_type_buy(self):
        """Test BUY order type."""
        self.assertEqual(OrderType.BUY.value, "BUY")
    
    def test_order_type_sell(self):
        """Test SELL order type."""
        self.assertEqual(OrderType.SELL.value, "SELL")
    
    def test_order_status_pending(self):
        """Test PENDING order status."""
        self.assertEqual(OrderStatus.PENDING.value, "pending")
    
    def test_order_status_filled(self):
        """Test FILLED order status."""
        self.assertEqual(OrderStatus.FILLED.value, "filled")

class TestPositionTypes(unittest.TestCase):
    """Test position side enumerations."""
    
    def test_position_long(self):
        """Test LONG position."""
        self.assertEqual(PositionSide.LONG.value, "LONG")
    
    def test_position_short(self):
        """Test SHORT position."""
        self.assertEqual(PositionSide.SHORT.value, "SHORT")
    
    def test_position_flat(self):
        """Test FLAT (no position)."""
        self.assertEqual(PositionSide.FLAT.value, "FLAT")

class TestMarketPrice(unittest.TestCase):
    """Test market price data structure."""
    
    def test_market_price_creation(self):
        """Test creating a market price."""
        price = MarketPrice(
            symbol="BTC/USD",
            open=50000.0,
            high=50100.0,
            low=49900.0,
            close=50050.0,
            volume=1000.0,
            timestamp=datetime.now()
        )
        
        self.assertEqual(price.symbol, "BTC/USD")
        self.assertEqual(price.open, 50000.0)
        self.assertEqual(price.close, 50050.0)
    
    def test_market_price_to_dict(self):
        """Test market price conversion to dict."""
        price = MarketPrice(
            symbol="BTC/USD",
            open=50000.0,
            high=50100.0,
            low=49900.0,
            close=50050.0,
            volume=1000.0,
            timestamp=datetime.now()
        )
        
        price_dict = price.to_dict()
        self.assertIn('symbol', price_dict)
        self.assertIn('close', price_dict)
        self.assertEqual(price_dict['symbol'], "BTC/USD")

class TestOrder(unittest.TestCase):
    """Test order data structure."""
    
    def test_order_creation(self):
        """Test creating an order."""
        order = Order(
            order_id="ORD-001",
            symbol="BTC/USD",
            order_type=OrderType.BUY,
            quantity=1.5,
            price=50000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        self.assertEqual(order.order_id, "ORD-001")
        self.assertEqual(order.symbol, "BTC/USD")
        self.assertEqual(order.order_type, OrderType.BUY)
        self.assertEqual(order.quantity, 1.5)
        self.assertEqual(order.price, 50000.0)
    
    def test_order_notional_value(self):
        """Test order notional value calculation."""
        order = Order(
            order_id="ORD-001",
            symbol="BTC/USD",
            order_type=OrderType.BUY,
            quantity=2.0,
            price=50000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        notional = order.quantity * order.price
        self.assertEqual(notional, 100000.0)

class TestPosition(unittest.TestCase):
    """Test position data structure."""
    
    def test_long_position_creation(self):
        """Test creating a long position."""
        position = Position(
            symbol="BTC/USD",
            side=PositionSide.LONG,
            quantity=2.5,
            entry_price=50000.0,
            current_price=51000.0,
            timestamp=datetime.now()
        )
        
        self.assertEqual(position.side, PositionSide.LONG)
        self.assertEqual(position.quantity, 2.5)
    
    def test_position_value(self):
        """Test position value calculation."""
        position = Position(
            symbol="BTC/USD",
            side=PositionSide.LONG,
            quantity=2.0,
            entry_price=50000.0,
            current_price=51000.0,
            timestamp=datetime.now()
        )
        
        position_value = position.position_value
        self.assertEqual(position_value, 102000.0)
    
    def test_position_return_rate(self):
        """Test return rate calculation."""
        position = Position(
            symbol="BTC/USD",
            side=PositionSide.LONG,
            quantity=2.0,
            entry_price=50000.0,
            current_price=51000.0,
            timestamp=datetime.now()
        )
        
        return_rate = position.return_rate
        self.assertEqual(return_rate, 2.0)

class TestAccountInfo(unittest.TestCase):
    """Test account information data structure."""
    
    def test_account_creation(self):
        """Test creating account info."""
        account = AccountInfo(
            account_id="ACC-001",
            balance=100000.0,
            equity=105000.0,
            free_margin=65000.0,
            used_margin=40000.0,
            margin_ratio=0.4,
            timestamp=datetime.now()
        )
        
        self.assertEqual(account.account_id, "ACC-001")
        self.assertEqual(account.balance, 100000.0)
        self.assertEqual(account.equity, 105000.0)
    
    def test_account_margin_level(self):
        """Test margin level calculation."""
        account = AccountInfo(
            account_id="ACC-001",
            balance=100000.0,
            equity=105000.0,
            free_margin=65000.0,
            used_margin=40000.0,
            margin_ratio=0.4,
            timestamp=datetime.now()
        )
        
        margin_level = account.margin_level
        # Should be (105000 / 40000) * 100 = 262.5%
        self.assertAlmostEqual(margin_level, 262.5)

class TestRiskManager(unittest.TestCase):
    """Test risk management functionality."""
    
    def setUp(self):
        """Set up risk manager."""
        self.risk_manager = RiskManager(
            max_position_size=10000.0,
            max_daily_loss=5000.0,
            max_leverage=2.0,
            stop_loss_percent=5.0
        )
    
    def test_risk_manager_creation(self):
        """Test risk manager initialization."""
        self.assertEqual(self.risk_manager.max_position_size, 10000.0)
        self.assertEqual(self.risk_manager.max_leverage, 2.0)
    
    def test_position_size_validation_ok(self):
        """Test position size validation - acceptable."""
        position_value = 8000.0
        account_equity = 100000.0
        
        is_valid = self.risk_manager.check_position_size(position_value, account_equity)
        self.assertTrue(is_valid)
    
    def test_position_size_validation_too_large(self):
        """Test position size validation - too large."""
        position_value = 15000.0  # Exceeds max_position_size of 10000
        account_equity = 100000.0
        
        is_valid = self.risk_manager.check_position_size(position_value, account_equity)
        self.assertFalse(is_valid)
    
    def test_stop_loss_calculation_buy(self):
        """Test stop loss level calculation for buy."""
        entry_price = 50000.0
        stop_loss = self.risk_manager.calculate_stop_loss(entry_price, OrderType.BUY)
        
        # Should be 50000 * (1 - 5/100) = 47500
        self.assertEqual(stop_loss, 47500.0)
    
    def test_stop_loss_calculation_sell(self):
        """Test stop loss level calculation for sell."""
        entry_price = 50000.0
        stop_loss = self.risk_manager.calculate_stop_loss(entry_price, OrderType.SELL)
        
        # Should be 50000 * (1 + 5/100) = 52500
        self.assertEqual(stop_loss, 52500.0)
    
    def test_daily_loss_tracking(self):
        """Test daily loss tracking."""
        self.risk_manager.update_daily_loss(-1000.0)
        self.assertEqual(self.risk_manager.daily_loss, 1000.0)
    
    def test_daily_loss_limit(self):
        """Test daily loss limit check."""
        is_valid = self.risk_manager.check_daily_loss(-2000.0)
        self.assertTrue(is_valid)

class TestOrderExecutor(unittest.TestCase):
    """Test order execution functionality."""
    
    def setUp(self):
        """Set up order executor."""
        self.data_source = MockDataSource()
        self.executor = OrderExecutor(self.data_source)
    
    def test_order_executor_creation(self):
        """Test order executor initialization."""
        self.assertIsNotNone(self.executor)
        self.assertIsInstance(self.executor.orders, dict)
        self.assertEqual(self.executor.data_source, self.data_source)
    
    def test_submit_buy_order(self):
        """Test submitting a buy order."""
        order = Order(
            order_id="ORD-001",
            symbol="BTC/USD",
            order_type=OrderType.BUY,
            quantity=1.0,
            price=50000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        self.executor.orders[order.order_id] = order
        
        self.assertIn(order.order_id, self.executor.orders)
        self.assertEqual(self.executor.orders[order.order_id].order_type, OrderType.BUY)
    
    def test_submit_sell_order(self):
        """Test submitting a sell order."""
        order = Order(
            order_id="ORD-002",
            symbol="BTC/USD",
            order_type=OrderType.SELL,
            quantity=1.0,
            price=51000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        self.executor.orders[order.order_id] = order
        
        self.assertIn(order.order_id, self.executor.orders)
        self.assertEqual(self.executor.orders[order.order_id].order_type, OrderType.SELL)
    
    def test_order_status_transition(self):
        """Test order status transition."""
        order = Order(
            order_id="ORD-001",
            symbol="BTC/USD",
            order_type=OrderType.BUY,
            quantity=1.0,
            price=50000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        self.executor.orders[order.order_id] = order
        
        # Simulate filling the order
        self.executor.orders[order.order_id].status = OrderStatus.FILLED
        
        self.assertEqual(self.executor.orders[order.order_id].status, OrderStatus.FILLED)

class TestMockDataSource(unittest.TestCase):
    """Test mock data source functionality."""
    
    def setUp(self):
        """Set up mock data source."""
        self.data_source = MockDataSource()
    
    def test_data_source_creation(self):
        """Test data source initialization."""
        self.assertIsNotNone(self.data_source)
        self.assertFalse(self.data_source.connected)
    
    def test_async_get_price(self):
        """Test getting async market price."""
        async def test_price():
            price = await self.data_source.get_price("BTC/USD")
            
            self.assertIsNotNone(price)
            self.assertEqual(price.symbol, "BTC/USD")
            self.assertGreater(price.close, 0)
        
        asyncio.run(test_price())
    
    def test_multiple_symbols_async(self):
        """Test getting prices for multiple symbols."""
        async def test_multiple():
            symbols = ["BTC/USD", "ETH/USD", "XRP/USD"]
            
            for symbol in symbols:
                price = await self.data_source.get_price(symbol)
                self.assertEqual(price.symbol, symbol)
                self.assertGreater(price.close, 0)
        
        asyncio.run(test_multiple())
    
    def test_data_source_connect(self):
        """Test data source connection."""
        async def test_connect():
            result = await self.data_source.connect()
            self.assertTrue(result)
            self.assertTrue(self.data_source.connected)
            await self.data_source.disconnect()
            self.assertFalse(self.data_source.connected)
        
        asyncio.run(test_connect())

class TestLiveTradingEngine(unittest.TestCase):
    """Test live trading engine functionality."""
    
    def setUp(self):
        """Set up trading engine."""
        self.engine = LiveTradingEngine(account_id="TEST-ACC", initial_balance=100000.0)
    
    def test_engine_initialization(self):
        """Test trading engine initialization."""
        self.assertEqual(self.engine.account_id, "TEST-ACC")
        self.assertEqual(self.engine.account_info.balance, 100000.0)
    
    def test_get_account_info(self):
        """Test getting account info."""
        account_info = self.engine.account_info
        
        self.assertIsNotNone(account_info)
        self.assertEqual(account_info.balance, 100000.0)
    
    def test_order_executor_access(self):
        """Test order executor access."""
        executor = self.engine.order_executor
        
        self.assertIsNotNone(executor)
        self.assertIsInstance(executor.orders, dict)
    
    def test_get_all_positions(self):
        """Test getting all positions."""
        positions = self.engine.order_executor.get_all_positions()
        
        self.assertIsInstance(positions, list)
        self.assertEqual(len(positions), 0)
    
    def test_get_stats_structure(self):
        """Test trading statistics structure."""
        stats = self.engine.get_stats()
        
        self.assertIn('total_trades', stats)
        self.assertIn('winning_trades', stats)
        self.assertIn('losing_trades', stats)
        self.assertIn('total_pnl', stats)
    
    def test_account_equity_calculation(self):
        """Test account equity calculation."""
        equity = self.engine.account_info.equity
        
        self.assertGreater(equity, 0)
        self.assertLessEqual(equity, self.engine.account_info.balance * 2)  # With leverage

class TestAsyncOperations(unittest.TestCase):
    """Test async operations in live trading."""
    
    def setUp(self):
        """Set up async test environment."""
        self.engine = LiveTradingEngine(account_id="ASYNC-TEST", initial_balance=50000.0)
    
    def test_event_loop_availability(self):
        """Test that async operations can be run."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.assertIsNotNone(loop)
        finally:
            loop.close()

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_zero_quantity_order(self):
        """Test handling zero quantity order."""
        order = Order(
            order_id="ORD-ZERO",
            symbol="BTC/USD",
            order_type=OrderType.BUY,
            quantity=0.0,  # Zero quantity
            price=50000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        notional = order.quantity * order.price
        self.assertEqual(notional, 0.0)
    
    def test_negative_pnl(self):
        """Test negative P&L handling."""
        position = Position(
            symbol="BTC/USD",
            side=PositionSide.LONG,
            quantity=1.0,
            entry_price=50000.0,
            current_price=48000.0,
            timestamp=datetime.now()
        )
        
        pnl = (position.current_price - position.entry_price) * position.quantity
        self.assertLess(pnl, 0)
    
    def test_very_large_position(self):
        """Test very large position handling."""
        position = Position(
            symbol="BTC/USD",
            side=PositionSide.LONG,
            quantity=1000.0,
            entry_price=50000.0,
            current_price=51000.0,
            timestamp=datetime.now()
        )
        
        notional_value = position.quantity * position.entry_price
        self.assertEqual(notional_value, 50000000.0)
    
    def test_very_small_quantity(self):
        """Test very small quantity handling."""
        order = Order(
            order_id="ORD-SMALL",
            symbol="BTC/USD",
            order_type=OrderType.BUY,
            quantity=0.0001,
            price=50000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        notional = order.quantity * order.price
        self.assertGreater(notional, 0)

class TestIntegration(unittest.TestCase):
    """Integration tests for live trading components."""
    
    def test_order_to_position_flow(self):
        """Test order creation to position tracking flow."""
        data_source = MockDataSource()
        engine = LiveTradingEngine("INT-TEST", 100000.0, data_source)
        
        # Create an order
        order = Order(
            order_id="ORD-INT-001",
            symbol="BTC/USD",
            order_type=OrderType.BUY,
            quantity=1.5,
            price=50000.0,
            status=OrderStatus.PENDING,
            timestamp=datetime.now()
        )
        
        # Add to executor
        engine.order_executor.orders[order.order_id] = order
        
        self.assertIn(order.order_id, engine.order_executor.orders)
        
        # Verify order structure
        stored_order = engine.order_executor.orders[order.order_id]
        self.assertEqual(stored_order.symbol, "BTC/USD")
        self.assertEqual(stored_order.quantity, 1.5)
    
    def test_risk_manager_with_engine(self):
        """Test risk manager integration with engine."""
        engine = LiveTradingEngine("RISK-TEST", 100000.0)
        
        # Try to place large order (should check risk limits)
        risk_mgr = engine.risk_manager
        
        # Check position size
        large_position = 50000.0  # Should exceed limits
        is_valid = risk_mgr.check_position_size(large_position, engine.account_info.equity)
        
        self.assertFalse(is_valid)
    
    def test_data_source_market_data(self):
        """Test market data retrieval from data source."""
        async def test_data():
            data_source = MockDataSource()
            await data_source.connect()
            
            price = await data_source.get_price("BTC/USD")
            
            self.assertIsNotNone(price)
            self.assertEqual(price.symbol, "BTC/USD")
            self.assertGreater(price.close, 0)
            
            await data_source.disconnect()
        
        asyncio.run(test_data())

if __name__ == '__main__':
    unittest.main()
