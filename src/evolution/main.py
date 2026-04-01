"""
Evolution Module Main Entry Point
Manages evolutionary algorithms and genetic programming
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class EvolutionModuleManager:
    """Manages evolutionary algorithms and frameworks"""
    
    def __init__(self):
        """Initialize the evolution module"""
        self.algorithms: Dict[str, Any] = {}
        self.initialized = False
        logger.info("EvolutionModuleManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize evolution algorithms"""
        try:
            logger.info("Initializing evolution module...")
            
            # Import evolution algorithms
            try:
                from .meta import MetaEvolution
                self.algorithms['meta'] = MetaEvolution
            except ImportError:
                logger.warning("MetaEvolution not available")
            
            try:
                from .gene import GeneticAlgorithm
                self.algorithms['genetic'] = GeneticAlgorithm
            except ImportError:
                logger.warning("GeneticAlgorithm not available")
            
            try:
                from .qgrn import QuantumGeneticRoughnessNetwork
                self.algorithms['qgrn'] = QuantumGeneticRoughnessNetwork
            except ImportError:
                logger.warning("QuantumGeneticRoughnessNetwork not available")
            
            self.initialized = True
            logger.info(f"Evolution module initialized with {len(self.algorithms)} algorithms")
            return True
        except Exception as e:
            logger.error(f"Error initializing evolution module: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown evolution module"""
        try:
            logger.info("Shutting down evolution module...")
            self.initialized = False
            logger.info("Evolution module shutdown successfully")
            return True
        except Exception as e:
            logger.error(f"Error shutting down evolution module: {e}", exc_info=True)
            return False
    
    def get_algorithm(self, algo_name: str) -> Optional[Any]:
        """Get a specific evolutionary algorithm"""
        return self.algorithms.get(algo_name)
    
    def list_algorithms(self) -> List[str]:
        """List all available algorithms"""
        return list(self.algorithms.keys())
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of evolution module"""
        return {
            'initialized': self.initialized,
            'algorithms': list(self.algorithms.keys()),
            'algorithm_count': len(self.algorithms)
        }


# Global manager instance
_manager: Optional[EvolutionModuleManager] = None


async def get_evolution_manager() -> EvolutionModuleManager:
    """Get or create the evolution module manager"""
    global _manager
    if _manager is None:
        _manager = EvolutionModuleManager()
        await _manager.initialize()
    return _manager


async def main():
    """Main entry point for evolution module"""
    try:
        manager = await get_evolution_manager()
        status = manager.get_status()
        logger.info(f"Evolution module status: {status}")
        
        return True
    except Exception as e:
        logger.error(f"Error in evolution module main: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = asyncio.run(main())
    exit(0 if success else 1)
