from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List

from .config import DataSourceConfig, DataLayerConfig


@dataclass
class DataSource:
    name: str
    source_type: str
    endpoint: str
    enabled: bool = True
    refresh_seconds: int = 300
    status: str = 'available'
    policy: str = 'compliant'
    tags: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class DataSourceRegistry:
    sources: List[DataSource]
    notes: Dict[str, str] = field(default_factory=dict)

    def enabled_sources(self) -> List[DataSource]:
        return [source for source in self.sources if source.status != 'disabled']

    def compliant_sources(self) -> List[DataSource]:
        return [source for source in self.sources if source.policy == 'compliant']

    def as_dict(self) -> Dict[str, object]:
        return {
            'sources': [source.as_dict() for source in self.sources],
            'notes': dict(self.notes),
        }


@dataclass
class DataCollectionResult:
    collected: Dict[str, Dict[str, object]]
    summary: Dict[str, object]
