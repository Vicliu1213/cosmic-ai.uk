#!/usr/bin/env python3
"""
Classical Algorithm Optimizer Tests
經典算法優化器測試

Unit tests for GeneticAlgorithm, ParticleSwarmOptimizer, SimulatedAnnealing,
ClassicalOptimizer, GradientDescent, and DifferentialEvolution.
"""

import sys
import math
from pathlib import Path

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from optimizer.classical_algorithms import (
    ClassicalOptimizer,
    DifferentialEvolution,
    GeneticAlgorithm,
    GradientDescent,
    OptimizationMethod,
    OptimizationResult,
    ParticleSwarmOptimizer,
    ParticleSwarmOptimization,
    SimulatedAnnealing,
)


# ---------------------------------------------------------------------------
# Shared test objective functions
# ---------------------------------------------------------------------------

def sphere(x: np.ndarray) -> float:
    """Sphere function – global minimum at origin (value 0)."""
    return float(np.sum(x ** 2))


def neg_sphere(x: np.ndarray) -> float:
    """Negated sphere for maximisation tests – maximum at origin (value 0)."""
    return -float(np.sum(x ** 2))


BOUNDS_2D = [(-5.0, 5.0), (-5.0, 5.0)]
BOUNDS_3D = [(-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0)]


# ---------------------------------------------------------------------------
# OptimizationResult
# ---------------------------------------------------------------------------

class TestOptimizationResult:
    """Tests for the OptimizationResult dataclass."""

    def test_creation(self):
        result = OptimizationResult(
            optimal_value=0.0,
            optimal_parameters=np.array([0.0, 0.0]),
            iterations=50,
            converged=True,
            method="test",
        )
        assert result.optimal_value == 0.0
        assert result.iterations == 50
        assert result.converged is True
        assert result.method == "test"
        assert len(result.optimal_parameters) == 2


# ---------------------------------------------------------------------------
# OptimizationMethod enum
# ---------------------------------------------------------------------------

class TestOptimizationMethod:
    """Tests for the OptimizationMethod enum."""

    def test_values(self):
        assert OptimizationMethod.GENETIC.value == "genetic"
        assert OptimizationMethod.PSO.value == "particle_swarm"
        assert OptimizationMethod.SIMULATED_ANNEALING.value == "simulated_annealing"
        assert OptimizationMethod.GRADIENT_DESCENT.value == "gradient_descent"
        assert OptimizationMethod.DIFFERENTIAL_EVOLUTION.value == "differential_evolution"

    def test_all_methods_present(self):
        expected = {"genetic", "particle_swarm", "simulated_annealing",
                    "gradient_descent", "differential_evolution"}
        actual = {m.value for m in OptimizationMethod}
        assert expected == actual


# ---------------------------------------------------------------------------
# GeneticAlgorithm
# ---------------------------------------------------------------------------

class TestGeneticAlgorithm:
    """Tests for GeneticAlgorithm."""

    def test_default_parameters(self):
        ga = GeneticAlgorithm()
        assert ga.population_size == 100
        assert ga.generations == 50
        assert 0 < ga.mutation_rate <= 1
        assert 0 < ga.crossover_rate <= 1

    def test_custom_parameters(self):
        ga = GeneticAlgorithm(population_size=20, generations=10,
                              mutation_rate=0.2, crossover_rate=0.7)
        assert ga.population_size == 20
        assert ga.generations == 10

    def test_returns_optimization_result(self):
        ga = GeneticAlgorithm(population_size=20, generations=5)
        result = ga.optimize(sphere, BOUNDS_2D, maximization=False)
        assert isinstance(result, OptimizationResult)

    def test_minimization_finds_near_zero(self):
        np.random.seed(42)
        ga = GeneticAlgorithm(population_size=50, generations=30)
        result = ga.optimize(sphere, BOUNDS_2D, maximization=False)
        assert result.optimal_value < 5.0  # should be considerably below worst-case 50

    def test_maximization_near_zero(self):
        """neg_sphere has a maximum of 0 at the origin."""
        np.random.seed(0)
        ga = GeneticAlgorithm(population_size=50, generations=30)
        result = ga.optimize(neg_sphere, BOUNDS_2D, maximization=True)
        # Maximum of neg_sphere is 0; result should be close to 0 or negative
        assert result.optimal_value <= 0.0

    def test_result_within_bounds(self):
        np.random.seed(7)
        ga = GeneticAlgorithm(population_size=30, generations=10)
        result = ga.optimize(sphere, BOUNDS_2D, maximization=False)
        for i, (lo, hi) in enumerate(BOUNDS_2D):
            assert lo <= result.optimal_parameters[i] <= hi

    def test_iterations_match_generations(self):
        ga = GeneticAlgorithm(population_size=10, generations=8)
        result = ga.optimize(sphere, BOUNDS_2D, maximization=False)
        assert result.iterations == 8

    def test_3d_bounds(self):
        np.random.seed(1)
        ga = GeneticAlgorithm(population_size=20, generations=10)
        result = ga.optimize(sphere, BOUNDS_3D, maximization=False)
        assert len(result.optimal_parameters) == 3


