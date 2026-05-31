#!/usr/bin/env python3
"""
自動修復系統數據記錄和追蹤
Auto-Repair System Data Logging & Tracking
完整數據支持模塊 - 詳細記錄所有修復操作
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class RepairEventType(Enum):
    """修復事件類型"""
    FAULT_DETECTED = "fault_detected"
    REPAIR_INITIATED = "repair_initiated"
    REPAIR_IN_PROGRESS = "repair_in_progress"
    REPAIR_SUCCESS = "repair_success"
    REPAIR_FAILED = "repair_failed"
    REPAIR_ROLLED_BACK = "repair_rolled_back"
    AUTO_HEALING_TRIGGERED = "auto_healing_triggered"
    PREDICTIVE_REPAIR = "predictive_repair"
    COMPONENT_RECOVERED = "component_recovered"


class ComponentType(Enum):
    """組件類型"""
    FAULT_TOLERANCE = "fault_tolerance"
    ERROR_CORRECTION = "error_correction"
    SELF_EVOLUTION = "self_evolution"
    AGENT = "agent"
    ORCHESTRATOR = "orchestrator"


@dataclass
class RepairEvent:
    """修復事件記錄"""
    timestamp: str
    event_type: str
    component_type: str
    component_id: str
    severity: str  # low, medium, high, critical
    description: str
    fault_description: Optional[str] = None
    repair_action: Optional[str] = None
    repair_duration_ms: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    data_backup: Optional[Dict[str, Any]] = None
    recovery_metrics: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """轉換為JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


@dataclass
class ComponentRepairHistory:
    """單個組件的修復歷史"""
    component_id: str
    component_type: str
    total_faults: int = 0
    total_repairs: int = 0
    successful_repairs: int = 0
    failed_repairs: int = 0
    average_repair_time_ms: float = 0.0
    last_repair_timestamp: Optional[str] = None
    repair_events: List[RepairEvent] = field(default_factory=list)
    
    def add_event(self, event: RepairEvent):
        """添加修復事件"""
        self.repair_events.append(event)
        if event.event_type == RepairEventType.FAULT_DETECTED.value:
            self.total_faults += 1
        elif event.event_type == RepairEventType.REPAIR_INITIATED.value:
            self.total_repairs += 1
        if event.success:
            self.successful_repairs += 1
            self.last_repair_timestamp = event.timestamp
        elif event.success is False:
            self.failed_repairs += 1
    
    def get_success_rate(self) -> float:
        """獲取修復成功率"""
        if self.total_repairs == 0:
            return 0.0
        return (self.successful_repairs / self.total_repairs) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        recent = list(self.repair_events)[-5:] if hasattr(self.repair_events, '__len__') else self.repair_events[-5:]
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "total_faults": self.total_faults,
            "total_repairs": self.total_repairs,
            "successful_repairs": self.successful_repairs,
            "failed_repairs": self.failed_repairs,
            "success_rate_percent": self.get_success_rate(),
            "average_repair_time_ms": self.average_repair_time_ms,
            "last_repair_timestamp": self.last_repair_timestamp,
            "recent_events": [e.to_dict() for e in recent]
        }


@dataclass
class SystemRepairMetrics:
    """系統級修復指標"""
    timestamp: str
    total_components_monitored: int = 0
    components_with_faults: int = 0
    active_repairs: int = 0
    completed_repairs_session: int = 0
    total_repair_time_ms: float = 0.0
    auto_repair_success_rate: float = 0.0
    predictive_repairs_triggered: int = 0
    auto_healing_events: int = 0
    rollbacks_required: int = 0
    
    component_histories: Dict[str, ComponentRepairHistory] = field(default_factory=dict)
    
    def add_component(self, component_id: str, component_type: str):
        """添加組件"""
        if component_id not in self.component_histories:
            self.component_histories[component_id] = ComponentRepairHistory(
                component_id=component_id,
                component_type=component_type
            )
            self.total_components_monitored += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """獲取摘要"""
        return {
            "timestamp": self.timestamp,
            "total_components_monitored": self.total_components_monitored,
            "components_with_faults": self.components_with_faults,
            "active_repairs": self.active_repairs,
            "completed_repairs_session": self.completed_repairs_session,
            "total_repair_time_ms": self.total_repair_time_ms,
            "auto_repair_success_rate": self.auto_repair_success_rate,
            "predictive_repairs_triggered": self.predictive_repairs_triggered,
            "auto_healing_events": self.auto_healing_events,
            "rollbacks_required": self.rollbacks_required
        }


