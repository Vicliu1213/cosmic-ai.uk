"""
突破序列管理 - 我是进化规划师，安排突破顺序与路径
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BreakthroughSequenceManager:
    """
    视角：我是进化路线规划师
    职责：管理技能突破的顺序、路径与历史
    """
    def __init__(self):
        self.breakthrough_history: Dict[str, List[Dict]] = {}
        self.pending_breakthroughs: List[str] = []
        self.sequence_cache: Dict[str, List[str]] = {}
        logger.info("📋 突破序列管理系统已上线")

    def plan_sequence(
        self, skills: List[str], strategy: str = "balanced"
    ) -> List[str]:
        logger.info(f"🔄 规划 {len(skills)} 个技能的突破顺序，策略: {strategy}")
        if strategy == "priority_first":
            return skills
        elif strategy == "weak_first":
            return list(reversed(skills))
        return skills

    def record_breakthrough(
        self, skill_name: str, count: int, effects: Dict
    ):
        if skill_name not in self.breakthrough_history:
            self.breakthrough_history[skill_name] = []
        record = {
            "count": count,
            "timestamp": datetime.now().isoformat(),
            "effects": effects,
        }
        self.breakthrough_history[skill_name].append(record)
        if skill_name in self.pending_breakthroughs:
            self.pending_breakthroughs.remove(skill_name)
        logger.info(f"📝 {skill_name} 第{count}次突破已记录")

    def get_history(self, skill_name: str) -> List[Dict]:
        return self.breakthrough_history.get(skill_name, [])

    def get_pending(self) -> List[str]:
        return self.pending_breakthroughs

    def add_pending(self, skill_name: str):
        if skill_name not in self.pending_breakthroughs:
            self.pending_breakthroughs.append(skill_name)
            logger.info(f"⏳ {skill_name} 已加入突破等待队列")
