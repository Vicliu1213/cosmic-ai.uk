"""
Utils Module - 工具庫
提供日誌、數據保存、緩存等基礎功能
"""

import logging

# 導入核心工具類
try:
    from .action_protocol import Action, normalize_action, is_open_action, is_close_action
except ImportError as e:
    logging.warning(f"⚠️  無法導入 action_protocol: {e}")
    Action = None

try:
    from .logger import ColoredLogger, log, setup_logger
except ImportError as e:
    logging.warning(f"⚠️  無法導入 logger: {e}")
    log = None

try:
    from .data_saver import DataSaver, CustomJSONEncoder
except ImportError as e:
    logging.warning(f"⚠️  無法導入 data_saver: {e}")
    DataSaver = None

try:
    from .json_utils import safe_json_dumps, safe_json_dump
except ImportError as e:
    logging.warning(f"⚠️  無法導入 json_utils: {e}")

try:
    from .kline_cache import KlineCache
except ImportError as e:
    logging.warning(f"⚠️  無法導入 kline_cache: {e}")
    KlineCache = None

# 可選通知模塊
try:
    from .notifications.telegram_bot import TelegramNotifier
except ImportError:
    TelegramNotifier = None

__all__ = [
    'Action', 'normalize_action', 'is_open_action', 'is_close_action',
    'ColoredLogger', 'log', 'setup_logger',
    'DataSaver', 'CustomJSONEncoder',
    'safe_json_dumps', 'safe_json_dump',
    'KlineCache',
    'TelegramNotifier',
]
