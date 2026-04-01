"""
Utils Logging Module - 日誌工具模塊
AI 日誌系統
"""

__version__ = "1.0.0"

try:
    from .ai_logging import *
    __all__ = ['ai_logging']
except ImportError:
    __all__ = []
