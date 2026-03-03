#!/usr/bin/env python3
"""
Comprehensive Multi-Strategy Backtesting Pipeline
完整多策略回測管道 - 系統性測試所有7個策略組合

This script tests all 7 strategy combinations on the same market data to ensure
accurate performance comparison and benchmarking.

Strategy Combinations:
1. Cosmic: Triangular Arbitrage
2. Cosmic: Wormhole Arbitrage
3. Hummingbot: Pure Market Making
4. Hummingbot: Avellaneda-Stoikov (optimal spread)
5. LLM-TradeBot: Three-Agent Debate Framework
6. Cosmic + Hummingbot Hybrid
7. Optimal Combo: Cosmic (decisions) + Hummingbot (execution) + LLM (risk)
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtesting.market_simulator import MarketSimulator
from src.backtesting.unified_backtester import UnifiedBacktester, BacktestConfig
from src.backtesting.performance_comparator import PerformanceComparator
from src.integrations.strategy_adapters.cosmic_adapter import CosmicStrategyAdapter
from src.integrations.strategy_adapters.hummingbot_adapter import HummingbotStrategyAdapter
from src.integrations.strategy_adapters.llm_adapter import LLMTradeBotAdapter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiStrategyBacktester:
    """Orchestrates comprehensive backtesting of all strategies."""
    
    def __init__(self, initial_capital: float = 100000.0):
        """Initialize multi-strategy backtester."""
        self.initial_capital = initial_capital
        self.comparator = PerformanceComparator()
        self.results: Dict[str, Any] = {}
        self.market_snapshots: List[Any] = []
    
    async def prepare_market_data(
        self,
        start_date: datetime,
        end_date: datetime,
        symbols: List[str] = None
    ) -> List[Any]:
        """Generate consistent market data for all strategies."""
        logger.info("=" * 80)
        logger.info("STEP 1: GENERATING MARKET DATA")
        logger.info("=" * 80)
        
        if symbols is None:
            symbols = ['BTC/USD', 'ETH/USD', 'BNB/USD']
        
        simulator = MarketSimulator(
            symbols=symbols,
            initial_prices={
                'BTC/USD': 42000.0,
                'ETH/USD': 2200.0,
                'BNB/USD': 550.0
            },
            start_date=start_date,
            end_date=end_date,
            timeframe='1h'
        )
        
        logger.info(f"Generating market snapshots from {start_date} to {end_date}...")
        self.market_snapshots = list(simulator)
        logger.info(f"✓ Generated {len(self.market_snapshots)} hourly market snapshots")
        logger.info(f"  Date range: {self.market_snapshots[0].timestamp} to {self.market_snapshots[-1].timestamp}")
        logger.info(f"  Symbols: {', '.join(symbols)}")
        
        return self.market_snapshots
    
    async def test_strategy(
        self,
        strategy_name: str,
        strategy_adapter,
        strategy_config: Dict[str, Any],
        backtest_config: BacktestConfig = None
    ) -> Dict[str, Any]:
        """Test a single strategy and return results."""
        logger.info("\n" + "=" * 80)
        logger.info(f"TESTING STRATEGY: {strategy_name}")
        logger.info("=" * 80)
        
        if backtest_config is None:
            backtest_config = BacktestConfig(
                initial_capital=self.initial_capital,
                maker_fee=0.001,
                taker_fee=0.002,
                max_position_size=0.5,
                slippage_bps=2.0,
                use_stop_loss=True,
                use_take_profit=True
            )
        
        try:
            # Initialize strategy with config
            logger.info(f"Initializing {strategy_name}...")
            strategy = strategy_adapter(config=strategy_config)
            
            # Run backtest
            logger.info(f"Running backtest ({len(self.market_snapshots)} snapshots)...")
            backtester = UnifiedBacktester(
                strategy=strategy,
                config=backtest_config
            )
            
            start_time = datetime.now()
            metrics = await backtester.run_backtest(self.market_snapshots)
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            # Get summary
            summary = backtester.get_backtest_summary()
            
            # Score the strategy
            score = self.comparator.add_strategy_result(strategy_name, metrics)
            
            # Compile results
            result = {
                'strategy_name': strategy_name,
                'status': 'completed',
                'execution_time_seconds': elapsed_time,
                'metrics': {
                    'total_return_pct': metrics.total_return_pct,
                    'annual_return_pct': metrics.annual_return_pct,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'sortino_ratio': metrics.extra_metrics.get('sortino_ratio', 0.0),
                    'max_drawdown_pct': metrics.max_drawdown_pct,
                    'total_trades': metrics.total_trades,
                    'winning_trades': metrics.winning_trades,
                    'losing_trades': metrics.losing_trades,
                    'win_rate': metrics.win_rate,
                    'total_pnl': metrics.total_pnl,
                    'daily_avg_profit': metrics.daily_avg_profit,
                    'avg_trade_duration': metrics.avg_trade_duration,
                    'volatility_pct': metrics.extra_metrics.get('volatility_pct', 0.0),
                    'calmar_ratio': metrics.extra_metrics.get('calmar_ratio', 0.0),
                    'profit_factor': metrics.extra_metrics.get('profit_factor', 0.0)
                },
                'summary': summary,
                'scores': {
                    'overall_score': score.overall_score,
                    'risk_adjusted_score': score.risk_adjusted_score,
                    'return_score': score.return_score,
                    'risk_management_score': score.risk_management_score,
                    'trade_quality_score': score.trade_quality_score
                }
            }
            
            # Log results
            logger.info(f"\n✓ {strategy_name} completed in {elapsed_time:.2f}s")
            logger.info(f"  Total Return: {metrics.total_return_pct:.2f}%")
            logger.info(f"  Annual Return: {metrics.annual_return_pct:.2f}%")
            logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
            logger.info(f"  Max Drawdown: {metrics.max_drawdown_pct:.2f}%")
            logger.info(f"  Win Rate: {metrics.win_rate:.2f}%")
            logger.info(f"  Trades: {metrics.total_trades} (W:{metrics.winning_trades} L:{metrics.losing_trades})")
            logger.info(f"  Overall Score: {score.overall_score:.2f}/100")
            
            self.results[strategy_name] = result
            return result
        
        except Exception as e:
            logger.error(f"✗ {strategy_name} FAILED: {e}", exc_info=True)
            result = {
                'strategy_name': strategy_name,
                'status': 'failed',
                'error': str(e)
            }
            self.results[strategy_name] = result
            return result
    
    async def run_all_strategies(self) -> Dict[str, Any]:
        """Run all 7 strategy combinations sequentially."""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: RUNNING ALL 7 STRATEGY COMBINATIONS")
        logger.info("=" * 80)
        
        # Define all 7 strategies
        strategies_to_test = [
            {
                'name': 'Cosmic: Triangular Arbitrage',
                'adapter': CosmicStrategyAdapter,
                'config': {
                    'timeframe': '1h',
                    'lookback_periods': 20,
                    'volatility_threshold': 0.02,
                    'min_confidence': 0.6,
                    'max_position_size': 0.05,
                    'arbitrage_type': 'triangular'
                }
            },
            {
                'name': 'Cosmic: Wormhole Arbitrage',
                'adapter': CosmicStrategyAdapter,
                'config': {
                    'timeframe': '1h',
                    'lookback_periods': 20,
                    'volatility_threshold': 0.02,
                    'min_confidence': 0.6,
                    'max_position_size': 0.05,
                    'arbitrage_type': 'wormhole'
                }
            },
            {
                'name': 'Hummingbot: Pure Market Making',
                'adapter': HummingbotStrategyAdapter,
                'config': {
                    'strategy_type': 'pure_market_making',
                    'bid_spread': 0.001,
                    'ask_spread': 0.001,
                    'order_amount': 1.0,
                    'volatility_sensitivity': 0.5
                }
            },
            {
                'name': 'Hummingbot: Avellaneda-Stoikov',
                'adapter': HummingbotStrategyAdapter,
                'config': {
                    'strategy_type': 'avellaneda_stoikov',
                    'volatility_sensitivity': 0.8,
                    'inventory_target_base_pct': 0.5,
                    'max_order_size': 10.0
                }
            },
            {
                'name': 'LLM-TradeBot: Debate Framework',
                'adapter': LLMTradeBotAdapter,
                'config': {
                    'num_agents': 3,
                    'debate_rounds': 2,
                    'consensus_threshold': 0.66,
                    'risk_level': 'moderate'
                }
            },
            {
                'name': 'Hybrid: Cosmic + Hummingbot',
                'adapter': CosmicStrategyAdapter,  # Primary
                'config': {
                    'timeframe': '1h',
                    'lookback_periods': 20,
                    'volatility_threshold': 0.02,
                    'min_confidence': 0.6,
                    'max_position_size': 0.05,
                    'use_hummingbot_execution': True
                }
            },
            {
                'name': 'Optimal Combo: Cosmic+Hummingbot+LLM',
                'adapter': CosmicStrategyAdapter,  # Primary decision maker
                'config': {
                    'timeframe': '1h',
                    'lookback_periods': 20,
                    'volatility_threshold': 0.02,
                    'min_confidence': 0.6,
                    'max_position_size': 0.05,
                    'use_hummingbot_execution': True,
                    'use_llm_risk_check': True
                }
            }
        ]
        
        # Run each strategy
        for i, strategy_spec in enumerate(strategies_to_test, 1):
            logger.info(f"\n[{i}/7] Testing {strategy_spec['name']}...")
            await self.test_strategy(
                strategy_name=strategy_spec['name'],
                strategy_adapter=strategy_spec['adapter'],
                strategy_config=strategy_spec['config']
            )
    
    def generate_comparison_report(self) -> str:
        """Generate comprehensive comparison report."""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: GENERATING COMPARISON REPORT")
        logger.info("=" * 80)
        
        report = self.comparator.generate_comparison_report()
        logger.info("\n" + report)
        return report
    
    def export_results(self, output_dir: Path = None) -> Path:
        """Export all results to JSON."""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4: EXPORTING RESULTS")
        logger.info("=" * 80)
        
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "reports" / "benchmarking"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export JSON results
        json_file = output_dir / f"strategy_benchmarking_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"✓ Exported results to {json_file}")
        
        # Export comparison JSON
        comparison_file = output_dir / "performance_comparison.json"
        self.comparator.export_comparison_json(str(comparison_file))
        logger.info(f"✓ Exported comparison to {comparison_file}")
        
        return output_dir
    
    async def run_complete_pipeline(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Run complete benchmarking pipeline."""
        if start_date is None:
            start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        if end_date is None:
            end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)
        
        logger.info("=" * 80)
        logger.info("COSMIC AI - COMPREHENSIVE STRATEGY BENCHMARKING PIPELINE")
        logger.info("=" * 80)
        logger.info(f"Start Time: {datetime.now()}")
        logger.info(f"Date Range: {start_date} to {end_date}")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        
        try:
            # Prepare market data
            await self.prepare_market_data(start_date, end_date)
            
            # Run all strategies
            await self.run_all_strategies()
            
            # Generate comparison
            comparison_report = self.generate_comparison_report()
            
            # Export results
            output_dir = self.export_results()
            
            logger.info("\n" + "=" * 80)
            logger.info("BENCHMARKING PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("=" * 80)
            logger.info(f"End Time: {datetime.now()}")
            logger.info(f"Results saved to: {output_dir}")
            
            return {
                'status': 'success',
                'results': self.results,
                'comparison_report': comparison_report,
                'output_directory': str(output_dir)
            }
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e)
            }


async def main():
    """Main entry point."""
    logger.info("Initializing Comprehensive Backtesting Pipeline")
    
    try:
        # Create backtester
        backtester = MultiStrategyBacktester(initial_capital=100000.0)
        
        # Run pipeline
        result = await backtester.run_complete_pipeline()
        
        if result['status'] == 'success':
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Pipeline initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
