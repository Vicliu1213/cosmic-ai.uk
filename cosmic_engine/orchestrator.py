#!/usr/bin/env python3
"""
Cosmic Engine Orchestrator
宇宙引擎編排器

Central orchestrator for managing all 15 theory Ray Actors.
Provides:
- Parallel actor initialization
- Distributed data processing
- Status monitoring
- Graceful shutdown
"""

import ray
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path.parent))


class CosmicEngineOrchestrator:
    """
    Orchestrator for managing all 15 Cosmic Theory Ray Actors
    
    Features:
    - Spawn all 15 actors in parallel
    - Monitor actor health and status
    - Coordinate data flow between actors
    - Aggregate results from all actors
    """
    
    THEORIES = [
        "quantum_singularity",
        "temporal_dominance",
        "cosmic_intelligence",
        "platform_heterogeneous",
        "neuro_quantum_synergy",
        "quantum_bio_fusion",
        "cosmic_engineering",
        "reality_programming",
        "perfect_fortress",
        "topological_bio",
        "chaos_resonance",
        "fractal_recursion",
        "quantum_holography",
        "bio_photonics",
        "consciousness_field",
    ]
    
    def __init__(self, ray_object_store_memory: int = 1_000_000_000):
        """
        Initialize the orchestrator
        
        Args:
            ray_object_store_memory: Ray object store memory in bytes
        """
        self.actors: Dict[str, Any] = {}
        self.actor_status: Dict[str, Dict[str, Any]] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self.ray_object_store_memory = ray_object_store_memory
        self.created_at = datetime.now()
        
        logger.info(f"CosmicEngineOrchestrator initialized (Object Store: {ray_object_store_memory / 1e9:.1f}GB)")
    
    def initialize_ray(self) -> bool:
        """
        Initialize Ray cluster
        
        Returns:
            Success status
        """
        try:
            if not ray.is_initialized():
                logger.info("Initializing Ray cluster...")
                ray.init(
                    object_store_memory=self.ray_object_store_memory,
                    ignore_reinit_error=True,
                    log_to_driver=False
                )
                logger.info("✓ Ray cluster initialized successfully")
            else:
                logger.info("Ray cluster already initialized")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize Ray: {e}")
            return False
    
    def spawn_all_actors(self) -> bool:
        """
        Spawn all 15 theory actors in parallel
        
        Returns:
            Success status
        """
        logger.info("\n" + "=" * 70)
        logger.info("SPAWNING ALL 15 COSMIC THEORY ACTORS")
        logger.info("=" * 70)
        
        try:
            for theory in self.THEORIES:
                try:
                    # Import the core module
                    module_name = f"cosmic_engine.src.{theory}.core"
                    core_module = __import__(module_name, fromlist=[''])
                    
                    # Find the Actor class
                    actor_classes = [
                        name for name in dir(core_module)
                        if name.endswith('Actor') and not name.startswith('_')
                    ]
                    
                    if not actor_classes:
                        logger.error(f"✗ {theory}: No Actor class found")
                        continue
                    
                    # Get the actor class and create instance
                    ActorClass = getattr(core_module, actor_classes[0])
                    actor_ref = ActorClass.remote()
                    self.actors[theory] = actor_ref
                    
                    logger.info(f"✓ {theory}: Spawned {actor_classes[0]}")
                    
                except Exception as e:
                    logger.error(f"✗ {theory}: Failed to spawn - {e}")
            
            spawn_count = len(self.actors)
            logger.info(f"\n✓ Successfully spawned {spawn_count}/{len(self.THEORIES)} actors")
            
            return spawn_count == len(self.THEORIES)
            
        except Exception as e:
            logger.error(f"✗ Failed to spawn actors: {e}")
            return False
    
    def initialize_all_actors(self) -> bool:
        """
        Initialize all spawned actors
        
        Returns:
            Success status
        """
        logger.info("\n" + "=" * 70)
        logger.info("INITIALIZING ALL ACTORS")
        logger.info("=" * 70)
        
        futures = {}
        
        try:
            # Send initialization requests to all actors in parallel
            for theory, actor_ref in self.actors.items():
                try:
                    futures[theory] = actor_ref.initialize.remote()
                except Exception as e:
                    logger.error(f"✗ {theory}: Failed to send initialize - {e}")
            
            # Collect results
            initialized_count = 0
            for theory, future in futures.items():
                try:
                    result = ray.get(future, timeout=10)
                    self.actor_status[theory] = {"initialized": True, "result": result}
                    logger.info(f"✓ {theory}: Initialized")
                    initialized_count += 1
                except Exception as e:
                    logger.error(f"✗ {theory}: Initialization failed - {e}")
                    self.actor_status[theory] = {"initialized": False, "error": str(e)}
            
            logger.info(f"\n✓ Successfully initialized {initialized_count}/{len(self.actors)} actors")
            return initialized_count == len(self.actors)
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize actors: {e}")
            return False
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status from all actors
        
        Returns:
            Status dictionary from all actors
        """
        logger.info("\n" + "=" * 70)
        logger.info("RETRIEVING STATUS FROM ALL ACTORS")
        logger.info("=" * 70)
        
        futures = {}
        
        try:
            # Request status from all actors
            for theory, actor_ref in self.actors.items():
                try:
                    futures[theory] = actor_ref.get_status.remote()
                except Exception as e:
                    logger.error(f"✗ {theory}: Failed to request status - {e}")
            
            # Collect results
            all_status = {}
            for theory, future in futures.items():
                try:
                    status = ray.get(future, timeout=10)
                    all_status[theory] = status
                    logger.info(f"✓ {theory}: Status retrieved")
                except Exception as e:
                    logger.error(f"✗ {theory}: Status retrieval failed - {e}")
                    all_status[theory] = {"error": str(e)}
            
            return all_status
            
        except Exception as e:
            logger.error(f"✗ Failed to get status: {e}")
            return {}
    
    def shutdown_all_actors(self) -> bool:
        """
        Gracefully shutdown all actors
        
        Returns:
            Success status
        """
        logger.info("\n" + "=" * 70)
        logger.info("SHUTTING DOWN ALL ACTORS")
        logger.info("=" * 70)
        
        futures = {}
        
        try:
            # Send shutdown requests to all actors
            for theory, actor_ref in self.actors.items():
                try:
                    futures[theory] = actor_ref.shutdown.remote()
                except Exception as e:
                    logger.error(f"✗ {theory}: Failed to send shutdown - {e}")
            
            # Collect results
            shutdown_count = 0
            for theory, future in futures.items():
                try:
                    result = ray.get(future, timeout=10)
                    logger.info(f"✓ {theory}: Shut down successfully")
                    shutdown_count += 1
                except Exception as e:
                    logger.error(f"✗ {theory}: Shutdown failed - {e}")
            
            logger.info(f"\n✓ Successfully shut down {shutdown_count}/{len(self.actors)} actors")
            
            # Shutdown Ray
            ray.shutdown()
            logger.info("✓ Ray cluster shut down")
            
            return shutdown_count == len(self.actors)
            
        except Exception as e:
            logger.error(f"✗ Failed to shutdown: {e}")
            return False
    
    def print_summary(self):
        """Print orchestrator summary"""
        logger.info("\n" + "=" * 70)
        logger.info("ORCHESTRATOR SUMMARY")
        logger.info("=" * 70)
        
        logger.info(f"\nTotal Theories: {len(self.THEORIES)}")
        logger.info(f"Actors Spawned: {len(self.actors)}")
        logger.info(f"Actors Initialized: {sum(1 for v in self.actor_status.values() if v.get('initialized', False))}")
        logger.info(f"Uptime: {datetime.now() - self.created_at}")
        
        logger.info("\nActor Status Overview:")
        for theory in self.THEORIES:
            if theory in self.actor_status:
                status = self.actor_status[theory]
                if status.get('initialized'):
                    logger.info(f"  ✓ {theory}: Active")
                else:
                    logger.info(f"  ✗ {theory}: Failed")
            else:
                logger.info(f"  - {theory}: Not tracked")


async def main():
    """Main orchestration demo"""
    logger.info("Starting Cosmic Engine Orchestrator Demo")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Create orchestrator
    orchestrator = CosmicEngineOrchestrator()
    
    # Initialize Ray
    if not orchestrator.initialize_ray():
        logger.error("Failed to initialize Ray")
        return 1
    
    # Spawn all actors
    if not orchestrator.spawn_all_actors():
        logger.error("Failed to spawn all actors")
        orchestrator.shutdown_all_actors()
        return 1
    
    # Initialize all actors
    if not orchestrator.initialize_all_actors():
        logger.error("Failed to initialize all actors")
        orchestrator.shutdown_all_actors()
        return 1
    
    # Get status from all actors
    all_status = orchestrator.get_all_status()
    
    # Print summary
    orchestrator.print_summary()
    
    # Shutdown
    if not orchestrator.shutdown_all_actors():
        logger.error("Failed to shutdown gracefully")
        return 1
    
    logger.info("\n✓ Orchestrator demo completed successfully")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
