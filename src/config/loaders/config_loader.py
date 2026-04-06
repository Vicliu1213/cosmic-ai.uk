"""
Configuration Loader Module
配置加载模块 - 处理YAML配置文件和环境变量的加载和合并
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self):
        """初始化配置加载器"""
        # 加载环境变量 (使用 override=True 确保 .env 中的设置能覆盖当前进程的环境变量)
        load_dotenv(override=True)
    
    def load_from_yaml(self, file_path: Path) -> Dict[str, Any]:
        """
        从YAML文件加载配置
        
        Args:
            file_path: YAML文件路径
            
        Returns:
            配置字典
        """
        if not file_path.exists():
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config if config else {}
    
    def load_config(self, config_path: Optional[Path] = None, 
                   example_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 主配置文件路径
            example_path: 示例配置文件路径
            
        Returns:
            配置字典
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yaml"
        if example_path is None:
            example_path = Path(__file__).parent.parent.parent / "config.example.yaml"
        
        # 优先加载主配置文件，如果不存在则加载示例配置
        if config_path.exists():
            config = self.load_from_yaml(config_path)
        elif example_path.exists():
            config = self.load_from_yaml(example_path)
        else:
            config = {}
        
        return config
    
    def override_from_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从环境变量覆盖配置
        
        Args:
            config: 原始配置字典
            
        Returns:
            更新后的配置字典
        """
        # Initialize sections if missing
        for section in ['binance', 'deepseek', 'redis', 'llm']:
            if section not in config or config[section] is None:
                config[section] = {}

        # Binance
        if os.getenv('BINANCE_API_KEY'):
            config['binance']['api_key'] = os.getenv('BINANCE_API_KEY')
        # Support both BINANCE_API_SECRET (legacy) and BINANCE_SECRET_KEY (current docs/UI)
        binance_secret = os.getenv('BINANCE_API_SECRET') or os.getenv('BINANCE_SECRET_KEY')
        if binance_secret:
            config['binance']['api_secret'] = binance_secret
        
        # DeepSeek (向后兼容)
        if os.getenv('DEEPSEEK_API_KEY'):
            config['deepseek']['api_key'] = os.getenv('DEEPSEEK_API_KEY')
        
        # Redis
        if os.getenv('REDIS_HOST'):
            config['redis']['host'] = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PORT'):
            config['redis']['port'] = int(os.getenv('REDIS_PORT'))
        
        # LLM 多提供商支持
        if 'llm' not in config:
            config['llm'] = {}
        
        # API Keys for each provider
        # 支持 ANTHROPIC_API_KEY 作为 CLAUDE_API_KEY 的别名（优先级更高）
        claude_api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
        
        llm_api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'deepseek': os.getenv('DEEPSEEK_API_KEY'),
            'claude': claude_api_key,
            'qwen': os.getenv('QWEN_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY'),
            'kimi': os.getenv('KIMI_API_KEY'),
            'minimax': os.getenv('MINIMAX_API_KEY'),
            'glm': os.getenv('GLM_API_KEY'),
        }
        config['llm']['api_keys'] = {k: v for k, v in llm_api_keys.items() if v}

        # Provider/model override via environment
        llm_provider = os.getenv('LLM_PROVIDER')
        if llm_provider:
            config['llm']['provider'] = llm_provider.lower()

        llm_model = os.getenv('LLM_MODEL') or os.getenv('DEEPSEEK_MODEL')
        if llm_model:
            config['llm']['model'] = llm_model
        
        # Custom base URL (for proxies)
        # 支持 ANTHROPIC_BASE_URL 作为 LLM_BASE_URL 的别名（优先级更高）
        base_url = os.getenv('ANTHROPIC_BASE_URL') or os.getenv('LLM_BASE_URL')
        if base_url:
            config['llm']['base_url'] = base_url
        
        return config


__all__ = ['ConfigLoader']
