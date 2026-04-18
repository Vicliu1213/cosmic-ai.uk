from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class EnhancedHybridConfig:
    name: str = 'enhanced_hybrid'
    realtime_interval_sec: float = 0.0
    watch_cycles: int = 2
    max_failures: int = 3
    modules: List[str] = field(default_factory=lambda: ['enhanced_classic', 'layers', 'module_catalog', 'dashboard'])
    metadata: Dict[str, str] = field(default_factory=dict)
