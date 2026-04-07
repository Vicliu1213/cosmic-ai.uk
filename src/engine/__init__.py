#!/usr/bin/env python3
"""
Enhanced quantum engine modules
增強型量子引擎模塊

Hybrid Quantum-Classical System:
  - HybridQuantumClassicalEngine: Main engine with automatic degradation
  - QuantumModeExecutor: Quantum algorithm executor
  - ClassicalModeExecutor: Enhanced classical algorithm executor
  - HybridModeExecutor: Blended quantum-classical executor
  - CapabilityDetector: Auto-detects available quantum capabilities

Core Engines:
  - EnhancedQuantumEngineCompiler: Main compiler integrating all quantum algorithms
  - QuantumEngine: Classical quantum simulation engine
  - EvolutionEngine: Evolutionary algorithm engine
  - RayDistributedEngine: Distributed Ray-based engine
  
Signal Processing:
  - EnhancedSignalProcessor: FFT-based signal processing with filtering
  - StateSpaceOptimizer: PCA-based state space optimization
  - ProbabilisticDecisionEngine: Signal coherence-based decision engine
  - CorrelationAnalyzer: Multi-variable correlation analysis

Data Models:
  - ClassicalQuantumState: Quantum state representation
  
Managers:
  - EngineModuleManager: Main module manager for all engines
"""

import logging
from typing import Dict, Any, Optional, List

# 导入配置模块
try:
    from .config import (
        EngineConfigLoader,
        get_engine_config,
        get_system_defaults,
        validate_config
    )
except ImportError as e:
    logger.warning(f"Could not import config module: {e}")
    EngineConfigLoader = None
    get_engine_config = None
    get_system_defaults = None
    validate_config = None

logger = logging.getLogger(__name__)

# 延遲導入核心引擎
def __getattr__(name: str) -> Any:
    """動態導入引擎組件"""
    
    # 混合量子-經典引擎 (最高優先級)
    if name == 'HybridQuantumClassicalEngine':
        try:
            from .hybrid_quantum_classical_engine import HybridQuantumClassicalEngine
            return HybridQuantumClassicalEngine
        except ImportError as e:
            logger.warning(f"Could not import HybridQuantumClassicalEngine: {e}")
            return None
    
    elif name == 'QuantumModeExecutor':
        try:
            from .hybrid_quantum_classical_engine import QuantumModeExecutor
            return QuantumModeExecutor
        except ImportError as e:
            logger.warning(f"Could not import QuantumModeExecutor: {e}")
            return None
    
    elif name == 'ClassicalModeExecutor':
        try:
            from .hybrid_quantum_classical_engine import ClassicalModeExecutor
            return ClassicalModeExecutor
        except ImportError as e:
            logger.warning(f"Could not import ClassicalModeExecutor: {e}")
            return None
    
    elif name == 'HybridModeExecutor':
        try:
            from .hybrid_quantum_classical_engine import HybridModeExecutor
            return HybridModeExecutor
        except ImportError as e:
            logger.warning(f"Could not import HybridModeExecutor: {e}")
            return None
    
    elif name == 'CapabilityDetector':
        try:
            from .hybrid_quantum_classical_engine import CapabilityDetector
            return CapabilityDetector
        except ImportError as e:
            logger.warning(f"Could not import CapabilityDetector: {e}")
            return None
    
    elif name == 'get_hybrid_engine':
        try:
            from .hybrid_quantum_classical_engine import get_hybrid_engine
            return get_hybrid_engine
        except ImportError as e:
            logger.warning(f"Could not import get_hybrid_engine: {e}")
            return None
    
    # 核心引擎
    elif name == 'EnhancedQuantumEngineCompiler':
        try:
            from .enhanced_quantum_engine import EnhancedQuantumEngineCompiler
            return EnhancedQuantumEngineCompiler
        except ImportError as e:
            logger.warning(f"Could not import EnhancedQuantumEngineCompiler: {e}")
            return None
    
    elif name == 'QuantumEngine':
        try:
            from .quantum_engine import QuantumEngine
            return QuantumEngine
        except ImportError as e:
            logger.warning(f"Could not import QuantumEngine: {e}")
            return None
    
    elif name == 'EvolutionEngine':
        try:
            from .evolution_engine import EvolutionEngine
            return EvolutionEngine
        except ImportError as e:
            logger.warning(f"Could not import EvolutionEngine: {e}")
            return None
    
    elif name == 'RayDistributedEngine':
        try:
            from .ray_distributed_engine import RayDistributedEngine
            return RayDistributedEngine
        except ImportError as e:
            logger.warning(f"Could not import RayDistributedEngine: {e}")
            return None
    
    # 信號處理組件
    elif name == 'EnhancedSignalProcessor':
        try:
            from .enhanced_quantum_engine import EnhancedSignalProcessor
            return EnhancedSignalProcessor
        except ImportError as e:
            logger.warning(f"Could not import EnhancedSignalProcessor: {e}")
            return None
    
    elif name == 'StateSpaceOptimizer':
        try:
            from .enhanced_quantum_engine import StateSpaceOptimizer
            return StateSpaceOptimizer
        except ImportError as e:
            logger.warning(f"Could not import StateSpaceOptimizer: {e}")
            return None
    
    elif name == 'ProbabilisticDecisionEngine':
        try:
            from .enhanced_quantum_engine import ProbabilisticDecisionEngine
            return ProbabilisticDecisionEngine
        except ImportError as e:
            logger.warning(f"Could not import ProbabilisticDecisionEngine: {e}")
            return None
    
    elif name == 'CorrelationAnalyzer':
        try:
            from .enhanced_quantum_engine import CorrelationAnalyzer
            return CorrelationAnalyzer
        except ImportError as e:
            logger.warning(f"Could not import CorrelationAnalyzer: {e}")
            return None
    
    elif name == 'ClassicalQuantumState':
        try:
            from .enhanced_quantum_engine import ClassicalQuantumState
            return ClassicalQuantumState
        except ImportError as e:
            logger.warning(f"Could not import ClassicalQuantumState: {e}")
            return None
    
    # 管理器
    elif name == 'EngineModuleManager':
        try:
            from .main import EngineModuleManager
            return EngineModuleManager
        except ImportError as e:
            logger.warning(f"Could not import EngineModuleManager: {e}")
            return None
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# 直接導入可用的組件
try:
    from .hybrid_quantum_classical_engine import (
        HybridQuantumClassicalEngine,
        QuantumModeExecutor,
        ClassicalModeExecutor,
        HybridModeExecutor,
        CapabilityDetector,
        get_hybrid_engine,
    )
