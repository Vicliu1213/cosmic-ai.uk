"""
Binance API Configuration
Binance API 相关配置
"""

from typing import Dict, Any, Optional


class BinanceConfig:
    """Binance API 配置"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化 Binance 配置
        
        Args:
            config_dict: 包含 Binance 配置的字典
        """
        self._config = config_dict or {}
    
    @property
    def api_key(self) -> str:
        """获取 API Key"""
        return self._config.get('api_key', '')
    
    @property
    def api_secret(self) -> str:
        """获取 API Secret"""
        return self._config.get('api_secret', '')
    
    def is_configured(self) -> bool:
        """检查是否已正确配置"""
        return bool(self.api_key and self.api_secret)


__all__ = ['BinanceConfig']
