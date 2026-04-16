"""
Core Module Main Entry Point
Initializes and coordinates core system components
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CoreModuleManager:
    """Manages core system components"""
    
    def __init__(self):
        """Initialize the core module"""
        self.components: Dict[str, Any] = {}
        self.initialized = False
        logger.info("CoreModuleManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize core components"""
        try:
            logger.info("Initializing core module...")
            
            # Import core components
            from .base_engine import BaseEngine, EngineConfig
            from .engine_factory import EngineFactory, get_engine_factory
            from .engine_registry import EngineRegistry, get_engine_registry
            
            self.components = {
                'engine_factory': get_engine_factory(),
                'engine_registry': get_engine_registry(),
            }
            
            self.initialized = True
            logger.info("Core module initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing core module: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown core components"""
        try:
            logger.info("Shutting down core module...")
            
            # Stop all engines if factory exists
            if 'engine_factory' in self.components:
                factory = self.components['engine_factory']
                await factory.stop_all()
            
            self.initialized = False
            logger.info("Core module shutdown successfully")
            return True
        except Exception as e:
            logger.error(f"Error shutting down core module: {e}", exc_info=True)
            return False
    
    def get_engine_factory(self):
        """Get the engine factory"""
        return self.components.get('engine_factory')
    
    def get_engine_registry(self):
        """Get the engine registry"""
        return self.components.get('engine_registry')
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of core module"""
        factory_status = {}
        if 'engine_factory' in self.components:
            factory = self.components['engine_factory']
            factory_status = factory.get_status_all()
        
        return {
            'initialized': self.initialized,
            'components': list(self.components.keys()),
            'engines': factory_status
        }


# Global manager instance
_manager: Optional[CoreModuleManager] = None


async def get_core_manager() -> CoreModuleManager:
    """Get or create the core module manager"""
    global _manager
    if _manager is None:
        _manager = CoreModuleManager()
        await _manager.initialize()
    return _manager


async def main():
    """Main entry point for core module"""
    try:
        manager = await get_core_manager()
        status = manager.get_status()
        logger.info(f"Core module status: {status}")
        
        return True
    except Exception as e:
        logger.error(f"Error in core module main: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = asyncio.run(main())
    exit(0 if success else 1)
