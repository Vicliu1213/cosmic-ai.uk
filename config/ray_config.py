#!/usr/bin/env python3
"""
Ray Configuration for Comic AI
Ray 分布式計算配置管理
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RayConfig:
    """Ray 配置管理類"""
    
    DEFAULT_CONFIG = {
        'cluster': {
            'num_cpus': None,  # None 表示自動檢測
            'num_gpus': 0,
            'memory_gb': None,  # None 表示自動檢測
            'dashboard': True,
            'temp_dir': str(Path.home() / '.ray_temp')
        },
        'performance': {
            'object_store_memory_gb': None,
            'redis_password': None,
            'resources': {}
        },
        'tuning': {
            'enable_object_reference_counting': True,
            'object_spilling_enabled': True,
            'object_spilling_config': {
                'type': 'filesystem',
                'params': {'directory_path': '/tmp/ray_spill'}
            }
        },
        'logging': {
            'level': 'INFO',
            'file_path': '/var/log/ray'
        },
        'distributed_computing': {
            'quantum_engine': {
                'use_distribution': True,
                'batch_size': 'auto',
                'workers': 'auto'
            },
            'data_manager': {
                'use_distribution': True,
                'compression_workers': 'auto',
                'parallel_batch_size': 'auto'
            },
            'genetic_algorithm': {
                'use_distribution': True,
                'population_distribution': 'balanced',
                'workers': 'auto'
            }
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化 Ray 配置
        
        Args:
            config_path: 配置文件路徑
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
            logger.info(f"✅ Ray config loaded from {config_path}")
        else:
            logger.info("✅ Using default Ray configuration")
    
    def load_config(self, config_path: str) -> None:
        """加載配置文件
        
        Args:
            config_path: YAML 配置文件路徑
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._deep_update(self.config, user_config)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
    
    def save_config(self, config_path: str) -> None:
        """保存配置文件
        
        Args:
            config_path: 保存路徑
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"✅ Config saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get_cluster_config(self) -> Dict[str, Any]:
        """獲取集群配置
        
        Returns:
            集群配置字典
        """
        return self.config.get('cluster', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """獲取性能配置
        
        Returns:
            性能配置字典
        """
        return self.config.get('performance', {})
    
    def get_distributed_computing_config(self, component: str) -> Dict[str, Any]:
        """獲取分布式計算組件配置
        
        Args:
            component: 組件名稱 (quantum_engine, data_manager, genetic_algorithm)
            
        Returns:
            組件配置字典
        """
        return self.config.get('distributed_computing', {}).get(component, {})
    
    def _deep_update(self, target: Dict, source: Dict) -> None:
        """深層更新字典
        
        Args:
            target: 目標字典
            source: 源字典
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def get_config(self) -> Dict[str, Any]:
        """獲取完整配置
        
        Returns:
            完整配置字典
        """
        return self.config


def create_default_config_file(output_path: str = "config/ray_config.yaml") -> str:
    """創建默認配置文件
    
    Args:
        output_path: 輸出路徑
        
    Returns:
        配置文件路徑
    """
    ray_config = RayConfig()
    ray_config.save_config(output_path)
    return output_path
