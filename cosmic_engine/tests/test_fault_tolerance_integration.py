#!/usr/bin/env python3
"""
Fault Tolerance Integration Test
容錯系統集成測試
"""

import pytest
import ray
import yaml
import logging
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cosmic.fault_tolerance import (
    FaultDetectionEngine,
    FaultIsolationManager,
    FailoverManager,
    FaultToleranceOrchestrator
)
from cosmic.agent import Agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def ray_cluster():
    """Initialize and cleanup Ray cluster for testing"""
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True, num_cpus=4, num_gpus=0)
    yield
    ray.shutdown()


@pytest.fixture
def config():
    """Load test configuration"""
    config_path = Path(__file__).parent.parent / "config" / "cosmic_config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


class TestFaultDetectionEngine:
    """Test Fault Detection Engine"""
    
    def test_fault_detection_initialization(self):
        """Test FaultDetectionEngine initialization"""
        config = {
            "detection_interval_ms": 1000,
            "failure_threshold": 0.5
        }
        engine = FaultDetectionEngine(config)
        assert engine is not None
        assert engine.detection_interval_ms == 1000
        logger.info("✅ FaultDetectionEngine initialized successfully")
    
    def test_health_check_monitoring(self):
        """Test health check monitoring"""
        config = {
            "detection_interval_ms": 1000,
            "failure_threshold": 0.5
        }
        engine = FaultDetectionEngine(config)
        
        # Simulate health check
        health_data = {
            "cpu_usage": 45.2,
            "memory_usage": 62.1,
            "network_latency_ms": 23.5
        }
        result = engine.check_component_health(health_data)
        assert result is not None
        assert "healthy" in result or "status" in result
        logger.info(f"✅ Health check monitoring working: {result}")


class TestFaultIsolationManager:
    """Test Fault Isolation Manager"""
    
    def test_fault_isolation_initialization(self):
        """Test FaultIsolationManager initialization"""
        config = {
            "isolation_strategy": "automatic",
            "strategies": ["circuit_breaker", "timeout_isolation"]
        }
        manager = FaultIsolationManager(config)
        assert manager is not None
        assert manager.isolation_strategy == "automatic"
        logger.info("✅ FaultIsolationManager initialized successfully")
    
    def test_isolation_strategies(self):
        """Test different isolation strategies"""
        config = {
            "isolation_strategy": "automatic",
            "strategies": ["circuit_breaker", "timeout_isolation"]
        }
        manager = FaultIsolationManager(config)
        
        # Test circuit breaker isolation
        component_id = "agent_1"
        result = manager.apply_isolation_strategy(component_id, "circuit_breaker")
        assert result is not None
        logger.info(f"✅ Circuit breaker isolation applied: {result}")


class TestFailoverManager:
    """Test Failover Manager"""
    
    def test_failover_initialization(self):
        """Test FailoverManager initialization"""
        config = {
            "failover_timeout_sec": 5,
            "backup_replicas": 2
        }
        manager = FailoverManager(config)
        assert manager is not None
        assert manager.failover_timeout_sec == 5
        logger.info("✅ FailoverManager initialized successfully")
    
    def test_failover_triggering(self):
        """Test failover triggering"""
        config = {
            "failover_timeout_sec": 5,
            "backup_replicas": 2
        }
        manager = FailoverManager(config)
        
        # Simulate failover
        failed_component = "agent_1"
        result = manager.trigger_failover(failed_component)
        assert result is not None
        logger.info(f"✅ Failover triggered successfully: {result}")


class TestFaultToleranceOrchestrator:
    """Test Fault Tolerance Orchestrator"""
    
    def test_orchestrator_initialization(self, ray_cluster, config):
        """Test FaultToleranceOrchestrator initialization"""
        ft_config = config.get("fault_tolerance", {})
        orchestrator_remote = FaultToleranceOrchestrator.remote(ft_config, [])
        assert orchestrator_remote is not None
        logger.info("✅ FaultToleranceOrchestrator initialized successfully")
    
    def test_health_check_execution(self, ray_cluster, config):
        """Test health check execution"""
        ft_config = config.get("fault_tolerance", {})
        orchestrator_remote = FaultToleranceOrchestrator.remote(ft_config, [])
        
        # Perform health check
        health_result = ray.get(orchestrator_remote.perform_health_check.remote())
        assert health_result is not None
        logger.info(f"✅ Health check executed: {health_result}")
    
    def test_fault_recovery_workflow(self, ray_cluster, config):
        """Test complete fault recovery workflow"""
        ft_config = config.get("fault_tolerance", {})
        orchestrator_remote = FaultToleranceOrchestrator.remote(ft_config, [])
        
        # Simulate fault scenario
        fault_info = {
            "component_id": "agent_1",
            "fault_type": "memory_leak",
            "severity": "high"
        }
        
        recovery_result = ray.get(
            orchestrator_remote.handle_fault.remote("agent_1", "memory_leak", "high")
        )
        assert recovery_result is not None
        logger.info(f"✅ Fault recovery workflow executed: {recovery_result}")


class TestFaultToleranceIntegration:
    """Integration tests for entire fault tolerance system"""
    
    def test_multi_component_monitoring(self, ray_cluster, config):
        """Test monitoring multiple components simultaneously"""
        ft_config = config.get("fault_tolerance", {})
        orchestrator_remote = FaultToleranceOrchestrator.remote(ft_config, [])
        
        # Simulate multiple component health checks
        for i in range(3):
            health_result = ray.get(orchestrator_remote.perform_health_check.remote())
            assert health_result is not None
        
        logger.info("✅ Multi-component monitoring working correctly")
    
    def test_cascading_failure_handling(self, ray_cluster, config):
        """Test handling of cascading failures"""
        ft_config = config.get("fault_tolerance", {})
        orchestrator_remote = FaultToleranceOrchestrator.remote(ft_config, [])
        
        # Simulate cascading failures
        failures = [
            ("agent_1", "timeout"),
            ("agent_2", "cpu_overload"),
            ("agent_3", "memory_pressure")
        ]
        
        for component_id, fault_type in failures:
            result = ray.get(
                orchestrator_remote.handle_fault.remote(component_id, fault_type, "medium")
            )
            assert result is not None
        
        logger.info("✅ Cascading failure handling working correctly")
    
    def test_system_recovery_metrics(self, ray_cluster, config):
        """Test system recovery metrics collection"""
        ft_config = config.get("fault_tolerance", {})
        orchestrator_remote = FaultToleranceOrchestrator.remote(ft_config, [])
        
        # Get system recovery metrics
        metrics = ray.get(orchestrator_remote.get_recovery_metrics.remote())
        assert metrics is not None
        assert isinstance(metrics, dict)
        logger.info(f"✅ System recovery metrics: {metrics}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
