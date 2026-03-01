#!/usr/bin/env python3
"""
Ray Distributed Computing Engine
Ray 分布式計算引擎 - 為量子分析提供並行計算加速
"""

import ray
import numpy as np
from typing import Dict, List, Optional, Any, Callable, Tuple
from pathlib import Path
import logging
from functools import partial
import asyncio

logger = logging.getLogger(__name__)

class RayDistributedEngine:
    """Ray 分布式計算引擎 - 提升計算效率"""
    
    def __init__(self, 
                 num_cpus: Optional[int] = None,
                 num_gpus: Optional[int] = 0,
                 memory_gb: Optional[int] = None,
                 ray_dashboard: bool = True):
        """初始化 Ray 分布式引擎
        
        Args:
            num_cpus: CPU 核心數（None 表示自動檢測）
            num_gpus: GPU 數量
            memory_gb: 內存大小（GB）
            ray_dashboard: 是否啟用 Ray 儀表板
        """
        self.num_cpus = num_cpus
        self.num_gpus = num_gpus
        self.memory_gb = memory_gb
        self.ray_dashboard = ray_dashboard
        self.is_initialized = False
        self._init_ray()
        
    def _init_ray(self) -> None:
        """初始化 Ray 環境"""
        try:
            if not ray.is_initialized():
                ray_kwargs = {
                    "_temp_dir": str(Path.home() / ".ray_temp"),
                    "include_dashboard": self.ray_dashboard,
                }
                
                if self.num_cpus:
                    ray_kwargs["num_cpus"] = self.num_cpus
                if self.num_gpus:
                    ray_kwargs["num_gpus"] = self.num_gpus
                if self.memory_gb:
                    ray_kwargs["memory"] = self.memory_gb * 1024 * 1024 * 1024
                
                ray.init(**ray_kwargs)
                self.is_initialized = True
                logger.info("✅ Ray distributed engine initialized")
                self._log_cluster_info()
            else:
                self.is_initialized = True
                logger.info("✅ Ray already initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ray: {e}")
            raise
    
    def _log_cluster_info(self) -> None:
        """記錄集群信息"""
        try:
            info = ray.cluster_resources()
            logger.info(f"Ray Cluster Resources: {info}")
        except Exception as e:
            logger.warning(f"Could not retrieve cluster info: {e}")
    
    @staticmethod
    def _parallel_map(func: Callable, data_list: List[Any], 
                     batch_size: Optional[int] = None) -> List[Any]:
        """並行映射函數到數據列表
        
        Args:
            func: 要應用的函數
            data_list: 數據列表
            batch_size: 批量大小（None 表示自動）
            
        Returns:
            處理結果列表
        """
        if batch_size is None:
            batch_size = len(data_list) // (ray.available_resources()["CPU"] or 1)
            batch_size = max(1, batch_size)
        
        remote_func = ray.remote(func)
        futures = [remote_func.remote(item) for item in data_list]
        results = ray.get(futures)
        
        return results
    
    def parallel_quantum_analysis(self, 
                                 data_batches: List[np.ndarray],
                                 analysis_func: Callable,
                                 theory_name: str) -> List[Dict[str, Any]]:
        """並行量子分析
        
        Args:
            data_batches: 數據批次列表
            analysis_func: 分析函數
            theory_name: 理論名稱
            
        Returns:
            分析結果列表
        """
        @ray.remote
        def quantum_analysis_task(batch: np.ndarray, 
                                 func: Callable,
                                 theory: str) -> Dict[str, Any]:
            """單個量子分析任務"""
            try:
                result = func(batch, theory)
                result['batch_size'] = batch.shape[0]
                result['status'] = 'completed'
                return result
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                return {'status': 'failed', 'error': str(e)}
        
        logger.info(f"Starting parallel quantum analysis with {len(data_batches)} batches")
        
        futures = [
            quantum_analysis_task.remote(batch, analysis_func, theory_name)
            for batch in data_batches
        ]
        
        results = ray.get(futures)
        logger.info(f"✅ Quantum analysis completed: {len(results)} batches processed")
        
        return results
    
    def distributed_genetic_algorithm(self,
                                     population_size: int,
                                     generations: int,
                                     fitness_func: Callable,
                                     crossover_func: Callable,
                                     mutation_func: Callable,
                                     workers: Optional[int] = None) -> Dict[str, Any]:
        """分布式遺傳算法
        
        Args:
            population_size: 種群大小
            generations: 代數
            fitness_func: 適應度函數
            crossover_func: 交叉函數
            mutation_func: 變異函數
            workers: 工作者數量
            
        Returns:
            進化結果
        """
        if workers is None:
            workers = int(ray.available_resources()["CPU"] or 1)
        
        @ray.remote
        def evaluate_population(individuals: List[Any]) -> List[Tuple[Any, float]]:
            """評估種群"""
            evaluated = []
            for individual in individuals:
                fitness = fitness_func(individual)
                evaluated.append((individual, fitness))
            return evaluated
        
        logger.info(f"Starting distributed genetic algorithm: {generations} generations, "
                   f"{population_size} population, {workers} workers")
        
        # 初始化種群
        population = [np.random.randn(population_size) for _ in range(workers)]
        
        best_fitness = float('-inf')
        best_individual = None
        
        for gen in range(generations):
            # 並行評估
            futures = [evaluate_population.remote(pop_chunk) for pop_chunk in population]
            evaluated_pops = ray.get(futures)
            
            # 合併和排序
            all_evaluated = []
            for pop in evaluated_pops:
                all_evaluated.extend(pop)
            
            all_evaluated.sort(key=lambda x: x[1], reverse=True)
            
            # 追蹤最佳個體
            current_best = all_evaluated[0]
            if current_best[1] > best_fitness:
                best_fitness = current_best[1]
                best_individual = current_best[0]
            
            # 選擇、交叉、變異
            top_half = all_evaluated[:len(all_evaluated)//2]
            population = [
                [
                    mutation_func(
                        crossover_func(
                            top_half[i % len(top_half)][0],
                            top_half[(i+1) % len(top_half)][0]
                        )
                    )
                    for i in range(population_size // workers)
                ]
                for _ in range(workers)
            ]
            
            if (gen + 1) % max(1, generations // 10) == 0:
                logger.info(f"Generation {gen+1}/{generations} - Best fitness: {best_fitness:.6f}")
        
        return {
            'best_fitness': best_fitness,
            'best_individual': best_individual,
            'generations': generations,
            'population_size': population_size,
            'status': 'completed'
        }
    
    def parallel_data_processing(self,
                                data_files: List[str],
                                process_func: Callable,
                                workers: Optional[int] = None) -> Dict[str, Any]:
        """並行數據處理
        
        Args:
            data_files: 數據文件列表
            process_func: 處理函數
            workers: 工作者數量
            
        Returns:
            處理結果
        """
        if workers is None:
            workers = int(ray.available_resources()["CPU"] or 1)
        
        @ray.remote
        def process_batch(file_paths: List[str]) -> Dict[str, Any]:
            """處理文件批次"""
            results = {}
            for file_path in file_paths:
                try:
                    result = process_func(file_path)
                    results[file_path] = result
                except Exception as e:
                    logger.error(f"Processing failed for {file_path}: {e}")
                    results[file_path] = {'error': str(e)}
            return results
        
        # 將文件分配到不同的工作者
        batch_size = max(1, len(data_files) // workers)
        batches = [
            data_files[i:i+batch_size]
            for i in range(0, len(data_files), batch_size)
        ]
        
        logger.info(f"Processing {len(data_files)} files with {len(batches)} batches")
        
        futures = [process_batch.remote(batch) for batch in batches]
        results = ray.get(futures)
        
        # 合併結果
        combined_results = {}
        for batch_result in results:
            combined_results.update(batch_result)
        
        return {
            'total_files': len(data_files),
            'processed': len([r for r in combined_results.values() if 'error' not in r]),
            'failed': len([r for r in combined_results.values() if 'error' in r]),
            'details': combined_results,
            'status': 'completed'
        }
    
    def compress_in_parallel(self,
                            file_paths: List[str],
                            compression_func: Callable,
                            workers: Optional[int] = None) -> Dict[str, str]:
        """並行壓縮文件
        
        Args:
            file_paths: 文件路徑列表
            compression_func: 壓縮函數
            workers: 工作者數量
            
        Returns:
            壓縮結果映射
        """
        if workers is None:
            workers = int(ray.available_resources()["CPU"] or 1)
        
        @ray.remote
        def compress_batch(files: List[str]) -> Dict[str, str]:
            """壓縮文件批次"""
            results = {}
            for file_path in files:
                try:
                    compressed = compression_func(file_path)
                    results[file_path] = compressed
                except Exception as e:
                    logger.error(f"Compression failed for {file_path}: {e}")
            return results
        
        # 分配文件到工作者
        batch_size = max(1, len(file_paths) // workers)
        batches = [
            file_paths[i:i+batch_size]
            for i in range(0, len(file_paths), batch_size)
        ]
        
        logger.info(f"Compressing {len(file_paths)} files with {len(batches)} workers")
        
        futures = [compress_batch.remote(batch) for batch in batches]
        batch_results = ray.get(futures)
        
        # 合併結果
        combined = {}
        for batch_result in batch_results:
            combined.update(batch_result)
        
        logger.info(f"✅ Compression completed: {len(combined)} files processed")
        return combined
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """獲取集群狀態"""
        try:
            resources = ray.cluster_resources()
            available = ray.available_resources()
            
            return {
                'total_cpus': resources.get('CPU', 0),
                'available_cpus': available.get('CPU', 0),
                'total_memory_gb': resources.get('memory', 0) / (1024**3),
                'nodes': len(ray.nodes()),
                'status': 'active' if ray.is_initialized() else 'inactive'
            }
        except Exception as e:
            logger.error(f"Could not get cluster status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def shutdown(self) -> None:
        """關閉 Ray"""
        if self.is_initialized and ray.is_initialized():
            ray.shutdown()
            self.is_initialized = False
            logger.info("✅ Ray distributed engine shut down")
    
    def __del__(self):
        """析構函數"""
        self.shutdown()
