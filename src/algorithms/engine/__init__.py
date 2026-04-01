"""
Algorithms Engine Module - 算法引擎模塊
交易所適配器和智能例程
"""

__version__ = "1.0.0"

try:
    from . import binance_adapter
    from . import bitget_adapter
    from . import smart_routine
    __all__ = ['binance_adapter', 'bitget_adapter', 'smart_routine']
except ImportError:
    __all__ = []
