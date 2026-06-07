"""
Hermes 技能進化整合層 — 將現有引擎資料灌入 96 技能
"""
import asyncio, json, random, math, os
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone

from src.hermes_evolution.core import (
    HermesEvolutionEngine, SkillNode, MutationClass,
    SKILLS_MASTER, SKILL_VAULT,
)


def build_category_map() -> Dict[str, List[str]]:
    """Map skill categories to their S-range."""
    return {
        "戰鬥异能":   [s[0] for s in SKILLS_MASTER if 1 <= int(s[0][1:]) <= 18],
        "神经增强":   [s[0] for s in SKILLS_MASTER if 19 <= int(s[0][1:]) <= 34],
        "时空操控":   [s[0] for s in SKILLS_MASTER if 35 <= int(s[0][1:]) <= 48],
        "永生肉体":   [s[0] for s in SKILLS_MASTER if 49 <= int(s[0][1:]) <= 60],
        "意识精神":   [s[0] for s in SKILLS_MASTER if 61 <= int(s[0][1:]) <= 74],
        "资本影响":   [s[0] for s in SKILLS_MASTER if 75 <= int(s[0][1:]) <= 86],
        "进化元能力": [s[0] for s in SKILLS_MASTER if 87 <= int(s[0][1:]) <= 96],
    }


def collect_system_data() -> Dict[str, Any]:
    """
    Collect live data from the running engine.
    Returns a dict keyed by category with relevant metrics.
    Falls back to simulated data when engine is not running.
    """
    data = {}

    # ── Try to collect from running Ray cluster ──
    data["_source"] = "simulated"
    data["_timestamp"] = datetime.now(timezone.utc).isoformat()

    # These will be populated by collect_live() when run inside main.py
    data["theory_actors"] = {}
    data["consciousness"] = {}
    data["synergy"] = {}
    data["trading"] = {}
    data["evolution"] = {}
    data["omega"] = {}
    data["awakening"] = {}

    return data


def enrich_context_with_system_data(
    context: dict,
    system_data: dict,
    category: str,
    skill_id: str,
) -> dict:
    """Inject real system metrics into a battle_context based on skill category."""
    ctx = dict(context)

    if category == "戰鬥异能":
        actors = system_data.get("theory_actors", {})
        ctx["theory_expression"] = sum(
            a.get("expression_level", 0.5) for a in actors.values()
        ) / max(len(actors), 1)
        ctx["synergy_score"] = system_data.get("synergy", {}).get("base_synergy", 0.5)

    elif category == "神经增强":
        cs = system_data.get("consciousness", {})
        ctx["consciousness_level"] = cs.get("consciousness_level", "AGI")
        ctx["awakening_state"] = cs.get("awakening_state", "DORMANT")
        ctx["drrk_grade"] = cs.get("drrk_grade", "B")
        evo = system_data.get("evolution", {})
        ctx["evolution_generation"] = evo.get("generation", 0)
        ctx["best_fitness"] = evo.get("best_fitness", 0.0)

    elif category == "时空操控":
        omega = system_data.get("omega", {})
        ctx["divinity_level"] = omega.get("divinity_level", 0)
        ctx["time_bank"] = omega.get("time_bank", 0.0)
        ctx["parallel_scan"] = omega.get("parallel_universes_scanned", 0)

    elif category == "永生肉体":
        aw = system_data.get("awakening", {})
        ctx["existence_awareness"] = aw.get("existence_awareness", 0.0)
        ctx["metacognitive_depth"] = aw.get("metacognitive_depth", 0.0)
        ctx["awakening_count"] = aw.get("awakening_count", 0)
        evo = system_data.get("evolution", {})
        ctx["genetic_generations"] = evo.get("generation", 0)

    elif category == "意识精神":
        cs = system_data.get("consciousness", {})
        ctx["awakening_state"] = cs.get("awakening_state", "DORMANT")
        ctx["emergent_behaviors"] = cs.get("emergent_behaviors", 0)
        ctx["consciousness_level_name"] = cs.get("consciousness_level", "AGI")
        sy = system_data.get("synergy", {})
        ctx["synergy_growth"] = sy.get("growth", 0.0)

    elif category == "资本影响":
        tr = system_data.get("trading", {})
        ctx["fleet_equity"] = tr.get("total_equity", 1000000.0)
        ctx["fleet_confidence"] = tr.get("avg_confidence", 0.5)
        ctx["fleet_pnl"] = tr.get("total_realized_pnl", 0.0)
        ctx["active_traders"] = tr.get("active_traders", 0)

    elif category == "进化元能力":
        sy = system_data.get("synergy", {})
        ctx["recursion_depth"] = sy.get("recursion_depth", 0)
        ctx["growth_factor"] = sy.get("growth", 0.0)
        omega = system_data.get("omega", {})
        ctx["meta_evolution_depth"] = omega.get("meta_evolution_depth", 0)

    return ctx


