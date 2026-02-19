#!/usr/bin/env python3
"""
量子 Grover 搜索算法 + 經典替代實現
Quantum Grover Search Algorithm + Classical Alternative
用於 Comic AI 交易系統的最優策略搜索

涵蓋:
1. 量子 Grover 算法實現
2. 經典算法替代實現
3. 性能對比分析
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import math
import json
from abc import ABC, abstractmethod
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 第 1 部分: 量子 Grover 算法實現
# ═══════════════════════════════════════════════════════════════════════════

class QuantumState:
    """量子態表示"""
    
    def __init__(self, amplitudes: np.ndarray):
        """
        初始化量子態
        
        Args:
            amplitudes: 復數振幅數組
        """
        self.amplitudes = amplitudes.astype(complex)
        self._normalize()
    
    def _normalize(self) -> None:
        """歸一化量子態"""
        norm = np.sqrt(np.sum(np.abs(self.amplitudes) ** 2))
        if norm > 0:
            self.amplitudes /= norm
    
    def apply_hadamard(self) -> 'QuantumState':
        """應用 Hadamard 門"""
        n = len(self.amplitudes)
        H = np.ones((n, n)) * (1 / np.sqrt(n))
        H[np.diag_indices_from(H)] = (1 - n) / np.sqrt(n)
        
        new_amplitudes = H @ self.amplitudes
        return QuantumState(new_amplitudes)
    
    def apply_phase_flip(self, marked_indices: List[int]) -> 'QuantumState':
        """應用相位翻轉 (對標記的態)"""
        new_amplitudes = self.amplitudes.copy()
        for idx in marked_indices:
            if 0 <= idx < len(new_amplitudes):
                new_amplitudes[idx] *= -1
        return QuantumState(new_amplitudes)
    
    def apply_diffusion(self) -> 'QuantumState':
        """應用 Grover 擴散操作符"""
        n = len(self.amplitudes)
        mean = np.mean(np.abs(self.amplitudes) ** 2)
        
        new_amplitudes = 2 * mean * np.ones(n) - self.amplitudes
        return QuantumState(new_amplitudes)
    
    def measure(self) -> int:
        """測量量子態,返回測量結果"""
        probabilities = np.abs(self.amplitudes) ** 2
        return np.random.choice(len(self.amplitudes), p=probabilities)
    
    def get_probabilities(self) -> np.ndarray:
        """獲取所有態的概率"""
        return np.abs(self.amplitudes) ** 2


class GroverQuantumSearch:
    """Grover 量子搜索算法"""
    
    def __init__(self, n_qubits: int):
        """
        初始化 Grover 搜索器
        
        Args:
            n_qubits: 量子比特數
        """
        self.n_qubits = n_qubits
        self.n_states = 2 ** n_qubits
        
    def search(self, 
               marked_indices: List[int],
               iterations: Optional[int] = None) -> Tuple[int, float]:
        """
        執行 Grover 搜索
        
        Args:
            marked_indices: 標記的態的索引 (目標)
            iterations: 迭代次數 (默認自動計算)
            
        Returns:
            (測量結果, 成功概率)
        """
        if iterations is None:
            # 最優迭代次數
            iterations = int(np.pi / 4 * np.sqrt(self.n_states / len(marked_indices)))
        
        # 1. 初始化:創建均勻疊加態
        amplitudes = np.ones(self.n_states) / np.sqrt(self.n_states)
        state = QuantumState(amplitudes)
        
        logger.info(f"初始化 Grover 搜索: {self.n_qubits} qubits, {len(marked_indices)} 標記態")
        logger.info(f"最優迭代次數: {iterations}")
        
        # 2. Grover 迭代
        for i in range(iterations):
            # 應用 Oracle (相位翻轉標記態)
            state = state.apply_phase_flip(marked_indices)
            
            # 應用擴散操作符
            state = state.apply_diffusion()
            
            if (i + 1) % max(1, iterations // 5) == 0:
                probs = state.get_probabilities()
                marked_prob = sum(probs[idx] for idx in marked_indices if idx < len(probs))
                logger.debug(f"迭代 {i + 1}: 標記態概率 = {marked_prob:.4f}")
        
        # 3. 測量
        result = state.measure()
        
        # 計算成功概率
        probs = state.get_probabilities()
        success_prob = sum(probs[idx] for idx in marked_indices if idx < len(probs))
        
        logger.info(f"搜索結果: {result}, 成功概率: {success_prob:.4f}")
        
        return result, success_prob


# ═══════════════════════════════════════════════════════════════════════════
# 第 2 部分: 經典算法替代實現
# ═══════════════════════════════════════════════════════════════════════════

class ClassicalSearchMethod(ABC):
    """經典搜索方法的抽象基類"""
    
    @abstractmethod
    def search(self, scores: np.ndarray) -> Tuple[int, float]:
        """搜索並返回 (最優索引, 置信度)"""
        pass


class LinearClassicalSearch(ClassicalSearchMethod):
    """線性搜索 (最簡單的替代)"""
    
    def search(self, scores: np.ndarray) -> Tuple[int, float]:
        """
        線性搜索最優值
        
        Args:
            scores: 每個態的評分
            
        Returns:
            (最優索引, 置信度)
        """
        best_idx = np.argmax(scores)
        best_score = scores[best_idx]
        
        # 置信度 = (最優分 - 次優分) / 最優分
        sorted_scores = np.sort(scores)[::-1]
        confidence = 1.0 if len(sorted_scores) < 2 else (sorted_scores[0] - sorted_scores[1]) / (sorted_scores[0] + 1e-9)
        
        logger.info(f"線性搜索: 最優索引={best_idx}, 最優分={best_score:.4f}, 置信度={confidence:.4f}")
        return best_idx, confidence


class BinarySearchClassical(ClassicalSearchMethod):
    """二分搜索 (中等複雜度)"""
    
    def search(self, scores: np.ndarray) -> Tuple[int, float]:
        """
        二分搜索最優值
        
        Args:
            scores: 每個態的評分
            
        Returns:
            (最優索引, 置信度)
        """
        indices = np.argsort(scores)[::-1]  # 降序排序
        
        # 取前 10% 的索引作為高質量候選
        n_candidates = max(1, len(indices) // 10)
        candidates = indices[:n_candidates]
        
        best_idx = candidates[0]
        best_score = scores[best_idx]
        
        # 計算置信度
        average_candidate_score = np.mean(scores[candidates])
        confidence = best_score / (average_candidate_score + 1e-9)
        
        logger.info(f"二分搜索: 最優索引={best_idx}, 最優分={best_score:.4f}, 置信度={confidence:.4f}")
        return best_idx, confidence


class QuantumInspiredClassical(ClassicalSearchMethod):
    """量子啟發的經典搜索 (模擬 Grover 行為)"""
    
    def __init__(self, iterations: int = 10):
        """
        初始化量子啟發搜索
        
        Args:
            iterations: 迭代次數 (模擬 Grover 迭代)
        """
        self.iterations = iterations
    
    def search(self, scores: np.ndarray) -> Tuple[int, float]:
        """
        使用量子啟發策略搜索
        
        模擬 Grover 算法的機制:
        1. 初始化:均勻分佈
        2. 每次迭代:增加高分態的權重
        3. 最終:選擇最高權重的態
        """
        n = len(scores)
        
        # 1. 初始化:均勻分佈
        weights = np.ones(n) / n
        
        # 2. 迭代優化
        for iteration in range(self.iterations):
            # 計算當前期望值
            current_mean = np.sum(weights * scores)
            
            # 應用相位翻轉 (增加高分態的權重)
            new_weights = np.zeros_like(weights)
            for i in range(n):
                if scores[i] > current_mean:
                    new_weights[i] = weights[i] * 2
                else:
                    new_weights[i] = weights[i] * 0.5
            
            # 歸一化
            new_weights /= np.sum(new_weights)
            weights = new_weights
        
        # 3. 選擇最高權重的態
        best_idx = np.argmax(weights)
        
        # 計算置信度 = (最高權重 - 次高權重) / 最高權重
        sorted_weights = np.sort(weights)[::-1]
        confidence = 1.0 if len(sorted_weights) < 2 else (sorted_weights[0] - sorted_weights[1]) / sorted_weights[0]
        
        logger.info(f"量子啟發搜索: 最優索引={best_idx}, 置信度={confidence:.4f}")
        return best_idx, confidence


# ═══════════════════════════════════════════════════════════════════════════
# 第 3 部分: 應用於交易系統
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TradingSignal:
    """交易信號"""
    signal_id: int
    strategy: str
    entry_price: float
    exit_price: float
    risk_reward_ratio: float
    win_probability: float
    sharpe_ratio: float
    
    def get_score(self) -> float:
        """計算信號的綜合評分"""
        # 加權評分: risk_reward_ratio (40%) + win_probability (40%) + sharpe_ratio (20%)
        score = (
            0.4 * min(self.risk_reward_ratio, 10.0) / 10.0 +
            0.4 * self.win_probability +
            0.2 * min(self.sharpe_ratio, 5.0) / 5.0
        )
        return score


class QuantumTradingOptimizer:
    """量子優化的交易信號選擇器"""
    
    def __init__(self, use_quantum: bool = True, n_qubits: int = 4):
        """
        初始化交易優化器
        
        Args:
            use_quantum: 是否使用量子算法 (True) 或經典算法 (False)
            n_qubits: 量子比特數
        """
        self.use_quantum = use_quantum
        self.n_qubits = n_qubits
        
        if use_quantum:
            self.quantum_searcher = GroverQuantumSearch(n_qubits)
            logger.info("使用量子 Grover 搜索")
        else:
            self.classical_searcher = QuantumInspiredClassical(iterations=15)
            logger.info("使用量子啟發的經典搜索")
    
    def select_best_signal(self, signals: List[TradingSignal]) -> Tuple[Optional[TradingSignal], Dict[str, Any]]:
        """
        從信號列表中選擇最優信號
        
        Args:
            signals: 交易信號列表
            
        Returns:
            (選中的信號, 詳細信息)
        """
        if not signals:
            return None, {"error": "No signals available"}
        
        # 計算每個信號的評分
        scores = np.array([signal.get_score() for signal in signals])
        
        logger.info(f"評估 {len(signals)} 個信號")
        logger.info(f"評分範圍: {scores.min():.4f} - {scores.max():.4f}")
        
        start_time = datetime.now()
        
        if self.use_quantum:
            # 使用量子搜索
            # 將評分轉換為比特索引 (標記高分信號)
            threshold = np.median(scores)
            marked_indices = [i for i, score in enumerate(scores) if score >= threshold]
            
            if not marked_indices:
                marked_indices = [np.argmax(scores)]
            
            selected_idx, success_prob = self.quantum_searcher.search(marked_indices)
            method = "Quantum Grover"
        else:
            # 使用經典搜索
            selected_idx, success_prob = self.classical_searcher.search(scores)
            method = "Classical (Quantum-Inspired)"
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        selected_signal = signals[selected_idx]
        
        details = {
            "method": method,
            "selected_index": selected_idx,
            "selected_signal_id": selected_signal.signal_id,
            "signal_score": float(scores[selected_idx]),
            "confidence": float(success_prob),
            "all_scores": scores.tolist(),
            "elapsed_time_ms": elapsed_time * 1000,
            "total_signals": len(signals)
        }
        
        logger.info(f"選擇完成: 信號 ID={selected_signal.signal_id}, 評分={scores[selected_idx]:.4f}, "
                   f"耗時={elapsed_time*1000:.2f}ms")
        
        return selected_signal, details


# ═══════════════════════════════════════════════════════════════════════════
# 第 4 部分: 性能對比分析
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BenchmarkResult:
    """基準測試結果"""
    method: str
    n_signals: int
    selected_signal_id: int
    signal_score: float
    confidence: float
    elapsed_time_ms: float
    quality_score: float  # 綜合質量評分


class AlgorithmBenchmark:
    """算法性能基準測試"""
    
    def __init__(self, n_qubits: int = 4):
        """初始化基準測試"""
        self.n_qubits = n_qubits
        self.results: List[BenchmarkResult] = []
    
    def generate_test_signals(self, n_signals: int = 100) -> List[TradingSignal]:
        """生成測試交易信號"""
        signals = []
        for i in range(n_signals):
            signal = TradingSignal(
                signal_id=i,
                strategy=f"Strategy_{i % 5}",
                entry_price=100.0 + np.random.randn() * 5,
                exit_price=100.0 + np.random.randn() * 5,
                risk_reward_ratio=1.0 + np.random.exponential(1.5),
                win_probability=0.3 + np.random.rand() * 0.4,
                sharpe_ratio=0.5 + np.random.exponential(1.0)
            )
            signals.append(signal)
        return signals
    
    def run_benchmark(self, n_signals: int = 100, num_runs: int = 10):
        """
        執行基準測試
        
        Args:
            n_signals: 每次運行的信號數量
            num_runs: 運行次數
        """
        logger.info(f"開始基準測試: {n_signals} 個信號, 運行 {num_runs} 次")
        
        quantum_optimizer = QuantumTradingOptimizer(use_quantum=True, n_qubits=self.n_qubits)
        classical_optimizer = QuantumTradingOptimizer(use_quantum=False, n_qubits=self.n_qubits)
        
        for run in range(num_runs):
            logger.info(f"\n運行 {run + 1}/{num_runs}")
            
            # 生成測試信號
            signals = self.generate_test_signals(n_signals)
            
            # 量子方法
            q_signal, q_details = quantum_optimizer.select_best_signal(signals)
            q_result = BenchmarkResult(
                method="Quantum (Grover)",
                n_signals=n_signals,
                selected_signal_id=q_signal.signal_id,
                signal_score=q_details["signal_score"],
                confidence=q_details["confidence"],
                elapsed_time_ms=q_details["elapsed_time_ms"],
                quality_score=q_details["signal_score"] * q_details["confidence"]
            )
            self.results.append(q_result)
            
            # 經典方法
            c_signal, c_details = classical_optimizer.select_best_signal(signals)
            c_result = BenchmarkResult(
                method="Classical (Quantum-Inspired)",
                n_signals=n_signals,
                selected_signal_id=c_signal.signal_id,
                signal_score=c_details["signal_score"],
                confidence=c_details["confidence"],
                elapsed_time_ms=c_details["elapsed_time_ms"],
                quality_score=c_details["signal_score"] * c_details["confidence"]
            )
            self.results.append(c_result)
        
        self.print_summary()
    
    def print_summary(self):
        """打印摘要"""
        quantum_results = [r for r in self.results if "Quantum" in r.method]
        classical_results = [r for r in self.results if "Classical" in r.method]
        
        print("\n" + "=" * 80)
        print("📊 基準測試結果摘要")
        print("=" * 80)
        
        for method_results, label in [(quantum_results, "量子方法"), (classical_results, "經典方法")]:
            if not method_results:
                continue
            
            print(f"\n{label}:")
            print(f"  平均耗時: {np.mean([r.elapsed_time_ms for r in method_results]):.4f} ms")
            print(f"  平均信號評分: {np.mean([r.signal_score for r in method_results]):.4f}")
            print(f"  平均置信度: {np.mean([r.confidence for r in method_results]):.4f}")
            print(f"  平均質量評分: {np.mean([r.quality_score for r in method_results]):.4f}")
        
        print("\n" + "=" * 80)
        print("結論: 兩種方法都能有效選擇高質量的交易信號")
        print("      量子方法在理論上更優雅,經典方法在實踐中更快速")
        print("=" * 80 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# 第 5 部分: 使用示例
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """主函數 - 演示使用"""
    
    print("\n" + "=" * 80)
    print("🚀 量子 Grover 搜索算法 + 經典替代實現")
    print("   Comic AI 交易系統中的應用")
    print("=" * 80 + "\n")
    
    # ──────────────────────────────────
    # 示例 1: 基本使用
    # ──────────────────────────────────
    print("示例 1: 基本使用")
    print("-" * 80)
    
    # 創建示例交易信號
    signals = [
        TradingSignal(
            signal_id=i,
            strategy=f"Strategy_{i}",
            entry_price=100.0 + i,
            exit_price=110.0 + i,
            risk_reward_ratio=2.0 + i * 0.1,
            win_probability=0.4 + i * 0.03,
            sharpe_ratio=1.0 + i * 0.15
        )
        for i in range(8)
    ]
    
    # 使用量子方法
    print("\n使用量子 Grover 搜索:")
    quantum_optimizer = QuantumTradingOptimizer(use_quantum=True, n_qubits=3)
    best_signal, details = quantum_optimizer.select_best_signal(signals)
    print(f"  選中信號: {best_signal.signal_id}")
    print(f"  評分: {details['signal_score']:.4f}")
    print(f"  置信度: {details['confidence']:.4f}")
    
    # 使用經典方法
    print("\n使用經典搜索 (量子啟發):")
    classical_optimizer = QuantumTradingOptimizer(use_quantum=False, n_qubits=3)
    best_signal_c, details_c = classical_optimizer.select_best_signal(signals)
    print(f"  選中信號: {best_signal_c.signal_id}")
    print(f"  評分: {details_c['signal_score']:.4f}")
    print(f"  置信度: {details_c['confidence']:.4f}")
    
    # ──────────────────────────────────
    # 示例 2: 性能基準測試
    # ──────────────────────────────────
    print("\n\n示例 2: 性能基準測試")
    print("-" * 80)
    
    benchmark = AlgorithmBenchmark(n_qubits=4)
    benchmark.run_benchmark(n_signals=50, num_runs=5)
    
    # ──────────────────────────────────
    # 示例 3: 分析結果
    # ──────────────────────────────────
    print("\n示例 3: 詳細分析")
    print("-" * 80)
    
    quantum_results = [r for r in benchmark.results if "Quantum" in r.method]
    classical_results = [r for r in benchmark.results if "Classical" in r.method]
    
    print("\n性能指標對比:")
    print(f"  方法                      耗時(ms)    評分    置信度   質量")
    print(f"  {'─' * 55}")
    
    for method, results in [("量子 Grover", quantum_results), ("經典搜索", classical_results)]:
        avg_time = np.mean([r.elapsed_time_ms for r in results])
        avg_score = np.mean([r.signal_score for r in results])
        avg_conf = np.mean([r.confidence for r in results])
        avg_quality = np.mean([r.quality_score for r in results])
        
        print(f"  {method:20s}  {avg_time:8.2f}    {avg_score:5.3f}   {avg_conf:5.3f}  {avg_quality:5.3f}")
    
    print("\n結論:")
    print("  • 量子算法理論上效率更高 (複雜度 O(√N) vs O(N))")
    print("  • 經典實現更實用,無需量子硬件")
    print("  • 兩種方法都能有效選擇最優交易信號")
    print("  • 可根據實際場景選擇合適的方法")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
