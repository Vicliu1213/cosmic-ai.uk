#!/usr/bin/env python3
"""
混合量子增強算法 - Hybrid Quantum Enhanced Algorithm

融合經典和量子計算框架的混合優化系統：
- 古典層：參數優化、控制邏輯
- 量子層：量子啟發式演化
- 混合層：量子-古典反饋迴路

應用於交易系統的策略優化、風險控制等領域。
"""

import asyncio
import json
import logging
import random
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Tuple, Optional, Callable
from datetime import datetime
from enum import Enum

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuantumState(Enum):
    """量子態枚舉"""
    SUPERPOSITION = "superposition"  # 疊加態
    ENTANGLED = "entangled"          # 糾纏態
    COLLAPSED = "collapsed"           # 坍縮態
    COHERENT = "coherent"            # 相幹態


@dataclass
class QuantumBit:
    """量子比特 - 代表一個可能的解決方案狀態"""
    state: QuantumState = QuantumState.SUPERPOSITION
    amplitude: complex = 1.0 + 0j  # 複數振幅
    phase: float = 0.0              # 量子相位
    entanglement_degree: float = 0.0 # 糾纏程度 (0-1)
    
    def collapse(self, measurement_basis: str = "computational") -> float:
        """量子態坍縮 - 測量得到經典結果"""
        self.state = QuantumState.COLLAPSED
        # 計算坍縮概率
        probability = abs(self.amplitude) ** 2
        return probability
    
    def apply_quantum_gate(self, gate_type: str) -> None:
        """應用量子邏輯門"""
        if gate_type == "hadamard":
            # Hadamard 門 - 產生疊加態
            self.amplitude = (1 + 1j) / math.sqrt(2)
            self.state = QuantumState.SUPERPOSITION
        elif gate_type == "pauli_x":
            # Pauli-X 門 - 翻轉
            self.amplitude *= -1
        elif gate_type == "pauli_z":
            # Pauli-Z 門 - 相位翻轉
            self.phase += math.pi
        elif gate_type == "phase_shift":
            # 相位移動
            self.amplitude *= math.exp(1j * self.phase)


@dataclass
class HybridQuantumState:
    """混合量子系統狀態"""
    qubits: List[QuantumBit]
    classical_parameters: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    energy_level: float = 0.0  # 系統能級
    fidelity: float = 1.0      # 量子保真度 (0-1)
    
    def get_state_vector(self) -> List[complex]:
        """獲取完整的量子態向量"""
        return [qubit.amplitude for qubit in self.qubits]
    
    def calculate_entanglement_entropy(self) -> float:
        """計算糾纏熵"""
        probabilities = [abs(qubit.amplitude) ** 2 for qubit in self.qubits]
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy


