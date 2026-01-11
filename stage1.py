# stage1.py
# Stage1: 四個物理極限定義 + 增強經典算法 + 量子優勢分析 + summary 一次完成

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Tuple
from datetime import datetime

import numpy as np


# =========================
# 0. 簡易增強經典算法 (DE + random)
# =========================

def random_search(
    objective: Callable[[np.ndarray], float],
    bounds: np.ndarray,
    n_samples: int = 500,
) -> Tuple[np.ndarray, float]:
    dim = bounds.shape[0]
    best_x = None
    best_f = np.inf
    for _ in range(n_samples):
        x = np.random.uniform(bounds[:, 0], bounds[:, 1], size=dim)
        f = objective(x)
        if f < best_f:
            best_f = f
            best_x = x
    return best_x, best_f


def differential_evolution(
    objective: Callable[[np.ndarray], float],
    bounds: np.ndarray,
    pop_size: int = 20,
    n_generations: int = 50,
    F: float = 0.8,
    CR: float = 0.9,
) -> Tuple[np.ndarray, float]:
    dim = bounds.shape[0]
    pop = np.random.uniform(bounds[:, 0], bounds[:, 1], size=(pop_size, dim))
    fitness = np.array([objective(ind) for ind in pop])

    for _ in range(n_generations):
        for i in range(pop_size):
            idxs = np.random.choice(pop_size, 3, replace=False)
            a, b, c = pop[idxs]
            mutant = a + F * (b - c)
            mutant = np.clip(mutant, bounds[:, 0], bounds[:, 1])

            cross = np.random.rand(dim) < CR
            if not np.any(cross):
                cross[np.random.randint(0, dim)] = True

            trial = np.where(cross, mutant, pop[i])
            f_trial = objective(trial)
            if f_trial < fitness[i]:
                pop[i] = trial
                fitness[i] = f_trial

    best_idx = np.argmin(fitness)
    return pop[best_idx], fitness[best_idx]


# =========================
# 1. TheorySpec + 四個理論
# =========================

@dataclass
class TheorySpec:
    name: str
    key: str
    category: str
    math_model: str
    base_capability: float
    breakthrough_threshold: float
    verification_metric: str
    classical_scaling: str
    quantum_scaling: str
    notes: Optional[str] = None


STAGE1_THEORIES: Dict[str, TheorySpec] = {
    "heisenberg": TheorySpec(
        name="Heisenberg Limit",
        key="heisenberg",
        category="precision",
        math_model="Δφ ≥ 1/N",
        base_capability=1e6,
        breakthrough_threshold=1e3,
        verification_metric="precision_gain",
        classical_scaling="1/sqrt(N)",
        quantum_scaling="1/N",
        notes="超精密測量"
    ),
    "bekenstein": TheorySpec(
        name="Bekenstein Bound",
        key="bekenstein",
        category="compression",
        math_model="I_max = 2πER/(ħ c ln 2)",
        base_capability=1e8,
        breakthrough_threshold=1e3,
        verification_metric="info_density_ratio",
        classical_scaling="O(ρ_classical)",
        quantum_scaling="O(ρ_holographic)",
        notes="信息極限壓縮"
    ),
    "bremermann": TheorySpec(
        name="Bremermann Limit",
        key="bremermann",
        category="speed",
        math_model="R_max = 2E/(πħ) bits/s",
        base_capability=1e7,
        breakthrough_threshold=1e3,
        verification_metric="speedup_factor",
        classical_scaling="O(N * f_clock)",
        quantum_scaling="O(N_parallel * f_q)",
        notes="計算速度上限"
    ),
    "landauer": TheorySpec(
        name="Landauer Principle",
        key="landauer",
        category="energy",
        math_model="E_min = k_B T ln 2",
        base_capability=1e9,
        breakthrough_threshold=1e3,
        verification_metric="energy_per_bit_ratio",
        classical_scaling="E ~ k_B T ln 2",
        quantum_scaling="E -> 0 (reversible)",
        notes="能耗下限"
    ),
}


# =========================
# 2. 量子優勢結果結構
# =========================

@dataclass
class QuantumAdvantageResult:
    theory_key: str
    problem_size: int
    classical_cost: float
    quantum_cost: float
    quantum_speedup: float
    crossover_point: Optional[float]
    advantage_achieved: bool
    sizes: List[int]
    classical_costs: List[float]
    quantum_costs: List[float]
    timestamp: str


# =========================
# 3. QuantumAdvantageAnalyzer（增強經典算法版）
# =========================

