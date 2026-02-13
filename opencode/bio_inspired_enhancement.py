#!/usr/bin/env python3
"""
Bio-Inspired Agent Self-Enhancement System
生物啟發代理自我強化系統

Advanced evolutionary algorithms for agent self-improvement and breakthrough capabilities.
Uses genetic algorithms, neural adaptation, and quantum-inspired evolution.
"""

import yaml
import logging
import math
import random
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EvolutionStrategy(Enum):
    """Agent evolution strategies"""
    GENETIC = "genetic"
    NEURAL_ADAPTATION = "neural_adaptation"
    QUANTUM_INSPIRED = "quantum_inspired"
    SWARM_INTELLIGENCE = "swarm_intelligence"
    MEMETIC = "memetic"


class AdaptationMechanism(Enum):
    """Adaptation mechanisms"""
    LEARNING_RATE_ADJUSTMENT = "learning_rate_adjustment"
    CAPABILITY_EXPANSION = "capability_expansion"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    RESOURCE_REALLOCATION = "resource_reallocation"
    STRATEGY_MUTATION = "strategy_mutation"


@dataclass
class AdaptationMetrics:
    """Track agent adaptation and evolution metrics"""
    
    performance_history: List[float] = field(default_factory=list)
    capability_scores: Dict[str, float] = field(default_factory=dict)
    evolution_generation: int = 0
    mutation_rate: float = 0.05
    adaptation_rate: float = 0.01
    fitness_trend: float = 0.0  # Trend of fitness improvements
    breakthrough_events: int = 0
    last_breakthrough: Optional[datetime] = None
    
    def add_performance(self, score: float) -> None:
        """Add performance score and update trend"""
        self.performance_history.append(score)
        
        # Update fitness trend (exponential moving average)
        if len(self.performance_history) > 1:
            prev_avg = np.mean(self.performance_history[-10:-1]) if len(self.performance_history) > 10 else self.performance_history[-2]
            curr_avg = np.mean(self.performance_history[-5:]) if len(self.performance_history) > 5 else score
            self.fitness_trend = (curr_avg - prev_avg) / max(prev_avg, 0.001)
    
    def get_average_performance(self, window: int = 10) -> float:
        """Get average performance over recent window"""
        if not self.performance_history:
            return 0.0
        return float(np.mean(self.performance_history[-window:]))
    
    def is_improving(self, threshold: float = 0.02) -> bool:
        """Check if agent is improving"""
        return self.fitness_trend > threshold


class GeneticGene:
    """Represents a gene for agent evolution"""
    
    def __init__(self, name: str, value: float, min_val: float = 0.0, max_val: float = 1.0):
        self.name = name
        self.value = max(min_val, min(max_val, value))
        self.min_val = min_val
        self.max_val = max_val
        self.mutation_history: List[float] = [value]
    
    def mutate(self, mutation_rate: float = 0.1) -> float:
        """Apply mutation to gene"""
        if random.random() < mutation_rate:
            # Gaussian mutation
            mutation = np.random.normal(0, 0.1)
            new_value = self.value + mutation
            self.value = max(self.min_val, min(self.max_val, new_value))
            self.mutation_history.append(self.value)
        return self.value
    
    def crossover(self, other: 'GeneticGene') -> 'GeneticGene':
        """Blend two genes"""
        blend_value = (self.value + other.value) / 2
        return GeneticGene(self.name, blend_value, self.min_val, self.max_val)


@dataclass
class AgentGenome:
    """Genetic representation of agent capabilities"""
    
    genes: Dict[str, GeneticGene] = field(default_factory=dict)
    fitness_score: float = 0.0
    age: int = 0
    parent_genomes: List['AgentGenome'] = field(default_factory=list)
    
    def mutate(self, mutation_rate: float = 0.05) -> None:
        """Mutate all genes"""
        for gene in self.genes.values():
            gene.mutate(mutation_rate)
    
    def crossover(self, other: 'AgentGenome') -> 'AgentGenome':
        """Create offspring genome from two parents"""
        offspring = AgentGenome()
        offspring.parent_genomes = [self, other]
        
        for gene_name, gene in self.genes.items():
            if gene_name in other.genes:
                offspring.genes[gene_name] = gene.crossover(other.genes[gene_name])
            else:
                offspring.genes[gene_name] = GeneticGene(
                    gene.name, 
                    gene.value, 
                    gene.min_val, 
                    gene.max_val
                )
        
        return offspring
    
    def get_phenotype(self) -> Dict[str, float]:
        """Get phenotype (expressed traits) from genotype"""
        return {name: gene.value for name, gene in self.genes.items()}


