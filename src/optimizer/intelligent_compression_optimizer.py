#!/usr/bin/env python3
"""
智能能源與壓縮優化系統
集成了離線處理、預約機制、經驗決策和量子損耗節省
"""

import numpy as np
import gzip
import pickle
import json
import os
import time
from typing import Dict, List, Tuple, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import threading
import queue
import hashlib

class CompressionLevel(Enum):
    """壓縮級別枚舉"""
    OFFLINE_FAST = "offline_fast"       # 離線快速壓縮
    OFFLINE_BALANCED = "offline_balanced" # 離線平衡壓縮  
    OFFLINE_MAXIMUM = "offline_maximum"   # 離線最大壓縮
    REALTIME_ADAPTIVE = "realtime_adaptive" # 實時自適應壓縮

class EnergyMode(Enum):
    """能源模式枚舉"""
    POWER_SAVING = "power_saving"     # 節能模式
    BALANCED = "balanced"              # 平衡模式
    PERFORMANCE = "performance"          # 性能模式
    QUANTUM_EFFICIENT = "quantum_efficient" # 量子高效模式

class ProcessingStatus(Enum):
    """處理狀態枚舉"""
    IDLE = "idle"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

@dataclass
class CompressionTask:
    """壓縮任務"""
    task_id: str
    file_path: str
    priority: int
    compression_level: CompressionLevel
    energy_mode: EnergyMode
    scheduled_time: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_size_original: int = 0
    file_size_compressed: int = 0
    energy_consumed: float = 0.0
    quantum_operations_used: int = 0

@dataclass
class PerformanceMetrics:
    """性能指標"""
    compression_ratio: float
    compression_speed: float  # MB/s
    energy_efficiency: float  # MB/kWh
    quantum_coherence: float
    cache_hit_rate: float
    cost_savings: float  # $/GB

