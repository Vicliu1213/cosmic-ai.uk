#!/usr/bin/env python3
"""
Test Order Monitoring System
訂單監控系統測試

Integration tests for order monitoring components.
Tests:
- OrderStatusMonitor functionality
- OrderBookWatcher functionality
- PortfolioMonitor functionality
- EventNotifier functionality
- MonitoringDashboard integration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import pytest

from src.phase5.order_management import (
    Order, OrderManager, OrderType, OrderSide, OrderStatus, OrderPrice,
    OrderQuantity, Position, PositionStatus, PortfolioManager,
    PositionManager
)
from src.phase5.order_execution import (
    OrderExecutionEngine, OrderBookManager, ExecutionMode, OrderBook
)
from src.phase5.order_monitoring import (
    OrderStatusMonitor, OrderBookWatcher, PortfolioMonitor, EventNotifier,
    MonitoringDashboard, AlertType, AlertLevel, MonitoringState
)
from src.phase5.exchange_connector import ExchangeType


# ============================================================================
# Test Setup
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrderMonitoringTest")


async def setup_test_environment():
    """Set up test managers and components.
    
    Returns:
        Tuple of (order_mgr, position_mgr, portfolio_mgr, book_mgr, notifier, dashboard)
    """
    order_mgr = OrderManager()
    position_mgr = PositionManager()
    portfolio_mgr = PortfolioManager(initial_capital=10000.0)

    book_mgr = OrderBookManager()
    
    # Create monitoring components
    order_monitor = OrderStatusMonitor(order_mgr)
    book_watcher = OrderBookWatcher(book_mgr)
    portfolio_monitor = PortfolioMonitor(portfolio_mgr)
    notifier = EventNotifier()

    # Create dashboard
    dashboard = MonitoringDashboard(
        order_monitor,
        book_watcher,
        portfolio_monitor,
        notifier
    )

    return (order_mgr, position_mgr, portfolio_mgr, book_mgr, order_monitor,
            book_watcher, portfolio_monitor, notifier, dashboard)


# ============================================================================
# Test Cases
# ============================================================================

@pytest.mark.asyncio
async def test_order_status_monitoring():
    """Test order status tracking."""
    logger.info("Testing OrderStatusMonitor...")
    
    order_mgr, _, _, _, order_monitor, _, _, _, _ = await setup_test_environment()

    # Create an order
    order = Order(
        exchange_type=ExchangeType.BINANCE,
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        symbol="BTC/USDT",
        quantity=OrderQuantity(original_quantity=1.0),
        price=OrderPrice(limit_price=50000.0)
    )

    # Add to manager
    order_mgr.orders[order.order_id] = order

    # Start monitoring
    await order_monitor.monitor_order(order.order_id)

    # Check initial status
    changes = await order_monitor.check_status_updates()
    assert len(changes) == 0, "Should have no changes initially"

    # Update order status
    order.status = OrderStatus.OPEN
    order.opened_at = datetime.utcnow()

    # Register callback
    status_changes: List[tuple] = []
    def track_changes(o, old, new):
        status_changes.append((o.order_id, old, new))

    order_monitor.register_status_callback(track_changes)

    # Check for updates
    changes = await order_monitor.check_status_updates()
    assert len(changes) == 1, "Should detect status change"
    assert changes[0][1] == OrderStatus.PENDING
    assert changes[0][2] == OrderStatus.OPEN

    # Fill the order
    order.status = OrderStatus.FILLED
    order.quantity.filled_quantity = 1.0
    order.price.average_fill_price = 50500.0

    changes = await order_monitor.check_status_updates()
    assert len(changes) == 1, "Should detect fill"
    assert changes[0][2] == OrderStatus.FILLED

    # Get history
    history = order_monitor.get_order_history(order.order_id)
    assert len(history) >= 2, "Should have history"

    # Get fill time
    fill_time = order_monitor.get_fill_time(order.order_id)
    assert fill_time is not None, "Should calculate fill time"
    assert fill_time.total_seconds() >= 0

    logger.info("✅ OrderStatusMonitor test passed")


@pytest.mark.asyncio
async def test_orderbook_watching():
    """Test order book monitoring."""
    logger.info("Testing OrderBookWatcher...")
    
    _, _, _, book_mgr, _, book_watcher, _, _, _ = await setup_test_environment()

    # Start watching symbol
    book_watcher.watch_symbol("BTC/USDT", ExchangeType.BINANCE)

    # Update order book
    bids = [(50000.0, 1.0), (49900.0, 2.0)]
    asks = [(50100.0, 1.5), (50200.0, 2.5)]

    book1 = await book_mgr.update_order_book(
        "BTC/USDT",
        ExchangeType.BINANCE,
        bids=bids,
        asks=asks,
        last_trade_price=50050.0
    )

    # Check updates
    updates = await book_watcher.check_book_updates()
    assert len(updates) == 1, "Should detect book update"
    assert updates[0][0].symbol == "BTC/USDT"

    # Update again with new prices
    bids2 = [(50200.0, 1.2), (50100.0, 2.2)]
    asks2 = [(50300.0, 1.7), (50400.0, 2.7)]

    book2 = await book_mgr.update_order_book(
        "BTC/USDT",
        ExchangeType.BINANCE,
        bids=bids2,
        asks=asks2,
        last_trade_price=50250.0
    )

    updates = await book_watcher.check_book_updates()
    assert len(updates) >= 1, "Should detect second update"

    # Check spread calculation
    avg_spread = book_watcher.get_average_spread("BTC/USDT", ExchangeType.BINANCE)
    assert avg_spread is not None, "Should calculate average spread"
    assert avg_spread > 0, "Spread should be positive"

    # Check price spike detection
    is_spike = book_watcher.detect_price_spike("BTC/USDT", ExchangeType.BINANCE, threshold_percent=5.0)
    # Should detect spike since price moved from 50050 to 50250 (~0.4%)
    # Actually shouldn't exceed 5% threshold

    logger.info("✅ OrderBookWatcher test passed")


@pytest.mark.asyncio
async def test_portfolio_monitoring():
    """Test portfolio monitoring."""
    logger.info("Testing PortfolioMonitor...")
    
    _, _, portfolio_mgr, _, _, _, portfolio_monitor, _, _ = await setup_test_environment()

    # Add a position
    position = Position(
        exchange_type=ExchangeType.BINANCE,
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        entry_price=50000.0,
        entry_quantity=1.0,
        current_quantity=1.0,
        current_price=50000.0,
        status=PositionStatus.OPEN
    )

    portfolio_mgr.position_manager.positions[position.position_id] = position

    # Take snapshot
    snap1 = await portfolio_monitor.take_snapshot()
    assert snap1.position_count == 1, "Should count position"
    assert snap1.total_value > 0, "Should calculate value"

    # Update position price
    position.current_price = 51000.0

    # Take another snapshot
    snap2 = await portfolio_monitor.take_snapshot()
    assert snap2.open_positions_value > snap1.open_positions_value, "Value should increase"
    assert snap2.unrealized_pnl > snap1.unrealized_pnl, "P&L should increase"

    # Get history
    history = portfolio_monitor.get_portfolio_history(lookback_minutes=60)
    assert len(history) >= 2, "Should have history"

    logger.info("✅ PortfolioMonitor test passed")


@pytest.mark.asyncio
async def test_event_notifications():
    """Test event notifications."""
    logger.info("Testing EventNotifier...")
    
    _, _, _, _, _, _, _, notifier, _ = await setup_test_environment()

    # Register callback
    received_alerts: List[Any] = []
    def handle_alert(alert):
        received_alerts.append(alert)

    notifier.register_alert_callback(handle_alert)

    # Emit alert
    alert = await notifier.emit_alert(
        AlertType.ORDER_FILLED,
        AlertLevel.INFO,
        "Test order filled",
        order_id="test-001",
        data={"price": 50000}
    )

    assert alert is not None, "Should return alert"
    assert len(received_alerts) == 1, "Should trigger callback"
    assert received_alerts[0].alert_type == AlertType.ORDER_FILLED

    # Get alerts
    alerts = notifier.get_alerts(alert_type=AlertType.ORDER_FILLED)
    assert len(alerts) == 1, "Should retrieve alerts"

    # Emit critical alert
    critical_alert = await notifier.emit_alert(
        AlertType.STOP_LOSS_HIT,
        AlertLevel.CRITICAL,
        "Stop loss triggered",
        position_id="pos-001"
    )

    # Get critical alerts
    critical = notifier.get_alerts(level=AlertLevel.CRITICAL)
    assert len(critical) >= 1, "Should find critical alerts"

    # Acknowledge alert
    acknowledged = await notifier.acknowledge_alert(critical_alert.alert_id)
    assert acknowledged, "Should acknowledge alert"

    critical_alert_obj = notifier.get_alerts()
    for a in critical_alert_obj:
        if a.alert_id == critical_alert.alert_id:
            assert a.acknowledged, "Alert should be acknowledged"

    logger.info("✅ EventNotifier test passed")


@pytest.mark.asyncio
async def test_monitoring_dashboard():
    """Test monitoring dashboard integration."""
    logger.info("Testing MonitoringDashboard...")
    
    (order_mgr, _, portfolio_mgr, book_mgr, order_monitor,
     book_watcher, portfolio_monitor, notifier, dashboard) = await setup_test_environment()

    # Verify dashboard initialization
    assert dashboard.state == MonitoringState.IDLE, "Should start idle"

    # Setup some data
    order = Order(
        exchange_type=ExchangeType.BINANCE,
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        symbol="BTC/USDT",
        quantity=OrderQuantity(original_quantity=1.0),
        price=OrderPrice(limit_price=50000.0)
    )
    order_mgr.orders[order.order_id] = order
    await order_monitor.monitor_order(order.order_id)

    # Setup order book
    book_watcher.watch_symbol("BTC/USDT", ExchangeType.BINANCE)
    await book_mgr.update_order_book(
        "BTC/USDT",
        ExchangeType.BINANCE,
        bids=[(50000, 1.0)],
        asks=[(50100, 1.0)]
    )

    # Setup position
    position = Position(
        exchange_type=ExchangeType.BINANCE,
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        entry_price=50000.0,
        entry_quantity=1.0,
        current_quantity=1.0,
        current_price=50000.0,
        status=PositionStatus.OPEN
    )
    portfolio_mgr.position_manager.positions[position.position_id] = position

    # Run dashboard briefly
    dashboard_task = asyncio.create_task(dashboard.start(refresh_interval_seconds=0.1))

    # Let it run for a short time
    await asyncio.sleep(0.3)

    # Pause
    dashboard.pause()
    assert dashboard.state == MonitoringState.PAUSED, "Should be paused"

    # Resume
    dashboard.resume()
    assert dashboard.state == MonitoringState.RUNNING, "Should resume"

    await asyncio.sleep(0.1)

    # Stop
    await dashboard.stop()
    assert dashboard.state == MonitoringState.STOPPED, "Should be stopped"

    try:
        await asyncio.wait_for(dashboard_task, timeout=1.0)
    except asyncio.TimeoutError:
        dashboard_task.cancel()

    # Get metrics
    metrics = dashboard.get_metrics()
    assert metrics.active_orders >= 1, "Should count active orders"
    assert metrics.active_positions >= 1, "Should count positions"

    # Get dashboard output
    output = dashboard.print_dashboard()
    assert "MONITORING DASHBOARD" in output, "Should print dashboard"
    assert "Active Orders" in output or "ORDERS" in output
    assert "Open Positions" in output or "POSITIONS" in output

    logger.info("✅ MonitoringDashboard test passed")


@pytest.mark.asyncio
async def test_alert_filtering():
    """Test alert filtering."""
    logger.info("Testing alert filtering...")
    
    _, _, _, _, _, _, _, notifier, _ = await setup_test_environment()

    # Set filter to suppress INFO level alerts
    def suppress_info_alerts(alert):
        return alert.level == AlertLevel.INFO

    notifier.set_alert_filter(AlertType.ORDER_FILLED, suppress_info_alerts)

    # Try to emit INFO alert (should be suppressed)
    alert1 = await notifier.emit_alert(
        AlertType.ORDER_FILLED,
        AlertLevel.INFO,
        "Suppressed alert"
    )

    # Try to emit WARNING alert (should NOT be suppressed)
    alert2 = await notifier.emit_alert(
        AlertType.ORDER_FILLED,
        AlertLevel.WARNING,
        "Not suppressed alert"
    )

    # Check alerts
    alerts = notifier.get_alerts(alert_type=AlertType.ORDER_FILLED)
    assert len(alerts) == 1, "Should only have 1 alert (suppressed one)"
    assert alerts[0].level == AlertLevel.WARNING

    logger.info("✅ Alert filtering test passed")


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_all_tests():
    """Run all tests."""
    logger.info("Starting order monitoring tests...")
    logger.info("=" * 80)

    try:
        await test_order_status_monitoring()
        await test_orderbook_watching()
        await test_portfolio_monitoring()
        await test_event_notifications()
        await test_alert_filtering()
        await test_monitoring_dashboard()

        logger.info("=" * 80)
        logger.info("✅ ALL TESTS PASSED")
        return True

    except AssertionError as e:
        logger.error(f"❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ TEST ERROR: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