class QuantumAdvantageAnalyzer:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "min_problem_size": 2**5,
            "max_problem_size": 2**15,
            "samples": 10,
            "optimizer": "DE",  # "DE" or "random"
        }

    def analyze_theory(self, theory: TheorySpec) -> QuantumAdvantageResult:
        sizes = self._gen_sizes()
        classical_costs, quantum_costs = self._estimate_costs(theory, sizes)
        crossover = self._find_crossover(sizes, classical_costs, quantum_costs)
        speedup = self._speedup(classical_costs, quantum_costs)

        advantage = (crossover is not None) and (speedup >= theory.breakthrough_threshold)

        return QuantumAdvantageResult(
            theory_key=theory.key,
            problem_size=int(sizes[-1]),
            classical_cost=float(classical_costs[-1]),
            quantum_cost=float(quantum_costs[-1]),
            quantum_speedup=float(speedup),
            crossover_point=float(crossover) if crossover is not None else None,
            advantage_achieved=advantage,
            sizes=list(map(int, sizes)),
            classical_costs=list(map(float, classical_costs)),
            quantum_costs=list(map(float, quantum_costs)),
            timestamp=datetime.utcnow().isoformat(),
        )

    def _gen_sizes(self) -> np.ndarray:
        n_min = self.config["min_problem_size"]
        n_max = self.config["max_problem_size"]
        k = self.config["samples"]
        return np.logspace(math.log10(n_min), math.log10(n_max), k, dtype=int)

    def _estimate_costs(
        self, theory: TheorySpec, sizes: np.ndarray
    ) -> (np.ndarray, np.ndarray):
        classical = []
        quantum = []
        for n in sizes:
            n = int(n)
            c = self._classical_best_cost(theory, n)
            q = self._quantum_limit_cost(theory, n)
            classical.append(c)
            quantum.append(q)
        return np.array(classical), np.array(quantum)

    def _classical_best_cost(self, theory: TheorySpec, n: int) -> float:
        # 根據 category 給不同的 toy objective，之後你可以換成真實 backtest
        if theory.category == "precision":
            def obj(x):
                c, m = x
                var_res = 1.0 / max(m, 1.0)
                compute = c ** 2 / max(n, 1)
                return var_res + compute
            bounds = np.array([[0.1, 10.0], [1.0, 1e4]])

        elif theory.category == "compression":
            def obj(x):
                r, c = x
                distortion = 1.0 / max(r, 1.0)
                compute = c ** 2 / max(n, 1)
                return distortion + compute
            bounds = np.array([[1.0, 1e6], [0.1, 10.0]])

        elif theory.category == "speed":
            def obj(x):
                p, f = x
                t_cost = n / max(p * f, 1.0)
                overhead = 0.1 * (p + f)
                return t_cost + overhead
            bounds = np.array([[1.0, 1e4], [0.1, 10.0]])

        elif theory.category == "energy":
            def obj(x):
                r, cool = x
                e_bit = 1.0 / max(r, 1.0)
                cooling = cool ** 2
                return e_bit + cooling
            bounds = np.array([[1.0, 1e6], [0.1, 10.0]])

        else:
            def obj(x):
                return float(np.sum(x ** 2))
            bounds = np.array([[0.0, 1.0]])

        if self.config.get("optimizer", "DE") == "DE":
            _, best = differential_evolution(obj, bounds)
        else:
            _, best = random_search(obj, bounds)

        return float(best)

    def _quantum_limit_cost(self, theory: TheorySpec, n: int) -> float:
        base = max(theory.base_capability, 1.0)
        n = float(n)

        if theory.category == "precision":
            return 1.0 / base * (1.0 / (n ** 2))
        elif theory.category == "compression":
            return 1.0 / base * (1.0 / (math.log2(n + 2) ** 2))
        elif theory.category == "speed":
            return 1.0 / base
        elif theory.category == "energy":
            return 1.0 / base
        else:
            return 1.0 / base

    def _find_crossover(
        self, sizes: np.ndarray, classical: np.ndarray, quantum: np.ndarray
    ) -> Optional[float]:
        diff = classical - quantum
        mask = diff > 0
        if not np.any(mask):
            return None
        idx = np.argmax(mask)
        return float(sizes[idx])

    def _speedup(self, classical: np.ndarray, quantum: np.ndarray) -> float:
        if quantum[-1] == 0:
            return float("inf")
        return float(classical[-1] / quantum[-1])


# =========================
# 4. Stage1 summary + vector
# =========================

def build_stage1_summary(results: Dict[str, QuantumAdvantageResult]) -> Dict:
    h = results["heisenberg"]
    b = results["bekenstein"]
    br = results["bremermann"]
    l = results["landauer"]

    G_h  = h.quantum_speedup
    G_b  = b.quantum_speedup
    G_br = br.quantum_speedup
    G_l  = l.quantum_speedup

    threshold_h  = STAGE1_THEORIES["heisenberg"].breakthrough_threshold
    threshold_b  = STAGE1_THEORIES["bekenstein"].breakthrough_threshold
    threshold_br = STAGE1_THEORIES["bremermann"].breakthrough_threshold
    threshold_l  = STAGE1_THEORIES["landauer"].breakthrough_threshold

    stage1_summary = {
        "heisenberg": {
            "precision_gain":   G_h,
            "breakthrough":     G_h  >= threshold_h,
        },
        "bekenstein": {
            "info_density_ratio":  G_b,
            "breakthrough":        G_b >= threshold_b,
        },
        "bremermann": {
            "speedup_factor":   G_br,
            "breakthrough":     G_br >= threshold_br,
        },
        "landauer": {
            "energy_per_bit_ratio": G_l,
            "breakthrough":         G_l >= threshold_l,
        },
        "stage1_vector": {
            "precision":   G_h,
            "compression": G_b,
            "speed":       G_br,
            "energy":      G_l,
        }
    }
    return stage1_summary


def run_stage1() -> Dict:
    """
    一行入口：跑四個理論 → 回傳 stage1_summary
    """
    analyzer = QuantumAdvantageAnalyzer()
    results: Dict[str, QuantumAdvantageResult] = {}
    for key, spec in STAGE1_THEORIES.items():
        results[key] = analyzer.analyze_theory(spec)
    summary = build_stage1_summary(results)
    return summary


if __name__ == "__main__":
    s = run_stage1()
    print("\n[Stage1 Summary]")
    for k, v in s.items():
        print(k, ":", v if k != "stage1_vector" else "vector=" + str(v))
