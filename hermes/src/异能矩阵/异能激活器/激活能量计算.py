"""
激活能量计算 - 我是精算师，计算每次激活的成本
"""
from typing import Dict, List
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class ActivationEnergyCalculation:
    """
    视角：我是能量会计
    职责：精确计算激活成本，优化能量使用
    """
    def __init__(self):
        self.efficiency_multiplier = 1.0
        self.cost_history = []
        logger.info("⚡ 激活能量计算系统已就绪")

    def calculate_activation_cost(self, ability: AbilityConfig, intensity: float = 1.0, duration: float = 1.0, modifiers: Dict = None) -> float:
        base_cost = ability.base_energy_cost
        intensity_factor = self._calculate_intensity_factor(intensity)
        duration_factor = self._calculate_duration_factor(duration)
        environmental_modifier = self._get_environmental_modifier(modifiers or {})
        efficiency = self.efficiency_multiplier
        total_cost = base_cost * intensity_factor * duration_factor * environmental_modifier / efficiency
        logger.info(f"💰 {ability.name} 激活成本: {total_cost:.2f} 能量点")
        return total_cost

    def _calculate_intensity_factor(self, intensity: float) -> float:
        return intensity ** 1.5

    def _calculate_duration_factor(self, duration: float) -> float:
        return max(0.5, duration)

    def _get_environmental_modifier(self, modifiers: Dict) -> float:
        base_modifier = 1.0
        if modifiers.get('favorable_terrain', False):
            base_modifier *= 0.85
        if modifiers.get('hostile_environment', False):
            base_modifier *= 1.25
        return base_modifier

    def optimize_energy_usage(self, abilities: List[AbilityConfig]) -> Dict:
        report = {'total_cost': 0, 'recommendations': [], 'savings_potential': 0}
        for ability in abilities:
            cost = self.calculate_activation_cost(ability)
            report['total_cost'] += cost
            if cost > ability.base_energy_cost * 1.2:
                report['recommendations'].append(f"{ability.name}: 考虑降低强度或寻找有利环境")
        return report
