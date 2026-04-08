"""
分形遞歸 核心模塊
使用 Ray Actor 模式實現分佈式計算
"""

import ray
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from .fractal_dim import FractalDim
from .recursive_engine import RecursiveEngine
from .scale_analyzer import ScaleAnalyzer
from .self_similarity import SelfSimilarity
from .iterated_function import IteratedFunction

__all__ = ['FractalrecursionActor'] + [FractalDim, RecursiveEngine, ScaleAnalyzer, SelfSimilarity, IteratedFunction]


@ray.remote
class FractalrecursionActor:
    """
    分形遞歸 Ray Actor
    
    功能：
    - 分佈式數據處理
    - 任務執行和協調
    - 度量收集
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 分形遞歸 Actor
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.is_active = False
        self.execution_count = 0
        self.error_count = 0
        self.created_at = datetime.now()
        
        # 初始化子模組
        self.fractal_dim = FractalDim()
        self.recursive_engine = RecursiveEngine()
        self.scale_analyzer = ScaleAnalyzer()
        self.self_similarity = SelfSimilarity()
        self.iterated_function = IteratedFunction()
        
        logger.info(f"分形遞歸 Actor initialized")
    
    def initialize(self) -> Dict[str, Any]:
        """初始化 Actor"""
        try:
            self.is_active = True
            return {"status": "success", "actor": "分形遞歸"}
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def process(self, data: Any) -> Dict[str, Any]:
        """
        處理數據
        
        Args:
            data: 輸入數據
            
        Returns:
            處理結果
        """
        if not self.is_active:
            return {"status": "inactive"}
        
        try:
            self.execution_count += 1
            # 這裡添加具體的數據處理邏輯
            result = {"status": "success", "execution_id": self.execution_count}
            return result
        except Exception as e:
            self.error_count += 1
            logger.error(f"Processing error: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """獲取 Actor 狀態"""
        return {
            "is_active": self.is_active,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "created_at": self.created_at.isoformat(),
        }
    

    def run_cycle(self, input_data=None):
        """
        標準循環處理方法
        
        Args:
            input_data: 輸入數據
            
        Returns:
            處理結果字典
        """
        import numpy as np
        
        try:
            if input_data is None:
                # 生成示例數據
                input_data = np.random.rand(10)
            
            # 將 numpy array 轉換為可序列化的格式
            if isinstance(input_data, np.ndarray):
                input_data = input_data.tolist()
            
            # 調用 process 方法
            result = self.process(input_data)
            
            return {
                "status": "success",
                "result": result,
                "is_active": self.is_active
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "is_active": self.is_active
            }

    def shutdown(self) -> Dict[str, Any]:
        """關閉 Actor"""
        self.is_active = False
        return {
            "status": "shutdown",
            "total_executions": self.execution_count,
            "total_errors": self.error_count
        }