# ---------------------------------------------------------------------------
# ParticleSwarmOptimizer
# ---------------------------------------------------------------------------

class TestParticleSwarmOptimizer:
    """Tests for ParticleSwarmOptimizer."""

    def test_default_parameters(self):
        pso = ParticleSwarmOptimizer()
        assert pso.num_particles == 30
        assert pso.max_iterations == 100
        assert pso.inertia_weight > 0

    def test_custom_parameters(self):
        pso = ParticleSwarmOptimizer(num_particles=10, max_iterations=20)
        assert pso.num_particles == 10
        assert pso.max_iterations == 20

    def test_returns_optimization_result(self):
        pso = ParticleSwarmOptimizer(num_particles=10, max_iterations=5)
        result = pso.optimize(sphere, BOUNDS_2D, maximization=False)
        assert isinstance(result, OptimizationResult)

    def test_minimization_improves(self):
        np.random.seed(42)
        pso = ParticleSwarmOptimizer(num_particles=20, max_iterations=50)
        result = pso.optimize(sphere, BOUNDS_2D, maximization=False)
        assert result.optimal_value < 10.0

    def test_maximization_returns_positive(self):
        """neg_sphere max is 0; PSO should find a value <= 0."""
        np.random.seed(0)
        pso = ParticleSwarmOptimizer(num_particles=20, max_iterations=30)
        result = pso.optimize(neg_sphere, BOUNDS_2D, maximization=True)
        assert result.optimal_value <= 0.0

    def test_result_within_bounds(self):
        np.random.seed(3)
        pso = ParticleSwarmOptimizer(num_particles=10, max_iterations=10)
        result = pso.optimize(sphere, BOUNDS_2D, maximization=False)
        for i, (lo, hi) in enumerate(BOUNDS_2D):
            assert lo <= result.optimal_parameters[i] <= hi

    def test_iterations_match_max_iterations(self):
        pso = ParticleSwarmOptimizer(num_particles=5, max_iterations=7)
        result = pso.optimize(sphere, BOUNDS_2D, maximization=False)
        assert result.iterations == 7

    def test_alias_particle_swarm_optimization(self):
        assert ParticleSwarmOptimization is ParticleSwarmOptimizer


# ---------------------------------------------------------------------------
# SimulatedAnnealing
# ---------------------------------------------------------------------------

class TestSimulatedAnnealing:
    """Tests for SimulatedAnnealing."""

    def test_default_parameters(self):
        sa = SimulatedAnnealing()
        assert sa.initial_temperature > 0
        assert 0 < sa.cooling_rate < 1
        assert sa.max_iterations > 0

    def test_custom_parameters(self):
        sa = SimulatedAnnealing(initial_temperature=50.0, cooling_rate=0.9,
                                max_iterations=200)
        assert sa.initial_temperature == 50.0
        assert sa.cooling_rate == 0.9
        assert sa.max_iterations == 200

    def test_returns_optimization_result(self):
        sa = SimulatedAnnealing(initial_temperature=10.0, max_iterations=10)
        result = sa.optimize(sphere, BOUNDS_2D, maximization=False)
        assert isinstance(result, OptimizationResult)

    def test_minimization(self):
        np.random.seed(42)
        sa = SimulatedAnnealing(initial_temperature=100.0, cooling_rate=0.95,
                                max_iterations=500)
        result = sa.optimize(sphere, BOUNDS_2D, maximization=False)
        assert result.optimal_value < 15.0

    def test_maximization(self):
        np.random.seed(5)
        sa = SimulatedAnnealing(initial_temperature=50.0, cooling_rate=0.9,
                                max_iterations=200)
        result = sa.optimize(neg_sphere, BOUNDS_2D, maximization=True)
        assert result.optimal_value <= 0.0

    def test_result_within_bounds(self):
        np.random.seed(9)
        sa = SimulatedAnnealing(max_iterations=50)
        result = sa.optimize(sphere, BOUNDS_2D, maximization=False)
        for i, (lo, hi) in enumerate(BOUNDS_2D):
            assert lo <= result.optimal_parameters[i] <= hi

    def test_iterations_match(self):
        sa = SimulatedAnnealing(max_iterations=15)
        result = sa.optimize(sphere, BOUNDS_2D, maximization=False)
        assert result.iterations == 15


# ---------------------------------------------------------------------------
# ClassicalOptimizer (unified interface)
# ---------------------------------------------------------------------------

