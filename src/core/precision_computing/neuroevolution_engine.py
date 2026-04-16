import numpy as np
import random
from typing import List, Dict, Any, Callable, Tuple
from deap import base, creator, tools, algorithms
from deap.algorithms import varAnd
import operator

class NeuroevolutionOrchestrator:
    """
    增研版：DEAP 強化遺傳演化 + 多目標 NSGA-II + 精英保留 + 自適應變異。
    專為加密量化代理演化設計，優化 Sharpe/PNL/最大回撤，生成抗震 Agent DNA。
    """
    def __init__(self, population_size=20, dna_bounds: Dict[str, Tuple[float, float]] = None):
        """
        dna_bounds: {'lr': (1e-5, 1e-2), 'momentum': (0.8, 0.99), 'layers': (2, 5), ...}
        定義代理超參空間，支援連續/離散參數 [web:1][web:5]。
        """
        self.population_size = population_size
        self.dna_bounds = dna_bounds or {
            'lr': (1e-5, 1e-2),
            'momentum': (0.85, 0.99),
            'batch_size': (16, 128),
            'dropout': (0.0, 0.5),
            'n_layers': (2, 6)  # 離散轉連續代理
        }

        # DEAP 多目標設定：最大化 Sharpe，最小化 MDD (負值最大化)
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))  # Sharpe, -MDD
        creator.create("Individual", list, fitness=creator.FitnessMulti)

        self.toolbox = base.Toolbox()
        self._setup_deap()
        self.population = self.toolbox.population(n=population_size)
        self.hall_of_fame = tools.HallOfFame(5)  # 精英庫
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("max", np.max)

    def _setup_deap(self):
        """DEAP 工具箱：自適應參數範圍 [web:2]。"""
        def init_individual():
            return creator.Individual([random.uniform(low, high) for low, high in self.dna_bounds.values()])

        self.toolbox.register("individual", init_individual)
        self.toolbox.register("population", self.toolbox.individual)

        # NSGA-II 選擇 (多目標)
        self.toolbox.register("select", tools.selNSGA2)
        self.toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=[b[0] for b in self.dna_bounds.values()],
                              up=[b[1] for b in self.dna_bounds.values()], eta=20)
        self.toolbox.register("mutate", tools.mutPolynomialBounded, low=[b[0] for b in self.dna_bounds.values()],
                              up=[b[1] for b in self.dna_bounds.values()], eta=20, indpb=0.2)
        self.toolbox.register("evaluate", self._dummy_evaluate)  # 替換為真 fitness

    def _dummy_evaluate(self, individual: List[float]) -> Tuple[float, float]:
        """佔位 fitness：Sharpe, -MaxDrawdown。替換為真回測 [web:3]。"""
        # 模擬：lr 高 -> Sharpe 高但 MDD 大
        sharpe = 1.0 + individual[0] * 10 - individual[3] * 2
        mdd = -(1.0 + individual[1] * 5 + np.random.normal(0, 0.1))
        return sharpe, mdd

    def dna_to_dict(self, dna: List[float]) -> Dict[str, float]:
        """DNA 轉代理超參字典。"""
        keys = list(self.dna_bounds.keys())
        # 離散轉整數：n_layers
        dna_dict = {k: v if k != 'n_layers' else int(round(v)) for k, v in zip(keys, dna)}
        return dna_dict

    def evolve_population(self, custom_fitness: Callable[[List[float]], Tuple[float, float]] = None,
                         generations: int = 10, cxpb: float = 0.7, mutpb: float = 0.3) -> Dict[str, Any]:
        """
        完整演化循環：NSGA-II + 精英保留 + log。
        custom_fitness: 注入 Bitget 回測 fitness (Sharpe, -MDD)。
        返回：最佳 DNA, Pareto 前沿, 演化統計 [web:4][web:6]。
        """
        if custom_fitness:
            self.toolbox.register("evaluate", custom_fitness)

        # 演化
        pop = self.toolbox.population(n=self.population_size)
        hof = tools.HallOfFame(5)

        algorithms.eaMuPlusLambda(pop, self.toolbox, mu=self.population_size, lambda_=self.population_size,
                                  cxpb=cxpb, mutpb=mutpb, ngen=generations,
                                  stats=self.stats, halloffame=hof, verbose=True)

        # 綜合最佳：Pareto 前沿中 max(Sharpe * (1 - MDD))
        def hypervolume_proxy(ind):
            s, mdd_neg = ind.fitness.values
            return s * (1 + mdd_neg)  # MDD 已負

        best_idx = max(range(len(hof)), key=lambda i: hypervolume_proxy(hof[i]))
        best_dna = self.dna_to_dict(hof[best_idx])

        print("🧬 跨代演化完成！新精英 DNA:", best_dna)
        print("🏆 Pareto 前沿 Top3:", [self.dna_to_dict(ind) for ind in hof[:3]])

        return {
            "best_dna": best_dna,
            "pareto_front": [self.dna_to_dict(ind) for ind in hof],
            "stats": self.stats.compile(pop),
            "hall_of_fame": hof
        }

# 使用範例：整合你的量子拓撲插件
# def trading_fitness(dna):
#     agent = YourAgent(**orchestrator.dna_to_dict(dna))
#     sharpe, mdd = backtest_on_bitget(agent)  # Sharpe, -MDD
#     return sharpe, mdd
#
# orch = NeuroevolutionOrchestrator(population_size=30)
# results = orch.evolve_population(custom_fitness=trading_fitness, generations=50)
# next_gen_agent = results["best_dna"]
