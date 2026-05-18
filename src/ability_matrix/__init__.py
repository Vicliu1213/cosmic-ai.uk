# ==================== 异能矩阵/__init__.py ====================
"""
异能矩阵系统 - 主入口
整合所有子系统，提供统一的异能管理接口
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AbilityType(Enum):
    """异能类型枚举"""
    OFFENSIVE = "offensive"      # 攻击型
    DEFENSIVE = "defensive"      # 防御型
    SUPPORT = "support"          # 支援型
    UTILITY = "utility"          # 工具型
    HYBRID = "hybrid"            # 混合型

class ActivationStatus(Enum):
    """激活状态"""
    READY = "ready"              # 就绪
    ACTIVATING = "activating"    # 激活中
    ACTIVE = "active"            # 已激活
    COOLING = "cooling"          # 冷却中
    EXHAUSTED = "exhausted"      # 能量耗尽

@dataclass
class AbilityConfig:
    """异能配置数据类"""
    ability_id: str
    name: str
    ability_type: AbilityType
    base_energy_cost: float
    base_cooldown: float  # 秒
    max_intensity: float = 1.0
    synergy_tags: List[str] = field(default_factory=list)
    conflict_tags: List[str] = field(default_factory=list)


# ==================== 异能激活器/条件检测系统.py ====================
"""
条件检测系统 - 我是守门员，决定异能能否激活
"""
from typing import Dict, Tuple

class ConditionDetectionSystem:
    """
    视角：我是一个严格的检查员
    职责：确保每次异能激活都满足所有必要条件
    """
    
    def __init__(self):
        self.environmental_sensors = {}  # 环境传感器
        self.user_state_monitor = {}     # 用户状态监控器
        self.safety_protocols = {}       # 安全协议
        logger.info("🔍 条件检测系统已初始化 - 守护激活安全")
    
    def check_activation_conditions(
        self, 
        ability: AbilityConfig, 
        user_state: Dict,
        environment: Dict
    ) -> Tuple[bool, List[str]]:
        """
        综合条件检查 - 这是我的核心职责
        
        我会像医生检查病人一样，逐项核对所有指标
        返回：(是否通过, 未通过的原因列表)
        """
        failed_checks = []
        
        # 1. 能量充足性检查
        if not self._check_energy_availability(ability, user_state):
            failed_checks.append("能量不足 - 需要充能")
        
        # 2. 用户状态检查
        if not self._validate_user_state(user_state):
            failed_checks.append("用户状态异常 - 无法激活")
        
        # 3. 环境因素检查
        if not self._check_environment(ability, environment):
            failed_checks.append("环境条件不满足")
        
        # 4. 冷却状态检查
        if not self._check_cooldown_status(ability.ability_id):
            failed_checks.append(f"冷却中 - 剩余时间: {self._get_remaining_cooldown(ability.ability_id)}秒")
        
        # 5. 安全限制检查
        if not self._check_safety_limits(ability):
            failed_checks.append("触发安全限制 - 暂时禁用")
        
        passed = len(failed_checks) == 0
        
        if passed:
            logger.info(f"✅ {ability.name} 通过所有条件检查")
        else:
            logger.warning(f"❌ {ability.name} 未通过检查: {', '.join(failed_checks)}")
        
        return passed, failed_checks
    
    def _check_energy_availability(self, ability: AbilityConfig, user_state: Dict) -> bool:
        """能量可用性检查 - 我会计算是否有足够能量"""
        available_energy = user_state.get('available_energy', 0)
        required_energy = ability.base_energy_cost
        return available_energy >= required_energy
    
    def _validate_user_state(self, user_state: Dict) -> bool:
        """用户状态验证 - 确保用户处于健康状态"""
        health = user_state.get('health', 100)
        status = user_state.get('status', 'normal')
        return health > 20 and status not in ['stunned', 'disabled', 'unconscious']
    
    def _check_environment(self, ability: AbilityConfig, environment: Dict) -> bool:
        """环境检查 - 有些异能对环境有特殊要求"""
        # 示例：火系异能在水下无法使用
        if 'fire' in ability.synergy_tags and environment.get('underwater', False):
            return False
        return True
    
    def _check_cooldown_status(self, ability_id: str) -> bool:
        """冷却状态检查"""
        # 这里需要与冷却时间管理器交互
        return True  # 简化实现
    
    def _get_remaining_cooldown(self, ability_id: str) -> float:
        """获取剩余冷却时间"""
        return 0.0  # 简化实现
    
    def _check_safety_limits(self, ability: AbilityConfig) -> bool:
        """安全限制检查 - 防止滥用"""
        return True  # 简化实现


# ==================== 异能激活器/激活能量计算.py ====================
"""
激活能量计算 - 我是精算师，计算每次激活的成本
"""

class ActivationEnergyCalculation:
    """
    视角：我是能量会计
    职责：精确计算激活成本，优化能量使用
    """
    
    def __init__(self):
        self.efficiency_multiplier = 1.0
        self.cost_history = []  # 历史成本记录
        logger.info("⚡ 激活能量计算系统已就绪")
    
    def calculate_activation_cost(
        self,
        ability: AbilityConfig,
        intensity: float = 1.0,
        duration: float = 1.0,
        modifiers: Dict = None
    ) -> float:
        """
        计算激活成本 - 这是我的专业领域
        
        我会考虑：基础成本、强度系数、持续时间、环境修正等
        """
        base_cost = ability.base_energy_cost
        
        # 强度系数 - 更强的异能需要更多能量
        intensity_factor = self._calculate_intensity_factor(intensity)
        
        # 持续时间系数 - 持续时间越长，成本越高
        duration_factor = self._calculate_duration_factor(duration)
        
        # 环境修正 - 有利环境可以降低成本
        environmental_modifier = self._get_environmental_modifier(modifiers or {})
        
        # 效率加成 - 熟练度提升可以降低能量消耗
        efficiency = self.efficiency_multiplier
        
        # 最终计算公式
        total_cost = (
            base_cost * 
            intensity_factor * 
            duration_factor * 
            environmental_modifier / 
            efficiency
        )
        
        logger.info(f"💰 {ability.name} 激活成本: {total_cost:.2f} 能量点")
        logger.debug(f"   └─ 基础: {base_cost} × 强度: {intensity_factor:.2f} × 持续: {duration_factor:.2f} × 环境: {environmental_modifier:.2f} ÷ 效率: {efficiency:.2f}")
        
        return total_cost
    
    def _calculate_intensity_factor(self, intensity: float) -> float:
        """
        强度系数计算
        使用非线性增长 - 高强度消耗更多
        """
        # 使用平方关系：强度翻倍，能耗约4倍
        return intensity ** 1.5
    
    def _calculate_duration_factor(self, duration: float) -> float:
        """持续时间系数 - 基本线性关系"""
        return max(0.5, duration)  # 最低50%成本
    
    def _get_environmental_modifier(self, modifiers: Dict) -> float:
        """环境修正系数"""
        base_modifier = 1.0
        
        # 有利条件降低成本
        if modifiers.get('favorable_terrain', False):
            base_modifier *= 0.85
        
        # 不利条件增加成本
        if modifiers.get('hostile_environment', False):
            base_modifier *= 1.25
        
        return base_modifier
    
    def optimize_energy_usage(self, abilities: List[AbilityConfig]) -> Dict:
        """
        能量使用优化建议
        我会分析并给出最经济的使用方案
        """
        optimization_report = {
            'total_cost': 0,
            'recommendations': [],
            'savings_potential': 0
        }
        
        for ability in abilities:
            cost = self.calculate_activation_cost(ability)
            optimization_report['total_cost'] += cost
            
            # 检查是否有优化空间
            if cost > ability.base_energy_cost * 1.2:
                optimization_report['recommendations'].append(
                    f"{ability.name}: 考虑降低强度或寻找有利环境"
                )
        
        return optimization_report


# ==================== 异能激活器/激活序列优化.py ====================
"""
激活序列优化 - 我是编舞者，安排最优的激活顺序
"""

class ActivationSequenceOptimization:
    """
    视角：我是战术规划师
    职责：优化多个异能的激活顺序，最大化效率
    """
    
    def __init__(self):
        self.sequence_cache = {}  # 缓存优化方案
        logger.info("🎯 激活序列优化器已上线")
    
    def optimize_sequence(
        self,
        abilities: List[AbilityConfig],
        objective: str = 'efficiency'
    ) -> List[str]:
        """
        序列优化 - 找出最佳激活顺序
        
        目标可以是：
        - efficiency: 最高效率（最低总成本）
        - speed: 最快速度（最短总时间）
        - power: 最大威力（最高输出）
        """
        logger.info(f"🔄 开始优化 {len(abilities)} 个异能的激活序列")
        logger.info(f"   优化目标: {objective}")
        
        if objective == 'efficiency':
            return self._optimize_for_efficiency(abilities)
        elif objective == 'speed':
            return self._optimize_for_speed(abilities)
        elif objective == 'power':
            return self._optimize_for_power(abilities)
        else:
            return [a.ability_id for a in abilities]
    
    def _optimize_for_efficiency(self, abilities: List[AbilityConfig]) -> List[str]:
        """
        效率优化 - 按能量成本排序
        先用低成本异能建立优势
        """
        sorted_abilities = sorted(abilities, key=lambda a: a.base_energy_cost)
        sequence = [a.ability_id for a in sorted_abilities]
        
        logger.info("   策略: 低成本优先 → 保持能量池健康")
        return sequence
    
    def _optimize_for_speed(self, abilities: List[AbilityConfig]) -> List[str]:
        """
        速度优化 - 按激活时间排序
        快速异能优先，打出连击
        """
        sorted_abilities = sorted(abilities, key=lambda a: a.base_cooldown)
        sequence = [a.ability_id for a in sorted_abilities]
        
        logger.info("   策略: 快速异能优先 → 形成连续攻势")
        return sequence
    
    def _optimize_for_power(self, abilities: List[AbilityConfig]) -> List[str]:
        """
        威力优化 - 高威力异能优先
        """
        # 按类型权重排序：OFFENSIVE > HYBRID > SUPPORT > DEFENSIVE
        type_priority = {
            AbilityType.OFFENSIVE: 4,
            AbilityType.HYBRID: 3,
            AbilityType.SUPPORT: 2,
            AbilityType.DEFENSIVE: 1,
            AbilityType.UTILITY: 0
        }
        
        sorted_abilities = sorted(
            abilities, 
            key=lambda a: type_priority.get(a.ability_type, 0),
            reverse=True
        )
        sequence = [a.ability_id for a in sorted_abilities]
        
        logger.info("   策略: 攻击优先 → 压制性输出")
        return sequence
    
    def parallel_activation_planning(
        self,
        abilities: List[AbilityConfig]
    ) -> Dict[str, List[str]]:
        """
        并行激活规划
        
        我会识别哪些异能可以同时激活
        就像指挥乐队，让多个声部和谐演奏
        """
        plan = {
            'wave_1': [],  # 第一波
            'wave_2': [],  # 第二波
            'wave_3': []   # 第三波
        }
        
        # 按类型分组并行激活
        for ability in abilities:
            if ability.ability_type == AbilityType.DEFENSIVE:
                plan['wave_1'].append(ability.ability_id)  # 防御先行
            elif ability.ability_type == AbilityType.SUPPORT:
                plan['wave_2'].append(ability.ability_id)  # 支援跟上
            else:
                plan['wave_3'].append(ability.ability_id)  # 攻击压制
        
        logger.info("📋 并行激活计划:")
        for wave, ability_ids in plan.items():
            logger.info(f"   {wave}: {len(ability_ids)} 个异能")
        
        return plan


# ==================== 异能激活器/冷却时间管理.py ====================
"""
冷却时间管理 - 我是时间管理大师
"""
from collections import defaultdict
from datetime import datetime, timedelta

class CooldownManagement:
    """
    视角：我是精密的计时器
    职责：追踪所有异能的冷却状态，一秒不差
    """
    
    def __init__(self):
        self.cooldown_registry = {}  # {ability_id: end_time}
        self.reduction_factors = defaultdict(lambda: 1.0)
        logger.info("⏰ 冷却时间管理系统已启动")
    
    def start_cooldown(
        self,
        ability_id: str,
        cooldown_duration: float,
        reduction: float = 0.0
    ):
        """
        开始冷却 - 异能使用后我会开始倒计时
        
        reduction: 冷却减免 (0.0-1.0)，0.2 表示减少20%冷却时间
        """
        effective_duration = cooldown_duration * (1 - reduction)
        end_time = datetime.now() + timedelta(seconds=effective_duration)
        
        self.cooldown_registry[ability_id] = end_time
        
        logger.info(f"⏳ {ability_id} 开始冷却: {effective_duration:.1f}秒")
        logger.debug(f"   └─ 基础: {cooldown_duration}秒 × 减免: {(1-reduction)*100:.0f}%")
    
    def check_cooldown_status(self, ability_id: str) -> Dict:
        """
        检查冷却状态
        
        我会告诉你：是否就绪、还需多久、完成百分比
        """
        if ability_id not in self.cooldown_registry:
            return {
                'ready': True,
                'remaining': 0.0,
                'progress': 1.0,
                'status': '✓ 就绪'
            }
        
        end_time = self.cooldown_registry[ability_id]
        now = datetime.now()
        
        if now >= end_time:
            # 冷却完成，清理记录
            del self.cooldown_registry[ability_id]
            return {
                'ready': True,
                'remaining': 0.0,
                'progress': 1.0,
                'status': '✓ 就绪'
            }
        
        remaining = (end_time - now).total_seconds()
        # 假设原始冷却时间（简化，实际应该记录）
        total = 10.0  
        progress = 1.0 - (remaining / total)
        
        return {
            'ready': False,
            'remaining': remaining,
            'progress': progress,
            'status': f'⏳ 冷却中 ({remaining:.1f}秒)'
        }
    
    def reduce_cooldown_time(
        self,
        ability_id: str,
        reduction_seconds: float
    ):
        """
        减少冷却时间 - 某些效果可以加速冷却
        
        就像给时钟拨快了几秒
        """
        if ability_id not in self.cooldown_registry:
            logger.warning(f"⚠️ {ability_id} 不在冷却中，无法减少")
            return
        
        end_time = self.cooldown_registry[ability_id]
        new_end_time = end_time - timedelta(seconds=reduction_seconds)
        
        # 确保不会变成负数
        if new_end_time < datetime.now():
            new_end_time = datetime.now()
        
        self.cooldown_registry[ability_id] = new_end_time
        logger.info(f"⚡ {ability_id} 冷却加速: -{reduction_seconds}秒")
    
    def get_all_cooldowns(self) -> Dict[str, Dict]:
        """获取所有冷却状态的总览"""
        overview = {}
        for ability_id in list(self.cooldown_registry.keys()):
            overview[ability_id] = self.check_cooldown_status(ability_id)
        return overview


# ==================== 异能激活器/异能组合生成.py ====================
"""
异能组合生成 - 我是创意大师，设计最强组合
"""

class AbilityCombinationGeneration:
    """
    视角：我是战术创新者
    职责：探索并创造强大的异能组合
    """
    
    def __init__(self):
        self.saved_combos = {}  # 保存的组合方案
        self.combo_ratings = {}  # 组合评分
        logger.info("🎨 异能组合生成器已就绪")
    
    def generate_combinations(
        self,
        available_abilities: List[AbilityConfig],
        combo_size: int = 3
    ) -> List[Dict]:
        """
        生成组合 - 探索所有可能的异能组合
        
        我会像厨师一样，尝试不同食材的搭配
        """
        from itertools import combinations
        
        all_combos = list(combinations(available_abilities, combo_size))
        
        logger.info(f"🔮 生成 {len(all_combos)} 个{combo_size}异能组合")
        
        evaluated_combos = []
        for combo in all_combos[:10]:  # 限制评估数量
            evaluation = self.evaluate_combination(list(combo))
            evaluated_combos.append(evaluation)
        
        # 按评分排序
        evaluated_combos.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 显示前3名
        logger.info("🏆 最佳组合Top 3:")
        for i, combo in enumerate(evaluated_combos[:3], 1):
            logger.info(f"   #{i}: {combo['combo_name']} - 评分: {combo['total_score']:.1f}")
        
        return evaluated_combos
    
    def evaluate_combination(self, abilities: List[AbilityConfig]) -> Dict:
        """
        评估组合效果
        
        我会从多个维度打分：
        - 协同效应
        - 能量效率
        - 战术价值
        - 灵活性
        """
        combo_name = " + ".join([a.name for a in abilities])
        
        # 计算各项指标
        synergy_score = self._calculate_synergy(abilities)
        efficiency_score = self._calculate_efficiency(abilities)
        tactical_score = self._calculate_tactical_value(abilities)
        flexibility_score = self._calculate_flexibility(abilities)
        
        total_score = (
            synergy_score * 0.35 +      # 协同效应权重35%
            efficiency_score * 0.25 +   # 能量效率权重25%
            tactical_score * 0.25 +     # 战术价值权重25%
            flexibility_score * 0.15    # 灵活性权重15%
        )
        
        return {
            'combo_name': combo_name,
            'abilities': [a.ability_id for a in abilities],
            'synergy_score': synergy_score,
            'efficiency_score': efficiency_score,
            'tactical_score': tactical_score,
            'flexibility_score': flexibility_score,
            'total_score': total_score,
            'recommendation': self._generate_recommendation(total_score)
        }
    
    def _calculate_synergy(self, abilities: List[AbilityConfig]) -> float:
        """计算协同效应分数"""
        score = 50.0  # 基础分
        
        # 检查标签匹配
        all_tags = []
        for ability in abilities:
            all_tags.extend(ability.synergy_tags)
        
        # 有共同标签加分
        unique_tags = set(all_tags)
        if len(all_tags) > len(unique_tags):
            score += (len(all_tags) - len(unique_tags)) * 10
        
        return min(100.0, score)
    
    def _calculate_efficiency(self, abilities: List[AbilityConfig]) -> float:
        """计算能量效率分数"""
        total_cost = sum(a.base_energy_cost for a in abilities)
        avg_cost = total_cost / len(abilities)
        
        # 成本越低，效率越高
        if avg_cost < 30:
            return 90.0
        elif avg_cost < 50:
            return 70.0
        else:
            return 50.0
    
    def _calculate_tactical_value(self, abilities: List[AbilityConfig]) -> float:
        """计算战术价值"""
        type_diversity = len(set(a.ability_type for a in abilities))
        
        # 类型多样性越高，战术价值越高
        return type_diversity * 25.0
    
    def _calculate_flexibility(self, abilities: List[AbilityConfig]) -> float:
        """计算灵活性 - 能应对多少种情况"""
        flexibility = 60.0
        
        # 检查是否覆盖多种场景
        has_offensive = any(a.ability_type == AbilityType.OFFENSIVE for a in abilities)
        has_defensive = any(a.ability_type == AbilityType.DEFENSIVE for a in abilities)
        has_support = any(a.ability_type == AbilityType.SUPPORT for a in abilities)
        
        if has_offensive: flexibility += 10
        if has_defensive: flexibility += 15
        if has_support: flexibility += 15
        
        return flexibility
    
    def _generate_recommendation(self, score: float) -> str:
        """根据评分生成建议"""
        if score >= 80:
            return "⭐⭐⭐ 卓越组合 - 强烈推荐"
        elif score >= 65:
            return "⭐⭐ 优秀组合 - 值得使用"
        elif score >= 50:
            return "⭐ 可用组合 - 特定情况下有效"
        else:
            return "❌ 不推荐 - 考虑其他方案"
    
    def save_custom_sequence(
        self,
        combo_name: str,
        abilities: List[str],
        notes: str = ""
    ):
        """
        保存自定义组合
        
        用户可以保存自己喜欢的组合，方便快速调用
        """
        self.saved_combos[combo_name] = {
            'abilities': abilities,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        logger.info(f"💾 组合已保存: {combo_name}")
        logger.info(f"   包含 {len(abilities)} 个异能")


# ==================== 核心矩阵.py ====================
"""
核心矩阵 - 我是指挥中心，统筹全局
"""

class CoreMatrix:
    """
    视角：我是异能系统的大脑
    职责：协调所有子系统，做出最优决策
    """
    
    def __init__(self):
        # 初始化所有子系统
        self.condition_detector = ConditionDetectionSystem()
        self.energy_calculator = ActivationEnergyCalculation()
        self.sequence_optimizer = ActivationSequenceOptimization()
        self.cooldown_manager = CooldownManagement()
        self.combo_generator = AbilityCombinationGeneration()
        
        # 系统状态
        self.active_abilities = {}
        self.energy_pool = 1000.0  # 总能量池
        self.available_energy = 1000.0
        
        logger.info("=" * 50)
        logger.info("🌟 异能矩阵核心系统已启动")
        logger.info("=" * 50)
    
    async def activate_ability(
        self,
        ability: AbilityConfig,
        intensity: float = 1.0,
        user_state: Dict = None,
        environment: Dict = None
    ) -> Dict:
        """
        激活异能 - 完整的激活流程
        
        这是我最重要的职责：
        1. 检查条件
        2. 计算成本
        3. 扣除能量
        4. 激活异能
        5. 启动冷却
        """
        logger.info(f"\n{'='*50}")
        logger.info(f"🚀 尝试激活: {ability.name}")
        logger.info(f"{'='*50}")
        
        # 默认状态
        user_state = user_state or {
            'available_energy': self.available_energy,
            'health': 100,
            'status': 'normal'
        }
        environment = environment or {}
        
        # 步骤1: 条件检查
        logger.info("📋 第1步: 条件检查")
        passed, reasons = self.condition_detector.check_activation_conditions(
            ability, user_state, environment
        )
        
        if not passed:
            logger.error(f"❌ 激活失败")
            for reason in reasons:
                logger.error(f"   - {reason}")
            return {
                'success': False,
                'reasons': reasons,
                'status': ActivationStatus.READY
            }
        
        # 步骤2: 能量计算
        logger.info("📋 第2步: 能量成本计算")
        energy_cost = self.energy_calculator.calculate_activation_cost(
            ability, intensity
        )
        
        if self.available_energy < energy_cost:
            logger.error(f"❌ 能量不足: 需要 {energy_cost:.1f}, 可用 {self.available_energy:.1f}")
            return {
                'success': False,
                'reasons': ['能量不足'],
                'status': ActivationStatus.EXHAUSTED
            }
        
        # 步骤3: 扣除能量
        logger.info("📋 第3步: 扣除能量")
        self.available_energy -= energy_cost
        logger.info(f"   能量池: {self.available_energy:.1f}/{self.energy_pool:.1f}")
        
        # 步骤4: 激活异能
        logger.info("📋 第4步: 激活异能")
        self.active_abilities[ability.ability_id] = {
            'ability': ability,
            'intensity': intensity,
            'activated_at': datetime.now(),
            'status': ActivationStatus.ACTIVE
        }
        logger.info(f"✨ {ability.name} 已激活！")
        
        # 步骤5: 启动冷却
        logger.info("📋 第5步: 启动冷却计时")
        self.cooldown_manager.start_cooldown(
            ability.ability_id,
            ability.base_cooldown
        )
        
        logger.info(f"\n{'='*50}")
        logger.info(f"✅ 激活成功！")
        logger.info(f"{'='*50}\n")
        
        return {
            'success': True,
            'energy_cost': energy_cost,
            'remaining_energy': self.available_energy,
            'status': ActivationStatus.ACTIVE,
            'cooldown': ability.base_cooldown
        }
    
    def get_system_status(self) -> Dict:
        """获取系统整体状态 - 我的仪表盘"""
        return {
            'energy_status': {
                'available': self.available_energy,
                'total': self.energy_pool,
                'percentage': (self.available_energy / self.energy_pool) * 100
            },
            'active_abilities': len(self.active_abilities),
            'cooling_abilities': len(self.cooldown_manager.cooldown_registry),
            'system_health': 'optimal' if self.available_energy > self.energy_pool * 0.3 else 'low'
        }


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    # 创建核心矩阵
    matrix = CoreMatrix()
    
    # 定义一些异能
    fireball = AbilityConfig(
        ability_id="fire_001",
        name="火球术",
        ability_type=AbilityType.OFFENSIVE,
        base_energy_cost=50.0,
        base_cooldown=5.0,
        synergy_tags=['fire', 'projectile', 'aoe']
    )
    
    shield = AbilityConfig(
        ability_id="def_001",
        name="能量护盾",
        ability_type=AbilityType.DEFENSIVE,
        base_energy_cost=30.0,
        base_cooldown=10.0,
        synergy_tags=['defense', 'barrier']
    )
    
    heal = AbilityConfig(
        ability_id="sup_001",
        name="治疗术",
        ability_type=AbilityType.SUPPORT,
        base_energy_cost=40.0,
        base_cooldown=8.0,
        synergy_tags=['heal', 'support']
    )
    
    # 测试激活
    print("\n" + "="*60)
    print("🎮 异能矩阵系统演示")
    print("="*60 + "\n")
    
    import asyncio
    
    async def demo():
        # 激活火球术
        result1 = await matrix.activate_ability(fireball, intensity=0.8)
        
        # 激活护盾
        result2 = await matrix.activate_ability(shield)
        
        # 查看系统状态
        print("\n" + "="*60)
        print("📊 系统状态")
        print("="*60)
        status = matrix.get_system_status()
        print(f"能量状态: {status['energy_status']['available']:.1f}/{status['energy_status']['total']:.1f} ({status['energy_status']['percentage']:.1f}%)")
        print(f"激活中的异能: {status['active_abilities']}")
        print(f"冷却中的异能: {status['cooling_abilities']}")
        print(f"系统健康度: {status['system_health']}")
        
        # 生成组合
        print("\n" + "="*60)
        print("🎨 组合生成演示")
        print("="*60)
        combos = matrix.combo_generator.generate_combinations([fireball, shield, heal], combo_size=2)
    
    asyncio.run(demo())
