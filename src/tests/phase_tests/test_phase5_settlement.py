#!/usr/bin/env python3
"""
Test Trade Settlement and Reporting System
交易結算和報告系統測試

Integration tests for trade settlement and reporting components.
Tests:
- TradeSettlementEngine functionality
- PerformanceReporter calculations
- TradeAnalytics analysis
- ReportExporter export formats
- ComplianceTracker recording
"""

import asyncio
import logging
import pytest
from datetime import datetime, timedelta

from src.phase5.order_management import (
    Trade, OrderSide, Order, OrderType, OrderQuantity, OrderPrice
)
from src.phase5.trade_settlement import (
    TradeSettlementEngine, PerformanceReporter, TradeAnalytics,
    ReportExporter, ComplianceTracker, ReportFormat, SettlementStatus,
    TradeOutcome
)
from src.phase5.exchange_connector import ExchangeType


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradeSettlementTest")


# ============================================================================
# Test Setup
# ============================================================================

def create_test_trade(
    symbol: str = "BTC/USDT",
    entry_price: float = 50000.0,
    exit_price: float = 51000.0,
    quantity: float = 1.0,
    side: OrderSide = OrderSide.BUY,
    entry_fees: float = 10.0,
    exit_fees: float = 10.0
) -> Trade:
    """Create a test trade."""
    now = datetime.utcnow()
    
    realized_pnl = (
        (exit_price - entry_price) * quantity - entry_fees - exit_fees
        if side == OrderSide.BUY
        else (entry_price - exit_price) * quantity - entry_fees - exit_fees
    )
    
    roi_percent = (realized_pnl / (entry_price * quantity)) * 100 if entry_price > 0 else 0
    
    return Trade(
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        entry_quantity=quantity,
        entry_time=now - timedelta(hours=1),
        entry_fees=entry_fees,
        exit_price=exit_price,
        exit_quantity=quantity,
        exit_time=now,
        exit_fees=exit_fees,
        realized_pnl=realized_pnl,
        roi_percent=roi_percent,
        exchange_type=ExchangeType.BINANCE
    )


# ============================================================================
# Test Cases
# ============================================================================

@pytest.mark.asyncio
async def test_trade_settlement():
    """Test trade settlement."""
    logger.info("Testing TradeSettlementEngine...")
    
    from src.phase5.order_management import Position, PositionStatus
    
    engine = TradeSettlementEngine()
    
    # Create test trade
    trade = create_test_trade()
    
    # Create test position
    position = Position(
        exchange_type=ExchangeType.BINANCE,
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        entry_price=50000.0,
        entry_quantity=1.0,
        current_quantity=0.0,
        current_price=51000.0,
        status=PositionStatus.CLOSED
    )
    
    # Confirm trade
    settlement = await engine.confirm_trade(trade, position)
    
    assert settlement is not None, "Should return settlement"
    assert settlement.status == SettlementStatus.CONFIRMED
    assert settlement.trade_id == trade.trade_id
    assert settlement.net_pnl == trade.realized_pnl
    assert len(engine.settlements) == 1
    
    # Mark settled
    success = await engine.mark_settled(settlement.settlement_id)
    assert success, "Should mark settled"
    assert settlement.status == SettlementStatus.SETTLED
    
    # Get unsettled
    unsettled = engine.get_unsettled_settlements()
    assert len(unsettled) == 0, "Should have no unsettled"
    
    logger.info("✅ TradeSettlementEngine test passed")


@pytest.mark.asyncio
async def test_performance_reporter():
    """Test performance calculations."""
    logger.info("Testing PerformanceReporter...")
    
    reporter = PerformanceReporter()
    
    # Create test trades
    trades = [
        create_test_trade(entry_price=50000, exit_price=51000, quantity=1.0),  # Win
        create_test_trade(entry_price=50000, exit_price=49500, quantity=1.0),  # Loss
        create_test_trade(entry_price=50000, exit_price=49000, quantity=1.0),  # Loss
        create_test_trade(entry_price=50000, exit_price=52000, quantity=1.0),  # Win
    ]
    
    # Calculate metrics
    metrics = await reporter.calculate_metrics(
        trades=trades,
        initial_capital=10000.0,
        current_capital=10500.0
    )
    
    assert metrics.total_trades == 4, "Should count all trades"
    assert metrics.winning_trades == 2, "Should count wins"
    assert metrics.losing_trades == 2, "Should count losses"
    assert metrics.win_rate > 0, "Should calculate win rate"
    assert metrics.return_percent > 0, "Should calculate return"
    assert metrics.profit_factor > 0, "Should calculate profit factor"
    assert metrics.average_trade_duration is not None, "Should calculate duration"
    
    logger.info(f"  Win Rate: {metrics.win_rate:.1f}%")
    logger.info(f"  Return: {metrics.return_percent:.2f}%")
    logger.info("✅ PerformanceReporter test passed")


