"""
能力优先级设置 - 我是优先级裁判，决定谁先谁后
"""
from typing import Dict, List
import logging
from .. import AbilityConfig, AbilityType

logger = logging.getLogger(__name__)

PRIORITY_TABLE = {
    AbilityType.DEFENSIVE: 10,
    AbilityType.SUPPORT: 8,
    AbilityType.OFFENSIVE: 6,
    AbilityType.HYBRID: 5,
    AbilityType.UTILITY: 3,
}

class AbilityPrioritySettings:
    """
    视角：我是战场指挥官
    职责：根据场景动态设定异能优先级
    """
    def __init__(self):
        self.custom_priorities: Dict[str, int] = {}
        logger.info("🏅 能力优先级系统已就绪")

    def get_priority(self, ability: AbilityConfig) -> int:
        if ability.ability_id in self.custom_priorities:
            return self.custom_priorities[ability.ability_id]
        return PRIORITY_TABLE.get(ability.ability_type, 0)

    def set_custom_priority(self, ability_id: str, priority: int):
        self.custom_priorities[ability_id] = priority
        logger.info(f"⚙️ 自定义优先级: {ability_id} → {priority}")

    def sort_by_priority(self, abilities: List[AbilityConfig]) -> List[AbilityConfig]:
        return sorted(abilities, key=lambda a: self.get_priority(a), reverse=True)