class EvolutionEngine:
    """Core evolutionary algorithm for agent enhancement"""
    
    def __init__(
        self,
        population_size: int = 20,
        generations: int = 50,
        mutation_rate: float = 0.05,
        crossover_rate: float = 0.7,
        elite_percentage: float = 0.1,
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_percentage = elite_percentage
        self.population: List[AgentGenome] = []
        self.best_genome: Optional[AgentGenome] = None
        self.fitness_history: List[float] = []
    
    def initialize_population(self, capability_names: List[str]) -> None:
        """Initialize population with random genomes"""
        self.population = []
        for _ in range(self.population_size):
            genome = AgentGenome()
            for cap_name in capability_names:
                genome.genes[cap_name] = GeneticGene(cap_name, random.random())
            self.population.append(genome)
        logger.info(f"🧬 Initialized population with {len(self.population)} genomes")
    
    def evaluate_fitness(self, genome: AgentGenome, fitness_func) -> float:
        """Evaluate fitness of a genome"""
        phenotype = genome.get_phenotype()
        fitness = fitness_func(phenotype)
        genome.fitness_score = fitness
        return fitness
    
    def select_parents(self) -> Tuple[AgentGenome, AgentGenome]:
        """Tournament selection"""
        tournament_size = 3
        tournament = random.sample(self.population, tournament_size)
        parent1 = max(tournament, key=lambda g: g.fitness_score)
        
        tournament = random.sample(self.population, tournament_size)
        parent2 = max(tournament, key=lambda g: g.fitness_score)
        
        return parent1, parent2
    
    def evolve(self, fitness_func) -> Tuple[AgentGenome, List[float]]:
        """Run evolution for specified generations"""
        for generation in range(self.generations):
            # Evaluate fitness
            for genome in self.population:
                self.evaluate_fitness(genome, fitness_func)
            
            # Sort by fitness
            self.population.sort(key=lambda g: g.fitness_score, reverse=True)
            
            # Track best
            if self.best_genome is None or self.population[0].fitness_score > self.best_genome.fitness_score:
                self.best_genome = self.population[0]
            
            best_fitness = self.best_genome.fitness_score
            self.fitness_history.append(best_fitness)
            
            logger.info(f"  Generation {generation+1}: Best fitness = {best_fitness:.4f}")
            
            # Elitism - keep top individuals
            elite_count = max(1, int(self.population_size * self.elite_percentage))
            elite = self.population[:elite_count]
            
            # Create new population
            new_population = elite.copy()
            
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    parent1, parent2 = self.select_parents()
                    offspring = parent1.crossover(parent2)
                else:
                    parent, _ = self.select_parents()
                    offspring = AgentGenome()
                    offspring.genes = {name: GeneticGene(gene.name, gene.value, gene.min_val, gene.max_val) 
                                      for name, gene in parent.genes.items()}
                
                offspring.mutate(self.mutation_rate)
                new_population.append(offspring)
            
            self.population = new_population[:self.population_size]
        
        logger.info(f"✅ Evolution complete. Best fitness: {self.best_genome.fitness_score:.4f}")
        return self.best_genome, self.fitness_history


class NeuralAdaptationEngine:
    """Neural network-based adaptation for agents"""
    
    def __init__(self, learning_rate: float = 0.01, hidden_units: int = 32):
        self.learning_rate = learning_rate
        self.hidden_units = hidden_units
        self.weights_hidden: Optional[np.ndarray] = None
        self.weights_output: Optional[np.ndarray] = None
        self.bias_hidden: Optional[np.ndarray] = None
        self.bias_output: Optional[np.ndarray] = None
    
    def initialize(self, input_size: int, output_size: int) -> None:
        """Initialize neural network"""
        self.weights_hidden = np.random.randn(input_size, self.hidden_units) * 0.01
        self.weights_output = np.random.randn(self.hidden_units, output_size) * 0.01
        self.bias_hidden = np.zeros((1, self.hidden_units))
        self.bias_output = np.zeros((1, output_size))
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass"""
        # Hidden layer with ReLU
        hidden = np.maximum(0, np.dot(inputs, self.weights_hidden) + self.bias_hidden)
        # Output layer with sigmoid
        output = 1 / (1 + np.exp(-np.dot(hidden, self.weights_output) - self.bias_output))
        return output
    
    def adapt(self, inputs: np.ndarray, targets: np.ndarray) -> float:
        """Single adaptation step"""
        # Forward pass
        hidden = np.maximum(0, np.dot(inputs, self.weights_hidden) + self.bias_hidden)
        output = 1 / (1 + np.exp(-np.dot(hidden, self.weights_output) - self.bias_output))
        
        # Compute loss
        loss = np.mean((output - targets) ** 2)
        
        # Backward pass (simplified)
        output_error = output - targets
        hidden_error = np.dot(output_error, self.weights_output.T) * (hidden > 0)
        
        # Update weights
        self.weights_output -= self.learning_rate * np.dot(hidden.T, output_error)
        self.bias_output -= self.learning_rate * np.sum(output_error, axis=0, keepdims=True)
        self.weights_hidden -= self.learning_rate * np.dot(inputs.T, hidden_error)
        self.bias_hidden -= self.learning_rate * np.sum(hidden_error, axis=0, keepdims=True)
        
        return loss


class BioInspiredAgentEnhancer:
    """Main system for agent self-enhancement"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.adaptation_metrics: Dict[str, AdaptationMetrics] = {}
        self.evolution_engines: Dict[str, EvolutionEngine] = {}
        self.neural_engines: Dict[str, NeuralAdaptationEngine] = {}
        self.strategy = EvolutionStrategy.GENETIC
        logger.info("🧬 Bio-Inspired Agent Enhancer initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML"""
        config = {
            'auto_optimization': {'enabled': True, 'adaptation_rate': 0.01, 'improvement_threshold': 0.05},
            'quantum_optimization': {'coherence_preservation': 0.9, 'energy_saving_mode': True},
            'experience_based': {'decision_weight': 0.4, 'knowledge_transfer': True},
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        config.update(file_config)
                logger.info(f"✅ Loaded config from {config_path}")
            except Exception as e:
                logger.warning(f"⚠️  Could not load config: {e}")
        
        return config
    
    def initialize_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """Initialize enhancement system for an agent"""
        self.adaptation_metrics[agent_id] = AdaptationMetrics()
        
        # Initialize evolution engine
        self.evolution_engines[agent_id] = EvolutionEngine(
            population_size=20,
            generations=10,
            mutation_rate=self.config['auto_optimization'].get('adaptation_rate', 0.01),
        )
        self.evolution_engines[agent_id].initialize_population(capabilities)
        
        # Initialize neural adaptation
        self.neural_engines[agent_id] = NeuralAdaptationEngine(
            learning_rate=self.config['auto_optimization'].get('adaptation_rate', 0.01),
        )
        self.neural_engines[agent_id].initialize(len(capabilities), 1)
        
        logger.info(f"🧬 Enhanced agent {agent_id} with {len(capabilities)} capabilities")
    
    def report_performance(self, agent_id: str, performance_score: float) -> None:
        """Report agent performance for evolution"""
        if agent_id not in self.adaptation_metrics:
            return
        
        metrics = self.adaptation_metrics[agent_id]
        metrics.add_performance(performance_score)
        
        # Check for breakthrough
        if metrics.fitness_trend > 0.1:  # 10% improvement
            metrics.breakthrough_events += 1
            metrics.last_breakthrough = datetime.now()
            logger.info(f"⚡ BREAKTHROUGH! Agent {agent_id} breakthrough #{metrics.breakthrough_events}")
            logger.info(f"   Performance improved by {metrics.fitness_trend*100:.1f}%")
    
    def evolve_agent(
        self,
        agent_id: str,
        fitness_func,
        generations: int = 5
    ) -> Tuple[Dict[str, float], float]:
        """Evolve agent capabilities"""
        if agent_id not in self.evolution_engines:
            logger.warning(f"Agent {agent_id} not initialized for evolution")
            return {}, 0.0
        
        engine = self.evolution_engines[agent_id]
        engine.generations = generations
        
        logger.info(f"🧬 Evolving agent {agent_id} for {generations} generations...")
        best_genome, history = engine.evolve(fitness_func)
        
        phenotype = best_genome.get_phenotype()
        best_fitness = best_genome.fitness_score
        
        logger.info(f"✅ Agent {agent_id} evolution complete")
        logger.info(f"   Best fitness: {best_fitness:.4f}")
        logger.info(f"   Improved capabilities: {phenotype}")
        
        return phenotype, best_fitness
    
    def adapt_agent(
        self,
        agent_id: str,
        performance_data: np.ndarray,
        target_data: np.ndarray,
        iterations: int = 100
    ) -> float:
        """Adapt agent using neural network"""
        if agent_id not in self.neural_engines:
            logger.warning(f"Agent {agent_id} not initialized for adaptation")
            return 0.0
        
        engine = self.neural_engines[agent_id]
        
        logger.info(f"🧠 Adapting agent {agent_id} with neural learning...")
        
        total_loss = 0.0
        for i in range(iterations):
            loss = engine.adapt(performance_data, target_data)
            total_loss += loss
            
            if (i + 1) % 20 == 0:
                logger.info(f"   Iteration {i+1}: Loss = {loss:.4f}")
        
        final_loss = total_loss / iterations
        logger.info(f"✅ Agent {agent_id} adaptation complete. Final loss: {final_loss:.4f}")
        
        return final_loss
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get enhancement status for agent"""
        if agent_id not in self.adaptation_metrics:
            return {}
        
        metrics = self.adaptation_metrics[agent_id]
        
        return {
            'average_performance': metrics.get_average_performance(),
            'fitness_trend': metrics.fitness_trend,
            'is_improving': metrics.is_improving(),
            'generation': metrics.evolution_generation,
            'breakthrough_events': metrics.breakthrough_events,
            'last_breakthrough': metrics.last_breakthrough.isoformat() if metrics.last_breakthrough else None,
            'mutation_rate': metrics.mutation_rate,
            'adaptation_rate': metrics.adaptation_rate,
        }
    
    def apply_breakthrough_enhancement(self, agent_id: str, enhancement_level: float = 1.5) -> Dict[str, Any]:
        """Apply breakthrough enhancement to agent"""
        if agent_id not in self.adaptation_metrics:
            return {}
        
        metrics = self.adaptation_metrics[agent_id]
        
        # Increase capability scores
        for cap_name, score in metrics.capability_scores.items():
            metrics.capability_scores[cap_name] = min(1.0, score * enhancement_level)
        
        # Reduce mutation rate for stability
        metrics.mutation_rate *= 0.8
        
        logger.info(f"⚡ Applied breakthrough enhancement to {agent_id}")
        logger.info(f"   Enhancement level: {enhancement_level:.1f}x")
        
        return metrics.capability_scores


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create enhancer
    enhancer = BioInspiredAgentEnhancer()
    
    # Initialize agents
    enhancer.initialize_agent('trading_agent', ['signal_generation', 'risk_analysis', 'position_sizing'])
    enhancer.initialize_agent('market_agent', ['technical_analysis', 'sentiment_analysis', 'pattern_recognition'])
    
    # Simulate performance reporting
    for i in range(10):
        enhancer.report_performance('trading_agent', 0.6 + i * 0.03)
        enhancer.report_performance('market_agent', 0.5 + i * 0.02)
    
    # Get agent status
    status = enhancer.get_agent_status('trading_agent')
    print(f"\nTrading Agent Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Apply breakthrough
    print(f"\nApplying breakthrough enhancement...")
    enhancements = enhancer.apply_breakthrough_enhancement('trading_agent')
