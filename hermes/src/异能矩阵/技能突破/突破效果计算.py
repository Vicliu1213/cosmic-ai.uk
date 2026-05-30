"""
突破效果计算 - 我是进化分析师，计算突破后的技能提升
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

BREAKTHROUGH_EFFECTS = {
    1: {"name": "基础强化", "multiplier": 1.5, "desc": "技能效果提升50%"},
    2: {"name": "质变进化", "multiplier": 2.5, "desc": "技能效果提升150%，解锁新特性"},
    3: {"name": "终极觉醒", "multiplier": 5.0, "desc": "技能效果提升400%，获得觉醒技"},
}


class BreakthroughEffectCalculation:
    """
    视角：我是力量计算师
    职责：精确计算每次突破带来的技能效果提升
    """
    def __init__(self):
        self.custom_effects: Dict[str, List[str]] = {}
        logger.info("📈 突破效果计算系统已就绪")

    def calculate_effect(
        self, skill_name: str, breakthrough_count: int,
        base_power: float = 1.0, no_skill_mode: bool = False
    ) -> Dict:
        effect = BREAKTHROUGH_EFFECTS.get(breakthrough_count, {
            "name": f"第{breakthrough_count}次突破",
            "multiplier": 1.0 + breakthrough_count * 0.5,
            "desc": f"技能效果提升{breakthrough_count * 50}%",
        })

        # 无技突破模式：额外倍增
        if no_skill_mode:
            effect["multiplier"] *= 2.0
            effect["desc"] += " (无技突破 ×2)"

        new_power = base_power * effect["multiplier"]
        custom = self.custom_effects.get(skill_name, [])

        logger.info(
            f"✨ {skill_name} 突破效果: {effect['name']} | "
            f"{base_power:.1f} → {new_power:.1f} ({effect['multiplier']}x)"
        )
        return {
            "skill": skill_name,
            "breakthrough": breakthrough_count,
            "effect_name": effect["name"],
            "multiplier": effect["multiplier"],
            "new_power": new_power,
            "description": effect["desc"],
            "custom_effects": custom,
        }

    def register_custom_effect(self, skill_name: str, effect: str):
        if skill_name not in self.custom_effects:
            self.custom_effects[skill_name] = []
        self.custom_effects[skill_name].append(effect)
        logger.info(f"🔧 {skill_name} 自定义突破效果: {effect}")
