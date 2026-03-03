#!/usr/bin/env python3
"""
Performance Comparator for Strategy Analysis
績效比較器 - 對比分析多個策略的表現

This module provides:
- Strategy ranking and scoring
- Comparative metrics visualization
- Statistical significance testing
- Performance comparison matrices
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime

from src.integrations.strategy_adapters.strategy_interface import StrategyMetrics

logger = logging.getLogger(__name__)


@dataclass
class StrategyScore:
    """Strategy performance score card."""
    strategy_name: str
    timestamp: datetime
    metrics: StrategyMetrics
    
    # Composite scores (0-100)
    risk_adjusted_score: float = 0.0  # Sharpe/Sortino weighted
    return_score: float = 0.0  # Returns weighted
    risk_management_score: float = 0.0  # Drawdown/volatility weighted
    trade_quality_score: float = 0.0  # Win rate/profit factor weighted
    overall_score: float = 0.0  # Weighted average of above
    
    # Ranking
    rank: int = 0


class PerformanceComparator:
    """
    Compare and rank multiple strategy performances.
    
    績效比較引擎 - 評估和排名多個策略系統
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize comparator.
        
        Args:
            risk_free_rate: Annual risk-free rate for calculations
        """
        self.risk_free_rate = risk_free_rate
        self.strategy_scores: Dict[str, StrategyScore] = {}
        self.comparison_history: List[Dict[str, Any]] = []
    
    def add_strategy_result(
        self,
        strategy_name: str,
        metrics: StrategyMetrics,
        timestamp: Optional[datetime] = None
    ) -> StrategyScore:
        """
        Add a strategy's performance metrics for comparison.
        
        Args:
            strategy_name: Name of the strategy
            metrics: StrategyMetrics from backtest
            timestamp: Timestamp of backtest (uses current time if None)
            
        Returns:
            StrategyScore with calculated scores
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        score = StrategyScore(
            strategy_name=strategy_name,
            timestamp=timestamp,
            metrics=metrics
        )
        
        # Calculate component scores
        score.risk_adjusted_score = self._calculate_risk_adjusted_score(metrics)
        score.return_score = self._calculate_return_score(metrics)
        score.risk_management_score = self._calculate_risk_management_score(metrics)
        score.trade_quality_score = self._calculate_trade_quality_score(metrics)
        
        # Calculate overall score (weighted composite)
        score.overall_score = self._calculate_overall_score(
            score.risk_adjusted_score,
            score.return_score,
            score.risk_management_score,
            score.trade_quality_score
        )
        
        self.strategy_scores[strategy_name] = score
        logger.info(f"Strategy '{strategy_name}' scored: {score.overall_score:.2f} "
                   f"(Sharpe: {metrics.sharpe_ratio:.2f}, Return: {metrics.total_return_pct:.2f}%)")
        
        return score
    
    def _calculate_risk_adjusted_score(self, metrics: StrategyMetrics) -> float:
        """
        Calculate risk-adjusted return score (0-100).
        
        Weighted: 70% Sharpe + 30% Sortino
        """
        sharpe = metrics.sharpe_ratio
        sortino = metrics.extra_metrics.get('sortino_ratio', 0.0)
        
        # Normalize: target Sharpe 2.5, Sortino 3.0
        sharpe_normalized = min(100, (sharpe / 2.5) * 100) if sharpe >= 0 else 0
        sortino_normalized = min(100, (sortino / 3.0) * 100) if sortino >= 0 else 0
        
        return 0.7 * sharpe_normalized + 0.3 * sortino_normalized
    
    def _calculate_return_score(self, metrics: StrategyMetrics) -> float:
        """
        Calculate absolute return score (0-100).
        
        Target annual return: 20% = 100 points
        """
        annual_return = metrics.annual_return_pct
        
        # Normalize: 20% = 100
        score = min(100, (annual_return / 20.0) * 100) if annual_return >= 0 else 0
        return score
    
    def _calculate_risk_management_score(self, metrics: StrategyMetrics) -> float:
        """
        Calculate risk management score (0-100).
        
        Weighted: 60% max drawdown + 40% volatility
        """
        max_dd = metrics.max_drawdown_pct
        volatility = metrics.extra_metrics.get('volatility_pct', 100.0)
        
        # Lower drawdown is better: target 10% = 100 points
        dd_score = max(0, 100 - (max_dd / 10.0) * 100) if max_dd >= 0 else 0
        
        # Lower volatility is better: target 15% = 100 points
        vol_score = max(0, 100 - (volatility / 15.0) * 100) if volatility >= 0 else 0
        
        return 0.6 * dd_score + 0.4 * vol_score
    
    def _calculate_trade_quality_score(self, metrics: StrategyMetrics) -> float:
        """
        Calculate trade quality score (0-100).
        
        Weighted: 50% win rate + 50% profit factor
        """
        win_rate = metrics.win_rate
        profit_factor = metrics.extra_metrics.get('profit_factor', 0.0)
        
        # Win rate: target 55% = 100 points
        wr_score = min(100, (win_rate / 55.0) * 100) if win_rate >= 0 else 0
        
        # Profit factor: target 2.0 = 100 points
        pf_score = min(100, (profit_factor / 2.0) * 100) if profit_factor >= 0 else 0
        
        return 0.5 * wr_score + 0.5 * pf_score
    
    def _calculate_overall_score(
        self,
        risk_adjusted: float,
        returns: float,
        risk_mgmt: float,
        trade_quality: float
    ) -> float:
        """
        Calculate overall strategy score (0-100).
        
        Weighting:
        - 35% Risk-Adjusted Returns (Sharpe/Sortino)
        - 30% Absolute Returns
        - 20% Risk Management
        - 15% Trade Quality
        """
        return (
            0.35 * risk_adjusted +
            0.30 * returns +
            0.20 * risk_mgmt +
            0.15 * trade_quality
        )
    
    def rank_strategies(self) -> List[StrategyScore]:
        """
        Rank strategies by overall score.
        
        Returns:
            List of StrategyScore sorted by overall_score (descending)
        """
        ranked = sorted(
            self.strategy_scores.values(),
            key=lambda x: x.overall_score,
            reverse=True
        )
        
        # Assign ranks
        for i, score in enumerate(ranked, 1):
            score.rank = i
        
        logger.info("Strategy Rankings:")
        for score in ranked:
            logger.info(f"  {score.rank}. {score.strategy_name}: {score.overall_score:.2f}")
        
        return ranked
    
    def generate_comparison_matrix(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate comprehensive comparison matrix.
        
        Returns:
            Dict with all metrics for each strategy
        """
        matrix = {}
        
        for name, score in self.strategy_scores.items():
            m = score.metrics
            matrix[name] = {
                'overall_score': score.overall_score,
                'rank': score.rank,
                'risk_adjusted_score': score.risk_adjusted_score,
                'return_score': score.return_score,
                'risk_management_score': score.risk_management_score,
                'trade_quality_score': score.trade_quality_score,
                'total_trades': m.total_trades,
                'winning_trades': m.winning_trades,
                'losing_trades': m.losing_trades,
                'win_rate': m.win_rate,
                'total_pnl': m.total_pnl,
                'total_return_pct': m.total_return_pct,
                'sharpe_ratio': m.sharpe_ratio,
                'max_drawdown_pct': m.max_drawdown_pct,
                'annual_return_pct': m.annual_return_pct,
                'avg_trade_duration': m.avg_trade_duration,
                'daily_avg_profit': m.daily_avg_profit,
                'sortino_ratio': m.extra_metrics.get('sortino_ratio', 0.0),
                'volatility_pct': m.extra_metrics.get('volatility_pct', 0.0),
                'calmar_ratio': m.extra_metrics.get('calmar_ratio', 0.0),
                'profit_factor': m.extra_metrics.get('profit_factor', 0.0),
                'avg_win': m.extra_metrics.get('avg_win', 0.0),
                'avg_loss': m.extra_metrics.get('avg_loss', 0.0),
                'consecutive_wins': m.extra_metrics.get('consecutive_wins', 0),
                'consecutive_losses': m.extra_metrics.get('consecutive_losses', 0),
            }
        
        return matrix
    
    def generate_comparison_report(self) -> str:
        """
        Generate human-readable comparison report.
        
        Returns:
            Formatted report string
        """
        self.rank_strategies()
        matrix = self.generate_comparison_matrix()
        
        lines = []
        lines.append("=" * 100)
        lines.append("STRATEGY PERFORMANCE COMPARISON REPORT")
        lines.append("=" * 100)
        lines.append("")
        
        # Rankings
        lines.append("RANKINGS")
        lines.append("-" * 100)
        for name, data in sorted(matrix.items(), key=lambda x: x[1]['rank']):
            lines.append(
                f"{data['rank']:2d}. {name:30s} | "
                f"Overall: {data['overall_score']:6.2f} | "
                f"Return: {data['total_return_pct']:7.2f}% | "
                f"Sharpe: {data['sharpe_ratio']:6.2f} | "
                f"MaxDD: {data['max_drawdown_pct']:6.2f}%"
            )
        lines.append("")
        
        # Detailed metrics
        lines.append("DETAILED METRICS COMPARISON")
        lines.append("-" * 100)
        
        # Get all metric names
        metric_keys = [
            'total_trades', 'win_rate', 'total_return_pct', 'annual_return_pct',
            'sharpe_ratio', 'sortino_ratio', 'max_drawdown_pct', 'volatility_pct',
            'calmar_ratio', 'profit_factor', 'avg_trade_duration'
        ]
        
        for key in metric_keys:
            lines.append(f"\n{key.upper().replace('_', ' ')}:")
            for name, data in sorted(matrix.items(), key=lambda x: x[1]['rank']):
                value = data.get(key, 0)
                if isinstance(value, float):
                    lines.append(f"  {name:30s}: {value:10.2f}")
                else:
                    lines.append(f"  {name:30s}: {value}")
        
        lines.append("")
        lines.append("=" * 100)
        
        return "\n".join(lines)
    
    def export_comparison_json(self, filepath: str) -> None:
        """
        Export comparison results to JSON.
        
        Args:
            filepath: Path to save JSON file
        """
        self.rank_strategies()
        matrix = self.generate_comparison_matrix()
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'strategies': matrix,
            'rankings': [
                {'rank': score.rank, 'name': score.strategy_name, 'score': score.overall_score}
                for score in sorted(self.strategy_scores.values(), key=lambda x: x.rank)
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Comparison exported to {filepath}")
    
    def get_winner(self) -> Optional[StrategyScore]:
        """
        Get the best-performing strategy.
        
        Returns:
            StrategyScore of winner, or None if no strategies added
        """
        if not self.strategy_scores:
            return None
        
        ranked = self.rank_strategies()
        return ranked[0] if ranked else None
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics across all strategies.
        
        Returns:
            Dict with aggregated statistics
        """
        if not self.strategy_scores:
            return {}
        
        scores = list(self.strategy_scores.values())
        metrics_list = [s.metrics for s in scores]
        
        return {
            'num_strategies': len(scores),
            'avg_sharpe_ratio': sum(m.sharpe_ratio for m in metrics_list) / len(metrics_list),
            'avg_total_return': sum(m.total_return_pct for m in metrics_list) / len(metrics_list),
            'avg_max_drawdown': sum(m.max_drawdown_pct for m in metrics_list) / len(metrics_list),
            'avg_win_rate': sum(m.win_rate for m in metrics_list) / len(metrics_list),
            'best_sharpe': max(m.sharpe_ratio for m in metrics_list),
            'best_return': max(m.total_return_pct for m in metrics_list),
            'best_win_rate': max(m.win_rate for m in metrics_list),
            'worst_max_drawdown': max(m.max_drawdown_pct for m in metrics_list),
        }
