#!/usr/bin/env python3
"""
Classical Algorithm Optimizers
經典算法優化器

Provides classical algorithm implementations that serve as alternatives to quantum algorithms.
提供經典算法實現，作為量子算法的替代方案。
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
from scipy.optimize import minimize, differential_evolution

logger = logging.getLogger(__name__)


class OptimizationMethod(Enum):
    """優化方法枚舉 - Optimization Method Enumeration"""
    GENETIC = "genetic"
    PSO = "particle_swarm"
    SIMULATED_ANNEALING = "simulated_annealing"
    GRADIENT_DESCENT = "gradient_descent"
    DIFFERENTIAL_EVOLUTION = "differential_evolution"


@dataclass
class OptimizationResult:
    """優化結果 - Optimization Result"""
    optimal_value: float
    optimal_parameters: np.ndarray
    iterations: int
    converged: bool
    method: str


class GeneticAlgorithm:
    """遺傳算法 - Genetic Algorithm (替代量子退火)"""
    
    def __init__(
        self,
        population_size: int = 100,
        generations: int = 50,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
    
    def optimize(
        self,
        objective_func: Callable,
        bounds: List[Tuple[float, float]],
        maximization: bool = True
    ) -> OptimizationResult:
        """Run genetic algorithm optimization."""
        dimension = len(bounds)
        
        # Initialize population
        population = np.random.uniform(
            [b[0] for b in bounds],
            [b[1] for b in bounds],
            size=(self.population_size, dimension)
        )
        
        best_fitness = -np.inf if maximization else np.inf
        best_solution = population[0].copy()
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness = np.array([objective_func(ind) for ind in population])
            
            # Track best solution
            if maximization:
                gen_best_idx = np.argmax(fitness)
                gen_best_fitness = fitness[gen_best_idx]
                if gen_best_fitness > best_fitness:
                    best_fitness = gen_best_fitness
                    best_solution = population[gen_best_idx].copy()
            else:
                gen_best_idx = np.argmin(fitness)
                gen_best_fitness = fitness[gen_best_idx]
                if gen_best_fitness < best_fitness:
                    best_fitness = gen_best_fitness
                    best_solution = population[gen_best_idx].copy()
            
            # Selection, crossover, mutation
            new_population = []
            
            for _ in range(self.population_size):
                # Tournament selection
                idx1, idx2 = np.random.choice(self.population_size, 2, replace=False)
                if maximization:
                    parent1 = population[idx1] if fitness[idx1] > fitness[idx2] else population[idx2]
                    parent2 = population[idx2] if fitness[idx2] > fitness[idx1] else population[idx1]
                else:
                    parent1 = population[idx1] if fitness[idx1] < fitness[idx2] else population[idx2]
                    parent2 = population[idx2] if fitness[idx2] < fitness[idx1] else population[idx1]
                
                # Crossover
                if random.random() < self.crossover_rate:
                    offspring = 0.5 * parent1 + 0.5 * parent2
                else:
                    offspring = parent1.copy()
                
                # Mutation
                if random.random() < self.mutation_rate:
                    mutation_idx = random.randint(0, dimension - 1)
                    offspring[mutation_idx] = np.random.uniform(bounds[mutation_idx][0], bounds[mutation_idx][1])
                
                # Ensure within bounds
                for i, (low, high) in enumerate(bounds):
                    offspring[i] = np.clip(offspring[i], low, high)
                
                new_population.append(offspring)
            
            population = np.array(new_population)
        
        return OptimizationResult(
            optimal_value=best_fitness,
            optimal_parameters=best_solution,
            iterations=self.generations,
            converged=True,
            method="genetic_algorithm"
        )


class ParticleSwarmOptimizer:
    """粒子群優化 - Particle Swarm Optimization (替代量子尋優)"""
    
    def __init__(
        self,
        num_particles: int = 30,
        max_iterations: int = 100,
        cognitive_param: float = 2.0,
        social_param: float = 2.0,
        inertia_weight: float = 0.7
    ):
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.cognitive_param = cognitive_param
        self.social_param = social_param
        self.inertia_weight = inertia_weight
    
    def optimize(
        self,
        objective_func: Callable,
        bounds: List[Tuple[float, float]],
        maximization: bool = True
    ) -> OptimizationResult:
        """Run PSO optimization."""
        dimension = len(bounds)
        
        # Initialize particles and velocities
        positions = np.random.uniform(
            [b[0] for b in bounds],
            [b[1] for b in bounds],
            size=(self.num_particles, dimension)
        )
        
        velocities = np.random.uniform(-1, 1, size=(self.num_particles, dimension))
        
        # Track best positions
        best_positions = positions.copy()
        best_fitness = np.array([objective_func(p) for p in positions])
        
        if maximization:
            global_best_idx = np.argmax(best_fitness)
        else:
            global_best_idx = np.argmin(best_fitness)
        
        global_best = positions[global_best_idx].copy()
        global_best_fitness = best_fitness[global_best_idx]
        
        for iteration in range(self.max_iterations):
            for i in range(self.num_particles):
                # Update velocity
                r1, r2 = np.random.random(dimension), np.random.random(dimension)
                
                velocities[i] = (
                    self.inertia_weight * velocities[i] +
                    self.cognitive_param * r1 * (best_positions[i] - positions[i]) +
                    self.social_param * r2 * (global_best - positions[i])
                )
                
                # Update position
                positions[i] = positions[i] + velocities[i]
                
                # Boundary conditions
                for j, (low, high) in enumerate(bounds):
                    positions[i][j] = np.clip(positions[i][j], low, high)
                
                # Evaluate fitness
                fitness = objective_func(positions[i])
                
                if maximization:
                    if fitness > best_fitness[i]:
                        best_fitness[i] = fitness
                        best_positions[i] = positions[i].copy()
                else:
                    if fitness < best_fitness[i]:
                        best_fitness[i] = fitness
                        best_positions[i] = positions[i].copy()
                
                # Update global best
                if maximization:
                    if fitness > global_best_fitness:
                        global_best_fitness = fitness
                        global_best = positions[i].copy()
                else:
                    if fitness < global_best_fitness:
                        global_best_fitness = fitness
                        global_best = positions[i].copy()
        
        return OptimizationResult(
            optimal_value=global_best_fitness,
            optimal_parameters=global_best,
            iterations=self.max_iterations,
            converged=True,
            method="particle_swarm_optimization"
        )


class SimulatedAnnealing:
    """模擬退火 - Simulated Annealing"""
    
    def __init__(
        self,
        initial_temperature: float = 100.0,
        cooling_rate: float = 0.95,
        max_iterations: int = 1000
    ):
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations
    
    def optimize(
        self,
        objective_func: Callable,
        bounds: List[Tuple[float, float]],
        maximization: bool = True
    ) -> OptimizationResult:
        """Run simulated annealing optimization."""
        dimension = len(bounds)
        
        # Initialize solution
        current_solution = np.random.uniform(
            [b[0] for b in bounds],
            [b[1] for b in bounds]
        )
        
        current_fitness = objective_func(current_solution)
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        
        temperature = self.initial_temperature
        
        for iteration in range(self.max_iterations):
            # Generate neighbor solution
            neighbor_solution = current_solution.copy()
            random_idx = random.randint(0, dimension - 1)
            perturbation = np.random.normal(0, temperature / 10)
            neighbor_solution[random_idx] += perturbation
            
            # Boundary conditions
            for i, (low, high) in enumerate(bounds):
                neighbor_solution[i] = np.clip(neighbor_solution[i], low, high)
            
            neighbor_fitness = objective_func(neighbor_solution)
            
            # Metropolis criterion
            if maximization:
                delta = neighbor_fitness - current_fitness
            else:
                delta = current_fitness - neighbor_fitness
            
            if delta > 0 or random.random() < np.exp(delta / temperature):
                current_solution = neighbor_solution.copy()
                current_fitness = neighbor_fitness
                
                if maximization:
                    if current_fitness > best_fitness:
                        best_fitness = current_fitness
                        best_solution = current_solution.copy()
                else:
                    if current_fitness < best_fitness:
                        best_fitness = current_fitness
                        best_solution = current_solution.copy()
            
            # Cool down
            temperature *= self.cooling_rate
        
        return OptimizationResult(
            optimal_value=best_fitness,
            optimal_parameters=best_solution,
            iterations=self.max_iterations,
            converged=True,
            method="simulated_annealing"
        )


class ClassicalOptimizer:
    """經典優化器統一接口 - Classical Optimizer Unified Interface"""
    
    def __init__(self, method: OptimizationMethod = OptimizationMethod.PSO):
        self.method = method
        
        if method == OptimizationMethod.GENETIC:
            self.optimizer = GeneticAlgorithm()
        elif method == OptimizationMethod.PSO:
            self.optimizer = ParticleSwarmOptimizer()
        elif method == OptimizationMethod.SIMULATED_ANNEALING:
            self.optimizer = SimulatedAnnealing()
        else:
            self.optimizer = ParticleSwarmOptimizer()
    
    def optimize(
        self,
        objective_func: Callable,
        bounds: List[Tuple[float, float]],
        maximization: bool = True
    ) -> OptimizationResult:
        """Run optimization using configured method."""
        logger.info(f"🚀 Starting {self.method.value} optimization")
        
        result = self.optimizer.optimize(objective_func, bounds, maximization)
        
        logger.info(f"✅ Optimization completed: {result.optimal_value:.6f}")
        
        return result


# 別名和額外的優化器
class GradientDescent:
    """梯度下降法 - Gradient Descent"""
    
    def __init__(self, learning_rate: float = 0.01, max_iterations: int = 100):
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
    
    def optimize(self, objective_func: Callable, initial_point=None, **kwargs):
        """Simple gradient descent optimization"""
        if initial_point is None:
            initial_point = np.array([0.0, 0.0])
        
        current = initial_point.copy()
        best_value = objective_func(current)
        best_point = current.copy()
        
        for iteration in range(self.max_iterations):
            # 簡單的數值梯度
            gradient = np.zeros_like(current)
            eps = 1e-5
            
            for i in range(len(current)):
                current[i] += eps
                gradient[i] = (objective_func(current) - best_value) / eps
                current[i] -= eps
            
            # 更新
            current = current - self.learning_rate * gradient
            value = objective_func(current)
            
            if value < best_value:
                best_value = value
                best_point = current.copy()
        
        return {
            'best_value': best_value,
            'best_params': best_point,
            'iterations': self.max_iterations
        }


class DifferentialEvolution:
    """差分進化 - Differential Evolution"""
    
    def __init__(self, population_size: int = 50, generations: int = 100, 
                 f: float = 0.7, cr: float = 0.9):
        self.population_size = population_size
        self.generations = generations
        self.f = f  # Mutation factor
        self.cr = cr  # Crossover rate
    
    def optimize(self, objective_func: Callable, bounds=None, **kwargs):
        """Run differential evolution"""
        if bounds is None:
            bounds = [(-5, 5), (-5, 5)]
        
        dimension = len(bounds)
        
        # Initialize population
        population = np.random.uniform(
            [b[0] for b in bounds],
            [b[1] for b in bounds],
            size=(self.population_size, dimension)
        )
        
        fitness = np.array([objective_func(ind) for ind in population])
        best_idx = np.argmin(fitness)
        best_value = fitness[best_idx]
        best_solution = population[best_idx].copy()
        
        for generation in range(self.generations):
            for i in range(self.population_size):
                # Select three random indices different from i
                candidates = list(range(self.population_size))
                candidates.remove(i)
                a, b, c = np.random.choice(candidates, 3, replace=False)
                
                # Mutation
                mutant = population[a] + self.f * (population[b] - population[c])
                
                # Boundary handling
                for j, (low, high) in enumerate(bounds):
                    mutant[j] = np.clip(mutant[j], low, high)
                
                # Crossover
                trial = population[i].copy()
                for j in range(dimension):
                    if np.random.random() < self.cr:
                        trial[j] = mutant[j]
                
                # Selection
                trial_fitness = objective_func(trial)
                if trial_fitness < fitness[i]:
                    population[i] = trial.copy()
                    fitness[i] = trial_fitness
                    
                    if trial_fitness < best_value:
                        best_value = trial_fitness
                        best_solution = trial.copy()
        
        return {
            'best_value': best_value,
            'best_params': best_solution,
            'iterations': self.generations
        }


# 別名以支持不同的命名
ParticleSwarmOptimization = ParticleSwarmOptimizer



# Example usage
if __name__ == '__main__':
    # Example objective function (Rosenbrock function)
    def rosenbrock(x):
        return -sum(100 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
    
    bounds = [(-5, 5), (-5, 5), (-5, 5)]
    
    # Test different optimizers
    for method in [OptimizationMethod.GENETIC, OptimizationMethod.PSO, OptimizationMethod.SIMULATED_ANNEALING]:
        optimizer = ClassicalOptimizer(method)
        result = optimizer.optimize(rosenbrock, bounds, maximization=False)
        print(f"{method.value}: {result.optimal_value:.6f}")