except ImportError:
    logger.debug("Hybrid quantum-classical components not available")
    HybridQuantumClassicalEngine = None
    QuantumModeExecutor = None
    ClassicalModeExecutor = None
    HybridModeExecutor = None
    CapabilityDetector = None
    get_hybrid_engine = None

try:
    from .enhanced_quantum_engine import (
        EnhancedQuantumEngineCompiler,
        StateSpaceOptimizer,
        ProbabilisticDecisionEngine,
        CorrelationAnalyzer,
        EnhancedSignalProcessor,
        ClassicalQuantumState,
    )
except ImportError:
    logger.debug("Some enhanced quantum engine components not available")
    EnhancedQuantumEngineCompiler = None
    StateSpaceOptimizer = None
    ProbabilisticDecisionEngine = None
    CorrelationAnalyzer = None
    EnhancedSignalProcessor = None
    ClassicalQuantumState = None

try:
    from .main import EngineModuleManager
except ImportError:
    logger.debug("EngineModuleManager not available")
    EngineModuleManager = None


__all__ = [
    # 混合量子-經典系統 (最新)
    'HybridQuantumClassicalEngine',
    'QuantumModeExecutor',
    'ClassicalModeExecutor',
    'HybridModeExecutor',
    'CapabilityDetector',
    'get_hybrid_engine',
    
    # 核心引擎
    'EnhancedQuantumEngineCompiler',
    'QuantumEngine',
    'EvolutionEngine',
    'RayDistributedEngine',
    
    # 信號處理
    'EnhancedSignalProcessor',
    'StateSpaceOptimizer',
    'ProbabilisticDecisionEngine',
    'CorrelationAnalyzer',
    
    # 數據模型
    'ClassicalQuantumState',
    
    # 管理器
    'EngineModuleManager',
    
    # 配置系統
    'EngineConfigLoader',
    'get_engine_config',
    'get_system_defaults',
    'validate_config',
]


