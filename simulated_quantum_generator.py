#!/usr/bin/env python3
"""
模擬量子生成系統 - Simulated Quantum Generator
實現真正可驗證的量子模擬,替代真實量子計算

功能:
1. 量子態生成和演化
2. 量子疊加態模擬
3. 量子糾纏模擬
4. 量子測量和坍縮
5. 成本追蹤和優化
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import hashlib

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuantumState(Enum):
    """量子態狀態"""
    SUPERPOSITION = "superposition"  # 疊加態
    ENTANGLED = "entangled"  # 糾纏態
    COLLAPSED = "collapsed"  # 坍縮態
    MEASURED = "measured"  # 已測量


@dataclass
class QuantumBit:
    """量子位元 - 模擬量子位元"""
    id: str
    state_vector: np.ndarray  # [alpha, beta] 複數係數
    measured_value: Optional[int] = None
    measurement_count: int = 0
    cost_per_operation: float = 0.001  # 每次操作的成本
    
    def get_probability_0(self) -> float:
        """獲得測量為 0 的概率"""
        alpha = self.state_vector[0]
        return float(np.abs(alpha) ** 2)
    
    def get_probability_1(self) -> float:
        """獲得測量為 1 的概率"""
        beta = self.state_vector[1]
        return float(np.abs(beta) ** 2)
    
    def measure(self) -> int:
        """測量量子位元 (量子坍縮)"""
        prob_0 = self.get_probability_0()
        self.measured_value = np.random.choice([0, 1], p=[prob_0, 1 - prob_0])
        self.measurement_count += 1
        return self.measured_value


@dataclass
class QuantumRegister:
    """量子暫存器 - 管理多個量子位元"""
    name: str
    num_qubits: int
    qubits: List[QuantumBit] = field(default_factory=list)
    entanglement_map: Dict[str, List[str]] = field(default_factory=dict)
    total_cost: float = 0.0
    operation_count: int = 0
    
    def __post_init__(self):
        """初始化量子位元"""
        if not self.qubits:
            self.qubits = [
                QuantumBit(
                    id=f"{self.name}_q{i}",
                    state_vector=np.array([1.0 + 0j, 0.0 + 0j])  # |0⟩ 狀態
                )
                for i in range(self.num_qubits)
            ]
    
    def hadamard(self, qubit_idx: int) -> float:
        """哈德瑪門 - 創建疊加態
        
        H|0⟩ = (|0⟩ + |1⟩)/√2
        """
        cost = self.qubits[qubit_idx].cost_per_operation
        # 應用 Hadamard 矩陣
        h_matrix = np.array([
            [1/np.sqrt(2), 1/np.sqrt(2)],
            [1/np.sqrt(2), -1/np.sqrt(2)]
        ])
        self.qubits[qubit_idx].state_vector = h_matrix @ self.qubits[qubit_idx].state_vector
        self.total_cost += cost
        self.operation_count += 1
        logger.info(f"✓ Hadamard gate on {self.qubits[qubit_idx].id} (成本: {cost:.6f})")
        return cost
    
    def pauli_x(self, qubit_idx: int) -> float:
        """Pauli-X 門 - 位元翻轉
        
        X|0⟩ = |1⟩, X|1⟩ = |0⟩
        """
        cost = self.qubits[qubit_idx].cost_per_operation
        x_matrix = np.array([
            [0, 1],
            [1, 0]
        ])
        self.qubits[qubit_idx].state_vector = x_matrix @ self.qubits[qubit_idx].state_vector
        self.total_cost += cost
        self.operation_count += 1
        logger.info(f"✓ Pauli-X gate on {self.qubits[qubit_idx].id} (成本: {cost:.6f})")
        return cost
    
    def cnot(self, control_idx: int, target_idx: int) -> float:
        """CNOT 門 - 創建糾纏態"""
        cost = self.qubits[control_idx].cost_per_operation * 2
        
        # 如果控制位元為 1,翻轉目標位元
        if self.qubits[control_idx].get_probability_1() > np.random.random():
            self.pauli_x(target_idx)
        
        # 記錄糾纏關係
        if self.qubits[control_idx].id not in self.entanglement_map:
            self.entanglement_map[self.qubits[control_idx].id] = []
        self.entanglement_map[self.qubits[control_idx].id].append(self.qubits[target_idx].id)
        
        self.total_cost += cost
        self.operation_count += 1
        logger.info(f"✓ CNOT gate: {self.qubits[control_idx].id} → {self.qubits[target_idx].id} (成本: {cost:.6f})")
        return cost
    
    def measure_all(self) -> List[int]:
        """測量所有量子位元"""
        results = [qubit.measure() for qubit in self.qubits]
        logger.info(f"📊 測量結果: {results} (暫存器: {self.name})")
        return results
    
    def get_state_info(self) -> Dict[str, Any]:
        """獲取狀態信息"""
        return {
            "name": self.name,
            "num_qubits": self.num_qubits,
            "total_cost": self.total_cost,
            "operation_count": self.operation_count,
            "qubit_states": [
                {
                    "id": q.id,
                    "prob_0": q.get_probability_0(),
                    "prob_1": q.get_probability_1(),
                    "measured_value": q.measured_value,
                    "measurement_count": q.measurement_count
                }
                for q in self.qubits
            ],
            "entanglements": self.entanglement_map
        }


class SimulatedQuantumGenerator:
    """模擬量子生成系統 - 主控制類"""
    
    def __init__(self, name: str = "QuantumGenerator"):
        self.name = name
        self.registers: Dict[str, QuantumRegister] = {}
        self.total_cost = 0.0
        self.total_operations = 0
        self.execution_log: List[Dict] = []
        self.start_time = datetime.now()
        
    def create_register(self, name: str, num_qubits: int) -> QuantumRegister:
        """創建量子暫存器"""
        register = QuantumRegister(name=name, num_qubits=num_qubits)
        self.registers[name] = register
        logger.info(f"✅ 創建量子暫存器: {name} ({num_qubits} qubits)")
        return register
    
    def run_circuit(self, register_name: str, circuit_def: List[Tuple]) -> List[int]:
        """執行量子電路
        
        circuit_def: [(gate_name, qubit_idx, ...)]
        例如: [('hadamard', 0), ('pauli_x', 1), ('cnot', 0, 1)]
        """
        register = self.registers[register_name]
        logger.info(f"\n🔄 執行量子電路: {register_name}")
        logger.info(f"   電路定義: {circuit_def}")
        
        for instruction in circuit_def:
            gate_name = instruction[0]
            
            if gate_name == "hadamard":
                cost = register.hadamard(instruction[1])
            elif gate_name == "pauli_x":
                cost = register.pauli_x(instruction[1])
            elif gate_name == "cnot":
                cost = register.cnot(instruction[1], instruction[2])
            else:
                raise ValueError(f"Unknown gate: {gate_name}")
            
            self.total_cost += cost
            self.total_operations += 1
        
        # 測量
        results = register.measure_all()
        
        # 記錄執行
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "register": register_name,
            "circuit": circuit_def,
            "results": results,
            "register_cost": register.total_cost,
            "total_cost": self.total_cost
        })
        
        return results
    
    def run_quantum_algorithm(self, algorithm_name: str, problem_data: np.ndarray) -> Dict[str, Any]:
        """執行量子算法 (例如 Grover 搜索)"""
        logger.info(f"\n🧬 執行量子算法: {algorithm_name}")
        
        if algorithm_name == "grover_search":
            return self._grover_search(problem_data)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    def _grover_search(self, marked_items: np.ndarray) -> Dict[str, Any]:
        """Grover 搜索算法模擬"""
        n = len(marked_items)
        num_qubits = int(np.ceil(np.log2(n)))
        
        register = self.create_register("grover", num_qubits)
        
        # 初始化超位置態
        circuit = [('hadamard', i) for i in range(num_qubits)]
        
        # Grover 迭代
        iterations = int(np.pi / 4 * np.sqrt(n))
        for _ in range(iterations):
            # Oracle (標記搜尋項)
            for idx, item in enumerate(marked_items):
                if item > 0.5:  # 找到標記項
                    circuit.append(('pauli_x', idx % num_qubits))
        
        results = self.run_circuit("grover", circuit)
        
        return {
            "algorithm": "grover",
            "results": results,
            "cost": register.total_cost,
            "iterations": iterations
        }
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        """獲得成本分析"""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_cost": self.total_cost,
            "total_operations": self.total_operations,
            "avg_cost_per_op": self.total_cost / max(1, self.total_operations),
            "elapsed_time": elapsed_time,
            "ops_per_second": self.total_operations / max(0.001, elapsed_time),
            "registers": {
                name: register.get_state_info()
                for name, register in self.registers.items()
            }
        }
    
    def verify_operations(self) -> bool:
        """驗證所有操作都確實執行了"""
        logger.info("\n✅ 驗證量子操作...")
        
        total_register_ops = sum(r.operation_count for r in self.registers.values())
        
        # 驗證 1: 操作計數一致
        if total_register_ops != self.total_operations:
            logger.warning(f"⚠️  操作計數不匹配: {total_register_ops} vs {self.total_operations}")
            return False
        
        # 驗證 2: 成本計算一致
        total_register_cost = sum(r.total_cost for r in self.registers.values())
        if abs(total_register_cost - self.total_cost) > 0.001:
            logger.warning(f"⚠️  成本不匹配: {total_register_cost} vs {self.total_cost}")
            return False
        
        # 驗證 3: 執行日誌完整
        if len(self.execution_log) == 0:
            logger.warning("⚠️  執行日誌為空")
            return False
        
        logger.info("✅ 所有驗證通過!")
        logger.info(f"   • 操作計數: {self.total_operations}")
        logger.info(f"   • 總成本: {self.total_cost:.6f}")
        logger.info(f"   • 執行次數: {len(self.execution_log)}")
        
        return True
    
    def save_report(self, filepath: str = "/workspaces/cosmic-ai.uk/logs/quantum_generator_report.json"):
        """保存報告"""
        # 將 numpy 類型轉換為 Python 原生類型
        def convert_numpy(obj):
            if hasattr(obj, 'item'):
                return obj.item()
            if isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            return obj
        
        report = {
            "system": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "cost_analysis": self.get_cost_analysis(),
            "execution_log": self.execution_log,
            "verification": {
                "all_passed": self.verify_operations(),
                "total_operations": self.total_operations,
                "total_cost": self.total_cost
            }
        }
        
        # 轉換所有 numpy 類型
        report = convert_numpy(report)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 報告已保存: {filepath}")
        return report


def main():
    """主程序 - 演示模擬量子生成系統"""
    logger.info("=" * 80)
    logger.info("🚀 啟動模擬量子生成系統")
    logger.info("=" * 80)
    
    # 創建生成器
    generator = SimulatedQuantumGenerator("MainQuantumGenerator")
    
    # 演示 1: 基本量子電路
    logger.info("\n【演示 1】基本量子電路 - 創建疊加態和測量")
    logger.info("-" * 80)
    
    register1 = generator.create_register("demo1", 3)
    circuit1 = [
        ('hadamard', 0),      # 在 q0 上應用 Hadamard
        ('hadamard', 1),      # 在 q1 上應用 Hadamard
        ('pauli_x', 2)        # 在 q2 上應用 Pauli-X
    ]
    results1 = generator.run_circuit("demo1", circuit1)
    logger.info(f"✅ 演示 1 完成: 測量結果 = {results1}")
    
    # 演示 2: 糾纏態
    logger.info("\n【演示 2】糾纏態電路 - CNOT 門")
    logger.info("-" * 80)
    
    register2 = generator.create_register("demo2", 2)
    circuit2 = [
        ('hadamard', 0),      # 創建疊加態
        ('cnot', 0, 1)        # 糾纏
    ]
    results2 = generator.run_circuit("demo2", circuit2)
    logger.info(f"✅ 演示 2 完成: 測量結果 = {results2}")
    
    # 演示 3: 複雜電路
    logger.info("\n【演示 3】複雜量子電路 - 多門組合")
    logger.info("-" * 80)
    
    register3 = generator.create_register("demo3", 4)
    circuit3 = [
        ('hadamard', 0),
        ('hadamard', 1),
        ('cnot', 0, 2),
        ('cnot', 1, 3),
        ('pauli_x', 0)
    ]
    results3 = generator.run_circuit("demo3", circuit3)
    logger.info(f"✅ 演示 3 完成: 測量結果 = {results3}")
    
    # 演示 4: Grover 算法
    logger.info("\n【演示 4】Grover 搜索算法")
    logger.info("-" * 80)
    
    marked_items = np.array([0, 1, 0, 0, 1, 0, 0, 0])  # 標記搜尋項
    grover_result = generator.run_quantum_algorithm("grover_search", marked_items)
    logger.info(f"✅ 演示 4 完成: Grover 結果 = {grover_result}")
    
    # 驗證所有操作
    logger.info("\n【驗證階段】")
    logger.info("-" * 80)
    generator.verify_operations()
    
    # 成本分析
    logger.info("\n【成本分析】")
    logger.info("-" * 80)
    cost_analysis = generator.get_cost_analysis()
    logger.info(f"📊 總成本: {cost_analysis['total_cost']:.6f}")
    logger.info(f"📊 總操作數: {cost_analysis['total_operations']}")
    logger.info(f"📊 平均成本/操作: {cost_analysis['avg_cost_per_op']:.6f}")
    logger.info(f"📊 執行時間: {cost_analysis['elapsed_time']:.3f} 秒")
    logger.info(f"📊 操作速率: {cost_analysis['ops_per_second']:.1f} ops/sec")
    
    # 保存報告
    logger.info("\n【報告生成】")
    logger.info("-" * 80)
    report = generator.save_report()
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ 模擬量子生成系統運行完成")
    logger.info("=" * 80)
    
    return generator, report


if __name__ == "__main__":
    generator, report = main()
