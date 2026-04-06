"""
Risk Management Configuration
风险管理相关配置
"""

from typing import Dict, Any, Optional


class RiskConfig:
    """风险管理配置"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化风险管理配置
        
        Args:
            config_dict: 包含风险管理配置的字典
        """
        self._config = config_dict or {}
    
    @property
    def max_drawdown_pct(self) -> float:
        """获取最大回撤百分比"""
        return self._config.get('max_drawdown_pct', 10.0)
    
    @property
    def max_position_size(self) -> float:
        """获取最大仓位大小"""
        return self._config.get('max_position_size', 100.0)
    
    @property
    def stop_loss_pct(self) -> float:
        """获取止损百分比"""
        return self._config.get('stop_loss_pct', 2.0)
    
    @property
    def take_profit_pct(self) -> float:
        """获取止盈百分比"""
        return self._config.get('take_profit_pct', 5.0)
    
    @property
    def max_consecutive_losses(self) -> int:
        """获取最大连续亏损次数"""
        return self._config.get('max_consecutive_losses', 5)
    
    def get(self, key: str, default=None):
        """获取任意风险配置值"""
        return self._config.get(key, default)


__all__ = ['RiskConfig']
