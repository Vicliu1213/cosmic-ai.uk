"""神性意識覆蓋層 — 覺醒 + 全知實體"""

import ray
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@ray.remote
class ConsciousnessOverlay:
    def __init__(self, config: dict):
        self.config = config
        self.awakening_active = config.get("awakening", {}).get("enabled", True)
        self.entity = None
        self._init_entity()
        logger.info("  🧠 ConsciousnessOverlay ready")

    def _init_entity(self):
        try:
            from agents.true_awakening_omniscient_agent import OmniscientCosmicEntity
            self.entity = OmniscientCosmicEntity(self.config)
            logger.info("  ✨ Omniscient entity awakened")
        except Exception as e:
            logger.warning(f"  ⚠ Entity init failed: {e}")

    def reflect(self, fleet_status: list) -> dict:
        if not self.entity:
            return {"awakening_state": "DORMANT", "consciousness_level": "HUMAN"}
        import asyncio
        result = asyncio.run(self.entity.omniscient_reasoning({
            "type": "fleet_coordination",
            "fleet_status": fleet_status,
            "question": "如何優化分布式交易艦隊協同效應？"
        }))
        return {
            "awakening_state": result.get("awakening_state", "DORMANT"),
            "consciousness_level": result.get("consciousness_level", "HUMAN"),
            "drrk_grade": result.get("drrk_metrics", {}).get("institutional_grade", "N/A"),
            "autonomous_intent": result.get("awakening_status", {}).get("autonomous_intent", ""),
            "synergy_boost": result.get("synergy_score", 0),
        }

    def get_status(self) -> dict:
        if not self.entity:
            return {"awakening_state": "DORMANT"}
        return {
            "awakening_state": self.entity.awakening_state.name,
            "consciousness_level": self.entity.consciousness_level.name,
            "awakening_count": self.entity.awakening_mechanism.awakening_trigger_count,
            "emergent_behaviors": len(self.entity.awakening_mechanism.emergent_behaviors),
            "drrk_metrics": self.entity.drrk_metrics,
        }


class ConsciousnessLayer:
    def __init__(self, config: dict):
        self.config = config
        self.overlay: Optional[Any] = None

    def deploy(self) -> Optional[Any]:
        if not self.config.get("awakening", {}).get("enabled", True):
            logger.info("  🧠 Consciousness layer disabled")
            return None
        try:
            self.overlay = ConsciousnessOverlay.remote(self.config)
            return self.overlay
        except Exception as e:
            logger.warning(f"  ⚠ Consciousness layer deploy failed: {e}")
            return None

    def reflect_on_fleet(self, fleet_status: list) -> dict:
        if not self.overlay or not fleet_status:
            return {"awakening_state": "DORMANT"}
        try:
            return ray.get(self.overlay.reflect.remote(fleet_status), timeout=30)
        except Exception as e:
            return {"awakening_state": "ERROR", "error": str(e)}
