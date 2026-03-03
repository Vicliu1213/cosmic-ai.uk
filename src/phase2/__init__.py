#!/usr/bin/env python3
"""
Phase 2 主模塊初始化 (Phase 2 Main Module Initialization)

五個基礎突破系統的主入口
Main entry point for Five Breakthrough System
"""

from .five_breakthrough_system import (
    FiveBreakthroughSystem,
    PhaseBreakthroughStatus
)

from .optimization import (
    # Energy Optimizer
    EnergyOptimizer,
    EnergyMode,
    EnergyMetrics,
    
    # Precision Enhancer
    PrecisionEnhancer,
    PrecisionLevel,
    PrecisionMetrics,
    
    # Capacity Manager
    CapacityManager,
    CapacityTier,
    CapacityMetrics,
    
    # Coordination Scheduler
    CoordinationScheduler,
    AgentRole,
    TaskPriority,
    CoordinationMetrics,
    Task,
    
    # Theory Validator
    TheoryValidator,
    ValidationLevel,
    VerificationStatus,
    ValidationMetrics
)

__all__ = [
    # Main System
    "FiveBreakthroughSystem",
    "PhaseBreakthroughStatus",
    
    # Energy Optimizer
    "EnergyOptimizer",
    "EnergyMode",
    "EnergyMetrics",
    
    # Precision Enhancer
    "PrecisionEnhancer",
    "PrecisionLevel",
    "PrecisionMetrics",
    
    # Capacity Manager
    "CapacityManager",
    "CapacityTier",
    "CapacityMetrics",
    
    # Coordination Scheduler
    "CoordinationScheduler",
    "AgentRole",
    "TaskPriority",
    "CoordinationMetrics",
    "Task",
    
    # Theory Validator
    "TheoryValidator",
    "ValidationLevel",
    "VerificationStatus",
    "ValidationMetrics"
]
