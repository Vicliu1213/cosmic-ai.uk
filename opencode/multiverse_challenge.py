#!/usr/bin/env python3
"""
多宇宙挑戰系統 - Multiverse Challenge System
多個並行宇宙，每個宇宙有獨立的市場狀態，但所有智能體共享記憶與知識

Multiverse Trading Challenge:
- 16 parallel universes with independent market states
- Shared memory system across all universes
- Multi-agent knowledge exchange & learning
- Cosmos-scale intelligence coordination
"""

import logging
import asyncio
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import numpy as np

from .agent_memory import (
    EnhancedMemorySystem,
    AgentMemoryManager,
    KnowledgeType,
    MemoryType,
)
from .universal_agent import UniversalAgent, AgentRole, AgentState
from .skills import SkillRegistry, BaseSkill

logger = logging.getLogger(__name__)


class UniverseType(Enum):
    """宇宙類型 - Universe Types"""
    BULL_MARKET = "bull_market"           # 牛市
    BEAR_MARKET = "bear_market"           # 熊市
    VOLATILE = "volatile"                 # 高波動
    STABLE = "stable"                     # 穩定
    RECOVERING = "recovering"             # 恢復中
    CORRECTION = "correction"             # 回調
    SIDEWAYS = "sideways"                 # 震蕩
    CRASH = "crash"                       # 崩盤


@dataclass
class UniverseState:
    """單個宇宙的市場狀態 - Single Universe Market State"""
    universe_id: int
    universe_type: UniverseType
    timestamp: datetime
    
    # 市場數據
    price: float                           # 當前價格
    volatility: float                      # 波動率
    trend: float                           # 趨勢強度 (-1 to 1)
    momentum: float                        # 動量
    
    # 風險指標
    drawdown: float                        # 最大回撤
    recovery_factor: float                 # 恢復因子
    sharpe_ratio: float                    # 夏普比率
    
    # 智能體活動
    active_agents: int = 0
    total_trades: int = 0
    avg_profit: float = 0.0
    max_profit: float = 0.0
    max_loss: float = 0.0
    
    # 宇宙特性
    difficulty_level: float = 0.5          # 難度等級 (0.0-1.0)
    anomaly_factor: float = 0.0            # 異常因子
    liquidity: float = 1.0                 # 流動性


@dataclass
class MultiverseAgent:
    """多宇宙智能體 - Multiverse Agent"""
    agent_id: str
    universe_ids: Set[int]                 # 可訪問的宇宙集合
    role: AgentRole
    
    # 記憶系統
    memory: EnhancedMemorySystem
    
    # 績效追蹤
    total_profit: float = 0.0
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    
    # 宇宙特定的狀態
    universe_states: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    
    # 策略統計
    strategy_confidence: Dict[str, float] = field(default_factory=dict)
    learned_patterns: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_success_rate(self) -> float:
        """計算成功率"""
        if self.total_trades == 0:
            return 0.0
        return self.successful_trades / self.total_trades
    
    def get_avg_profit(self) -> float:
        """計算平均利潤"""
        if self.total_trades == 0:
            return 0.0
        return self.total_profit / self.total_trades


@dataclass
class CrossUniverseKnowledge:
    """跨宇宙知識 - Cross-Universe Knowledge"""
    knowledge_id: str
    knowledge_type: KnowledgeType
    
    # 知識內容
    content: Dict[str, Any]
    confidence: float
    
    # 來源追蹤
    source_agent: str
    source_universes: Set[int]
    
    # 應用統計
    applied_count: int = 0
    success_count: int = 0
    
    def get_effectiveness(self) -> float:
        """計算知識的有效性"""
        if self.applied_count == 0:
            return 0.0
        return self.success_count / self.applied_count


