"""
能量回收系统 - 我是回收站，将废弃能量变废为宝
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class EnergyRecoverySystem:
    """
    视角：我是循环利用专家
    职责：从取消、失败、或过期的异能中回收能量
    """
    def __init__(self, recovery_rate: float = 0.7):
        self.recovery_rate = recovery_rate  # 回收比例
        self.recovered_total: float = 0.0
        self.recovery_log: List[Dict] = []
        logger.info(f"♻️ 能量回收系统已就绪，回收率: {recovery_rate*100:.0f}%")

    def recover_from_cancel(self, ability_id: str, original_cost: float) -> float:
        """取消激活时部分回收能量"""
        recovered = original_cost * self.recovery_rate
        self.recovered_total += recovered
        self.recovery_log.append({'source': ability_id, 'type': 'cancel', 'amount': recovered})
        logger.info(f"♻️ {ability_id} 取消回收: {recovered:.1f} 能量（原成本: {original_cost:.1f}）")
        return recovered

    def recover_from_interrupt(self, ability_id: str, original_cost: float, completion_pct: float) -> float:
        """中断异能时按完成比例回收剩余能量"""
        unused_cost = original_cost * (1 - completion_pct)
        recovered = unused_cost * self.recovery_rate
        self.recovered_total += recovered
        self.recovery_log.append({'source': ability_id, 'type': 'interrupt', 'amount': recovered})
        logger.info(f"♻️ {ability_id} 中断回收: {recovered:.1f} 能量（完成 {completion_pct*100:.0f}%）")
        return recovered

    def get_recovery_stats(self) -> Dict:
        return {
            'total_recovered': self.recovered_total,
            'recovery_events': len(self.recovery_log),
            'average_per_event': self.recovered_total / max(1, len(self.recovery_log))
        }
