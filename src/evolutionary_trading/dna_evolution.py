#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dna_evolution.py — 金融大鰐 神絕對超越完全體
IntelligenceDNA 進化基因引擎 v2
支援：浮點/整數/布林/字串基因、自適應突變率、Pareto 適應度記錄
"""
from __future__ import annotations
import numpy as np
import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class GeneType(str, Enum):
    FLOAT = "float"
    INT   = "int"
    BOOL  = "bool"
    STR   = "str"


@dataclass
class Gene:
    """單一基因：帶自適應突變率"""
    gene_type: str       = GeneType.FLOAT
    allele_value: Any    = 0.0
    mutation_rate: float = 0.08
    mutation_range: float = 0.15
    clamp_min: Optional[float] = None
    clamp_max: Optional[float] = None

    def mutate(self, strength: float = 1.0) -> Gene:
        new = copy.copy(self)
        effective_rate = min(0.9, self.mutation_rate * strength)
        if np.random.rand() < effective_rate:
            if self.gene_type in (GeneType.FLOAT, "float"):
                delta = np.random.randn() * self.mutation_range * strength
                v = self.allele_value + delta
                if self.clamp_min is not None:
                    v = max(self.clamp_min, v)
                if self.clamp_max is not None:
                    v = min(self.clamp_max, v)
                new.allele_value = float(v)
            elif self.gene_type in (GeneType.INT, "int"):
                delta = int(np.round(np.random.randn() * strength))
                v = self.allele_value + delta
                if self.clamp_min is not None:
                    v = max(int(self.clamp_min), v)
                if self.clamp_max is not None:
                    v = min(int(self.clamp_max), v)
                new.allele_value = int(v)
            elif self.gene_type in (GeneType.BOOL, "bool"):
                if np.random.rand() < 0.3 * strength:
                    new.allele_value = not self.allele_value
        return new

    def get_phenotype(self) -> Any:
        return self.allele_value

    def __repr__(self) -> str:
        return f"Gene({self.gene_type}={self.allele_value:.4g})" if isinstance(self.allele_value, float) else f"Gene({self.gene_type}={self.allele_value})"


class IntelligenceDNA:
    """智能DNA v2 — 可交叉、多目標適應度、Pareto rank"""

    def __init__(self, generation: int = 0):
        self.generation = generation
        self.genome: Dict[str, Gene] = {}
        # 多目標適應度
        self.fitness: float = 0.0
        self.fitness_vec: Dict[str, float] = {}
        self.pareto_rank: int = 9999
        self.crowding_distance: float = 0.0

    # ── 表現型 ──────────────────────────────────────────
    def get_phenotype(self, context: Dict = None) -> Dict[str, Any]:
        return {k: g.get_phenotype() for k, g in self.genome.items()}

    # ── 複製（突變） ──────────────────────────────────
    def replicate(self, mutation_strength: float = 0.3) -> IntelligenceDNA:
        child = IntelligenceDNA(generation=self.generation + 1)
        child.genome = {k: g.mutate(mutation_strength) for k, g in self.genome.items()}
        return child

    # ── 交叉 ─────────────────────────────────────────
    def crossover(
        self,
        other: IntelligenceDNA,
        crossover_rate: float = 0.7,
    ) -> Tuple[IntelligenceDNA, IntelligenceDNA]:
        child1 = IntelligenceDNA(generation=self.generation + 1)
        child2 = IntelligenceDNA(generation=other.generation + 1)
        all_keys = set(self.genome) | set(other.genome)
        for key in all_keys:
            g1 = self.genome.get(key)
            g2 = other.genome.get(key)
            if g1 is None:
                child1.genome[key] = copy.deepcopy(g2)
                child2.genome[key] = copy.deepcopy(g2)
            elif g2 is None:
                child1.genome[key] = copy.deepcopy(g1)
                child2.genome[key] = copy.deepcopy(g1)
            else:
                if np.random.rand() < crossover_rate:
                    # BLX-α 混合交叉（浮點）
                    if g1.gene_type in (GeneType.FLOAT, "float"):
                        alpha = 0.3
                        lo = min(g1.allele_value, g2.allele_value)
                        hi = max(g1.allele_value, g2.allele_value)
                        spread = (hi - lo) * alpha
                        v1 = np.random.uniform(lo - spread, hi + spread)
                        v2 = np.random.uniform(lo - spread, hi + spread)
                        c1 = copy.copy(g1); c1.allele_value = float(v1)
                        c2 = copy.copy(g2); c2.allele_value = float(v2)
                        child1.genome[key] = c1
                        child2.genome[key] = c2
                    else:
                        child1.genome[key] = copy.deepcopy(g1)
                        child2.genome[key] = copy.deepcopy(g2)
                else:
                    child1.genome[key] = copy.deepcopy(g2)
                    child2.genome[key] = copy.deepcopy(g1)
        return child1, child2

    def snapshot(self) -> Dict:
        return {k: round(g.allele_value, 5) if isinstance(g.allele_value, float) else g.allele_value
                for k, g in self.genome.items()}

    def __repr__(self) -> str:
        return (f"DNA(gen={self.generation}, rank={self.pareto_rank}, "
                f"fit={self.fitness:.4f})")
