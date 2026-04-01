"""
技术指标计算模块，基于 TA-Lib 或自定义实现。
如果 TA-Lib 未安装，使用纯 Python 回退。
"""
import numpy as np
import pandas as pd

try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    print("警告: TA-Lib 未安装，将使用简化的 Python 实现。")


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """相对强弱指数"""
    if HAS_TALIB:
        return talib.RSI(close, timeperiod=period)
    # 纯 Python 实现
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def macd(close: pd.Series, fast=12, slow=26, signal=9):
    """MACD 指标"""
    if HAS_TALIB:
        macd, macd_signal, macd_hist = talib.MACD(close, fast, slow, signal)
        return macd, macd_signal, macd_hist
    # 简化实现
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """平均真实波幅"""
    if HAS_TALIB:
        return talib.ATR(high, low, close, timeperiod=period)
    # 纯 Python 实现
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def sma(close: pd.Series, period: int) -> pd.Series:
    """简单移动平均"""
    if HAS_TALIB:
        return talib.SMA(close, timeperiod=period)
    return close.rolling(window=period).mean()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """能量潮"""
    if HAS_TALIB:
        return talib.OBV(close, volume)
    # 简化实现
    obv = np.zeros(len(close))
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv[i] = obv[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv[i] = obv[i-1] - volume.iloc[i]
        else:
            obv[i] = obv[i-1]
    return pd.Series(obv, index=close.index)
