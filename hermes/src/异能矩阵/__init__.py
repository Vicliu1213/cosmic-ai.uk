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
    ACTIVATING = "activating"   # 激活中
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
    level: int = 1
    max_level: int = 10
    breakthrough_count: int = 0
    breakthrough: bool = False
