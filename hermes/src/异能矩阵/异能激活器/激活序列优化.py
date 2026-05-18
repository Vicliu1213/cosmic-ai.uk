"""
激活序列优化 - 我是编舞者，安排最优的激活顺序
"""
from typing import Dict, List
import logging
from .. import AbilityConfig, AbilityType

logger = logging.getLogger(__name__)

class ActivationSequenceOptimization:
    """
    视角：我是战术规划师
    职责：优化多个异能的激活顺序，最大化效率
    """
    def __init__(self):
        self.sequence_cache = {}
        logger.info("🎯 激活序列优化器已上线")

    def optimize_sequence(self, abilities: List[AbilityConfig], objective: str = 'efficiency') -> List[str]:
        logger.info(f"🔄 开始优化 {len(abilities)} 个异能的激活序列，目标: {objective}")
        if objective == 'efficiency':
            return self._optimize_for_efficiency(abilities)
        elif objective == 'speed':
            return self._optimize_for_speed(abilities)
        elif objective == 'power':
            return self._optimize_for_power(abilities)
        return [a.ability_id for a in abilities]

    def _optimize_for_efficiency(self, abilities: List[AbilityConfig]) -> List[str]:
        sorted_abilities = sorted(abilities, key=lambda a: a.base_energy_cost)
        logger.info("   策略: 低成本优先 → 保持能量池健康")
        return [a.ability_id for a in sorted_abilities]

    def _optimize_for_speed(self, abilities: List[AbilityConfig]) -> List[str]:
        sorted_abilities = sorted(abilities, key=lambda a: a.base_cooldown)
        logger.info("   策略: 快速异能优先 → 形成连续攻势")
        return [a.ability_id for a in sorted_abilities]

    def _optimize_for_power(self, abilities: List[AbilityConfig]) -> List[str]:
        type_priority = {
            AbilityType.OFFENSIVE: 4, AbilityType.HYBRID: 3,
            AbilityType.SUPPORT: 2, AbilityType.DEFENSIVE: 1, AbilityType.UTILITY: 0
        }
        sorted_abilities = sorted(abilities, key=lambda a: type_priority.get(a.ability_type, 0), reverse=True)
        logger.info("   策略: 攻击优先 → 压制性输出")
        return [a.ability_id for a in sorted_abilities]

    def parallel_activation_planning(self, abilities: List[AbilityConfig]) -> Dict[str, List[str]]:
        plan = {'wave_1': [], 'wave_2': [], 'wave_3': []}
        for ability in abilities:
            if ability.ability_type == AbilityType.DEFENSIVE:
                plan['wave_1'].append(ability.ability_id)
            elif ability.ability_type == AbilityType.SUPPORT:
                plan['wave_2'].append(ability.ability_id)
            else:
                plan['wave_3'].append(ability.ability_id)
        return plan
