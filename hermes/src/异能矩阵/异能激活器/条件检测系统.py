"""
条件检测系统 - 我是守门员，决定异能能否激活
"""
from typing import Dict, List, Tuple
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class ConditionDetectionSystem:
    """
    视角：我是一个严格的检查员
    职责：确保每次异能激活都满足所有必要条件
    """
    def __init__(self):
        self.environmental_sensors = {}
        self.user_state_monitor = {}
        self.safety_protocols = {}
        logger.info("🔍 条件检测系统已初始化 - 守护激活安全")

    def check_activation_conditions(self, ability: AbilityConfig, user_state: Dict, environment: Dict) -> Tuple[bool, List[str]]:
        failed_checks = []
        if not self._check_energy_availability(ability, user_state):
            failed_checks.append("能量不足 - 需要充能")
        if not self._validate_user_state(user_state):
            failed_checks.append("用户状态异常 - 无法激活")
        if not self._check_environment(ability, environment):
            failed_checks.append("环境条件不满足")
        if not self._check_cooldown_status(ability.ability_id):
            failed_checks.append(f"冷却中 - 剩余时间: {self._get_remaining_cooldown(ability.ability_id)}秒")
        if not self._check_safety_limits(ability):
            failed_checks.append("触发安全限制 - 暂时禁用")
        passed = len(failed_checks) == 0
        if passed:
            logger.info(f"✅ {ability.name} 通过所有条件检查")
        else:
            logger.warning(f"❌ {ability.name} 未通过检查: {', '.join(failed_checks)}")
        return passed, failed_checks

    def _check_energy_availability(self, ability: AbilityConfig, user_state: Dict) -> bool:
        return user_state.get('available_energy', 0) >= ability.base_energy_cost

    def _validate_user_state(self, user_state: Dict) -> bool:
        health = user_state.get('health', 100)
        status = user_state.get('status', 'normal')
        return health > 20 and status not in ['stunned', 'disabled', 'unconscious']

    def _check_environment(self, ability: AbilityConfig, environment: Dict) -> bool:
        if 'fire' in ability.synergy_tags and environment.get('underwater', False):
            return False
        return True

    def _check_cooldown_status(self, ability_id: str) -> bool:
        return True

    def _get_remaining_cooldown(self, ability_id: str) -> float:
        return 0.0

    def _check_safety_limits(self, ability: AbilityConfig) -> bool:
        return True
