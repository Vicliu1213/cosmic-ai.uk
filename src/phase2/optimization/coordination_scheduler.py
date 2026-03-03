#!/usr/bin/env python3
"""
協同調度器 (Coordination Scheduler)
Coordination Scheduler for Cosmic AI Phase 2

統-超指數遞歸協同增長 (Unified Hyper-Exponential Recursive Synergistic Growth)

五個基礎突破之四：協同理論 (Coordination Synergy - Breakthrough #4)

此模塊實現多代理協同、工作流編排、和動態任務調度。
通過協同共振和遞歸任務組合實現指數級系統協同效應。

Key Concepts:
- Multi-agent resonance coordination: 多代理共振協同
- Recursive task composition: 遞歸任務組合
- Synergistic workflow orchestration: 協同工作流編排
- Exponential coordination multiplier: 指數級協同倍數
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import math
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """代理角色枚舉 (Agent Role Enumeration)"""
    COORDINATOR = "coordinator"  # 協調器：主控調度
    PROCESSOR = "processor"  # 處理器：執行任務
    VALIDATOR = "validator"  # 驗證器：質量控制
    OPTIMIZER = "optimizer"  # 優化器：性能優化
    MONITOR = "monitor"  # 監視器：系統監控


class TaskPriority(Enum):
    """任務優先級枚舉 (Task Priority Enumeration)"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    DEFERRED = 5


@dataclass
class CoordinationMetrics:
    """協同指標 (Coordination Metrics)"""
    timestamp: datetime
    total_agents: int
    active_agents: int
    coordination_efficiency: float  # 協同效率 (0-1)
    resonance_level: float  # 共振度 (0-1)
    throughput: float  # 吞吐量 (任務/秒)
    average_latency: float  # 平均延遲 (毫秒)
    synergy_multiplier: float  # 協同倍數
    cascade_depth: int  # 級聯深度


@dataclass
class Task:
    """任務 (Task)"""
    task_id: str
    name: str
    agent_role: AgentRole
    priority: TaskPriority
    required_capacity: float  # 所需容量
    dependencies: List[str] = field(default_factory=list)  # 依賴任務
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    cascade_group: int = 0  # 級聯組編號


@dataclass
class CoordinationState:
    """協同狀態 (Coordination State)"""
    agent_id: str
    role: AgentRole
    is_active: bool
    resonance_level: float  # 與其他代理的共振度 (0-1)
    processed_tasks: int = 0
    average_response_time: float = 0.0  # 毫秒
    last_update: datetime = field(default_factory=datetime.now)
    connected_agents: List[str] = field(default_factory=list)


