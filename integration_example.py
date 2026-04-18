#!/usr/bin/env python3
"""
Cosmic Engine Integration Example
宇宙引擎整合示例

Demonstrates parallel data processing across all 15 Cosmic Theory Actors.
Shows how to:
- Spawn all actors
- Send data to all actors in parallel
- Process results from multiple actors concurrently
- Aggregate findings
"""

import ray
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import sys
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path.parent))


class CosmicIntegrationExample:
    """
    Integration example for Cosmic Engine with all 15 theory actors
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
    
    def __init__(self):
        """Initialize example"""
        self.actors: Dict[str, Any] = {}
        self.results: Dict[str, List[Dict[str, Any]]] = {}
        self.start_time = datetime.now()
        
    def initialize_ray(self) -> bool:
        """Initialize Ray"""
        try:
            if not ray.is_initialized():
                ray.init(
                    object_store_memory=1_000_000_000,
                    ignore_reinit_error=True,
                    log_to_driver=False
                )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Ray: {e}")
            return False
    
    def spawn_actors(self) -> bool:
        """Spawn all theory actors"""
        logger.info("\n" + "=" * 70)
        logger.info("SPAWNING ACTORS")
        logger.info("=" * 70)
        
        for theory in self.THEORIES:
            try:
                module_name = f"cosmic_engine.src.{theory}.core"
                core_module = __import__(module_name, fromlist=[''])
                
                actor_classes = [
                    name for name in dir(core_module)
                    if name.endswith('Actor') and not name.startswith('_')
                ]
                
                if actor_classes:
                    ActorClass = getattr(core_module, actor_classes[0])
                    actor_ref = ActorClass.remote()
                    self.actors[theory] = actor_ref
                    ray.get(actor_ref.initialize.remote())
                    logger.info(f"✓ {theory}: Spawned and initialized")
                    
            except Exception as e:
                logger.error(f"✗ {theory}: Failed - {e}")
        
        logger.info(f"\n✓ Spawned {len(self.actors)}/15 actors")
        return len(self.actors) == 15
    
    def generate_test_data(self, size: int = 100) -> Dict[str, Any]:
        """Generate test data for processing"""
        logger.info("\n" + "=" * 70)
        logger.info("GENERATING TEST DATA")
        logger.info("=" * 70)
        
        data = {
            "vector": np.random.rand(size).tolist(),
            "matrix": np.random.rand(size, size).tolist(),
            "signal": np.sin(np.linspace(0, 2*np.pi, size)).tolist(),
            "timestamps": [
                (datetime.now().timestamp() + i) for i in range(size)
            ],
            "metadata": {
                "source": "cosmic_integration_example",
                "version": "1.0",
                "created_at": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✓ Generated test data:")
        logger.info(f"  - Vector size: {len(data['vector'])}")
        logger.info(f"  - Matrix shape: {len(data['matrix'])}x{len(data['matrix'][0])}")
        logger.info(f"  - Signal size: {len(data['signal'])}")
        
        return data
    
    def submit_data_to_all_actors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit data to all actors in parallel
        
        Each actor receives the same data but processes it according to its theory
        """
        logger.info("\n" + "=" * 70)
        logger.info("SUBMITTING DATA TO ALL ACTORS (PARALLEL)")
        logger.info("=" * 70)
        
        futures = {}
        
        # Submit data to all actors
        for theory, actor_ref in self.actors.items():
            try:
                # Each actor's process method has different signatures, so we
                # send a generic data structure that can be interpreted
                future = actor_ref.run_cycle.remote(
                    np.array(data["vector"][:50])  # Send a subset as numpy array
                )
                futures[theory] = future
                logger.info(f"✓ {theory}: Data submitted")
                
            except AttributeError:
                # Some actors might not have run_cycle, try execute instead
                try:
                    future = actor_ref.execute.remote(data)
                    futures[theory] = future
                    logger.info(f"✓ {theory}: Data submitted via execute")
                except Exception as e:
                    logger.warning(f"⚠ {theory}: Could not submit data - {e}")
        
        # Collect results
        logger.info("\n" + "-" * 70)
        logger.info("COLLECTING RESULTS FROM ALL ACTORS")
        logger.info("-" * 70)
        
        results = {}
        
        for theory, future in futures.items():
            try:
                result = ray.get(future, timeout=30)
                results[theory] = result
                logger.info(f"✓ {theory}: Result received")
                
                # Store in results dict
                if theory not in self.results:
                    self.results[theory] = []
                self.results[theory].append({
                    "timestamp": datetime.now().isoformat(),
                    "result": result
                })
                
            except ray.exceptions.GetTimeoutError:
                logger.error(f"✗ {theory}: Timeout waiting for result")
            except Exception as e:
                logger.error(f"✗ {theory}: Failed to get result - {e}")
        
        return results
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status from all actors"""
        logger.info("\n" + "=" * 70)
        logger.info("GETTING STATUS FROM ALL ACTORS")
        logger.info("=" * 70)
        
        futures = {}
        
        for theory, actor_ref in self.actors.items():
            try:
                futures[theory] = actor_ref.get_status.remote()
            except Exception as e:
                logger.warning(f"⚠ {theory}: Could not request status - {e}")
        
        status_results = {}
        
        for theory, future in futures.items():
            try:
                status = ray.get(future, timeout=10)
                status_results[theory] = status
                logger.info(f"✓ {theory}: {status}")
                
            except Exception as e:
                logger.error(f"✗ {theory}: Status failed - {e}")
        
        return status_results
    
    def aggregate_results(self) -> Dict[str, Any]:
        """Aggregate results from all actors"""
        logger.info("\n" + "=" * 70)
        logger.info("AGGREGATING RESULTS")
        logger.info("=" * 70)
        
        aggregated = {
            "total_actors": len(self.actors),
            "actors_with_results": len([t for t in self.THEORIES if t in self.results]),
            "total_processing_time": str(datetime.now() - self.start_time),
            "execution_time": datetime.now().isoformat(),
            "theory_results": {}
        }
        
        for theory in self.THEORIES:
            if theory in self.results and self.results[theory]:
                aggregated["theory_results"][theory] = {
                    "execution_count": len(self.results[theory]),
                    "last_result": self.results[theory][-1]
                }
        
        logger.info(f"✓ Total actors: {aggregated['total_actors']}")
        logger.info(f"✓ Actors with results: {aggregated['actors_with_results']}")
        logger.info(f"✓ Processing time: {aggregated['total_processing_time']}")
        
        return aggregated
    
    def shutdown(self) -> bool:
        """Gracefully shutdown all actors"""
        logger.info("\n" + "=" * 70)
        logger.info("SHUTTING DOWN ALL ACTORS")
        logger.info("=" * 70)
        
        futures = {}
        
        for theory, actor_ref in self.actors.items():
            try:
                futures[theory] = actor_ref.shutdown.remote()
            except Exception as e:
                logger.warning(f"⚠ {theory}: Could not send shutdown - {e}")
        
        shutdown_count = 0
        
        for theory, future in futures.items():
            try:
                ray.get(future, timeout=10)
                logger.info(f"✓ {theory}: Shut down")
                shutdown_count += 1
            except Exception as e:
                logger.error(f"✗ {theory}: Shutdown failed - {e}")
        
        ray.shutdown()
        logger.info(f"\n✓ Ray cluster shut down ({shutdown_count}/15 actors)")
        
        return shutdown_count == 15
    
    def run_integration_demo(self):
        """Run the complete integration demo"""
        logger.info("=" * 70)
        logger.info("COSMIC ENGINE INTEGRATION EXAMPLE")
        logger.info("=" * 70)
        logger.info(f"Start time: {self.start_time.isoformat()}")
        
        # Initialize Ray
        if not self.initialize_ray():
            logger.error("Failed to initialize Ray")
            return False
        
        # Spawn actors
        if not self.spawn_actors():
            logger.error("Failed to spawn all actors")
            self.shutdown()
            return False
        
        # Generate test data
        test_data = self.generate_test_data(size=100)
        
        # Submit data to all actors (parallel processing)
        results = self.submit_data_to_all_actors(test_data)
        
        # Get status from all actors
        status = self.get_all_status()
        
        # Aggregate results
        aggregated = self.aggregate_results()
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("INTEGRATION DEMO SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total theories: {len(self.THEORIES)}")
        logger.info(f"Actors initialized: {len(self.actors)}")
        logger.info(f"Actors with results: {aggregated['actors_with_results']}")
        logger.info(f"Processing time: {aggregated['total_processing_time']}")
        
        # Shutdown
        self.shutdown()
        
        logger.info("\n✓ Integration demo completed successfully!")
        return True


def main():
    """Main entry point"""
    example = CosmicIntegrationExample()
    success = example.run_integration_demo()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
