# src/synergy_engine/adaptive_depth.py

class AdaptiveRecursionDepth:
    """
    自適應遞歸深度管理器
    根據協同效應動態調整遞歸深度
    """

    def __init__(self, max_depth: int = 20):
        self.max_depth = max_depth
        self.current_depth = 1
        self.performance_history = []

    def adjust_depth(self, synergy_gain: float) -> int:
        """
        根據協同增益調整遞歸深度

        當協同增益超過閾值時自動加深遞歸
        """
        # 記錄性能
        self.performance_history.append(synergy_gain)

        # 計算近期平均增益
        if len(self.performance_history) > 10:
            recent_avg = np.mean(self.performance_history[-10:])
        else:
            recent_avg = synergy_gain

        # 動態調整規則
        if recent_avg > 0.9:
            # 超強協同，深度 +3
            self.current_depth = min(self.max_depth, self.current_depth + 3)
        elif recent_avg > 0.7:
            # 強協同，深度 +2
            self.current_depth = min(self.max_depth, self.current_depth + 2)
        elif recent_avg > 0.5:
            # 中等協同，深度 +1
            self.current_depth = min(self.max_depth, self.current_depth + 1)
        elif recent_avg < 0.3:
            # 弱協同，深度 -1（避免浪費資源）
            self.current_depth = max(1, self.current_depth - 1)

        return self.current_depth

    def get_optimal_depth(self, n_strategies: int) -> int:
        """
        根據策略數量計算最優遞歸深度

        公式：optimal_depth = log₂(n_strategies) × φ
        """
        optimal = int(np.log2(n_strategies) * 1.618) if n_strategies > 1 else 1
        return min(self.max_depth, max(1, optimal))
