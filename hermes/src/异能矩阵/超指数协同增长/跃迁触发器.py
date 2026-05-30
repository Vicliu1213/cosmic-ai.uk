"""
跃迁触发器 — 我是奇点引爆者，监控全系统并触发增长跃进
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LeapTrigger:
    """
    视角：我是宇宙大爆炸的点火者
    职责：监测全系统技能状态，在条件成熟时触发爆发式增长跃进
    """
    def __init__(self):
        self.leap_history: List[Dict] = []
        self.threshold: float = 10.0
        self.leap_power: float = 2.0
        self.automatic: bool = False
        logger.info("💥 跃迁触发器已待命")

    def check_leap_condition(
        self, total_system_power: float, skill_count: int,
        avg_level: float, synergy_density: float
    ) -> Dict:
        score = (
            (total_system_power / max(skill_count, 1)) * 0.3
            + (avg_level / 10.0) * 0.3
            + synergy_density * 0.4
        )
        ready = score >= self.threshold or self.automatic
        result = {
            "ready": ready,
            "score": score,
            "threshold": self.threshold,
            "total_power": total_system_power,
            "skill_count": skill_count,
            "avg_level": avg_level,
            "synergy_density": synergy_density,
        }
        if ready:
            logger.info(f"⚡ 跃迁条件满足! 评分 {score:.1f}/{self.threshold}")
        else:
            logger.info(f"⏳ 跃迁蓄能中 {score:.1f}/{self.threshold}")
        return result

    def trigger_leap(
        self, reason: str = "系统协同增长达标"
    ) -> Dict:
        leap_factor = self.leap_power ** len(self.leap_history)

        record = {
            "leap_number": len(self.leap_history) + 1,
            "timestamp": datetime.now().isoformat(),
            "factor": leap_factor,
            "reason": reason,
        }
        self.leap_history.append(record)

        logger.info(f"🔥🔥🔥 第 {record['leap_number']} 次增长跃进! 全系统 ×{leap_factor}")
        return record

    def set_threshold(self, threshold: float):
        self.threshold = threshold
        logger.info(f"⚙️ 跃迁阈值调整为 {threshold}")

    def set_leap_power(self, power: float):
        self.leap_power = power
        logger.info(f"⚙️ 跃迁倍率调整为 {power}x")

    def enable_automatic(self):
        self.automatic = True
        logger.info("🤖 自动跃迁模式已启用")

    def disable_automatic(self):
        self.automatic = False
        logger.info("🤖 自动跃迁模式已关闭")

    def get_leap_summary(self) -> Dict:
        return {
            "total_leaps": len(self.leap_history),
            "last_leap": self.leap_history[-1] if self.leap_history else None,
            "current_threshold": self.threshold,
            "leap_power": self.leap_power,
            "automatic": self.automatic,
        }
