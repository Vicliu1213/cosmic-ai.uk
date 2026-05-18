"""
协同强度计算 - 我是量化分析师，计算协同效应的实际增益
"""
from typing import Dict, List
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class SynergyStrengthCalculation:
    """
    视角：我是增益量化器
    职责：将定性的协同关系转化为可量化的增益系数
    """
    def __init__(self):
        self.base_multiplier = 1.0
        logger.info("📐 协同强度计算器已就绪")

    def calculate_multiplier(self, abilities: List[AbilityConfig]) -> float:
        """计算一组异能激活时的整体协同倍率"""
        if len(abilities) < 2:
            return self.base_multiplier
        multiplier = self.base_multiplier
        all_tags = []
        for ability in abilities:
            all_tags.extend(ability.synergy_tags)
        unique_tags = set(all_tags)
        # 重复标签越多，协同越强
        overlap_ratio = 1 - (len(unique_tags) / len(all_tags)) if all_tags else 0
        multiplier += overlap_ratio * 0.5  # 最大额外加成 50%
        # 类型多样性加成
        type_count = len(set(a.ability_type for a in abilities))
        multiplier += (type_count - 1) * 0.05
        multiplier = min(2.0, multiplier)  # 上限 2x
        logger.info(f"💥 协同倍率: {multiplier:.2f}x（{len(abilities)} 个异能，{type_count} 种类型）")
        return multiplier

    def calculate_effective_output(self, base_output: float, abilities: List[AbilityConfig]) -> float:
        multiplier = self.calculate_multiplier(abilities)
        effective = base_output * multiplier
        logger.info(f"📊 有效输出: {base_output:.1f} × {multiplier:.2f} = {effective:.1f}")
        return effective

    def rank_synergy_pairs(self, abilities: List[AbilityConfig]) -> List[Dict]:
        from itertools import combinations
        pairs = []
        for a, b in combinations(abilities, 2):
            common = len(set(a.synergy_tags) & set(b.synergy_tags))
            conflict = len((set(a.synergy_tags) & set(b.conflict_tags)) | (set(b.synergy_tags) & set(a.conflict_tags)))
            score = common * 20 - conflict * 30
            pairs.append({'pair': f"{a.name}+{b.name}", 'score': score, 'common_tags': common, 'conflict_tags': conflict})
        return sorted(pairs, key=lambda x: x['score'], reverse=True)
