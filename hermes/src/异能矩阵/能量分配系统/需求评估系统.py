"""
需求评估系统 - 我是需求分析师，预测能量需求
"""
from typing import Dict, List
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class DemandAssessmentSystem:
    """
    视角：我是预测专家
    职责：评估当前和未来的能量需求，避免能量危机
    """
    def __init__(self):
        self.demand_history: List[float] = []
        logger.info("📈 需求评估系统已就绪")

    def assess_immediate(self, abilities: List[AbilityConfig]) -> float:
        """立即执行这些异能的总能量需求"""
        total = sum(a.base_energy_cost for a in abilities)
        logger.info(f"📊 立即需求评估: {total:.1f} 能量（{len(abilities)} 个异能）")
        return total

    def assess_reserve_requirement(self, abilities: List[AbilityConfig], safety_factor: float = 1.3) -> float:
        """加上安全余量后的推荐储备量"""
        immediate = self.assess_immediate(abilities)
        reserve = immediate * safety_factor
        logger.info(f"🛡️ 推荐储备: {reserve:.1f}（安全系数: {safety_factor}x）")
        return reserve

    def can_afford(self, abilities: List[AbilityConfig], available_energy: float) -> Dict:
        required = self.assess_immediate(abilities)
        affordable = []
        unaffordable = []
        running_energy = available_energy
        for ability in sorted(abilities, key=lambda a: a.base_energy_cost):
            if running_energy >= ability.base_energy_cost:
                affordable.append(ability.ability_id)
                running_energy -= ability.base_energy_cost
            else:
                unaffordable.append(ability.ability_id)
        return {
            'required': required,
            'available': available_energy,
            'affordable': affordable,
            'unaffordable': unaffordable,
            'deficit': max(0.0, required - available_energy)
        }
