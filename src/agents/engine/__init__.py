"""
Agent Engine Module - 代理引擎模塊
交易引擎和多代理協調系統
"""

__version__ = "1.0.0"
__all__ = []

# 延遲導入以避免循環依賴
def __getattr__(name: str):
    if name == 'main':
        from . import main as _main
        return _main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
