"""
协同效应分析 - 我是化学家，分析异能之间的反应
"""
from typing import Dict, List, Tuple
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class SynergyEffectAnalysis:
    """
    视角：我是协同效应研究员
    职责：深度分析多个异能间的化学反应
    """
    def __init__(self):
        self.synergy_matrix: Dict[str, Dict[str, float]] = {}
        logger.info("🔬 协同效应分析器已就绪")

    def analyze_pair(self, a: AbilityConfig, b: AbilityConfig) -> Dict:
        """分析两个异能的协同关系"""
        common_tags = set(a.synergy_tags) & set(b.synergy_tags)
        conflict_tags = (set(a.synergy_tags) & set(b.conflict_tags)) | (set(b.synergy_tags) & set(a.conflict_tags))
        synergy_score = len(common_tags) * 20.0 - len(conflict_tags) * 30.0
        return {
            'pair': f"{a.name} + {b.name}",
            'common_tags': list(common_tags),
            'conflict_tags': list(conflict_tags),
            'synergy_score': synergy_score,
            'verdict': '✅ 协同' if synergy_score > 0 else '❌ 冲突' if synergy_score < 0 else '⚪ 中性'
        }

    def analyze_group(self, abilities: List[AbilityConfig]) -> Dict:
        """分析一组异能的整体协同"""
        from itertools import combinations
        pairs = []
        total_score = 0.0
        for a, b in combinations(abilities, 2):
            result = self.analyze_pair(a, b)
            pairs.append(result)
            total_score += result['synergy_score']
        return {
            'group_size': len(abilities),
            'pair_analyses': pairs,
            'total_synergy': total_score,
            'avg_synergy': total_score / max(1, len(pairs))
        }

    def find_best_partner(self, target: AbilityConfig, candidates: List[AbilityConfig]) -> Tuple[AbilityConfig, Dict]:
        """为目标异能找出最佳搭档"""
        best = None
        best_result = None
        best_score = float('-inf')
        for candidate in candidates:
            if candidate.ability_id == target.ability_id:
                continue
            result = self.analyze_pair(target, candidate)
            if result['synergy_score'] > best_score:
                best_score = result['synergy_score']
                best = candidate
                best_result = result
        return best, best_result