class ExperienceDecisionEngine:
    """經驗決策引擎"""
    
    def __init__(self, experience_db_path: str = "data/experience_db.json"):
        self.experience_db_path = experience_db_path
        self.experience_data = self._load_experience()
        self.logger = logging.getLogger(__name__)
        
    def _load_experience(self) -> Dict[str, Any]:
        """載入經驗數據庫"""
        try:
            if os.path.exists(self.experience_db_path):
                with open(self.experience_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            self.logger.warning("Failed to load experience database, starting fresh")
            
        return {
            'file_type_patterns': {},
            'compression_strategies': {},
            'energy_optimization': {},
            'quantum_efficiency': {},
            'performance_history': [],
            'decision_outcomes': []
        }
        
    def record_outcome(self, 
                      context: Dict[str, Any],
                      decision: Dict[str, Any],
                      outcome: Dict[str, Any]) -> None:
        """記錄決策結果"""
        experience_entry = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'decision': decision,
            'outcome': outcome,
            'success': outcome.get('success', False),
            'performance_gain': outcome.get('performance_gain', 0.0)
        }
        
        self.experience_data['decision_outcomes'].append(experience_entry)
        
        # 限制數據庫大小
        if len(self.experience_data['decision_outcomes']) > 1000:
            self.experience_data['decision_outcomes'] = self.experience_data['decision_outcomes'][-500:]
            
        self._save_experience()
        
    def _save_experience(self) -> None:
        """保存經驗數據庫"""
        try:
            os.makedirs(os.path.dirname(self.experience_db_path), exist_ok=True)
            with open(self.experience_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.experience_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save experience database: {e}")
            
    def recommend_compression_strategy(self, 
                                   file_info: Dict[str, Any],
                                   constraints: Dict[str, Any]) -> Dict[str, Any]:
        """推薦壓縮策略"""
        file_type = file_info.get('type', 'unknown')
        file_size = file_info.get('size', 0)
        available_energy = constraints.get('energy_budget', 1.0)
        time_constraint = constraints.get('time_limit', None)
        
        # 基於經驗的相似文件分析
        similar_cases = self._find_similar_cases(file_type, file_size)
        
        if similar_cases:
            # 選擇最佳歷史策略
            best_case = max(similar_cases, key=lambda c: c.get('performance_gain', 0))
            
            recommendation = {
                'strategy': 'experiential',
                'compression_level': best_case.get('compression_level', CompressionLevel.OFFLINE_BALANCED.value),
                'energy_mode': best_case.get('energy_mode', EnergyMode.QUANTUM_EFFICIENT.value),
                'confidence': min(len(similar_cases) * 0.1, 0.9),
                'expected_compression_ratio': best_case.get('compression_ratio', 0.7),
                'expected_energy_savings': best_case.get('energy_savings', 0.3)
            }
        else:
            # 使用默認策略
            recommendation = self._default_strategy(file_type, file_size, available_energy, time_constraint)
            
        return recommendation
        
    def _find_similar_cases(self, 
                           file_type: str,
                           file_size: int) -> List[Dict[str, Any]]:
        """查找相似案例"""
        similar_cases = []
        
        for outcome in self.experience_data['decision_outcomes']:
            context = outcome.get('context', {})
            outcome_result = outcome.get('outcome', {})
            
            if (context.get('file_type') == file_type and
                abs(context.get('file_size', 0) - file_size) / file_size < 0.5 and
                outcome.get('success', False)):
                
                similar_cases.append({
                    'compression_level': outcome.get('decision', {}).get('compression_level'),
                    'energy_mode': outcome.get('decision', {}).get('energy_mode'),
                    'compression_ratio': outcome_result.get('compression_ratio', 0.5),
                    'energy_savings': outcome_result.get('energy_savings', 0.2),
                    'performance_gain': outcome.get('performance_gain', 0.0)
                })
                
        return similar_cases[:10]  # 返回最近10個相似案例
        
    def _default_strategy(self, 
                        file_type: str,
                        file_size: int,
                        energy_budget: float,
                        time_limit: Optional[datetime]) -> Dict[str, Any]:
        """默認策略推薦"""
        # 基於文件類型的默認配置
        default_configs = {
            'text': {
                'compression_level': CompressionLevel.OFFLINE_BALANCED.value,
                'energy_mode': EnergyMode.QUANTUM_EFFICIENT.value
            },
            'image': {
                'compression_level': CompressionLevel.OFFLINE_MAXIMUM.value,
                'energy_mode': EnergyMode.BALANCED.value
            },
            'video': {
                'compression_level': CompressionLevel.OFFLINE_FAST.value,
                'energy_mode': EnergyMode.POWER_SAVING.value
            },
            'data': {
                'compression_level': CompressionLevel.OFFLINE_BALANCED.value,
                'energy_mode': EnergyMode.QUANTUM_EFFICIENT.value
            }
        }
        
        config = default_configs.get(file_type, default_configs['data'])
        
        # 考慮約束條件
        if energy_budget < 0.3:
            config['energy_mode'] = EnergyMode.POWER_SAVING.value
            
        if time_limit and (time_limit - datetime.now()).total_seconds() < 300:  # 5分鐘內
            config['compression_level'] = CompressionLevel.OFFLINE_FAST.value
            
        return {
            'strategy': 'default',
            **config,
            'confidence': 0.5,
            'expected_compression_ratio': 0.7,
            'expected_energy_savings': 0.25
        }

class QuantumLossOptimizer:
    """量子損耗優化器"""
    
    def __init__(self):
        self.quantum_coherence_history = []
        self.operation_cost_cache = {}
        self.logger = logging.getLogger(__name__)
        
    def calculate_quantum_efficiency(self, 
                                  coherence_before: float,
                                  coherence_after: float,
                                  operations_count: int) -> float:
        """計算量子效率"""
        if coherence_before == 0:
            return 0.0
            
        coherence_preservation = coherence_after / coherence_before
        operation_efficiency = min(1.0, operations_count / 10.0)  # 標準化到10個操作
        
        return coherence_preservation * operation_efficiency
        
    def minimize_quantum_loss(self, 
                            operations: List[Dict[str, Any]],
                            coherence_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """最小化量子損耗"""
        optimized_operations = []
        current_coherence = 1.0
        
        for op in operations:
            op_type = op.get('type', 'classical')
            priority = op.get('priority', 1)
            
            # 計算操作的量子損耗
            if op_type == 'quantum':
                loss_factor = 0.1 * priority  # 量子操作有損耗
                cost_factor = 1.5  # 量子操作成本更高
            else:
                loss_factor = 0.01 * priority  # 經典操作損耗小
                cost_factor = 1.0
                
            # 檢查相干性閾值
            if current_coherence * (1 - loss_factor) < coherence_threshold:
                # 改用經典操作
                op['optimized_type'] = 'classical_fallback'
                op['coherence_impact'] = -loss_factor * 0.5
                cost_factor = 1.0
            else:
                op['optimized_type'] = op_type
                op['coherence_impact'] = -loss_factor
                
            current_coherence *= (1 + op['coherence_impact'])
            op['energy_cost'] = op.get('energy_cost', 1.0) * cost_factor
            
            optimized_operations.append(op)
            
        return optimized_operations
        
    def estimate_savings(self, 
                        optimized_operations: List[Dict[str, Any]]) -> Dict[str, float]:
        """估算節省"""
        quantum_operations = sum(1 for op in optimized_operations 
                             if op.get('optimized_type') == 'quantum')
        classical_operations = len(optimized_operations) - quantum_operations
        
        # 量子操作節省
        quantum_savings = quantum_operations * 0.3  # 30%節省
        
        # 相干性維護節省
        coherence_savings = sum(op.get('energy_cost', 0) * 0.2 
                               for op in optimized_operations
                               if op.get('optimized_type') == 'classical_fallback')
        
        return {
            'quantum_operation_savings': quantum_savings,
            'coherence_savings': coherence_savings,
            'total_savings': quantum_savings + coherence_savings,
            'efficiency_gain': (quantum_operations + classical_operations) / max(quantum_operations, 1)
        }

class IntelligentCompressionOptimizer:
    """智能壓縮優化器主類"""
    
    def __init__(self, config_path: str = "config/compression_optimizer.yaml"):
        self.config = self._load_config(config_path)
        self.experience_engine = ExperienceDecisionEngine()
        self.quantum_optimizer = QuantumLossOptimizer()
        self.task_queue = queue.PriorityQueue()
        self.cache = {}
        self.processing_threads = []
        self.profit_tracker = {}
        self.logger = logging.getLogger(__name__)
        self.running = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入配置"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            'compression': {
                'offline_batch_size': 100,
                'cache_size': 1000,
                'max_workers': 4,
                'energy_optimization': True
            },
            'quantum': {
                'coherence_threshold': 0.8,
                'max_concurrent_quantum_ops': 2,
                'efficiency_target': 0.9
            },
            'profit': {
                'storage_cost_per_gb': 0.023,  # $/GB/month
                'energy_cost_per_kwh': 0.12,   # $/kWh
                'quantum_op_cost': 0.001,       # $/operation
                'target_profit_margin': 0.3
            }
        }
        
    def start_optimization_service(self) -> None:
        """啟動優化服務"""
        self.running = True
        
        # 啟動處理線程
        for i in range(self.config['compression']['max_workers']):
            thread = threading.Thread(
                target=self._processing_worker,
                name=f"CompressionWorker-{i}",
                daemon=True
            )
            thread.start()
            self.processing_threads.append(thread)
            
        self.logger.info(f"Started optimization service with {len(self.processing_threads)} workers")
        
    def stop_optimization_service(self) -> None:
        """停止優化服務"""
        self.running = False
        
        # 等待所有線程完成
        for thread in self.processing_threads:
            thread.join(timeout=10)
            
        self.logger.info("Optimization service stopped")
        
    def schedule_compression(self, 
                           file_path: str,
                           priority: int = 5,
                           scheduled_time: Optional[datetime] = None) -> str:
        """調度壓縮任務"""
        # 分析文件信息
        file_info = self._analyze_file(file_path)
        
        # 生成任務ID
        task_id = hashlib.md5(f"{file_path}_{time.time()}".encode()).hexdigest()
        
        # 獲取推薦策略
        constraints = {
            'energy_budget': self._get_current_energy_budget(),
            'time_limit': scheduled_time
        }
        
        recommendation = self.experience_engine.recommend_compression_strategy(
            file_info, constraints
        )
        
        # 創建任務
        task = CompressionTask(
            task_id=task_id,
            file_path=file_path,
            priority=priority,
            compression_level=CompressionLevel(recommendation['compression_level']),
            energy_mode=EnergyMode(recommendation['energy_mode']),
            scheduled_time=scheduled_time
        )
        
        # 檢查緩存
        cache_key = self._generate_cache_key(file_path, recommendation)
        if cache_key in self.cache:
            task.status = ProcessingStatus.CACHED
            self.logger.info(f"Task {task_id} found in cache")
            return task_id
            
        # 添加到隊列
        self.task_queue.put((-priority, task))
        
        self.logger.info(f"Scheduled compression task {task_id} for {file_path}")
        return task_id
        
    def _processing_worker(self) -> None:
        """處理工作線程"""
        while self.running:
            try:
                priority, task = self.task_queue.get(timeout=1)
                
                # 檢查是否需要延遲
                if task.scheduled_time and datetime.now() < task.scheduled_time:
                    sleep_time = (task.scheduled_time - datetime.now()).total_seconds()
                    time.sleep(sleep_time)
                    
                # 執行壓縮
                result = self._execute_compression_task(task)
                
                # 記錄經驗
                self.experience_engine.record_outcome(
                    context={
                        'file_path': task.file_path,
                        'file_type': self._analyze_file(task.file_path).get('type'),
                        'file_size': self._analyze_file(task.file_path).get('size', 0),
                        'priority': task.priority
                    },
                    decision={
                        'compression_level': task.compression_level.value,
                        'energy_mode': task.energy_mode.value
                    },
                    outcome=result
                )
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Processing worker error: {e}")
                
    def _execute_compression_task(self, task: CompressionTask) -> Dict[str, Any]:
        """執行壓縮任務"""
        start_time = time.time()
        task.status = ProcessingStatus.PROCESSING
        task.started_at = datetime.now()
        
        try:
            # 讀取文件
            with open(task.file_path, 'rb') as f:
                data = f.read()
                
            task.file_size_original = len(data)
            
            # 根據壓縮級別選擇策略
            if task.compression_level == CompressionLevel.OFFLINE_FAST:
                compressed_data = self._fast_compression(data)
            elif task.compression_level == CompressionLevel.OFFLINE_BALANCED:
                compressed_data = self._balanced_compression(data, task.energy_mode)
            elif task.compression_level == CompressionLevel.OFFLINE_MAXIMUM:
                compressed_data = self._maximum_compression(data, task.energy_mode)
            elif task.compression_level == CompressionLevel.REALTIME_ADAPTIVE:
                compressed_data = self._adaptive_compression(data, task.energy_mode)
            else:
                compressed_data = data  # 不壓縮
                
            task.file_size_compressed = len(compressed_data)
            
            # 計算能源消耗
            energy_consumed = self._calculate_energy_consumption(
                task.file_size_original, 
                task.file_size_compressed,
                task.energy_mode
            )
            task.energy_consumed = energy_consumed
            
            # 計算量子操作次數
            quantum_operations = self._count_quantum_operations(task.compression_level, task.energy_mode)
            task.quantum_operations_used = quantum_operations
            
            # 保存壓縮文件
            output_path = task.file_path + '.compressed'
            with open(output_path, 'wb') as f:
                f.write(compressed_data)
                
            # 計算性能指標
            execution_time = time.time() - start_time
            compression_ratio = task.file_size_compressed / task.file_size_original
            compression_speed = (task.file_size_original / 1024 / 1024) / execution_time  # MB/s
            
            # 計算盈利
            profit = self._calculate_profit(task, compression_ratio, energy_consumed)
            
            task.status = ProcessingStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # 更新緩存
            cache_key = self._generate_cache_key(task.file_path, {
                'compression_level': task.compression_level.value,
                'energy_mode': task.energy_mode.value
            })
            self.cache[cache_key] = {
                'output_path': output_path,
                'compression_ratio': compression_ratio,
                'energy_consumed': energy_consumed,
                'timestamp': datetime.now()
            }
            
            return {
                'success': True,
                'task_id': task.task_id,
                'compression_ratio': compression_ratio,
                'compression_speed': compression_speed,
                'energy_consumed': energy_consumed,
                'quantum_operations_used': quantum_operations,
                'execution_time': execution_time,
                'profit': profit,
                'output_path': output_path
            }
            
        except Exception as e:
            task.status = ProcessingStatus.FAILED
            task.completed_at = datetime.now()
            
            return {
                'success': False,
                'task_id': task.task_id,
                'error': str(e)
            }
            
    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析文件信息"""
        try:
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            
            # 簡單的文件類型檢測
            _, ext = os.path.splitext(file_path)
            file_type = ext.lower().lstrip('.')
            
            if file_type in ['txt', 'md', 'py', 'js', 'json', 'yaml']:
                file_type = 'text'
            elif file_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                file_type = 'image'
            elif file_type in ['mp4', 'avi', 'mov', 'mkv']:
                file_type = 'video'
            else:
                file_type = 'data'
                
            return {
                'path': file_path,
                'size': file_size,
                'type': file_type,
                'extension': ext
            }
        except Exception:
            return {'path': file_path, 'size': 0, 'type': 'unknown', 'extension': ''}
            
    def _generate_cache_key(self, file_path: str, params: Dict[str, Any]) -> str:
        """生成緩存鍵"""
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(f"{file_path}_{params_str}".encode()).hexdigest()
        
    def _fast_compression(self, data: bytes) -> bytes:
        """快速壓縮"""
        return gzip.compress(data, compresslevel=1)
        
    def _balanced_compression(self, data: bytes, energy_mode: EnergyMode) -> bytes:
        """平衡壓縮（考慮能源模式）"""
        if energy_mode == EnergyMode.QUANTUM_EFFICIENT:
            # 使用量子優化的壓縮參數
            compresslevel = 6
        elif energy_mode == EnergyMode.POWER_SAVING:
            compresslevel = 4
        elif energy_mode == EnergyMode.PERFORMANCE:
            compresslevel = 8
        else:  # BALANCED
            compresslevel = 6
            
        return gzip.compress(data, compresslevel=compresslevel)
        
    def _maximum_compression(self, data: bytes, energy_mode: EnergyMode) -> bytes:
        """最大壓縮"""
        if energy_mode == EnergyMode.QUANTUM_EFFICIENT:
            # 最大壓縮但保持量子效率
            compresslevel = 9
        else:
            compresslevel = 9
            
        return gzip.compress(data, compresslevel=compresslevel)
        
    def _adaptive_compression(self, data: bytes, energy_mode: EnergyMode) -> bytes:
        """自適應壓縮"""
        # 基於數據特徵動態調整
        data_sample = data[:1024] if len(data) > 1024 else data
        entropy = self._calculate_entropy(data_sample)
        
        # 高熵數據使用更高壓縮級別
        if entropy > 7.0:
            compresslevel = 8
        else:
            compresslevel = 6
            
        # 考慮能源模式
        if energy_mode == EnergyMode.QUANTUM_EFFICIENT:
            compresslevel = min(compresslevel, 7)
        elif energy_mode == EnergyMode.POWER_SAVING:
            compresslevel = max(compresslevel - 2, 1)
            
        return gzip.compress(data, compresslevel=compresslevel)
        
    def _calculate_entropy(self, data: bytes) -> float:
        """計算數據熵"""
        if not data:
            return 0.0
            
        # 計算字節頻率
        byte_counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
        probabilities = byte_counts / len(data)
        
        # 移除零概率
        probabilities = probabilities[probabilities > 0]
        
        # 計算熵
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy
        
    def _calculate_energy_consumption(self, 
                                 original_size: int,
                                 compressed_size: int,
                                 energy_mode: EnergyMode) -> float:
        """計算能源消耗"""
        base_energy = (original_size + compressed_size) / 1024 / 1024 * 0.01  # 基礎能源
        
        # 能源模式調整
        mode_multipliers = {
            EnergyMode.POWER_SAVING: 0.7,
            EnergyMode.BALANCED: 1.0,
            EnergyMode.PERFORMANCE: 1.3,
            EnergyMode.QUANTUM_EFFICIENT: 0.85
        }
        
        return base_energy * mode_multipliers.get(energy_mode, 1.0)
        
    def _count_quantum_operations(self, 
                              compression_level: CompressionLevel,
                              energy_mode: EnergyMode) -> int:
        """計算量子操作次數"""
        base_count = {
            CompressionLevel.OFFLINE_FAST: 2,
            CompressionLevel.OFFLINE_BALANCED: 5,
            CompressionLevel.OFFLINE_MAXIMUM: 8,
            CompressionLevel.REALTIME_ADAPTIVE: 3
        }
        
        mode_multiplier = {
            EnergyMode.QUANTUM_EFFICIENT: 1.5,
            EnergyMode.BALANCED: 1.0,
            EnergyMode.PERFORMANCE: 0.8,
            EnergyMode.POWER_SAVING: 0.5
        }
        
        return int(base_count.get(compression_level, 3) * mode_multiplier.get(energy_mode, 1.0))
        
    def _calculate_profit(self, 
                      task: CompressionTask,
                      compression_ratio: float,
                      energy_consumed: float) -> float:
        """計算盈利"""
        profit_config = self.config['profit']
        
        # 存儲節省成本
        storage_savings = (1 - compression_ratio) * task.file_size_original / 1024 / 1024 / 1024 * profit_config['storage_cost_per_gb']
        
        # 能源成本
        energy_cost = energy_consumed * profit_config['energy_cost_per_kwh'] / 1000  # 假設單位轉換
        
        # 量子操作成本
        quantum_cost = task.quantum_operations_used * profit_config['quantum_op_cost']
        
        # 總成本
        total_cost = energy_cost + quantum_cost
        
        # 利潤
        profit = storage_savings - total_cost
        
        # 更新利潤追蹤
        self.profit_tracker[task.task_id] = {
            'timestamp': datetime.now().isoformat(),
            'storage_savings': storage_savings,
            'energy_cost': energy_cost,
            'quantum_cost': quantum_cost,
            'total_cost': total_cost,
            'profit': profit,
            'profit_margin': profit / (storage_savings + 1e-10)  # 避免除零
        }
        
        return profit
        
    def _get_current_energy_budget(self) -> float:
        """獲取當前能源預算"""
        # 模擬當前系統負載
        current_load = len(self.processing_threads) * 0.2  # 每個線程20%負載
        return max(0.3, 1.0 - current_load)  # 最少保留30%預算
        
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        # 計算隊列狀態
        queue_size = self.task_queue.qsize()
        
        # 計算績統計
        completed_tasks = len([t for t in self.profit_tracker.values() if t.get('profit', 0) > 0])
        total_profit = sum(t.get('profit', 0) for t in self.profit_tracker.values())
        avg_profit_margin = np.mean([t.get('profit_margin', 0) for t in self.profit_tracker.values()]) if self.profit_tracker else 0
        
        # 緩存統計
        cache_hit_rate = len(self.cache) / max(len(self.profit_tracker), 1)
        
        return {
            'service_running': self.running,
            'active_workers': len([t for t in self.processing_threads if t.is_alive()]),
            'queue_size': queue_size,
            'cache_size': len(self.cache),
            'cache_hit_rate': cache_hit_rate,
            'completed_tasks': completed_tasks,
            'total_profit': total_profit,
            'average_profit_margin': avg_profit_margin,
            'energy_efficiency': self._calculate_overall_energy_efficiency(),
            'quantum_coherence': self.quantum_optimizer.quantum_coherence_history[-1] if self.quantum_optimizer.quantum_coherence_history else 1.0,
            'experience_database_size': len(self.experience_engine.experience_data.get('decision_outcomes', []))
        }
        
    def _calculate_overall_energy_efficiency(self) -> float:
        """計算整體能源效率"""
        if not self.profit_tracker:
            return 1.0
            
        total_tasks = len(self.profit_tracker)
        efficient_tasks = len([t for t in self.profit_tracker.values() 
                             if t.get('profit', 0) > 0 and 
                                t.get('profit_margin', 0) > self.config['profit']['target_profit_margin']])
        
        return efficient_tasks / max(total_tasks, 1)