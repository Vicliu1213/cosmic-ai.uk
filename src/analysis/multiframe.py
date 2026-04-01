"""
多时间框架分析：综合不同周期（1h, 4h, 1d）的信号。
"""
import pandas as pd
import numpy as np
from .indicators import rsi, macd, sma


class MultiFrameAnalyzer:
    def __init__(self):
        self.timeframes = ['1h', '4h', '1d']
        self.weights = {'1h': 0.2, '4h': 0.3, '1d': 0.5}

    def analyze(self, data_dict: dict) -> dict:
        """data_dict: {'1h': df, '4h': df, '1d': df}"""
        results = {}
        composite_score = 0.0

        for tf, df in data_dict.items():
            if df.empty:
                continue
            # 计算趋势强度（简单示例）
            close = df['close']
            sma20 = sma(close, 20)
            sma50 = sma(close, 50)
            trend = 1 if sma20.iloc[-1] > sma50.iloc[-1] else -1

            # 动量
            rsi_val = rsi(close, 14).iloc[-1]
            momentum = 1 if rsi_val > 50 else -1

            # 价格位置
            price = close.iloc[-1]
            sma20_val = sma20.iloc[-1]
            price_ratio = (price - sma20_val) / sma20_val

            # 综合得分
            score = trend * 0.4 + momentum * 0.3 + np.tanh(price_ratio) * 0.3

            results[tf] = {
                'price': price,
                'trend': trend,
                'momentum': momentum,
                'score': score
            }
            composite_score += score * self.weights.get(tf, 1/len(self.timeframes))

        return {
            'timeframe_analysis': results,
            'composite_score': composite_score,
            'market_regime': self._classify_regime(composite_score)
        }

    def _classify_regime(self, score: float) -> str:
        """根据综合得分划分市场状态"""
        if score > 0.5:
            return "BULL_TREND"
        elif score < -0.5:
            return "BEAR_TREND"
        elif abs(score) < 0.2:
            return "RANGING"
        else:
            return "TRANSITION"
