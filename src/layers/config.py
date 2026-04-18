from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class LayerConfig:
    name: str
    precision_bits: int
    compression_ratio: float
    sample_window: int
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CompressionConfig:
    target_token_budget: int
    target_latency_ms: int
    dynamic_scaling: bool = True
    entropy_floor: float = 0.01
    max_gradient_delta: float = 0.15


@dataclass(frozen=True)
class DistributedConfig:
    enabled: bool = True
    workers: int = 4
    shard_size: int = 128
    adaptive_rebalancing: bool = True
    locality_bias: float = 0.8


@dataclass(frozen=True)
class LayerSystemConfig:
    layers: List[LayerConfig]
    compression: CompressionConfig
    distributed: DistributedConfig
    notes: Dict[str, Any] = field(default_factory=dict)
