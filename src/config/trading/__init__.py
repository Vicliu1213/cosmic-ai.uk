"""
Trading Configuration Module
交易相关配置 - 包含交易参数、风险管理等
"""

from typing import Dict, Any, Optional


class TradingConfig:
    """交易配置管理器"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化交易配置
        
        Args:
            config_dict: 包含交易配置的字典
        """
        self._config = config_dict or {}
    
    @property
    def pair(self) -> str:
        """获取交易对"""
        return self._config.get('pair', 'BTCUSDT')
    
    @property
    def timeframe(self) -> str:
        """获取时间框架"""
        return self._config.get('timeframe', '5m')
    
    @property
    def leverage(self) -> float:
        """获取杠杆"""
        return self._config.get('leverage', 1.0)
    
    @property
    def position_size(self) -> float:
        """获取仓位大小"""
        return self._config.get('position_size', 0.1)
    
    def get(self, key: str, default=None):
        """获取任意交易配置值"""
        return self._config.get(key, default)


__all__ = ['TradingConfig']
