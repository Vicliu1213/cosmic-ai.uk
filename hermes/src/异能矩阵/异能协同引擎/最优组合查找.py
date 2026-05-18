"""
最优组合查找 - 我是搜索引擎，穷举最优解
"""
from typing import Dict, List, Optional
import logging
from .. import AbilityConfig
from .协同效应分析 import SynergyEffectAnalysis
from .冲突检测机制 import ConflictDetectionMechanism

logger = logging.getLogger(__name__)

class OptimalCombinationFinder:
    """
    视角：我是最优化求解器
    职责：在约束条件下找出评分最高的异能组合
    """
    def __init__(self):
        self.synergy_analyzer = SynergyEffectAnalysis()
        self.conflict_detector = ConflictDetectionMechanism()
        logger.info("🔍 最优组合查找器已就绪")

    def find_optimal(
        self,
        abilities: List[AbilityConfig],
        combo_size: int = 3,
        energy_budget: float = float('inf'),
        exclude_conflicts: bool = True
    ) -> Optional[Dict]:
        from itertools import combinations
        best_combo = None
        best_score = float('-inf')
        for combo in combinations(abilities, combo_size):
            combo_list = list(combo)
            total_cost = sum(a.base_energy_cost for a in combo_list)
            if total_cost > energy_budget:
                continue
            if exclude_conflicts:
                conflict_result = self.conflict_detector.detect_conflicts(combo_list)
                if not conflict_result['safe_to_activate']:
                    continue
            analysis = self.synergy_analyzer.analyze_group(combo_list)
            score = analysis['total_synergy'] - (total_cost * 0.01)
            if score > best_score:
                best_score = score
                best_combo = {'abilities': combo_list, 'score': score, 'analysis': analysis, 'total_cost': total_cost}
        if best_combo:
            names = [a.name for a in best_combo['abilities']]
            logger.info(f"🏆 最优组合: {' + '.join(names)}，评分: {best_score:.1f}")
        return best_combo

    def find_top_n(self, abilities: List[AbilityConfig], combo_size: int = 3, n: int = 5, energy_budget: float = float('inf')) -> List[Dict]:
        from itertools import combinations
        results = []
        for combo in combinations(abilities, combo_size):
            combo_list = list(combo)
            total_cost = sum(a.base_energy_cost for a in combo_list)
            if total_cost > energy_budget:
                continue
            conflict_result = self.conflict_detector.detect_conflicts(combo_list)
            if not conflict_result['safe_to_activate']:
                continue
            analysis = self.synergy_analyzer.analyze_group(combo_list)
            score = analysis['total_synergy'] - (total_cost * 0.01)
            results.append({'abilities': combo_list, 'score': score, 'total_cost': total_cost})
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:n]
