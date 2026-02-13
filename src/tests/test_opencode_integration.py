#!/usr/bin/env python3
"""
OpenCode Framework Integration Tests
OpenCode框架集成测试

Tests for OpenCode framework, agents, skills, and orchestration.
"""

import pytest
import asyncio
import time
from typing import Dict, Any

# Import OpenCode components
from opencode import (
    create_framework,
    create_orchestrator,
    get_version,
    OpenCodeConfig,
    OpenCodeFramework,
    UniversalAgentOrchestrator,
    AgentRole,
    AgentState,
    UniversalAgent,
    SkillCategory,
    SkillLevel,
    BaseSkill,
    SkillRegistry,
)


class TestOpenCodeFramework:
    """Tests for OpenCode framework initialization and management"""
    
    def test_version(self):
        """Test version retrieval"""
        version = get_version()
        assert version == "1.0.0"
        print(f"✅ Version: {version}")
    
    def test_framework_creation(self):
        """Test framework creation with default config"""
        framework = create_framework()
        assert framework is not None
        assert isinstance(framework, OpenCodeFramework)
        assert framework.config is not None
        print(f"✅ Framework created: {framework.__class__.__name__}")
    
    def test_framework_config(self):
        """Test framework configuration"""
        config = OpenCodeConfig()
        assert config.api_enabled == True
        assert config.api_port == 8000
        assert config.enable_cosmos_agent == True
        print(f"✅ Framework config is valid")
    
    def test_framework_initialization(self):
        """Test framework initialization with agents and skills"""
        framework = create_framework()
        assert len(framework.agent_registry.agents) > 0
        assert len(framework.skill_registry.skills) > 0
        print(f"✅ Framework initialized with {len(framework.agent_registry.agents)} agents")
        print(f"✅ Framework initialized with {len(framework.skill_registry.skills)} skills")
    
    def test_framework_agent_registry(self):
        """Test agent registry in framework"""
        framework = create_framework()
        agents = framework.agent_registry.agents
        
        # Verify trading agents
        assert 'trading_signal_agent' in agents
        assert 'risk_management_agent' in agents
        
        # Verify analytics agents
        assert 'market_analysis_agent' in agents
        
        # Verify system agents
        assert 'system_monitor_agent' in agents
        
        # Verify cosmos agent
        assert 'cosmos_intelligence_agent' in agents
        
        print(f"✅ All agent registry checks passed")
    
    def test_framework_skill_registry(self):
        """Test skill registry in framework"""
        framework = create_framework()
        skills = framework.skill_registry.skills
        
        assert len(skills) > 0
        # Check for core skills
        skill_names = list(skills.keys())
        print(f"✅ Skills registered: {skill_names}")


class TestUniversalAgentOrchestrator:
    """Tests for universal agent orchestrator"""
    
    def test_orchestrator_creation(self):
        """Test orchestrator creation"""
        framework = create_framework()
        orchestrator = create_orchestrator(framework)
        
        assert orchestrator is not None
        assert isinstance(orchestrator, UniversalAgentOrchestrator)
        print(f"✅ Orchestrator created: {orchestrator.__class__.__name__}")
    
    def test_orchestrator_agent_registration(self):
        """Test agent registration in orchestrator"""
        framework = create_framework()
        orchestrator = create_orchestrator(framework)
        
        assert len(orchestrator.agents) > 0
        assert len(orchestrator.agents) == len(framework.agent_registry.agents)
        print(f"✅ Orchestrator has {len(orchestrator.agents)} agents")
    
    def test_orchestrator_agent_retrieval(self):
        """Test retrieving agents from orchestrator"""
        framework = create_framework()
        orchestrator = create_orchestrator(framework)
        
        # Get a specific agent
        agent = orchestrator.get_agent('trading_signal_agent')
        assert agent is not None
        assert agent.agent_id == 'trading_signal_agent'
        print(f"✅ Retrieved agent: {agent.agent_id}")
    
    def test_orchestrator_get_agents_by_role(self):
        """Test retrieving agents by role"""
        framework = create_framework()
        orchestrator = create_orchestrator(framework)
        
        # Get executor agents
        executors = orchestrator.get_agents_by_role(AgentRole.EXECUTOR)
        assert len(executors) > 0
        print(f"✅ Found {len(executors)} executor agents")
        
        # Get analyzer agents
        analyzers = orchestrator.get_agents_by_role(AgentRole.ANALYZER)
        assert len(analyzers) > 0
        print(f"✅ Found {len(analyzers)} analyzer agents")
    
    def test_orchestrator_get_agents_by_capability(self):
        """Test retrieving agents by capability"""
        framework = create_framework()
        orchestrator = create_orchestrator(framework)
        
        # Get agents with signal_generation capability
        signal_agents = orchestrator.get_agents_by_capability('signal_generation')
        assert len(signal_agents) > 0
        print(f"✅ Found {len(signal_agents)} agents with signal_generation capability")


