"""
AI Trader - 配置管理模块
Configuration Management Module for Cosmic AI Trading System

Classes:
  - Config: 主配置管理器 (Singleton Pattern)
  
Functions:
  - get_config(): 获取全局配置实例
  
Submodules:
  - loaders.config_loader: 配置加载器，处理YAML和环境变量
  - api_keys: API密钥相关配置 (Binance, LLM等)
  - trading: 交易相关配置 (交易参数、风险管理、回测)
  - infrastructure: 基础设施配置 (Redis、日志)
  - templates: 提示词模板
  - schemas: 配置数据验证模式
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .loaders.config_loader import ConfigLoader
from .api_keys import APIKeysConfig, BinanceConfig, LLMConfig
from .trading import TradingConfig, RiskConfig, BacktestConfig
from .infrastructure import RedisConfig, LoggingConfig


class Config:
    """配置管理类 - Singleton 模式"""
    
    _instance = None
    _config_dict: Dict[str, Any] = {}
    
    # 配置组件
    api_keys: APIKeysConfig = None
    binance: BinanceConfig = None
    llm: LLMConfig = None
    trading: TradingConfig = None
    risk: RiskConfig = None
    backtest: BacktestConfig = None
    redis: RedisConfig = None
    logging: LoggingConfig = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件并初始化所有配置组件"""
        # 使用 ConfigLoader 加载配置
        loader = ConfigLoader()
        self._config_dict = loader.load_config()
        self._config_dict = loader.override_from_env(self._config_dict)
        
        # 初始化所有配置组件
        self.api_keys = APIKeysConfig(self._config_dict)
        self.binance = BinanceConfig(self._config_dict.get('binance', {}))
        self.llm = LLMConfig(self._config_dict.get('llm', {}))
        self.trading = TradingConfig(self._config_dict.get('trading', {}))
        self.risk = RiskConfig(self._config_dict.get('risk', {}))
        self.backtest = BacktestConfig(self._config_dict.get('backtest', {}))
        self.redis = RedisConfig(self._config_dict.get('redis', {}))
        self.logging = LoggingConfig(self._config_dict.get('logging', {}))
    
    def get(self, key_path: str, default=None):
        """
        获取配置值
        key_path: 使用点分隔的路径，如 'binance.api_key'
        """
        keys = key_path.split('.')
        value = self._config_dict
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def reload(self) -> bool:
        """重新加载配置文件"""
        try:
            self._load_config()
            return True
        except Exception as e:
            print(f"Error reloading config: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """获取整个配置字典"""
        return self._config_dict.copy()


# 全局配置实例
config = Config()


# 导出配置相关的类和工具函数
def get_config() -> Config:
    """
    获取全局配置实例
    
    Returns:
        Config: 全局配置单例
    """
    return config


def reload_config() -> bool:
    """
    重新加载配置文件
    
    Returns:
        bool: 是否成功重新加载
    """
    return config.reload()


# 导出清单
__all__ = [
    'Config',
    'config',
    'get_config',
    'reload_config',
    'APIKeysConfig',
    'BinanceConfig',
    'LLMConfig',
    'TradingConfig',
    'RiskConfig',
    'BacktestConfig',
    'RedisConfig',
    'LoggingConfig',
]
