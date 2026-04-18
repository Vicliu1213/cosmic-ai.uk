from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List

from .config import LayerConfig, CompressionConfig, DistributedConfig, LayerSystemConfig


@dataclass
class EnergySample:
    metric: str
    value: float
    unit: str
    source: str
    confidence: float = 1.0


@dataclass
class EnergyTrace:
    name: str
    samples: List[EnergySample]
    summary: str = ""


@dataclass
class PrecisionLayerResult:
    layer_name: str
    input_tokens: int
    output_tokens: int
    energy_reduction_ratio: float
    precision_score: float
    notes: List[str] = field(default_factory=list)


@dataclass
class EnergyTelemetry:
    traces: List[EnergyTrace]
    metadata: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "traces": [
                {
                    "name": trace.name,
                    "summary": trace.summary,
                    "samples": [asdict(sample) for sample in trace.samples],
                }
                for trace in self.traces
            ],
            "metadata": dict(self.metadata),
        }


FOUR_LAYER_TEMPLATE = [
    LayerConfig(
        name="energy-observation",
        precision_bits=16,
        compression_ratio=0.60,
        sample_window=256,
        tags=["measurement", "telemetry", "observability"],
    ),
    LayerConfig(
        name="energy-normalization",
        precision_bits=12,
        compression_ratio=0.42,
        sample_window=192,
        tags=["denoise", "aggregation", "normalization"],
    ),
    LayerConfig(
        name="energy-compression",
        precision_bits=8,
        compression_ratio=0.28,
        sample_window=128,
        tags=["entropy", "token-budget", "compression"],
    ),
    LayerConfig(
        name="energy-distribution",
        precision_bits=4,
        compression_ratio=0.14,
        sample_window=64,
        tags=["distributed", "adaptive", "scaling"],
    ),
]

DEFAULT_COMPRESSION = CompressionConfig(
    target_token_budget=2048,
    target_latency_ms=50,
    dynamic_scaling=True,
    entropy_floor=0.02,
    max_gradient_delta=0.10,
)

DEFAULT_DISTRIBUTED = DistributedConfig(
    enabled=True,
    workers=8,
    shard_size=64,
    adaptive_rebalancing=True,
    locality_bias=0.85,
)

DEFAULT_SYSTEM_CONFIG = LayerSystemConfig(
    layers=FOUR_LAYER_TEMPLATE,
    compression=DEFAULT_COMPRESSION,
    distributed=DEFAULT_DISTRIBUTED,
    notes={
        "goal": "minimize token consumption while preserving high precision",
        "mode": "financial-whale-grade aggressive optimization",
    },
)
