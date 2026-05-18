"""
能量池管理 - 我是资金库管理员，维护能量储备
"""
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class EnergyPoolManager:
    """
    视角：我是能量银行
    职责：管理总能量池，处理充能与消耗
    """
    def __init__(self, capacity: float = 1000.0, regen_rate: float = 5.0):
        self.capacity = capacity
        self.current = capacity
        self.regen_rate = regen_rate  # 每秒恢复量
        logger.info(f"🔋 能量池初始化: {capacity} 满载，再生速率: {regen_rate}/秒")

    def consume(self, amount: float) -> bool:
        if self.current < amount:
            logger.warning(f"⚠️ 能量不足: 需要 {amount:.1f}，剩余 {self.current:.1f}")
            return False
        self.current -= amount
        logger.info(f"⚡ 消耗 {amount:.1f} 能量，剩余: {self.current:.1f}/{self.capacity:.1f}")
        return True

    def restore(self, amount: float):
        self.current = min(self.capacity, self.current + amount)
        logger.info(f"♻️ 恢复 {amount:.1f} 能量，当前: {self.current:.1f}/{self.capacity:.1f}")

    def tick(self, seconds: float = 1.0):
        """时间流逝触发自动再生"""
        regen = self.regen_rate * seconds
        self.restore(regen)

    def get_status(self) -> Dict:
        pct = (self.current / self.capacity) * 100
        return {
            'current': self.current,
            'capacity': self.capacity,
            'percentage': pct,
            'level': 'full' if pct >= 90 else 'high' if pct >= 60 else 'medium' if pct >= 30 else 'low'
        }
