"""相容層 — 委派至 src.layers.distributed.synergy"""

from src.layers.distributed.synergy import SynergyEngine as SynergyScaleRecorder
from src.layers.distributed.synergy import THEORIES, THEORY_LABELS

SynergyLevelSnapshot = dict
TheorySynergyMatrix = dict

__all__ = ["SynergyScaleRecorder", "SynergyLevelSnapshot", "TheorySynergyMatrix"]
