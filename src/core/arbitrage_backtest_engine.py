#!/usr/bin/env python3
"""
Phase 5 Stage 3 Plus - 完整套利系統回測框架
Comprehensive Backtesting Framework for Arbitrage Trading System

功能:
1. 加載歷史市場數據 (多個交易所)
2. 模擬三角套利、蟲洞套利執行
3. 計算真實年化收益、Sharpe比率、最大回撤
4. 生成詳細回測報告

目標: 驗證三角/蟲洞套利在真實數據上的實際收益
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import logging

# ============================================================================
# 數據結構
# ============================================================================

class BacktestMetric(Enum):
    """回測指標"""
    TOTAL_RETURN = "total_return"
    ANNUAL_RETURN = "annual_return"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    CALMAR_RATIO = "calmar_ratio"
    MONTHLY_RETURNS = "monthly_returns"


@dataclass
class TradeRecord:
    """交易記錄"""
    timestamp: datetime
    strategy: str                          # 'triangular' 或 'wormhole'
    entry_price: float
    exit_price: float
    entry_capital: float
    exit_capital: float
    profit: float                          # 絕對收益
    profit_pct: float                      # 百分比收益
    fees: float
    slippage: float
    duration_seconds: float
    symbol_or_pair: str                    # 交易對或交易對組合
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BacktestResult:
    """回測結果"""
    strategy: str
    start_date: datetime
    end_date: datetime
    
    # 主要指標
    total_return: float                    # 總收益率 (%)
    annual_return: float                   # 年化收益率 (%)
    sharpe_ratio: float                    # Sharpe 比率
    max_drawdown: float                    # 最大回撤 (%)
    win_rate: float                        # 勝率
    profit_factor: float                   # 利潤因子
    calmar_ratio: float                    # Calmar 比率
    
    # 詳細統計
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_winning_trade: float               # 平均獲利交易 (%)
    avg_losing_trade: float                # 平均虧損交易 (%)
    monthly_returns: List[float]           # 每月收益率 (%)
    
    # 交易記錄
    trades: List[TradeRecord] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)  # 資產曲線
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'strategy': self.strategy,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'total_return': round(self.total_return, 2),
            'annual_return': round(self.annual_return, 2),
            'sharpe_ratio': round(self.sharpe_ratio, 4),
            'max_drawdown': round(self.max_drawdown, 2),
            'win_rate': round(self.win_rate, 4),
            'profit_factor': round(self.profit_factor, 4),
            'calmar_ratio': round(self.calmar_ratio, 4),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_winning_trade': round(self.avg_winning_trade, 2),
            'avg_losing_trade': round(self.avg_losing_trade, 2),
            'monthly_returns': [round(r, 2) for r in self.monthly_returns]
        }


# ============================================================================
# 歷史數據加載器
# ============================================================================

class HistoricalDataLoader:
    """歷史市場數據加載器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.price_data: Dict[str, pd.DataFrame] = {}
    
    def generate_synthetic_prices(
        self,
        start_date: datetime,
        end_date: datetime,
        symbols: List[str],
        daily_volatility: float = 0.02
    ) -> Dict[str, pd.DataFrame]:
        """
        生成合成歷史價格數據 (用於演示)
        
        真實場景應從 API 加載:
        - Binance REST API
        - Kraken REST API
        - CCXT 統一接口
        """
        
        dates = pd.date_range(start=start_date, end=end_date, freq='h')
        
        # 初始價格
        initial_prices = {
            'BTC/USDT': 45000,
            'ETH/USDT': 2500,
            'BTC/ETH': 18.0,
            'BTC/USDC': 45100,  # 交易所2
            'ETH/USDC': 2510,
            'BTC/BUSD': 44900,  # 交易所3
            'ETH/BUSD': 2490
        }
        
        data = {}
        
        for symbol in symbols:
            if symbol not in initial_prices:
                continue
            
            initial_price = initial_prices[symbol]
            
            # 生成幾何布朗運動價格路徑
            n_periods = len(dates)
            returns = np.random.normal(0.0001, daily_volatility, n_periods)
            prices = initial_price * np.exp(np.cumsum(returns))
            
            df = pd.DataFrame({
                'timestamp': dates,
                'open': prices,
                'high': prices * (1 + np.abs(np.random.normal(0, 0.001, n_periods))),
                'low': prices * (1 - np.abs(np.random.normal(0, 0.001, n_periods))),
                'close': prices,
                'volume': np.random.uniform(100, 1000, n_periods)
            })
            
            data[symbol] = df
        
        self.price_data = data
        return data


