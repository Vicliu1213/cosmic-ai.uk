#!/usr/bin/env python3
"""
容量管理層 (Capacity Management Layer)
Capacity Management Layer for Cosmic AI Phase 2

統-超指數遞歸協同增長 (Unified Hyper-Exponential Recursive Synergistic Growth)

五個基礎突破之三：容量擴展 (Capacity Management - Breakthrough #3)

此模塊實現資源容量管理、指數級擴展、和動態負載均衡。
通過分層容量管理和協同資源調配實現無限擴展潛力。

Key Concepts:
- Exponential scaling capacity: 指數級擴展容量
- Multi-tier resource pooling: 多層資源池化
- Dynamic load balancing: 動態負載均衡
- Hierarchical capacity hierarchy: 分層容量階層
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import math

logger = logging.getLogger(__name__)


class CapacityTier(Enum):
    """容量層級枚舉 (Capacity Tier Enumeration)"""
    L1_COMPUTE = "l1_compute"  # L1 計算層：快速本地計算
    L2_MEMORY = "l2_memory"  # L2 記憶層：中等容量記憶
    L3_STORAGE = "l3_storage"  # L3 存儲層：大容量存儲
    L4_DISTRIBUTED = "l4_distributed"  # L4 分布層：分布式計算
    L5_QUANTUM = "l5_quantum"  # L5 量子層：量子計算資源


@dataclass
class CapacityMetrics:
    """容量指標 (Capacity Metrics)"""
    timestamp: datetime
    tier: CapacityTier
    total_capacity: float  # 總容量 (字節或操作數)
    used_capacity: float  # 已用容量
    available_capacity: float  # 可用容量
    utilization_rate: float  # 使用率 (0-1)
    throughput: float  # 吞吐量 (操作/秒)
    scaling_efficiency: float  # 擴展效率 (0-1)
    expansion_potential: float  # 擴展潛力 (0-1)


@dataclass
class CapacityState:
    """容量狀態 (Capacity State)"""
    tier: CapacityTier
    current_capacity: float
    max_capacity: float
    growth_rate: float  # 增長速率
    utilization: float  # 使用率
    forecast_demand: float  # 預測需求
    auto_scale_enabled: bool = True


class CapacityScaler(ABC):
    """容量縮放器抽象基類 (Capacity Scaler Abstract Base)"""

    @abstractmethod
    def scale_up(self, target_capacity: float) -> float:
        """擴容 (Scale Up)"""
        pass

    @abstractmethod
    def scale_down(self, target_capacity: float) -> float:
        """縮容 (Scale Down)"""
        pass

    @abstractmethod
    def get_scaling_cost(self) -> float:
        """獲取縮放成本 (Get Scaling Cost)"""
        pass


class ExponentialCapacityScaler(CapacityScaler):
    """指數級容量縮放器 (Exponential Capacity Scaler)
    
    通過指數級增長實現無限擴展潛力
    Achieve unlimited expansion potential through exponential growth
    """

    def __init__(self, base_capacity: float = 1000.0, growth_factor: float = 2.0):
        self.base_capacity = base_capacity
        self.growth_factor = growth_factor
        self.current_level = 0
        self.scaling_history: List[Tuple[datetime, float]] = []

    def scale_up(self, target_capacity: float) -> float:
        """指數級擴容 (Exponential scale up)"""
        
        # 計算所需的級別
        required_level = np.log(target_capacity / self.base_capacity) / np.log(self.growth_factor)
        required_level = math.ceil(required_level)
        
        # 新容量 = 基礎容量 × 增長因子^級別
        new_capacity = self.base_capacity * (self.growth_factor ** required_level)
        
        self.current_level = required_level
        self.scaling_history.append((datetime.now(), new_capacity))
        
        logger.info(f"Exponential scale up: {target_capacity:.2f} → {new_capacity:.2f} (level {required_level})")
        
        return new_capacity

    def scale_down(self, target_capacity: float) -> float:
        """指數級縮容 (Exponential scale down)"""
        
        # 計算所需的級別
        required_level = max(0, np.log(target_capacity / self.base_capacity) / np.log(self.growth_factor))
        required_level = math.floor(required_level)
        
        # 新容量 = 基礎容量 × 增長因子^級別
        new_capacity = self.base_capacity * (self.growth_factor ** required_level)
        
        self.current_level = required_level
        self.scaling_history.append((datetime.now(), new_capacity))
        
        return new_capacity

    def get_scaling_cost(self) -> float:
        """獲取縮放成本 (Get Scaling Cost)
        
        成本與級別呈指數增長
        Cost grows exponentially with level
        """
        return (2 ** self.current_level) * 100  # 基礎成本 × 2^級別


class RecursiveCapacityScaler(CapacityScaler):
    """遞歸容量縮放器 (Recursive Capacity Scaler)
    
    通過遞歸分割實現細粒度容量管理
    Achieve fine-grained capacity management through recursive partitioning
    """

    def __init__(self, recursion_depth: int = 5):
        self.recursion_depth = recursion_depth
        self.partition_tree: Dict[int, float] = {}  # 遞歸分割樹

    def scale_up(self, target_capacity: float) -> float:
        """遞歸擴容 (Recursive scale up)"""
        
        # 遞歸創建分割
        # Recursively create partitions
        current = target_capacity
        
        for level in range(self.recursion_depth):
            # 在每一級分割為多個子分區
            # Partition into sub-partitions at each level
            num_partitions = 2 ** (level + 1)
            partition_size = current / num_partitions
            
            self.partition_tree[level] = partition_size
            current = partition_size
        
        return target_capacity

    def scale_down(self, target_capacity: float) -> float:
        """遞歸縮容 (Recursive scale down)"""
        
        # 反向遞歸收縮
        # Recursive contraction in reverse
        if not self.partition_tree:
            return target_capacity
        
        # 合併分區
        # Merge partitions
        current = target_capacity
        for level in range(self.recursion_depth - 1, -1, -1):
            num_partitions = 2 ** (level + 1)
            current = current * num_partitions
        
        return current

    def get_scaling_cost(self) -> float:
        """獲取縮放成本 (Get Scaling Cost)"""
        # 遞歸成本 = 分割次數
        return float(sum(2 ** i for i in range(self.recursion_depth)))


class AdaptiveCapacityScaler(CapacityScaler):
    """自適應容量縮放器 (Adaptive Capacity Scaler)
    
    根據需求動態選擇最優縮放策略
    Dynamically select optimal scaling strategy based on demand
    """

    def __init__(self):
        self.exponential_scaler = ExponentialCapacityScaler()
        self.recursive_scaler = RecursiveCapacityScaler()
        self.demand_history: List[float] = []

    def scale_up(self, target_capacity: float) -> float:
        """自適應擴容 (Adaptive scale up)"""
        
        self.demand_history.append(target_capacity)
        
        # 分析需求趨勢
        if len(self.demand_history) > 10:
            recent_demand = np.mean(self.demand_history[-10:])
            demand_trend = recent_demand / (np.mean(self.demand_history[-20:-10]) + 1e-10)
        else:
            demand_trend = 1.0
        
        # 高速增長時使用指數縮放
        # Use exponential scaling for rapid growth
        if demand_trend > 1.5:
            return self.exponential_scaler.scale_up(target_capacity)
        else:
            # 緩慢增長時使用遞歸縮放
            # Use recursive scaling for gradual growth
            return self.recursive_scaler.scale_up(target_capacity)

    def scale_down(self, target_capacity: float) -> float:
        """自適應縮容 (Adaptive scale down)"""
        return self.recursive_scaler.scale_down(target_capacity)

    def get_scaling_cost(self) -> float:
        """獲取縮放成本 (Get Scaling Cost)"""
        exp_cost = self.exponential_scaler.get_scaling_cost()
        rec_cost = self.recursive_scaler.get_scaling_cost()
        return min(exp_cost, rec_cost)


class CapacityManager:
    """容量管理器 (Capacity Manager)
    
    統-超指數遞歸協同增長的容量管理核心
    Core capacity management for unified hyper-exponential recursive synergistic growth
    """

    def __init__(self):
        self.tiers: Dict[CapacityTier, CapacityState] = {}
        self.scalers: Dict[CapacityTier, CapacityScaler] = {}
        self.metrics_history: List[CapacityMetrics] = []
        
        # 初始化各層級
        self._initialize_tiers()

    def _initialize_tiers(self) -> None:
        """初始化容量層級 (Initialize Capacity Tiers)"""
        
        tier_configs = {
            CapacityTier.L1_COMPUTE: {"capacity": 1000, "max": 10000},
            CapacityTier.L2_MEMORY: {"capacity": 10000, "max": 100000},
            CapacityTier.L3_STORAGE: {"capacity": 100000, "max": 1000000},
            CapacityTier.L4_DISTRIBUTED: {"capacity": 1000000, "max": 10000000},
            CapacityTier.L5_QUANTUM: {"capacity": 10000000, "max": 100000000}
        }
        
        for tier, config in tier_configs.items():
            self.tiers[tier] = CapacityState(
                tier=tier,
                current_capacity=config["capacity"],
                max_capacity=config["max"],
                growth_rate=1.1,
                utilization=0.5,
                forecast_demand=config["capacity"],
                auto_scale_enabled=True
            )
            
            self.scalers[tier] = AdaptiveCapacityScaler()

    def allocate_capacity(
        self,
        tier: CapacityTier,
        required_capacity: float
    ) -> bool:
        """分配容量 (Allocate Capacity)"""
        
        state = self.tiers.get(tier)
        if not state:
            logger.warning(f"Tier {tier} not found")
            return False
        
        # 檢查可用容量
        available = state.current_capacity - state.forecast_demand
        
        if available >= required_capacity:
            # 直接分配
            state.forecast_demand += required_capacity
            state.utilization = state.forecast_demand / state.current_capacity
            return True
        
        elif state.auto_scale_enabled and state.current_capacity < state.max_capacity:
            # 自動擴容
            scaler = self.scalers[tier]
            new_capacity = scaler.scale_up(required_capacity + state.forecast_demand)
            
            state.current_capacity = min(new_capacity, state.max_capacity)
            state.forecast_demand += required_capacity
            state.utilization = state.forecast_demand / state.current_capacity
            
            logger.info(f"Auto-scaled {tier.value} to {state.current_capacity}")
            return True
        
        else:
            logger.error(f"Cannot allocate {required_capacity} on tier {tier.value}")
            return False

    def release_capacity(
        self,
        tier: CapacityTier,
        released_capacity: float
    ) -> None:
        """釋放容量 (Release Capacity)"""
        
        state = self.tiers.get(tier)
        if state:
            state.forecast_demand = max(0, state.forecast_demand - released_capacity)
            state.utilization = state.forecast_demand / state.current_capacity

    def get_multi_tier_utilization(self) -> Dict[str, float]:
        """獲取多層級使用率 (Get Multi-Tier Utilization)"""
        
        return {
            tier.value: state.utilization
            for tier, state in self.tiers.items()
        }

    def get_hierarchical_capacity_summary(self) -> Dict[str, Any]:
        """獲取分層容量摘要 (Get Hierarchical Capacity Summary)"""
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "tiers": {}
        }
        
        for tier, state in self.tiers.items():
            summary["tiers"][tier.value] = {
                "current_capacity": float(state.current_capacity),
                "max_capacity": float(state.max_capacity),
                "forecast_demand": float(state.forecast_demand),
                "utilization": float(state.utilization),
                "growth_rate": float(state.growth_rate),
                "auto_scale": state.auto_scale_enabled
            }
        
        # 計算總體統計
        total_capacity = sum(state.current_capacity for state in self.tiers.values())
        total_demand = sum(state.forecast_demand for state in self.tiers.values())
        
        summary["total_capacity"] = float(total_capacity)
        summary["total_demand"] = float(total_demand)
        summary["overall_utilization"] = float(total_demand / (total_capacity + 1e-10))
        
        return summary

    def record_capacity_metrics(
        self,
        tier: CapacityTier,
        throughput: float,
        scaling_efficiency: float = 1.0
    ) -> CapacityMetrics:
        """記錄容量指標 (Record Capacity Metrics)"""
        
        state = self.tiers[tier]
        
        metrics = CapacityMetrics(
            timestamp=datetime.now(),
            tier=tier,
            total_capacity=state.current_capacity,
            used_capacity=state.forecast_demand,
            available_capacity=state.current_capacity - state.forecast_demand,
            utilization_rate=state.utilization,
            throughput=throughput,
            scaling_efficiency=scaling_efficiency,
            expansion_potential=1.0 - (state.current_capacity / state.max_capacity)
        )
        
        self.metrics_history.append(metrics)
        return metrics

    def estimate_exponential_expansion_capacity(
        self,
        current_capacity: float,
        levels: int = 5
    ) -> float:
        """估計指數級擴展容量 (Estimate Exponential Expansion Capacity)
        
        計算通過 n 級指數擴展可達到的總容量
        Calculate total capacity achievable through n levels of exponential expansion
        """
        
        # 使用海鷺級聯：每級增長因子 2
        # Use cascading growth: factor 2 per level
        total_capacity = current_capacity
        
        for level in range(levels):
            # 每級容量翻倍
            total_capacity *= 2
        
        return total_capacity

    def estimate_synergistic_capacity_multiplier(
        self,
        active_tiers: int
    ) -> float:
        """估計協同容量倍數 (Estimate Synergistic Capacity Multiplier)
        
        當多個層級協同工作時的容量倍數
        Capacity multiplier when multiple tiers work synergistically
        """
        
        # 超指數：e^(n-1)
        exponential_factor = np.exp(active_tiers - 1)
        
        # 層級協同：log2(n+1)
        hierarchical_factor = np.log2(active_tiers + 1)
        
        return exponential_factor * hierarchical_factor


# 示例用法 (Example Usage)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = CapacityManager()
    
    print("=== Capacity Management Test ===\n")
    
    # 獲取初始容量摘要
    summary = manager.get_hierarchical_capacity_summary()
    print("Initial Capacity Summary:")
    for tier_name, tier_data in summary["tiers"].items():
        print(f"\n{tier_name}:")
        print(f"  Current: {tier_data['current_capacity']:.0f}")
        print(f"  Max: {tier_data['max_capacity']:.0f}")
        print(f"  Utilization: {tier_data['utilization']:.2%}")
    
    # 測試容量分配
    print("\n=== Capacity Allocation Test ===\n")
    
    # 分配 L1 計算容量
    required = 5000
    tier = CapacityTier.L1_COMPUTE
    success = manager.allocate_capacity(tier, required)
    print(f"Allocate {required} to {tier.value}: {'✓' if success else '✗'}")
    
    # 分配更大容量（觸發自動擴容）
    required = 15000
    success = manager.allocate_capacity(tier, required)
    print(f"Allocate {required} to {tier.value}: {'✓' if success else '✗'}")
    
    # 獲取更新後的容量摘要
    print("\n=== Updated Capacity Summary ===\n")
    summary = manager.get_hierarchical_capacity_summary()
    print(f"Overall Utilization: {summary['overall_utilization']:.2%}")
    print(f"Total Capacity: {summary['total_capacity']:.0f}")
    print(f"Total Demand: {summary['total_demand']:.0f}")
    
    # 測試指數擴展
    print("\n=== Exponential Expansion Calculation ===\n")
    base_cap = 1000
    levels = 5
    expanded_cap = manager.estimate_exponential_expansion_capacity(base_cap, levels)
    print(f"Base Capacity: {base_cap}")
    print(f"After {levels} exponential expansions: {expanded_cap:.0f}")
    
    # 協同容量倍數
    print("\n=== Synergistic Capacity Multiplier ===\n")
    for num_tiers in range(1, 6):
        multiplier = manager.estimate_synergistic_capacity_multiplier(num_tiers)
        print(f"{num_tiers} tiers synergy: {multiplier:.2f}x")
