#!/usr/bin/env python3
"""
OpenCode Skills System - Comprehensive Skill Framework
OpenCode 技能系統 - 完整技能框架

Modular, composable skills for agent capabilities.
用於代理能力的模塊化、可組合的技能
"""

import logging
from typing import Dict, List, Any, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class SkillCategory(Enum):
    """Skill categories"""
    OPTIMIZATION = "optimization"
    TRADING = "trading"
    ANALYSIS = "analysis"
    PREDICTION = "prediction"
    SYSTEM = "system"
    INTEGRATION = "integration"
    COSMOS = "cosmos"


class SkillLevel(Enum):
    """Skill proficiency levels"""
    NOVICE = 1
    BEGINNER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5
    MASTER = 6


@dataclass
class SkillMetadata:
    """Metadata for a skill"""
    skill_id: str
    name: str
    description: str
    category: SkillCategory
    version: str = "1.0.0"
    author: str = "Comic AI"
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    proficiency_level: SkillLevel = SkillLevel.INTERMEDIATE


class BaseSkill(ABC, Generic[T]):
    """
    Base class for all skills
    所有技能的基類
    """

    def __init__(self, metadata: SkillMetadata):
        """Initialize skill"""
        self.metadata = metadata
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_time = 0.0

    @abstractmethod
    def execute(self, *args, **kwargs) -> T:
        """Execute the skill - must be implemented by subclasses"""
        pass

    @abstractmethod
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate input parameters"""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get skill metadata"""
        return {
            'skill_id': self.metadata.skill_id,
            'name': self.metadata.name,
            'description': self.metadata.description,
            'category': self.metadata.category.value,
            'version': self.metadata.version,
            'proficiency_level': self.metadata.proficiency_level.name,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'error_count': self.error_count
        }


# ============================================================================
# OPTIMIZATION SKILLS
# ============================================================================

class QuantumOptimizationSkill(BaseSkill):
    """Quantum-enhanced optimization skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="quantum_optimization",
                name="Quantum Optimization",
                description="Hybrid quantum-enhanced optimization using superposition and entanglement",
                category=SkillCategory.OPTIMIZATION,
                proficiency_level=SkillLevel.EXPERT,
                parameters={
                    "population_size": 30,
                    "quantum_gates": 8,
                    "max_iterations": 50
                }
            )
        )

    def execute(self, objective_func: Callable, bounds: List, **kwargs) -> Dict[str, Any]:
        """Execute quantum optimization"""
        from optimizer.hybrid_quantum_algorithm import HybridQuantumEnhancedAlgorithm

        algo = HybridQuantumEnhancedAlgorithm(
            population_size=kwargs.get('population_size', 30),
            quantum_gates=kwargs.get('quantum_gates', 8),
            max_iterations=kwargs.get('max_iterations', 50)
        )

        return algo.optimize(objective_func, bounds)

    def validate_input(self, objective_func: Callable, bounds: List, **kwargs) -> bool:
        """Validate optimization inputs"""
        return callable(objective_func) and isinstance(bounds, list) and len(bounds) > 0


class ParticleSwarmSkill(BaseSkill):
    """Particle Swarm Optimization skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="particle_swarm",
                name="Particle Swarm Optimization",
                description="PSO-based optimization for continuous problems",
                category=SkillCategory.OPTIMIZATION,
                proficiency_level=SkillLevel.ADVANCED
            )
        )

    def execute(self, objective_func: Callable, bounds: List, **kwargs) -> Dict[str, Any]:
        """Execute PSO"""
        from optimizer.classical_algorithms import ParticleSwarmOptimizer

        pso = ParticleSwarmOptimizer(
            population_size=kwargs.get('population_size', 30),
            max_iterations=kwargs.get('max_iterations', 100)
        )

        return pso.optimize(objective_func, bounds)

    def validate_input(self, objective_func: Callable, bounds: List, **kwargs) -> bool:
        """Validate PSO inputs"""
        return callable(objective_func) and isinstance(bounds, list)


# ============================================================================
# TRADING SKILLS
# ============================================================================

