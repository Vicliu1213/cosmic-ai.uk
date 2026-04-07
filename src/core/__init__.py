#!/usr/bin/env python3
"""
Core trading system modules
核心交易系統模塊

Main Analyzers:
  - EnhancedQuantumMarketAnalyzer: Enhanced quantum market analyzer with classical algorithms
  - SingularityResonanceTradingSystem: Main singularity resonance trading system
  - MarketRegimeDetector: Market regime detection engine
  
System Engines:
  - BaseEngine: Base engine class
  - EngineFactory: Factory for creating engines
  - EngineRegistry: Registry for managing engines
  - EngineConfig: Configuration data class for engines
  
Managers:
  - CoreModuleManager: Main module manager for core components
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def __getattr__(name: str) -> Any:
    """動態導入核心系統組件"""
    
    # 主要分析器
    if name == 'EnhancedQuantumMarketAnalyzer':
        try:
            from .enhanced_quantum_market_analyzer import EnhancedQuantumMarketAnalyzer
            return EnhancedQuantumMarketAnalyzer
        except ImportError as e:
            logger.warning(f"Could not import EnhancedQuantumMarketAnalyzer: {e}")
            return None
    
    elif name == 'SingularityResonanceTradingSystem':
        try:
            from .singularity_trading_system import SingularityResonanceTradingSystem
            return SingularityResonanceTradingSystem
        except ImportError as e:
            logger.warning(f"Could not import SingularityResonanceTradingSystem: {e}")
            return None
    
    elif name == 'MarketRegimeDetector':
        try:
            from .market_regime_detector import MarketRegimeDetector
            return MarketRegimeDetector
        except ImportError as e:
            logger.warning(f"Could not import MarketRegimeDetector: {e}")
            return None
    
    # 基礎引擎
    elif name == 'BaseEngine':
        try:
            from .base_engine import BaseEngine
            return BaseEngine
        except ImportError as e:
            logger.warning(f"Could not import BaseEngine: {e}")
            return None
    
    elif name == 'EngineConfig':
        try:
            from .base_engine import EngineConfig
            return EngineConfig
        except ImportError as e:
            logger.warning(f"Could not import EngineConfig: {e}")
            return None
    
    # 引擎工廠和註冊表
    elif name == 'EngineFactory':
        try:
            from .engine_factory import EngineFactory
            return EngineFactory
        except ImportError as e:
            logger.warning(f"Could not import EngineFactory: {e}")
            return None
    
    elif name == 'EngineRegistry':
        try:
            from .engine_registry import EngineRegistry
            return EngineRegistry
        except ImportError as e:
            logger.warning(f"Could not import EngineRegistry: {e}")
            return None
    
    # 管理器
    elif name == 'CoreModuleManager':
        try:
            from .main import CoreModuleManager
            return CoreModuleManager
        except ImportError as e:
            logger.warning(f"Could not import CoreModuleManager: {e}")
            return None
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# 嘗試直接導入可用的組件
try:
    from .enhanced_quantum_market_analyzer import EnhancedQuantumMarketAnalyzer
except ImportError:
    logger.debug("EnhancedQuantumMarketAnalyzer not available")
    EnhancedQuantumMarketAnalyzer = None

try:
    from .singularity_trading_system import SingularityResonanceTradingSystem
except ImportError:
    logger.debug("SingularityResonanceTradingSystem not available")
    SingularityResonanceTradingSystem = None

try:
    from .main import CoreModuleManager
except ImportError:
    logger.debug("CoreModuleManager not available")
    CoreModuleManager = None


__all__ = [
    # 主要分析器
    'EnhancedQuantumMarketAnalyzer',
    'SingularityResonanceTradingSystem',
    'MarketRegimeDetector',
    
    # 基礎引擎和配置
    'BaseEngine',
    'EngineConfig',
    
    # 工廠和註冊表
    'EngineFactory',
    'EngineRegistry',
    
    # 管理器
    'CoreModuleManager',
]

