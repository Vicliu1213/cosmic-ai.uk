"""
能力持续时间控制 - 我是计时器，掌控每个异能的生命周期
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AbilityDurationControl:
    """
    视角：我是异能的生命管理者
    职责：精确控制每个异能的持续时间
    """
    def __init__(self):
        self.active_durations: Dict[str, Dict] = {}
        logger.info("⏱️ 能力持续时间控制器已启动")

    def start(self, ability_id: str, duration_seconds: float):
        end_time = datetime.now() + timedelta(seconds=duration_seconds)
        self.active_durations[ability_id] = {
            'start': datetime.now(),
            'end': end_time,
            'duration': duration_seconds
        }
        logger.info(f"▶️ {ability_id} 持续时间开始: {duration_seconds}秒")

    def is_active(self, ability_id: str) -> bool:
        if ability_id not in self.active_durations:
            return False
        return datetime.now() < self.active_durations[ability_id]['end']

    def remaining(self, ability_id: str) -> float:
        if not self.is_active(ability_id):
            return 0.0
        return (self.active_durations[ability_id]['end'] - datetime.now()).total_seconds()

    def extend(self, ability_id: str, extra_seconds: float):
        if ability_id in self.active_durations:
            self.active_durations[ability_id]['end'] += timedelta(seconds=extra_seconds)
            logger.info(f"⏩ {ability_id} 持续时间延长: +{extra_seconds}秒")

    def terminate(self, ability_id: str):
        if ability_id in self.active_durations:
            del self.active_durations[ability_id]
            logger.info(f"⏹️ {ability_id} 强制终止")

    def get_all_active(self) -> Dict[str, float]:
        return {aid: self.remaining(aid) for aid in list(self.active_durations.keys()) if self.is_active(aid)}
