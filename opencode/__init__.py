#!/usr/bin/env python3
"""
OpenCode Framework - Universal Multi-Agent Intelligence System
OpenCode框架 - 通用多智能体系统

A comprehensive framework for managing universal agents, skills, and orchestration
in the Comic AI trading system and beyond.

核心功能:
- Universal Agent Management (通用智能体管理)
- Skill Registration & Execution (技能注册和执行)
- Multi-Agent Orchestration (多智能体编排)
- Cosmos-Scale Intelligence (宇宙规模智能)
- Trading System Integration (交易系统集成)
"""

__version__ = "1.0.0"
__author__ = "Comic AI Development Team"
__description__ = "Universal Multi-Agent Intelligence Framework"

# Import core components
from .oh_my_opencode import (
    OpenCodeConfig,
    UniversalAgentRegistry,
    SkillRegistry as OpenCodeSkillRegistry,
    OpenCodeFramework,
)

from .universal_agent import (
    AgentRole,
    AgentState,
    AgentMessage,
    UniversalAgent,
    UniversalAgentOrchestrator,
    CosmosIntelligenceAgent,
    initialize_orchestrator,
)

from .skills import (
    SkillCategory,
    SkillLevel,
    BaseSkill,
    QuantumOptimizationSkill,
    ParticleSwarmSkill,
    SignalGenerationSkill,
    RiskManagementSkill,
    MarketAnalysisSkill,
    CorrelationAnalysisSkill,
    ConfigurationManagementSkill,
    DataProcessingSkill,
    SkillRegistry,
)

from .bio_inspired_enhancement import (
    EvolutionStrategy,
    AdaptationMechanism,
    AdaptationMetrics,
    GeneticGene,
    AgentGenome,
    EvolutionEngine,
    NeuralAdaptationEngine,
    BioInspiredAgentEnhancer,
)

from .agent_memory import (
    MemoryType,
    KnowledgeType,
    MemoryEntry,
    ContextFrame,
    DistilledKnowledge,
    EnhancedMemorySystem,
    AgentMemoryManager,
)

from .performance_optimization import (
    OptimizedMemoryIndex,
    ThreadSafeMemoryCache,
    ReadWriteLock,
    OptimizedMemoryRecall,
)

from .multiverse_challenge import (
    MultiverseChallenge,
    create_multiverse_challenge,
    run_multiverse_simulation,
    UniverseType,
    MultiverseAgent,
)

# Define public API
__all__ = [
    # OpenCode Framework
    "OpenCodeConfig",
    "UniversalAgentRegistry",
    "OpenCodeSkillRegistry",
    "OpenCodeFramework",
    "create_framework",
    "create_orchestrator",
    "get_version",
    
    # Agent System
    "AgentRole",
    "AgentState",
    "AgentMessage",
    "UniversalAgent",
    "UniversalAgentOrchestrator",
    "CosmosIntelligenceAgent",
    "initialize_orchestrator",
    
    # Skills
    "SkillCategory",
    "SkillLevel",
    "BaseSkill",
    "QuantumOptimizationSkill",
    "ParticleSwarmSkill",
    "SignalGenerationSkill",
    "RiskManagementSkill",
    "MarketAnalysisSkill",
    "CorrelationAnalysisSkill",
    "ConfigurationManagementSkill",
    "DataProcessingSkill",
    "SkillRegistry",
    
    # Bio-Inspired Enhancement
    "EvolutionStrategy",
    "AdaptationMechanism",
    "AdaptationMetrics",
    "GeneticGene",
    "AgentGenome",
    "EvolutionEngine",
    "NeuralAdaptationEngine",
    "BioInspiredAgentEnhancer",
    
    # Memory & Context System
    "MemoryType",
    "KnowledgeType",
    "MemoryEntry",
    "ContextFrame",
    "DistilledKnowledge",
    "EnhancedMemorySystem",
    "AgentMemoryManager",
    
    # Performance Optimization
    "OptimizedMemoryIndex",
    "ThreadSafeMemoryCache",
    "ReadWriteLock",
    "OptimizedMemoryRecall",
    
    # Multiverse Challenge System
    "MultiverseChallenge",
    "create_multiverse_challenge",
    "run_multiverse_simulation",
    "UniverseType",
    "MultiverseAgent",
]


def create_framework(
    config_dict=None,
    mode=None,
    api_enabled=True,
    api_port=8000,
    max_agents=100,
):
    """
    Create and initialize OpenCode framework with default configuration.
    
    Args:
        config_dict: Optional configuration dictionary
        mode: OpenCode mode (development, staging, production, sandbox)
        api_enabled: Enable REST API (default: True)
        api_port: API port number (default: 8000)
        max_agents: Maximum number of agents (default: 100)
        
    Returns:
        OpenCodeFramework: Initialized framework instance
    """
    from .oh_my_opencode import OpenCodeMode
    
    # Create config
    config = OpenCodeConfig(
        name="Comic-AI-Trading-System",
        version=__version__,
        api_enabled=api_enabled,
        api_port=api_port,
    )
    
    if mode:
        if isinstance(mode, str):
            config.mode = OpenCodeMode[mode.upper()]
        else:
            config.mode = mode
    
    if config_dict:
        # Merge additional config
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    # Create framework
    framework = OpenCodeFramework(config)
    
    # Initialize with default agents and skills
    framework.initialize()
    
    return framework


def create_orchestrator(framework=None):
    """
    Create a universal agent orchestrator.
    
    Args:
        framework: OpenCode framework (optional)
        
    Returns:
        UniversalAgentOrchestrator: Initialized orchestrator
    """
    if framework is None:
        framework = create_framework()
    
    orchestrator = UniversalAgentOrchestrator()
    
    # Create and register agents from framework configuration
    for agent_id, agent_config in framework.agent_registry.agents.items():
        # Determine agent role based on agent type
        agent_type = agent_config.get('type', 'unknown').upper()
        if agent_type == 'TRADING':
            role = AgentRole.EXECUTOR
        elif agent_type == 'ANALYTICS':
            role = AgentRole.ANALYZER
        elif agent_type == 'SYSTEM':
            role = AgentRole.MONITOR
        elif agent_type == 'COSMOS':
            role = AgentRole.COORDINATOR
        else:
            role = AgentRole.INTEGRATOR
        
        # Create agent
        agent = orchestrator.create_agent(
            agent_id=agent_id,
            role=role,
            name=agent_id.replace('_', ' ').title(),
            capabilities=agent_config.get('capabilities', []),
            description=agent_config.get('description', '')
        )
    
    return orchestrator


def get_version():
    """Get OpenCode version."""
    return __version__


# Log initialization
import logging
logger = logging.getLogger(__name__)
logger.info(f"OpenCode Framework v{__version__} initialized")
logger.info("Available components: Agents, Skills, Orchestration, Framework")
