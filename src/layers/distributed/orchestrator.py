"""分布式協同編排器 — 一鍵啟動所有層"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

from .cluster import DistributedCluster
from .actors import ActorOrchestrator
from .synergy import SynergyEngine
from .fleet import CrocodileFleet
from .consciousness import ConsciousnessLayer
from .evolution import EvolutionEngine

COSMIC_WS = Path(__file__).parent.parent.parent.parent


class DistributedOrchestrator:
    def __init__(self, config_path: str = "config/cosmic_config.yaml"):
        self.config_path = COSMIC_WS / config_path
        self.config = self._load_config()
        self.cluster = DistributedCluster()
        self.actors = ActorOrchestrator()
        self.synergy = SynergyEngine()
        self.fleet: Optional[CrocodileFleet] = None
        self.consciousness: Optional[ConsciousnessLayer] = None
        self.evolution: Optional[EvolutionEngine] = None
        self.fleet_traders = []
        self.consciousness_ref = None
        self.evolution_ref = None
        self._dashboard_server = None

    def _load_config(self) -> dict:
        import yaml
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Config load failed: {e}")
            return {}

    def deploy_all(self) -> Dict[str, Any]:
        results = {}
        start = time.time()

        # Layer 1: Cluster
        ns = self.config.get("system", {}).get("namespace", "cosmic")
        ok = self.cluster.init()
        results["cluster"] = "ready" if ok else "failed"
        if not ok:
            return results

        # Layer 2: Theory Actors
        n = self.actors.spawn_all()
        results["actors"] = f"{n}/15 spawned"

        # Layer 3: Crocodile Fleet
        self.fleet = CrocodileFleet(self.config.get("trading", {}))
        self.fleet_traders = self.fleet.deploy()
        results["fleet"] = f"{len(self.fleet_traders)} traders"

        # Layer 4: Consciousness
        self.consciousness = ConsciousnessLayer(self.config)
        self.consciousness_ref = self.consciousness.deploy()
        results["consciousness"] = "deployed" if self.consciousness_ref else "disabled"

        # Layer 5: Evolution
        self.evolution = EvolutionEngine(self.config)
        self.evolution_ref = self.evolution.deploy()
        results["evolution"] = "deployed" if self.evolution_ref else "disabled"

        # Layer 6: Synergy Recording
        self.synergy.record_all(consciousness=0.5)
        results["synergy"] = f"{len(self.synergy.snapshots)} levels recorded"

        # Layer 7: Recursive Leap
        leap = self.synergy.recursive_leap()
        results["recursive_depth"] = leap["depth"]
        results["growth_factor"] = leap["growth"]

        elapsed = time.time() - start
        results["elapsed"] = f"{elapsed:.2f}s"
        return results

    def run_live_cycle(self) -> Dict[str, Any]:
        results = {}

        # Fleet trading cycle
        if self.fleet and self.fleet_traders:
            fleet_results = self.fleet.run_cycle()
            results["fleet"] = [
                f"{r['trader_id']} [{r['symbol']}] {r.get('execution',{}).get('status','?')}"
                for r in fleet_results
            ]

        # Consciousness reflection on fleet
        if self.consciousness and self.consciousness_ref:
            fleet_status = self.fleet.get_status() if self.fleet else []
            ref = self.consciousness.reflect_on_fleet(fleet_status)
            results["consciousness"] = {
                "state": ref.get("awakening_state"),
                "level": ref.get("consciousness_level"),
                "drrk": ref.get("drrk_grade"),
                "intent": ref.get("autonomous_intent"),
            }

        # Evolution
        if self.evolution and self.evolution_ref:
            evo = self.evolution.run_generation()
            results["evolution"] = {
                "generation": evo.get("generation"),
                "best_fitness": evo.get("best_fitness"),
            }

        return results

    def get_full_status(self) -> Dict[str, Any]:
        return {
            "cluster": self.cluster.get_status(),
            "actors": self.actors.get_all_status(),
            "synergy": {
                "levels": sorted(self.synergy.snapshots.keys()),
                "depth": self.synergy.recursive_depth,
                "consciousness": self.synergy.global_consciousness,
                "growth": self.synergy.growth_factor,
            },
            "summary": self.synergy.summary_table(),
        }

    def serialize_synergy(self) -> str:
        return self.synergy.to_json()

    def shutdown(self):
        self.actors.shutdown_all()
        self.cluster.shutdown()
        logger.info("DistributedOrchestrator shut down")
