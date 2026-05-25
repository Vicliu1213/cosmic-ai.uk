"""理論 Actor 自動生成 — 掃描、實例化、生命周期"""

import ray
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

THEORIES = [
    "quantum_singularity", "temporal_dominance", "cosmic_intelligence",
    "platform_heterogeneous", "neuro_quantum_synergy", "quantum_bio_fusion",
    "cosmic_engineering", "reality_programming", "perfect_fortress",
    "topological_bio", "chaos_resonance", "fractal_recursion",
    "quantum_holography", "bio_photonics", "consciousness_field",
]


class ActorOrchestrator:
    def __init__(self):
        self.actors: Dict[str, Any] = {}
        self.status: Dict[str, str] = {}

    def spawn_all(self) -> int:
        for theory in THEORIES:
            name = theory[0].upper() + theory[1:].replace("_", "") + "Actor"
            try:
                mod = __import__(theory + ".core", fromlist=[""])
                if hasattr(mod, name):
                    self.actors[theory] = getattr(mod, name).remote()
                    self.status[theory] = "active"
                    logger.info(f"  + {theory}: {name}")
                else:
                    self.status[theory] = "skipped"
                    logger.info(f"  ~ {theory}: no actor class")
            except Exception as e:
                self.status[theory] = f"error: {e}"
                logger.warning(f"  - {theory}: {e}")
        return len(self.actors)

    def get_all_status(self) -> Dict[str, dict]:
        futures = {}
        for theory, ref in self.actors.items():
            try:
                futures[theory] = ref.get_status.remote()
            except Exception:
                pass
        results = {}
        for theory, future in futures.items():
            try:
                results[theory] = ray.get(future, timeout=10)
            except Exception as e:
                results[theory] = {"error": str(e)}
        return results

    def shutdown_all(self):
        for ref in self.actors.values():
            try:
                ref.shutdown.remote()
            except Exception:
                pass
        self.actors.clear()
        self.status.clear()
        logger.info("All actors shut down")
