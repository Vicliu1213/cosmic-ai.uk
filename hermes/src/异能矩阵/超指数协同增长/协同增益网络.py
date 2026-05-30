"""
协同增益网络 — 我是神经中枢，连接所有技能形成协同放大网络
"""
from typing import Dict, List, Set, Tuple
import math
import logging

logger = logging.getLogger(__name__)


class SynergyBoostNetwork:
    """
    视角：我是互联智慧的编织者
    职责：构建技能间的协同增益网络，每个技能放大其他技能
    """
    def __init__(self):
        self.connections: Dict[str, Set[str]] = {}
        self.boost_matrix: Dict[Tuple[str, str], float] = {}
        self.global_synergy_multiplier: float = 1.0
        logger.info("🔗 协同增益网络已建立")

    def connect(self, skill_a: str, skill_b: str, boost: float = 1.2):
        if skill_a not in self.connections:
            self.connections[skill_a] = set()
        if skill_b not in self.connections:
            self.connections[skill_b] = set()
        self.connections[skill_a].add(skill_b)
        self.connections[skill_b].add(skill_a)
        self.boost_matrix[(skill_a, skill_b)] = boost
        self.boost_matrix[(skill_b, skill_a)] = boost
        logger.info(f"🔗 {skill_a} ↔ {skill_b} 协同连接建立 (增益: {boost}x)")

    def connect_all(self, skill_names: List[str], base_boost: float = 1.15):
        for i in range(len(skill_names)):
            for j in range(i + 1, len(skill_names)):
                self.connect(skill_names[i], skill_names[j], base_boost)
        logger.info(f"🌐 全连接网络: {len(skill_names)} 个技能全互联 (增益: {base_boost}x)")

    def get_synergy_count(self, skill_name: str) -> int:
        return len(self.connections.get(skill_name, set()))

    def calculate_boost(
        self, skill_name: str, all_skills: Dict[str, float]
    ) -> float:
        connected = self.connections.get(skill_name, set())
        if not connected:
            return 1.0

        total_boost = 1.0
        for neighbor in connected:
            neighbor_power = all_skills.get(neighbor, 1.0)
            edge_boost = self.boost_matrix.get((skill_name, neighbor), 1.15)
            total_boost *= edge_boost ** math.log2(max(neighbor_power, 1.0) + 1)

        total_boost *= self.global_synergy_multiplier
        logger.info(
            f"🔄 {skill_name} 接收 {len(connected)} 个协同连接 → 协同倍率: {total_boost:.4f}x"
        )
        return total_boost

    def set_global_multiplier(self, multiplier: float):
        self.global_synergy_multiplier = multiplier
        logger.info(f"🌍 全局协同倍率调整为 {multiplier}x")

    def get_network_status(self) -> Dict:
        return {
            "total_skills": len(self.connections),
            "total_edges": sum(len(v) for v in self.connections.values()) // 2,
            "global_multiplier": self.global_synergy_multiplier,
        }

    def get_connections(self, skill_name: str) -> List[str]:
        return list(self.connections.get(skill_name, set()))
