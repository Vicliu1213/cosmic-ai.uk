"""
奇点检测器：综合多个因子，计算市场奇点概率。
"""
import numpy as np
import pandas as pd
from .indicators import atr


class SingularityDetector:
    def __init__(self):
        self.history = []
        self.threshold = 0.7

    def detect(self, df: pd.DataFrame, technical_indicators: dict) -> float:
        """返回奇点概率（0-1）"""
        # 1. 价格加速度
        price_acc = self._price_acceleration(df)

        # 2. 波动率突破
        vol_break = self._volatility_breakout(df)

        # 3. 成交量异常
        vol_anom = self._volume_anomaly(df)

        # 4. 市场情绪极端（从技术指标中提取）
        sentiment = self._sentiment_extreme(technical_indicators)

        # 5. 流动性冲击（价差）
        liquid = self._liquidity_shock(df)

        # 加权组合
        score = (price_acc * 0.3 +
                 vol_break * 0.25 +
                 vol_anom * 0.2 +
                 sentiment * 0.15 +
                 liquid * 0.1)

        # 转换为概率
        prob = 1 / (1 + np.exp(-10 * (score - 0.5)))
        prob = min(1.0, max(0.0, prob))

        # 记录历史
        self.history.append({
            'timestamp': pd.Timestamp.now(),
            'score': score,
            'probability': prob,
            'components': {
                'price_acceleration': price_acc,
                'volatility_breakout': vol_break,
                'volume_anomaly': vol_anom,
                'sentiment_extreme': sentiment,
                'liquidity_shock': liquid
            }
        })

        return prob

    def _price_acceleration(self, df: pd.DataFrame) -> float:
        """价格加速度：最近几根K线的二阶差分"""
        returns = df['close'].pct_change()
        acceleration = returns.diff().abs()
        if len(acceleration) < 5:
            return 0.5
        # 取最后5根的平均加速度，归一化
        acc = acceleration.iloc[-5:].mean()
        # 使用 sigmoid 将加速度映射到 [0,1]
        return 1 / (1 + np.exp(-acc * 100))

    def _volatility_breakout(self, df: pd.DataFrame, period=14) -> float:
        """波动率突破：当前ATR与历史ATR的比值"""
        atr_vals = atr(df['high'], df['low'], df['close'], period)
        if len(atr_vals) < period:
            return 0.5
        current = atr_vals.iloc[-1]
        past_mean = atr_vals.iloc[-period:-1].mean()
        if past_mean == 0:
            return 0.5
        ratio = current / past_mean
        # 将 ratio 映射到 [0,1]，ratio>2 视为突破
        return min(1.0, ratio / 2)

    def _volume_anomaly(self, df: pd.DataFrame, period=20) -> float:
        """成交量异常：当前成交量与移动平均的比值"""
        vol = df['volume']
        if len(vol) < period:
            return 0.5
        vol_ma = vol.rolling(period).mean()
        ratio = vol.iloc[-1] / vol_ma.iloc[-1] if vol_ma.iloc[-1] != 0 else 1
        return min(1.0, ratio / 3)  # 3倍以上视为异常

    def _sentiment_extreme(self, indicators: dict) -> float:
        """情绪极端：从 RSI, 威廉指标等估算"""
        rsi = indicators.get('rsi', 50)
        # RSI 极端（>80 或 <20）
        rsi_extreme = abs(rsi - 50) / 50
        return min(1.0, rsi_extreme)

    def _liquidity_shock(self, df: pd.DataFrame, period=20) -> float:
        """流动性冲击：买卖价差异常扩大"""
        spread = (df['high'] - df['low']) / df['close']
        if len(spread) < period:
            return 0.5
        spread_ma = spread.rolling(period).mean()
        ratio = spread.iloc[-1] / spread_ma.iloc[-1] if spread_ma.iloc[-1] != 0 else 1
        return min(1.0, ratio / 2)
