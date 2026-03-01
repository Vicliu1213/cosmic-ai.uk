#!/usr/bin/env python3
"""
智能代理系統
基於量子增強的多代理協作平台
"""

import numpy as np
import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

class AgentType(Enum):
    """代理類型枚舉"""
    QUANTUM_ANALYST = "quantum_analyst"
    DATA_OPTIMIZER = "data_optimizer"
    SYSTEM_MONITOR = "system_monitor"
    LEARNING_ADVISOR = "learning_advisor"
    SECURITY_GUARDIAN = "security_guardian"

class AgentState(Enum):
    """代理狀態枚舉"""
    IDLE = "idle"
    ACTIVE = "active"
    THINKING = "thinking"
    COMMUNICATING = "communicating"
    LEARNING = "learning"
    ERROR = "error"

@dataclass
class Message:
    """代理間通信消息"""
    id: str
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 1
    quantum_signature: Optional[str] = None

@dataclass
class AgentCapability:
    """代理能力定義"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    confidence_level: float
    energy_cost: float
    quantum_enhanced: bool = False

@dataclass
class Agent:
    """智能代理基礎類"""
    id: str
    agent_type: AgentType
    name: str
    capabilities: List[AgentCapability]
    state: AgentState = AgentState.IDLE
    memory: Dict[str, Any] = field(default_factory=dict)
    message_queue: List[Message] = field(default_factory=list)
    relationships: Dict[str, float] = field(default_factory=dict)
    last_update: Optional[datetime] = None
    
    # Quantum properties
    quantum_coherence: float = 0.0
    entanglement_partners: List[str] = field(default_factory=list)
    superposition_states: int = 1
    
    # Self-evolution properties
    error_count: int = 0
    success_count: int = 0
    evolution_confidence: float = 0.5
    strategy_weights: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.1
    saturation_level: float = 0.0
    last_evolution: Optional[datetime] = None
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)

class IntelligentAgentSystem:
    """智能代理系統管理器"""
    
    def __init__(self, config_path: str = "data/agents/agents_config.yaml"):
        self.config = self._load_config(config_path)
        self.agents: Dict[str, Agent] = {}
        self.message_bus: List[Message] = []
        self.system_log = []
        self.quantum_network = {}
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入代理系統配置"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            'system': {
                'max_agents': 20,
                'message_ttl': 3600,  # seconds
                'communication_protocol': 'quantum_entangled',
                'synchronization_interval': 1000  # ms
            },
            'agents': {
                'quantum_analyst': {'count': 3, 'priority': 'high'},
                'data_optimizer': {'count': 2, 'priority': 'medium'},
                'system_monitor': {'count': 4, 'priority': 'critical'},
                'learning_advisor': {'count': 2, 'priority': 'medium'},
                'security_guardian': {'count': 1, 'priority': 'critical'}
            },
            'quantum_network': {
                'coherence_threshold': 0.85,
                'entanglement_depth': 4,
                'superposition_capacity': 8
            }
        }
        
    def initialize_agents(self) -> None:
        """初始化所有代理"""
        agent_configs = self.config['agents']
        
        for agent_type_name, config in agent_configs.items():
            agent_type = AgentType(agent_type_name)
            count = config['count']
            priority = config.get('priority', 'medium')
            
            for i in range(count):
                agent = self._create_agent(agent_type, i, priority)
                self.agents[agent.id] = agent
                
        self.logger.info(f"Initialized {len(self.agents)} intelligent agents")
        
    def _create_agent(self, agent_type: AgentType, index: int, priority: str) -> Agent:
        """創建單個代理"""
        agent_id = f"{agent_type.value}_{index:02d}"
        name = f"{agent_type.value.replace('_', ' ').title()} {index+1}"
        
        capabilities = self._generate_capabilities(agent_type)
        
        agent = Agent(
            id=agent_id,
            agent_type=agent_type,
            name=name,
            capabilities=capabilities
        )
        
        # 設置量子屬性
        if priority == 'critical':
            agent.quantum_coherence = 0.95
            agent.superposition_states = 4
        elif priority == 'high':
            agent.quantum_coherence = 0.85
            agent.superposition_states = 3
        else:
            agent.quantum_coherence = 0.75
            agent.superposition_states = 2
            
        return agent
        
    def _generate_capabilities(self, agent_type: AgentType) -> List[AgentCapability]:
        """生成代理能力"""
        capability_map = {
            AgentType.QUANTUM_ANALYST: [
                AgentCapability(
                    name="quantum_analysis",
                    description="Perform quantum advantage analysis",
                    input_types=["numerical_data", "parameters"],
                    output_types=["analysis_result", "quantum_metrics"],
                    confidence_level=0.9,
                    energy_cost=0.3,
                    quantum_enhanced=True
                ),
                AgentCapability(
                    name="theory_validation",
                    description="Validate physical theories",
                    input_types=["theory_spec", "test_data"],
                    output_types=["validation_result"],
                    confidence_level=0.85,
                    energy_cost=0.2,
                    quantum_enhanced=True
                )
            ],
            AgentType.DATA_OPTIMIZER: [
                AgentCapability(
                    name="data_compression",
                    description="Optimize data storage and compression",
                    input_types=["raw_data", "metadata"],
                    output_types=["compressed_data", "compression_metrics"],
                    confidence_level=0.88,
                    energy_cost=0.25
                ),
                AgentCapability(
                    name="storage_optimization",
                    description="Optimize storage algorithms",
                    input_types=["storage_patterns", "access_logs"],
                    output_types=["optimization_plan"],
                    confidence_level=0.82,
                    energy_cost=0.2
                )
            ],
            AgentType.SYSTEM_MONITOR: [
                AgentCapability(
                    name="performance_monitoring",
                    description="Monitor system performance metrics",
                    input_types=["system_metrics", "logs"],
                    output_types=["performance_report", "alerts"],
                    confidence_level=0.95,
                    energy_cost=0.15
                ),
                AgentCapability(
                    name="anomaly_detection",
                    description="Detect system anomalies",
                    input_types=["behavioral_patterns", "metrics"],
                    output_types=["anomaly_report"],
                    confidence_level=0.9,
                    energy_cost=0.2
                )
            ],
            AgentType.LEARNING_ADVISOR: [
                AgentCapability(
                    name="adaptive_learning",
                    description="Provide learning recommendations",
                    input_types=["performance_data", "learning_history"],
                    output_types=["learning_plan", "recommendations"],
                    confidence_level=0.85,
                    energy_cost=0.18
                )
            ],
            AgentType.SECURITY_GUARDIAN: [
                AgentCapability(
                    name="security_monitoring",
                    description="Monitor and ensure system security",
                    input_types=["access_logs", "system_events"],
                    output_types=["security_report", "threat_alerts"],
                    confidence_level=0.92,
                    energy_cost=0.25
                ),
                AgentCapability(
                    name="threat_response",
                    description="Respond to security threats",
                    input_types=["threat_intelligence", "security_events"],
                    output_types=["response_actions"],
                    confidence_level=0.88,
                    energy_cost=0.3
                )
            ]
        }
        
        return capability_map.get(agent_type, [])
        
    async def start_agents(self) -> None:
        """啟動所有代理"""
        tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(self._run_agent_loop(agent))
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        
    async def _run_agent_loop(self, agent: Agent) -> None:
        """運行代理主循環"""
        while True:
            try:
                # 檢查消息隊列
                if agent.message_queue:
                    await self._process_messages(agent)
                    
                # 執行代理特定任務
                await self._execute_agent_tasks(agent)
                    
                # 量子協調
                await self._quantum_coordination(agent)
                
                # 短暫休眠
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Agent {agent.id} error: {e}")
                agent.state = AgentState.ERROR
                
    async def _process_messages(self, agent: Agent) -> None:
        """處理代理消息"""
        messages = agent.message_queue.copy()
        agent.message_queue.clear()
        
        for message in messages:
            if message.receiver == agent.id:
                await self._handle_message(agent, message)
                
    async def _handle_message(self, agent: Agent, message: Message) -> None:
        """處理單個消息"""
        agent.state = AgentState.THINKING
        
        # 基於消息類型執行相應處理
        if message.message_type == "task_request":
            await self._handle_task_request(agent, message)
        elif message.message_type == "data_share":
            await self._handle_data_share(agent, message)
        elif message.message_type == "quantum_entanglement":
            await self._handle_quantum_entanglement(agent, message)
            
        agent.state = AgentState.IDLE
        
    async def _execute_agent_tasks(self, agent: Agent) -> None:
        """執行代理特定任務"""
        if agent.agent_type == AgentType.QUANTUM_ANALYST:
            await self._quantum_analysis_task(agent)
        elif agent.agent_type == AgentType.DATA_OPTIMIZER:
            await self._data_optimization_task(agent)
        elif agent.agent_type == AgentType.SYSTEM_MONITOR:
            await self._system_monitoring_task(agent)
            
    async def _quantum_analysis_task(self, agent: Agent) -> None:
        """量子分析任務"""
        agent.state = AgentState.ACTIVE
        
        # 模擬量子分析
        await asyncio.sleep(0.5)
        
        # 生成分析結果
        analysis_result = {
            'agent_id': agent.id,
            'analysis_type': 'quantum_advantage',
            'quantum_metrics': {
                'coherence': agent.quantum_coherence,
                'entanglement_strength': np.random.random(),
                'superposition_states': agent.superposition_states
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # 分享結果給其他代理
        await self._broadcast_message(agent.id, "analysis_result", analysis_result)
        
        agent.state = AgentState.IDLE
        
    async def _data_optimization_task(self, agent: Agent) -> None:
        """數據優化任務"""
        agent.state = AgentState.ACTIVE
        
        # 模擬數據優化
        await asyncio.sleep(0.3)
        
        optimization_result = {
            'agent_id': agent.id,
            'optimization_type': 'compression_efficiency',
            'improvement': np.random.uniform(0.1, 0.3),
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_message(agent.id, "optimization_result", optimization_result)
        
        agent.state = AgentState.IDLE
        
    async def _system_monitoring_task(self, agent: Agent) -> None:
        """系統監控任務"""
        agent.state = AgentState.ACTIVE
        
        # 模擬系統監控
        await asyncio.sleep(0.2)
        
        monitoring_data = {
            'agent_id': agent.id,
            'system_health': np.random.uniform(0.8, 1.0),
            'resource_usage': np.random.uniform(0.3, 0.7),
            'timestamp': datetime.now().isoformat()
        }
        
        await self._broadcast_message(agent.id, "system_status", monitoring_data)
        
        agent.state = AgentState.IDLE
        
    async def _quantum_coordination(self, agent: Agent) -> None:
        """量子協調"""
        if agent.entanglement_partners:
            # 量子糾纏協調
            for partner_id in agent.entanglement_partners:
                if partner_id in self.agents:
                    partner = self.agents[partner_id]
                    # 量子同步
                    coherence_avg = (agent.quantum_coherence + partner.quantum_coherence) / 2
                    agent.quantum_coherence = coherence_avg
                    
    async def _broadcast_message(self, sender_id: str, message_type: str, content: Dict[str, Any]) -> None:
        """廣播消息給所有代理"""
        message = Message(
            id=f"msg_{datetime.now().timestamp()}",
            sender=sender_id,
            receiver="all",
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            priority=1
        )
        
        self.message_bus.append(message)
        
        # 添加到所有代理的消息隊列
        for agent in self.agents.values():
            if agent.id != sender_id:
                agent.message_queue.append(message)
                
    def get_system_status(self) -> Dict[str, Any]:
        """獲取代理系統狀態"""
        agent_states = {}
        for agent in self.agents.values():
            if agent.agent_type.value not in agent_states:
                agent_states[agent.agent_type.value] = {
                    'count': 0,
                    'active': 0,
                    'avg_coherence': 0
                }
                
            agent_type_data = agent_states[agent.agent_type.value]
            agent_type_data['count'] += 1
            if agent.state == AgentState.ACTIVE:
                agent_type_data['active'] += 1
            agent_type_data['avg_coherence'] += agent.quantum_coherence
            
        # 計算平均值
        for agent_type_data in agent_states.values():
            if agent_type_data['count'] > 0:
                agent_type_data['avg_coherence'] /= agent_type_data['count']
                
        return {
            'total_agents': len(self.agents),
            'agent_distribution': agent_states,
            'message_bus_size': len(self.message_bus),
            'quantum_network_status': 'active',
            'timestamp': datetime.now().isoformat()
        }
        
    async def _handle_task_request(self, agent: Agent, message: Message) -> None:
        """處理任務請求"""
        try:
            # 執行任務並跟蹤結果
            task_type = message.content.get('task_type', '')
            result = await self._execute_specialized_task(agent, task_type, message.content)
            
            if result:
                agent.success_count += 1
                agent.evolution_confidence = min(0.95, agent.evolution_confidence + 0.05)
            else:
                agent.error_count += 1
                agent.evolution_confidence = max(0.1, agent.evolution_confidence - 0.1)
                
            # 檢查是否需要進化
            await self._check_evolution_trigger(agent)
            
        except Exception as e:
            agent.error_count += 1
            self.logger.error(f"Task request error for {agent.id}: {e}")
            
    async def _handle_data_share(self, agent: Agent, message: Message) -> None:
        """處理數據共享"""
        try:
            shared_data = message.content.get('data', {})
            agent.memory['shared_data'] = shared_data
            agent.success_count += 1
        except Exception as e:
            self.logger.error(f"Data share error for {agent.id}: {e}")
            
    async def _handle_quantum_entanglement(self, agent: Agent, message: Message) -> None:
        """處理量子糾纏"""
        try:
            entangle_target = message.content.get('target_agent', '')
            if entangle_target in self.agents:
                agent.entanglement_partners.append(entangle_target)
                agent.success_count += 1
        except Exception as e:
            self.logger.error(f"Quantum entanglement error for {agent.id}: {e}")
            
    async def _execute_specialized_task(self, agent: Agent, task_type: str, content: Dict[str, Any]) -> bool:
        """執行專門化任務"""
        await asyncio.sleep(0.05)
        return np.random.random() > 0.2  # 80% 成功率
        
    async def _check_evolution_trigger(self, agent: Agent) -> None:
        """檢查是否觸發進化 (改進的觸發條件)"""
        # 改進的觸發閾值 - 更容易被激發
        total_attempts = agent.success_count + agent.error_count
        
        if total_attempts > 0:
            success_rate = agent.success_count / total_attempts
            saturation = min(1.0, agent.success_count / 100.0)
            agent.saturation_level = saturation
            
            # 改進的觸發邏輯 - 降低門檻 (從95% && AND 改為 OR 組合)
            trigger_confidence = agent.evolution_confidence > 0.6  # 降低從 0.95
            trigger_success_rate = success_rate > 0.65  # 降低從隱含的更高值
            trigger_low_saturation = saturation < 0.8  # 改進的飽和度檢查
            
            should_evolve = (trigger_confidence and trigger_success_rate) or (trigger_success_rate and trigger_low_saturation)
            
            if should_evolve:
                await self._evolve_agent(agent)
                
    async def _evolve_agent(self, agent: Agent) -> None:
        """進化代理策略 (添加反饋迴路和改進的激活函數)"""
        try:
            agent.state = AgentState.LEARNING
            
            # 改進的激活函數 (從 sigmoid 改為 ReLU + 縮放)
            activation_value = max(0, agent.evolution_confidence - 0.5) * 2.0  # ReLU-like
            
            # 更新策略權重 (反饋迴路)
            if 'primary_strategy' not in agent.strategy_weights:
                agent.strategy_weights['primary_strategy'] = 0.5
                agent.strategy_weights['fallback_strategy'] = 0.3
                agent.strategy_weights['innovative_strategy'] = 0.2
                
            # 根據成功率增強成功的策略權重
            success_rate = agent.success_count / max(1, agent.success_count + agent.error_count)
            weight_increase = activation_value * success_rate * agent.learning_rate
            
            agent.strategy_weights['primary_strategy'] = min(0.95, agent.strategy_weights['primary_strategy'] + weight_increase)
            agent.strategy_weights['innovative_strategy'] = min(0.3, agent.strategy_weights['innovative_strategy'] + weight_increase * 0.3)
            
            # 歸一化權重
            total_weight = sum(agent.strategy_weights.values())
            if total_weight > 0:
                for key in agent.strategy_weights:
                    agent.strategy_weights[key] /= total_weight
                    
            # 進化信息記錄
            agent.last_evolution = datetime.now()
            agent.evolution_history.append({
                'timestamp': datetime.now().isoformat(),
                'confidence': agent.evolution_confidence,
                'success_rate': success_rate,
                'weights': agent.strategy_weights.copy()
            })
            
            # 嘗試多代理協作學習
            await self._cooperative_learn(agent)
            
            # 自適應學習率
            agent.learning_rate = max(0.01, min(0.5, agent.learning_rate * (0.9 + success_rate * 0.2)))
            
            agent.state = AgentState.IDLE
            self.logger.info(f"Agent {agent.id} evolved: confidence={agent.evolution_confidence:.3f}, success_rate={success_rate:.3f}")
            
        except Exception as e:
            self.logger.error(f"Evolution error for {agent.id}: {e}")
            agent.state = AgentState.ERROR
            
    async def _cooperative_learn(self, agent: Agent) -> None:
        """多代理協作學習"""
        try:
            # 與糾纏伙伴分享學習成果
            for partner_id in agent.entanglement_partners:
                if partner_id in self.agents:
                    partner = self.agents[partner_id]
                    
                    # 從成功的夥伴那裡學習
                    if partner.evolution_confidence > agent.evolution_confidence:
                        agent.strategy_weights['innovative_strategy'] += 0.05
                        agent.learning_rate = min(0.5, agent.learning_rate + 0.02)
                        
        except Exception as e:
            self.logger.error(f"Cooperative learning error for {agent.id}: {e}")