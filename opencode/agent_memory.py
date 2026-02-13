#!/usr/bin/env python3
"""
Enhanced Memory & Context System for OpenCode Agents
OpenCode 代理的增強記憶和上下文系統

Advanced memory management with knowledge distillation, context preservation,
and persistent learning capabilities for agents.
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from collections import OrderedDict, defaultdict

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory in agent cognitive system"""
    SENSORY = "sensory"              # Immediate perception (< 1 second)
    SHORT_TERM = "short_term"        # Working memory (< 30 seconds)
    EPISODIC = "episodic"            # Specific events and experiences
    SEMANTIC = "semantic"            # Facts and knowledge
    PROCEDURAL = "procedural"        # Skills and strategies
    EMOTIONAL = "emotional"          # Performance impact and confidence


class KnowledgeType(Enum):
    """Types of knowledge to distill"""
    STRATEGIC = "strategic"          # Trading strategies, patterns
    TACTICAL = "tactical"            # Immediate actions, tactics
    METACOGNITIVE = "metacognitive"  # Learning about learning
    CAUSAL = "causal"               # Cause-effect relationships
    PATTERN = "pattern"             # Recurring patterns
    EXCEPTION = "exception"         # Edge cases and exceptions


@dataclass
class MemoryEntry:
    """Single memory entry in agent memory"""
    
    entry_id: str
    memory_type: MemoryType
    timestamp: datetime
    content: Dict[str, Any]
    importance_score: float = 0.5    # 0-1, higher = more important
    relevance_score: float = 0.5     # 0-1, relevance to current context
    access_count: int = 0            # How many times accessed
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    
    def update_access(self) -> None:
        """Update access metadata"""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def get_priority(self) -> float:
        """Calculate priority for retention"""
        # Priority = importance × recency × relevance × access_frequency
        recency_factor = 1.0 if self.last_accessed is None else \
            max(0.1, 1.0 - (datetime.now() - self.last_accessed).total_seconds() / 86400)
        return self.importance_score * recency_factor * self.relevance_score * (1 + self.access_count * 0.1)


@dataclass
class ContextFrame:
    """Context frame capturing agent state at a moment"""
    
    frame_id: str
    timestamp: datetime
    agent_id: str
    market_state: Dict[str, Any]     # Current market conditions
    agent_state: Dict[str, Any]      # Agent internal state
    recent_decisions: List[str]      # Recent trading/analysis decisions
    performance_metrics: Dict[str, float]  # Current performance
    active_goals: List[str]          # Current objectives
    constraints: List[str]           # Current constraints
    context_hash: str = ""           # Hash for quick comparison
    
    def compute_hash(self) -> str:
        """Compute hash of context for deduplication"""
        context_str = json.dumps({
            'market': self.market_state,
            'state': self.agent_state,
            'goals': self.active_goals,
        }, sort_keys=True, default=str)
        self.context_hash = hashlib.md5(context_str.encode()).hexdigest()
        return self.context_hash


class DistilledKnowledge:
    """Compressed knowledge representation"""
    
    def __init__(self, knowledge_type: KnowledgeType, confidence: float = 0.8):
        self.knowledge_type = knowledge_type
        self.confidence = confidence
        self.core_insights: List[str] = []
        self.supporting_evidence: Dict[str, Any] = {}
        self.contradictions: List[str] = []
        self.applicability_conditions: Dict[str, Any] = {}
        self.success_rate: float = 0.0
        self.usage_count: int = 0
        self.created_at: datetime = datetime.now()
        self.last_validated: datetime = datetime.now()
    
    def add_insight(self, insight: str, evidence: Dict[str, Any]) -> None:
        """Add a core insight with supporting evidence"""
        self.core_insights.append(insight)
        self.supporting_evidence[insight] = evidence
    
    def validate(self, success: bool, performance_metric: float) -> None:
        """Update knowledge validity based on performance"""
        self.usage_count += 1
        if success:
            self.success_rate = (self.success_rate * (self.usage_count - 1) + performance_metric) / self.usage_count
        else:
            self.success_rate *= 0.95  # Decay on failure
        self.last_validated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'type': self.knowledge_type.value,
            'confidence': self.confidence,
            'insights': self.core_insights,
            'success_rate': self.success_rate,
            'usage_count': self.usage_count,
            'applicability': self.applicability_conditions,
        }


