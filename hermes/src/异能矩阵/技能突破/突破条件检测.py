"""
突破条件检测 - 我是守门人，判断技能是否满足突破条件
"""
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class BreakthroughConditionDetection:
    """
    视角：我是严格的资格审核官
    职责：检查技能是否满足突破所需的全部条件
    """
    def __init__(self):
        self.override_rules: Dict[str, bool] = {}
        logger.info("🔓 突破条件检测系统已就绪")

    def check_conditions(
        self, skill_name: str, current_level: int, max_level: int,
        breakthrough_count: int, extra: Dict = None
    ) -> Tuple[bool, List[str]]:
        failed = []

        # 条件1: 等级已满才能突破
        if current_level < max_level and not self.override_rules.get("bypass_level_check"):
            failed.append(f"等级不足 ({current_level}/{max_level})")

        # 条件2: 突破次数限制检查
        if breakthrough_count >= 3 and not self.override_rules.get("unlimited_breakthrough"):
            failed.append("已达最大突破次数 (3/3)")

        # 条件3: 无技突破模式检查
        if self.override_rules.get("no_skill_mode"):
            logger.info(f"⚡ {skill_name} 触发无技突破 — 跳过所有条件")
            return True, []

        passed = len(failed) == 0
        if passed:
            logger.info(f"✅ {skill_name} 通过突破条件检查")
        else:
            logger.warning(f"❌ {skill_name} 未通过: {', '.join(failed)}")
        return passed, failed

    def set_override(self, rule: str, value: bool):
        self.override_rules[rule] = value
        logger.info(f"⚙️ 突破规则覆盖: {rule} = {value}")

    def enable_no_skill_mode(self):
        self.set_override("no_skill_mode", True)
        self.set_override("bypass_level_check", True)
        self.set_override("unlimited_breakthrough", True)
        logger.info("🚀 无技突破模式已启用 — 所有技能可无条件突破")