class ResonanceCoordinator:
    """共振協調器 (Resonance Coordinator)
    
    實現多代理之間的共振同步
    Implement resonance synchronization between multiple agents
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.resonance_frequency = 1.0  # Hz
        self.connected_agents: Dict[str, float] = {}  # agent_id → resonance_level
        self.resonance_history: List[Tuple[datetime, float]] = []

    def add_connection(self, other_agent_id: str) -> None:
        """添加連接 (Add Connection)"""
        self.connected_agents[other_agent_id] = 0.5  # 初始共振度

    def calculate_resonance(self) -> float:
        """計算共振度 (Calculate Resonance Level)"""
        if not self.connected_agents:
            return 0.0
        
        # 共振度 = 所有連接的平均值
        # Resonance = average of all connections
        total_resonance = sum(self.connected_agents.values())
        avg_resonance = total_resonance / len(self.connected_agents)
        
        # 應用共振放大（超指數增長）
        # Apply resonance amplification (hyper-exponential growth)
        amplified_resonance = avg_resonance * (1.0 + 0.5 * len(self.connected_agents))
        
        # 限制在 [0, 1]
        amplified_resonance = min(1.0, amplified_resonance)
        
        self.resonance_history.append((datetime.now(), amplified_resonance))
        return amplified_resonance

    def get_resonance_report(self) -> Dict[str, Any]:
        """獲取共振報告 (Get Resonance Report)"""
        if not self.resonance_history:
            return {"status": "no_data"}
        
        recent = self.resonance_history[-100:]
        resonances = [r for _, r in recent]
        
        return {
            "agent_id": self.agent_id,
            "current_resonance": float(resonances[-1]) if resonances else 0.0,
            "average_resonance": float(np.mean(resonances)),
            "peak_resonance": float(np.max(resonances)),
            "connected_agents": len(self.connected_agents),
            "total_measurements": len(self.resonance_history)
        }


class RecursiveTaskComposer:
    """遞歸任務組合器 (Recursive Task Composer)
    
    通過遞歸組合實現複雜工作流
    Create complex workflows through recursive task composition
    """

    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.composed_tasks: List[List[Task]] = []  # 按級聯級別組織

    def compose_workflow(
        self,
        base_tasks: List[Task],
        composition_depth: int = 1
    ) -> List[Task]:
        """組合工作流 (Compose Workflow)"""
        
        if composition_depth >= self.max_depth:
            return base_tasks
        
        # 每一級創建新的組合任務
        # Create new composed tasks at each level
        composed = []
        
        for level in range(composition_depth):
            # 將前一級的任務作為輸入
            # Use previous level tasks as input
            if level == 0:
                input_tasks = base_tasks
            else:
                input_tasks = composed
            
            # 創建組合任務
            new_composed = []
            for i in range(0, len(input_tasks), 2):
                if i + 1 < len(input_tasks):
                    # 組合兩個任務
                    combined_task = Task(
                        task_id=f"composed_{level}_{i}",
                        name=f"Composed Task Level {level}",
                        agent_role=AgentRole.COORDINATOR,
                        priority=TaskPriority.NORMAL,
                        required_capacity=input_tasks[i].required_capacity + 
                                        input_tasks[i+1].required_capacity,
                        dependencies=[input_tasks[i].task_id, input_tasks[i+1].task_id],
                        cascade_group=level
                    )
                    new_composed.append(combined_task)
            
            composed = new_composed if new_composed else input_tasks
        
        self.composed_tasks.append(composed)
        return composed

    def get_cascade_structure(self) -> List[Dict[str, Any]]:
        """獲取級聯結構 (Get Cascade Structure)"""
        return [
            {
                "level": idx,
                "task_count": len(tasks),
                "total_capacity": sum(t.required_capacity for t in tasks)
            }
            for idx, tasks in enumerate(self.composed_tasks)
        ]


class CoordinationScheduler:
    """協同調度器 (Coordination Scheduler)
    
    統-超指數遞歸協同增長的協同管理核心
    Core coordination management for unified hyper-exponential recursive synergistic growth
    """

    def __init__(self, num_agents: int = 5):
        self.num_agents = num_agents
        self.agents: Dict[str, CoordinationState] = {}
        self.resonance_coordinators: Dict[str, ResonanceCoordinator] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.task_composer = RecursiveTaskComposer()
        self.metrics_history: List[CoordinationMetrics] = []
        
        # 初始化代理
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """初始化代理 (Initialize Agents)"""
        
        roles = [AgentRole.COORDINATOR, AgentRole.PROCESSOR, 
                AgentRole.VALIDATOR, AgentRole.OPTIMIZER, AgentRole.MONITOR]
        
        for i in range(self.num_agents):
            agent_id = f"agent_{i}"
            role = roles[i % len(roles)]
            
            self.agents[agent_id] = CoordinationState(
                agent_id=agent_id,
                role=role,
                is_active=True,
                resonance_level=0.5
            )
            
            self.resonance_coordinators[agent_id] = ResonanceCoordinator(agent_id)
        
        # 建立代理連接
        self._establish_connections()

    def _establish_connections(self) -> None:
        """建立代理連接 (Establish Agent Connections)"""
        for agent_id, coordinator in self.resonance_coordinators.items():
            for other_id in self.agents:
                if other_id != agent_id:
                    coordinator.add_connection(other_id)
                    self.agents[agent_id].connected_agents.append(other_id)

    def schedule_task(self, task: Task) -> bool:
        """調度任務 (Schedule Task)"""
        
        # 檢查依賴是否滿足
        if task.dependencies:
            completed_ids = [t.task_id for t in self.completed_tasks]
            if not all(dep_id in completed_ids for dep_id in task.dependencies):
                logger.warning(f"Task {task.task_id} has unsatisfied dependencies")
                return False
        
        # 尋找合適的代理
        suitable_agent = self._find_suitable_agent(task)
        if not suitable_agent:
            self.task_queue.append(task)  # 放入隊列等待
            return False
        
        task.scheduled_at = datetime.now()
        self.task_queue.append(task)
        logger.info(f"Task {task.task_id} scheduled to {suitable_agent.agent_id}")
        
        return True

    def _find_suitable_agent(self, task: Task) -> Optional[CoordinationState]:
        """尋找合適的代理 (Find Suitable Agent)"""
        
        # 查找角色匹配的活躍代理
        for agent in self.agents.values():
            if agent.is_active and agent.role == task.agent_role:
                return agent
        
        # 備選：查找任何活躍代理
        for agent in self.agents.values():
            if agent.is_active:
                return agent
        
        return None

    def execute_task(self, task: Task) -> bool:
        """執行任務 (Execute Task)"""
        
        task.completed_at = datetime.now()
        task.result = {"status": "completed"}
        
        self.completed_tasks.append(task)
        
        # 更新代理統計
        for agent in self.agents.values():
            if agent.role == task.agent_role:
                agent.processed_tasks += 1
                execution_time = (task.completed_at - task.scheduled_at).total_seconds() * 1000
                agent.average_response_time = (
                    (agent.average_response_time * (agent.processed_tasks - 1) + execution_time) /
                    agent.processed_tasks
                )
        
        return True

    def calculate_coordination_efficiency(self) -> float:
        """計算協同效率 (Calculate Coordination Efficiency)"""
        
        if not self.agents:
            return 0.0
        
        # 效率 = 完成的任務 / 總任務 × 代理參與度
        total_tasks = len(self.completed_tasks) + len(self.task_queue)
        completion_rate = len(self.completed_tasks) / (total_tasks + 1e-10)
        
        active_rate = sum(1 for a in self.agents.values() if a.is_active) / len(self.agents)
        
        efficiency = completion_rate * active_rate
        return min(1.0, efficiency)

    def calculate_synergy_multiplier(self) -> float:
        """計算協同倍數 (Calculate Synergy Multiplier)
        
        基於連接的代理數量計算指數級協同
        Calculate exponential synergy based on connected agents
        """
        
        active_agents = sum(1 for a in self.agents.values() if a.is_active)
        
        # 超指數增長：e^(n-1)
        # Hyper-exponential: e^(n-1)
        exponential_growth = np.exp(active_agents - 1)
        
        # 共振放大：計算平均共振度
        avg_resonance = np.mean([
            coordinator.calculate_resonance()
            for coordinator in self.resonance_coordinators.values()
        ])
        
        # 協同倍數 = 指數增長 × 共振度
        synergy = exponential_growth * (1.0 + avg_resonance)
        
        return float(synergy)

    def record_coordination_metrics(self) -> CoordinationMetrics:
        """記錄協同指標 (Record Coordination Metrics)"""
        
        active_count = sum(1 for a in self.agents.values() if a.is_active)
        avg_latency = np.mean([
            a.average_response_time for a in self.agents.values()
            if a.average_response_time > 0
        ]) if self.agents else 0.0
        
        metrics = CoordinationMetrics(
            timestamp=datetime.now(),
            total_agents=len(self.agents),
            active_agents=active_count,
            coordination_efficiency=self.calculate_coordination_efficiency(),
            resonance_level=np.mean([
                coordinator.calculate_resonance()
                for coordinator in self.resonance_coordinators.values()
            ]),
            throughput=len(self.completed_tasks) / max(1, (
                datetime.now() - self.metrics_history[0].timestamp
            ).total_seconds() if self.metrics_history else 1),
            average_latency=avg_latency,
            synergy_multiplier=self.calculate_synergy_multiplier(),
            cascade_depth=len(self.task_composer.composed_tasks)
        )
        
        self.metrics_history.append(metrics)
        return metrics

    def get_coordination_report(self) -> Dict[str, Any]:
        """獲取協同報告 (Get Coordination Report)"""
        
        if not self.metrics_history:
            return {"status": "no_metrics"}
        
        recent_metrics = self.metrics_history[-50:]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_metrics": len(self.metrics_history),
            "agents": {
                agent_id: {
                    "role": agent.role.value,
                    "active": agent.is_active,
                    "processed_tasks": agent.processed_tasks,
                    "avg_response_time_ms": float(agent.average_response_time),
                    "resonance_level": float(self.resonance_coordinators[agent_id].calculate_resonance())
                }
                for agent_id, agent in self.agents.items()
            },
            "overall": {
                "avg_efficiency": float(np.mean([m.coordination_efficiency for m in recent_metrics])),
                "avg_resonance": float(np.mean([m.resonance_level for m in recent_metrics])),
                "avg_throughput": float(np.mean([m.throughput for m in recent_metrics])),
                "avg_synergy_multiplier": float(np.mean([m.synergy_multiplier for m in recent_metrics])),
                "completed_tasks": len(self.completed_tasks),
                "queued_tasks": len(self.task_queue)
            }
        }


# 示例用法 (Example Usage)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scheduler = CoordinationScheduler(num_agents=5)
    
    print("=== Coordination Scheduler Test ===\n")
    
    # 創建示例任務
    tasks = [
        Task(
            task_id=f"task_{i}",
            name=f"Task {i}",
            agent_role=[AgentRole.PROCESSOR, AgentRole.PROCESSOR, AgentRole.VALIDATOR][i % 3],
            priority=TaskPriority.NORMAL,
            required_capacity=100.0 * (i + 1)
        )
        for i in range(5)
    ]
    
    # 調度並執行任務
    print("Scheduling and executing tasks...\n")
    for task in tasks:
        scheduler.schedule_task(task)
        scheduler.execute_task(task)
        metrics = scheduler.record_coordination_metrics()
        print(f"Task {task.task_id}: Completed")
        print(f"  Synergy Multiplier: {metrics.synergy_multiplier:.2f}x")
    
    # 獲取協同報告
    print("\n=== Coordination Report ===\n")
    report = scheduler.get_coordination_report()
    
    print(f"Total Metrics: {report['total_metrics']}")
    print(f"\nOverall Performance:")
    for key, value in report['overall'].items():
        print(f"  {key}: {value}")
    
    # 代理統計
    print(f"\nAgent Statistics:")
    for agent_id, agent_data in report['agents'].items():
        print(f"\n{agent_id}:")
        print(f"  Role: {agent_data['role']}")
        print(f"  Processed Tasks: {agent_data['processed_tasks']}")
        print(f"  Resonance Level: {agent_data['resonance_level']:.4f}")
