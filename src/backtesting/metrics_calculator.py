#!/usr/bin/env python3
"""
Metrics Calculator for Strategy Performance Analysis
績效指標計算器 - 計算Sharpe、回報、最大回撤、交易統計

This module calculates comprehensive performance metrics from trade history:
- Sharpe Ratio (risk-adjusted returns)
- Total/Daily/Monthly/Annualized Returns
- Maximum Drawdown and Drawdown Analysis
- Trade Statistics (win rate, avg win/loss, profit factor)
- Risk Metrics (volatility, Calmar ratio, Sortino ratio)
"""

import logging
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any

from src.integrations.strategy_adapters.strategy_interface import StrategyMetrics

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """Individual trade record for metrics calculation."""
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    quantity: float
    position_type: str  # "long" or "short"
    pnl: float
    pnl_pct: float
    fees: float = 0.0
    slippage: float = 0.0


@dataclass
class PortfolioSnapshot:
    """Portfolio state at a point in time."""
    timestamp: datetime
    total_value: float
    cash: float
    positions_value: float
    open_pnl: float
    closed_pnl: float


class MetricsCalculator:
    """
    Calculate comprehensive strategy performance metrics.
    
    績效計算引擎 - 從交易歷史生成詳細的績效報告
    """
    
    def __init__(self, initial_capital: float = 100000.0, risk_free_rate: float = 0.02):
        """
        Initialize metrics calculator.
        
        Args:
            initial_capital: Starting portfolio value
            risk_free_rate: Annual risk-free rate for Sharpe ratio (default 2%)
        """
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self.trades: List[TradeRecord] = []
        self.portfolio_snapshots: List[PortfolioSnapshot] = []
    
    def add_trade(
        self,
        entry_time: datetime,
        entry_price: float,
        exit_time: datetime,
        exit_price: float,
        quantity: float,
        position_type: str = "long",
        fees: float = 0.0,
        slippage: float = 0.0
    ) -> None:
        """
        Record a completed trade.
        
        Args:
            entry_time: Trade entry timestamp
            entry_price: Entry price
            exit_time: Trade exit timestamp
            exit_price: Exit price
            quantity: Trade quantity
            position_type: "long" or "short"
            fees: Trading fees
            slippage: Execution slippage cost
        """
        if position_type == "long":
            pnl = (exit_price - entry_price) * quantity
        else:  # short
            pnl = (entry_price - exit_price) * quantity
        
        # Adjust for fees and slippage
        pnl -= (fees + slippage)
        
        entry_cost = entry_price * quantity
        pnl_pct = (pnl / entry_cost * 100) if entry_cost > 0 else 0.0
        
        trade = TradeRecord(
            entry_time=entry_time,
            entry_price=entry_price,
            exit_time=exit_time,
            exit_price=exit_price,
            quantity=quantity,
            position_type=position_type,
            pnl=pnl,
            pnl_pct=pnl_pct,
            fees=fees,
            slippage=slippage
        )
        self.trades.append(trade)
        logger.info(f"Trade recorded: {trade.position_type} {quantity}@{entry_price} → "
                   f"{exit_price}, PnL: ${pnl:.2f} ({pnl_pct:.2f}%)")
    
    def add_portfolio_snapshot(
        self,
        timestamp: datetime,
        total_value: float,
        cash: float,
        positions_value: float,
        open_pnl: float = 0.0,
        closed_pnl: float = 0.0
    ) -> None:
        """
        Record portfolio state at a point in time.
        
        Args:
            timestamp: Snapshot timestamp
            total_value: Total portfolio value
            cash: Cash available
            positions_value: Value of open positions
            open_pnl: Unrealized P&L
            closed_pnl: Realized P&L
        """
        snapshot = PortfolioSnapshot(
            timestamp=timestamp,
            total_value=total_value,
            cash=cash,
            positions_value=positions_value,
            open_pnl=open_pnl,
            closed_pnl=closed_pnl
        )
        self.portfolio_snapshots.append(snapshot)
    
    def calculate_total_return(self) -> float:
        """
        Calculate total return percentage.
        
        Returns:
            Total return % from initial capital to final value
        """
        if not self.portfolio_snapshots or len(self.portfolio_snapshots) < 2:
            return 0.0
        
        final_value = self.portfolio_snapshots[-1].total_value
        total_return_pct = ((final_value - self.initial_capital) / self.initial_capital) * 100
        return total_return_pct
    
    def calculate_daily_returns(self) -> np.ndarray:
        """
        Calculate daily returns from portfolio snapshots.
        
        Returns:
            Array of daily returns (decimals, e.g., 0.01 = 1%)
        """
        if len(self.portfolio_snapshots) < 2:
            return np.array([])
        
        values = np.array([snap.total_value for snap in self.portfolio_snapshots])
        daily_returns = np.diff(values) / values[:-1]
        return daily_returns
    
    def calculate_sharpe_ratio(self) -> float:
        """
        Calculate annualized Sharpe ratio.
        
        Sharpe = (mean_return - risk_free_rate) / std_return * sqrt(252)
        
        Returns:
            Sharpe ratio (annualized)
        """
        daily_returns = self.calculate_daily_returns()
        
        if len(daily_returns) < 2:
            logger.warning("Insufficient data for Sharpe ratio calculation")
            return 0.0
        
        mean_return = float(np.mean(daily_returns))
        std_return = float(np.std(daily_returns))
        
        if std_return == 0:
            return 0.0
        
        # Annualize: daily Sharpe * sqrt(252 trading days)
        daily_risk_free = self.risk_free_rate / 252
        sharpe = (mean_return - daily_risk_free) / std_return * np.sqrt(252)
        
        return float(sharpe)
    
    def calculate_sortino_ratio(self) -> float:
        """
        Calculate annualized Sortino ratio (downside deviation only).
        
        Sortino = (mean_return - risk_free_rate) / downside_std * sqrt(252)
        
        Returns:
            Sortino ratio (annualized)
         """
        daily_returns = self.calculate_daily_returns()
        
        if len(daily_returns) < 2:
            logger.warning("Insufficient data for Sortino ratio calculation")
            return 0.0
        
        mean_return = float(np.mean(daily_returns))
        
        # Downside deviation: only negative returns
        downside_returns = daily_returns[daily_returns < 0]
        if len(downside_returns) == 0:
            downside_std = 0.0
        else:
            downside_std = float(np.std(downside_returns))
        
        if downside_std == 0:
            return float('inf') if mean_return > 0 else 0.0
        
        daily_risk_free = self.risk_free_rate / 252
        sortino = (mean_return - daily_risk_free) / downside_std * np.sqrt(252)
        
        return float(sortino)
    
    def calculate_max_drawdown(self) -> Tuple[float, datetime, datetime, float]:
        """
        Calculate maximum drawdown and recovery period.
        
        Returns:
            Tuple of (max_drawdown_pct, start_time, bottom_time, recovery_time_days)
        """
        if len(self.portfolio_snapshots) < 2:
            # Return with epoch timestamps instead of None
            epoch = datetime.fromtimestamp(0, tz=timezone.utc)
            return 0.0, epoch, epoch, 0.0
        
        values = np.array([snap.total_value for snap in self.portfolio_snapshots])
        timestamps = [snap.timestamp for snap in self.portfolio_snapshots]
        
        # Running maximum
        running_max = np.maximum.accumulate(values)
        drawdown = (values - running_max) / running_max
        
        # Find max drawdown
        max_dd_idx = np.argmin(drawdown)
        max_drawdown_pct = abs(drawdown[max_dd_idx]) * 100
        
        # Find when max was reached and when bottom occurred
        peak_idx = np.where(running_max[:max_dd_idx+1] == running_max[max_dd_idx])[0][-1]
        peak_time = timestamps[peak_idx]
        bottom_time = timestamps[max_dd_idx]
        
        # Find recovery time (when returns to previous peak)
        recovery_idx = None
        peak_value = running_max[max_dd_idx]
        for i in range(max_dd_idx + 1, len(values)):
            if values[i] >= peak_value:
                recovery_idx = i
                break
        
        if recovery_idx:
            recovery_days = (timestamps[recovery_idx] - bottom_time).days
        else:
            recovery_days = (timestamps[-1] - bottom_time).days
        
        return max_drawdown_pct, peak_time, bottom_time, float(recovery_days)
    
    def calculate_trade_statistics(self) -> Dict[str, float]:
        """
        Calculate trade-level statistics.
        
        Returns:
            Dict with win_rate, avg_win, avg_loss, profit_factor, etc.
        """
        if len(self.trades) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'avg_trade_duration_hours': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'consecutive_wins': 0,
                'consecutive_losses': 0,
            }
        
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0.0
        
        # Average win/loss
        winning_pnl = [t.pnl for t in winning_trades]
        losing_pnl = [t.pnl for t in losing_trades]
        
        avg_win = float(np.mean(winning_pnl)) if winning_pnl else 0.0
        avg_loss = float(np.mean(losing_pnl)) if losing_pnl else 0.0
        
        # Profit factor
        total_winning = sum(winning_pnl)
        total_losing = abs(sum(losing_pnl)) if losing_pnl else 0.0
        profit_factor = total_winning / total_losing if total_losing > 0 else float('inf')
        
        # Average trade duration
        durations = [(t.exit_time - t.entry_time).total_seconds() / 3600 for t in self.trades]
        avg_duration = float(np.mean(durations)) if durations else 0.0
        
        # Largest win/loss
        largest_win = max(winning_pnl) if winning_pnl else 0.0
        largest_loss = min(losing_pnl) if losing_pnl else 0.0
        
        # Consecutive wins/losses
        consecutive_wins = self._max_consecutive(self.trades, lambda t: t.pnl > 0)
        consecutive_losses = self._max_consecutive(self.trades, lambda t: t.pnl < 0)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_count,
            'losing_trades': losing_count,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor if profit_factor != float('inf') else 0.0,
            'avg_trade_duration_hours': avg_duration,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses,
        }
    
    def _max_consecutive(self, items: List[Any], predicate) -> int:
        """Helper to find max consecutive items matching predicate."""
        max_consecutive = 0
        current_consecutive = 0
        for item in items:
            if predicate(item):
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        return max_consecutive
    
    def calculate_volatility(self) -> float:
        """
        Calculate annualized portfolio volatility.
        
        Returns:
            Annualized volatility (%)
        """
        daily_returns = self.calculate_daily_returns()
        if len(daily_returns) < 2:
            return 0.0
        
        daily_volatility = float(np.std(daily_returns))
        annualized_volatility = daily_volatility * np.sqrt(252) * 100
        return float(annualized_volatility)
    
    def calculate_calmar_ratio(self) -> float:
        """
        Calculate Calmar ratio (annual return / max drawdown).
        
        Returns:
            Calmar ratio
        """
        annual_return = self.calculate_total_return() / (
            (self.portfolio_snapshots[-1].timestamp - 
             self.portfolio_snapshots[0].timestamp).days / 365.25
        ) if len(self.portfolio_snapshots) >= 2 else 0.0
        
        max_dd, _, _, _ = self.calculate_max_drawdown()
        
        if max_dd == 0:
            return float('inf') if annual_return > 0 else 0.0
        
        return annual_return / max_dd
    
    def calculate_annualized_return(self) -> float:
        """
        Calculate annualized return percentage.
        
        Returns:
            Annualized return %
        """
        if len(self.portfolio_snapshots) < 2:
            return 0.0
        
        start_value = self.portfolio_snapshots[0].total_value
        end_value = self.portfolio_snapshots[-1].total_value
        
        time_span_days = (self.portfolio_snapshots[-1].timestamp - 
                          self.portfolio_snapshots[0].timestamp).days
        time_span_years = time_span_days / 365.25
        
        if time_span_years <= 0 or start_value <= 0:
            return 0.0
        
        annualized_return = ((end_value / start_value) ** (1 / time_span_years) - 1) * 100
        return annualized_return
    
    def calculate_daily_avg_profit(self) -> float:
        """
        Calculate average daily profit.
        
        Returns:
            Average daily profit ($)
        """
        if not self.trades:
            return 0.0
        
        total_pnl = sum(t.pnl for t in self.trades)
        
        if len(self.portfolio_snapshots) < 2:
            return 0.0
        
        time_span_days = (self.portfolio_snapshots[-1].timestamp - 
                          self.portfolio_snapshots[0].timestamp).days
        
        if time_span_days <= 0:
            return 0.0
        
        daily_avg = total_pnl / time_span_days
        return daily_avg
    
    def generate_metrics(self) -> StrategyMetrics:
        """
        Generate complete StrategyMetrics report.
        
        Returns:
            StrategyMetrics dataclass with all calculations
        """
        trade_stats = self.calculate_trade_statistics()
        max_dd, dd_start, dd_bottom, recovery_days = self.calculate_max_drawdown()
        
        metrics = StrategyMetrics(
            total_trades=int(trade_stats['total_trades']),
            winning_trades=int(trade_stats['winning_trades']),
            losing_trades=int(trade_stats['losing_trades']),
            win_rate=trade_stats['win_rate'],
            total_pnl=sum(t.pnl for t in self.trades),
            total_return_pct=self.calculate_total_return(),
            sharpe_ratio=self.calculate_sharpe_ratio(),
            max_drawdown_pct=max_dd,
            annual_return_pct=self.calculate_annualized_return(),
            avg_trade_duration=trade_stats['avg_trade_duration_hours'],
            daily_avg_profit=self.calculate_daily_avg_profit(),
            execution_latency_ms=0.0,  # Set by backtester
            extra_metrics={
                'sortino_ratio': self.calculate_sortino_ratio(),
                'volatility_pct': self.calculate_volatility(),
                'calmar_ratio': self.calculate_calmar_ratio(),
                'profit_factor': trade_stats['profit_factor'],
                'avg_win': trade_stats['avg_win'],
                'avg_loss': trade_stats['avg_loss'],
                'largest_win': trade_stats['largest_win'],
                'largest_loss': trade_stats['largest_loss'],
                'consecutive_wins': trade_stats['consecutive_wins'],
                'consecutive_losses': trade_stats['consecutive_losses'],
                'drawdown_start': dd_start.isoformat() if dd_start else None,
                'drawdown_bottom': dd_bottom.isoformat() if dd_bottom else None,
                'recovery_days': recovery_days,
            }
        )
        
        logger.info(f"Metrics generated: Sharpe={metrics.sharpe_ratio:.2f}, "
                   f"Return={metrics.total_return_pct:.2f}%, "
                   f"MaxDD={metrics.max_drawdown_pct:.2f}%")
        
        return metrics
