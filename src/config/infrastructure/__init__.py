"""
Infrastructure Configuration Module
基础设施相关配置 - Redis、日志等
"""

from typing import Dict, Any, Optional


class RedisConfig:
    """Redis 配置"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化 Redis 配置
        
        Args:
            config_dict: 包含 Redis 配置的字典
        """
        self._config = config_dict or {}
    
    @property
    def host(self) -> str:
        """获取 Redis 主机"""
        return self._config.get('host', 'localhost')
    
    @property
    def port(self) -> int:
        """获取 Redis 端口"""
        return self._config.get('port', 6379)
    
    @property
    def db(self) -> int:
        """获取 Redis 数据库号"""
        return self._config.get('db', 0)
    
    @property
    def password(self) -> Optional[str]:
        """获取 Redis 密码"""
        return self._config.get('password')
    
    def get_connection_string(self) -> str:
        """获取 Redis 连接字符串"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.host and self.port)


class LoggingConfig:
    """日志配置"""
    
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化日志配置
        
        Args:
            config_dict: 包含日志配置的字典
        """
        self._config = config_dict or {}
    
    @property
    def level(self) -> str:
        """获取日志级别"""
        return self._config.get('level', 'INFO')
    
    @property
    def format(self) -> str:
        """获取日志格式"""
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        return self._config.get('format', default_format)
    
    @property
    def file(self) -> Optional[str]:
        """获取日志文件路径"""
        return self._config.get('file')
    
    def is_valid_level(self) -> bool:
        """检查日志级别是否有效"""
        return self.level in self.LOG_LEVELS
    
    def get(self, key: str, default=None):
        """获取任意日志配置值"""
        return self._config.get(key, default)


__all__ = ['RedisConfig', 'LoggingConfig']
