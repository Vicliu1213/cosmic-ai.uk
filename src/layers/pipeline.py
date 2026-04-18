from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List

from .config import LayerSystemConfig
from .core import DEFAULT_SYSTEM_CONFIG, EnergySample, EnergyTelemetry, EnergyTrace, PrecisionLayerResult


class EnergyPrecisionCompressionPipeline:
    def __init__(self, config: LayerSystemConfig | None = None) -> None:
        self.config = config or DEFAULT_SYSTEM_CONFIG

    def collect_four_sources(self) -> EnergyTelemetry:
        traces = [
            EnergyTrace(
                name="system-telemetry",
                summary="CPU/GPU/RAM/IO baseline trace",
                samples=[
                    EnergySample("cpu_load", 0.42, "ratio", "runtime"),
                    EnergySample("memory_pressure", 0.31, "ratio", "runtime"),
                ],
            ),
            EnergyTrace(
                name="resource-pressure",
                summary="scheduler and queue pressure",
                samples=[
                    EnergySample("queue_depth", 12, "jobs", "scheduler"),
                    EnergySample("shard_skew", 0.07, "ratio", "scheduler"),
                ],
            ),
            EnergyTrace(
                name="precision-quality",
                summary="precision vs compression quality",
                samples=[
                    EnergySample("bit_loss", 0.03, "ratio", "model"),
                    EnergySample("token_savings", 0.58, "ratio", "model"),
                ],
            ),
            EnergyTrace(
                name="distributed-locality",
                summary="shard locality and adaptive rebalance",
                samples=[
                    EnergySample("locality", 0.87, "ratio", "cluster"),
                    EnergySample("rebalance_cost", 0.12, "ratio", "cluster"),
                ],
            ),
        ]
        return EnergyTelemetry(traces=traces, metadata={"mode": "four-layer-energy-precision"})

    def run(self) -> Dict[str, object]:
        telemetry = self.collect_four_sources()
        results: List[PrecisionLayerResult] = []
        input_tokens = 10000
        current_tokens = input_tokens
        precision_score = 0.99

        for layer in self.config.layers:
            if not layer.enabled:
                continue
            output_tokens = max(1, int(current_tokens * layer.compression_ratio))
            precision_score = max(0.0, precision_score - (1.0 - layer.compression_ratio) * 0.01)
            results.append(
                PrecisionLayerResult(
                    layer_name=layer.name,
                    input_tokens=current_tokens,
                    output_tokens=output_tokens,
                    energy_reduction_ratio=1.0 - layer.compression_ratio,
                    precision_score=round(precision_score, 4),
                    notes=[
                        f"precision_bits={layer.precision_bits}",
                        f"window={layer.sample_window}",
                        f"tags={','.join(layer.tags)}",
                    ],
                )
            )
            current_tokens = output_tokens

        return {
            "config": {
                "compression": asdict(self.config.compression),
                "distributed": asdict(self.config.distributed),
                "layers": [asdict(layer) for layer in self.config.layers],
                "notes": dict(self.config.notes),
            },
            "telemetry": telemetry.as_dict(),
            "results": [asdict(result) for result in results],
            "final": {
                "input_tokens": input_tokens,
                "output_tokens": current_tokens,
                "token_reduction_ratio": round(1.0 - (current_tokens / input_tokens), 4),
                "precision_score": round(precision_score, 4),
                "distributed_workers": self.config.distributed.workers,
                "dynamic_scaling": self.config.distributed.adaptive_rebalancing,
            },
        }


def build_default_pipeline() -> EnergyPrecisionCompressionPipeline:
    return EnergyPrecisionCompressionPipeline(DEFAULT_SYSTEM_CONFIG)
