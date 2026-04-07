"""
Analysis Module - 市場分析與信號生成
包含技術指標、信號生成、多框架分析等
"""

import logging

# 導入技術指標函數
try:
    from .indicators import rsi, macd, atr, sma, obv
except ImportError as e:
    logging.warning(f"⚠️  無法導入 indicators: {e}")
    rsi = None
    macd = None
    atr = None
    sma = None
    obv = None

# 導入信號生成器
try:
    from .signal_generator import SignalGenerator, TradingSignal, SignalStrength
except ImportError as e:
    logging.warning(f"⚠️  無法導入 signal_generator: {e}")
    SignalGenerator = None
    TradingSignal = None
    SignalStrength = None

# 可選的機器學習分析器
try:
    from .forest import ForestAnalyzer
except ImportError:
    ForestAnalyzer = None

try:
    from .multiframe import MultiframeAnalyzer
except ImportError:
    MultiframeAnalyzer = None

try:
    from .singularity import SingularityDetector
except ImportError:
    SingularityDetector = None

__all__ = [
    'rsi', 'macd', 'atr', 'sma', 'obv',
    'SignalGenerator', 'TradingSignal', 'SignalStrength',
    'ForestAnalyzer', 'MultiframeAnalyzer', 'SingularityDetector',
]
