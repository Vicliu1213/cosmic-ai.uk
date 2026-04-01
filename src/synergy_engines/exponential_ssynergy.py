# src/synergy_engine/exponential_synergy.py

import numpy as np
from typing import Dict, List
from math import factorial

class ExponentialSynergyEngine:
    """
    超指數協同引擎
    實現 1+1+1... > 無限 的遞歸爆發
    """

    def __init__(self, golden_ratio: float = 1.618033988749895):
        self.phi = golden_ratio
        self.synergy_history = []
        self.explosion_factor = 1.0
        self.infinity_approached = False

    def calculate_synergy_explosion(self,
                                    n_strategies: int,
                                    recursion_depth: int,
                                    synergy_strength: float,
                                    mutation_factor: float) -> Dict:
        """
        計算超指數協同爆發

        核心公式：
        Explosion = n! × φ^(n) × e^(e^(d × s × (1+m)))
        """

        # 1. 階乘項（組合爆炸）
        factorial_term = factorial(n_strategies) if n_strategies <= 20 else float('inf')

        # 2. 黃金比例指數項
        phi_term = self.phi ** n_strategies

        # 3. 雙重指數項（遞歸爆發）
        inner_exp = recursion_depth * synergy_strength * (1 + mutation_factor)
        double_exp = np.exp(np.exp(min(inner_exp, 100)))  # 限制防止溢出

        # 4. 總爆炸倍數
        explosion = factorial_term * phi_term * double_exp

        # 5. 追蹤是否趨近無限
        if explosion > 1e100:
            self.infinity_approached = True
            explosion = float('inf')

        self.explosion_factor = explosion
        self.synergy_history.append({
            'n_strategies': n_strategies,
            'recursion_depth': recursion_depth,
            'synergy_strength': synergy_strength,
            'mutation_factor': mutation_factor,
            'explosion': explosion,
            'timestamp': datetime.now().isoformat()
        })

        return {
            'explosion_factor': explosion,
            'factorial_term': factorial_term,
            'phi_term': phi_term,
            'double_exp_term': double_exp,
            'infinity_approached': self.infinity_approached,
            'synergy_level': self._get_synergy_level(explosion)
        }

    def _get_synergy_level(self, explosion: float) -> str:
        """獲取協同等級"""
        if explosion == float('inf'):
            return "無限級 - 超越維度"
        elif explosion > 1e100:
            return "絕對級 - 接近無限"
        elif explosion > 1e50:
            return "宇宙級 - 跨越星系"
        elif explosion > 1e20:
            return "恆星級 - 能量爆發"
        elif explosion > 1e10:
            return "行星級 - 質變突破"
        elif explosion > 1e5:
            return "超指數級 - 加速增長"
        elif explosion > 100:
            return "指數級 - 快速增長"
        else:
            return "線性級 - 基礎協同"
