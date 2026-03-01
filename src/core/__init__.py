#!/usr/bin/env python3
"""
Core trading system modules
核心交易系統模塊

Exports:
- EnhancedQuantumMarketAnalyzer: Enhanced quantum market analyzer with classical algorithms
- SingularityTradingSystem: Main singularity resonance trading system
"""

from typing import Any

def __getattr__(name) -> Any:
    if name == 'EnhancedQuantumMarketAnalyzer':
        from .enhanced_quantum_market_analyzer import EnhancedQuantumMarketAnalyzer
        return EnhancedQuantumMarketAnalyzer
    elif name == 'SingularityResonanceTradingSystem':
        from .singularity_trading_system import SingularityResonanceTradingSystem
        return SingularityResonanceTradingSystem
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'EnhancedQuantumMarketAnalyzer',
    'SingularityResonanceTradingSystem',
]
