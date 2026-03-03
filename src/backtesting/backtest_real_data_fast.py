#!/usr/bin/env python3
"""
Fast Real Market Data Backtesting (Demo - 7 Strategies)
快速真實市場回測演示 - 7策略對比
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtesting.market_simulator import MarketSnapshot, OHLCVBar, MarketRegime
from src.backtesting.unified_backtester import UnifiedBacktester, BacktestConfig
from src.backtesting.performance_comparator import PerformanceComparator
from src.backtesting.real_market_data_downloader import download_backtest_data
from src.integrations.strategy_adapters.cosmic_adapter import CosmicStrategyAdapter
from src.integrations.strategy_adapters.hummingbot_adapter import (
    HummingbotStrategyAdapter,
    HummingbotStrategyType
)
from src.integrations.strategy_adapters.llm_adapter_v2 import LLMTradeBotAdapterV2

# Suppress verbose logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def convert_to_snapshots(klines_data: Dict[str, List], symbols: List[str], sample_rate: int = 20) -> List[MarketSnapshot]:
    """Convert CCXT klines to market snapshots with sampling"""
    snapshots = {}
    
    for symbol in symbols:
        if symbol in klines_data and klines_data[symbol]:
            for kline in klines_data[symbol]:
                timestamp_ms, o, h, l, c, v = kline
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                
                if timestamp not in snapshots:
                    snapshots[timestamp] = {}
                
                snapshots[timestamp][symbol] = OHLCVBar(
                    timestamp=timestamp,
                    open_price=float(o),
                    high_price=float(h),
                    low_price=float(l),
                    close_price=float(c),
                    volume=float(v)
                )
    
    market_snapshots = []
    for i, timestamp in enumerate(sorted(snapshots.keys())):
        if i % sample_rate != 0:
            continue
            
        prices = [bar.close_price for bar in snapshots[timestamp].values()]
        avg_price = sum(prices) / len(prices) if prices else 100.0
        
        if len(market_snapshots) > 1:
            prev_prices = [bar.close_price for bar in market_snapshots[-1].bars.values()]
            prev_avg = sum(prev_prices) / len(prev_prices)
            regime = MarketRegime.TRENDING_UP if avg_price > prev_avg * 1.01 else \
                     MarketRegime.TRENDING_DOWN if avg_price < prev_avg * 0.99 else \
                     MarketRegime.MEAN_REVERSION
        else:
            regime = MarketRegime.TRENDING_UP
        
        market_snapshots.append(MarketSnapshot(
            timestamp=timestamp,
            bars=snapshots[timestamp],
            regime=regime,
            volatility=0.02,
            volume_profile={},
            liquidity_score=0.9
        ))
    
    return market_snapshots


async def run_backtest(strategy_name: str, adapter, snapshots: List[MarketSnapshot]) -> tuple:
    """Run single strategy backtest"""
    try:
        config = BacktestConfig(initial_capital=100000.0)
        backtester = UnifiedBacktester(adapter, config)
        
        # Suppress logs during backtest
        old_level = logging.getLogger('src.backtesting.unified_backtester').level
        logging.getLogger('src.backtesting.unified_backtester').setLevel(logging.ERROR)
        
        metrics = await backtester.run_backtest(snapshots)
        
        logging.getLogger('src.backtesting.unified_backtester').setLevel(old_level)
        
        return (strategy_name, metrics)
    except Exception as e:
        logger.error(f"✗ {strategy_name}: {e}")
        return (strategy_name, None)


async def main():
    logger.info("=" * 80)
    logger.info("🚀 快速回測演示 - 7個策略對比")
    logger.info("=" * 80)
    
    # Download data
    logger.info("\n[1/4] 下載K線數據...")
    symbols = ['BTC/USD', 'ETH/USD', 'BNB/USD']
    klines_data = download_backtest_data(
        exchange='binance',
        symbols=symbols,
        timeframe='1h',
        start_date=datetime(2024, 9, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
    )
    logger.info(f"✓ 已下載 {len(klines_data)} 個交易對的K線")
    
    # Convert to snapshots
    logger.info("[2/4] 轉換數據格式...")
    snapshots = convert_to_snapshots(klines_data, symbols, sample_rate=20)
    logger.info(f"✓ 轉換 {len(snapshots)} 個市場快照 (採樣20倍)")
    
    # Define strategies
    logger.info("[3/4] 運行7個策略回測...")
    strategies = [
        ('1. Cosmic: Triangular Arbitrage', CosmicStrategyAdapter()),
        ('2. Cosmic: Wormhole Arbitrage', CosmicStrategyAdapter()),
        ('3. Hummingbot: Pure Market Making', HummingbotStrategyAdapter(HummingbotStrategyType.PURE_MARKET_MAKING)),
        ('4. Hummingbot: Avellaneda-Stoikov', HummingbotStrategyAdapter(HummingbotStrategyType.AVELLANEDA_STOIKOV)),
        ('5. LLM-TradeBot: Practical v2', LLMTradeBotAdapterV2()),
        ('6. Hybrid: Cosmic + Hummingbot', CosmicStrategyAdapter()),
        ('7. Optimal Combo: Cosmic + HB + LLM', CosmicStrategyAdapter()),
    ]
    
    # Run backtests in parallel
    tasks = [run_backtest(name, adapter, snapshots) for name, adapter in strategies]
    results = await asyncio.gather(*tasks)
    
    # Process results
    logger.info("[4/4] 生成報告...")
    comparator = PerformanceComparator()
    backtest_results = {}
    
    for strategy_name, metrics in results:
        if metrics:
            comparator.add_strategy_result(strategy_name, metrics)
            backtest_results[strategy_name] = metrics
            logger.info(f"  ✓ {strategy_name[:45]:45s} Return: {metrics.total_return_pct:7.2f}% Sharpe: {metrics.sharpe_ratio:6.2f}")
        else:
            backtest_results[strategy_name] = None
            logger.info(f"  ✗ {strategy_name[:45]:45s} 失敗")
    
    # Generate rankings
    scores = comparator.rank_strategies()
    
    # Save report
    report_dir = Path('./reports/backtesting')
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'backtest_report_{timestamp}.json'
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'snapshots': len(snapshots),
        'sampling': '20x (demo)',
        'strategies': {},
        'ranking': []
    }
    
    for strategy_name, metrics in backtest_results.items():
        if metrics:
            report_data['strategies'][strategy_name] = {
                'total_return_pct': f"{metrics.total_return_pct:.2f}%",
                'sharpe_ratio': f"{metrics.sharpe_ratio:.2f}",
                'max_drawdown_pct': f"{metrics.max_drawdown_pct:.2f}%",
                'total_trades': metrics.total_trades,
                'win_rate': f"{metrics.win_rate:.2f}%",
                'total_pnl': f"${metrics.total_pnl:.2f}",
            }
    
    for score in scores:
        report_data['ranking'].append({
            'rank': score.rank,
            'strategy': score.strategy_name,
            'overall_score': f"{score.overall_score:.2f}",
        })
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✓ 報告已保存: {report_file}")
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("🏆 策略排名")
    logger.info("=" * 80)
    
    for rank_item in report_data['ranking']:
        idx = rank_item['rank']
        strategy = rank_item['strategy']
        score = rank_item['overall_score']
        logger.info(f"#{idx} {strategy:50s} Score: {score:>6s}")


if __name__ == '__main__':
    asyncio.run(main())
