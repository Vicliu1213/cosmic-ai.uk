#!/usr/bin/env python3
"""
Ray Distribution Performance Test
Ray 分布式性能測試套件
"""

import time
import numpy as np
from typing import Dict, Any, List
import logging
import json
from datetime import datetime

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """性能基準測試類"""
    
    def __init__(self, output_file: str = "benchmark_results.json"):
        """初始化基準測試
        
        Args:
            output_file: 結果輸出文件
        """
        self.output_file = output_file
        self.results = []
    
    def benchmark_quantum_engine(self) -> Dict[str, Any]:
        """量子引擎性能測試
        
        Returns:
            測試結果
        """
        logger.info("🔬 Starting Quantum Engine Benchmark...")
        
        try:
            from engine.quantum_engine import QuantumEngine
        except ImportError:
            logger.error("Failed to import QuantumEngine")
            return {'status': 'failed', 'error': 'Import failed'}
        
        results = {
            'test': 'quantum_engine',
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {}
        }
        
        # 測試 1: 非分布式分析
        logger.info("Test 1: Sequential Quantum Analysis")
        qe_sequential = QuantumEngine(use_distributed=False)
        data = np.random.randn(1000, 100)
        
        start_time = time.time()
        seq_result = qe_sequential.run_analysis('heisenberg', data)
        sequential_time = time.time() - start_time
        
        results['benchmarks']['sequential'] = {
            'time_seconds': sequential_time,
            'data_shape': str(data.shape)
        }
        logger.info(f"✅ Sequential analysis completed in {sequential_time:.4f}s")
        
        # 測試 2: 分布式分析
        logger.info("Test 2: Distributed Quantum Analysis")
        try:
            qe_distributed = QuantumEngine(use_distributed=True)
            
            # 創建批次數據
            batches = [np.random.randn(100, 100) for _ in range(10)]
            
            start_time = time.time()
            dist_results = qe_distributed.run_parallel_analysis(batches, 'heisenberg')
            distributed_time = time.time() - start_time
            
            results['benchmarks']['distributed'] = {
                'time_seconds': distributed_time,
                'batches': len(batches),
                'speedup': round(sequential_time / distributed_time, 2) if distributed_time > 0 else 0
            }
            logger.info(f"✅ Distributed analysis completed in {distributed_time:.4f}s")
            logger.info(f"📈 Speedup: {results['benchmarks']['distributed']['speedup']}x")
            
            qe_distributed.shutdown()
        except Exception as e:
            logger.warning(f"Distributed test failed: {e}")
            results['benchmarks']['distributed'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return results
    
    def benchmark_genetic_algorithm(self) -> Dict[str, Any]:
        """遺傳算法性能測試
        
        Returns:
            測試結果
        """
        logger.info("🧬 Starting Genetic Algorithm Benchmark...")
        
        try:
            from engine.quantum_engine import QuantumEngine
        except ImportError:
            logger.error("Failed to import QuantumEngine")
            return {'status': 'failed', 'error': 'Import failed'}
        
        results = {
            'test': 'genetic_algorithm',
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {}
        }
        
        # 測試 1: 順序遺傳算法
        logger.info("Test 1: Sequential Genetic Algorithm")
        qe = QuantumEngine(use_distributed=False)
        
        start_time = time.time()
        seq_ga = qe._sequential_genetic_analysis(population_size=50, generations=20)
        seq_time = time.time() - start_time
        
        results['benchmarks']['sequential'] = {
            'time_seconds': seq_time,
            'generations': 20,
            'population_size': 50
        }
        logger.info(f"✅ Sequential GA completed in {seq_time:.4f}s")
        
        # 測試 2: 分布式遺傳算法
        logger.info("Test 2: Distributed Genetic Algorithm")
        try:
            qe_dist = QuantumEngine(use_distributed=True)
            
            start_time = time.time()
            dist_ga = qe_dist.distributed_genetic_analysis(population_size=50, generations=20)
            dist_time = time.time() - start_time
            
            results['benchmarks']['distributed'] = {
                'time_seconds': dist_time,
                'generations': 20,
                'population_size': 50,
                'speedup': round(seq_time / dist_time, 2) if dist_time > 0 else 0
            }
            logger.info(f"✅ Distributed GA completed in {dist_time:.4f}s")
            logger.info(f"📈 Speedup: {results['benchmarks']['distributed']['speedup']}x")
            
            qe_dist.shutdown()
        except Exception as e:
            logger.warning(f"Distributed GA test failed: {e}")
            results['benchmarks']['distributed'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return results
    
    def benchmark_data_compression(self) -> Dict[str, Any]:
        """數據壓縮性能測試
        
        Returns:
            測試結果
        """
        logger.info("🗜️ Starting Data Compression Benchmark...")
        
        try:
            from data.data_manager import DataManager
        except ImportError:
            logger.error("Failed to import DataManager")
            return {'status': 'failed', 'error': 'Import failed'}
        
        results = {
            'test': 'data_compression',
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {}
        }
        
        # 測試 1: 順序壓縮
        logger.info("Test 1: Sequential Compression")
        dm_seq = DataManager(use_distributed=False)
        
        # 創建測試數據
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            test_files = []
            for i in range(5):
                file_path = f"{tmpdir}/test_file_{i}.txt"
                with open(file_path, 'w') as f:
                    f.write("x" * 1000000)  # 1MB
                test_files.append(file_path)
            
            start_time = time.time()
            seq_results = dm_seq.batch_compress([f"*.txt"])
            seq_time = time.time() - start_time
            
            results['benchmarks']['sequential'] = {
                'time_seconds': seq_time,
                'files_compressed': len([r for r in seq_results.values() if r])
            }
            logger.info(f"✅ Sequential compression completed in {seq_time:.4f}s")
        
        # 測試 2: 分布式壓縮
        logger.info("Test 2: Distributed Compression")
        try:
            dm_dist = DataManager(use_distributed=True)
            
            with tempfile.TemporaryDirectory() as tmpdir:
                test_files = []
                for i in range(5):
                    file_path = f"{tmpdir}/test_file_{i}.txt"
                    with open(file_path, 'w') as f:
                        f.write("x" * 1000000)
                    test_files.append(file_path)
                
                start_time = time.time()
                dist_results = dm_dist.batch_compress([f"*.txt"])
                dist_time = time.time() - start_time
                
                results['benchmarks']['distributed'] = {
                    'time_seconds': dist_time,
                    'files_compressed': len([r for r in dist_results.values() if r]),
                    'speedup': round(seq_time / dist_time, 2) if dist_time > 0 else 0
                }
                logger.info(f"✅ Distributed compression completed in {dist_time:.4f}s")
                logger.info(f"📈 Speedup: {results['benchmarks']['distributed']['speedup']}x")
            
            dm_dist.shutdown()
        except Exception as e:
            logger.warning(f"Distributed compression test failed: {e}")
            results['benchmarks']['distributed'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return results
    
    def run_all_benchmarks(self) -> List[Dict[str, Any]]:
        """運行所有基準測試
        
        Returns:
            所有測試結果
        """
        logger.info("=" * 60)
        logger.info("🚀 Comic AI Ray Distribution Performance Benchmark")
        logger.info("=" * 60)
        
        benchmarks = [
            self.benchmark_quantum_engine(),
            self.benchmark_genetic_algorithm(),
            self.benchmark_data_compression(),
        ]
        
        self.results = benchmarks
        self._save_results()
        
        return benchmarks
    
    def _save_results(self) -> None:
        """保存結果到文件"""
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"✅ Results saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def print_summary(self) -> None:
        """打印性能摘要"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 Performance Summary")
        logger.info("=" * 60)
        
        for result in self.results:
            logger.info(f"\n{result['test'].upper()}")
            logger.info("-" * 40)
            
            for bench_name, bench_data in result.get('benchmarks', {}).items():
                logger.info(f"  {bench_name}:")
                for key, value in bench_data.items():
                    logger.info(f"    {key}: {value}")


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()
    benchmark.print_summary()
