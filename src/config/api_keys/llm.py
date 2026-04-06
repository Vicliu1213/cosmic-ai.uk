"""
LLM Providers Configuration
LLM 提供商相关配置 - 支持多个 LLM 服务商
"""

from typing import Dict, Any, Optional


class LLMConfig:
    """LLM 配置管理器"""
    
    SUPPORTED_PROVIDERS = [
        'openai', 'deepseek', 'claude', 'qwen',
        'gemini', 'kimi', 'minimax', 'glm'
    ]
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化 LLM 配置
        
        Args:
            config_dict: 包含 LLM 配置的字典
        """
        self._config = config_dict or {}
    
    @property
    def provider(self) -> str:
        """获取当前 LLM 提供商"""
        return self._config.get('provider', 'deepseek')
    
    @property
    def model(self) -> str:
        """获取当前使用的模型"""
        return self._config.get('model', '')
    
    @property
    def api_keys(self) -> Dict[str, str]:
        """获取所有 API 密钥"""
        return self._config.get('api_keys', {})
    
    @property
    def base_url(self) -> Optional[str]:
        """获取自定义基础 URL (用于代理)"""
        return self._config.get('base_url')
    
    def get_api_key(self, provider: Optional[str] = None) -> str:
        """
        获取指定提供商的 API 密钥
        
        Args:
            provider: 提供商名称，默认使用当前提供商
            
        Returns:
            API 密钥
        """
        if provider is None:
            provider = self.provider
        return self.api_keys.get(provider, '')
    
    def is_configured(self) -> bool:
        """检查 LLM 是否正确配置"""
        return (
            self.provider in self.SUPPORTED_PROVIDERS and
            bool(self.model) and
            bool(self.get_api_key())
        )
    
    def validate_provider(self, provider: str) -> bool:
        """检查提供商是否支持"""
        return provider in self.SUPPORTED_PROVIDERS


__all__ = ['LLMConfig']
