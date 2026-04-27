import numpy as np
from core.omega_core import OmegaSkill

class OrderFlowHunt(OmegaSkill):
    def __init__(self, memory_matrix):
        super().__init__()
        self.memory = memory_matrix
        self.imbalance_history = []

    def compute_imbalance(self, buy_vol, sell_vol):
        total = buy_vol + sell_vol
        min_total = max(total, 0.5 * (buy_vol + sell_vol + 1e-8))
        return (buy_vol - sell_vol) / min_total

    def dynamic_threshold(self):
        if len(self.imbalance_history) < 100:
            return 0.4
        std = np.std(self.imbalance_history[-100:])
        return max(0.4, 0.5 * std + 0.3)

    def evaluate(self, symbol, buy_vol, sell_vol, price_ticks, spread):
        imb = self.compute_imbalance(buy_vol, sell_vol)
        self.imbalance_history.append(imb)
        threshold = self.dynamic_threshold()
        price_move = price_ticks[-1] - price_ticks[-2]
        min_move = 0.5 * spread

        if imb > threshold and price_move > min_move:
            # 调用神性核心计算交易计划
            from core.omega_core import OmegaCore
            core = OmegaCore.get_instance()
            plan = core.calculate_trade_setup(price_ticks[-1], atr=core.get_atr(symbol), adx=core.get_adx(symbol))
            return {
                'symbol': symbol,
                'price': price_ticks[-1],
                'confidence': min(1.0, imb / 0.8),
                **plan
            }
        return None