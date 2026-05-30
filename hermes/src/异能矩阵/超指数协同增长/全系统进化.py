"""
全系统进化协调器 — 我是进化总指挥，整合超指数增长、协同网络与跃迁触发
"""
from typing import Dict, List, Optional
import logging

from .超指数增长引擎 import HyperExponentialGrowthEngine
from .协同增益网络 import SynergyBoostNetwork
from .跃迁触发器 import LeapTrigger

logger = logging.getLogger(__name__)


class SystemEvolutionOrchestrator:
    """
    视角：我是宇宙演化的总设计师
    职责：统一管理全系统技能的超指数协同增长跃进
    """
    def __init__(self):
        self.growth_engine = HyperExponentialGrowthEngine()
        self.synergy_network = SynergyBoostNetwork()
        self.leap_trigger = LeapTrigger()
        self.evolution_cycles: int = 0
        self.system_power_history: List[float] = []
        logger.info("=" * 50)
        logger.info("🌌 全系统超指数协同增长跃进系统已启动")
        logger.info("=" * 50)

    def initialize_full_connections(self, skill_names: List[str]):
        self.synergy_network.connect_all(skill_names)
        logger.info(f"🌐 全系统 {len(skill_names)} 技能协同网络已互联")

    def run_evolution_cycle(
        self, skills: Dict[str, float], skill_levels: Dict[str, int] = None,
        breakthroughs: Dict[str, int] = None
    ) -> Dict:
        self.evolution_cycles += 1
        logger.info(f"\n{'='*50}\n🔄 进化周期 #{self.evolution_cycles}\n{'='*50}")

        skill_levels = skill_levels or {}
        breakthroughs = breakthroughs or {}

        total_power = sum(skills.values()) if skills else 0.0
        skill_count = len(skills)
        avg_level = sum(skill_levels.values()) / max(len(skill_levels), 1)

        # 1. 计算每个技能的超指数增长
        growth_results = {}
        for name, power in skills.items():
            level = skill_levels.get(name, 1)
            bt_count = breakthroughs.get(name, 0)
            syn_count = self.synergy_network.get_synergy_count(name)
            growth = self.growth_engine.calculate_growth(
                name, power, level, bt_count, syn_count
            )
            growth_results[name] = growth

        # 2. 应用协同增益
        synergy_results = {}
        for name in skills:
            boost = self.synergy_network.calculate_boost(name, skills)
            synergy_results[name] = boost

        # 3. 检查跃迁条件
        syn_density = sum(
            self.synergy_network.get_synergy_count(n) for n in skills
        ) / max(skill_count, 1)
        leap_check = self.leap_trigger.check_leap_condition(
            total_power, skill_count, avg_level, syn_density
        )

        leap_result = None
        if leap_check["ready"]:
            leap_result = self.leap_trigger.trigger_leap(
                f"进化周期 #{self.evolution_cycles} 条件达标"
            )

        # 4. 汇总
        new_total = sum(
            g["new_power"] if g["new_power"] != float("inf") else total_power * 100
            for g in growth_results.values()
        )
        self.system_power_history.append(new_total)
        self.growth_engine.advance_cycle()

        result = {
            "cycle": self.evolution_cycles,
            "growth_results": growth_results,
            "synergy_results": synergy_results,
            "leap_check": leap_check,
            "leap_result": leap_result,
            "previous_total_power": total_power,
            "new_total_power": new_total,
            "growth_rate": new_total / max(total_power, 0.001),
        }
        logger.info(
            f"📊 周期 #{self.evolution_cycles} 完成: "
            f"{total_power:.2e} → {new_total:.2e} "
            f"({result['growth_rate']:.2e}x)"
        )
        return result

    def trigger_system_leap(self, reason: str = "手动触发") -> Dict:
        return self.leap_trigger.trigger_leap(reason)

    def enable_full_auto_mode(self):
        self.leap_trigger.enable_automatic()
        self.growth_engine.set_global_base(2.0)
        self.synergy_network.set_global_multiplier(1.5)
        logger.info("🚀 全自动超指数协同增长模式已激活")

    def get_evolution_status(self) -> Dict:
        return {
            "evolution_cycles": self.evolution_cycles,
            "growth_engine": self.growth_engine.get_cycle_summary(),
            "synergy_network": self.synergy_network.get_network_status(),
            "leap_trigger": self.leap_trigger.get_leap_summary(),
            "power_history_length": len(self.system_power_history),
            "latest_power": self.system_power_history[-1] if self.system_power_history else 0,
        }