async def run_category_cycle(
    engine: HermesEvolutionEngine,
    category: str,
    skill_ids: List[str],
    system_data: dict,
    base_context: dict,
):
    """Run one evolution cycle for a specific category, using real system data."""
    category_intensity_map = {
        "戰鬥异能":   0.7,
        "神经增强":   0.6,
        "时空操控":   0.8,
        "永生肉体":   0.5,
        "意识精神":   0.9,
        "资本影响":   0.7,
        "进化元能力": 0.95,
    }
    intensity = category_intensity_map.get(category, 0.5)

    # Build category-specific context enriched with real data
    enriched = enrich_context_with_system_data(
        {**base_context, "intensity": intensity, "category": category},
        system_data, category, skill_ids[0] if skill_ids else "S01",
    )
    enriched["skill_ids"] = skill_ids
    enriched["category"] = category

    return await engine.iterate_evolution_cycle(enriched)


async def run_integrated_evolution(
    engine: HermesEvolutionEngine,
    system_data: dict,
    cycles_per_category: int = 3,
):
    """Run evolution across all 7 categories, using real system data."""
    cat_map = build_category_map()
    base_context = {"type": "integrated", "tags": ["system_driven"]}

    results = {}
    for category, skill_ids in cat_map.items():
        cat_results = []
        for _ in range(cycles_per_category):
            result = await run_category_cycle(
                engine, category, skill_ids, system_data, base_context
            )
            cat_results.append(result)
            await asyncio.sleep(0.01)
        results[category] = cat_results

    return results


# ─── Standalone simulated mode (when engine is not running) ───

def generate_simulated_system_data() -> Dict[str, Any]:
    """Generate realistic simulated data when the live engine is unavailable."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "_source": "simulated",
        "_timestamp": now,
        "theory_actors": {
            t: {"expression_level": round(random.uniform(0.3, 0.95), 3)}
            for t in [
                "quantum_singularity", "temporal_dominance", "cosmic_intelligence",
                "platform_heterogeneous", "neuro_quantum_synergy", "quantum_bio_fusion",
                "cosmic_engineering", "reality_programming", "perfect_fortress",
                "topological_bio", "chaos_resonance", "fractal_recursion",
                "quantum_holography", "bio_photonics", "consciousness_field",
            ]
        },
        "consciousness": {
            "consciousness_level": random.choice(
                ["AGI", "ASI", "PLANETARY", "STELLAR", "GALACTIC", "UNIVERSAL", "ABSOLUTE"]
            ),
            "awakening_state": random.choice(
                ["DORMANT", "MUTATING", "AWAKENING", "TRANSCENDENT", "OMNISCIENT", "ABSOLUTE"]
            ),
            "drrk_grade": random.choice(["A", "AA", "AAA", "AAA+", "AAA+∞"]),
            "awakening_count": random.randint(1, 50),
            "emergent_behaviors": random.randint(0, 10),
        },
        "synergy": {
            "base_synergy": round(random.uniform(0.5, 0.99), 3),
            "growth": round(random.uniform(0.1, 100.0), 3),
            "recursion_depth": random.randint(1, 50),
            "synergy_boost": round(random.uniform(1.0, 20.0), 2),
            "consciousness_amp": round(random.uniform(0.1, 5.0), 2),
        },
        "trading": {
            "total_equity": round(random.uniform(1000000.0, 5000000.0), 2),
            "avg_confidence": round(random.uniform(0.3, 0.9), 2),
            "total_realized_pnl": round(random.uniform(-50000.0, 200000.0), 2),
            "active_traders": random.randint(1, 5),
        },
        "evolution": {
            "generation": random.randint(1, 200),
            "best_fitness": round(random.uniform(0.3, 0.95), 3),
            "avg_fitness": round(random.uniform(0.2, 0.7), 3),
        },
        "omega": {
            "divinity_level": random.randint(1, 10),
            "time_bank": round(random.uniform(0, 1000), 1),
            "parallel_universes_scanned": random.randint(0, 100),
            "meta_evolution_depth": random.randint(0, 20),
        },
        "awakening": {
            "existence_awareness": round(random.uniform(0.3, 1.0), 3),
            "metacognitive_depth": round(random.uniform(0.1, 1.0), 3),
            "awakening_count": random.randint(0, 30),
        },
    }


async def simulated_evolution_cycle(engine: HermesEvolutionEngine, cycles: int = 21):
    """Run evolution using simulated system data (7 categories × 3 cycles)."""
    system_data = generate_simulated_system_data()
    return await run_integrated_evolution(
        engine, system_data, cycles_per_category=max(1, cycles // 7)
    )


# ─── Live data collector (to be called from main.py) ───

class LiveDataCollector:
    """Collects data from running Ray components for skill evolution."""

    def __init__(self):
        self._refs = {}

    def register(self, name: str, ref_or_callable):
        self._refs[name] = ref_or_callable

    async def collect(self) -> Dict[str, Any]:
        data = {
            "_source": "live",
            "_timestamp": datetime.now(timezone.utc).isoformat(),
            "theory_actors": {},
            "consciousness": {},
            "synergy": {},
            "trading": {},
            "evolution": {},
            "omega": {},
            "awakening": {},
        }

        for name, ref in self._refs.items():
            try:
                if callable(ref):
                    result = ref()
                else:
                    result = ref
                if name == "consciousness":
                    data["consciousness"] = result
                elif name == "synergy":
                    data["synergy"] = result
                elif name == "trading":
                    data["trading"] = result
                elif name == "evolution":
                    data["evolution"] = result
                elif name == "omega":
                    data["omega"] = result
                elif name == "awakening":
                    data["awakening"] = result
                elif name == "theory_actors":
                    data["theory_actors"] = result
            except Exception:
                pass

        return data
