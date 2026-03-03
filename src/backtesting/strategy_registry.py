#!/usr/bin/env python3
"""
Strategy Registry & Loader
策略登錄與加載器 - 動態策略發現與實例化

This module enables dynamic discovery and loading of strategies
without hard-coding imports everywhere.
"""

import logging
from typing import Dict, Type, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class StrategyCategory(Enum):
    """Strategy classification."""
    QUANTUM = "quantum"          # Quantum-inspired algorithms
    CLASSIC = "classic"          # Traditional market-making
    HYBRID = "hybrid"            # Combinations of strategies


class StrategyRegistry:
    """
    Central registry for all available strategies.
    
    Usage:
        registry = StrategyRegistry()
        cosmic = registry.load('cosmic', config={...})
        all_quantum = registry.list_by_category('quantum')
    """
    
    def __init__(self):
        """Initialize registry."""
        self._strategies: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[StrategyCategory, List[str]] = {
            StrategyCategory.QUANTUM: [],
            StrategyCategory.CLASSIC: [],
            StrategyCategory.HYBRID: []
        }
        self._modules_loaded = False
    
    def register(
        self,
        name: str,
        adapter_class: Type,
        category: StrategyCategory,
        description: str = "",
        required_config: List[str] = None
    ) -> None:
        """
        Register a strategy adapter.
        
        Args:
            name: Strategy identifier (e.g., 'cosmic_triangular')
            adapter_class: Strategy adapter class
            category: Strategy category
            description: Human-readable description
            required_config: List of required config keys
        """
        if name in self._strategies:
            logger.warning(f"Strategy '{name}' already registered, overwriting")
        
        self._strategies[name] = {
            'adapter_class': adapter_class,
            'category': category,
            'description': description,
            'required_config': required_config or []
        }
        
        if name not in self._categories[category]:
            self._categories[category].append(name)
        
        logger.debug(f"Registered strategy: {name} ({category.value})")
    
    def load(self, name: str, config: Dict[str, Any] = None):
        """
        Load a strategy by name.
        
        Args:
            name: Strategy identifier
            config: Strategy configuration
            
        Returns:
            Instantiated strategy adapter
            
        Raises:
            ValueError: If strategy not found
        """
        if name not in self._strategies:
            available = ', '.join(self._strategies.keys())
            raise ValueError(
                f"Strategy '{name}' not registered. "
                f"Available: {available}"
            )
        
        spec = self._strategies[name]
        adapter_class = spec['adapter_class']
        
        # Validate config
        if config is None:
            config = {}
        
        for required_key in spec['required_config']:
            if required_key not in config:
                logger.warning(
                    f"Strategy '{name}' missing required config: {required_key}"
                )
        
        # Instantiate adapter
        logger.info(f"Loading strategy: {name}")
        try:
            adapter = adapter_class(config=config)
            logger.info(f"✓ Loaded {name} successfully")
            return adapter
        except Exception as e:
            logger.error(f"✗ Failed to load {name}: {e}", exc_info=True)
            raise
    
    def list_all(self) -> List[str]:
        """List all registered strategies."""
        return list(self._strategies.keys())
    
    def list_by_category(self, category: StrategyCategory) -> List[str]:
        """List strategies by category."""
        return self._categories.get(category, [])
    
    def get_info(self, name: str) -> Dict[str, Any]:
        """Get strategy metadata."""
        if name not in self._strategies:
            raise ValueError(f"Strategy '{name}' not found")
        
        spec = self._strategies[name]
        return {
            'name': name,
            'category': spec['category'].value,
            'description': spec['description'],
            'required_config': spec['required_config'],
            'adapter_class': spec['adapter_class'].__name__
        }
    
    def list_all_info(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all strategies."""
        return {name: self.get_info(name) for name in self._strategies}


# Global registry instance
_global_registry: Optional[StrategyRegistry] = None


def get_registry() -> StrategyRegistry:
    """Get global strategy registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = StrategyRegistry()
        _register_all_strategies(_global_registry)
    return _global_registry


def _register_all_strategies(registry: StrategyRegistry) -> None:
    """Register all built-in strategies."""
    logger.info("Registering all built-in strategies...")
    
    try:
        # Quantum strategies
        from src.integrations.strategy_adapters.cosmic_adapter import CosmicStrategyAdapter
        
        registry.register(
            name='cosmic_triangular_arbitrage',
            adapter_class=CosmicStrategyAdapter,
            category=StrategyCategory.QUANTUM,
            description='Cosmic system with triangular arbitrage detection',
            required_config=[]
        )
        
        registry.register(
            name='cosmic_wormhole_arbitrage',
            adapter_class=CosmicStrategyAdapter,
            category=StrategyCategory.QUANTUM,
            description='Cosmic system with wormhole arbitrage detection',
            required_config=[]
        )
        
        # Classic strategies
        from src.integrations.strategy_adapters.hummingbot_adapter import HummerbotStrategyAdapter
        from src.integrations.strategy_adapters.llm_adapter import LLMStrategyAdapter
        
        registry.register(
            name='hummingbot_pure_market_making',
            adapter_class=HummerbotStrategyAdapter,
            category=StrategyCategory.CLASSIC,
            description='Hummingbot pure market making with dual-sided quotes',
            required_config=[]
        )
        
        registry.register(
            name='hummingbot_avellaneda_stoikov',
            adapter_class=HummerbotStrategyAdapter,
            category=StrategyCategory.CLASSIC,
            description='Hummingbot Avellaneda-Stoikov optimal spread strategy',
            required_config=[]
        )
        
        registry.register(
            name='llm_debate_framework',
            adapter_class=LLMStrategyAdapter,
            category=StrategyCategory.CLASSIC,
            description='LLM-based debate framework with 3 agents',
            required_config=[]
        )
        
        # Hybrid strategies
        registry.register(
            name='hybrid_cosmic_hummingbot',
            adapter_class=CosmicStrategyAdapter,
            category=StrategyCategory.HYBRID,
            description='Cosmic decision-making + Hummingbot execution',
            required_config=[]
        )
        
        registry.register(
            name='optimal_combo_all',
            adapter_class=CosmicStrategyAdapter,
            category=StrategyCategory.HYBRID,
            description='Cosmic + Hummingbot + LLM (optimal combination)',
            required_config=[]
        )
        
        logger.info("✓ Registered 7 strategies successfully")
    
    except ImportError as e:
        logger.error(f"Failed to register strategies: {e}", exc_info=True)
        raise


def list_strategies(category: Optional[str] = None) -> List[str]:
    """
    List available strategies.
    
    Args:
        category: Filter by category ('quantum', 'classic', 'hybrid')
        
    Returns:
        List of strategy names
    """
    registry = get_registry()
    
    if category is None:
        return registry.list_all()
    
    try:
        cat = StrategyCategory(category)
        return registry.list_by_category(cat)
    except ValueError:
        raise ValueError(
            f"Invalid category: {category}. "
            f"Must be one of: {', '.join([c.value for c in StrategyCategory])}"
        )


def load_strategy(name: str, config: Dict[str, Any] = None):
    """
    Load a strategy by name.
    
    Args:
        name: Strategy identifier
        config: Strategy configuration
        
    Returns:
        Instantiated strategy adapter
    """
    registry = get_registry()
    return registry.load(name, config)


if __name__ == "__main__":
    import json
    
    registry = get_registry()
    
    print("\n" + "=" * 80)
    print("STRATEGY REGISTRY - AVAILABLE STRATEGIES")
    print("=" * 80)
    
    for category in StrategyCategory:
        strategies = registry.list_by_category(category)
        print(f"\n{category.value.upper()} ({len(strategies)} strategies):")
        for name in strategies:
            info = registry.get_info(name)
            print(f"  • {name}")
            print(f"    Description: {info['description']}")
    
    print("\n" + "=" * 80)
    print("FULL REGISTRY JSON")
    print("=" * 80)
    all_info = registry.list_all_info()
    print(json.dumps(all_info, indent=2, default=str))
