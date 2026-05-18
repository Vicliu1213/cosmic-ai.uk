"""
异能组合生成 - 我是创意大师，设计最强组合
"""
from typing import Dict, List
from datetime import datetime
import logging
from .. import AbilityConfig, AbilityType

logger = logging.getLogger(__name__)

class AbilityCombinationGeneration:
    """
    视角：我是战术创新者
    职责：探索并创造强大的异能组合
    """
    def __init__(self):
        self.saved_combos = {}
        self.combo_ratings = {}
        logger.info("🎨 异能组合生成器已就绪")

    def generate_combinations(self, available_abilities: List[AbilityConfig], combo_size: int = 3) -> List[Dict]:
        from itertools import combinations
        all_combos = list(combinations(available_abilities, combo_size))
        logger.info(f"🔮 生成 {len(all_combos)} 个{combo_size}异能组合")
        evaluated_combos = []
        for combo in all_combos[:10]:
            evaluation = self.evaluate_combination(list(combo))
            evaluated_combos.append(evaluation)
        evaluated_combos.sort(key=lambda x: x['total_score'], reverse=True)
        for i, combo in enumerate(evaluated_combos[:3], 1):
            logger.info(f"   #{i}: {combo['combo_name']} - 评分: {combo['total_score']:.1f}")
        return evaluated_combos

    def evaluate_combination(self, abilities: List[AbilityConfig]) -> Dict:
        combo_name = " + ".join([a.name for a in abilities])
        synergy_score = self._calculate_synergy(abilities)
        efficiency_score = self._calculate_efficiency(abilities)
        tactical_score = self._calculate_tactical_value(abilities)
        flexibility_score = self._calculate_flexibility(abilities)
        total_score = (synergy_score * 0.35 + efficiency_score * 0.25 + tactical_score * 0.25 + flexibility_score * 0.15)
        return {
            'combo_name': combo_name,
            'abilities': [a.ability_id for a in abilities],
            'synergy_score': synergy_score,
            'efficiency_score': efficiency_score,
            'tactical_score': tactical_score,
            'flexibility_score': flexibility_score,
            'total_score': total_score,
            'recommendation': self._generate_recommendation(total_score)
        }

    def _calculate_synergy(self, abilities: List[AbilityConfig]) -> float:
        score = 50.0
        all_tags = []
        for ability in abilities:
            all_tags.extend(ability.synergy_tags)
        unique_tags = set(all_tags)
        if len(all_tags) > len(unique_tags):
            score += (len(all_tags) - len(unique_tags)) * 10
        return min(100.0, score)

    def _calculate_efficiency(self, abilities: List[AbilityConfig]) -> float:
        avg_cost = sum(a.base_energy_cost for a in abilities) / len(abilities)
        if avg_cost < 30: return 90.0
        elif avg_cost < 50: return 70.0
        return 50.0

    def _calculate_tactical_value(self, abilities: List[AbilityConfig]) -> float:
        return len(set(a.ability_type for a in abilities)) * 25.0

    def _calculate_flexibility(self, abilities: List[AbilityConfig]) -> float:
        flexibility = 60.0
        if any(a.ability_type == AbilityType.OFFENSIVE for a in abilities): flexibility += 10
        if any(a.ability_type == AbilityType.DEFENSIVE for a in abilities): flexibility += 15
        if any(a.ability_type == AbilityType.SUPPORT for a in abilities): flexibility += 15
        return flexibility

    def _generate_recommendation(self, score: float) -> str:
        if score >= 80: return "⭐⭐⭐ 卓越组合 - 强烈推荐"
        elif score >= 65: return "⭐⭐ 优秀组合 - 值得使用"
        elif score >= 50: return "⭐ 可用组合 - 特定情况下有效"
        return "❌ 不推荐 - 考虑其他方案"

    def save_custom_sequence(self, combo_name: str, abilities: List[str], notes: str = ""):
        self.saved_combos[combo_name] = {
            'abilities': abilities, 'notes': notes,
            'created_at': datetime.now().isoformat(), 'usage_count': 0
        }
        logger.info(f"💾 组合已保存: {combo_name}，包含 {len(abilities)} 个异能")
