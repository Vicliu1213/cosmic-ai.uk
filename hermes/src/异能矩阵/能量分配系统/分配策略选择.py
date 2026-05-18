"""
分配策略选择 - 我是战略顾问，选择最优分配方案
"""
from typing import Dict, List
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class AllocationStrategySelector:
    """
    视角：我是战略决策者
    职责：根据场景选择最合适的能量分配策略
    """
    STRATEGIES = ['conservative', 'balanced', 'aggressive', 'emergency']

    def __init__(self, default_strategy: str = 'balanced'):
        self.current_strategy = default_strategy
        logger.info(f"🎯 分配策略选择器已就绪，默认策略: {default_strategy}")

    def select_strategy(self, energy_level_pct: float, threat_level: str = 'normal') -> str:
        """根据能量水位和威胁等级自动选择策略"""
        if energy_level_pct < 20:
            strategy = 'emergency'
        elif energy_level_pct < 40:
            strategy = 'conservative'
        elif threat_level == 'high':
            strategy = 'aggressive'
        else:
            strategy = 'balanced'
        self.current_strategy = strategy
        logger.info(f"🔀 选择策略: {strategy}（能量: {energy_level_pct:.0f}%，威胁: {threat_level}）")
        return strategy

    def apply_strategy(self, abilities: List[AbilityConfig], available: float) -> Dict[str, float]:
        """按当前策略分配能量"""
        allocation = {}
        if self.current_strategy == 'emergency':
            # 只给最低成本的异能
            sorted_a = sorted(abilities, key=lambda a: a.base_energy_cost)
            budget = available * 0.5
            for ability in sorted_a:
                if budget >= ability.base_energy_cost:
                    allocation[ability.ability_id] = ability.base_energy_cost
                    budget -= ability.base_energy_cost
        elif self.current_strategy == 'aggressive':
            for ability in abilities:
                allocation[ability.ability_id] = ability.base_energy_cost * 1.2
        else:
            for ability in abilities:
                allocation[ability.ability_id] = ability.base_energy_cost
        return allocation
