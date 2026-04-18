#!/usr/bin/env python3
"""
Test all 15 Cosmic Theory Ray Actors
宇宙理論 - 15個射線參與者測試

This script tests that all 15 theory modules can be imported and their
Ray Actor classes can be instantiated.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path.parent))

# Theory modules
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


def test_imports():
    """Test that all theory modules can be imported."""
    logger.info("=" * 60)
    logger.info("TESTING MODULE IMPORTS")
    logger.info("=" * 60)
    
    import_results = {}
    
    for theory in THEORIES:
        try:
            # Import the core module
            module_name = f"cosmic_engine.src.{theory}"
            exec(f"from {module_name} import core")
            import_results[theory] = "✓ PASS"
            logger.info(f"✓ {theory}: Successfully imported")
        except Exception as e:
            import_results[theory] = f"✗ FAIL: {str(e)}"
            logger.error(f"✗ {theory}: Import failed - {e}")
    
    return import_results


def test_actor_instantiation():
    """Test that Ray Actor classes can be instantiated."""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING ACTOR INSTANTIATION")
    logger.info("=" * 60)
    
    import ray
    
    # Initialize Ray
    if not ray.is_initialized():
        logger.info("Initializing Ray...")
        ray.init(ignore_reinit_error=True, log_to_driver=False)
    
    actor_results = {}
    actors_created = []
    
    for theory in THEORIES:
        try:
            # Dynamically import the core module
            module_name = f"cosmic_engine.src.{theory}.core"
            core_module = __import__(module_name, fromlist=[''])
            
            # Find any class that ends with 'Actor' in the module
            actor_classes = [name for name in dir(core_module) if name.endswith('Actor') and not name.startswith('_')]
            
            if actor_classes:
                # Use the first Actor class found
                class_name = actor_classes[0]
                ActorClass = getattr(core_module, class_name)
                
                # Create remote actor
                actor_ref = ActorClass.remote()
                actors_created.append((theory, actor_ref))
                actor_results[theory] = "✓ PASS"
                logger.info(f"✓ {theory}: Actor created - {class_name}")
            else:
                available_classes = [name for name in dir(core_module) if not name.startswith('_')]
                actor_results[theory] = f"✗ FAIL: No Actor class found"
                logger.error(f"✗ {theory}: No Actor class found. Available: {available_classes}")
                
        except Exception as e:
            actor_results[theory] = f"✗ FAIL: {str(e)}"
            logger.error(f"✗ {theory}: Instantiation failed - {e}")
    
    # Test actor methods
    logger.info("\n" + "=" * 60)
    logger.info("TESTING ACTOR METHODS")
    logger.info("=" * 60)
    
    method_results = {}
    
    for theory, actor_ref in actors_created:
        try:
            # Test initialize
            ray.get(actor_ref.initialize.remote())
            logger.info(f"✓ {theory}: initialize() successful")
            
            # Test get_status
            status = ray.get(actor_ref.get_status.remote())
            logger.info(f"✓ {theory}: get_status() returned {status}")
            
            method_results[theory] = "✓ PASS"
            
        except Exception as e:
            method_results[theory] = f"✗ FAIL: {str(e)}"
            logger.error(f"✗ {theory}: Method test failed - {e}")
    
    # Shutdown actors
    logger.info("\n" + "=" * 60)
    logger.info("SHUTTING DOWN ACTORS")
    logger.info("=" * 60)
    
    for theory, actor_ref in actors_created:
        try:
            ray.get(actor_ref.shutdown.remote())
            logger.info(f"✓ {theory}: shutdown() successful")
        except Exception as e:
            logger.error(f"✗ {theory}: Shutdown failed - {e}")
    
    ray.shutdown()
    
    return actor_results, method_results, actors_created


def print_summary(import_results, actor_results, method_results, actors_created):
    """Print test summary."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    import_pass = sum(1 for v in import_results.values() if "✓" in v)
    actor_pass = sum(1 for v in actor_results.values() if "✓" in v)
    method_pass = sum(1 for v in method_results.values() if "✓" in v)
    
    logger.info(f"\nImports: {import_pass}/{len(THEORIES)} passed")
    logger.info(f"Actor Instantiation: {actor_pass}/{len(THEORIES)} passed")
    logger.info(f"Actor Methods: {method_pass}/{len(actors_created)} passed")
    
    total_pass = import_pass + actor_pass + method_pass
    total_tests = len(THEORIES) + len(THEORIES) + len(actors_created)
    
    logger.info(f"\nOverall: {total_pass}/{total_tests} tests passed")
    
    if total_pass == total_tests and total_tests > 0:
        logger.info("\n✓ ALL TESTS PASSED!")
        return True
    else:
        logger.info(f"\n✗ {total_tests - total_pass} tests failed")
        return False


def main():
    """Run all tests."""
    logger.info("Starting Cosmic Engine Ray Actor Tests")
    logger.info(f"Testing {len(THEORIES)} theory modules")
    
    import_results = test_imports()
    actor_results, method_results, actors_created = test_actor_instantiation()
    success = print_summary(import_results, actor_results, method_results, actors_created)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
