"""
核心矩阵 - 我是指挥中心，统筹全局
"""
from typing import Dict, Optional
from datetime import datetime
import logging
from . import AbilityConfig, ActivationStatus
from .异能激活器 import (
    ConditionDetectionSystem, ActivationEnergyCalculation,
    ActivationSequenceOptimization, CooldownManagement, AbilityCombinationGeneration
)
from .能力管理系统 import (
    EnergyAllocationAlgorithm, AbilityPrioritySettings,
    AbilityDurationControl, AbilityIntensityAdjuster, AbilityCooldownMonitor
)
from .能量分配系统 import (
    EnergyPoolManager, DemandAssessmentSystem,
    AllocationStrategySelector, DynamicAdjustmentMechanism, EnergyRecoverySystem
)
from .异能协同引擎 import (
    SynergyEffectAnalysis, ConflictDetectionMechanism,
    OptimalCombinationFinder, SynergyStrengthCalculation
)

logger = logging.getLogger(__name__)

class CoreMatrix:
    """
    视角：我是异能系统的大脑
    职责：协调所有子系统，做出最优决策
    """
    def __init__(self, energy_capacity: float = 1000.0):
        # 异能激活器
        self.condition_detector = ConditionDetectionSystem()
        self.energy_calculator = ActivationEnergyCalculation()
        self.sequence_optimizer = ActivationSequenceOptimization()
        self.cooldown_manager = CooldownManagement()
        self.combo_generator = AbilityCombinationGeneration()
        # 能力管理系统
        self.energy_allocator = EnergyAllocationAlgorithm(energy_capacity)
        self.priority_settings = AbilityPrioritySettings()
        self.duration_control = AbilityDurationControl()
        self.intensity_adjuster = AbilityIntensityAdjuster()
        self.cooldown_monitor = AbilityCooldownMonitor(self.cooldown_manager)
        # 能量分配系统
        self.energy_pool = EnergyPoolManager(capacity=energy_capacity)
        self.demand_assessor = DemandAssessmentSystem()
        self.strategy_selector = AllocationStrategySelector()
        self.dynamic_adjuster = DynamicAdjustmentMechanism()
        self.energy_recovery = EnergyRecoverySystem()
        # 异能协同引擎
        self.synergy_analyzer = SynergyEffectAnalysis()
        self.conflict_detector = ConflictDetectionMechanism()
        self.optimal_finder = OptimalCombinationFinder()
        self.synergy_calculator = SynergyStrengthCalculation()
        # 运行状态
        self.active_abilities: Dict = {}
        logger.info("=" * 50)
        logger.info("🌟 异能矩阵核心系统已启动（全子系统就绪）")
        logger.info("=" * 50)

    async def activate_ability(
        self,
        ability: AbilityConfig,
        intensity: float = 1.0,
        user_state: Dict = None,
        environment: Dict = None
    ) -> Dict:
        """完整激活流程：检测 → 计算 → 扣除 → 激活 → 冷却"""
        logger.info(f"\n{'='*50}\n🚀 尝试激活: {ability.name}\n{'='*50}")
        pool_status = self.energy_pool.get_status()
        user_state = user_state or {
            'available_energy': pool_status['current'],
            'health': 100,
            'status': 'normal'
        }
        environment = environment or {}

        # 1. 条件检查
        passed, reasons = self.condition_detector.check_activation_conditions(ability, user_state, environment)
        if not passed:
            return {'success': False, 'reasons': reasons, 'status': ActivationStatus.READY}

        # 2. 能量成本计算
        energy_cost = self.energy_calculator.calculate_activation_cost(ability, intensity)

        # 3. 扣除能量
        if not self.energy_pool.consume(energy_cost):
            return {'success': False, 'reasons': ['能量不足'], 'status': ActivationStatus.EXHAUSTED}

        # 4. 激活
        self.active_abilities[ability.ability_id] = {
            'ability': ability, 'intensity': intensity,
            'activated_at': datetime.now(), 'status': ActivationStatus.ACTIVE
        }
        self.duration_control.start(ability.ability_id, ability.base_cooldown * 2)
        logger.info(f"✨ {ability.name} 已激活！")

        # 5. 启动冷却
        self.cooldown_manager.start_cooldown(ability.ability_id, ability.base_cooldown)

        logger.info(f"\n{'='*50}\n✅ 激活成功！\n{'='*50}\n")
        return {
            'success': True, 'energy_cost': energy_cost,
            'remaining_energy': self.energy_pool.current,
            'status': ActivationStatus.ACTIVE, 'cooldown': ability.base_cooldown
        }

    def get_system_status(self) -> Dict:
        pool = self.energy_pool.get_status()
        return {
            'energy_status': pool,
            'active_abilities': len(self.active_abilities),
            'cooling_abilities': len(self.cooldown_manager.cooldown_registry),
            'system_health': 'optimal' if pool['percentage'] > 30 else 'low',
            'cooldown_dashboard': self.cooldown_monitor.get_dashboard()
        }
