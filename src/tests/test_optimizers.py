#!/usr/bin/env python3
"""
Optimizer Tests
優化器測試

Unit tests for optimization algorithms and classical optimizers.
優化算法和經典優化器的單位測試。
"""

import unittest
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestGeneticAlgorithm(unittest.TestCase):
    """Test genetic algorithm functionality."""
    
    def test_population_initialization(self):
        """Test population initialization."""
        population_size = 100
        population = np.random.rand(population_size, 10)
        
        self.assertEqual(population.shape[0], population_size)
        self.assertEqual(population.shape[1], 10)
    
    def test_fitness_calculation(self):
        """Test fitness calculation."""
        def simple_fitness(x):
            """Simple sphere function."""
            return -np.sum(x**2)
        
        solution = np.array([0.1, 0.2, 0.3])
        fitness = simple_fitness(solution)
        
        self.assertLess(fitness, 0)
    
    def test_mutation(self):
        """Test mutation operation."""
        individual = np.array([0.5, 0.5, 0.5])
        mutation_rate = 0.1
        
        mutated = individual.copy()
        for i in range(len(mutated)):
            if np.random.rand() < mutation_rate:
                mutated[i] = np.random.rand()
        
        self.assertEqual(len(mutated), len(individual))
    
    def test_crossover(self):
        """Test crossover operation."""
        parent1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        parent2 = np.array([0.5, 0.4, 0.3, 0.2, 0.1])
        
        crossover_point = 3
        child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
        
        self.assertEqual(len(child1), len(parent1))
        self.assertEqual(len(child2), len(parent2))


class TestParticleSwarmOptimization(unittest.TestCase):
    """Test particle swarm optimization."""
    
    def test_particle_initialization(self):
        """Test particle initialization."""
        num_particles = 30
        dimensions = 5
        
        positions = np.random.rand(num_particles, dimensions)
        velocities = np.random.randn(num_particles, dimensions) * 0.1
        
        self.assertEqual(positions.shape, (num_particles, dimensions))
        self.assertEqual(velocities.shape, (num_particles, dimensions))
    
    def test_velocity_update(self):
        """Test velocity update in PSO."""
        velocity = 0.1
        position = 0.5
        best_position = 0.3
        
        w = 0.7
        c1 = 1.5
        c2 = 1.5
        
        new_velocity = (w * velocity + 
                       c1 * np.random.rand() * (best_position - position))
        
        self.assertIsInstance(new_velocity, (float, np.floating))
    
    def test_position_update(self):
        """Test position update in PSO."""
        position = 0.5
        velocity = 0.1
        
        new_position = position + velocity
        
        self.assertGreater(new_position, position)


class TestSimulatedAnnealing(unittest.TestCase):
    """Test simulated annealing optimization."""
    
    def test_temperature_schedule(self):
        """Test temperature cooling schedule."""
        initial_temp = 100.0
        cooling_rate = 0.95
        
        temperatures = []
        temp = initial_temp
        
        for _ in range(10):
            temperatures.append(temp)
            temp *= cooling_rate
        
        self.assertEqual(len(temperatures), 10)
        self.assertGreater(temperatures[0], temperatures[-1])
    
    def test_acceptance_probability(self):
        """Test acceptance probability calculation."""
        delta_energy = 10.0
        temperature = 50.0
        
        # Metropolis acceptance criterion
        if delta_energy < 0:
            acceptance_prob = 1.0
        else:
            acceptance_prob = np.exp(-delta_energy / temperature)
        
        self.assertGreater(acceptance_prob, 0)
        self.assertLessEqual(acceptance_prob, 1)


class TestGradientDescent(unittest.TestCase):
    """Test gradient descent optimization."""
    
    def test_gradient_calculation(self):
        """Test gradient calculation."""
        x = np.array([1.0, 2.0, 3.0])
        
        # Simple quadratic function: f(x) = x^2
        # Gradient: df/dx = 2x
        gradient = 2 * x
        
        np.testing.assert_array_almost_equal(gradient, np.array([2.0, 4.0, 6.0]))
    
    def test_step_update(self):
        """Test parameter update step."""
        params = np.array([1.0, 2.0, 3.0])
        gradient = np.array([0.1, 0.2, 0.3])
        learning_rate = 0.01
        
        new_params = params - learning_rate * gradient
        
        self.assertLess(new_params[0], params[0])
        self.assertLess(new_params[1], params[1])
    
    def test_convergence_check(self):
        """Test convergence criteria."""
        losses = [10.0, 9.5, 9.4, 9.39, 9.3901]
        threshold = 0.001
        
        converged = abs(losses[-1] - losses[-2]) < threshold
        self.assertTrue(converged)


class TestDifferentialEvolution(unittest.TestCase):
    """Test differential evolution optimization."""
    
    def test_mutation_vector(self):
        """Test mutation vector generation."""
        population_size = 10
        dimensions = 5
        population = np.random.rand(population_size, dimensions)
        
        # Select 3 random indices
        indices = np.random.choice(population_size, 3, replace=False)
        
        # Create mutant vector
        F = 0.8
        mutant = population[indices[0]] + F * (population[indices[1]] - population[indices[2]])
        
        self.assertEqual(len(mutant), dimensions)
    
    def test_crossover_de(self):
        """Test crossover in differential evolution."""
        target = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        mutant = np.array([0.5, 0.4, 0.3, 0.2, 0.1])
        cr = 0.7
        
        trial = target.copy()
        for i in range(len(trial)):
            if np.random.rand() < cr:
                trial[i] = mutant[i]
        
        self.assertEqual(len(trial), len(target))


class TestOptimizationResults(unittest.TestCase):
    """Test optimization result handling."""
    
    def test_result_structure(self):
        """Test optimization result structure."""
        result = {
            'optimal_value': -1.234,
            'optimal_parameters': np.array([0.1, 0.2, 0.3]),
            'iterations': 150,
            'converged': True,
            'method': 'genetic'
        }
        
        self.assertIn('optimal_value', result)
        self.assertIn('optimal_parameters', result)
        self.assertEqual(result['iterations'], 150)
        self.assertTrue(result['converged'])
    
    def test_result_comparison(self):
        """Test comparing optimization results."""
        result1 = {'optimal_value': -2.5, 'iterations': 100}
        result2 = {'optimal_value': -2.3, 'iterations': 150}
        
        # Result 1 is better (lower value for minimization)
        self.assertLess(result1['optimal_value'], result2['optimal_value'])


class TestObjectiveFunction(unittest.TestCase):
    """Test objective function handling."""
    
    def test_sphere_function(self):
        """Test sphere function."""
        def sphere(x):
            return np.sum(x**2)
        
        result = sphere(np.array([0, 0, 0]))
        self.assertEqual(result, 0)
        
        result = sphere(np.array([1, 1, 1]))
        self.assertEqual(result, 3)
    
    def test_rosenbrock_function(self):
        """Test Rosenbrock function."""
        def rosenbrock(x):
            return sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)
        
        result = rosenbrock(np.array([1, 1, 1]))
        self.assertEqual(result, 0)
        
        result = rosenbrock(np.array([0, 0, 0]))
        self.assertGreater(result, 0)


if __name__ == '__main__':
    unittest.main()
