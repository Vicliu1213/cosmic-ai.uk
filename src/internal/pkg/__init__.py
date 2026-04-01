"""
Internal Pkg Module - 內部包模塊
審計和度量指標
"""

__version__ = "1.0.0"

try:
    from . import audit
    from . import metric
    __all__ = ['audit', 'metric']
except ImportError:
    __all__ = []
