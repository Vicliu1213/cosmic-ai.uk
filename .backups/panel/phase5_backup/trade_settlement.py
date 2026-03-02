#!/usr/bin/env python3
"""
Trade Settlement and Reporting System
交易結算和報告系統

Complete trade settlement, confirmation, and performance reporting:
- Trade confirmation and settlement
- P&L calculation and tracking
- Trade history and analytics
- Performance metrics
- Export functionality

This module provides:
1. TradeSettlementEngine for settlement processing
2. PerformanceReporter for metrics calculation
3. TradeAnalytics for historical analysis
4. ReportExporter for various export formats
5. ComplianceTracker for regulatory tracking
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import json
import csv
from io import StringIO

from src.phase5.order_management import (
    Order, OrderStatus, Position, PositionStatus, Trade, OrderSide,
    OrderManager, PositionManager, PortfolioManager
)
from src.phase5.exchange_connector import ExchangeType


# ============================================================================
# Enums
# ============================================================================

class SettlementStatus(Enum):
    """Settlement status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SETTLED = "settled"
    FAILED = "failed"


class ReportFormat(Enum):
    """Report export format."""
    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    HTML = "html"


class TradeOutcome(Enum):
    """Trade outcome classification."""
    WINNING = "winning"
    LOSING = "losing"
    BREAKEVEN = "breakeven"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TradeSettlement:
    """Trade settlement record."""
    settlement_id: str
    trade_id: str
    position_id: str
    exchange_type: ExchangeType
    status: SettlementStatus = SettlementStatus.PENDING
    
    # Amounts
    entry_amount: float = 0.0
    exit_amount: float = 0.0
    total_fees: float = 0.0
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    
    # Timing
    entry_time: datetime = field(default_factory=datetime.utcnow)
    exit_time: datetime = field(default_factory=datetime.utcnow)
    settlement_time: Optional[datetime] = None
    
    # Metadata
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a period."""
    period_start: datetime
    period_end: datetime
    
    # Trade statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    breakeven_trades: int = 0
    
    # P&L metrics
    total_pnl: float = 0.0
    total_fees: float = 0.0
    net_pnl: float = 0.0
    
    # Ratios
    win_rate: float = 0.0
    profit_factor: float = 0.0  # Wins / Losses
    average_win: float = 0.0
    average_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    
    # Risk metrics
    max_drawdown: float = 0.0
    recovery_factor: float = 0.0
    
    # Time metrics
    average_trade_duration: Optional[timedelta] = None
    average_win_duration: Optional[timedelta] = None
    average_loss_duration: Optional[timedelta] = None
    
    # Capital
    initial_capital: float = 0.0
    final_capital: float = 0.0
    return_percent: float = 0.0


# ============================================================================
# Trade Settlement Engine
# ============================================================================

class TradeSettlementEngine:
    """Handles trade settlement and confirmation."""

    def __init__(self):
        """Initialize settlement engine."""
        self.logger = logging.getLogger("TradeSettlementEngine")
        self.settlements: Dict[str, TradeSettlement] = {}
        self.settlement_history: List[TradeSettlement] = []

    async def confirm_trade(
        self,
        trade: Trade,
        position: Position
    ) -> TradeSettlement:
        """Confirm and settle a completed trade.
        
        Args:
            trade: Trade record
            position: Associated position
            
        Returns:
            TradeSettlement record
        """
        import uuid
        
        settlement_id = str(uuid.uuid4())
        
        # Calculate amounts
        entry_amount = trade.entry_price * trade.entry_quantity
        exit_amount = trade.exit_price * trade.exit_quantity
        total_fees = trade.entry_fees + trade.exit_fees
        gross_pnl = trade.realized_pnl + total_fees
        net_pnl = trade.realized_pnl
        
        settlement = TradeSettlement(
            settlement_id=settlement_id,
            trade_id=trade.trade_id,
            position_id=position.position_id,
            exchange_type=position.exchange_type,
            status=SettlementStatus.CONFIRMED,
            entry_amount=entry_amount,
            exit_amount=exit_amount,
            total_fees=total_fees,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            entry_time=trade.entry_time,
            exit_time=trade.exit_time,
            settlement_time=datetime.utcnow()
        )
        
        self.settlements[settlement_id] = settlement
        self.settlement_history.append(settlement)
        
        self.logger.info(
            f"Trade {trade.trade_id} settled: "
            f"P&L ${net_pnl:+.2f}, Fees ${total_fees:.2f}"
        )
        
        return settlement

    async def mark_settled(self, settlement_id: str) -> bool:
        """Mark settlement as fully settled.
        
        Args:
            settlement_id: Settlement ID
            
        Returns:
            True if successful
        """
        settlement = self.settlements.get(settlement_id)
        if not settlement:
            return False

        settlement.status = SettlementStatus.SETTLED
        settlement.settlement_time = datetime.utcnow()
        
        self.logger.info(f"Settlement {settlement_id} marked as settled")
        return True

    def get_settlements_by_status(
        self,
        status: SettlementStatus
    ) -> List[TradeSettlement]:
        """Get settlements by status.
        
        Args:
            status: Settlement status
            
        Returns:
            List of settlements
        """
        return [s for s in self.settlements.values() if s.status == status]

    def get_unsettled_settlements(self) -> List[TradeSettlement]:
        """Get all unsettled settlements.
        
        Returns:
            List of unsettled settlements
        """
        return self.get_settlements_by_status(SettlementStatus.PENDING) + \
               self.get_settlements_by_status(SettlementStatus.CONFIRMED)


# ============================================================================
# Performance Reporter
# ============================================================================

class PerformanceReporter:
    """Calculates performance metrics."""

    def __init__(self):
        """Initialize performance reporter."""
        self.logger = logging.getLogger("PerformanceReporter")

    async def calculate_metrics(
        self,
        trades: List[Trade],
        initial_capital: float,
        current_capital: float,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics.
        
        Args:
            trades: List of completed trades
            initial_capital: Starting capital
            current_capital: Current capital
            period_start: Analysis start time (optional)
            period_end: Analysis end time (optional)
            
        Returns:
            PerformanceMetrics
        """
        if not period_start:
            period_start = datetime.utcnow() - timedelta(days=30)
        if not period_end:
            period_end = datetime.utcnow()

        # Filter trades in period
        period_trades = [
            t for t in trades
            if period_start <= t.exit_time <= period_end
        ]

        # Calculate statistics
        winning_trades = [t for t in period_trades if t.realized_pnl > 0]
        losing_trades = [t for t in period_trades if t.realized_pnl < 0]
        breakeven_trades = [t for t in period_trades if t.realized_pnl == 0]

        total_trades = len(period_trades)
        total_pnl = sum(t.realized_pnl for t in period_trades)
        total_fees = sum(t.entry_fees + t.exit_fees for t in period_trades)
        net_pnl = total_pnl - total_fees

        # Ratios
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0.0
        
        win_sum = sum(t.realized_pnl for t in winning_trades)
        loss_sum = sum(abs(t.realized_pnl) for t in losing_trades)
        profit_factor = (win_sum / loss_sum) if loss_sum > 0 else (win_sum if win_sum > 0 else 0.0)

        avg_win = (win_sum / len(winning_trades)) if winning_trades else 0.0
        avg_loss = (loss_sum / len(losing_trades)) if losing_trades else 0.0
        
        largest_win = max((t.realized_pnl for t in winning_trades), default=0.0)
        largest_loss = min((t.realized_pnl for t in losing_trades), default=0.0)

        # Durations
        durations = [t.exit_time - t.entry_time for t in period_trades]
        avg_duration = sum(durations, timedelta()) / len(durations) if durations else None

        win_durations = [t.exit_time - t.entry_time for t in winning_trades]
        avg_win_duration = sum(win_durations, timedelta()) / len(win_durations) if win_durations else None

        loss_durations = [t.exit_time - t.entry_time for t in losing_trades]
        avg_loss_duration = sum(loss_durations, timedelta()) / len(loss_durations) if loss_durations else None

        # Return
        return_percent = ((current_capital - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0.0

        metrics = PerformanceMetrics(
            period_start=period_start,
            period_end=period_end,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            breakeven_trades=len(breakeven_trades),
            total_pnl=total_pnl,
            total_fees=total_fees,
            net_pnl=net_pnl,
            win_rate=win_rate,
            profit_factor=profit_factor,
            average_win=avg_win,
            average_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            average_trade_duration=avg_duration,
            average_win_duration=avg_win_duration,
            average_loss_duration=avg_loss_duration,
            initial_capital=initial_capital,
            final_capital=current_capital,
            return_percent=return_percent
        )

        self.logger.info(f"Calculated metrics: {total_trades} trades, Win Rate {win_rate:.1f}%")
        return metrics


# ============================================================================
# Trade Analytics
# ============================================================================

class TradeAnalytics:
    """Analytics and analysis of trades."""

    def __init__(self):
        """Initialize analytics."""
        self.logger = logging.getLogger("TradeAnalytics")

    def classify_trade(self, trade: Trade) -> TradeOutcome:
        """Classify trade outcome.
        
        Args:
            trade: Trade record
            
        Returns:
            TradeOutcome classification
        """
        if trade.realized_pnl > 0:
            return TradeOutcome.WINNING
        elif trade.realized_pnl < 0:
            return TradeOutcome.LOSING
        else:
            return TradeOutcome.BREAKEVEN

    def get_consecutive_wins_losses(
        self,
        trades: List[Trade]
    ) -> Tuple[int, int]:
        """Get current consecutive wins and losses.
        
        Args:
            trades: Sorted list of trades
            
        Returns:
            Tuple of (consecutive_wins, consecutive_losses)
        """
        if not trades:
            return 0, 0

        # Get most recent trades
        sorted_trades = sorted(trades, key=lambda t: t.exit_time, reverse=True)
        
        consecutive_wins = 0
        consecutive_losses = 0

        for trade in sorted_trades:
            if trade.realized_pnl > 0:
                if consecutive_losses > 0:
                    break
                consecutive_wins += 1
            elif trade.realized_pnl < 0:
                if consecutive_wins > 0:
                    break
                consecutive_losses += 1
            else:
                break

        return consecutive_wins, consecutive_losses

    def calculate_drawdown(self, trades: List[Trade]) -> float:
        """Calculate maximum drawdown from peak.
        
        Args:
            trades: List of trades sorted by time
            
        Returns:
            Maximum drawdown percentage
        """
        if not trades:
            return 0.0

        # Calculate cumulative balance
        balance = 0.0
        peak = 0.0
        max_drawdown = 0.0

        for trade in sorted(trades, key=lambda t: t.exit_time):
            balance += trade.realized_pnl
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak if peak != 0 else 0.0
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown * 100

    def find_best_performers(
        self,
        trades: List[Trade],
        top_n: int = 10
    ) -> List[Trade]:
        """Find best performing trades.
        
        Args:
            trades: List of trades
            top_n: Number of top trades to return
            
        Returns:
            List of best trades
        """
        sorted_trades = sorted(
            trades,
            key=lambda t: t.realized_pnl,
            reverse=True
        )
        return sorted_trades[:top_n]

    def find_worst_performers(
        self,
        trades: List[Trade],
        bottom_n: int = 10
    ) -> List[Trade]:
        """Find worst performing trades.
        
        Args:
            trades: List of trades
            bottom_n: Number of worst trades to return
            
        Returns:
            List of worst trades
        """
        sorted_trades = sorted(
            trades,
            key=lambda t: t.realized_pnl
        )
        return sorted_trades[:bottom_n]

    def get_symbol_statistics(self, trades: List[Trade]) -> Dict[str, Dict[str, Any]]:
        """Get statistics per symbol.
        
        Args:
            trades: List of trades
            
        Returns:
            Dict of symbol statistics
        """
        stats: Dict[str, Dict[str, Any]] = {}

        for trade in trades:
            if trade.symbol not in stats:
                stats[trade.symbol] = {
                    "total_trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": 0.0,
                    "win_rate": 0.0,
                    "average_pnl": 0.0
                }

            stats[trade.symbol]["total_trades"] += 1
            stats[trade.symbol]["total_pnl"] += trade.realized_pnl

            if trade.realized_pnl > 0:
                stats[trade.symbol]["wins"] += 1
            elif trade.realized_pnl < 0:
                stats[trade.symbol]["losses"] += 1

        # Calculate averages
        for symbol in stats:
            total = stats[symbol]["total_trades"]
            stats[symbol]["win_rate"] = (stats[symbol]["wins"] / total * 100) if total > 0 else 0.0
            stats[symbol]["average_pnl"] = stats[symbol]["total_pnl"] / total if total > 0 else 0.0

        return stats


# ============================================================================
# Report Exporter
# ============================================================================

class ReportExporter:
    """Export reports in various formats."""

    def __init__(self):
        """Initialize exporter."""
        self.logger = logging.getLogger("ReportExporter")

    async def export_trades(
        self,
        trades: List[Trade],
        format: ReportFormat = ReportFormat.CSV
    ) -> str:
        """Export trades in specified format.
        
        Args:
            trades: List of trades
            format: Export format
            
        Returns:
            Formatted report string
        """
        if format == ReportFormat.CSV:
            return self._export_trades_csv(trades)
        elif format == ReportFormat.JSON:
            return self._export_trades_json(trades)
        elif format == ReportFormat.TEXT:
            return self._export_trades_text(trades)
        else:
            return ""

    def _export_trades_csv(self, trades: List[Trade]) -> str:
        """Export trades as CSV."""
        output = StringIO()
        if not trades:
            return ""

        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Trade ID", "Symbol", "Side", "Entry Price", "Entry Qty",
            "Entry Time", "Exit Price", "Exit Qty", "Exit Time",
            "Entry Fees", "Exit Fees", "P&L", "ROI%", "Duration"
        ])

        # Rows
        for trade in trades:
            duration = (trade.exit_time - trade.entry_time).total_seconds() / 3600
            writer.writerow([
                trade.trade_id,
                trade.symbol,
                trade.side.value,
                f"{trade.entry_price:.2f}",
                f"{trade.entry_quantity:.8f}",
                trade.entry_time.isoformat(),
                f"{trade.exit_price:.2f}",
                f"{trade.exit_quantity:.8f}",
                trade.exit_time.isoformat(),
                f"{trade.entry_fees:.2f}",
                f"{trade.exit_fees:.2f}",
                f"{trade.realized_pnl:+.2f}",
                f"{trade.roi_percent:+.2f}",
                f"{duration:.2f}h"
            ])

        return output.getvalue()

    def _export_trades_json(self, trades: List[Trade]) -> str:
        """Export trades as JSON."""
        trades_data = []
        for trade in trades:
            trades_data.append({
                "trade_id": trade.trade_id,
                "symbol": trade.symbol,
                "side": trade.side.value,
                "entry_price": trade.entry_price,
                "entry_quantity": trade.entry_quantity,
                "entry_time": trade.entry_time.isoformat(),
                "exit_price": trade.exit_price,
                "exit_quantity": trade.exit_quantity,
                "exit_time": trade.exit_time.isoformat(),
                "entry_fees": trade.entry_fees,
                "exit_fees": trade.exit_fees,
                "realized_pnl": trade.realized_pnl,
                "roi_percent": trade.roi_percent
            })

        return json.dumps(trades_data, indent=2)

    def _export_trades_text(self, trades: List[Trade]) -> str:
        """Export trades as formatted text."""
        lines = []
        lines.append("=" * 100)
        lines.append("TRADE REPORT".center(100))
        lines.append("=" * 100)
        lines.append("")

        for i, trade in enumerate(trades, 1):
            lines.append(f"Trade #{i}: {trade.trade_id}")
            lines.append(f"  Symbol: {trade.symbol}")
            lines.append(f"  Side: {trade.side.value}")
            lines.append(f"  Entry: {trade.entry_price:.2f} x {trade.entry_quantity:.8f} @ {trade.entry_time}")
            lines.append(f"  Exit: {trade.exit_price:.2f} x {trade.exit_quantity:.8f} @ {trade.exit_time}")
            lines.append(f"  Fees: Entry ${trade.entry_fees:.2f}, Exit ${trade.exit_fees:.2f}")
            lines.append(f"  P&L: ${trade.realized_pnl:+.2f} ({trade.roi_percent:+.2f}%)")
            lines.append("")

        lines.append("=" * 100)
        return "\n".join(lines)

    async def export_metrics(
        self,
        metrics: PerformanceMetrics,
        format: ReportFormat = ReportFormat.TEXT
    ) -> str:
        """Export performance metrics.
        
        Args:
            metrics: PerformanceMetrics
            format: Export format
            
        Returns:
            Formatted metrics string
        """
        if format == ReportFormat.JSON:
            return self._export_metrics_json(metrics)
        elif format == ReportFormat.TEXT:
            return self._export_metrics_text(metrics)
        else:
            return ""

    def _export_metrics_json(self, metrics: PerformanceMetrics) -> str:
        """Export metrics as JSON."""
        data = {
            "period": {
                "start": metrics.period_start.isoformat(),
                "end": metrics.period_end.isoformat()
            },
            "trade_statistics": {
                "total_trades": metrics.total_trades,
                "winning_trades": metrics.winning_trades,
                "losing_trades": metrics.losing_trades,
                "breakeven_trades": metrics.breakeven_trades
            },
            "pnl": {
                "total_pnl": metrics.total_pnl,
                "total_fees": metrics.total_fees,
                "net_pnl": metrics.net_pnl
            },
            "ratios": {
                "win_rate_percent": metrics.win_rate,
                "profit_factor": metrics.profit_factor,
                "average_win": metrics.average_win,
                "average_loss": metrics.average_loss,
                "largest_win": metrics.largest_win,
                "largest_loss": metrics.largest_loss
            },
            "capital": {
                "initial": metrics.initial_capital,
                "final": metrics.final_capital,
                "return_percent": metrics.return_percent
            }
        }
        return json.dumps(data, indent=2)

    def _export_metrics_text(self, metrics: PerformanceMetrics) -> str:
        """Export metrics as formatted text."""
        lines = []
        lines.append("=" * 80)
        lines.append("PERFORMANCE METRICS REPORT".center(80))
        lines.append("=" * 80)
        lines.append("")

        lines.append(f"Period: {metrics.period_start} to {metrics.period_end}")
        lines.append("")

        lines.append("TRADE STATISTICS".ljust(40) + "VALUE")
        lines.append("-" * 80)
        lines.append(f"  Total Trades: {metrics.total_trades}".ljust(40) + str(metrics.total_trades))
        lines.append(f"  Winning Trades: {metrics.winning_trades}".ljust(40) + str(metrics.winning_trades))
        lines.append(f"  Losing Trades: {metrics.losing_trades}".ljust(40) + str(metrics.losing_trades))
        lines.append(f"  Breakeven Trades: {metrics.breakeven_trades}".ljust(40) + str(metrics.breakeven_trades))
        lines.append("")

        lines.append("P&L SUMMARY".ljust(40) + "VALUE")
        lines.append("-" * 80)
        lines.append(f"  Total P&L: ${metrics.total_pnl:+,.2f}".ljust(40) + f"${metrics.total_pnl:+,.2f}")
        lines.append(f"  Total Fees: ${metrics.total_fees:,.2f}".ljust(40) + f"${metrics.total_fees:,.2f}")
        lines.append(f"  Net P&L: ${metrics.net_pnl:+,.2f}".ljust(40) + f"${metrics.net_pnl:+,.2f}")
        lines.append("")

        lines.append("PERFORMANCE RATIOS".ljust(40) + "VALUE")
        lines.append("-" * 80)
        lines.append(f"  Win Rate: {metrics.win_rate:.2f}%".ljust(40) + f"{metrics.win_rate:.2f}%")
        lines.append(f"  Profit Factor: {metrics.profit_factor:.2f}".ljust(40) + f"{metrics.profit_factor:.2f}")
        lines.append(f"  Average Win: ${metrics.average_win:+,.2f}".ljust(40) + f"${metrics.average_win:+,.2f}")
        lines.append(f"  Average Loss: ${metrics.average_loss:+,.2f}".ljust(40) + f"${metrics.average_loss:+,.2f}")
        lines.append(f"  Largest Win: ${metrics.largest_win:+,.2f}".ljust(40) + f"${metrics.largest_win:+,.2f}")
        lines.append(f"  Largest Loss: ${metrics.largest_loss:+,.2f}".ljust(40) + f"${metrics.largest_loss:+,.2f}")
        lines.append("")

        lines.append("CAPITAL PERFORMANCE".ljust(40) + "VALUE")
        lines.append("-" * 80)
        lines.append(f"  Initial Capital: ${metrics.initial_capital:,.2f}".ljust(40) + f"${metrics.initial_capital:,.2f}")
        lines.append(f"  Final Capital: ${metrics.final_capital:,.2f}".ljust(40) + f"${metrics.final_capital:,.2f}")
        lines.append(f"  Return: {metrics.return_percent:+.2f}%".ljust(40) + f"{metrics.return_percent:+.2f}%")
        lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)


