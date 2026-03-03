#!/usr/bin/env python3
"""
Advanced Multi-Strategy Portfolio Optimizer with Real Constraints
高级多策略投资组合优化器 - 带有现实约束的权重分配
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
from scipy.optimize import minimize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedPortfolioOptimizer:
    """Advanced portfolio optimization with realistic constraints"""
    
    def __init__(self, backtest_report_path: str):
        """Initialize optimizer from backtest report"""
        self.report_path = Path(backtest_report_path)
        self.strategies: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}
        self.optimizations: List[Dict[str, Any]] = []
        self._load_report()
    
    def _load_report(self):
        """Load backtest report"""
        if not self.report_path.exists():
            logger.error(f"Report not found: {self.report_path}")
            return
        
        with open(self.report_path, 'r') as f:
            data = json.load(f)
            self.strategies = data.get("individual_results", {})
            logger.info(f"Loaded {len(self.strategies)} strategies from report")
    
    def _calculate_metrics_matrix(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """Calculate metrics matrix for optimization"""
        strategy_names = list(self.strategies.keys())
        n_strats = len(strategy_names)
        
        returns = np.zeros(n_strats)
        sharpe = np.zeros(n_strats)
        drawdowns = np.zeros(n_strats)
        
        for i, name in enumerate(strategy_names):
            strat_data = self.strategies[name]
            returns[i] = strat_data.get("total_return_pct", 0.0) / 100.0  # Convert to decimal
            sharpe[i] = strat_data.get("sharpe_ratio", 0.0)
            drawdowns[i] = strat_data.get("max_drawdown_pct", 100.0) / 100.0
        
        return returns, sharpe, drawdowns, strategy_names
    
    def optimize_with_constraints(
        self,
        min_diversification: int = 2,
        max_concentration: float = 0.6,
        min_weight: float = 0.05,
        risk_limit: float = 0.15
    ) -> Dict[str, Any]:
        """
        Optimize with realistic constraints:
        - Minimum number of strategies in portfolio
        - Maximum concentration (largest weight)
        - Minimum weight per strategy included
        - Risk tolerance
        """
        logger.info("Starting constrained portfolio optimization...")
        
        returns, sharpe, drawdowns, strategy_names = self._calculate_metrics_matrix()
        n_strats = len(strategy_names)
        
        # Objective function: maximize risk-adjusted returns
        def objective(weights):
            # Ensure weights sum to 1
            weights = np.abs(weights)
            weights = weights / (weights.sum() + 1e-10)
            
            # Portfolio metrics
            port_return = np.dot(weights, returns)
            port_sharpe = np.dot(weights, sharpe)
            port_drawdown = np.dot(weights, drawdowns)
            
            # Risk-adjusted score (maximize)
            # Objective = Sharpe ratio + return premium - drawdown penalty
            score = port_sharpe + (port_return * 2.0) - (port_drawdown * 1.5)
            
            return -score  # Minimize negative score
        
        # Constraints
        constraints = [
            # Weights sum to 1
            {'type': 'eq', 'fun': lambda w: np.sum(np.abs(w)) - 1.0},
            
            # Maximum concentration constraint
            {'type': 'ineq', 'fun': lambda w: max_concentration - np.max(np.abs(w))},
            
            # Risk constraint
            {'type': 'ineq', 'fun': lambda w: risk_limit - np.dot(np.abs(w), drawdowns)}
        ]
        
        # Bounds: each weight between 0 and max_concentration
        bounds = [(0, max_concentration) for _ in range(n_strats)]
        
        # Initial guess: equal weights
        x0 = np.ones(n_strats) / n_strats
        
        # Optimize
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        # Normalize weights
        optimal_weights = np.abs(result.x)
        optimal_weights = optimal_weights / (optimal_weights.sum() + 1e-10)
        
        # Filter out very small weights
        optimal_weights[optimal_weights < min_weight] = 0
        optimal_weights = optimal_weights / (optimal_weights.sum() + 1e-10)
        
        # Calculate portfolio metrics
        port_return = np.dot(optimal_weights, returns)
        port_sharpe = np.dot(optimal_weights, sharpe)
        port_drawdown = np.dot(optimal_weights, drawdowns)
        port_score = port_sharpe + (port_return * 2.0) - (port_drawdown * 1.5)
        
        # Create result dictionary
        optimization_result = {
            "optimization_type": "Constrained Portfolio Optimization",
            "constraints": {
                "min_diversification": min_diversification,
                "max_concentration": max_concentration,
                "min_weight": min_weight,
                "risk_limit": risk_limit
            },
            "weights": {
                strategy_names[i]: float(optimal_weights[i])
                for i in range(n_strats)
            },
            "portfolio_metrics": {
                "total_return": float(port_return * 100),
                "sharpe_ratio": float(port_sharpe),
                "max_drawdown": float(port_drawdown * 100),
                "risk_adjusted_score": float(port_score)
            },
            "active_strategies": len([w for w in optimal_weights if w > 0.01]),
            "optimizer_success": result.success,
            "optimizer_message": result.message
        }
        
        logger.info(f"Optimization success: {result.success}")
        logger.info(f"Active strategies: {optimization_result['active_strategies']}")
        logger.info(f"Portfolio Return: {port_return*100:.2f}%")
        logger.info(f"Portfolio Sharpe: {port_sharpe:.2f}")
        logger.info(f"Portfolio Max DD: {port_drawdown*100:.2f}%")
        
        self.optimizations.append(optimization_result)
        return optimization_result
    
    def generate_comparison_scenarios(self) -> Dict[str, Any]:
        """Generate multiple optimization scenarios"""
        logger.info("Generating multiple optimization scenarios...")
        
        scenarios = {
            "aggressive": self.optimize_with_constraints(
                min_diversification=1,
                max_concentration=1.0,
                min_weight=0.01,
                risk_limit=0.50
            ),
            "balanced": self.optimize_with_constraints(
                min_diversification=2,
                max_concentration=0.6,
                min_weight=0.05,
                risk_limit=0.25
            ),
            "conservative": self.optimize_with_constraints(
                min_diversification=3,
                max_concentration=0.4,
                min_weight=0.10,
                risk_limit=0.15
            )
        }
        
        return scenarios
    
    def create_detailed_report(self, output_path: str) -> Dict[str, Any]:
        """Create detailed optimization report"""
        logger.info("Creating detailed optimization report...")
        
        returns, sharpe, drawdowns, strategy_names = self._calculate_metrics_matrix()
        
        # Individual strategy rankings
        individual_rankings = []
        for i, name in enumerate(strategy_names):
            strat_data = self.strategies[name]
            score = sharpe[i] + (returns[i] * 2.0) - (drawdowns[i] * 1.5)
            individual_rankings.append({
                "rank": i + 1,
                "strategy": name,
                "return": float(returns[i] * 100),
                "sharpe": float(sharpe[i]),
                "max_drawdown": float(drawdowns[i] * 100),
                "score": float(score)
            })
        
        individual_rankings.sort(key=lambda x: x['score'], reverse=True)
        for i, r in enumerate(individual_rankings):
            r['rank'] = i + 1
        
        # Generate scenarios
        scenarios = self.generate_comparison_scenarios()
        
        # Create final report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "report_type": "Advanced Multi-Strategy Portfolio Optimization",
            "num_strategies": len(strategy_names),
            "individual_strategy_rankings": individual_rankings,
            "optimization_scenarios": scenarios,
            "best_scenario": max(
                scenarios.items(),
                key=lambda x: x[1]["portfolio_metrics"]["risk_adjusted_score"]
            )[0],
            "recommendation": self._generate_recommendation(scenarios)
        }
        
        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {output_path}")
        return report
    
    def _generate_recommendation(self, scenarios: Dict[str, Any]) -> str:
        """Generate investment recommendation"""
        best_scenario = max(
            scenarios.values(),
            key=lambda x: x["portfolio_metrics"]["risk_adjusted_score"]
        )
        
        best_name = None
        for name, scenario in scenarios.items():
            if scenario == best_scenario:
                best_name = name
                break
        
        return (
            f"Recommended portfolio allocation strategy: {best_name.upper()} "
            f"with {best_scenario['active_strategies']} active strategies, "
            f"expected return: {best_scenario['portfolio_metrics']['total_return']:.2f}%, "
            f"Sharpe ratio: {best_scenario['portfolio_metrics']['sharpe_ratio']:.2f}"
        )
    
    def create_visualization_data(self, output_path: str):
        """Create visualization data for dashboard"""
        logger.info("Creating visualization data...")
        
        returns, sharpe, drawdowns, strategy_names = self._calculate_metrics_matrix()
        
        # Prepare data for visualization
        viz_data = {
            "strategies": [
                {
                    "name": name,
                    "return": float(returns[i] * 100),
                    "sharpe": float(sharpe[i]),
                    "drawdown": float(drawdowns[i] * 100),
                    "pnl": float(self.strategies[name].get("total_pnl", 0.0))
                }
                for i, name in enumerate(strategy_names)
            ],
            "scenarios": []
        }
        
        # Add scenario data
        for opt in self.optimizations:
            scenario_data = {
                "type": opt["optimization_type"],
                "weights": opt["weights"],
                "portfolio": opt["portfolio_metrics"],
                "diversification": opt["active_strategies"]
            }
            viz_data["scenarios"].append(scenario_data)
        
        # Save visualization data
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(viz_data, f, indent=2)
        
        logger.info(f"Visualization data saved to {output_path}")
        return viz_data


def main():
    """Main execution"""
    report_path = "/workspaces/cosmic-ai.uk/reports/backtesting/six_strategy_optimization_report.json"
    
    optimizer = AdvancedPortfolioOptimizer(report_path)
    
    # Create detailed report
    detailed_report = optimizer.create_detailed_report(
        "/workspaces/cosmic-ai.uk/reports/backtesting/advanced_portfolio_optimization_report.json"
    )
    
    # Create visualization data
    optimizer.create_visualization_data(
        "/workspaces/cosmic-ai.uk/reports/backtesting/portfolio_visualization_data.json"
    )
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("OPTIMIZATION SUMMARY")
    logger.info("=" * 80)
    
    logger.info("\nIndividual Strategy Rankings (Top 5):")
    for ranking in detailed_report["individual_strategy_rankings"][:5]:
        logger.info(
            f"  {ranking['rank']}. {ranking['strategy']}: "
            f"Return={ranking['return']:.2f}%, Sharpe={ranking['sharpe']:.2f}, "
            f"DD={ranking['max_drawdown']:.2f}%"
        )
    
    logger.info("\nPortfolio Scenarios:")
    for scenario_name, scenario_data in detailed_report["optimization_scenarios"].items():
        logger.info(f"\n  {scenario_name.upper()}:")
        logger.info(f"    Return: {scenario_data['portfolio_metrics']['total_return']:.2f}%")
        logger.info(f"    Sharpe: {scenario_data['portfolio_metrics']['sharpe_ratio']:.2f}")
        logger.info(f"    Max DD: {scenario_data['portfolio_metrics']['max_drawdown']:.2f}%")
        logger.info(f"    Active Strategies: {scenario_data['active_strategies']}")
    
    logger.info(f"\n🎯 {detailed_report['recommendation']}")
    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    main()
