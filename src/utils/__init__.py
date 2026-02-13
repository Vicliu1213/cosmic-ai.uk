#!/usr/bin/env python3
"""
Utils Module
工具模組

Provides utility functions for logging, configuration management, and data processing.
提供日誌、配置管理和數據處理的工具函數。
"""

import os
import sys
import logging
import json
import yaml
import hashlib
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from functools import wraps
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器 - Configuration Manager"""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        path = Path(config_path)
        
        if not path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return {}
        
        try:
            if path.suffix in ['.yaml', '.yml']:
                with open(path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            elif path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                logger.error(f"Unsupported config format: {path.suffix}")
                return {}
            
            logger.info(f"✅ Configuration loaded from {config_path}")
            return self._config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return full configuration as dictionary."""
        return self._config.copy()


class Logger:
    """自定義日誌器 - Custom Logger"""
    
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def get_logger(cls, name: str, level: int = logging.INFO) -> logging.Logger:
        """Get or create logger with specified name."""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(level)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # File handler
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f'{name}.log'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            cls._loggers[name] = logger
        
        return cls._loggers[name]


def timing_decorator(func):
    """執行時間計時裝飾器 - Timing decorator for functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"⏱️  {func.__name__} completed in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ {func.__name__} failed after {elapsed:.3f}s: {e}")
            raise
    return wrapper


class DataProcessor:
    """數據處理器 - Data Processor"""
    
    @staticmethod
    def normalize_data(data: List[float], min_val: float = 0.0, max_val: float = 1.0) -> List[float]:
        """Normalize data to specified range."""
        if not data:
            return []
        
        min_data = min(data)
        max_data = max(data)
        range_data = max_data - min_data
        
        if range_data == 0:
            return [min_val] * len(data)
        
        return [
            min_val + (x - min_data) / range_data * (max_val - min_val)
            for x in data
        ]
    
    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, float]:
        """Calculate basic statistics."""
        if not data:
            return {
                'count': 0,
                'sum': 0.0,
                'mean': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std': 0.0
            }
        
        import statistics
        
        count = len(data)
        total = sum(data)
        mean = total / count
        
        return {
            'count': count,
            'sum': total,
            'mean': mean,
            'min': min(data),
            'max': max(data),
            'std': statistics.stdev(data) if count > 1 else 0.0
        }
    
    @staticmethod
    def batch_data(data: List[Any], batch_size: int) -> List[List[Any]]:
        """Split data into batches."""
        return [data[i:i + batch_size] for i in range(0, len(data), batch_size)]


class CacheManager:
    """緩存管理器 - Cache Manager"""
    
    def __init__(self, cache_dir: str = 'data/cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f'{key_hash}.cache'
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value from cache."""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return default
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Cache read error for {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in cache."""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            logger.debug(f"✅ Cached: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache write error for {key}: {e}")
            return False
    
    def clear(self, key: Optional[str] = None) -> bool:
        """Clear cache entry or entire cache."""
        try:
            if key:
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
            else:
                for cache_file in self.cache_dir.glob('*.cache'):
                    cache_file.unlink()
            logger.info("✅ Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


class FileManager:
    """文件管理器 - File Manager"""
    
    @staticmethod
    def ensure_directory(directory: str) -> Path:
        """Ensure directory exists."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def read_file(filepath: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read file contents."""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return None
    
    @staticmethod
    def write_file(filepath: str, content: str, encoding: str = 'utf-8') -> bool:
        """Write content to file."""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            logger.info(f"✅ File written: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error writing file {filepath}: {e}")
            return False
    
    @staticmethod
    def list_files(directory: str, pattern: str = '*') -> List[str]:
        """List files in directory matching pattern."""
        path = Path(directory)
        if not path.exists():
            return []
        return [str(f) for f in path.glob(pattern) if f.is_file()]


# Convenience functions
config = ConfigManager()
get_logger = Logger.get_logger
cache = CacheManager()
file_manager = FileManager()


__all__ = [
    'ConfigManager',
    'Logger',
    'DataProcessor',
    'CacheManager',
    'FileManager',
    'timing_decorator',
    'config',
    'get_logger',
    'cache',
    'file_manager',
]
