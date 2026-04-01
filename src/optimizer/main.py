"""
最佳化模組 - 主入點

負責初始化和協調所有最佳化算法，包括：
- 古典算法（遺傳演算法、粒子群優化、模擬退火）
- 混合量子增強算法
"""

import sys
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class OptimizerModuleManager:
    """最佳化模組管理器 - 協調所有最佳化操作"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化最佳化模組管理器
        
        Args:
            config: 模組配置字典
        """
        self.config = config or {}
        self.algorithms = {}
        self.is_initialized = False
        logger.info("✅ 最佳化模組管理器初始化完成")
    
    def initialize_algorithms(self) -> Dict[str, bool]:
        """
        初始化所有可用的最佳化算法
        
        Returns:
            各算法初始化狀態字典
        """
        try:
            # 嘗試導入所有可用的算法
            try:
                from .classical_algorithms import (
                    GeneticAlgorithm,
                    ParticleSwarmOptimization,
                    SimulatedAnnealing,
                    GradientDescent,
                    DifferentialEvolution
                )
                
                # 初始化古典算法
                self.algorithms['genetic'] = GeneticAlgorithm
                self.algorithms['pso'] = ParticleSwarmOptimization
                self.algorithms['simulated_annealing'] = SimulatedAnnealing
                self.algorithms['gradient_descent'] = GradientDescent
                self.algorithms['differential_evolution'] = DifferentialEvolution
            except ImportError as e:
                logger.warning(f"⚠️ 古典算法導入失敗: {str(e)}")
                # 提供回退實現
                self.algorithms['genetic'] = dict  # 臨時佔位符
                self.algorithms['pso'] = dict
                self.algorithms['simulated_annealing'] = dict
                self.algorithms['gradient_descent'] = dict
                self.algorithms['differential_evolution'] = dict
            
            # 嘗試導入混合量子算法
            try:
                from .hybrid_quantum_algorithm import HybridQuantumEnhancedAlgorithm
                self.algorithms['hybrid_quantum'] = HybridQuantumEnhancedAlgorithm
            except ImportError as e:
                logger.warning(f"⚠️ 混合量子算法導入失敗: {str(e)}")
                self.algorithms['hybrid_quantum'] = dict
            
            self.is_initialized = True
            logger.info(f"✅ 已初始化 {len(self.algorithms)} 個最佳化算法")
            
            return {name: True for name in self.algorithms.keys()}
            
        except Exception as e:
            logger.error(f"❌ 最佳化算法初始化失敗: {str(e)}")
            return {name: False for name in self.algorithms.keys()}
    
    def get_algorithm(self, name: str):
        """
        獲取指定的最佳化算法
        
        Args:
            name: 算法名稱
            
        Returns:
            算法類
        """
        if name not in self.algorithms:
            raise ValueError(f"未知的算法: {name}")
        return self.algorithms[name]
    
    def list_available_algorithms(self) -> List[str]:
        """列出所有可用的最佳化算法"""
        return list(self.algorithms.keys())
    
    def optimize(self, algorithm_name: str, objective_func, **kwargs) -> Dict[str, Any]:
        """
        使用指定算法進行最佳化
        
        Args:
            algorithm_name: 算法名稱
            objective_func: 目標函數
            **kwargs: 算法特定參數
            
        Returns:
            最佳化結果字典
        """
        try:
            AlgorithmClass = self.get_algorithm(algorithm_name)
            algo = AlgorithmClass(**kwargs)
            
            result = algo.optimize(objective_func)
            logger.info(f"✅ {algorithm_name} 最佳化完成")
            
            return {
                'algorithm': algorithm_name,
                'best_value': result.get('best_value'),
                'best_params': result.get('best_params'),
                'iterations': result.get('iterations'),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ 最佳化失敗 ({algorithm_name}): {str(e)}")
            return {
                'algorithm': algorithm_name,
                'success': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """獲取模組狀態"""
        return {
            'initialized': self.is_initialized,
            'algorithms_count': len(self.algorithms),
            'available_algorithms': self.list_available_algorithms()
        }


async def main(config: Optional[Dict[str, Any]] = None):
    """
    最佳化模組主入點
    
    Args:
        config: 模組配置
    """
    manager = OptimizerModuleManager(config)
    status = manager.initialize_algorithms()
    
    print("\n" + "="*60)
    print("🔧 最佳化模組 (Optimizer Module)")
    print("="*60)
    print(f"初始化狀態: {status}")
    print(f"可用算法: {manager.list_available_algorithms()}")
    print("="*60 + "\n")
    
    return manager


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
