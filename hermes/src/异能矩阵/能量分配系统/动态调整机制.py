"""
动态调整机制 - 我是实时调控员，根据状态动态调整分配
"""
from typing import Dict, Callable
import logging

logger = logging.getLogger(__name__)

class DynamicAdjustmentMechanism:
    """
    视角：我是自适应控制器
    职责：实时监控并动态调整能量分配
    """
    def __init__(self):
        self.adjustment_rules: Dict[str, Callable] = {}
        self.adjustment_history: list = []
        logger.info("🔄 动态调整机制已激活")

    def register_rule(self, rule_name: str, condition_fn: Callable, adjustment_fn: Callable):
        """注册一条调整规则：当condition成立时执行adjustment"""
        self.adjustment_rules[rule_name] = (condition_fn, adjustment_fn)
        logger.info(f"📋 注册调整规则: {rule_name}")

    def evaluate(self, context: Dict) -> Dict:
        """评估所有规则，返回建议的调整列表"""
        adjustments = []
        for rule_name, (condition_fn, adjustment_fn) in self.adjustment_rules.items():
            try:
                if condition_fn(context):
                    result = adjustment_fn(context)
                    adjustments.append({'rule': rule_name, 'adjustment': result})
                    logger.info(f"✅ 规则触发: {rule_name} → {result}")
            except Exception as e:
                logger.warning(f"⚠️ 规则 {rule_name} 执行失败: {e}")
        self.adjustment_history.extend(adjustments)
        return {'triggered': len(adjustments), 'adjustments': adjustments}

    def apply_emergency_cutoff(self, allocation: Dict[str, float], cutoff_factor: float = 0.5) -> Dict[str, float]:
        """紧急情况下削减所有分配"""
        adjusted = {k: v * cutoff_factor for k, v in allocation.items()}
        logger.warning(f"🚨 紧急削减：所有分配降低至 {cutoff_factor*100:.0f}%")
        return adjusted
