from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(frozen=True)
class DataSourceConfig:
    name: str
    source_type: str
    endpoint: str
    enabled: bool = True
    refresh_seconds: int = 300
    policy: str = 'compliant'
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class DataLayerConfig:
    max_sources: int = 8
    allow_third_party: bool = True
    allow_derived: bool = True
    allow_public_feeds: bool = True
    allow_onchain: bool = True
    allow_regulatory: bool = True
    allow_dark_web: bool = False
    source_budget: int = 6
    notes: Dict[str, Any] = field(default_factory=dict)
