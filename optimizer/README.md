# Optimizer Module README

## Overview

The Optimizer module provides classical optimization algorithms that serve as alternatives and complements to quantum algorithms. These algorithms are used for portfolio optimization, parameter tuning, and risk management in the Comic AI trading system.

優化模塊提供經典優化算法，作為量子算法的替代方案和補充。這些算法用於投資組合優化、參數調整和 Comic AI 交易系統中的風險管理。

## Module Purpose

This module provides:
- **Genetic Algorithm**: Population-based evolutionary optimization
- **Particle Swarm Optimization**: Swarm intelligence optimization
- **Simulated Annealing**: Probabilistic optimization technique
- **Gradient Descent**: First-order optimization
- **Differential Evolution**: Population-based stochastic optimization

## Key Classes and Functions

### Genetic Algorithm

Population-based evolutionary optimization mimicking natural selection.

```python
from optimizer import GeneticAlgorithm, OptimizationMethod

def objective(x):
    """Function to minimize/maximize."""
    return -sum(x**2)  # Maximize

ga = GeneticAlgorithm(
    population_size=100,
    generations=50,
    mutation_rate=0.1,
    crossover_rate=0.8
)

result = ga.optimize(objective, bounds=[(-5, 5)] * 10)
print(f"Optimal value: {result.optimal_value}")
print(f"Iterations: {result.iterations}")
```

### Particle Swarm Optimization

Simulates social behavior of bird flocking or fish schooling.

```python
from optimizer import ParticleSwarmOptimization

pso = ParticleSwarmOptimization(
    num_particles=30,
    dimensions=5,
    max_iterations=100,
    inertia=0.7,
    cognitive_coeff=1.5,
    social_coeff=1.5
)

result = pso.optimize(objective, bounds=[(-5, 5)] * 5)
print(f"Optimal parameters: {result.optimal_parameters}")
print(f"Converged: {result.converged}")
```

### Simulated Annealing

Probabilistic technique for approximating global optimum.

```python
from optimizer import SimulatedAnnealing

sa = SimulatedAnnealing(
    initial_temperature=100.0,
    cooling_rate=0.95,
    max_iterations=1000
)

result = sa.optimize(objective, initial_solution=np.random.rand(10))
print(f"Solution: {result.optimal_parameters}")
print(f"Energy: {result.optimal_value}")
```

### Gradient Descent

First-order iterative optimization algorithm.

```python
from optimizer import GradientDescentOptimizer

gd = GradientDescentOptimizer(
    learning_rate=0.01,
    max_iterations=1000,
    tolerance=1e-6
)

result = gd.optimize(objective, initial_params=np.random.rand(10))
print(f"Converged: {result.converged}")
print(f"Final loss: {result.optimal_value}")
```

### Differential Evolution

Population-based stochastic optimization.

```python
from optimizer import DifferentialEvolution

de = DifferentialEvolution(
    population_size=50,
    generations=100,
    mutation_factor=0.8,
    crossover_rate=0.7
)

result = de.optimize(objective, bounds=[(-5, 5)] * 10)
print(f"Best fitness: {result.optimal_value}")
```

## Usage Examples

### Example 1: Portfolio Weight Optimization

```python
import numpy as np
from optimizer import GeneticAlgorithm

def portfolio_risk(weights):
    """Calculate portfolio risk for given weights."""
    # Assuming we have correlation matrix and volatilities
    covariance = np.array([[0.04, 0.01], [0.01, 0.09]])
    portfolio_var = weights @ covariance @ weights.T
    return portfolio_var  # Minimize risk

# Constraints: weights sum to 1
def normalize_weights(weights):
    return weights / weights.sum()

ga = GeneticAlgorithm(
    population_size=50,
    generations=100,
    mutation_rate=0.1
)

# Optimize with bounds [0, 1] for each weight
result = ga.optimize(
    objective=portfolio_risk,
    bounds=[(0, 1), (0, 1)],
    constraint_fn=normalize_weights
)

optimal_weights = normalize_weights(result.optimal_parameters)
print(f"Optimal weights: {optimal_weights}")
print(f"Minimum risk: {result.optimal_value}")
```

### Example 2: Hyperparameter Tuning

```python
from optimizer import ParticleSwarmOptimization
import numpy as np

def model_performance(params):
    """Evaluate model with given hyperparameters."""
    learning_rate = params[0]
    regularization = params[1]
    batch_size = int(params[2])
    
    # Train model and return negative accuracy (for minimization)
    accuracy = train_model(learning_rate, regularization, batch_size)
    return -accuracy

pso = ParticleSwarmOptimization(
    num_particles=20,
    dimensions=3,
    max_iterations=50
)

result = pso.optimize(
    objective=model_performance,
    bounds=[
        (0.0001, 0.1),    # learning_rate
        (0.0, 0.1),       # regularization
        (16, 256)         # batch_size
    ]
)

best_lr, best_reg, best_bs = result.optimal_parameters
print(f"Best learning rate: {best_lr}")
print(f"Best regularization: {best_reg}")
print(f"Best batch size: {int(best_bs)}")
```

### Example 3: Multi-Objective Optimization

