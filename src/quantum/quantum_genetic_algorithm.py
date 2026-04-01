#!/usr/bin/env python3
"""
OpenCode 量子啟發式遺傳算法配置優化引擎
融合量子邏輯和經典遺傳算法，實現配置的自進化

量子概念應用：
- 疊加態：配置的多個可能性同時存在
- 糾纏：代理、模型、工具間的相互影響
- 測量坍縮：性能評估選擇最佳配置
"""

import json
import random
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path
import statistics
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ConfigGene:
    """配置基因 - 代表一個可調整的配置參數"""
    name: str  # 例：'temperature', 'max_steps', 'agent_type'
    value: Any  # 當前值
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    alleles: Optional[List[Any]] = None  # 離散值選項
    
    def mutate(self) -> 'ConfigGene':
        """基因突變"""
        if self.alleles:  # 離散值
            return ConfigGene(
                name=self.name,
                value=random.choice(self.alleles),
                min_value=self.min_value,
                max_value=self.max_value,
                alleles=self.alleles
            )
        elif self.min_value is not None and self.max_value is not None:
            # 連續值 - 高斯突變
            delta = (self.max_value - self.min_value) * random.gauss(0, 0.1)
            new_value = self.value + delta
            new_value = max(self.min_value, min(self.max_value, new_value))
            
            return ConfigGene(
                name=self.name,
                value=new_value,
                min_value=self.min_value,
                max_value=self.max_value,
                alleles=self.alleles
            )
        return self


@dataclass
class Chromosome:
    """染色體 - 代表完整的配置組合"""
    genes: List[ConfigGene]
    fitness: float = 0.0  # 適應度（品質得分）
    age: int = 0  # 世代年齡
    quantum_amplitude: float = 1.0  # 量子振幅（用於概率加權）
    
    def to_config_dict(self) -> Dict[str, Any]:
        """轉換為 OpenCode 配置格式"""
        config = {}
        for gene in self.genes:
            config[gene.name] = gene.value
        return config
    
    def crossover(self, other: 'Chromosome') -> Tuple['Chromosome', 'Chromosome']:
        """交叉 - 量子糾纏：兩個配置融合產生後代"""
        # 單點交叉
        crossover_point = random.randint(1, len(self.genes) - 1)
        
        offspring1_genes = self.genes[:crossover_point] + other.genes[crossover_point:]
        offspring2_genes = other.genes[:crossover_point] + self.genes[crossover_point:]
        
        offspring1 = Chromosome(genes=offspring1_genes, age=0)
        offspring2 = Chromosome(genes=offspring2_genes, age=0)
        
        return offspring1, offspring2
    
    def mutate(self, mutation_rate: float = 0.1):
        """突變 - 隨機改變基因"""
        for i, gene in enumerate(self.genes):
            if random.random() < mutation_rate:
                self.genes[i] = gene.mutate()
    
    def calculate_quantum_amplitude(self, best_fitness: float):
        """計算量子振幅 - 作用於選擇概率"""
        if best_fitness == 0:
            self.quantum_amplitude = 1.0
        else:
            # 適應度越高，振幅越大
            self.quantum_amplitude = math.sqrt(self.fitness / best_fitness)


