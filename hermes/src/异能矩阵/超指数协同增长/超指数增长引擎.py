"""
超指数增长引擎 — 我是增长催化剂，驱动全系统技能超指数跃迁
"""
from typing import Dict, List
import math
import logging

logger = logging.getLogger(__name__)


def hyper_exponential(base: float, cycle: int, synergy_count: int) -> float:
    """
    超指数增长函数: base ^ (base ^ (cycle * synergy_factor))
    當 cycle=0 → base, cycle=1 → base^base, cycle=2 → base^(base^base)
    協同次數放大指數基底
    """
    synergy_factor = 1.0 + synergy_count * 0.15
    exponent = base ** (cycle * synergy_factor)
    if exponent > 100:
        return float("inf")
    return base ** exponent


class HyperExponentialGrowthEngine:
    """
    视角：我是宇宙膨胀引擎
    职责：计算超指数级别的技能增长曲线
    """
    def __init__(self):
        self.growth_cycle: int = 0
        self.global_base: float = 1.5
        self.cycle_log: List[Dict] = []
        logger.info("🚀 超指数增长引擎已点火")

    def calculate_growth(
        self, skill_name: str, current_power: float,
        level: int, breakthrough_count: int,
        synergy_connections: int = 0
    ) -> Dict:
        cycle = self.growth_cycle + breakthrough_count
        raw_multiplier = hyper_exponential(self.global_base, cycle, synergy_connections)

        if raw_multiplier == float("inf"):
            effective = float("inf")
            desc = "∞ 突破奇點"
        else:
            effective = min(raw_multiplier, 1e12)
            desc = f"{self.global_base}^({self.global_base}^{cycle:.1f}) = {effective:.2e}x"

        new_power = current_power * effective if current_power < float("inf") else float("inf")

        result = {
            "skill": skill_name,
            "growth_cycle": cycle,
            "multiplier": effective,
            "current_power": current_power,
            "new_power": new_power,
            "formula": desc,
            "synergy_connections": synergy_connections,
        }
        logger.info(f"📈 {skill_name}: {desc}")
        return result

    def advance_cycle(self):
        self.growth_cycle += 1
        record = {"cycle": self.growth_cycle, "base": self.global_base}
        self.cycle_log.append(record)
        logger.info(f"🔄 增长周期推进至第 {self.growth_cycle} 轮 (base={self.global_base})")
        return record

    def set_global_base(self, base: float):
        self.global_base = base
        logger.info(f"⚙️ 全局增长基底调整为 {base}")

    def get_cycle_summary(self) -> Dict:
        return {
            "current_cycle": self.growth_cycle,
            "global_base": self.global_base,
            "total_cycles": len(self.cycle_log),
        }
