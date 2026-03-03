#!/usr/bin/env python3
"""
End-to-End Backtesting Test
完整端到端回測測試 - 驗證整個回測流程

This script runs a complete backtest with one strategy (Cosmic) and generates
performance metrics and comparisons.
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtesting.market_simulator import MarketSimulator
from src.backtesting.unified_backtester import UnifiedBacktester, BacktestConfig
from src.backtesting.performance_comparator import PerformanceComparator
from src.integrations.strategy_adapters.cosmic_adapter import CosmicStrategyAdapter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_cosmic_backtest():
    """Run backtest with Cosmic strategy."""
    logger.info("=" * 80)
    logger.info("COSMIC STRATEGY BACKTEST - END-TO-END TEST")
    logger.info("=" * 80)
    
    # 1. Initialize market simulator
    logger.info("\n1. Initializing Market Simulator...")
    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)
    
    simulator = MarketSimulator(
        symbols=['BTC/USD', 'ETH/USD', 'BNB/USD'],
        initial_prices={
            'BTC/USD': 42000.0,
            'ETH/USD': 2200.0,
            'BNB/USD': 550.0
        },
        start_date=start_date,
        end_date=end_date,
        timeframe='1h'
    )
    
    # Generate market data
    logger.info("Collecting market snapshots...")
    snapshots = list(simulator)
    logger.info(f"Collected {len(snapshots)} market snapshots")
    
    # 2. Initialize Cosmic strategy
    logger.info("\n2. Initializing Cosmic Strategy Adapter...")
    cosmic_config = {
        'timeframe': '1h',
        'lookback_periods': 20,
        'volatility_threshold': 0.02,
        'min_confidence': 0.6,
        'max_position_size': 0.05
    }
    cosmic_strategy = CosmicStrategyAdapter(config=cosmic_config)
    
    # 3. Configure backtester
    logger.info("\n3. Configuring Backtester...")
    backtest_config = BacktestConfig(
        initial_capital=100000.0,
        maker_fee=0.001,
        taker_fee=0.002,
        max_position_size=0.5,
        slippage_bps=2.0,
        use_stop_loss=True,
        use_take_profit=True
    )
    
    # 4. Run backtest
    logger.info("\n4. Running Backtest...")
    backtester = UnifiedBacktester(
        strategy=cosmic_strategy,
        config=backtest_config
    )
    
    metrics = await backtester.run_backtest(snapshots)
    
    # 5. Display results
    logger.info("\n" + "=" * 80)
    logger.info("BACKTEST RESULTS - COSMIC STRATEGY")
    logger.info("=" * 80)
    
    summary = backtester.get_backtest_summary()
    logger.info(f"\nBacktest Summary:")
    logger.info(f"  Market snapshots processed: {summary['market_snapshots_processed']}")
    logger.info(f"  Signals generated: {summary['signals_generated']}")
    logger.info(f"  Trades executed: {summary['trades_executed']}")
    logger.info(f"  Final cash: ${summary['final_cash']:,.2f}")
    logger.info(f"  Final portfolio value: ${summary['final_portfolio_value']:,.2f}")
    
    logger.info(f"\nPerformance Metrics:")
    logger.info(f"  Total Return: {metrics.total_return_pct:.2f}%")
    logger.info(f"  Annual Return: {metrics.annual_return_pct:.2f}%")
    logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
    logger.info(f"  Max Drawdown: {metrics.max_drawdown_pct:.2f}%")
    logger.info(f"  Total Trades: {metrics.total_trades}")
    logger.info(f"  Winning Trades: {metrics.winning_trades}")
    logger.info(f"  Losing Trades: {metrics.losing_trades}")
    logger.info(f"  Win Rate: {metrics.win_rate:.2f}%")
    logger.info(f"  Total P&L: ${metrics.total_pnl:,.2f}")
    logger.info(f"  Avg Trade Duration: {metrics.avg_trade_duration:.2f} hours")
    logger.info(f"  Daily Avg Profit: ${metrics.daily_avg_profit:,.2f}")
    
    logger.info(f"\nExtra Metrics:")
    logger.info(f"  Sortino Ratio: {metrics.extra_metrics.get('sortino_ratio', 0.0):.2f}")
    logger.info(f"  Volatility: {metrics.extra_metrics.get('volatility_pct', 0.0):.2f}%")
    logger.info(f"  Calmar Ratio: {metrics.extra_metrics.get('calmar_ratio', 0.0):.2f}")
    logger.info(f"  Profit Factor: {metrics.extra_metrics.get('profit_factor', 0.0):.2f}")
    logger.info(f"  Consecutive Wins: {metrics.extra_metrics.get('consecutive_wins', 0)}")
    logger.info(f"  Consecutive Losses: {metrics.extra_metrics.get('consecutive_losses', 0)}")
    
    # 6. Add to comparator
    logger.info("\n5. Adding Results to Comparator...")
    comparator = PerformanceComparator()
    score = comparator.add_strategy_result('Cosmic', metrics)
    
    logger.info(f"\nStrategy Scores:")
    logger.info(f"  Overall Score: {score.overall_score:.2f}")
    logger.info(f"  Risk-Adjusted Score: {score.risk_adjusted_score:.2f}")
    logger.info(f"  Return Score: {score.return_score:.2f}")
    logger.info(f"  Risk Management Score: {score.risk_management_score:.2f}")
    logger.info(f"  Trade Quality Score: {score.trade_quality_score:.2f}")
    
    # 7. Generate report
    logger.info("\n6. Generating Comparison Report...")
    report = comparator.generate_comparison_report()
    logger.info("\n" + report)
    
    # 8. Export results
    logger.info("\n7. Exporting Results...")
    reports_dir = Path(__file__).parent.parent.parent / "reports" / "benchmarking"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    json_file = reports_dir / "cosmic_backtest_results.json"
    comparator.export_comparison_json(str(json_file))
    logger.info(f"Results exported to {json_file}")
    
    logger.info("\n" + "=" * 80)
    logger.info("END-TO-END TEST COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)
    
    return metrics, comparator


def main():
    """Main entry point."""
    logger.info("Starting End-to-End Backtesting Pipeline")
    logger.info(f"Timestamp: {datetime.now()}")
    
    try:
        # Run async backtest
        metrics, comparator = asyncio.run(run_cosmic_backtest())
        
        # Return success code
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Backtest failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
