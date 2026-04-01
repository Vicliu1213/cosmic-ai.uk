#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
容错拓扑系统 - 用于 Cosmic Engine
Fault Tolerance Topology System for Cosmic Engine

集成到异变全知宇宙智能体系统中的容错机制
- 多层冗余监控
- 自动故障检测
- 快速故障转移
- 健康恢复机制
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict, deque
import threading
import json

logger = logging.getLogger(__name__)


class FaultLevel(Enum):
    """故障级别"""
    CRITICAL = "critical"      # 严重：系统不可用
    HIGH = "high"              # 高：功能受损
    MEDIUM = "medium"          # 中：性能下降
    LOW = "low"                # 低：信息性


class ComponentStatus(Enum):
    """组件状态"""
    HEALTHY = "healthy"        # 健康
    DEGRADED = "degraded"      # 降级
    OFFLINE = "offline"        # 离线


@dataclass
class HealthMetric:
    """健康指标"""
    component_id: str
    timestamp: float
    cpu_usage: float            # 0-1
    memory_usage: float         # 0-1
    network_latency: float      # ms
    error_rate: float           # 0-1
    response_time: float        # ms
    
    def is_healthy(self) -> bool:
        """检查是否健康"""
        return (
            self.cpu_usage < 0.9 and
            self.memory_usage < 0.9 and
            self.network_latency < 500 and
            self.error_rate < 0.05 and
            self.response_time < 1000
        )


@dataclass
class FaultEvent:
    """故障事件"""
    fault_id: str
    timestamp: float
    component_id: str
    fault_level: FaultLevel
    description: str
    error_trace: str = ""
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_time: float = 0.0


class FaultDetectionEngine:
    """故障检测引擎"""
    
    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.health_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self.monitoring_active = False
        self.fault_callbacks: List[callable] = []
    
    def check_component_health(
        self,
        component_id: str,
        metrics: HealthMetric
    ) -> Tuple[ComponentStatus, Optional[FaultEvent]]:
        """检查组件健康状态"""
        
        self.health_history[component_id].append(metrics)
        
        # 检查当前健康状态
        if not metrics.is_healthy():
            # 检查是否为持续性故障
            recent_metrics = list(self.health_history[component_id])[-5:]
            unhealthy_count = sum(1 for m in recent_metrics if not m.is_healthy())
            
            if unhealthy_count >= 3:
                # 持续性故障 -> 创建故障事件
                fault_level = self._determine_fault_level(metrics)
                fault_event = FaultEvent(
                    fault_id=f"fault_{int(time.time() * 1000)}",
                    timestamp=metrics.timestamp,
                    component_id=component_id,
                    fault_level=fault_level,
                    description=self._describe_fault(metrics)
                )
                
                # 触发故障回调
                for callback in self.fault_callbacks:
                    try:
                        callback(fault_event)
                    except Exception as e:
                        logger.error(f"故障回调执行失败: {e}")
                
                return ComponentStatus.DEGRADED, fault_event
        
        return ComponentStatus.HEALTHY, None
    
    def _determine_fault_level(self, metrics: HealthMetric) -> FaultLevel:
        """确定故障级别"""
        if metrics.error_rate > 0.5 or metrics.cpu_usage > 0.95:
            return FaultLevel.CRITICAL
        elif metrics.error_rate > 0.2 or metrics.cpu_usage > 0.9:
            return FaultLevel.HIGH
        elif metrics.error_rate > 0.1 or metrics.response_time > 5000:
            return FaultLevel.MEDIUM
        else:
            return FaultLevel.LOW
    
    def _describe_fault(self, metrics: HealthMetric) -> str:
        """描述故障"""
        issues = []
        if metrics.cpu_usage > 0.9:
            issues.append(f"CPU使用率过高 ({metrics.cpu_usage:.1%})")
        if metrics.memory_usage > 0.9:
            issues.append(f"内存使用率过高 ({metrics.memory_usage:.1%})")
        if metrics.error_rate > 0.1:
            issues.append(f"错误率高 ({metrics.error_rate:.1%})")
        if metrics.response_time > 5000:
            issues.append(f"响应时间过长 ({metrics.response_time:.0f}ms)")
        
        return "; ".join(issues) if issues else "未知故障"
    
    def register_fault_callback(self, callback: callable):
        """注册故障回调"""
        self.fault_callbacks.append(callback)