# ============================================================================
# Compliance Tracker
# ============================================================================

class ComplianceTracker:
    """Track regulatory and compliance requirements."""

    def __init__(self):
        """Initialize compliance tracker."""
        self.logger = logging.getLogger("ComplianceTracker")
        self.compliance_records: List[Dict[str, Any]] = []

    async def record_trade_execution(
        self,
        trade: Trade,
        execution_price: float,
        execution_quantity: float
    ) -> None:
        """Record trade execution for compliance.
        
        Args:
            trade: Trade record
            execution_price: Price executed at
            execution_quantity: Quantity executed
        """
        record = {
            "timestamp": datetime.utcnow(),
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "side": trade.side.value,
            "quantity": execution_quantity,
            "price": execution_price,
            "amount": execution_price * execution_quantity,
            "fees": trade.entry_fees if trade.side == OrderSide.BUY else trade.exit_fees
        }

        self.compliance_records.append(record)
        self.logger.debug(f"Recorded trade execution: {trade.trade_id}")

    def get_compliance_report(self, days: int = 30) -> Dict[str, Any]:
        """Get compliance report for period.
        
        Args:
            days: Number of days to report
            
        Returns:
            Compliance report dict
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_records = [
            r for r in self.compliance_records
            if r["timestamp"] >= cutoff
        ]

        total_volume = sum(r["amount"] for r in recent_records)
        total_fees = sum(r["fees"] for r in recent_records)
        total_trades = len(recent_records)

        return {
            "period_days": days,
            "total_trades": total_trades,
            "total_volume": total_volume,
            "total_fees": total_fees,
            "average_trade_size": total_volume / total_trades if total_trades > 0 else 0,
            "records": recent_records
        }
