"""
Data Module - 數據處理與驗證
包含K線驗證、數據處理和特徵提取
"""

import logging

try:
    from .validator import DataValidator
except ImportError as e:
    logging.warning(f"⚠️  無法導入 validator: {e}")
    DataValidator = None

try:
    from .processor import MarketDataProcessor
except ImportError as e:
    logging.warning(f"⚠️  無法導入 processor: {e}")
    MarketDataProcessor = None

try:
    from .kline_validator import KlineValidator
except ImportError as e:
    logging.warning(f"⚠️  無法導入 kline_validator: {e}")
    KlineValidator = None

__all__ = [
    'DataValidator',
    'MarketDataProcessor',
    'KlineValidator',
]