class EnhancedMemorySystem:
    """Complete memory system for agents with knowledge distillation"""
    
    def __init__(
        self,
        agent_id: str,
        max_short_term: int = 100,
        max_episodic: int = 1000,
        knowledge_decay_rate: float = 0.001,
    ):
        self.agent_id = agent_id
        self.max_short_term = max_short_term
        self.max_episodic = max_episodic
        self.knowledge_decay_rate = knowledge_decay_rate
        
        # Memory storage
        self.sensory_memory: OrderedDict = OrderedDict()
        self.short_term_memory: OrderedDict = OrderedDict()
        self.episodic_memory: OrderedDict = OrderedDict()
        self.semantic_memory: Dict[str, DistilledKnowledge] = {}
        self.procedural_memory: Dict[str, Dict[str, Any]] = {}
        self.emotional_memory: Dict[str, float] = defaultdict(float)
        
        # Context tracking
        self.context_history: List[ContextFrame] = []
        self.current_context: Optional[ContextFrame] = None
        
        # Metadata
        self.total_experiences: int = 0
        self.total_decisions: int = 0
        self.creation_time: datetime = datetime.now()
        
        logger.info(f"🧠 Memory system initialized for agent: {agent_id}")
    
    def record_sensory_input(
        self,
        content: Dict[str, Any],
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> str:
        """Record sensory input"""
        entry_id = f"sensory_{len(self.sensory_memory)}"
        entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=MemoryType.SENSORY,
            timestamp=datetime.now(),
            content=content,
            importance_score=importance,
            tags=tags or []
        )
        self.sensory_memory[entry_id] = entry
        
        # Keep only recent sensory data (sliding window)
        if len(self.sensory_memory) > self.max_short_term:
            oldest = next(iter(self.sensory_memory))
            del self.sensory_memory[oldest]
        
        return entry_id
    
    def store_experience(
        self,
        experience: Dict[str, Any],
        importance: float = 0.7,
        tags: Optional[List[str]] = None
    ) -> str:
        """Store episodic memory of experience"""
        entry_id = f"episode_{len(self.episodic_memory)}"
        entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=MemoryType.EPISODIC,
            timestamp=datetime.now(),
            content=experience,
            importance_score=importance,
            tags=tags or []
        )
        self.episodic_memory[entry_id] = entry
        self.total_experiences += 1
        
        # Manage episodic memory size
        if len(self.episodic_memory) > self.max_episodic:
            # Remove lowest priority memories
            priorities = {eid: mem.get_priority() for eid, mem in self.episodic_memory.items()}
            lowest = min(priorities, key=priorities.get)
            del self.episodic_memory[lowest]
        
        return entry_id
    
    def store_semantic_knowledge(
        self,
        knowledge_type: KnowledgeType,
        insights: List[str],
        evidence: Dict[str, Any],
        confidence: float = 0.8,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store distilled semantic knowledge"""
        knowledge_id = f"knowledge_{knowledge_type.value}_{len(self.semantic_memory)}"
        knowledge = DistilledKnowledge(knowledge_type, confidence)
        
        for insight in insights:
            knowledge.add_insight(insight, evidence)
        
        if conditions:
            knowledge.applicability_conditions = conditions
        
        self.semantic_memory[knowledge_id] = knowledge
        logger.info(f"📚 Stored knowledge: {knowledge_id} - {len(insights)} insights")
        
        return knowledge_id
    
    def store_procedure(
        self,
        procedure_name: str,
        steps: List[str],
        success_rate: float = 0.0,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store procedural knowledge (skills)"""
        self.procedural_memory[procedure_name] = {
            'steps': steps,
            'success_rate': success_rate,
            'parameters': parameters or {},
            'created': datetime.now().isoformat(),
            'usage_count': 0,
        }
        logger.info(f"🎯 Stored procedure: {procedure_name}")
    
    def record_emotional_state(self, emotion: str, intensity: float) -> None:
        """Record emotional state (confidence, frustration, etc.)"""
        # Apply decay to existing emotions
        for key in self.emotional_memory:
            self.emotional_memory[key] *= (1 - self.knowledge_decay_rate)
        
        # Add new emotion
        self.emotional_memory[emotion] = max(0, min(1, intensity))
    
    def update_context(
        self,
        market_state: Dict[str, Any],
        agent_state: Dict[str, Any],
        active_goals: List[str],
        constraints: List[str],
        performance_metrics: Optional[Dict[str, float]] = None
    ) -> str:
        """Update current context frame"""
        frame_id = f"context_{len(self.context_history)}"
        frame = ContextFrame(
            frame_id=frame_id,
            timestamp=datetime.now(),
            agent_id=self.agent_id,
            market_state=market_state,
            agent_state=agent_state,
            recent_decisions=[],
            performance_metrics=performance_metrics or {},
            active_goals=active_goals,
            constraints=constraints,
        )
        frame.compute_hash()
        
        self.current_context = frame
        self.context_history.append(frame)
        
        # Keep context history bounded
        if len(self.context_history) > 1000:
            self.context_history = self.context_history[-1000:]
        
        return frame_id
    
    def recall_relevant_memories(
        self,
        query_context: Dict[str, Any],
        memory_type: Optional[MemoryType] = None,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """Recall memories relevant to current context"""
        # Combine all memories
        all_memories = []
        if memory_type is None or memory_type == MemoryType.EPISODIC:
            all_memories.extend(self.episodic_memory.values())
        if memory_type is None or memory_type == MemoryType.SEMANTIC:
            # Convert semantic to memory entries for unified handling
            for kid, knowledge in self.semantic_memory.items():
                entry = MemoryEntry(
                    entry_id=kid,
                    memory_type=MemoryType.SEMANTIC,
                    timestamp=knowledge.created_at,
                    content={'insights': knowledge.core_insights},
                    importance_score=knowledge.confidence,
                )
                all_memories.append(entry)
        
        # Score by relevance
        scored = []
        for mem in all_memories:
            # Simple relevance: based on tags and content similarity
            relevance = self._compute_relevance(mem, query_context)
            mem.relevance_score = relevance
            scored.append((mem, mem.get_priority()))
        
        # Sort by priority and return top-k
        scored.sort(key=lambda x: x[1], reverse=True)
        recalled = [mem for mem, _ in scored[:limit]]
        
        # Update access info
        for mem in recalled:
            mem.update_access()
        
        return recalled
    
    def _compute_relevance(self, memory: MemoryEntry, query_context: Dict[str, Any]) -> float:
        """Compute relevance of memory to query context"""
        relevance = 0.5
        
        # Tag-based relevance
        query_tags = query_context.get('tags', [])
        if query_tags:
            matching_tags = len(set(memory.tags) & set(query_tags))
            relevance += matching_tags * 0.1
        
        # Temporal relevance (recent is more relevant)
        time_diff = (datetime.now() - memory.timestamp).total_seconds()
        temporal_factor = max(0.1, 1.0 - time_diff / 86400)
        relevance *= temporal_factor
        
        return min(1.0, relevance)
    
    def distill_knowledge_from_experiences(self) -> Dict[str, DistilledKnowledge]:
        """Extract and distill knowledge from episodic memories"""
        logger.info(f"🧪 Distilling knowledge from {len(self.episodic_memory)} experiences...")
        
        distilled = {}
        
        # Analyze episodic memories for patterns
        successful_experiences = [
            mem for mem in self.episodic_memory.values()
            if mem.content.get('success', False)
        ]
        
        if successful_experiences:
            # Extract strategic patterns
            patterns = self._extract_patterns(successful_experiences)
            
            for pattern_name, pattern_data in patterns.items():
                knowledge = DistilledKnowledge(
                    KnowledgeType.PATTERN,
                    confidence=pattern_data.get('confidence', 0.7)
                )
                knowledge.add_insight(
                    f"Pattern: {pattern_name}",
                    pattern_data
                )
                distilled[f"pattern_{pattern_name}"] = knowledge
        
        logger.info(f"✅ Distilled {len(distilled)} knowledge items")
        return distilled
    
    def _extract_patterns(self, experiences: List[MemoryEntry]) -> Dict[str, Any]:
        """Extract common patterns from experiences"""
        patterns = defaultdict(list)
        
        for exp in experiences:
            tags = exp.tags
            for tag in tags:
                patterns[tag].append(exp.content)
        
        # Analyze pattern frequency
        result = {}
        for pattern, instances in patterns.items():
            if len(instances) > 1:
                result[pattern] = {
                    'frequency': len(instances),
                    'confidence': min(1.0, len(instances) / 10),
                    'examples': instances[:3]
                }
        
        return result
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            'agent_id': self.agent_id,
            'total_experiences': self.total_experiences,
            'total_decisions': self.total_decisions,
            'episodic_count': len(self.episodic_memory),
            'semantic_count': len(self.semantic_memory),
            'procedural_count': len(self.procedural_memory),
            'context_frames': len(self.context_history),
            'sensory_buffer_size': len(self.sensory_memory),
            'emotional_states': dict(self.emotional_memory),
            'uptime_seconds': (datetime.now() - self.creation_time).total_seconds(),
        }
    
    def export_critical_memories(self) -> Dict[str, Any]:
        """Export critical memories for persistence or sharing"""
        # Select top-priority memories
        top_episodic = sorted(
            self.episodic_memory.values(),
            key=lambda m: m.get_priority(),
            reverse=True
        )[:10]
        
        export = {
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat(),
            'critical_experiences': [
                {
                    'id': mem.entry_id,
                    'content': mem.content,
                    'importance': mem.importance_score,
                    'tags': mem.tags,
                }
                for mem in top_episodic
            ],
            'distilled_knowledge': {
                kid: knowledge.to_dict()
                for kid, knowledge in self.semantic_memory.items()
            },
            'procedures': self.procedural_memory,
            'emotional_state': dict(self.emotional_memory),
        }
        
        return export
    
    def import_memories(self, memory_data: Dict[str, Any]) -> None:
        """Import memories from another agent or persistence"""
        logger.info(f"📥 Importing memories from {memory_data.get('agent_id')}...")
        
        # Import critical experiences
        for exp_data in memory_data.get('critical_experiences', []):
            self.store_experience(
                exp_data['content'],
                importance=exp_data.get('importance', 0.7),
                tags=exp_data.get('tags', [])
            )
        
        # Import procedures
        for proc_name, proc_data in memory_data.get('procedures', {}).items():
            self.procedural_memory[proc_name] = proc_data
        
        logger.info(f"✅ Imported {len(memory_data.get('critical_experiences', []))} experiences")


class AgentMemoryManager:
    """Manager for multiple agents' memories with knowledge sharing"""
    
    def __init__(self):
        self.agent_memories: Dict[str, EnhancedMemorySystem] = {}
        self.shared_knowledge_base: Dict[str, DistilledKnowledge] = {}
        self.knowledge_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def register_agent(self, agent_id: str) -> EnhancedMemorySystem:
        """Register new agent memory system"""
        memory_system = EnhancedMemorySystem(agent_id)
        self.agent_memories[agent_id] = memory_system
        logger.info(f"✅ Registered memory for agent: {agent_id}")
        return memory_system
    
    def share_knowledge(self, source_agent: str, knowledge_id: str, target_agents: Optional[List[str]] = None) -> None:
        """Share knowledge between agents"""
        if source_agent not in self.agent_memories:
            logger.warning(f"Source agent {source_agent} not found")
            return
        
        source_memory = self.agent_memories[source_agent]
        if knowledge_id not in source_memory.semantic_memory:
            logger.warning(f"Knowledge {knowledge_id} not found")
            return
        
        knowledge = source_memory.semantic_memory[knowledge_id]
        self.shared_knowledge_base[knowledge_id] = knowledge
        
        # Distribute to target agents
        targets = target_agents or list(self.agent_memories.keys())
        for agent_id in targets:
            if agent_id != source_agent:
                self.agent_memories[agent_id].semantic_memory[f"shared_{knowledge_id}"] = knowledge
                logger.info(f"📤 Shared knowledge {knowledge_id} to {agent_id}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics for all agents"""
        stats = {
            'total_agents': len(self.agent_memories),
            'shared_knowledge_items': len(self.shared_knowledge_base),
            'agents': {}
        }
        
        for agent_id, memory_sys in self.agent_memories.items():
            stats['agents'][agent_id] = memory_sys.get_memory_stats()
        
        return stats


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    memory = EnhancedMemorySystem('trading_agent')
    
    # Record sensory input
    memory.record_sensory_input({'price': 100.5, 'volume': 1000}, importance=0.8, tags=['market_data'])
    
    # Store experience
    memory.store_experience(
        {'action': 'buy', 'price': 100.5, 'success': True, 'profit': 2.5},
        importance=0.9,
        tags=['trading', 'successful']
    )
    
    # Store knowledge
    memory.store_semantic_knowledge(
        KnowledgeType.STRATEGIC,
        ['Buy when RSI < 30 on 4H chart'],
        {'support': 'Historical data 2024-2026', 'success_rate': 0.72},
        confidence=0.85
    )
    
    # Store procedure
    memory.store_procedure(
        'rsi_strategy',
        ['Calculate RSI', 'Check if RSI < 30', 'Place buy order'],
        success_rate=0.72
    )
    
    # Update context
    memory.update_context(
        market_state={'price': 101, 'trend': 'up'},
        agent_state={'portfolio': 10000},
        active_goals=['maximize_profit'],
        constraints=['max_loss_5pct']
    )
    
    # Get stats
    stats = memory.get_memory_stats()
    print("Memory Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