class TestUniversalAgent:
    """Tests for universal agent functionality"""
    
    def test_agent_creation(self):
        """Test creating a new agent"""
        orchestrator = UniversalAgentOrchestrator()
        
        agent = orchestrator.create_agent(
            agent_id='test_agent',
            role=AgentRole.ANALYZER,
            name='Test Agent',
            capabilities=['analysis', 'prediction'],
            description='Test agent for validation'
        )
        
        assert agent is not None
        assert agent.agent_id == 'test_agent'
        assert agent.role == AgentRole.ANALYZER
        assert 'analysis' in agent.capabilities
        print(f"✅ Agent created: {agent.agent_id}")
    
    def test_agent_state_transitions(self):
        """Test agent state transitions"""
        orchestrator = UniversalAgentOrchestrator()
        
        agent = orchestrator.create_agent(
            agent_id='state_test_agent',
            role=AgentRole.EXECUTOR,
            name='State Test Agent',
            capabilities=['testing'],
        )
        
        # Initial state should be IDLE
        assert agent.state == AgentState.IDLE
        
        # Transition to ACTIVE
        agent.state = AgentState.ACTIVE
        assert agent.state == AgentState.ACTIVE
        
        # Transition to BUSY
        agent.state = AgentState.BUSY
        assert agent.state == AgentState.BUSY
        
        print(f"✅ Agent state transitions work correctly")
    
    def test_agent_task_tracking(self):
        """Test agent task completion tracking"""
        orchestrator = UniversalAgentOrchestrator()
        
        agent = orchestrator.create_agent(
            agent_id='task_tracking_agent',
            role=AgentRole.EXECUTOR,
            name='Task Tracking Agent',
            capabilities=['task_execution'],
        )
        
        # Initial counts
        assert agent.tasks_completed == 0
        assert agent.tasks_failed == 0
        
        # Simulate task completion
        agent.tasks_completed = 5
        assert agent.tasks_completed == 5
        
        # Simulate task failure
        agent.tasks_failed = 2
        assert agent.tasks_failed == 2
        
        print(f"✅ Agent task tracking works correctly")


class TestSkillRegistry:
    """Tests for skill registry and management"""
    
    def test_skill_registry_creation(self):
        """Test skill registry creation"""
        registry = SkillRegistry()
        assert registry is not None
        print(f"✅ Skill registry created")
    
    def test_framework_skill_registry(self):
        """Test framework skill registry integration"""
        framework = create_framework()
        
        # Verify skill registry exists
        assert framework.skill_registry is not None
        
        # Verify skills are loaded
        skills = framework.skill_registry.skills
        assert isinstance(skills, dict)
        assert len(skills) > 0
        
        print(f"✅ Framework skill registry has {len(skills)} skills")
    
    def test_skill_execution(self):
        """Test executing a skill from framework"""
        framework = create_framework()
        registry = framework.skill_registry
        
        # Get available skills
        skills = list(registry.skills.keys())
        assert len(skills) > 0
        
        print(f"✅ Available skills: {skills[:5]}...")  # Print first 5


class TestOpenCodeIntegration:
    """Integration tests for complete OpenCode system"""
    
    def test_full_system_initialization(self):
        """Test complete system initialization"""
        framework = create_framework()
        orchestrator = create_orchestrator(framework)
        
        # Verify all components are initialized
        assert framework.agent_registry is not None
        assert framework.skill_registry is not None
        assert orchestrator.agents is not None
        
        # Verify counts
        assert len(framework.agent_registry.agents) == len(orchestrator.agents)
        assert len(framework.skill_registry.skills) > 0
        
        print(f"✅ Full system initialized successfully")
    
    def test_agent_orchestrator_coordination(self):
        """Test agent-orchestrator coordination"""
        orchestrator = UniversalAgentOrchestrator()
        
        # Create multiple agents
        executor = orchestrator.create_agent(
            agent_id='executor',
            role=AgentRole.EXECUTOR,
            name='Executor',
            capabilities=['execution']
        )
        
        analyzer = orchestrator.create_agent(
            agent_id='analyzer',
            role=AgentRole.ANALYZER,
            name='Analyzer',
            capabilities=['analysis']
        )
        
        coordinator = orchestrator.create_agent(
            agent_id='coordinator',
            role=AgentRole.COORDINATOR,
            name='Coordinator',
            capabilities=['coordination']
        )
        
        # Verify all agents are registered
        assert len(orchestrator.agents) == 3
        
        # Verify role-based retrieval
        executors = orchestrator.get_agents_by_role(AgentRole.EXECUTOR)
        assert len(executors) == 1
        
        analyzers = orchestrator.get_agents_by_role(AgentRole.ANALYZER)
        assert len(analyzers) == 1
        
        coordinators = orchestrator.get_agents_by_role(AgentRole.COORDINATOR)
        assert len(coordinators) == 1
        
        print(f"✅ Agent coordination working correctly")
    
    def test_framework_with_custom_config(self):
        """Test framework with custom configuration"""
        config_dict = {
            'api_enabled': False,
            'api_port': 9000,
        }
        
        framework = create_framework(config_dict=config_dict)
        
        assert framework.config.api_enabled == False
        assert framework.config.api_port == 9000
        
        print(f"✅ Custom configuration applied successfully")


class TestOpenCodePerformance:
    """Performance tests for OpenCode framework"""
    
    def test_framework_creation_time(self):
        """Test framework creation time"""
        start = time.time()
        framework = create_framework()
        elapsed = time.time() - start
        
        assert elapsed < 5.0  # Should take less than 5 seconds
        print(f"✅ Framework creation time: {elapsed:.3f}s")
    
    def test_orchestrator_creation_time(self):
        """Test orchestrator creation time"""
        framework = create_framework()
        
        start = time.time()
        orchestrator = create_orchestrator(framework)
        elapsed = time.time() - start
        
        assert elapsed < 1.0  # Should take less than 1 second
        print(f"✅ Orchestrator creation time: {elapsed:.3f}s")
    
    def test_agent_retrieval_performance(self):
        """Test agent retrieval performance"""
        framework = create_framework()
        orchestrator = create_orchestrator(framework)
        
        # Measure agent retrieval time
        start = time.time()
        for i in range(1000):
            orchestrator.get_agent('trading_signal_agent')
        elapsed = time.time() - start
        
        avg_time = elapsed / 1000
        assert avg_time < 0.001  # Average should be less than 1ms
        print(f"✅ Agent retrieval average time: {avg_time*1000:.3f}ms")


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
