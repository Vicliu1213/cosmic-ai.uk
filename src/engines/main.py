"""
Engines Module Main Entry Point
Manages all exchange client implementations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class EnginesModuleManager:
    """Manages all exchange client engines"""
    
    def __init__(self):
        """Initialize the engines module"""
        self.clients: Dict[str, Any] = {}
        self.initialized = False
        logger.info("EnginesModuleManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize all exchange clients"""
        try:
            logger.info("Initializing engines module...")
            
            # Import exchange clients
            try:
                from .base_client import BaseClient
                self.clients['base'] = BaseClient
            except ImportError:
                logger.warning("BaseClient not available")
            
            try:
                from .binance_client import BinanceClient
                self.clients['binance'] = BinanceClient
            except ImportError:
                logger.warning("BinanceClient not available")
            
            try:
                from .kraken_client import KrakenClient
                self.clients['kraken'] = KrakenClient
            except ImportError:
                logger.warning("KrakenClient not available")
            
            try:
                from .bitget_client import BitgetClient
                self.clients['bitget'] = BitgetClient
            except ImportError:
                logger.warning("BitgetClient not available")
            
            try:
                from .bybit_client import BybitClient
                self.clients['bybit'] = BybitClient
            except ImportError:
                logger.warning("BybitClient not available")
            
            try:
                from .okx_client import OKXClient
                self.clients['okx'] = OKXClient
            except ImportError:
                logger.warning("OKXClient not available")
            
            self.initialized = True
            logger.info(f"Engines module initialized with {len(self.clients)} clients")
            return True
        except Exception as e:
            logger.error(f"Error initializing engines module: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown all exchange clients"""
        try:
            logger.info("Shutting down engines module...")
            self.initialized = False
            logger.info("Engines module shutdown successfully")
            return True
        except Exception as e:
            logger.error(f"Error shutting down engines module: {e}", exc_info=True)
            return False
    
    def get_client(self, client_name: str) -> Optional[Any]:
        """Get a specific exchange client"""
        return self.clients.get(client_name)
    
    def list_clients(self) -> List[str]:
        """List all available exchange clients"""
        return list(self.clients.keys())
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of engines module"""
        return {
            'initialized': self.initialized,
            'clients': list(self.clients.keys()),
            'client_count': len(self.clients)
        }


# Global manager instance
_manager: Optional[EnginesModuleManager] = None


async def get_engines_manager() -> EnginesModuleManager:
    """Get or create the engines module manager"""
    global _manager
    if _manager is None:
        _manager = EnginesModuleManager()
        await _manager.initialize()
    return _manager


async def main():
    """Main entry point for engines module"""
    try:
        manager = await get_engines_manager()
        status = manager.get_status()
        logger.info(f"Engines module status: {status}")
        
        return True
    except Exception as e:
        logger.error(f"Error in engines module main: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = asyncio.run(main())
    exit(0 if success else 1)
