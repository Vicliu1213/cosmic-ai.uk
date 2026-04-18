"""
Ray Actor 基礎類
所有理論模塊都會繼承這個基類
"""

import ray
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@ray.remote
class BaseCosmicActor(ABC):
    """
    宇宙引擎基礎 Ray Actor
    
    所有理論 Actor 的基類
    """
    
    def __init__(self, actor_name: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化基礎 Actor
        
        Args:
            actor_name: Actor 名稱
            config: 配置字典
        """
        self.actor_name = actor_name
        self.config = config or {}
        self.is_active = False
        self.execution_count = 0
        self.error_count = 0
        self.metrics = {}
        self.created_at = datetime.now()
        
        logger.info(f"BaseCosmicActor '{actor_name}' initialized")
    
    def initialize(self) -> Dict[str, Any]:
        """
        初始化 Actor
        
        Returns:
            初始化結果
        """
        self.is_active = True
        return {
            "status": "success",
            "actor": self.actor_name,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """獲取 Actor 狀態"""
        return {
            "actor_name": self.actor_name,
            "is_active": self.is_active,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "created_at": self.created_at.isoformat(),
            "metrics": self.metrics
        }
    
    @abstractmethod
    def process(self, data: Any) -> Dict[str, Any]:
        """
        抽象方法：處理數據
        
        Args:
            data: 輸入數據
            
        Returns:
            處理結果
        """
        pass
    
    def execute(self, data: Any) -> Dict[str, Any]:
        """
        執行處理
        
        Args:
            data: 輸入數據
            
        Returns:
            執行結果
        """
        try:
            self.execution_count += 1
            result = self.process(data)
            return {
                "status": "success",
                "actor": self.actor_name,
                "execution_id": self.execution_count,
                "result": result
            }
        except Exception as e:
            self.error_count += 1
            logger.error(f"Execution error in {self.actor_name}: {e}")
            return {
                "status": "error",
                "actor": self.actor_name,
                "error": str(e)
            }
    
    def shutdown(self) -> Dict[str, Any]:
        """關閉 Actor"""
        self.is_active = False
        return {
            "status": "shutdown",
            "actor": self.actor_name,
            "total_executions": self.execution_count,
            "total_errors": self.error_count
        }