class SignalGenerationSkill(BaseSkill):
    """Quantum signal generation skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="signal_generation",
                name="Signal Generation",
                description="Generate quantum-enhanced trading signals",
                category=SkillCategory.TRADING,
                proficiency_level=SkillLevel.EXPERT
            )
        )

    def execute(self, price_data, volume_data, volatility, **kwargs) -> Dict[str, Any]:
        """Generate trading signals"""
        from optimizer.hybrid_quantum_algorithm import QuantumEnhancedSignalGenerator

        generator = QuantumEnhancedSignalGenerator()
        return generator.generate_quantum_signal(price_data, volume_data, volatility)

    def validate_input(self, price_data, volume_data, volatility, **kwargs) -> bool:
        """Validate signal generation inputs"""
        import numpy as np
        return (isinstance(price_data, (list, np.ndarray)) and
                isinstance(volume_data, (list, np.ndarray)) and
                isinstance(volatility, (int, float)))


class RiskManagementSkill(BaseSkill):
    """Risk management skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="risk_management",
                name="Risk Management",
                description="Calculate and manage trading risks",
                category=SkillCategory.TRADING,
                proficiency_level=SkillLevel.ADVANCED
            )
        )

    def execute(self, portfolio: Dict, risk_params: Dict, **kwargs) -> Dict[str, Any]:
        """Execute risk management"""
        # Calculate Value at Risk (VaR)
        import numpy as np

        positions = portfolio.get('positions', [])
        confidence_level = risk_params.get('confidence_level', 0.95)

        returns = np.array([p.get('return', 0) for p in positions])

        var = np.percentile(returns, (1 - confidence_level) * 100)
        cvar = returns[returns <= var].mean()

        return {
            'value_at_risk': float(var),
            'conditional_var': float(cvar),
            'confidence_level': confidence_level,
            'portfolio_size': len(positions)
        }

    def validate_input(self, portfolio: Dict, risk_params: Dict, **kwargs) -> bool:
        """Validate risk management inputs"""
        return isinstance(portfolio, dict) and isinstance(risk_params, dict)


# ============================================================================
# ANALYSIS SKILLS
# ============================================================================

class MarketAnalysisSkill(BaseSkill):
    """Market analysis skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="market_analysis",
                name="Market Analysis",
                description="Comprehensive market analysis with quantum enhancement",
                category=SkillCategory.ANALYSIS,
                proficiency_level=SkillLevel.EXPERT
            )
        )

    def execute(self, market_data: Dict, **kwargs) -> Dict[str, Any]:
        """Perform market analysis"""
        from src.core.enhanced_quantum_market_analyzer import EnhancedQuantumMarketAnalyzer

        analyzer = EnhancedQuantumMarketAnalyzer()
        return analyzer.analyze_market_quantum(market_data)

    def validate_input(self, market_data: Dict, **kwargs) -> bool:
        """Validate market data"""
        return isinstance(market_data, dict) and len(market_data) > 0


class CorrelationAnalysisSkill(BaseSkill):
    """Correlation analysis skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="correlation_analysis",
                name="Correlation Analysis",
                description="Analyze correlations and entanglement",
                category=SkillCategory.ANALYSIS,
                proficiency_level=SkillLevel.ADVANCED
            )
        )

    def execute(self, time_series_data: Dict, **kwargs) -> Dict[str, Any]:
        """Analyze correlations"""
        import numpy as np

        series_list = list(time_series_data.values())

        if len(series_list) < 2:
            return {'error': 'Need at least 2 time series'}

        # Calculate correlation matrix
        data_array = np.array(series_list)
        correlation = np.corrcoef(data_array)

        return {
            'correlation_matrix': correlation.tolist(),
            'series_count': len(series_list),
            'avg_correlation': float(np.mean(correlation[np.triu_indices_from(correlation, k=1)]))
        }

    def validate_input(self, time_series_data: Dict, **kwargs) -> bool:
        """Validate time series data"""
        return isinstance(time_series_data, dict)


# ============================================================================
# SYSTEM SKILLS
# ============================================================================