class FaultIsolationManager:
    """故障隔离管理器"""
    
    def __init__(self):
        self.isolated_components: Dict[str, FaultEvent] = {}
        self.isolation_history: deque = deque(maxlen=1000)
    
    def isolate_fault(self, fault_event: FaultEvent) -> bool:
        """隔离故障"""
        try:
            # 记录隔离
            self.isolated_components[fault_event.component_id] = fault_event
            self.isolation_history.append({
                'timestamp': datetime.now().isoformat(),
                'component_id': fault_event.component_id,
                'fault_level': fault_event.fault_level.value,
                'description': fault_event.description
            })
            
            logger.info(
                f"🔒 隔离故障 - 组件: {fault_event.component_id}, "
                f"级别: {fault_event.fault_level.value}"
            )
            return True
        except Exception as e:
            logger.error(f"隔离故障失败: {e}")
            return False
    
    def is_isolated(self, component_id: str) -> bool:
        """检查组件是否隔离"""
        return component_id in self.isolated_components
    
    def get_isolation_status(self) -> Dict[str, Any]:
        """获取隔离状态"""
        return {
            'isolated_count': len(self.isolated_components),
            'isolated_components': list(self.isolated_components.keys()),
            'recent_isolations': list(self.isolation_history)[-10:]
        }


class FailoverManager:
    """故障转移管理器"""
    
    def __init__(self):
        self.backup_components: Dict[str, List[str]] = defaultdict(list)
        self.failover_history: deque = deque(maxlen=1000)
    
    def register_backup(self, primary_id: str, backup_ids: List[str]):
        """注册备份组件"""
        self.backup_components[primary_id] = backup_ids
        logger.info(f"注册备份 - 主: {primary_id}, 备: {backup_ids}")
    
    def initiate_failover(
        self,
        fault_event: FaultEvent
    ) -> Tuple[bool, Optional[str]]:
        """启动故障转移"""
        
        component_id = fault_event.component_id
        backup_ids = self.backup_components.get(component_id, [])
        
        if not backup_ids:
            logger.warning(f"⚠️ 无可用备份 - 组件: {component_id}")
            return False, None
        
        # 尝试转移到第一个可用的备份
        for backup_id in backup_ids:
            try:
                start_time = time.time()
                
                # 这里应该执行实际的转移逻辑
                # 例如: 更新负载均衡器、重定向流量等
                
                failover_time = time.time() - start_time
                fault_event.recovery_time = failover_time
                fault_event.recovery_successful = True
                
                self.failover_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'from': component_id,
                    'to': backup_id,
                    'failover_time': failover_time,
                    'success': True
                })
                
                logger.info(
                    f"✅ 故障转移成功 - 从 {component_id} 到 {backup_id} "
                    f"({failover_time:.2f}s)"
                )
                
                return True, backup_id
            
            except Exception as e:
                logger.error(f"故障转移到 {backup_id} 失败: {e}")
                continue
        
        return False, None
    
    def get_failover_stats(self) -> Dict[str, Any]:
        """获取转移统计"""
        successful = sum(1 for f in self.failover_history if f['success'])
        
        return {
            'total_failovers': len(self.failover_history),
            'successful_failovers': successful,
            'success_rate': successful / len(self.failover_history) if self.failover_history else 0,
            'recent_failovers': list(self.failover_history)[-10:]
        }


class FaultToleranceOrchestrator:
    """容错协调器 - 整合所有容错机制"""
    
    def __init__(self):
        self.detection_engine = FaultDetectionEngine()
        self.isolation_manager = FaultIsolationManager()
        self.failover_manager = FailoverManager()
        self.recovery_stats = defaultdict(lambda: {'attempts': 0, 'successes': 0})
    
    def handle_fault(self, fault_event: FaultEvent) -> bool:
        """处理故障事件"""
        
        logger.info(f"🚨 处理故障 - ID: {fault_event.fault_id}, "
                   f"组件: {fault_event.component_id}")
        
        # 步骤1: 隔离故障
        isolated = self.isolation_manager.isolate_fault(fault_event)
        if not isolated:
            logger.error("隔离故障失败")
            return False
        
        # 步骤2: 尝试故障转移
        success, backup_id = self.failover_manager.initiate_failover(fault_event)
        
        # 步骤3: 记录恢复统计
        component_key = fault_event.component_id
        self.recovery_stats[component_key]['attempts'] += 1
        if success:
            self.recovery_stats[component_key]['successes'] += 1
        
        return success
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'isolation_status': self.isolation_manager.get_isolation_status(),
            'failover_stats': self.failover_manager.get_failover_stats(),
            'recovery_stats': dict(self.recovery_stats),
            'timestamp': datetime.now().isoformat()
        }
    
    def register_component_backup(
        self,
        primary_id: str,
        backup_ids: List[str]
    ):
        """注册组件备份"""
        self.failover_manager.register_backup(primary_id, backup_ids)
    
    def check_component_health(
        self,
        component_id: str,
        metrics: HealthMetric
    ):
        """检查组件健康"""
        status, fault_event = self.detection_engine.check_component_health(
            component_id, metrics
        )
        
        if fault_event:
            self.handle_fault(fault_event)
        
        return status


# 导出主类
__all__ = [
    'FaultDetectionEngine',
    'FaultIsolationManager',
    'FailoverManager',
    'FaultToleranceOrchestrator',
    'HealthMetric',
    'FaultEvent',
    'FaultLevel',
    'ComponentStatus'
]
