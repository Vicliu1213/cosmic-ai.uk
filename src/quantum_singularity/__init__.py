"""
量子奇點模塊 (Quantum Singularity Module)
核心用途：處理量子奇點的檢測、穩定化和計算
"""

from .core import QuantumSingularityActor
from .vacuum import VacuumCoupler
from .grid import SpacetimeGrid
from .stabilizer import TopologicalStabilizer
from .qnn import QuantumNeuralNet
from .detector import SingularityDetector

__all__ = [
    'QuantumSingularityActor',
    'VacuumCoupler',
    'SpacetimeGrid',
    'TopologicalStabilizer',
    'QuantumNeuralNet',
    'SingularityDetector',
]

__version__ = '1.0.0'
__author__ = 'Cosmic Engine'
