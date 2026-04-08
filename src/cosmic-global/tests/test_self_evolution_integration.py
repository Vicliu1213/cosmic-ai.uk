#!/usr/bin/env python3
"""
Self-Evolution Learning Integration Test
自進化學習系統集成測試
"""

import pytest
import ray
import yaml
import logging
import numpy as np
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cosmic.self_evolution import (
    PPOLearner,
    CMAESEvolutionStrategy,
    KnowledgeDistiller,
    SelfEvolutionEngine
)

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


class TestPPOLearner:
    """Test Proximal Policy Optimization Learner"""
    
    def test_ppo_learner_initialization(self):
        """Test PPOLearner initialization"""
        config = {
            "learning_rate": 0.001,
            "gamma": 0.99,
            "gae_lambda": 0.95,
            "clip_ratio": 0.2
        }
        learner = PPOLearner(config)
        assert learner is not None
        assert learner.learning_rate == 0.001
        logger.info("✅ PPOLearner initialized successfully")
    
    def test_policy_optimization(self):
        """Test policy optimization"""
        config = {
            "learning_rate": 0.001,
            "gamma": 0.99,
            "gae_lambda": 0.95,
            "clip_ratio": 0.2
        }
        learner = PPOLearner(config)
        
        # Create sample trajectory
        trajectory = {
            "states": np.random.rand(10, 5),
            "actions": np.random.randint(0, 3, 10),
            "rewards": np.random.rand(10),
            "values": np.random.rand(10)
        }
        
        # Optimize policy
        loss = learner.optimize_policy(trajectory)
        assert loss is not None
        assert isinstance(loss, (float, np.floating))
        logger.info(f"✅ Policy optimization loss: {loss}")
    
    def test_advantage_estimation(self):
        """Test advantage estimation (GAE)"""
        config = {
            "learning_rate": 0.001,
            "gamma": 0.99,
            "gae_lambda": 0.95,
            "clip_ratio": 0.2
        }
        learner = PPOLearner(config)
        
        # Estimate advantages
        rewards = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
        values = np.array([0.9, 1.8, 2.8, 1.9, 0.95])
        
        advantages = learner.estimate_advantages(rewards, values)
        assert advantages is not None
        assert len(advantages) == len(rewards)
        logger.info(f"✅ Advantages estimated: {advantages}")
    
    def test_entropy_regularization(self):
        """Test entropy regularization for exploration"""
        config = {
            "learning_rate": 0.001,
            "gamma": 0.99,
            "gae_lambda": 0.95,
            "entropy_coeff": 0.01
        }
        learner = PPOLearner(config)
        
        # Sample actions from policy
        state = np.random.rand(5)
        action_probs = learner.get_action_distribution(state)
        
        # Calculate entropy
        entropy = learner.calculate_entropy(action_probs)
        assert entropy is not None
        assert entropy >= 0
        logger.info(f"✅ Entropy regularization calculated: {entropy}")


class TestCMAESEvolutionStrategy:
    """Test CMA-ES Evolution Strategy"""
    
    def test_cma_es_initialization(self):
        """Test CMAESEvolutionStrategy initialization"""
        config = {
            "population_size": 30,
            "mutation_rate": 0.15,
            "selection_pressure": 2.0
        }
        strategy = CMAESEvolutionStrategy(config)
        assert strategy is not None
        assert strategy.population_size == 30
        logger.info("✅ CMAESEvolutionStrategy initialized successfully")
    
    def test_population_initialization(self):
        """Test population initialization"""
        config = {
            "population_size": 30,
            "mutation_rate": 0.15,
            "selection_pressure": 2.0
        }
        strategy = CMAESEvolutionStrategy(config)
        
        # Initialize population
        genome_size = 10
        population = strategy.initialize_population(genome_size)
        
        assert population is not None
        assert len(population) == 30
        assert all(len(individual) == genome_size for individual in population)
        logger.info(f"✅ Population initialized: {len(population)} individuals")
    
    def test_selection_and_mutation(self):
        """Test selection and mutation"""
        config = {
            "population_size": 30,
            "mutation_rate": 0.15,
            "selection_pressure": 2.0
        }
        strategy = CMAESEvolutionStrategy(config)
        
        # Create population with fitness scores
        population = np.random.rand(30, 10)
        fitness_scores = np.random.rand(30)
        
        # Select and mutate
        new_population = strategy.evolve(population, fitness_scores)
        assert new_population is not None
        assert len(new_population) == 30
        logger.info("✅ Selection and mutation performed")
    
    def test_covariance_matrix_adaptation(self):
        """Test covariance matrix adaptation"""
        config = {
            "population_size": 30,
            "mutation_rate": 0.15,
            "selection_pressure": 2.0
        }
        strategy = CMAESEvolutionStrategy(config)
        
        # Get covariance matrix
        genome_size = 10
        cov_matrix = strategy.get_covariance_matrix(genome_size)
        
        assert cov_matrix is not None
        assert cov_matrix.shape == (genome_size, genome_size)
        logger.info(f"✅ Covariance matrix adapted: shape {cov_matrix.shape}")


