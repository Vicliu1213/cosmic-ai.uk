from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class HestCheck:
    name: str
    target: str
    threshold: float = 0.8
    enabled: bool = True
    realtime: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class HestVerificationConfig:
    name: str = 'hest_verification'
    realtime_interval_sec: float = 1.0
    max_failures: int = 3
    watch_cycles: int = 3
    checks: List[HestCheck] = field(default_factory=lambda: [
        HestCheck(name='layers', target='layers', threshold=1.0, tags=['energy', 'compression', 'precision', 'compute']),
        HestCheck(name='enhanced_classic', target='enhanced_classic', threshold=1.0, tags=['recommendation', 'indexing']),
        HestCheck(name='catalog', target='module_catalog', threshold=1.0, tags=['ui', 'module']),
        HestCheck(name='dashboard', target='dashboard', threshold=1.0, tags=['ui', 'real-time']),
        HestCheck(name='sharpe_growth', target='sharpe', threshold=1.05, tags=['risk-adjusted', 'growth']),
        HestCheck(name='growth_stack', target='growth_stack', threshold=1.0, tags=['nonlinear', 'stacked']),
        HestCheck(name='strategy_winrate', target='strategy', threshold=1.0, tags=['live', 'backtest', 'win-rate']),
    ])
    metadata: Dict[str, str] = field(default_factory=dict)
