"""
Engine Factory - Creates and manages engine instances
Implements factory pattern for unified engine creation
"""

from typing import Dict, Type, Optional, Any, List
import logging
from .base_engine import BaseEngine, EngineConfig, EngineState

logger = logging.getLogger(__name__)


class EngineFactory:
    """
    Factory class for creating and managing engine instances
    Provides unified interface for engine instantiation and lifecycle management
    """
    
    def __init__(self):
        """Initialize the engine factory"""
        self._engines: Dict[str, BaseEngine] = {}
        self._engine_registry: Dict[str, Type[BaseEngine]] = {}
        self._config_cache: Dict[str, EngineConfig] = {}
    
    def register_engine_class(self, name: str, engine_class: Type[BaseEngine]) -> None:
        """
        Register an engine class with the factory
        
        Args:
            name: Engine name identifier
            engine_class: Engine class (must inherit from BaseEngine)
        
        Raises:
            ValueError: If engine_class doesn't inherit from BaseEngine
        """
        if not issubclass(engine_class, BaseEngine):
            raise ValueError(f"{engine_class} must inherit from BaseEngine")
        
        self._engine_registry[name] = engine_class
        logger.info(f"Registered engine class: {name}")
    
    def create_engine(self, name: str, config: EngineConfig) -> Optional[BaseEngine]:
        """
        Create an engine instance
        
        Args:
            name: Engine name identifier
            config: Engine configuration
        
        Returns:
            Optional[BaseEngine]: Engine instance or None if creation failed
        """
        if name not in self._engine_registry:
            logger.error(f"Engine class '{name}' not registered")
            return None
        
        try:
            engine_class = self._engine_registry[name]
            engine = engine_class(config)
            
            # Store reference for lifecycle management
            instance_name = f"{name}:{config.name}"
            self._engines[instance_name] = engine
            self._config_cache[instance_name] = config
            
            logger.info(f"Created engine instance: {instance_name}")
            return engine
            
        except Exception as e:
            logger.error(f"Error creating engine '{name}': {e}", exc_info=True)
            return None
    
    def get_engine(self, instance_name: str) -> Optional[BaseEngine]:
        """
        Get a registered engine instance
        
        Args:
            instance_name: Engine instance identifier
        
        Returns:
            Optional[BaseEngine]: Engine instance or None if not found
        """
        return self._engines.get(instance_name)
    
    def remove_engine(self, instance_name: str) -> bool:
        """
        Remove an engine from the factory
        
        Args:
            instance_name: Engine instance identifier
        
        Returns:
            bool: True if removed successfully
        """
        if instance_name in self._engines:
            del self._engines[instance_name]
            if instance_name in self._config_cache:
                del self._config_cache[instance_name]
            logger.info(f"Removed engine: {instance_name}")
            return True
        return False
    
    def get_all_engines(self) -> Dict[str, BaseEngine]:
        """
        Get all registered engine instances
        
        Returns:
            Dict: All engine instances indexed by name
        """
        return self._engines.copy()
    
    def get_registered_classes(self) -> Dict[str, Type[BaseEngine]]:
        """
        Get all registered engine classes
        
        Returns:
            Dict: Registered engine classes indexed by name
        """
        return self._engine_registry.copy()
    
    async def start_all(self) -> Dict[str, bool]:
        """
        Start all registered engines
        
        Returns:
            Dict: Start results indexed by engine instance name
        """
        results = {}
        for instance_name, engine in self._engines.items():
            try:
                success = await engine.start()
                results[instance_name] = success
                logger.info(f"Engine {instance_name} start: {'success' if success else 'failed'}")
            except Exception as e:
                results[instance_name] = False
                logger.error(f"Error starting engine {instance_name}: {e}")
        
        return results
    
    async def stop_all(self) -> Dict[str, bool]:
        """
        Stop all registered engines
        
        Returns:
            Dict: Stop results indexed by engine instance name
        """
        results = {}
        for instance_name, engine in self._engines.items():
            try:
                success = await engine.stop()
                results[instance_name] = success
                logger.info(f"Engine {instance_name} stop: {'success' if success else 'failed'}")
            except Exception as e:
                results[instance_name] = False
                logger.error(f"Error stopping engine {instance_name}: {e}")
        
        return results
    
    def get_status_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all engines
        
        Returns:
            Dict: Status information for all engines
        """
        status = {}
        for instance_name, engine in self._engines.items():
            try:
                status[instance_name] = engine.get_status()
            except Exception as e:
                logger.error(f"Error getting status for {instance_name}: {e}")
                status[instance_name] = {'error': str(e)}
        
        return status


# Global factory instance
_global_factory: Optional[EngineFactory] = None


def get_engine_factory() -> EngineFactory:
    """
    Get or create the global engine factory
    
    Returns:
        EngineFactory: Global factory instance
    """
    global _global_factory
    if _global_factory is None:
        _global_factory = EngineFactory()
    return _global_factory


def register_engine_class(name: str, engine_class: Type[BaseEngine]) -> None:
    """
    Register an engine class globally
    
    Args:
        name: Engine name identifier
        engine_class: Engine class
    """
    factory = get_engine_factory()
    factory.register_engine_class(name, engine_class)


def create_engine(name: str, config: EngineConfig) -> Optional[BaseEngine]:
    """
    Create an engine instance globally
    
    Args:
        name: Engine name identifier
        config: Engine configuration
    
    Returns:
        Optional[BaseEngine]: Engine instance
    """
    factory = get_engine_factory()
    return factory.create_engine(name, config)
