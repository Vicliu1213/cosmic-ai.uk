from __future__ import annotations

from typing import Any, Dict, List


class SelfEvolve:
    def __init__(self, trade_history=None, review_interval: int = 1000, min_win_rate: float = 0.5):
        self.trade_history: List[Dict[str, Any]] = trade_history or []
        self.review_interval = review_interval
        self.min_win_rate = min_win_rate
        self.last_review: Dict[str, Any] | None = None

    def ingest_trade(self, trade_result: Dict[str, Any]) -> None:
        self.trade_history.append(trade_result)

    def summarize_window(self) -> Dict[str, Any]:
        total = len(self.trade_history)
        wins = sum(1 for item in self.trade_history if item.get('win'))
        losses = total - wins
        pnl = sum(float(item.get('pnl', 0.0)) for item in self.trade_history)
        win_rate = wins / total if total else 0.0
        return {
            'trade_count': total,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'net_pnl': pnl,
        }

    def review(self) -> Dict[str, Any]:
        summary = self.summarize_window()
        should_optimize = summary['trade_count'] >= max(1, self.review_interval)
        if summary['trade_count'] == 0:
            action = 'tighten'
        elif summary['win_rate'] >= self.min_win_rate:
            action = 'retain' if not should_optimize else 'compound'
        else:
            action = 'tighten'

        self.last_review = {
            **summary,
            'review_interval': self.review_interval,
            'should_optimize': should_optimize,
            'action': action,
        }
        return self.last_review

    def next_parameter_patch(self) -> Dict[str, Any]:
        review = self.last_review or self.review()
        if review['action'] in {'retain', 'compound'}:
            return {
                'slippage_tolerance_multiplier': 0.95,
                'confidence_floor_delta': 0.02,
                'position_size_delta': 0.0,
            }
        return {
            'slippage_tolerance_multiplier': 0.8,
            'confidence_floor_delta': 0.05,
            'position_size_delta': -0.1,
        }