class AutoRepairDataLogger:
    """自動修復系統數據記錄器"""
    
    def __init__(self, log_dir: str = "logs/auto_repair"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics = SystemRepairMetrics(timestamp=datetime.now().isoformat())
        self.event_log_file = self.log_dir / "repair_events.jsonl"
        self.metrics_log_file = self.log_dir / "repair_metrics.json"
        self.history_file = self.log_dir / "component_history.json"
        
        # 緩衝寫入器: 累積事件每 N 條或每 T 秒 flush
        self._event_buffer: List[str] = []
        self._buffer_max = 50
        self._file_handle = None
        
        logger.info(f"✅ AutoRepairDataLogger initialized at {self.log_dir}")
    
    def _flush_buffer(self):
        if not self._event_buffer:
            return
        try:
            if self._file_handle is None:
                self._file_handle = open(self.event_log_file, 'a', encoding='utf-8')
            self._file_handle.write(''.join(self._event_buffer))
            self._file_handle.flush()
            self._event_buffer.clear()
        except Exception as e:
            logger.error(f"❌ Failed to flush event buffer: {e}")
    
    def log_repair_event(self, event: RepairEvent):
        """記錄修復事件到文件 (緩衝寫入)"""
        try:
            self._event_buffer.append(event.to_json() + "\n")
            if len(self._event_buffer) >= self._buffer_max:
                self._flush_buffer()
            
            # 更新指標
            if event.component_id in self.metrics.component_histories:
                self.metrics.component_histories[event.component_id].add_event(event)
            
            logger.debug(f"✅ Event logged: {event.event_type} for {event.component_id}")
        except Exception as e:
            logger.error(f"❌ Failed to log event: {e}")

    def __del__(self):
        self._flush_buffer()
        if self._file_handle:
            self._file_handle.close()
    
    def save_metrics(self):
        """保存系統指標"""
        try:
            with open(self.metrics_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics.get_summary(), f, indent=2, ensure_ascii=False)
            logger.debug("✅ Metrics saved")
        except Exception as e:
            logger.error(f"❌ Failed to save metrics: {e}")
    
    def save_history(self):
        """保存組件歷史"""
        try:
            history_data = {
                component_id: history.to_dict()
                for component_id, history in self.metrics.component_histories.items()
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            logger.debug("✅ Component history saved")
        except Exception as e:
            logger.error(f"❌ Failed to save history: {e}")
    
    def get_component_repair_history(self, component_id: str) -> Optional[ComponentRepairHistory]:
        """獲取組件修復歷史"""
        return self.metrics.component_histories.get(component_id)
    
    def get_all_repair_events(self, component_id: Optional[str] = None) -> List[RepairEvent]:
        """獲取所有修復事件 (使用緩存)"""
        try:
            self._flush_buffer()
            if not hasattr(self, '_event_cache'):
                self._event_cache = []
                if self.event_log_file.exists():
                    with open(self.event_log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                self._event_cache.append(RepairEvent(**json.loads(line)))
            events = self._event_cache
            if component_id is not None:
                return [e for e in events if e.component_id == component_id]
            return list(events)
        except Exception as e:
            logger.error(f"❌ Failed to read events: {e}")
            return []
    
    def generate_repair_report(self) -> str:
        """生成修復報告"""
        report = "\n" + "="*80 + "\n"
        report += "🔧 自動修復系統詳細報告 (Auto-Repair System Detailed Report)\n"
        report += "="*80 + "\n"
        
        # 系統級摘要
        summary = self.metrics.get_summary()
        report += "\n📊 系統級指標:\n"
        report += f"  時間戳: {summary['timestamp']}\n"
        report += f"  監控組件總數: {summary['total_components_monitored']}\n"
        report += f"  故障組件數: {summary['components_with_faults']}\n"
        report += f"  當前活躍修復: {summary['active_repairs']}\n"
        report += f"  本次會話完成修復: {summary['completed_repairs_session']}\n"
        report += f"  總修復時間: {summary['total_repair_time_ms']}ms\n"
        report += f"  自動修復成功率: {summary['auto_repair_success_rate']:.2f}%\n"
        report += f"  預測修復觸發: {summary['predictive_repairs_triggered']}\n"
        report += f"  自動治愈事件: {summary['auto_healing_events']}\n"
        report += f"  所需回滾: {summary['rollbacks_required']}\n"
        
        # 組件級詳情
        report += "\n🔍 組件級詳情:\n"
        for component_id, history in self.metrics.component_histories.items():
            report += f"\n  [{history.component_type}] {component_id}\n"
            report += f"    故障總數: {history.total_faults}\n"
            report += f"    修復總數: {history.total_repairs}\n"
            report += f"    成功修復: {history.successful_repairs}\n"
            report += f"    失敗修復: {history.failed_repairs}\n"
            report += f"    修復成功率: {history.get_success_rate():.2f}%\n"
            report += f"    平均修復時間: {history.average_repair_time_ms:.2f}ms\n"
        
        report += "\n" + "="*80 + "\n"
        return report
    
    def print_report(self):
        """打印修復報告"""
        print(self.generate_repair_report())


def create_sample_repair_events():
    """創建示例修復事件"""
    logger.info("🔧 Creating sample repair events for demonstration...")
    
    logger = AutoRepairDataLogger()
    
    # 示例事件1: 容錯系統故障和修復
    event1 = RepairEvent(
        timestamp=datetime.now().isoformat(),
        event_type=RepairEventType.FAULT_DETECTED.value,
        component_type=ComponentType.FAULT_TOLERANCE.value,
        component_id="ft_system_01",
        severity="high",
        description="High memory usage detected in fault tolerance system",
        fault_description="Memory usage exceeded 85%"
    )
    logger.log_repair_event(event1)
    
    # 示例事件2: 自動修復啟動
    event2 = RepairEvent(
        timestamp=datetime.now().isoformat(),
        event_type=RepairEventType.REPAIR_INITIATED.value,
        component_type=ComponentType.FAULT_TOLERANCE.value,
        component_id="ft_system_01",
        severity="high",
        description="Auto-repair initiated for fault tolerance system",
        repair_action="memory_cleanup_and_restart"
    )
    logger.log_repair_event(event2)
    
    # 示例事件3: 修復成功
    event3 = RepairEvent(
        timestamp=datetime.now().isoformat(),
        event_type=RepairEventType.REPAIR_SUCCESS.value,
        component_type=ComponentType.FAULT_TOLERANCE.value,
        component_id="ft_system_01",
        severity="high",
        description="Fault tolerance system recovered successfully",
        repair_action="memory_cleanup_and_restart",
        repair_duration_ms=2345.5,
        success=True,
        recovery_metrics={
            "memory_usage_before": "85%",
            "memory_usage_after": "42%",
            "downtime_ms": 2345.5,
            "services_recovered": 3
        }
    )
    logger.log_repair_event(event3)
    
    # 添加組件並保存
    logger.metrics.add_component("ft_system_01", ComponentType.FAULT_TOLERANCE.value)
    logger.metrics.add_component("ec_system_01", ComponentType.ERROR_CORRECTION.value)
    logger.metrics.add_component("se_system_01", ComponentType.SELF_EVOLUTION.value)
    
    logger.save_metrics()
    logger.save_history()
    logger.print_report()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_sample_repair_events()
