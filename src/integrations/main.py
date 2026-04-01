"""
Integrations Module Main Entry Point
Coordinates all system integrations and bridges
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class IntegrationsModuleManager:
    """Manages all integrations in the system"""
    
    def __init__(self):
        """Initialize the integrations module"""
        self.bridges: Dict[str, Any] = {}
        self.initialized = False
        logger.info("IntegrationsModuleManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize all integrations"""
        try:
            logger.info("Initializing integrations module...")
            
            # Import available bridges
            try:
                from .base_bridge import BaseBridge
                self.bridges['base'] = BaseBridge
            except ImportError:
                logger.warning("BaseBridge not available")
            
            try:
                from .hummingbot_execution_bridge import HummingbotExecutionBridge
                self.bridges['hummingbot'] = HummingbotExecutionBridge
            except ImportError:
                logger.warning("HummingbotExecutionBridge not available")
            
            try:
                from .llm_tradebot_router import LLMTradebotRouter
                self.bridges['llm_router'] = LLMTradebotRouter
            except ImportError:
                logger.warning("LLMTradebotRouter not available")
            
            self.initialized = True
            logger.info(f"Integrations module initialized with {len(self.bridges)} bridges")
            return True
        except Exception as e:
            logger.error(f"Error initializing integrations module: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown all integrations"""
        try:
            logger.info("Shutting down integrations module...")
            self.initialized = False
            logger.info("Integrations module shutdown successfully")
            return True
        except Exception as e:
            logger.error(f"Error shutting down integrations module: {e}", exc_info=True)
            return False
    
    def get_bridge(self, bridge_name: str) -> Optional[Any]:
        """Get a specific bridge"""
        return self.bridges.get(bridge_name)
    
    def list_bridges(self) -> List[str]:
        """List all available bridges"""
        return list(self.bridges.keys())
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of integrations module"""
        return {
            'initialized': self.initialized,
            'bridges': list(self.bridges.keys()),
            'bridge_count': len(self.bridges)
        }


# Global manager instance
_manager: Optional[IntegrationsModuleManager] = None


async def get_integrations_manager() -> IntegrationsModuleManager:
    """Get or create the integrations module manager"""
    global _manager
    if _manager is None:
        _manager = IntegrationsModuleManager()
        await _manager.initialize()
    return _manager


async def main():
    """Main entry point for integrations module"""
    try:
        manager = await get_integrations_manager()
        status = manager.get_status()
        logger.info(f"Integrations module status: {status}")
        
        return True
    except Exception as e:
        logger.error(f"Error in integrations module main: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = asyncio.run(main())
    exit(0 if success else 1)