class HybridQuantumEnhancedAlgorithm:
    """
    混合量子增強算法 - 融合量子計算和經典優化的混合系統
    
    用於複雜優化問題，特別是在交易系統中的應用：
    - 策略參數優化
    - 組合優化
    - 特徵選擇
    - 風險調整
    """
    
    def __init__(self, 
                 num_qubits: int = 8,
                 population_size: int = 100,
                 generations: int = 50,
                 mutation_rate: float = 0.1,
                 entanglement_strength: float = 0.8):
        """
        初始化混合量子增強算法
        
        Args:
            num_qubits: 量子比特數量
            population_size: 種群大小
            generations: 演化代數
            mutation_rate: 突變率
            entanglement_strength: 糾纏強度
        """
        self.num_qubits = num_qubits
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.entanglement_strength = entanglement_strength
        
        self.population: List[HybridQuantumState] = []
        self.best_solution: Optional[HybridQuantumState] = None
        self.fitness_history: List[float] = []
        self.generation_count = 0
        
        logger.info(f"✅ 混合量子增強算法已初始化")
        logger.info(f"   量子比特: {num_qubits}")
        logger.info(f"   種群大小: {population_size}")
        logger.info(f"   演化代數: {generations}")
    
    def initialize_population(self) -> None:
        """初始化量子種群"""
        self.population = []
        
        for i in range(self.population_size):
            # 創建量子比特
            qubits = []
            for j in range(self.num_qubits):
                qubit = QuantumBit(
                    amplitude=complex(random.gauss(0.5, 0.1), random.gauss(0.5, 0.1)),
                    entanglement_degree=random.random() * self.entanglement_strength
                )
                # 歸一化振幅
                magnitude = abs(qubit.amplitude)
                if magnitude > 0:
                    qubit.amplitude /= magnitude
                qubits.append(qubit)
            
            # 創建古典參數
            classical_params = {
                f"param_{k}": random.uniform(0, 1)
                for k in range(5)  # 5 個古典參數
            }
            
            state = HybridQuantumState(
                qubits=qubits,
                classical_parameters=classical_params,
                fidelity=random.uniform(0.8, 1.0)
            )
            self.population.append(state)
        
        logger.info(f"✅ 種群已初始化，共 {len(self.population)} 個個體")
    
    def apply_quantum_transformations(self, state: HybridQuantumState) -> None:
        """應用量子變換"""
        gates = ["hadamard", "pauli_x", "pauli_z", "phase_shift"]
        
        for qubit in state.qubits:
            if random.random() < 0.3:  # 30% 的概率應用門
                gate = random.choice(gates)
                qubit.apply_quantum_gate(gate)
    
    def evaluate_fitness(self, state: HybridQuantumState, 
                        fitness_function: Optional[Callable] = None) -> float:
        """
        評估個體適應度
        
        Args:
            state: 混合量子狀態
            fitness_function: 自定義適應度函數
            
        Returns:
            適應度值 (0-1)
        """
        if fitness_function:
            return fitness_function(state)
        
        # 默認適應度計算：結合量子保真度和古典參數質量
        # 量子部分：基於狀態的糾纏和保真度
        quantum_fitness = state.fidelity * (1 - state.calculate_entanglement_entropy() / self.num_qubits)
        
        # 古典部分：基於參數的多樣性和收斂性
        param_values = list(state.classical_parameters.values())
        param_variance = max(0.1, sum((p - 0.5) ** 2 for p in param_values) / len(param_values))
        classical_fitness = 1.0 / (1.0 + param_variance)
        
        # 結合評分
        total_fitness = 0.6 * quantum_fitness + 0.4 * classical_fitness
        return max(0.0, min(1.0, total_fitness))
    
    def selection(self) -> List[HybridQuantumState]:
        """選擇最優個體進行繁殖"""
        # 計算每個個體的適應度
        fitnesses = [self.evaluate_fitness(individual) for individual in self.population]
        
        # 基於適應度的輪盤賭選擇
        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            return random.sample(self.population, self.population_size // 2)
        
        selected = []
        for _ in range(self.population_size // 2):
            pick = random.uniform(0, total_fitness)
            current = 0
            for individual, fitness in zip(self.population, fitnesses):
                current += fitness
                if current > pick:
                    selected.append(individual)
                    break
        
        return selected
    
    def crossover(self, parent1: HybridQuantumState, 
                 parent2: HybridQuantumState) -> HybridQuantumState:
        """
        量子交叉 - 糾纏態下的重組
        """
        # 量子部分：重組量子比特
        new_qubits = []
        for i in range(self.num_qubits):
            if random.random() < 0.5:
                new_qubits.append(parent1.qubits[i])
            else:
                new_qubits.append(parent2.qubits[i])
        
        # 古典部分：重組參數
        new_params = {}
        for key in parent1.classical_parameters:
            if random.random() < 0.5:
                new_params[key] = parent1.classical_parameters[key]
            else:
                new_params[key] = parent2.classical_parameters[key]
        
        # 平均保真度
        new_fidelity = (parent1.fidelity + parent2.fidelity) / 2
        
        return HybridQuantumState(
            qubits=new_qubits,
            classical_parameters=new_params,
            fidelity=new_fidelity
        )
    
    def mutation(self, state: HybridQuantumState) -> HybridQuantumState:
        """應用突變"""
        # 量子突變：應用隨機量子門
        if random.random() < self.mutation_rate:
            self.apply_quantum_transformations(state)
        
        # 古典突變：調整參數
        if random.random() < self.mutation_rate:
            param_to_mutate = random.choice(list(state.classical_parameters.keys()))
            delta = random.gauss(0, 0.1)
            state.classical_parameters[param_to_mutate] = max(
                0.0, min(1.0, state.classical_parameters[param_to_mutate] + delta)
            )
        
        return state
    
    def evolve(self, fitness_function: Optional[Callable] = None, 
               verbose: bool = True) -> Dict[str, Any]:
        """
        執行混合量子演化算法
        
        Args:
            fitness_function: 自定義適應度函數
            verbose: 是否輸出詳細信息
            
        Returns:
            演化結果字典
        """
        logger.info("🚀 開始混合量子演化...")
        
        # 初始化種群
        self.initialize_population()
        
        # 演化循環
        for gen in range(self.generations):
            # 評估適應度
            fitnesses = [self.evaluate_fitness(ind, fitness_function) for ind in self.population]
            
            # 跟蹤最佳適應度
            max_fitness = max(fitnesses)
            self.fitness_history.append(max_fitness)
            best_idx = fitnesses.index(max_fitness)
            
            if self.best_solution is None or max_fitness > self.evaluate_fitness(self.best_solution):
                self.best_solution = self.population[best_idx]
            
            if verbose and gen % 10 == 0:
                logger.info(f"   代 {gen}: 最佳適應度 = {max_fitness:.4f}")
            
            # 選擇、交叉、突變
            selected = self.selection()
            new_population = []
            
            for i in range(0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
                
                child = self.crossover(parent1, parent2)
                child = self.mutation(child)
                new_population.append(child)
            
            # 保留最佳個體（精英主義）
            self.population = sorted(
                self.population + new_population,
                key=lambda x: self.evaluate_fitness(x),
                reverse=True
            )[:self.population_size]
            
            self.generation_count = gen + 1
        
        logger.info(f"✅ 演化完成，共 {self.generation_count} 代")
        
        return {
            'best_solution': self.best_solution,
            'best_fitness': self.evaluate_fitness(self.best_solution) if self.best_solution else 0,
            'fitness_history': self.fitness_history,
            'generations': self.generation_count,
            'population_size': len(self.population)
        }
    
    async def evolve_async(self, fitness_function: Optional[Callable] = None) -> Dict[str, Any]:
        """非同步演化"""
        return await asyncio.to_thread(self.evolve, fitness_function)
    
    def get_best_solution(self) -> Optional[HybridQuantumState]:
        """獲取最佳解"""
        return self.best_solution
    
    def get_status(self) -> Dict[str, Any]:
        """獲取算法狀態"""
        return {
            'initialized': len(self.population) > 0,
            'generation': self.generation_count,
            'population_size': len(self.population),
            'num_qubits': self.num_qubits,
            'best_fitness': self.evaluate_fitness(self.best_solution) if self.best_solution else 0,
            'fitness_history_length': len(self.fitness_history),
            'average_fitness': sum(self.fitness_history) / len(self.fitness_history) if self.fitness_history else 0
        }


def main():
    """主函數 - 演示混合量子增強算法"""
    
    print("\n" + "="*70)
    print("🌌 混合量子增強算法演示")
    print("="*70)
    
    # 創建算法實例
    algorithm = HybridQuantumEnhancedAlgorithm(
        num_qubits=8,
        population_size=50,
        generations=20,
        mutation_rate=0.15,
        entanglement_strength=0.8
    )
    
    # 定義簡單的適應度函數
    def simple_fitness(state: HybridQuantumState) -> float:
        """簡單的適應度函數 - 獎勵參數靠近最優點"""
        # 目標：所有參數都接近 0.7
        target = 0.7
        penalties = sum((p - target) ** 2 for p in state.classical_parameters.values())
        return 1.0 / (1.0 + penalties)
    
    # 執行演化
    result = algorithm.evolve(fitness_function=simple_fitness, verbose=True)
    
    print("\n📊 演化結果:")
    print(f"  最佳適應度: {result['best_fitness']:.4f}")
    print(f"  演化代數: {result['generations']}")
    print(f"  種群大小: {result['population_size']}")
    
    print("\n🎯 最佳解的古典參數:")
    if result['best_solution']:
        for name, value in result['best_solution'].classical_parameters.items():
            print(f"  {name}: {value:.4f}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
