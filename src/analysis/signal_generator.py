"""
综合森林分析、奇点检测、多时间框架分析，生成最终交易信号。
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum


class SignalStrength(Enum):
    VERY_WEAK = 0.2
    WEAK = 0.4
    NEUTRAL = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0


@dataclass
class TradingSignal:
    symbol: str
    signal_type: str  # BUY or SELL
    strength: SignalStrength
    confidence: float
    price: float
    timestamp: pd.Timestamp
    target_prices: dict
    stop_loss: float
    risk_reward_ratio: float
    recommended_position: float
    market_regime: str
    singularity_prob: float
    forest_confidence: float


class SignalGenerator:
    def __init__(self, symbol: str = "BTC/USDT"):
        self.symbol = symbol

    def generate(self, multi_frame_result: dict, forest_result: dict, singularity_prob: float, price: float) -> list:
        """生成信号列表"""
        signals = []

        # 综合得分
        composite = multi_frame_result['composite_score']
        forest_dir = forest_result['direction']
        forest_conf = forest_result['confidence']

        # 加权置信度
        combined_conf = (abs(composite) * 0.4 + forest_conf * 0.6) if forest_dir != 0 else abs(composite)

        # 确定信号方向
        if composite > 0.3 and forest_dir == 1:
            signal_type = "BUY"
            direction = 1
        elif composite < -0.3 and forest_dir == -1:
            signal_type = "SELL"
            direction = -1
        else:
            return signals  # 无信号

        # 信号强度
        if combined_conf > 0.8:
            strength = SignalStrength.VERY_STRONG
        elif combined_conf > 0.7:
            strength = SignalStrength.STRONG
        elif combined_conf > 0.6:
            strength = SignalStrength.NEUTRAL
        else:
            strength = SignalStrength.WEAK

        # 简单目标价和止损（示例）
        if signal_type == "BUY":
            target1 = price * 1.03
            target2 = price * 1.05
            stop_loss = price * 0.98
        else:
            target1 = price * 0.97
            target2 = price * 0.95
            stop_loss = price * 1.02

        risk = abs(price - stop_loss)
        reward = abs(target1 - price)
        rr_ratio = reward / risk if risk > 0 else 0

        # 建议仓位（简化）
        position = 0.1 * combined_conf  # 10% 基础仓位

        # 如果奇点概率高，降低仓位
        if singularity_prob > 0.7:
            position *= (1 - singularity_prob)

        signal = TradingSignal(
            symbol=self.symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=combined_conf,
            price=price,
            timestamp=pd.Timestamp.now(),
            target_prices={'tp1': target1, 'tp2': target2},
            stop_loss=stop_loss,
            risk_reward_ratio=rr_ratio,
            recommended_position=position,
            market_regime=multi_frame_result['market_regime'],
            singularity_prob=singularity_prob,
            forest_confidence=forest_conf
        )
        signals.append(signal)
        return signals