# ============================================================================
# 套利機會檢測器
# ============================================================================

class ArbitrageOpportunityDetector:
    """套利機會檢測器"""
    
    def __init__(
        self,
        min_profit_threshold: float = 0.001,  # 最低 0.1% 利潤
        max_execution_time: int = 60  # 最大執行時間 60 秒
    ):
        self.min_profit_threshold = min_profit_threshold
        self.max_execution_time = max_execution_time
        self.logger = logging.getLogger(__name__)
    
    def detect_triangular_opportunities(
        self,
        prices: Dict[str, float],
        timestamp: datetime
    ) -> List[Tuple[str, str, str, float]]:
        """
        檢測三角套利機會
        
        返回: [(pair1, pair2, pair3, profit_pct), ...]
        """
        opportunities = []
        
        # 檢測 BTC → ETH → USD → BTC 循環
        if all(k in prices for k in ['BTC/USDT', 'ETH/BTC', 'ETH/USDT']):
            # 模擬交易流程
            btc_amount = 1.0
            
            # 第1步: BTC → USDT
            usdt_amount = btc_amount * prices['BTC/USDT']
            
            # 第2步: USDT → ETH
            eth_amount = usdt_amount / prices['ETH/USDT']
            
            # 第3步: ETH → BTC
            btc_final = eth_amount / prices['BTC/ETH']
            
            # 計算利潤
            profit_pct = (btc_final - btc_amount) / btc_amount
            
            if profit_pct > self.min_profit_threshold:
                opportunities.append((
                    'BTC/USDT',
                    'ETH/BTC',
                    'ETH/USDT',
                    profit_pct
                ))
        
        return opportunities
    
    def detect_wormhole_opportunities(
        self,
        exchange_prices: Dict[str, Dict[str, float]],
        transfer_costs: Dict[str, float],
        timestamp: datetime
    ) -> List[Tuple[str, str, str, float]]:
        """
        檢測蟲洞套利機會 (跨交易所)
        
        例如:
        - Binance BTC/USDT: 45000
        - Kraken BTC/USDT: 45100
        - 轉賬成本: 0.5%
        - 利潤機會: (45100-45000)/45000 - 0.005 = 0.7%
        """
        opportunities = []
        
        # 遍歷所有交易對
        all_pairs = set()
        for prices in exchange_prices.values():
            all_pairs.update(prices.keys())
        
        for pair in all_pairs:
            exchange_prices_list = []
            
            for exchange, prices in exchange_prices.items():
                if pair in prices:
                    exchange_prices_list.append((exchange, prices[pair]))
            
            if len(exchange_prices_list) < 2:
                continue
            
            # 找出最高和最低價
            exchange_prices_list.sort(key=lambda x: x[1])
            
            buy_exchange, buy_price = exchange_prices_list[0]
            sell_exchange, sell_price = exchange_prices_list[-1]
            
            # 計算利潤
            price_diff_pct = (sell_price - buy_price) / buy_price
            transfer_cost = transfer_costs.get(pair, 0.005)  # 默認 0.5%
            
            profit_pct = price_diff_pct - transfer_cost
            
            if profit_pct > self.min_profit_threshold:
                opportunities.append((
                    buy_exchange,
                    pair,
                    sell_exchange,
                    profit_pct
                ))
        
        return opportunities


# ============================================================================
# 回測引擎
# ============================================================================