class TestKnowledgeDistiller:
    """Test Knowledge Distillation"""
    
    def test_knowledge_distiller_initialization(self):
        """Test KnowledgeDistiller initialization"""
        config = {
            "temperature": 3.0,
            "alpha": 0.5
        }
        distiller = KnowledgeDistiller(config)
        assert distiller is not None
        assert distiller.temperature == 3.0
        logger.info("✅ KnowledgeDistiller initialized successfully")
    
    def test_teacher_student_distillation(self):
        """Test teacher-student knowledge distillation"""
        config = {
            "temperature": 3.0,
            "alpha": 0.5
        }
        distiller = KnowledgeDistiller(config)
        
        # Teacher and student outputs
        teacher_logits = np.random.rand(10)
        student_logits = np.random.rand(10)
        
        # Distillation loss
        distillation_loss = distiller.calculate_distillation_loss(
            teacher_logits, student_logits
        )
        assert distillation_loss is not None
        assert distillation_loss >= 0
        logger.info(f"✅ Distillation loss: {distillation_loss}")
    
    def test_knowledge_transfer(self):
        """Test knowledge transfer from teacher to student"""
        config = {
            "temperature": 3.0,
            "alpha": 0.5
        }
        distiller = KnowledgeDistiller(config)
        
        # Transfer knowledge
        teacher_model = {"weights": np.random.rand(10, 5)}
        student_model = distiller.transfer_knowledge(teacher_model)
        
        assert student_model is not None
        assert "weights" in student_model
        logger.info("✅ Knowledge transferred to student model")


class TestSelfEvolutionEngine:
    """Test complete Self-Evolution Engine"""
    
    def test_engine_initialization(self, ray_cluster, config):
        """Test SelfEvolutionEngine initialization"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        assert engine_remote is not None
        logger.info("✅ SelfEvolutionEngine initialized successfully")
    
    def test_learning_algorithm_selection(self, ray_cluster, config):
        """Test learning algorithm selection"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        
        # Test different algorithms
        algorithms = ["ppo", "cma_es", "hybrid"]
        for algo in algorithms:
            result = ray.get(engine_remote.select_algorithm.remote(algo))
            assert result is not None
            logger.info(f"✅ Algorithm '{algo}' selected successfully")
    
    def test_policy_learning_step(self, ray_cluster, config):
        """Test single learning step"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        
        # Perform learning step
        experience = {
            "states": [[1.0, 2.0, 3.0]],
            "actions": [0],
            "rewards": [1.0]
        }
        
        result = ray.get(engine_remote.update_policy.remote(experience))
        assert result is not None
        logger.info(f"✅ Policy learning step completed: {result}")
    
    def test_exploration_exploitation_balance(self, ray_cluster, config):
        """Test exploration-exploitation balance"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        
        # Get current exploration rate
        exploration_rate = ray.get(engine_remote.get_exploration_rate.remote())
        assert exploration_rate is not None
        assert 0 <= exploration_rate <= 1.0
        
        logger.info(f"✅ Exploration rate: {exploration_rate}")


class TestSelfEvolutionIntegration:
    """Integration tests for self-evolution with other systems"""
    
    def test_multi_agent_learning(self, ray_cluster, config):
        """Test multi-agent learning coordination"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        
        # Simulate learning from multiple agents
        for agent_id in range(3):
            experience = {
                "agent_id": agent_id,
                "rewards": [1.0, 2.0, 1.5]
            }
            result = ray.get(engine_remote.aggregate_experience.remote(experience))
            assert result is not None
        
        logger.info("✅ Multi-agent learning coordinated successfully")
    
    def test_continuous_improvement(self, ray_cluster, config):
        """Test continuous improvement over training steps"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        
        # Track performance over multiple updates
        performance_history = []
        for step in range(5):
            metrics = ray.get(engine_remote.get_learning_metrics.remote())
            if metrics and "performance" in metrics:
                performance_history.append(metrics["performance"])
        
        assert len(performance_history) > 0
        logger.info(f"✅ Performance history tracked: {performance_history}")
    
    def test_curriculum_learning(self, ray_cluster, config):
        """Test curriculum learning progression"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        
        # Progress through curriculum stages
        for stage in range(3):
            result = ray.get(engine_remote.advance_curriculum.remote(stage))
            assert result is not None
        
        logger.info("✅ Curriculum learning progression completed")
    
    def test_knowledge_distillation_pipeline(self, ray_cluster, config):
        """Test knowledge distillation in learning pipeline"""
        se_config = config.get("self_evolution", {})
        engine_remote = SelfEvolutionEngine.remote(se_config, [])
        
        # Test distillation integration
        result = ray.get(engine_remote.run_distillation_cycle.remote())
        assert result is not None
        
        logger.info("✅ Knowledge distillation pipeline executed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