@pytest.mark.asyncio
async def test_trade_analytics():
    """Test trade analytics."""
    logger.info("Testing TradeAnalytics...")
    
    analytics = TradeAnalytics()
    
    # Create test trades
    winning_trade = create_test_trade(entry_price=50000, exit_price=51000)
    losing_trade = create_test_trade(entry_price=50000, exit_price=49500)
    neutral_trade = create_test_trade(entry_price=50000, exit_price=50200)  # Will be win after fees
    
    # Classify trades
    assert analytics.classify_trade(winning_trade) == TradeOutcome.WINNING
    assert analytics.classify_trade(losing_trade) == TradeOutcome.LOSING
    
    # Test consecutive wins/losses
    trades = [winning_trade, winning_trade, losing_trade]
    wins, losses = analytics.get_consecutive_wins_losses(trades)
    assert wins == 0, "Should detect recent loss"
    assert losses == 1, "Should count recent loss"
    
    # Test drawdown
    drawdown = analytics.calculate_drawdown(trades)
    assert drawdown >= 0, "Drawdown should be non-negative"
    
    # Test best/worst performers
    all_trades = [winning_trade, losing_trade, neutral_trade]
    best = analytics.find_best_performers(all_trades, top_n=1)
    assert len(best) == 1, "Should find best"
    assert best[0].realized_pnl > 0, "Best should be winning"
    
    worst = analytics.find_worst_performers(all_trades, bottom_n=1)
    assert len(worst) == 1, "Should find worst"
    assert worst[0].realized_pnl < 0, "Worst should be losing"
    
    # Test symbol statistics
    stats = analytics.get_symbol_statistics(all_trades)
    assert "BTC/USDT" in stats, "Should have symbol stats"
    assert stats["BTC/USDT"]["total_trades"] == 3
    assert stats["BTC/USDT"]["win_rate"] > 0
    
    logger.info("✅ TradeAnalytics test passed")


@pytest.mark.asyncio
async def test_report_exporter():
    """Test report export."""
    logger.info("Testing ReportExporter...")
    
    exporter = ReportExporter()
    
    # Create test trades
    trades = [
        create_test_trade(entry_price=50000, exit_price=51000),
        create_test_trade(entry_price=50000, exit_price=49500),
    ]
    
    # Test CSV export
    csv_report = await exporter.export_trades(trades, ReportFormat.CSV)
    assert csv_report, "Should generate CSV"
    assert "Trade ID" in csv_report, "CSV should have headers"
    assert "BTC/USDT" in csv_report, "CSV should have trades"
    
    # Test JSON export
    json_report = await exporter.export_trades(trades, ReportFormat.JSON)
    assert json_report, "Should generate JSON"
    assert "trade_id" in json_report, "JSON should have fields"
    
    # Test TEXT export
    text_report = await exporter.export_trades(trades, ReportFormat.TEXT)
    assert text_report, "Should generate text"
    assert "TRADE REPORT" in text_report, "Text should have title"
    
    logger.info("✅ ReportExporter test passed")


@pytest.mark.asyncio
async def test_performance_metrics_export():
    """Test performance metrics export."""
    logger.info("Testing Performance Metrics Export...")
    
    from src.phase5.trade_settlement import PerformanceMetrics
    
    reporter = PerformanceReporter()
    exporter = ReportExporter()
    
    # Create test trades and metrics
    trades = [
        create_test_trade(entry_price=50000, exit_price=51000),
        create_test_trade(entry_price=50000, exit_price=49500),
    ]
    
    metrics = await reporter.calculate_metrics(
        trades=trades,
        initial_capital=10000.0,
        current_capital=10500.0
    )
    
    # Export metrics
    json_metrics = await exporter.export_metrics(metrics, ReportFormat.JSON)
    assert json_metrics, "Should generate JSON metrics"
    assert "win_rate" in json_metrics, "JSON should have metrics"
    
    text_metrics = await exporter.export_metrics(metrics, ReportFormat.TEXT)
    assert text_metrics, "Should generate text metrics"
    assert "PERFORMANCE METRICS" in text_metrics, "Text should have title"
    assert "Win Rate" in text_metrics or "win_rate" in text_metrics, "Should show win rate"
    
    logger.info("✅ Performance Metrics Export test passed")


@pytest.mark.asyncio
async def test_compliance_tracker():
    """Test compliance tracking."""
    logger.info("Testing ComplianceTracker...")
    
    tracker = ComplianceTracker()
    
    # Create test trade
    trade = create_test_trade()
    
    # Record execution
    await tracker.record_trade_execution(
        trade=trade,
        execution_price=50000.0,
        execution_quantity=1.0
    )
    
    assert len(tracker.compliance_records) == 1, "Should record execution"
    
    # Get compliance report
    report = tracker.get_compliance_report(days=1)
    assert report["total_trades"] == 1, "Should count trades"
    assert report["total_volume"] > 0, "Should calculate volume"
    assert report["total_fees"] > 0, "Should calculate fees"
    
    logger.info("✅ ComplianceTracker test passed")


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_all_tests():
    """Run all tests."""
    logger.info("Starting trade settlement tests...")
    logger.info("=" * 80)

    try:
        await test_trade_settlement()
        await test_performance_reporter()
        await test_trade_analytics()
        await test_report_exporter()
        await test_performance_metrics_export()
        await test_compliance_tracker()

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