```python
from optimizer import SimulatedAnnealing

def multi_objective(params):
    """Combine multiple objectives."""
    return_score = calculate_returns(params)
    risk_score = calculate_risk(params)
    
    # Weighted combination (higher is better)
    return 0.7 * return_score - 0.3 * risk_score

sa = SimulatedAnnealing(
    initial_temperature=50.0,
    cooling_rate=0.99,
    max_iterations=5000
)

result = sa.optimize(
    objective=multi_objective,
    initial_solution=np.random.rand(5)
)

print(f"Optimal parameters: {result.optimal_parameters}")
print(f"Combined score: {result.optimal_value}")
```

## Configuration

### Algorithm Parameters

#### Genetic Algorithm
- `population_size` (int): Population size (default: 100)
- `generations` (int): Number of generations (default: 50)
- `mutation_rate` (float): Mutation probability (default: 0.1)
- `crossover_rate` (float): Crossover probability (default: 0.8)
- `elite_size` (int): Number of elite individuals to keep (default: 2)

#### Particle Swarm Optimization
- `num_particles` (int): Number of particles (default: 30)
- `dimensions` (int): Problem dimensions
- `max_iterations` (int): Maximum iterations (default: 100)
- `inertia` (float): Inertia weight (default: 0.7)
- `cognitive_coeff` (float): Cognitive coefficient (default: 1.5)
- `social_coeff` (float): Social coefficient (default: 1.5)

#### Simulated Annealing
- `initial_temperature` (float): Starting temperature
- `cooling_rate` (float): Temperature reduction rate (default: 0.95)
- `max_iterations` (int): Maximum iterations
- `min_temperature` (float): Stopping temperature (default: 1e-6)

#### Gradient Descent
- `learning_rate` (float): Step size (default: 0.01)
- `max_iterations` (int): Maximum iterations (default: 1000)
- `tolerance` (float): Convergence tolerance (default: 1e-6)
- `momentum` (float): Momentum factor (default: 0.0)

#### Differential Evolution
- `population_size` (int): Population size (default: 50)
- `generations` (int): Number of generations (default: 100)
- `mutation_factor` (float): Mutation factor (default: 0.8)
- `crossover_rate` (float): Crossover probability (default: 0.7)

## Result Structure

```python
@dataclass
class OptimizationResult:
    optimal_value: float           # Best objective value achieved
    optimal_parameters: np.ndarray # Best parameters found
    iterations: int                # Iterations performed
    converged: bool                # Whether algorithm converged
    method: str                    # Algorithm name
```

## Algorithm Comparison

| Algorithm | Speed | Accuracy | Robustness | Memory |
|-----------|-------|----------|-----------|--------|
| Genetic | Fast | Medium | High | High |
| PSO | Fast | High | High | Medium |
| Simulated Annealing | Slow | High | High | Low |
| Gradient Descent | Very Fast | High | Low | Low |
| Differential Evolution | Medium | Very High | High | High |

## Performance Tips

1. **Scaling**: Normalize input variables to [-1, 1]
2. **Population Size**: Use 10-50x problem dimension
3. **Iterations**: Adjust based on problem complexity
4. **Parallelization**: Use multiprocessing for large populations
5. **Constraints**: Implement penalty methods for constraints

## Objective Function Guidelines

```python
def objective_function(x):
    """
    Objective function template.
    
    Args:
        x: Parameter vector (numpy array)
        
    Returns:
        float: Objective value to minimize
    """
    # Minimize objective (for maximization, return -value)
    return np.sum(x**2)

# Good practices:
# 1. Use numpy for vectorization
# 2. Handle edge cases
# 3. Return scalar float value
# 4. Make computationally efficient
# 5. Handle NaN/Inf gracefully
```

## Advanced Usage

### Custom Constraint Handling

```python
from optimizer import GeneticAlgorithm

ga = GeneticAlgorithm()

def constraint_violation(x):
    """Penalty for constraint violations."""
    penalties = 0
    
    # Constraint: x[0] + x[1] <= 1
    if x[0] + x[1] > 1:
        penalties += (x[0] + x[1] - 1) ** 2
    
    # Constraint: x[0] >= 0
    if x[0] < 0:
        penalties += x[0] ** 2
    
    return penalties

def penalized_objective(x):
    return objective(x) + 1000 * constraint_violation(x)
```

### Hybrid Approach

```python
# Use GA for coarse search, then GD for fine-tuning
ga = GeneticAlgorithm(generations=50)
ga_result = ga.optimize(objective, bounds)

gd = GradientDescentOptimizer(learning_rate=0.01)
final_result = gd.optimize(
    objective,
    initial_params=ga_result.optimal_parameters
)
```

## Testing

Run optimizer tests:

```bash
pytest src/tests/test_optimizers.py -v
```

## Common Issues

### Convergence Problems
- Check objective function for bugs
- Adjust parameters (population size, iterations)
- Try different algorithm
- Normalize variables

### Slow Performance
- Reduce problem dimension
- Simplify objective function
- Use smaller population
- Consider parallelization

### Poor Results
- Try different random seed
- Increase iterations
- Adjust algorithm parameters
- Check bounds are correct

## Related Modules

- `src/plugins/multi_agent_trading.py`: Uses optimizers for portfolio allocation
- `data/__init__.py`: Data for optimization
- `src/api/server.py`: API integration
- `src/tests/test_optimizers.py`: Tests

## References

- Genetic Algorithms: Holland, J.H. (1992)
- Particle Swarm Optimization: Kennedy & Eberhart (1995)
- Simulated Annealing: Kirkpatrick et al. (1983)
- Differential Evolution: Storn & Price (1997)

## License

Part of Comic AI trading system
