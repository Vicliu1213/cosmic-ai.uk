"""相容層 — 委派至 src.layers.distributed.synergy 核心實作"""

from src.layers.distributed.synergy import SynergyEngine as SynergyScaleRecorder
from src.layers.distributed.synergy import SynergyEngine

__all__ = ["SynergyScaleRecorder", "SynergyEngine"]
