"""
API Keys Configuration Module
API 密钥相关配置 - 管理各类 LLM 和 Binance API 密钥
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from .binance import BinanceConfig
from .llm import LLMConfig

load_dotenv(override=True)


class APIKeysConfig:
    """API密钥配置管理器"""
    
    # LLM 提供商列表
    SUPPORTED_LLM_PROVIDERS = [
        'openai', 'deepseek', 'claude', 'qwen', 
        'gemini', 'kimi', 'minimax', 'glm'
    ]
    
    def __init__(self, config_dict: Optional[Dict] = None):
        """
        初始化 API 密钥配置
        
        Args:
            config_dict: 从配置文件读取的字典
        """
        self._config = config_dict or {}
    
    def get_binance_keys(self) -> Dict[str, str]:
        """获取 Binance API 密钥"""
        binance_config = self._config.get('binance', {})
        return {
            'api_key': binance_config.get('api_key', ''),
            'api_secret': binance_config.get('api_secret', ''),
        }
    
    def get_deepseek_key(self) -> str:
        """获取 DeepSeek API 密钥"""
        return self._config.get('deepseek', {}).get('api_key', '')
    
    def get_llm_config(self) -> Dict:
        """获取 LLM 配置"""
        return self._config.get('llm', {})
    
    def get_llm_api_keys(self) -> Dict[str, str]:
        """获取所有 LLM API 密钥"""
        llm_config = self.get_llm_config()
        return llm_config.get('api_keys', {})
    
    def get_llm_provider(self) -> str:
        """获取当前 LLM 提供商"""
        llm_config = self.get_llm_config()
        return llm_config.get('provider', 'deepseek')
    
    def get_llm_model(self) -> str:
        """获取当前 LLM 模型"""
        llm_config = self.get_llm_config()
        return llm_config.get('model', '')
    
    def get_llm_base_url(self) -> Optional[str]:
        """获取 LLM 自定义基础 URL"""
        llm_config = self.get_llm_config()
        return llm_config.get('base_url')
    
    def validate_binance_keys(self) -> bool:
        """验证 Binance 密钥是否存在"""
        keys = self.get_binance_keys()
        return bool(keys.get('api_key') and keys.get('api_secret'))
    
    def validate_llm_config(self) -> bool:
        """验证 LLM 配置是否有效"""
        provider = self.get_llm_provider()
        model = self.get_llm_model()
        api_keys = self.get_llm_api_keys()
        
        return (provider in self.SUPPORTED_LLM_PROVIDERS and 
                bool(model) and 
                bool(api_keys.get(provider)))


__all__ = ['APIKeysConfig', 'BinanceConfig', 'LLMConfig']
