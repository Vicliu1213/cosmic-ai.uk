"""
Quantum Module - 量子計算系統
提供量子場論、混合量子算法等量子增強功能
"""

import logging
from typing import Any

def __getattr__(name: str) -> Any:
    """延遲加載量子組件 - 避免重量級依賴問題"""
    components = {
        'QuantumFieldTheorySystem': '.quantum_field_theory_system.QuantumFieldTheorySystem',
        'QuantumGeneticAlgorithm': '.quantum_genetic_algorithm.QuantumGeneticAlgorithm',
        'QuantumGroverTradingAlgorithm': '.quantum_grover_trading_algorithm.QuantumGroverTradingAlgorithm',
        'HybridQuantumEnhancedAlgorithm': '.hybrid_quantum_algorithm.HybridQuantumEnhancedAlgorithm',
    }
    
    if name in components:
        try:
            module_path, class_name = components[name].rsplit('.', 1)
            module = __import__(f'src.quantum{module_path}', fromlist=[class_name])
            cls = getattr(module, class_name, None)
            if cls:
                return cls
        except (ImportError, AttributeError) as e:
            logging.warning(f"⚠️  無法加載 {name}: {e}")
            return None
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'QuantumFieldTheorySystem',
    'QuantumGeneticAlgorithm',
    'QuantumGroverTradingAlgorithm',
    'HybridQuantumEnhancedAlgorithm',
]
