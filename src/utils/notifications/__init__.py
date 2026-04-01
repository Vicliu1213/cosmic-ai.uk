"""
Utils Notifications Module - 通知模塊
Telegram 機器人和通知系統
"""

__version__ = "1.0.0"

try:
    from .telegram_bot import *
    __all__ = ['telegram_bot']
except ImportError:
    __all__ = []
