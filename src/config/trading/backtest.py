"""
Backtest Configuration
回测相关配置
"""

from typing import Dict, Any, Optional
from datetime import datetime


class BacktestConfig:
    """回测配置"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化回测配置
        
        Args:
            config_dict: 包含回测配置的字典
        """
        self._config = config_dict or {}
    
    @property
    def enabled(self) -> bool:
        """获取是否启用回测"""
        return self._config.get('enabled', False)
    
    @property
    def start_date(self) -> str:
        """获取回测开始日期"""
        return self._config.get('start_date', '')
    
    @property
    def end_date(self) -> str:
        """获取回测结束日期"""
        return self._config.get('end_date', '')
    
    @property
    def initial_capital(self) -> float:
        """获取初始资金"""
        return self._config.get('initial_capital', 10000.0)
    
    @property
    def commission(self) -> float:
        """获取手续费百分比"""
        return self._config.get('commission', 0.001)
    
    def get(self, key: str, default=None):
        """获取任意回测配置值"""
        return self._config.get(key, default)


__all__ = ['BacktestConfig']
