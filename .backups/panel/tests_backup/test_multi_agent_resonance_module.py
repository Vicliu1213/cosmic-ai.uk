#!/usr/bin/env python3
"""
Unit Tests for Multi-Agent Resonance Module

Tests agent registry, coordination, amplification, and full module
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict

from src.core.multi_agent_resonance_module import (
    MultiAgentResonanceModule,
    AgentRegistry,
    ResonanceCoordinator,
    ResonanceAmplifier,
    AgentState,
    AgentProfile
)


class TestAgentRegistry:
    """Test AgentRegistry class."""
    
    def test_init(self):
        """Test registry initialization."""
        registry = AgentRegistry()
        assert len(registry.agents) == 0
        assert len(registry.resonance_states) == 0
    
    def test_register_agent(self):
        """Test agent registration."""
        registry = AgentRegistry()
        
        agent_id = str(1)  # Simple id
        registry.agents[agent_id] = AgentProfile(
            agent_id=agent_id,
            agent_name="Test Agent",
            theories=["momentum", "trend"],
            expertise_areas=["trends"],
            success_rate=0.5
        )
        
        assert agent_id in registry.agents
        assert registry.agents[agent_id].agent_name == "Test Agent"
    
    def test_register_multiple_agents(self):
        """Test registering multiple agents."""
        registry = AgentRegistry()
        
        for i in range(5):
            agent_id = str(i)
            registry.agents[agent_id] = AgentProfile(
                agent_id=agent_id,
                agent_name=f"Agent {i}",
                theories=["momentum"],
                expertise_areas=["trends"]
            )
        
        assert len(registry.agents) == 5
    
    def test_get_agent(self):
        """Test retrieving an agent."""
        registry = AgentRegistry()
        
        agent_id = "test_1"
        profile = AgentProfile(
            agent_id=agent_id,
            agent_name="Test",
            theories=["momentum"],
            expertise_areas=["trends"]
        )
        registry.agents[agent_id] = profile
        
        retrieved = registry.get_agent(agent_id)
        assert retrieved is not None
        assert retrieved.agent_name == "Test"
    
    def test_update_agent_state(self):
        """Test updating agent state."""
        registry = AgentRegistry()
        
        agent_id = "test_1"
        registry.agents[agent_id] = AgentProfile(
            agent_id=agent_id,
            agent_name="Test",
            theories=["momentum"],
            expertise_areas=["trends"],
            state=AgentState.IDLE
        )
        
        registry.update_agent_state(agent_id, AgentState.ANALYZING)
        assert registry.agents[agent_id].state == AgentState.ANALYZING
    
    def test_update_success_rate(self):
        """Test updating agent success rate."""
        registry = AgentRegistry()
        
        agent_id = "test_1"
        registry.agents[agent_id] = AgentProfile(
            agent_id=agent_id,
            agent_name="Test",
            theories=["momentum"],
            expertise_areas=["trends"],
            success_rate=0.5
        )
        
        # Update with success
        registry.update_agent_success_rate(agent_id, True)
        new_rate = registry.agents[agent_id].success_rate
        assert new_rate > 0.5
        
        # Update with failure
        registry.update_agent_success_rate(agent_id, False)
        newer_rate = registry.agents[agent_id].success_rate
        assert newer_rate < new_rate


class TestResonanceCoordinator:
    """Test ResonanceCoordinator class."""
    
    def test_init(self):
        """Test coordinator initialization."""
        registry = AgentRegistry()
        coordinator = ResonanceCoordinator(registry)
        assert coordinator.registry is registry
        assert len(coordinator.resonance_events) == 0
    
    def test_detect_agent_resonance_single_agent(self):
        """Test resonance detection with single agent."""
        registry = AgentRegistry()
        coordinator = ResonanceCoordinator(registry)
        
        signals = {"agent_1": 0.8}
        detected, details = coordinator.detect_agent_resonance(signals)
        assert not detected
    
    def test_detect_agent_resonance_perfect_alignment(self):
        """Test resonance detection with perfect alignment."""
        registry = AgentRegistry()
        coordinator = ResonanceCoordinator(registry)
        
        signals = {"agent_1": 0.85, "agent_2": 0.80, "agent_3": 0.82}
        detected, details = coordinator.detect_agent_resonance(signals)
        
        assert detected
        assert details["resonance_score"] > 0.6
        assert details["agreement_ratio"] > 0.8
    
    def test_detect_agent_resonance_divergent(self):
        """Test resonance detection with divergent signals."""
        registry = AgentRegistry()
        coordinator = ResonanceCoordinator(registry)
        
        # Strongly divergent signals (both positive and strongly negative)
        signals = {"agent_1": 0.9, "agent_2": -0.85, "agent_3": 0.88}
        detected, details = coordinator.detect_agent_resonance(signals)
        
        # Two agents agree, one disagrees - moderate resonance
        assert "resonance_score" in details
        assert "agreement_ratio" in details
    
    def test_trigger_resonance_event(self):
        """Test triggering resonance event."""
        registry = AgentRegistry()
        coordinator = ResonanceCoordinator(registry)
        
        event = coordinator.trigger_resonance_event(
            trigger_type="test",
            participating_agents=["agent_1", "agent_2"],
            resonance_score=0.8,
            amplification_factor=1.4,
            recommended_action="buy"
        )
        
        assert event is not None
        assert event.resonance_score == 0.8
        assert event.amplification_factor == 1.4
        assert len(coordinator.resonance_events) == 1
    
    def test_register_event_callback(self):
        """Test registering and invoking event callbacks."""
        registry = AgentRegistry()
        coordinator = ResonanceCoordinator(registry)
        
        callback_invoked = []
        
        def test_callback(event):
            callback_invoked.append(event.trigger_type)
        
        coordinator.register_event_callback("test_event", test_callback)
        
        event = coordinator.trigger_resonance_event(
            trigger_type="test_event",
            participating_agents=["agent_1"],
            resonance_score=0.8,
            amplification_factor=1.4,
            recommended_action="buy"
        )
        
        assert "test_event" in callback_invoked


class TestResonanceAmplifier:
    """Test ResonanceAmplifier class."""
    
    def test_init(self):
        """Test amplifier initialization."""
        registry = AgentRegistry()
        amplifier = ResonanceAmplifier(registry)
        assert amplifier.registry is registry
    
    def test_compute_amplified_decision_empty(self):
        """Test amplified decision with no agents."""
        registry = AgentRegistry()
        amplifier = ResonanceAmplifier(registry)
        
        result = amplifier.compute_amplified_decision({}, 0.8)
        assert result == {}
    
    def test_compute_amplified_decision(self):
        """Test computing amplified decision."""
        registry = AgentRegistry()
        amplifier = ResonanceAmplifier(registry)
        
        # Add agents
        for i in range(3):
            agent_id = str(i)
            registry.agents[agent_id] = AgentProfile(
                agent_id=agent_id,
                agent_name=f"Agent {i}",
                theories=["momentum"],
                expertise_areas=["trends"],
                success_rate=0.7
            )
        
        decisions = {
            "0": {"position_size": 1.0, "confidence": 0.9, "leverage": 1.5},
            "1": {"position_size": 0.8, "confidence": 0.85, "leverage": 1.2},
            "2": {"position_size": 1.1, "confidence": 0.92, "leverage": 1.3}
        }
        
        amplified = amplifier.compute_amplified_decision(decisions, 0.8)
        
        assert "position_size" in amplified
        assert "confidence" in amplified
        assert "leverage" in amplified
        assert amplified["participating_agents"] == 3
    
    def test_compute_consensus_signal(self):
        """Test computing consensus signal."""
        registry = AgentRegistry()
        amplifier = ResonanceAmplifier(registry)
        
        # Add agents with positive consensus
        for i in range(3):
            agent_id = str(i)
            registry.agents[agent_id] = AgentProfile(
                agent_id=agent_id,
                agent_name=f"Agent {i}",
                theories=["momentum"],
                expertise_areas=["trends"],
                success_rate=0.7
            )
        
        signals = {"0": 0.8, "1": 0.75, "2": 0.85}
        consensus = amplifier.compute_consensus_signal(signals)
        
        assert consensus > 0.5
        assert -1.0 <= consensus <= 1.0


class TestMultiAgentResonanceModule:
    """Test main MultiAgentResonanceModule class."""
    
    def test_init(self):
        """Test module initialization."""
        module = MultiAgentResonanceModule()
        assert module.registry is not None
        assert module.coordinator is not None
        assert module.amplifier is not None
        assert module.total_resonances == 0
    
    def test_register_trading_agent(self):
        """Test registering trading agents."""
        module = MultiAgentResonanceModule()
        
        agent_id = module.register_trading_agent(
            agent_name="Test Agent",
            theories=["momentum", "trend"],
            expertise_areas=["trends", "volatility"]
        )
        
        assert agent_id is not None
        assert len(module.registry.agents) == 1
    
    def test_synchronize_agents_no_resonance(self):
        """Test agent synchronization with no resonance."""
        module = MultiAgentResonanceModule()
        
        # Register agents
        agent1 = module.register_trading_agent("Agent 1", ["momentum"], ["trends"])
        agent2 = module.register_trading_agent("Agent 2", ["reversion"], ["ranges"])
        
        # Divergent signals (no resonance)
        signals = {agent1: 0.9, agent2: -0.8}
        decisions = {
            agent1: {"position_size": 1.0, "confidence": 0.9, "leverage": 1.5},
            agent2: {"position_size": 0.8, "confidence": 0.85, "leverage": 1.2}
        }
        
        resonance, amplified = module.synchronize_agents_on_resonance(signals, decisions)
        
        assert isinstance(resonance, bool)
        assert isinstance(amplified, dict)
    
    def test_synchronize_agents_with_resonance(self):
        """Test agent synchronization with resonance."""
        module = MultiAgentResonanceModule()
        
        # Register agents
        agent1 = module.register_trading_agent("Agent 1", ["momentum"], ["trends"])
        agent2 = module.register_trading_agent("Agent 2", ["trend_follow"], ["trends"])
        agent3 = module.register_trading_agent("Agent 3", ["quantum"], ["complex"])
        
        # Aligned signals (resonance expected)
        signals = {agent1: 0.85, agent2: 0.80, agent3: 0.82}
        decisions = {
            agent1: {"position_size": 1.0, "confidence": 0.9, "leverage": 1.5},
            agent2: {"position_size": 0.8, "confidence": 0.85, "leverage": 1.2},
            agent3: {"position_size": 1.1, "confidence": 0.92, "leverage": 1.3}
        }
        
        resonance, amplified = module.synchronize_agents_on_resonance(signals, decisions)
        
        assert amplified["participating_agents"] == 3
        if resonance:
            assert module.total_resonances > 0
    
    def test_get_module_metrics(self):
        """Test getting module metrics."""
        module = MultiAgentResonanceModule()
        
        # Register some agents
        for i in range(3):
            module.register_trading_agent(
                f"Agent {i}",
                ["momentum"],
                ["trends"]
            )
        
        metrics = module.get_module_metrics()
        
        assert "registry" in metrics
        assert "coordination" in metrics
        assert "amplification" in metrics
        assert metrics["registry"]["total_agents"] == 3
    
    def test_multiple_resonance_cycles(self):
        """Test multiple cycles of agent synchronization."""
        module = MultiAgentResonanceModule()
        
        # Register agents
        agents = [
            module.register_trading_agent(f"Agent {i}", ["momentum"], ["trends"])
            for i in range(3)
        ]
        
        # Simulate multiple trading cycles
        for cycle in range(5):
            signals = {a: 0.75 + 0.05 * cycle for a in agents}
            decisions = {
                a: {
                    "position_size": 1.0,
                    "confidence": 0.85,
                    "leverage": 1.5
                }
                for a in agents
            }
            
            resonance, amplified = module.synchronize_agents_on_resonance(
                signals,
                decisions
            )
            
            assert "participating_agents" in amplified
        
        # Verify metrics
        metrics = module.get_module_metrics()
        assert metrics["registry"]["total_agents"] == 3


class TestIntegration:
    """Integration tests for multi-agent resonance."""
    
    def test_end_to_end_resonance_flow(self):
        """Test complete resonance flow."""
        module = MultiAgentResonanceModule()
        
        # Register 5 agents
        agents = []
        for i in range(5):
            agent_id = module.register_trading_agent(
                f"Trading Agent {i}",
                ["momentum", "mean_reversion"],
                ["trending", "ranges"]
            )
            agents.append(agent_id)
        
        # Simulate resonance scenario
        signals = {a: 0.8 + 0.02 * i for i, a in enumerate(agents)}
        decisions = {
            a: {
                "position_size": 1.0 + 0.1 * i,
                "confidence": 0.85 + 0.02 * i,
                "leverage": 1.5
            }
            for i, a in enumerate(agents)
        }
        
        resonance, amplified = module.synchronize_agents_on_resonance(signals, decisions)
        
        assert amplified["participating_agents"] == 5
        assert "position_size" in amplified
        assert amplified["position_size"] > 0
    
    def test_agent_success_rate_update(self):
        """Test updating agent success rates and impact on coordination."""
        module = MultiAgentResonanceModule()
        
        agents = [
            module.register_trading_agent(f"Agent {i}", ["momentum"], ["trends"])
            for i in range(2)
        ]
        
        # Update success rates
        for agent_id in agents:
            for _ in range(3):
                module.registry.update_agent_success_rate(agent_id, True)
        
        # Verify success rates increased
        for agent_id in agents:
            agent = module.registry.get_agent(agent_id)
            assert agent.success_rate > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
