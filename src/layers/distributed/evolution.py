"""DNA 並行演化引擎"""

import ray
import numpy as np
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


@ray.remote
class DNAEvolutionPool:
    def __init__(self, evolution_cfg: dict):
        from src.evolutionary_trading.dna_evolution import IntelligenceDNA, Gene
        self.cfg = evolution_cfg
        self.pool: List[Any] = []
        self.generation = 0
        for _ in range(evolution_cfg.get("pool_size", 50)):
            dna = IntelligenceDNA()
            dna.genome = {
                "entry_sensitivity": Gene("float", np.random.uniform(0.1, 2.0), clamp_min=0.01, clamp_max=5.0),
                "stop_loss_atr": Gene("float", np.random.uniform(1.0, 4.0), clamp_min=0.5, clamp_max=10.0),
                "take_profit_rr": Gene("float", np.random.uniform(1.5, 5.0), clamp_min=1.0, clamp_max=10.0),
                "position_size_pct": Gene("float", np.random.uniform(0.01, 0.25), clamp_min=0.001, clamp_max=0.5),
                "confidence_threshold": Gene("float", np.random.uniform(0.3, 0.8), clamp_min=0.1, clamp_max=0.99),
                "ma_short_window": Gene("int", np.random.randint(3, 15), clamp_min=2, clamp_max=50),
                "ma_long_window": Gene("int", np.random.randint(15, 50), clamp_min=5, clamp_max=200),
                "use_trailing_stop": Gene("bool", np.random.rand() > 0.5),
            }
            self.pool.append(dna)
        logger.info(f"  🧬 DNA pool: {len(self.pool)} genomes")

    def evolve(self, fitness: list) -> dict:
        for i, f in enumerate(fitness):
            if i < len(self.pool):
                self.pool[i].fitness = f
        self.pool.sort(key=lambda d: d.fitness, reverse=True)
        n = len(self.pool)
        elites = self.pool[:max(2, int(n * self.cfg.get("elite_ratio", 0.1)))]
        next_gen = list(elites)
        while len(next_gen) < n:
            p1, p2 = np.random.choice(elites), np.random.choice(self.pool[:n // 2])
            c1, c2 = p1.crossover(p2, self.cfg.get("crossover_rate", 0.7))
            next_gen.extend([c1.replicate(self.cfg.get("mutation_rate", 0.08)),
                             c2.replicate(self.cfg.get("mutation_rate", 0.08))])
        self.pool = next_gen[:n]
        self.generation += 1
        return {
            "generation": self.generation,
            "best_fitness": float(self.pool[0].fitness),
            "avg_fitness": float(np.mean([d.fitness for d in self.pool])),
            "elite_count": len(elites),
        }

    def best_genome(self) -> dict:
        return self.pool[0].snapshot() if self.pool else {}

    def get_status(self) -> dict:
        return {"pool_size": len(self.pool), "generation": self.generation,
                "best_fitness": float(self.pool[0].fitness) if self.pool else 0}


class EvolutionEngine:
    def __init__(self, config: dict):
        self.config = config
        self.pool: Any = None

    def deploy(self):
        cfg = self.config.get("evolution", {})
        if cfg.get("pool_size", 0) <= 0:
            return None
        self.pool = DNAEvolutionPool.remote(cfg)
        return self.pool

    def run_generation(self) -> dict:
        if not self.pool:
            return {"error": "no pool"}
        status = ray.get(self.pool.get_status.remote(), timeout=10)
        fitness = np.random.uniform(0.1, 0.9, status.get("pool_size", 50)).tolist()
        result = ray.get(self.pool.evolve.remote(fitness), timeout=30)
        best = ray.get(self.pool.best_genome.remote(), timeout=10)
        logger.info(f"  🧬 generation {result['generation']}: best={result['best_fitness']:.4f}")
        return {**result, "best_genome": best}
