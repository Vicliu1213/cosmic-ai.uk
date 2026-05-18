"""
冷却时间管理 - 我是时间管理大师
"""
from typing import Dict
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CooldownManagement:
    """
    视角：我是精密的计时器
    职责：追踪所有异能的冷却状态，一秒不差
    """
    def __init__(self):
        self.cooldown_registry = {}
        self.reduction_factors = defaultdict(lambda: 1.0)
        logger.info("⏰ 冷却时间管理系统已启动")

    def start_cooldown(self, ability_id: str, cooldown_duration: float, reduction: float = 0.0):
        effective_duration = cooldown_duration * (1 - reduction)
        end_time = datetime.now() + timedelta(seconds=effective_duration)
        self.cooldown_registry[ability_id] = end_time
        logger.info(f"⏳ {ability_id} 开始冷却: {effective_duration:.1f}秒")

    def check_cooldown_status(self, ability_id: str) -> Dict:
        if ability_id not in self.cooldown_registry:
            return {'ready': True, 'remaining': 0.0, 'progress': 1.0, 'status': '✓ 就绪'}
        end_time = self.cooldown_registry[ability_id]
        now = datetime.now()
        if now >= end_time:
            del self.cooldown_registry[ability_id]
            return {'ready': True, 'remaining': 0.0, 'progress': 1.0, 'status': '✓ 就绪'}
        remaining = (end_time - now).total_seconds()
        total = 10.0
        progress = 1.0 - (remaining / total)
        return {'ready': False, 'remaining': remaining, 'progress': progress, 'status': f'⏳ 冷却中 ({remaining:.1f}秒)'}

    def reduce_cooldown_time(self, ability_id: str, reduction_seconds: float):
        if ability_id not in self.cooldown_registry:
            logger.warning(f"⚠️ {ability_id} 不在冷却中，无法减少")
            return
        end_time = self.cooldown_registry[ability_id]
        new_end_time = end_time - timedelta(seconds=reduction_seconds)
        if new_end_time < datetime.now():
            new_end_time = datetime.now()
        self.cooldown_registry[ability_id] = new_end_time
        logger.info(f"⚡ {ability_id} 冷却加速: -{reduction_seconds}秒")

    def get_all_cooldowns(self) -> Dict[str, Dict]:
        return {aid: self.check_cooldown_status(aid) for aid in list(self.cooldown_registry.keys())}
