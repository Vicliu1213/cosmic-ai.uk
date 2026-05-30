"""
无技突破模式 - 我是规则破坏者，让旧技能无需任何代价即可突破
"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class NoSkillBreakthroughMode:
    """
    视角：我是规则之外的解放者
    职责：让所有旧技能可以无视任何条件直接突破，产生技能效果
    """
    def __init__(self):
        self.active: bool = False
        self.affected_skills: Dict[str, bool] = {}
        self.global_multiplier: float = 1.0
        logger.info("⚡ 无技突破模式已注册（待激活）")

    def enable(self):
        self.active = True
        logger.info("🚀 无技突破模式已激活 — 所有旧技能可无条件突破")

    def disable(self):
        self.active = False
        logger.info("🛑 无技突破模式已关闭")

    def apply_to_skill(self, skill_name: str) -> Dict:
        if not self.active:
            return {"success": False, "reason": "无技突破模式未激活"}

        self.affected_skills[skill_name] = True
        result = {
            "success": True,
            "skill": skill_name,
            "mode": "无技突破",
            "effect_multiplier": 1.5 * self.global_multiplier,
            "description": f"{skill_name} 已解放 — 无需技能点、无需材料、无需等待",
        }
        logger.info(f"⚡ {skill_name} → 无技突破生效 (倍率: {result['effect_multiplier']}x)")
        return result

    def apply_to_all_old_skills(self, skill_names: List[str]) -> List[Dict]:
        results = []
        for name in skill_names:
            results.append(self.apply_to_skill(name))
        logger.info(f"📦 批量无技突破完成: {len(results)} 個舊技能")
        return results

    def set_global_multiplier(self, multiplier: float):
        self.global_multiplier = multiplier
        logger.info(f"🔧 无技突破全局倍率调整为: {multiplier}x")

    def get_status(self) -> Dict:
        return {
            "active": self.active,
            "affected_skills": list(self.affected_skills.keys()),
            "skill_count": len(self.affected_skills),
            "global_multiplier": self.global_multiplier,
        }