class MultiverseChallenge:
    """多宇宙交易挑戰系統 - Multiverse Trading Challenge System"""
    
    def __init__(self, num_universes: int = 16, num_agents: int = 16):
        """初始化多宇宙系統
        
        Args:
            num_universes: 宇宙數量 (默認 16)
            num_agents: 智能體數量 (默認 16)
        """
        self.num_universes = num_universes
        self.num_agents = num_agents
        
        # 宇宙管理
        self.universes: Dict[int, UniverseState] = {}
        
        # 智能體管理
        self.agents: Dict[str, MultiverseAgent] = {}
        
        # 共享記憶與知識
        self.memory_manager = AgentMemoryManager()
        
        # 跨宇宙知識庫
        self.cross_universe_knowledge: Dict[str, CrossUniverseKnowledge] = {}
        
        # 績效追蹤
        self.global_stats = {
            'total_trades': 0,
            'total_profit': 0.0,
            'universe_performance': {},
            'agent_performance': {},
            'knowledge_effectiveness': {},
        }
        
        # 初始化
        self._initialize_universes()
        self._initialize_agents()
        
        logger.info(f"✅ MultiverseChallenge initialized with {num_universes} universes and {num_agents} agents")
    
    def _initialize_universes(self):
        """初始化所有宇宙"""
        universe_types = list(UniverseType)
        base_price = 100.0
        
        for i in range(self.num_universes):
            universe_type = universe_types[i % len(universe_types)]
            
            # 基於宇宙類型生成市場狀態
            if universe_type == UniverseType.BULL_MARKET:
                price = base_price * (1 + np.random.uniform(0.05, 0.15))
                trend = np.random.uniform(0.6, 1.0)
                volatility = np.random.uniform(0.1, 0.2)
            elif universe_type == UniverseType.BEAR_MARKET:
                price = base_price * (1 - np.random.uniform(0.05, 0.15))
                trend = np.random.uniform(-1.0, -0.6)
                volatility = np.random.uniform(0.15, 0.25)
            elif universe_type == UniverseType.VOLATILE:
                price = base_price * (1 + np.random.uniform(-0.1, 0.1))
                trend = np.random.uniform(-0.3, 0.3)
                volatility = np.random.uniform(0.3, 0.5)
            elif universe_type == UniverseType.STABLE:
                price = base_price
                trend = np.random.uniform(-0.1, 0.1)
                volatility = np.random.uniform(0.05, 0.1)
            elif universe_type == UniverseType.RECOVERING:
                price = base_price * (1 + np.random.uniform(0.02, 0.08))
                trend = np.random.uniform(0.3, 0.7)
                volatility = np.random.uniform(0.12, 0.2)
            elif universe_type == UniverseType.CORRECTION:
                price = base_price * (1 - np.random.uniform(0.02, 0.08))
                trend = np.random.uniform(-0.5, -0.1)
                volatility = np.random.uniform(0.15, 0.25)
            elif universe_type == UniverseType.SIDEWAYS:
                price = base_price
                trend = np.random.uniform(-0.05, 0.05)
                volatility = np.random.uniform(0.08, 0.15)
            else:  # CRASH
                price = base_price * (1 - np.random.uniform(0.2, 0.4))
                trend = -0.9
                volatility = np.random.uniform(0.4, 0.6)
            
            universe_state = UniverseState(
                universe_id=i,
                universe_type=universe_type,
                timestamp=datetime.now(timezone.utc),
                price=price,
                volatility=volatility,
                trend=trend,
                momentum=np.random.uniform(-1.0, 1.0),
                drawdown=np.random.uniform(0, 0.3),
                recovery_factor=np.random.uniform(0.5, 2.0),
                sharpe_ratio=np.random.uniform(-2.0, 3.0),
                difficulty_level=0.5 + volatility,
                anomaly_factor=np.random.uniform(0, 0.2),
                liquidity=np.random.uniform(0.5, 2.0),
            )
            
            self.universes[i] = universe_state
            self.global_stats['universe_performance'][i] = {
                'type': universe_type.value,
                'trades': 0,
                'profit': 0.0,
            }
    
    def _initialize_agents(self):
        """初始化所有智能體"""
        roles = [AgentRole.EXECUTOR, AgentRole.ANALYZER, AgentRole.MONITOR, AgentRole.COORDINATOR]
        
        for i in range(self.num_agents):
            agent_id = f"multiverse_agent_{i:02d}"
            role = roles[i % len(roles)]
            
            # 每個智能體可訪問多個宇宙
            universe_count = np.random.randint(3, self.num_universes + 1)
            accessible_universes = set(
                np.random.choice(self.num_universes, size=universe_count, replace=False)
            )
            
            # 創建記憶系統
            memory = EnhancedMemorySystem(agent_id)
            
            # 註冊到記憶管理器
            self.memory_manager.register_agent(agent_id)
            
            # 創建智能體
            agent = MultiverseAgent(
                agent_id=agent_id,
                universe_ids=accessible_universes,
                role=role,
                memory=memory,
            )
            
            self.agents[agent_id] = agent
            self.global_stats['agent_performance'][agent_id] = {
                'role': role.value,
                'universes': len(accessible_universes),
                'profit': 0.0,
                'trades': 0,
                'success_rate': 0.0,
            }
            
            logger.debug(f"✅ Agent {agent_id} initialized (role: {role.value}, universes: {len(accessible_universes)})")
    
    async def simulate_step(self, step: int) -> Dict[str, Any]:
        """執行一個模擬步驟
        
        Args:
            step: 步驟號
            
        Returns:
            Dict: 這一步的結果
        """
        step_results = {
            'step': step,
            'timestamp': datetime.now(timezone.utc),
            'universe_updates': {},
            'agent_actions': {},
            'knowledge_exchanges': 0,
        }
        
        # 更新每個宇宙的狀態
        for universe_id, universe_state in self.universes.items():
            self._update_universe_state(universe_id, universe_state)
            step_results['universe_updates'][universe_id] = {
                'price': universe_state.price,
                'trend': universe_state.trend,
                'volatility': universe_state.volatility,
            }
        
        # 每個智能體在其可訪問的宇宙中執行
        for agent_id, agent in self.agents.items():
            agent_action = await self._execute_agent_action(agent, step)
            step_results['agent_actions'][agent_id] = agent_action
        
        # 促進知識交換
        knowledge_exchanges = self._facilitate_knowledge_exchange()
        step_results['knowledge_exchanges'] = knowledge_exchanges
        
        return step_results
    
    def _update_universe_state(self, universe_id: int, universe_state: UniverseState):
        """更新宇宙狀態"""
        # 隨機遊走生成價格變化
        change = np.random.normal(universe_state.trend * 0.01, universe_state.volatility)
        universe_state.price *= (1 + change)
        
        # 更新趨勢和動量
        universe_state.trend = np.clip(
            universe_state.trend + np.random.normal(0, 0.05),
            -1.0,
            1.0
        )
        universe_state.momentum = np.clip(
            universe_state.momentum + np.random.normal(0, 0.1),
            -1.0,
            1.0
        )
        
        # 更新時間戳
        universe_state.timestamp = datetime.now(timezone.utc)
    
    async def _execute_agent_action(self, agent: MultiverseAgent, step: int) -> Dict[str, Any]:
        """執行智能體在其宇宙中的行動"""
        action_result = {
            'agent_id': agent.agent_id,
            'trades': [],
            'knowledge_distilled': False,
            'memories_used': 0,
        }
        
        # 對每個可訪問的宇宙執行交易
        for universe_id in agent.universe_ids:
            universe_state = self.universes[universe_id]
            
            # 召回相關記憶以做出決策
            memories = agent.memory.recall_relevant_memories(
                query_context={'universe_id': universe_id, 'trend': universe_state.trend},
                memory_type=MemoryType.EPISODIC,
                limit=5
            )
            action_result['memories_used'] += len(memories)
            
            # 簡化的交易決策邏輯
            if universe_state.trend > 0.5 and len(memories) > 0:
                # 買入信號
                profit = np.random.normal(2.0, 1.5)
            elif universe_state.trend < -0.5:
                # 賣出信號
                profit = np.random.normal(-1.0, 1.5)
            else:
                # 沒有明確信號
                profit = np.random.normal(0, 0.5)
            
            # 記錄交易
            trade = {
                'universe_id': universe_id,
                'profit': profit,
                'success': profit > 0,
            }
            action_result['trades'].append(trade)
            
            # 更新智能體統計
            agent.total_profit += profit
            agent.total_trades += 1
            if profit > 0:
                agent.successful_trades += 1
            else:
                agent.failed_trades += 1
            
            # 記錄經驗到記憶
            agent.memory.store_experience(
                experience={
                    'universe_id': universe_id,
                    'trend': universe_state.trend,
                    'volatility': universe_state.volatility,
                    'profit': profit,
                    'universe_type': universe_state.universe_type.value,
                },
                importance=min(1.0, abs(profit) / 10.0),
                tags=['trading', universe_state.universe_type.value]
            )
            
            # 更新全局統計
            self.global_stats['universe_performance'][universe_id]['trades'] += 1
            self.global_stats['universe_performance'][universe_id]['profit'] += profit
            self.global_stats['total_trades'] += 1
            self.global_stats['total_profit'] += profit
        
        # 定期進行知識蒸餾
        if step % 10 == 0:
            distilled = agent.memory.distill_knowledge_from_experiences()
            if distilled:
                action_result['knowledge_distilled'] = True
                # 提升信心
                agent.learned_patterns.extend(distilled)
        
        # 更新全局智能體統計
        self.global_stats['agent_performance'][agent.agent_id] = {
            'role': agent.role.value,
            'universes': len(agent.universe_ids),
            'profit': agent.total_profit,
            'trades': agent.total_trades,
            'success_rate': agent.get_success_rate(),
        }
        
        return action_result
    
    def _facilitate_knowledge_exchange(self) -> int:
        """促進智能體間的知識交換"""
        exchanges = 0
        
        # 選擇随機對的智能體進行知識交換
        agents_list = list(self.agents.values())
        
        if len(agents_list) < 2:
            return 0
        
        # 進行 N 次交換
        for _ in range(min(3, len(agents_list) // 2)):
            source, target = np.random.choice(agents_list, size=2, replace=False)
            
            # 源智能體選擇一個知識分享
            if source.learned_patterns:
                knowledge_to_share = np.random.choice(len(source.learned_patterns))
                pattern = source.learned_patterns[knowledge_to_share]
                
                # 目標智能體學習這個知識
                target.memory.store_semantic_knowledge(
                    knowledge_type=KnowledgeType.STRATEGIC,
                    insights={
                        'pattern': pattern,
                        'source_agent': source.agent_id,
                    },
                    evidence={'pattern_count': 1},
                    conditions={}
                )
                
                exchanges += 1
        
        return exchanges
    
    async def run_challenge(self, num_steps: int = 100) -> Dict[str, Any]:
        """運行完整的多宇宙挑戰
        
        Args:
            num_steps: 要運行的步驟數
            
        Returns:
            Dict: 完整的挑戰結果
        """
        logger.info(f"🚀 Starting Multiverse Challenge: {num_steps} steps")
        
        challenge_results = {
            'start_time': datetime.now(timezone.utc),
            'num_steps': num_steps,
            'steps': [],
            'final_stats': {},
        }
        
        for step in range(num_steps):
            step_result = await self.simulate_step(step)
            challenge_results['steps'].append(step_result)
            
            if (step + 1) % 10 == 0:
                logger.info(f"✅ Completed step {step + 1}/{num_steps}")
        
        # 計算最終統計
        challenge_results['final_stats'] = {
            'total_trades': self.global_stats['total_trades'],
            'total_profit': self.global_stats['total_profit'],
            'universes': self.global_stats['universe_performance'],
            'agents': self.global_stats['agent_performance'],
        }
        
        challenge_results['end_time'] = datetime.now(timezone.utc)
        challenge_results['duration'] = (
            challenge_results['end_time'] - challenge_results['start_time']
        ).total_seconds()
        
        logger.info(f"✅ Multiverse Challenge completed in {challenge_results['duration']:.2f}s")
        
        return challenge_results
    
    def get_best_performing_agents(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """獲取表現最好的智能體"""
        agent_profits = [
            (agent_id, agent.get_avg_profit())
            for agent_id, agent in self.agents.items()
        ]
        agent_profits.sort(key=lambda x: x[1], reverse=True)
        return agent_profits[:top_n]
    
    def get_best_performing_universes(self, top_n: int = 5) -> List[Tuple[int, float]]:
        """獲取表現最好的宇宙"""
        universe_profits = [
            (universe_id, stats['profit'])
            for universe_id, stats in self.global_stats['universe_performance'].items()
        ]
        universe_profits.sort(key=lambda x: x[1], reverse=True)
        return universe_profits[:top_n]
    
    def get_summary(self) -> Dict[str, Any]:
        """獲取系統摘要"""
        best_agents = self.get_best_performing_agents(3)
        best_universes = self.get_best_performing_universes(3)
        
        return {
            'num_universes': self.num_universes,
            'num_agents': self.num_agents,
            'total_trades': self.global_stats['total_trades'],
            'total_profit': self.global_stats['total_profit'],
            'avg_profit_per_trade': (
                self.global_stats['total_profit'] / max(1, self.global_stats['total_trades'])
            ),
            'best_agents': best_agents,
            'best_universes': best_universes,
            'agent_count': len(self.agents),
            'universe_count': len(self.universes),
        }


# 便利函數
def create_multiverse_challenge(
    num_universes: int = 16,
    num_agents: int = 16
) -> MultiverseChallenge:
    """快速創建多宇宙挑戰系統"""
    return MultiverseChallenge(num_universes, num_agents)


async def run_multiverse_simulation(
    num_universes: int = 16,
    num_agents: int = 16,
    num_steps: int = 100,
) -> Dict[str, Any]:
    """運行完整的多宇宙模擬"""
    challenge = create_multiverse_challenge(num_universes, num_agents)
    results = await challenge.run_challenge(num_steps)
    
    return {
        'results': results,
        'summary': challenge.get_summary(),
    }
