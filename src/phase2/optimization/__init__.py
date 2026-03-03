#!/usr/bin/env python3
"""
Phase 2 優化模塊初始化 (Phase 2 Optimization Module Initialization)

統-超指數遞歸協同增長 (Unified Hyper-Exponential Recursive Synergistic Growth)

五個基礎突破系統的統一導出
"""

from .energy_optimizer import (
    EnergyOptimizer,
    EnergyMode,
    EnergyMetrics,
    CompressionState,
    CompressionStrategy,
    QuantumCompressionStrategy,
    RecursiveCompressionStrategy
)

from .precision_enhancer import (
    PrecisionEnhancer,
    PrecisionLevel,
    PrecisionMetrics,
    PrecisionState,
    PrecisionCorrection,
    RecursivePrecisionCorrection,
    QuantumPrecisionEnhancement,
    AdaptivePrecisionCorrection
)

from .capacity_manager import (
    CapacityManager,
    CapacityTier,
    CapacityMetrics,
    CapacityState,
    CapacityScaler,
    ExponentialCapacityScaler,
    RecursiveCapacityScaler,
    AdaptiveCapacityScaler
)

from .coordination_scheduler import (
    CoordinationScheduler,
    AgentRole,
    TaskPriority,
    CoordinationMetrics,
    Task,
    CoordinationState,
    ResonanceCoordinator,
    RecursiveTaskComposer
)

from .theory_validator import (
    TheoryValidator,
    ValidationLevel,
    VerificationStatus,
    ValidationMetrics,
    VerificationResult,
    HypothesisValidator,
    RecursiveHypothesisValidator,
    SynergisticValidationFusion
)

__all__ = [
    # Energy Optimizer
    "EnergyOptimizer",
    "EnergyMode",
    "EnergyMetrics",
    "CompressionState",
    "CompressionStrategy",
    "QuantumCompressionStrategy",
    "RecursiveCompressionStrategy",
    
    # Precision Enhancer
    "PrecisionEnhancer",
    "PrecisionLevel",
    "PrecisionMetrics",
    "PrecisionState",
    "PrecisionCorrection",
    "RecursivePrecisionCorrection",
    "QuantumPrecisionEnhancement",
    "AdaptivePrecisionCorrection",
    
    # Capacity Manager
    "CapacityManager",
    "CapacityTier",
    "CapacityMetrics",
    "CapacityState",
    "CapacityScaler",
    "ExponentialCapacityScaler",
    "RecursiveCapacityScaler",
    "AdaptiveCapacityScaler",
    
    # Coordination Scheduler
    "CoordinationScheduler",
    "AgentRole",
    "TaskPriority",
    "CoordinationMetrics",
    "Task",
    "CoordinationState",
    "ResonanceCoordinator",
    "RecursiveTaskComposer",
    
    # Theory Validator
    "TheoryValidator",
    "ValidationLevel",
    "VerificationStatus",
    "ValidationMetrics",
    "VerificationResult",
    "HypothesisValidator",
    "RecursiveHypothesisValidator",
    "SynergisticValidationFusion"
]