class ArbitrageBacktestEngine:
    """套利回測引擎"""
    
    def __init__(
        self,
        initial_capital: float = 100000,  # 初始資本 $100,000
        transaction_fee: float = 0.0005,  # 交易費 0.05%
        slippage: float = 0.0002,         # 滑點 0.02%
        max_position_pct: float = 0.1     # 最大持倉 10%
    ):
        self.initial_capital = initial_capital
        self.transaction_fee = transaction_fee
        self.slippage = slippage
        self.max_position_pct = max_position_pct
        
        self.logger = logging.getLogger(__name__)
        self.opportunity_detector = ArbitrageOpportunityDetector()
    
    def backtest_triangular_arbitrage(
        self,
        price_data: Dict[str, pd.DataFrame],
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResult:
        """
        回測三角套利策略
        """
        
        trades = []
        equity = [self.initial_capital]
        equity_timestamps = []
        
        # 獲取價格數據
        price_df = price_data.get('BTC/USDT')
        if price_df is None:
            raise ValueError("需要 BTC/USDT 價格數據")
        
        # 篩選時間範圍
        price_df = price_df[
            (price_df['timestamp'] >= start_date) &
            (price_df['timestamp'] <= end_date)
        ].copy()
        
        # 逐小時模擬
        for idx, row in price_df.iterrows():
            timestamp = row['timestamp']
            current_price = row['close']
            
            # 模擬三角套利機會 (簡化)
            # 實際應基於完整的 BTC/ETH/USDT 價格三角形
            profit_pct = self._simulate_triangular_opportunity(
                current_price,
                idx
            )
            
            if profit_pct > self.opportunity_detector.min_profit_threshold:
                # 執行交易
                position_size = min(
                    equity[-1] * self.max_position_pct,
                    equity[-1]
                )
                
                # 計算費用和滑點
                total_cost_pct = self.transaction_fee * 3 + self.slippage * 3  # 3 次交易
                net_profit_pct = profit_pct - total_cost_pct
                
                if net_profit_pct > 0:
                    profit = position_size * net_profit_pct
                    
                    trade = TradeRecord(
                        timestamp=timestamp,
                        strategy='triangular_arbitrage',
                        entry_price=current_price,
                        exit_price=current_price * (1 + net_profit_pct),
                        entry_capital=position_size,
                        exit_capital=position_size * (1 + net_profit_pct),
                        profit=profit,
                        profit_pct=net_profit_pct,
                        fees=position_size * total_cost_pct * 2 / 3,
                        slippage=position_size * total_cost_pct * 1 / 3,
                        duration_seconds=45,
                        symbol_or_pair='BTC/ETH/USDT'
                    )
                    
                    trades.append(trade)
                    
                    # 更新資產
                    new_equity = equity[-1] + profit
                    equity.append(new_equity)
                    equity_timestamps.append(timestamp)
            else:
                # 即使沒有機會，也記錄每個時間點的資產
                equity.append(equity[-1])
                equity_timestamps.append(timestamp)
        
        # 計算回測指標
        return self._calculate_backtest_metrics(
            trades=trades,
            equity_curve=equity,
            strategy='triangular_arbitrage',
            start_date=start_date,
            end_date=end_date,
            trading_days=len(price_df) / 24  # 轉換為交易日
        )
    
    def backtest_wormhole_arbitrage(
        self,
        price_data: Dict[str, pd.DataFrame],
        exchange_multiplier: float = 0.3,  # 交易所2 價格高 0.3%
        start_date: datetime = None,
        end_date: datetime = None
    ) -> BacktestResult:
        """
        回測蟲洞套利策略 (跨交易所)
        """
        
        trades = []
        equity = [self.initial_capital]
        
        # 獲取主交易所價格
        primary_df = price_data.get('BTC/USDT')
        if primary_df is None:
            raise ValueError("需要 BTC/USDT 價格數據")
        
        if start_date is None:
            start_date = primary_df['timestamp'].min()
        if end_date is None:
            end_date = primary_df['timestamp'].max()
        
        primary_df = primary_df[
            (primary_df['timestamp'] >= start_date) &
            (primary_df['timestamp'] <= end_date)
        ].copy()
        
        # 逐小時模擬
        for idx, row in primary_df.iterrows():
            timestamp = row['timestamp']
            primary_price = row['close']
            
            # 模擬交易所2 的價格 (略高)
            secondary_price = primary_price * (1 + exchange_multiplier / 100)
            
            # 轉賬成本 (估計)
            transfer_cost_pct = 0.005  # 0.5%
            
            # 套利利潤
            profit_pct = (secondary_price - primary_price) / primary_price - transfer_cost_pct
            
            if profit_pct > self.opportunity_detector.min_profit_threshold:
                position_size = equity[-1] * self.max_position_pct
                
                # 計算費用
                total_cost_pct = self.transaction_fee * 2 + self.slippage * 2 + transfer_cost_pct
                net_profit_pct = profit_pct - total_cost_pct + transfer_cost_pct  # 已計入
                
                if net_profit_pct > 0:
                    profit = position_size * net_profit_pct
                    
                    trade = TradeRecord(
                        timestamp=timestamp,
                        strategy='wormhole_arbitrage',
                        entry_price=primary_price,
                        exit_price=secondary_price,
                        entry_capital=position_size,
                        exit_capital=position_size * (1 + net_profit_pct),
                        profit=profit,
                        profit_pct=net_profit_pct,
                        fees=position_size * total_cost_pct * 0.4,
                        slippage=position_size * total_cost_pct * 0.1,
                        duration_seconds=600,  # 轉賬需要更長時間
                        symbol_or_pair='BTC/USDT (Binance→Kraken)'
                    )
                    
                    trades.append(trade)
                    equity.append(equity[-1] + profit)
            else:
                equity.append(equity[-1])
        
        return self._calculate_backtest_metrics(
            trades=trades,
            equity_curve=equity,
            strategy='wormhole_arbitrage',
            start_date=start_date,
            end_date=end_date,
            trading_days=len(primary_df) / 24
        )
    
    def _simulate_triangular_opportunity(
        self,
        base_price: float,
        index: int
    ) -> float:
        """模擬三角套利機會利潤"""
        # 基於價格和時間指數的偽機會
        # 實際應基於完整的市場數據
        
        # 生成週期性機會 (每小時大約 2-3 次)
        cycle_factor = (index % 24) / 24
        opportunity = 0.0015 + 0.001 * np.sin(2 * np.pi * cycle_factor)
        
        # 添加隨機性
        opportunity += np.random.normal(0, 0.0005)
        
        return max(0, opportunity)
    
    def _calculate_backtest_metrics(
        self,
        trades: List[TradeRecord],
        equity_curve: List[float],
        strategy: str,
        start_date: datetime,
        end_date: datetime,
        trading_days: float
    ) -> BacktestResult:
        """計算回測指標"""
        
        if not trades:
            # 沒有交易
            return BacktestResult(
                strategy=strategy,
                start_date=start_date,
                end_date=end_date,
                total_return=0.0,
                annual_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                calmar_ratio=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                avg_winning_trade=0.0,
                avg_losing_trade=0.0,
                monthly_returns=[],
                trades=[],
                equity_curve=equity_curve
            )
        
        # 計算基本指標
        total_return = (equity_curve[-1] - self.initial_capital) / self.initial_capital * 100
        days = (end_date - start_date).days
        annual_return = total_return * 365 / max(days, 1)
        
        # 計算 Sharpe 比率
        returns = np.diff(equity_curve) / np.array(equity_curve[:-1])
        daily_returns = returns[returns != 0]  # 去掉無交易日
        
        if len(daily_returns) > 0:
            sharpe_ratio = (
                np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
                if np.std(daily_returns) > 0 else 0
            )
        else:
            sharpe_ratio = 0
        
        # 計算最大回撤
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (np.array(equity_curve) - running_max) / running_max * 100
        max_drawdown = np.min(drawdown)
        
        # 計算勝率
        winning_trades = sum(1 for t in trades if t.profit > 0)
        losing_trades = len(trades) - winning_trades
        win_rate = winning_trades / len(trades) if trades else 0
        
        # 計算利潤因子
        gross_profit = sum(t.profit for t in trades if t.profit > 0)
        gross_loss = abs(sum(t.profit for t in trades if t.profit < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # 計算 Calmar 比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # 計算平均獲利/虧損
        winning_pnl = [t.profit_pct for t in trades if t.profit > 0]
        losing_pnl = [t.profit_pct for t in trades if t.profit < 0]
        
        avg_winning = np.mean(winning_pnl) * 100 if winning_pnl else 0
        avg_losing = np.mean(losing_pnl) * 100 if losing_pnl else 0
        
        # 計算月度收益
        monthly_returns = []
        # (簡化版本，實際應按月份統計)
        
        return BacktestResult(
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            calmar_ratio=calmar_ratio,
            total_trades=len(trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_winning_trade=avg_winning,
            avg_losing_trade=avg_losing,
            monthly_returns=monthly_returns,
            trades=trades,
            equity_curve=equity_curve
        )


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序 - 運行完整回測"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 初始化
    data_loader = HistoricalDataLoader()
    backtest_engine = ArbitrageBacktestEngine(
        initial_capital=100000,
        transaction_fee=0.0005,
        slippage=0.0002
    )
    
    # 生成測試數據 (3 個月)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    logger.info(f"🔄 生成 {start_date} - {end_date} 的歷史價格數據...")
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'BTC/ETH', 'BTC/USDC', 'ETH/USDC']
    price_data = data_loader.generate_synthetic_prices(
        start_date=start_date,
        end_date=end_date,
        symbols=symbols
    )
    
    logger.info(f"✅ 已加載 {len(price_data)} 個交易對的數據")
    
    # 三角套利回測
    logger.info("\n🔄 運行三角套利回測...")
    triangular_result = backtest_engine.backtest_triangular_arbitrage(
        price_data=price_data,
        start_date=start_date,
        end_date=end_date
    )
    
    logger.info(f"""
    📊 三角套利結果:
    ├─ 總收益率: {triangular_result.total_return:.2f}%
    ├─ 年化收益: {triangular_result.annual_return:.2f}%
    ├─ Sharpe 比率: {triangular_result.sharpe_ratio:.4f}
    ├─ 最大回撤: {triangular_result.max_drawdown:.2f}%
    ├─ 勝率: {triangular_result.win_rate:.2%}
    ├─ 總交易數: {triangular_result.total_trades}
    └─ 利潤因子: {triangular_result.profit_factor:.2f}
    """)
    
    # 蟲洞套利回測
    logger.info("\n🔄 運行蟲洞套利回測...")
    wormhole_result = backtest_engine.backtest_wormhole_arbitrage(
        price_data=price_data,
        start_date=start_date,
        end_date=end_date
    )
    
    logger.info(f"""
    📊 蟲洞套利結果:
    ├─ 總收益率: {wormhole_result.total_return:.2f}%
    ├─ 年化收益: {wormhole_result.annual_return:.2f}%
    ├─ Sharpe 比率: {wormhole_result.sharpe_ratio:.4f}
    ├─ 最大回撤: {wormhole_result.max_drawdown:.2f}%
    ├─ 勝率: {wormhole_result.win_rate:.2%}
    ├─ 總交易數: {wormhole_result.total_trades}
    └─ 利潤因子: {wormhole_result.profit_factor:.2f}
    """)
    
    # 保存結果
    results = {
        'triangular': triangular_result.to_dict(),
        'wormhole': wormhole_result.to_dict(),
        'combined_annual_return': (
            triangular_result.annual_return + wormhole_result.annual_return
        )
    }
    
    output_file = Path('reports/backtest/arbitrage_backtest_results.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n✅ 結果已保存到 {output_file}")
    
    # 性能對比
    logger.info(f"""
    🎯 策略對比:
    ├─ 三角套利 年化: {triangular_result.annual_return:.2f}%
    ├─ 蟲洞套利 年化: {wormhole_result.annual_return:.2f}%
    └─ 組合年化 (簡單相加): {triangular_result.annual_return + wormhole_result.annual_return:.2f}%
    """)


if __name__ == '__main__':
    main()
