"""
能力冷却监控 - 我是监控中心，实时追踪所有冷却状态
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class AbilityCooldownMonitor:
    """
    视角：我是全局监控员
    职责：汇总并展示所有异能的冷却状态
    """
    def __init__(self, cooldown_manager):
        self.cooldown_manager = cooldown_manager
        logger.info("📡 能力冷却监控已启动")

    def get_dashboard(self) -> List[Dict]:
        """生成冷却状态仪表盘"""
        all_cooldowns = self.cooldown_manager.get_all_cooldowns()
        dashboard = []
        for ability_id, status in all_cooldowns.items():
            bar_len = 20
            filled = int(status['progress'] * bar_len)
            bar = '█' * filled + '░' * (bar_len - filled)
            dashboard.append({
                'ability_id': ability_id,
                'status': status['status'],
                'progress_bar': f"[{bar}] {status['progress']*100:.0f}%",
                'ready': status['ready']
            })
        return dashboard

    def alert_ready(self) -> List[str]:
        """返回刚冷却完毕可用的异能"""
        ready = []
        for ability_id, status in self.cooldown_manager.get_all_cooldowns().items():
            if status['ready']:
                ready.append(ability_id)
                logger.info(f"🔔 {ability_id} 冷却完毕，可以使用！")
        return ready

    def summary(self) -> Dict:
        cooldowns = self.cooldown_manager.get_all_cooldowns()
        total = len(cooldowns)
        ready_count = sum(1 for s in cooldowns.values() if s['ready'])
        return {
            'total_tracked': total,
            'ready': ready_count,
            'cooling': total - ready_count
        }