class QuantumGeneticAlgorithm:
    """量子啟發式遺傳算法"""
    
    def __init__(self, population_size: int = 20, generations: int = 50):
        self.population_size = population_size
        self.generations = generations
        self.current_generation = 0
        self.population: List[Chromosome] = []
        self.best_chromosome: Optional[Chromosome] = None
        self.fitness_history: List[float] = []
        self.config_dir = Path("~/.config/opencode").expanduser()
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_population(self):
        """初始化種群 - 量子疊加態"""
        logger.info("🌌 初始化量子種群（疊加態）...")
        
        for _ in range(self.population_size):
            genes = self._create_random_genes()
            chromosome = Chromosome(genes=genes, age=0)
            self.population.append(chromosome)
        
        logger.info(f"✓ 種群大小: {self.population_size} 個染色體")
    
    def _create_random_genes(self) -> List[ConfigGene]:
        """創建隨機基因組合"""
        genes = [
            ConfigGene(
                name="temperature",
                value=random.uniform(0.0, 1.0),
                min_value=0.0,
                max_value=1.0
            ),
            ConfigGene(
                name="max_steps",
                value=random.randint(5, 20),
                min_value=5,
                max_value=20
            ),
            ConfigGene(
                name="agent_type",
                value=random.choice(["build", "plan", "general", "explore"]),
                alleles=["build", "plan", "general", "explore"]
            ),
            ConfigGene(
                name="model_size",
                value=random.choice(["fast", "balanced", "powerful"]),
                alleles=["fast", "balanced", "powerful"]
            ),
            ConfigGene(
                name="scroll_acceleration",
                value=random.choice([True, False]),
                alleles=[True, False]
            ),
            ConfigGene(
                name="auto_save_interval",
                value=random.randint(30, 300),
                min_value=30,
                max_value=300
            ),
        ]
        return genes
    
    def evaluate_fitness(self, chromosome: Chromosome, 
                        task_history: List[Dict[str, Any]]) -> float:
        """評估染色體的適應度 - 測量坍縮"""
        if not task_history:
            return 50.0  # 默認分數
        
        config = chromosome.to_config_dict()
        total_score = 0
        matching_tasks = 0
        
        for task in task_history:
            # 檢查配置是否匹配任務
            agent_match = config["agent_type"] == task.get("best_agent", config["agent_type"])
            
            # 計算相似度
            similarity = 0.0
            
            # 代理匹配權重：40%
            if agent_match:
                similarity += 40
            
            # 溫度匹配權重：30%
            temp_diff = abs(config["temperature"] - task.get("avg_temperature", 0.5))
            similarity += max(0, 30 - (temp_diff * 30))
            
            # 效率權重：30%
            if config["max_steps"] <= task.get("optimal_steps", 10):
                similarity += 30
            else:
                similarity += max(0, 30 - ((config["max_steps"] - task.get("optimal_steps", 10)) * 2))
            
            total_score += similarity
            matching_tasks += 1
        
        fitness = total_score / matching_tasks if matching_tasks > 0 else 50.0
        chromosome.fitness = fitness
        
        return fitness
    
    def selection(self) -> List[Chromosome]:
        """選擇 - 量子測量：機率與振幅相關"""
        # 計算最大適應度
        best_fitness = max(c.fitness for c in self.population)
        
        # 計算所有染色體的量子振幅
        for chromosome in self.population:
            chromosome.calculate_quantum_amplitude(best_fitness)
        
        # 基於量子振幅的加權選擇
        total_amplitude = sum(c.quantum_amplitude for c in self.population)
        
        selected = []
        for _ in range(len(self.population)):
            # 輪盤賭選擇
            r = random.uniform(0, total_amplitude)
            cumsum = 0
            
            for chromosome in self.population:
                cumsum += chromosome.quantum_amplitude
                if cumsum >= r:
                    selected.append(chromosome)
                    break
        
        return selected
    
    def evolve_generation(self, task_history: List[Dict[str, Any]]) -> Chromosome:
        """進化一代 - 遺傳操作循環"""
        self.current_generation += 1
        logger.info(f"\n🧬 第 {self.current_generation} 代進化...")
        
        # 評估適應度
        for chromosome in self.population:
            self.evaluate_fitness(chromosome, task_history)
        
        # 找到最佳個體
        best = max(self.population, key=lambda c: c.fitness)
        
        if self.best_chromosome is None or best.fitness > self.best_chromosome.fitness:
            self.best_chromosome = Chromosome(genes=best.genes, fitness=best.fitness)
            logger.info(f"✨ 發現新最佳適應度: {best.fitness:.2f}")
        
        self.fitness_history.append(best.fitness)
        
        # 選擇
        selected = self.selection()
        
        # 創建新種群
        new_population = []
        
        # 精英保留（保留最佳個體）
        elite_size = max(1, self.population_size // 10)
        elite = sorted(self.population, key=lambda c: c.fitness, reverse=True)[:elite_size]
        new_population.extend(elite)
        
        # 交叉和突變
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(selected, 2)
            offspring1, offspring2 = parent1.crossover(parent2)
            
            # 應用突變
            mutation_rate = 0.1 + (0.1 * (50 - self.current_generation) / 50)  # 早期更激進
            offspring1.mutate(mutation_rate)
            offspring2.mutate(mutation_rate)
            
            new_population.extend([offspring1, offspring2])
        
        self.population = new_population[:self.population_size]
        
        # 增加年齡
        for chromosome in self.population:
            chromosome.age += 1
        
        avg_fitness = statistics.mean(c.fitness for c in self.population)
        logger.info(f"  平均適應度: {avg_fitness:.2f}")
        
        return self.best_chromosome
    
    def optimize(self, task_history: List[Dict[str, Any]]) -> Optional[Chromosome]:
        """執行完整的進化過程"""
        logger.info("🚀 開始量子遺傳演化...")
        logger.info(f"   種群大小: {self.population_size}")
        logger.info(f"   目標代數: {self.generations}\n")
        
        self.initialize_population()
        
        best = None
        for gen in range(self.generations):
            best = self.evolve_generation(task_history)
        
        if best is None:
            logger.error("❌ 進化失敗：未找到最佳染色體")
            return None
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 進化完成！")
        logger.info(f"   最終最佳適應度: {best.fitness:.2f}")
        logger.info(f"   進化世代: {self.current_generation}")
        logger.info("=" * 60 + "\n")
        
        return best
    
    def export_best_config(self) -> Dict[str, Any]:
        """導出最優配置"""
        if self.best_chromosome is None:
            logger.warning("⚠️  未找到最佳染色體")
            return {}
        
        config = self.best_chromosome.to_config_dict()
        best_fitness = self.best_chromosome.fitness
        
        return {
            "model": "anthropic/claude-haiku-4-20250514",
            "theme": "one-dark",
            "tui": {
                "scroll_speed": 3,
                "scroll_acceleration": {
                    "enabled": config.get("scroll_acceleration", True)
                },
                "diff_style": "auto"
            },
            "optimization": {
                "temperature": config.get("temperature", 0.3),
                "max_steps": config.get("max_steps", 10),
                "agent_type": config.get("agent_type", "build"),
                "model_size": config.get("model_size", "balanced"),
                "auto_save_interval": config.get("auto_save_interval", 60)
            },
            "genetic_algorithm": {
                "fitness": float(best_fitness),
                "generation": self.current_generation,
                "evolved_at": datetime.now().isoformat()
            }
        }
    
    def generate_report(self) -> str:
        """生成進化報告"""
        report = []
        report.append("\n" + "=" * 70)
        report.append("🧬 OpenCode 量子遺傳算法進化報告")
        report.append("=" * 70)
        
        report.append(f"\n📊 進化統計:")
        report.append(f"  • 總代數: {self.current_generation}")
        report.append(f"  • 種群大小: {self.population_size}")
        if self.best_chromosome:
            report.append(f"  • 最終最佳適應度: {self.best_chromosome.fitness:.2f}/100")
        else:
            report.append(f"  • 最終最佳適應度: N/A")
        
        if len(self.fitness_history) > 1:
            improvement = self.fitness_history[-1] - self.fitness_history[0]
            report.append(f"  • 適應度改善: {improvement:+.2f}")
            report.append(f"  • 平均進步: {improvement / len(self.fitness_history):.4f}/代")
        
        if self.best_chromosome:
            report.append(f"\n🎯 最優配置:")
            for gene in self.best_chromosome.genes:
                report.append(f"  • {gene.name}: {gene.value}")
        
        report.append(f"\n📈 適應度演變:")
        for i, fitness in enumerate(self.fitness_history[-10:], 
                                    start=max(1, len(self.fitness_history) - 9)):
            bar_length = int(fitness / 10)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            report.append(f"  [{i:2d}] {bar} {fitness:.1f}")
        
        report.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(report)


def main():
    """示例執行"""
    # 模擬任務歷史
    task_history = [
        {
            "task_type": "code_generation",
            "best_agent": "build",
            "avg_temperature": 0.3,
            "optimal_steps": 8,
            "success_rate": 0.95
        },
        {
            "task_type": "analysis",
            "best_agent": "plan",
            "avg_temperature": 0.1,
            "optimal_steps": 5,
            "success_rate": 0.98
        },
        {
            "task_type": "debug",
            "best_agent": "explore",
            "avg_temperature": 0.2,
            "optimal_steps": 6,
            "success_rate": 0.92
        },
        {
            "task_type": "refactor",
            "best_agent": "build",
            "avg_temperature": 0.4,
            "optimal_steps": 10,
            "success_rate": 0.90
        },
    ]
    
    # 執行遺傳算法
    ga = QuantumGeneticAlgorithm(population_size=20, generations=30)
    best = ga.optimize(task_history)
    
    # 輸出報告
    print(ga.generate_report())
    
    # 導出最優配置
    print("\n💾 最優配置 (JSON 格式):")
    best_config = ga.export_best_config()
    print(json.dumps(best_config, indent=2, ensure_ascii=False))
    
    # 保存配置
    config_file = Path("~/.config/opencode/evolved_config.json").expanduser()
    with open(config_file, 'w') as f:
        json.dump(best_config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ 配置已保存到: {config_file}")


if __name__ == "__main__":
    main()
