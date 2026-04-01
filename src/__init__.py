"""
Cosmic AI - 量子交易系統主模塊
集成所有核心功能模塊
"""

__version__ = "1.0.0"
__author__ = "Cosmic AI Team"
__description__ = "Quantum-Enhanced AI Trading System with Hybrid Algorithms"

# 延遲導入主模塊 - 避免循環依賴
def __getattr__(name: str):
    """動態導入主系統類"""
    from .main import CosmicAITradingSystem
    
    if name == 'CosmicAITradingSystem':
        return CosmicAITradingSystem
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['CosmicAITradingSystem']
