"""
能量分配算法 - 我是分配调度员，确保能量合理分配
"""
from typing import Dict, List
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class EnergyAllocationAlgorithm:
    """
    视角：我是能量经济学家
    职责：在多个异能之间合理分配有限能量
    """
    def __init__(self, total_energy: float = 1000.0):
        self.total_energy = total_energy
        self.allocation_map: Dict[str, float] = {}
        logger.info("📊 能量分配算法已初始化")

    def allocate(self, abilities: List[AbilityConfig], available: float) -> Dict[str, float]:
        """按优先级比例分配能量"""
        total_cost = sum(a.base_energy_cost for a in abilities)
        if total_cost == 0:
            return {}
        allocation = {}
        for ability in abilities:
            ratio = ability.base_energy_cost / total_cost
            allocation[ability.ability_id] = available * ratio
            logger.info(f"   分配 {ability.name}: {allocation[ability.ability_id]:.1f}")
        self.allocation_map.update(allocation)
        return allocation

    def get_allocation(self, ability_id: str) -> float:
        return self.allocation_map.get(ability_id, 0.0)

    def release_allocation(self, ability_id: str):
        if ability_id in self.allocation_map:
            del self.allocation_map[ability_id]
            logger.info(f"🔓 释放 {ability_id} 的能量分配")
