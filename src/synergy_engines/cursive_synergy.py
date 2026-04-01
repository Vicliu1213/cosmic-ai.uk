#!/usr/bin/env python3
"""
遞歸協同引擎 - 超協同增強版
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StrategyState:
    """策略狀態"""
    name: str
    weight: float = 1.0
    performance: float = 0.0
    synergy_boost: float = 0.0
    activation_level: float = 0.0
    mutation_potential: float = 0.0
    quantum_phase: float = 0.0


class RecursiveSynergyEngine:
    """遞歸協同引擎"""

    def __init__(self, num_strategies: int = 10, golden_ratio: float = 1.618033988749895):
        self.num_strategies = num_strategies
        self.golden_ratio = golden_ratio
        self.strategies: Dict[str, StrategyState] = {}
        self.recursion_depth = 0
        self.max_recursion = 100
        self.synergy_history = []
        self.growth_history = []
        self.transcendence_count = 0
        self.synergy_matrix = np.eye(num_strategies) * 0.5

    def recursive_synergy_activation(self, input_vector: np.ndarray, depth: int = 0) -> Dict:
        """遞歸協同激活"""
        if depth >= self.max_recursion:
            return {'overflow': True}

        self.recursion_depth = depth

        # 前向傳播
        activations = {}
        for i, (name, strategy) in enumerate(self.strategies.items()):
            signal = input_vector[i] if i < len(input_vector) else 0.0
            strategy.activation_level = np.tanh(signal * strategy.weight)
            activations[name] = strategy.activation_level

        # 計算協同增益
        synergy_boost = self._calculate_synergy_boost(activations)

        # 檢測異變
        mutation_trigger = self._detect_mutation(activations, synergy_boost)

        # 遞歸調用
        if synergy_boost > 0.618:
            rec_input = np.array(list(activations.values())) * synergy_boost
            rec_res = self.recursive_synergy_activation(rec_input, depth + 1)
            if 'activations' in rec_res:
                for name in activations:
                    activations[name] += rec_res['activations'].get(name, 0)

        # 增長因子
        growth_factor = self._super_exponential_growth(depth, synergy_boost, mutation_trigger)

        self.growth_history.append({
            'depth': depth,
            'synergy_boost': synergy_boost,
            'growth_factor': growth_factor,
            'timestamp': datetime.now()
        })

        return {
            'activations': activations,
            'synergy_boost': synergy_boost,
            'growth_factor': growth_factor,
            'recursion_depth': depth,
            'mutation_trigger': mutation_trigger,
            'emergence_level': self._calculate_emergence_level(growth_factor)
        }

    def _calculate_synergy_boost(self, activations: Dict[str, float]) -> float:
        """計算協同增益"""
        total = 0.0
        count = 0
        strategies_list = list(self.strategies.values())

        for i, s1 in enumerate(strategies_list):
            for j, s2 in enumerate(strategies_list):
                if i != j:
                    synergy = (activations.get(s1.name, 0) *
                              activations.get(s2.name, 0) *
                              self.synergy_matrix[i, j] *
                              (1 + min(s1.performance, s2.performance)))
                    total += synergy
                    count += 1

        return total / max(count, 1)

    def _detect_mutation(self, activations: Dict[str, float], synergy: float) -> float:
        """檢測異變"""
        total = 0.0
        for strategy in self.strategies.values():
            impact = activations.get(strategy.name, 0) * 0.3 + synergy * 0.2
            strategy.mutation_potential = min(1.0, strategy.mutation_potential + impact)
            total += strategy.mutation_potential

        return total / len(self.strategies)

    def _super_exponential_growth(self, depth: int, synergy: float, mutation: float) -> float:
        """超指數增長"""
        exponent = self.golden_ratio * depth * synergy * (1 + mutation)
        return np.exp(np.exp(min(exponent, 100)))

    def _calculate_emergence_level(self, growth_factor: float) -> str:
        """計算湧現等級"""
        if growth_factor > 1e100:
            return "無限級"
        elif growth_factor > 1e50:
            return "超越級"
        elif growth_factor > 1e30:
            return "宇宙級"
        elif growth_factor > 1e20:
            return "星系級"
        elif growth_factor > 1e10:
            return "爆發級"
        elif growth_factor > 1e5:
            return "生長級"
        else:
            return "萌芽級"


class HyperSynergyTrigger:
    """超協同觸發器"""

    def __init__(self):
        self.thresholds = {
            'synergy': 0.8,
            'depth': 5,
            'mutation': 0.5,
            'quantum_phase': 0.9
        }

    def check_hyper_synergy(self, engine: RecursiveSynergyEngine) -> Dict:
        """檢查超協同條件"""
        n = len(engine.strategies)

        # 計算各項指標
        avg_activation = np.mean([s.activation_level for s in engine.strategies.values()]) if n > 0 else 0
        avg_synergy = np.mean(engine.synergy_matrix) if n > 0 else 0
        phase_consistency = self._calculate_phase_consistency(engine)

        # 超協同評分
        hyper_score = (
            n / 10 * 0.3 +
            avg_activation * 0.2 +
            avg_synergy * 0.3 +
            phase_consistency * 0.2
        )

        # 深度乘數
        depth_multiplier = 1 + engine.recursion_depth / 10

        # 增強倍數
        enhancement = hyper_score * depth_multiplier * (1 + engine.transcendence_count / 10)

        # 檢查是否觸發
        triggered = (
            n >= 5 and
            avg_synergy > self.thresholds['synergy'] and
            engine.recursion_depth >= self.thresholds['depth']
        )

        return {
            'hyper_synergy_triggered': triggered,
            'enhancement_factor': enhancement,
            'n_strategies': n,
            'avg_activation': avg_activation,
            'avg_synergy': avg_synergy,
            'phase_consistency': phase_consistency,
            'recursion_depth': engine.recursion_depth
        }

    def _calculate_phase_consistency(self, engine: RecursiveSynergyEngine) -> float:
        """計算相位一致性"""
        phases = [s.quantum_phase for s in engine.strategies.values()] if engine.strategies else []
        if not phases:
            return 0.0

        phase_variance = np.var(phases)
        return 1.0 / (1.0 + phase_variance)