class TestClassicalOptimizer:
    """Tests for ClassicalOptimizer unified interface."""

    @pytest.mark.parametrize("method", [
        OptimizationMethod.GENETIC,
        OptimizationMethod.PSO,
        OptimizationMethod.SIMULATED_ANNEALING,
    ])
    def test_optimize_returns_result(self, method):
        optimizer = ClassicalOptimizer(method=method)
        # Use small settings via the underlying optimizer to keep test fast
        optimizer.optimizer.generations = 5 if hasattr(optimizer.optimizer, 'generations') else None
        if hasattr(optimizer.optimizer, 'max_iterations'):
            optimizer.optimizer.max_iterations = 10
        result = optimizer.optimize(sphere, BOUNDS_2D, maximization=False)
        assert isinstance(result, OptimizationResult)

    def test_default_method_is_pso(self):
        optimizer = ClassicalOptimizer()
        assert optimizer.method == OptimizationMethod.PSO
        assert isinstance(optimizer.optimizer, ParticleSwarmOptimizer)

    def test_genetic_method_uses_genetic(self):
        optimizer = ClassicalOptimizer(method=OptimizationMethod.GENETIC)
        assert isinstance(optimizer.optimizer, GeneticAlgorithm)

    def test_sa_method_uses_sa(self):
        optimizer = ClassicalOptimizer(method=OptimizationMethod.SIMULATED_ANNEALING)
        assert isinstance(optimizer.optimizer, SimulatedAnnealing)

    def test_unknown_method_falls_back_to_pso(self):
        """Methods not explicitly handled should fall back to PSO."""
        optimizer = ClassicalOptimizer(method=OptimizationMethod.GRADIENT_DESCENT)
        assert isinstance(optimizer.optimizer, ParticleSwarmOptimizer)


# ---------------------------------------------------------------------------
# GradientDescent
# ---------------------------------------------------------------------------

class TestGradientDescent:
    """Tests for GradientDescent."""

    def test_default_parameters(self):
        gd = GradientDescent()
        assert gd.learning_rate > 0
        assert gd.max_iterations > 0

    def test_custom_parameters(self):
        gd = GradientDescent(learning_rate=0.05, max_iterations=50)
        assert gd.learning_rate == 0.05
        assert gd.max_iterations == 50

    def test_returns_dict(self):
        gd = GradientDescent(max_iterations=5)
        result = gd.optimize(sphere, initial_point=np.array([1.0, 1.0]))
        assert isinstance(result, dict)
        assert 'best_value' in result
        assert 'best_params' in result
        assert 'iterations' in result

    def test_iterations_match(self):
        gd = GradientDescent(max_iterations=12)
        result = gd.optimize(sphere, initial_point=np.array([1.0, 1.0]))
        assert result['iterations'] == 12

    def test_minimizes_sphere(self):
        gd = GradientDescent(learning_rate=0.01, max_iterations=200)
        result = gd.optimize(sphere, initial_point=np.array([2.0, 2.0]))
        assert result['best_value'] < sphere(np.array([2.0, 2.0]))

    def test_default_initial_point(self):
        """Should work without providing an initial point."""
        gd = GradientDescent(max_iterations=5)
        result = gd.optimize(sphere)
        assert 'best_value' in result

    def test_best_params_shape(self):
        gd = GradientDescent(max_iterations=5)
        initial = np.array([1.0, -1.0, 0.5])
        result = gd.optimize(sphere, initial_point=initial)
        assert len(result['best_params']) == 3


# ---------------------------------------------------------------------------
# DifferentialEvolution
# ---------------------------------------------------------------------------

class TestDifferentialEvolution:
    """Tests for DifferentialEvolution."""

    def test_default_parameters(self):
        de = DifferentialEvolution()
        assert de.population_size > 0
        assert de.generations > 0
        assert 0 < de.f <= 1
        assert 0 < de.cr <= 1

    def test_custom_parameters(self):
        de = DifferentialEvolution(population_size=10, generations=5,
                                   f=0.5, cr=0.8)
        assert de.population_size == 10
        assert de.generations == 5
        assert de.f == 0.5
        assert de.cr == 0.8

    def test_returns_dict(self):
        de = DifferentialEvolution(population_size=10, generations=3)
        result = de.optimize(sphere, bounds=BOUNDS_2D)
        assert isinstance(result, dict)
        assert 'best_value' in result
        assert 'best_params' in result
        assert 'iterations' in result

    def test_iterations_match_generations(self):
        de = DifferentialEvolution(population_size=5, generations=4)
        result = de.optimize(sphere, bounds=BOUNDS_2D)
        assert result['iterations'] == 4

    def test_minimizes_sphere(self):
        np.random.seed(42)
        de = DifferentialEvolution(population_size=30, generations=50)
        result = de.optimize(sphere, bounds=BOUNDS_2D)
        assert result['best_value'] < 5.0

    def test_default_bounds(self):
        """Should use default bounds when none provided."""
        de = DifferentialEvolution(population_size=5, generations=3)
        result = de.optimize(sphere)
        assert 'best_value' in result

    def test_result_within_bounds(self):
        np.random.seed(0)
        de = DifferentialEvolution(population_size=10, generations=10)
        result = de.optimize(sphere, bounds=BOUNDS_2D)
        for i, (lo, hi) in enumerate(BOUNDS_2D):
            assert lo <= result['best_params'][i] <= hi

    def test_3d_optimization(self):
        np.random.seed(1)
        de = DifferentialEvolution(population_size=15, generations=10)
        result = de.optimize(sphere, bounds=BOUNDS_3D)
        assert len(result['best_params']) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
