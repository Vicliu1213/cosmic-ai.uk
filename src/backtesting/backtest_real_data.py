#!/usr/bin/env python3
"""
Real Market Data Backtesting Pipeline
真實市場數據回測管道 - 使用實際下載的K線進行7策略對比

This script:
1. 自動下載真實K線數據（如果尚未快取）
2. 轉換為回測格式
3. 運行所有7個策略
4. 生成性能對比報告
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.backtesting.market_simulator import MarketSnapshot, OHLCVBar, MarketRegime
from src.backtesting.unified_backtester import UnifiedBacktester, BacktestConfig
from src.backtesting.performance_comparator import PerformanceComparator
from src.backtesting.real_market_data_downloader import download_backtest_data
from src.integrations.strategy_adapters.cosmic_adapter import CosmicStrategyAdapter
from src.integrations.strategy_adapters.hummingbot_adapter import HummingbotStrategyAdapter
from src.integrations.strategy_adapters.llm_adapter import LLMTradeBotAdapter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_ccxt_klines_to_snapshots(
    klines_data: Dict[str, List],
    symbols: List[str]
) -> List[MarketSnapshot]:
    """
    將CCXT K線數據轉換為回測格式
    
    Args:
        klines_data: {symbol: [[timestamp, o, h, l, c, v], ...]}
        symbols: 交易對列表
    
    Returns:
        市場快照列表
    """
    
    snapshots = {}
    
    # 初始化每個符號的數據
    for symbol in symbols:
        if symbol in klines_data and klines_data[symbol]:
            klines = klines_data[symbol]
            for kline in klines:
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
    
    # 轉換為時間排序的快照列表
    market_snapshots = []
    for timestamp in sorted(snapshots.keys()):
        # 計算市場指標
        prices = [bar.close_price for bar in snapshots[timestamp].values()]
        avg_price = sum(prices) / len(prices) if prices else 100.0
        
        # 簡單波動率估計
        volatility = 0.02  # 默認2%
        
        # 流動性評分（假設全部流動）
        liquidity_score = 0.9
        
        # 市場政權（基於價格趨勢的簡單啟發式）
        if len(market_snapshots) > 1:
            prev_prices = [bar.close_price for bar in market_snapshots[-1].bars.values()]
            prev_avg = sum(prev_prices) / len(prev_prices)
            if avg_price > prev_avg * 1.01:
                regime = MarketRegime.TRENDING_UP
            elif avg_price < prev_avg * 0.99:
                regime = MarketRegime.TRENDING_DOWN
            else:
                regime = MarketRegime.MEAN_REVERSION
        else:
            regime = MarketRegime.MEAN_REVERSION
        
        snapshot = MarketSnapshot(
            timestamp=timestamp,
            bars=snapshots[timestamp],
            regime=regime,
            volatility=volatility,
            volume_profile={symbol: bar.volume for symbol, bar in snapshots[timestamp].items()},
            liquidity_score=liquidity_score
        )
        market_snapshots.append(snapshot)
    
    logger.info(f"✓ 轉換 {len(market_snapshots)} 個市場快照")
    return market_snapshots


async def backtest_strategy(
    strategy_name: str,
    strategy_adapter,
    strategy_config: Dict[str, Any],
    market_snapshots: List[MarketSnapshot],
    initial_capital: float = 100000.0
):
    """運行單個策略的回測"""
    
    logger.info(f"\n{'='*80}")
    logger.info(f"[{strategy_name}] 開始回測")
    logger.info(f"{'='*80}")
    
    try:
        # 初始化策略
        logger.info(f"初始化 {strategy_name}...")
        strategy = strategy_adapter(config=strategy_config)
        
        # 創建回測器
        config = BacktestConfig(initial_capital=initial_capital)
        backtester = UnifiedBacktester(strategy=strategy, config=config)
        
        # 運行回測
        logger.info(f"運行回測 ({len(market_snapshots)} 個快照)...")
        metrics = await backtester.run_backtest(market_snapshots)
        
        logger.info(f"✓ {strategy_name} 回測完成")
        logger.info(f"  收益: {metrics.total_return_pct:.2f}%")
        logger.info(f"  Sharpe比率: {metrics.sharpe_ratio:.2f}")
        logger.info(f"  勝率: {metrics.win_rate:.2f}%")
        logger.info(f"  交易數: {metrics.total_trades}")
        
        return strategy_name, metrics
        
    except Exception as e:
        logger.error(f"✗ {strategy_name} 回測失敗: {e}")
        import traceback
        traceback.print_exc()
        return strategy_name, None


async def run_all_strategies_backtest(
    market_snapshots: List[MarketSnapshot],
    initial_capital: float = 100000.0
) -> Dict[str, Any]:
    """運行所有7個策略的回測"""
    
    # 定義所有策略
    strategies = [
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
            'adapter': CosmicStrategyAdapter,
            'config': {
                'timeframe': '1h',
                'lookback_periods': 20,
                'volatility_threshold': 0.015,
                'min_confidence': 0.65,
                'max_position_size': 0.1,
                'arbitrage_type': 'triangular',
                'use_hybrid_execution': True
            }
        },
        {
            'name': 'Optimal Combo: Cosmic + Hummingbot + LLM',
            'adapter': CosmicStrategyAdapter,
            'config': {
                'timeframe': '1h',
                'lookback_periods': 25,
                'volatility_threshold': 0.018,
                'min_confidence': 0.70,
                'max_position_size': 0.08,
                'arbitrage_type': 'wormhole',
                'use_hybrid_execution': True,
                'enable_llm_risk_check': True
            }
        }
    ]
    
    # 並行運行所有策略
    tasks = [
        backtest_strategy(
            strategy['name'],
            strategy['adapter'],
            strategy['config'],
            market_snapshots,
            initial_capital
        )
        for strategy in strategies
    ]
    
    results = await asyncio.gather(*tasks)
    
    # 整理結果
    backtest_results = {}
    for strategy_name, metrics in results:
        backtest_results[strategy_name] = metrics
    
    return backtest_results


async def main():
    """主函數"""
    
    logger.info("="*80)
    logger.info("宇宙AI交易系統 - 真實數據回測管道")
    logger.info("="*80)
    
    # Step 1: 下載真實K線數據
    logger.info("\n[Step 1] 下載真實K線數據")
    logger.info("-"*80)
    
    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)
    symbols = ['BTC/USD', 'ETH/USD', 'BNB/USD']
    
    klines_data = download_backtest_data(
        exchange='binance',
        symbols=symbols,
        timeframe='1h',
        start_date=start_date,
        end_date=end_date
    )
    
    # 檢查下載結果
    valid_symbols = []
    for symbol in symbols:
        if klines_data.get(symbol):
            valid_symbols.append(symbol)
            logger.info(f"✓ {symbol}: {len(klines_data[symbol])} 根K線")
        else:
            logger.warning(f"✗ {symbol}: 下載失敗")
    
    if not valid_symbols:
        logger.error("❌ 沒有成功下載任何數據")
        return
    
    # Step 2: 轉換為回測格式
    logger.info("\n[Step 2] 轉換數據格式")
    logger.info("-"*80)
    
    market_snapshots = convert_ccxt_klines_to_snapshots(klines_data, valid_symbols)
    logger.info(f"數據範圍: {market_snapshots[0].timestamp} 到 {market_snapshots[-1].timestamp}")
    
    # Step 3: 運行回測
    logger.info("\n[Step 3] 運行7策略回測")
    logger.info("-"*80)
    
    initial_capital = 100000.0
    backtest_results = await run_all_strategies_backtest(market_snapshots, initial_capital)
    
    # Step 4: 生成報告
    logger.info("\n[Step 4] 生成性能報告")
    logger.info("-"*80)
    
    comparator = PerformanceComparator()
    
    report_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'backtest_period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'symbols': valid_symbols,
        'initial_capital': initial_capital,
        'strategies': {}
    }
    
    for strategy_name, metrics in backtest_results.items():
        if metrics:
            # 添加到比較器
            comparator.add_strategy_result(strategy_name, metrics)
            
            # 添加到報告
            report_data['strategies'][strategy_name] = {
                'total_return_pct': f"{metrics.total_return_pct:.2f}%",
                'sharpe_ratio': f"{metrics.sharpe_ratio:.2f}",
                'annual_return_pct': f"{metrics.annual_return_pct:.2f}%",
                'win_rate': f"{metrics.win_rate:.2f}%",
                'max_drawdown_pct': f"{metrics.max_drawdown_pct:.2f}%",
                'total_trades': metrics.total_trades,
                'winning_trades': metrics.winning_trades,
                'losing_trades': metrics.losing_trades,
                'total_pnl': f"${metrics.total_pnl:.2f}",
                'avg_trade_duration': f"{metrics.avg_trade_duration:.2f}s"
            }
        else:
            report_data['strategies'][strategy_name] = {'error': '回測失敗'}
    
    # 添加排名
    scores = comparator.rank_strategies()
    report_data['ranking'] = [
        {
            'rank': score.rank,
            'strategy': score.strategy_name,
            'overall_score': f"{score.overall_score:.2f}",
            'return_score': f"{score.return_score:.2f}",
            'risk_adjusted_score': f"{score.risk_adjusted_score:.2f}",
            'trade_quality_score': f"{score.trade_quality_score:.2f}"
        }
        for score in scores[:7]
    ]
    
    # 保存報告
    report_dir = Path('./reports/backtesting')
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f'backtest_report_real_data_{timestamp}.json'
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ 報告已保存: {report_file}")
    
    # 打印摘要
    logger.info("\n" + "="*80)
    logger.info("🏆 策略排名")
    logger.info("="*80)
    
    for rank_item in report_data.get('ranking', []):
        logger.info(
            f"#{rank_item['rank']}: {rank_item['strategy']} "
            f"(綜合分: {rank_item['overall_score']})"
        )


if __name__ == '__main__':
    asyncio.run(main())
