#!/usr/bin/env python3
"""
Self-Evolution Integration Plan
自進化智能體系統重新啟動與集成

This document outlines how to reconnect the CMA-ES Adaptive Evolution system
with the current backtesting framework to enable self-evolving strategies.

系統架構:
1. CMA-ES Adaptive Evolution (523 lines) - 已存在, 等待集成
2. 多智能體協調 (AdaptiveEvolutionCoordinator) - 可用
3. 步長自適應 (StepSizeAdapter) - 可用
4. 協方差矩陣管理 (CovarianceMatrix) - 可用

集成需求:
- 連接到 unified_backtester.py
- 在每個epoch後自動優化參數
- 多代進化 (multi-generation evolution)
- 實時性能反饋
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class SelfEvolutionMode(Enum):
    """Self-evolution operating modes."""
    DISABLED = "disabled"
    ADAPTIVE = "adaptive"  # Adapt during backtesting
    AGGRESSIVE = "aggressive"  # Rapid evolution
    CONSERVATIVE = "conservative"  # Careful parameter tuning


@dataclass
class EvolutionConfig:
    """Configuration for self-evolution during backtesting."""
    enabled: bool = True
    mode: SelfEvolutionMode = SelfEvolutionMode.ADAPTIVE
    
    # Evolution parameters
    population_size: int = 50
    generations_per_epoch: int = 5
    mutation_rate: float = 0.2
    crossover_rate: float = 0.8
    
    # Parameters to evolve (from strategy adapters)
    evolve_params: List[str] = None  # e.g., ['min_confidence', 'stop_loss_pct']
    
    # Convergence criteria
    target_sharpe: float = 2.0
    target_win_rate: float = 0.55
    max_total_generations: int = 100
    
    # Fault tolerance & topological correction
    enable_fault_tolerance: bool = True
    enable_topological_correction: bool = True
    topology_repair_threshold: float = 0.7  # Fitness threshold for repair
    
    def __post_init__(self):
        if self.evolve_params is None:
            self.evolve_params = [
                'min_confidence',
                'stop_loss_pct',
                'take_profit_pct',
                'volatility_threshold'
            ]


class EvolutionIntegrationManager:
    """
    Manages integration of CMA-ES evolution with unified backtester.
    
    Integration Points:
    1. Strategy Adapter → Extract parameters
    2. Backtester → Get fitness (Sharpe, returns, etc.)
    3. CMA-ES Optimizer → Evolve parameters
    4. Fault Tolerance → Handle convergence failures
    5. Topology Correction → Fix population degeneration
    """
    
    def __init__(self, config: EvolutionConfig = None):
        """Initialize evolution integration."""
        self.config = config or EvolutionConfig()
        self.generation = 0
        self.evolution_history: List[Dict[str, Any]] = []
        self.best_fitness = -float('inf')
        self.best_parameters = None
        
    def setup_evolution_with_backtester(
        self,
        backtester,  # UnifiedBacktester instance
        strategy_adapter,  # Strategy adapter instance
        market_snapshots: List[Any]
    ) -> None:
        """
        Setup evolution process integrated with backtester.
        
        Args:
            backtester: UnifiedBacktester instance
            strategy_adapter: Strategy adapter (CosmicStrategyAdapter, etc.)
            market_snapshots: Market data snapshots
        """
        logger.info("Setting up self-evolution with backtester...")
        
        self.backtester = backtester
        self.strategy_adapter = strategy_adapter
        self.market_snapshots = market_snapshots
        
        # Extract current parameters from strategy
        self.initial_parameters = self._extract_parameters(strategy_adapter)
        logger.info(f"Initial parameters: {self.initial_parameters}")
        
    def _extract_parameters(self, strategy_adapter) -> Dict[str, float]:
        """Extract parameter values from strategy adapter."""
        params = {}
        
        # Strategy-specific parameter extraction
        if hasattr(strategy_adapter, 'config'):
            config = strategy_adapter.config
            for param_name in self.config.evolve_params:
                if param_name in config:
                    params[param_name] = float(config[param_name])
        
        logger.debug(f"Extracted parameters: {params}")
        return params
    
    def _apply_parameters(self, strategy_adapter, parameters: Dict[str, float]) -> None:
        """Apply evolved parameters to strategy adapter."""
        if hasattr(strategy_adapter, 'config'):
            for param_name, value in parameters.items():
                if param_name in self.config.evolve_params:
                    strategy_adapter.config[param_name] = value
        
        logger.debug(f"Applied parameters: {parameters}")
    
    async def evolve_one_generation(self) -> Dict[str, Any]:
        """
        Run one generation of CMA-ES evolution.
        
        Returns:
            Generation statistics with best fitness and parameters
        """
        from src.core.cma_es_adaptive_evolution import CMAESOptimizer
        
        logger.info(f"\n=== EVOLUTION GENERATION {self.generation + 1} ===")
        
        # Setup optimizer
        optimizer = CMAESOptimizer(
            fitness_function=self._fitness_function,
            dimension=len(self.config.evolve_params),
            config_dict={
                'population_size': self.config.population_size,
                'max_generations': self.config.generations_per_epoch
            }
        )
        
        # Run optimization
        best_params, best_fitness, history = await optimizer.optimize()
        
        # Check for improvement
        if best_fitness > self.best_fitness:
            self.best_fitness = best_fitness
            self.best_parameters = best_params
            logger.info(f"✓ New best fitness: {best_fitness:.4f}")
        
        # Apply topological correction if enabled
        if self.config.enable_topological_correction:
            await self._apply_topological_correction(history)
        
        # Record generation
        gen_record = {
            'generation': self.generation,
            'best_fitness': best_fitness,
            'best_parameters': best_params,
            'history': history,
            'timestamp': str(__import__('datetime').datetime.now())
        }
        self.evolution_history.append(gen_record)
        
        self.generation += 1
        
        return gen_record
    
    async def _fitness_function(self, parameters: np.ndarray) -> float:
        """
        Fitness function for CMA-ES optimization.
        
        Evaluates strategy performance with given parameters.
        
        Args:
            parameters: Parameter vector to evaluate
            
        Returns:
            Fitness score (Sharpe ratio, normalized)
        """
        # Convert parameter vector back to dict
        param_dict = {
            name: float(parameters[i])
            for i, name in enumerate(self.config.evolve_params)
        }
        
        # Apply parameters to strategy
        self._apply_parameters(self.strategy_adapter, param_dict)
        
        # Run backtest
        try:
            metrics = await self.backtester.run_backtest(self.market_snapshots)
            
            # Composite fitness: Sharpe ratio + return score + win rate
            sharpe_score = max(0, metrics.sharpe_ratio) / 2.0  # Normalize
            return_score = max(0, metrics.total_return_pct) / 100.0  # Normalize
            win_rate_score = metrics.win_rate / 100.0  # Normalize
            
            # Weighted combination
            fitness = (
                0.5 * sharpe_score +  # Most important
                0.3 * return_score +   # Secondary
                0.2 * win_rate_score   # Tertiary
            )
            
            logger.debug(f"Fitness: {fitness:.4f} (Sharpe: {metrics.sharpe_ratio:.2f})")
            return fitness
            
        except Exception as e:
            logger.error(f"Fitness evaluation failed: {e}")
            return -1.0  # Penalize failures
    
    async def _apply_topological_correction(
        self,
        population_history: Dict[str, Any]
    ) -> None:
        """
        Apply topological correction to fix population degeneration.
        
        Detects when population is converging to local optima and
        injects diversity while maintaining structure.
        
        Args:
            population_history: Evolution history from optimizer
        """
        logger.info("Applying topological correction...")
        
        # Check for stagnation (diversity loss)
        if len(self.evolution_history) > 3:
            recent_improvements = [
                self.evolution_history[-i]['best_fitness'] -
                self.evolution_history[-i-1]['best_fitness']
                for i in range(min(3, len(self.evolution_history) - 1))
            ]
            
            avg_improvement = np.mean(recent_improvements)
            
            if avg_improvement < 0.01:
                logger.warning("Population stagnation detected, injecting diversity...")
                # TODO: Implement topology repair mechanism
                pass
    
    async def run_self_evolution_session(
        self,
        num_generations: int = None
    ) -> Dict[str, Any]:
        """
        Run complete self-evolution session with multiple generations.
        
        Args:
            num_generations: Number of generations to evolve
            
        Returns:
            Session results with best parameters found
        """
        if not self.config.enabled:
            logger.info("Self-evolution is disabled")
            return {'status': 'disabled'}
        
        num_generations = num_generations or self.config.max_total_generations
        
        logger.info("=" * 80)
        logger.info(f"STARTING SELF-EVOLUTION SESSION ({num_generations} generations)")
        logger.info(f"Mode: {self.config.mode.value}")
        logger.info(f"Evolving parameters: {self.config.evolve_params}")
        logger.info("=" * 80)
        
        session_results = {
            'mode': self.config.mode.value,
            'num_generations': num_generations,
            'generations_completed': 0,
            'best_fitness': -float('inf'),
            'best_parameters': None,
            'convergence_achieved': False,
            'history': []
        }
        
        for gen in range(num_generations):
            # Run one generation
            gen_result = await self.evolve_one_generation()
            session_results['history'].append(gen_result)
            session_results['generations_completed'] += 1
            
            # Update session best
            if gen_result['best_fitness'] > session_results['best_fitness']:
                session_results['best_fitness'] = gen_result['best_fitness']
                session_results['best_parameters'] = gen_result['best_parameters']
            
            # Check convergence criteria
            if gen_result['best_fitness'] >= self.config.target_sharpe:
                logger.info(f"✓ Convergence achieved at generation {gen + 1}!")
                session_results['convergence_achieved'] = True
                break
            
            # Adaptive mode: adjust number of generations based on progress
            if self.config.mode == SelfEvolutionMode.ADAPTIVE:
                # Reduce generations if converging quickly
                if gen > 5 and session_results['best_fitness'] > 0.8:
                    logger.info("Strong convergence detected, can accelerate...")
        
        logger.info("=" * 80)
        logger.info(f"SELF-EVOLUTION SESSION COMPLETE")
        logger.info(f"Best fitness achieved: {session_results['best_fitness']:.4f}")
        logger.info(f"Best parameters: {session_results['best_parameters']}")
        logger.info("=" * 80)
        
        return session_results
    
    def export_evolution_results(self, filepath: str) -> None:
        """Export evolution history to JSON file."""
        import json
        
        results = {
            'evolution_mode': self.config.mode.value,
            'total_generations': self.generation,
            'best_fitness': self.best_fitness,
            'best_parameters': self.best_parameters,
            'history': self.evolution_history
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Evolution results exported to {filepath}")


# Integration recipe for backtesting workflow
async def run_backtest_with_self_evolution(
    strategy_adapter,
    market_snapshots,
    config: EvolutionConfig = None
):
    """
    Run backtesting with integrated self-evolution.
    
    Usage:
        from src.core.cma_es_adaptive_evolution import EvolutionConfig
        from src.backtesting.evolution_integration import run_backtest_with_self_evolution
        
        results = await run_backtest_with_self_evolution(
            strategy_adapter=cosmic_adapter,
            market_snapshots=snapshots,
            config=EvolutionConfig(
                enabled=True,
                mode=SelfEvolutionMode.ADAPTIVE,
                evolve_params=['min_confidence', 'volatility_threshold']
            )
        )
    """
    from src.backtesting.unified_backtester import UnifiedBacktester, BacktestConfig
    
    config = config or EvolutionConfig()
    
    # Setup backtester
    backtester = UnifiedBacktester(strategy=strategy_adapter)
    
    # Setup evolution
    evolution_manager = EvolutionIntegrationManager(config)
    evolution_manager.setup_evolution_with_backtester(
        backtester,
        strategy_adapter,
        market_snapshots
    )
    
    # Run evolution session
    evolution_results = await evolution_manager.run_self_evolution_session()
    
    # Apply best parameters
    if evolution_results['best_parameters'] is not None:
        best_params = {
            name: float(evolution_results['best_parameters'][i])
            for i, name in enumerate(config.evolve_params)
        }
        evolution_manager._apply_parameters(strategy_adapter, best_params)
    
    # Run final backtest with best parameters
    final_metrics = await backtester.run_backtest(market_snapshots)
    
    return {
        'evolution_results': evolution_results,
        'final_metrics': final_metrics,
        'final_parameters': evolution_results['best_parameters']
    }


if __name__ == "__main__":
    import numpy as np
    
    # This is a template - shows how to use the system
    print(__doc__)