class ConfigurationManagementSkill(BaseSkill):
    """Configuration management skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="config_management",
                name="Configuration Management",
                description="Load and manage system configuration",
                category=SkillCategory.SYSTEM,
                proficiency_level=SkillLevel.INTERMEDIATE
            )
        )

    def execute(self, config_path: str, **kwargs) -> Dict[str, Any]:
        """Load configuration"""
        from src.utils import ConfigManager

        manager = ConfigManager()
        return manager.load_config(config_path)

    def validate_input(self, config_path: str, **kwargs) -> bool:
        """Validate config path"""
        return isinstance(config_path, str) and len(config_path) > 0


class DataProcessingSkill(BaseSkill):
    """Data processing skill"""

    def __init__(self):
        super().__init__(
            SkillMetadata(
                skill_id="data_processing",
                name="Data Processing",
                description="Normalize and process data",
                category=SkillCategory.SYSTEM,
                proficiency_level=SkillLevel.INTERMEDIATE
            )
        )

    def execute(self, data: List, operation: str, **kwargs) -> List:
        """Process data"""
        import numpy as np

        data_array = np.array(data)

        if operation == 'normalize':
            return ((data_array - data_array.min()) / (data_array.max() - data_array.min())).tolist()
        elif operation == 'standardize':
            return ((data_array - data_array.mean()) / data_array.std()).tolist()
        elif operation == 'log':
            return np.log(data_array + 1).tolist()
        else:
            return data

    def validate_input(self, data: List, operation: str, **kwargs) -> bool:
        """Validate data processing inputs"""
        return isinstance(data, (list, tuple)) and isinstance(operation, str)


# ============================================================================
# SKILL REGISTRY
# ============================================================================

class SkillRegistry:
    """Registry for all available skills"""

    def __init__(self):
        """Initialize skill registry"""
        self.skills: Dict[str, BaseSkill] = {}
        self._register_default_skills()

    def _register_default_skills(self) -> None:
        """Register all default skills"""
        # Optimization
        self.register_skill(QuantumOptimizationSkill())
        self.register_skill(ParticleSwarmSkill())

        # Trading
        self.register_skill(SignalGenerationSkill())
        self.register_skill(RiskManagementSkill())

        # Analysis
        self.register_skill(MarketAnalysisSkill())
        self.register_skill(CorrelationAnalysisSkill())

        # System
        self.register_skill(ConfigurationManagementSkill())
        self.register_skill(DataProcessingSkill())

    def register_skill(self, skill: BaseSkill) -> None:
        """Register a skill"""
        skill_id = skill.metadata.skill_id
        self.skills[skill_id] = skill
        logger.info(f"✅ Registered skill: {skill_id} ({skill.metadata.name})")

    def get_skill(self, skill_id: str) -> Optional[BaseSkill]:
        """Get skill by ID"""
        return self.skills.get(skill_id)

    def list_skills(self, category: Optional[SkillCategory] = None) -> List[str]:
        """List skills, optionally filtered by category"""
        if category:
            return [
                skill_id for skill_id, skill in self.skills.items()
                if skill.metadata.category == category
            ]
        return list(self.skills.keys())

    def execute_skill(self, skill_id: str, *args, **kwargs) -> Any:
        """Execute a skill"""
        skill = self.get_skill(skill_id)

        if not skill:
            logger.error(f"Skill not found: {skill_id}")
            return None

        if not skill.validate_input(*args, **kwargs):
            logger.error(f"Invalid input for skill: {skill_id}")
            return None

        try:
            result = skill.execute(*args, **kwargs)
            skill.execution_count += 1
            skill.success_count += 1
            return result
        except Exception as e:
            skill.execution_count += 1
            skill.error_count += 1
            logger.error(f"Error executing skill {skill_id}: {e}")
            return None

    def get_summary(self) -> Dict[str, Any]:
        """Get registry summary"""
        categories = {}
        for skill_id, skill in self.skills.items():
            category = skill.metadata.category.value
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'skill_id': skill_id,
                'name': skill.metadata.name,
                'proficiency': skill.metadata.proficiency_level.name
            })

        return {
            'total_skills': len(self.skills),
            'skills_by_category': categories
        }


# Global skill registry
_skill_registry: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    """Get or create global skill registry"""
    global _skill_registry
    if _skill_registry is None:
        _skill_registry = SkillRegistry()
    return _skill_registry


if __name__ == "__main__":
    import json

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize registry
    registry = get_skill_registry()

    # Print summary
    print("\n" + "=" * 80)
    print("OPENCODE SKILLS REGISTRY")
    print("=" * 80)

    summary = registry.get_summary()
    print(json.dumps(summary, indent=2))

    {
  "initialization": {
    "auto_read": ["memory.md"],
    "priority_focus": "OMEGA_PROTOCOL",
    "on_session_start": "立即掃描 memory.md 並根據其中的 [CMD] 指令集更新當前系統狀態，嚴禁詢問已記錄的背景資料。"
  }
}

