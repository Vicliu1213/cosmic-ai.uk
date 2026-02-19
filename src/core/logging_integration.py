#!/usr/bin/env python3
"""
日誌整合模組 (Logging Integration Module)
日志整合系统 - 支持本地、雲端日誌存儲
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

# 日誌配置類
class LogConfig:
    """日誌配置管理"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化日誌配置
        
        Args:
            config_path: YAML 配置檔案路徑
        """
        self.config_path = config_path or "config/logging_config.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """載入 YAML 配置檔案"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """預設配置"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
                'json': {
                    'format': '%(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'standard'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/app.log',
                    'maxBytes': 10485760,
                    'backupCount': 5,
                    'level': 'DEBUG',
                    'formatter': 'standard'
                }
            },
            'loggers': {
                'trading': {'level': 'DEBUG'},
                'system': {'level': 'INFO'},
                'api': {'level': 'DEBUG'}
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        return self.config.get(key, default)


# 日誌管理器
class LogManager:
    """統一日誌管理器"""
    
    def __init__(self, config: Optional[LogConfig] = None, log_dir: str = "logs"):
        """初始化日誌管理器
        
        Args:
            config: 日誌配置對象
            log_dir: 日誌目錄
        """
        self.config = config or LogConfig()
        self.log_dir = log_dir
        self._ensure_log_dir()
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_base_logger()
    
    def _ensure_log_dir(self) -> None:
        """確保日誌目錄存在"""
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
    
    def _setup_base_logger(self) -> None:
        """設置基礎日誌記錄器"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"{self.log_dir}/app.log")
            ]
        )
    
    def get_logger(self, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """獲取或創建日誌記錄器
        
        Args:
            name: 日誌記錄器名稱
            log_file: 自訂日誌檔案名稱
            
        Returns:
            logging.Logger 對象
        """
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # 文件處理器
        if log_file is None:
            log_file = f"{self.log_dir}/{name}.log"
        
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self.loggers[name] = logger
        return logger
    
    def log_event(self, category: str, level: str, message: str, **kwargs) -> None:
        """記錄事件
        
        Args:
            category: 日誌類別 (trading, system, api)
            level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: 日誌消息
            **kwargs: 額外資料
        """
        logger = self.get_logger(category)
        
        # 構建完整消息
        full_message = message
        if kwargs:
            full_message = f"{message} | {json.dumps(kwargs, ensure_ascii=False)}"
        
        # 寫入日誌
        if level == "DEBUG":
            logger.debug(full_message)
        elif level == "INFO":
            logger.info(full_message)
        elif level == "WARNING":
            logger.warning(full_message)
        elif level == "ERROR":
            logger.error(full_message)
        elif level == "CRITICAL":
            logger.critical(full_message)


# 日誌查詢工具
class LogQueryTool:
    """日誌查詢工具"""
    
    def __init__(self, log_dir: str = "logs"):
        """初始化查詢工具
        
        Args:
            log_dir: 日誌目錄
        """
        self.log_dir = log_dir
    
    def get_recent_logs(
        self,
        category: str,
        limit: int = 100,
        level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """獲取最近的日誌
        
        Args:
            category: 日誌類別
            limit: 限制數量
            level: 日誌級別篩選
            
        Returns:
            日誌列表
        """
        log_file = f"{self.log_dir}/{category}.log"
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-limit:]
                for line in lines:
                    if level and level not in line:
                        continue
                    logs.append({
                        'timestamp': self._extract_timestamp(line),
                        'message': line.strip()
                    })
        except Exception as e:
            logging.error(f"Error reading logs: {e}")
        
        return logs
    
    def _extract_timestamp(self, log_line: str) -> str:
        """從日誌行提取時間戳"""
        try:
            return log_line.split(' - ')[0]
        except:
            return datetime.now(timezone.utc).isoformat()
    
    def search_logs(
        self,
        category: str,
        keyword: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """搜索日誌
        
        Args:
            category: 日誌類別
            keyword: 搜索關鍵字
            limit: 限制數量
            
        Returns:
            匹配的日誌列表
        """
        log_file = f"{self.log_dir}/{category}.log"
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if keyword.lower() in line.lower():
                        logs.append({
                            'timestamp': self._extract_timestamp(line),
                            'message': line.strip()
                        })
                        if len(logs) >= limit:
                            break
        except Exception as e:
            logging.error(f"Error searching logs: {e}")
        
        return logs
    
    def get_log_summary(self, category: str) -> Dict[str, Any]:
        """獲取日誌摘要
        
        Args:
            category: 日誌類別
            
        Returns:
            日誌摘要統計
        """
        log_file = f"{self.log_dir}/{category}.log"
        
        if not os.path.exists(log_file):
            return {}
        
        summary = {
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0,
            'total': 0
        }
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    summary['total'] += 1
                    if 'DEBUG' in line:
                        summary['DEBUG'] += 1
                    elif 'INFO' in line:
                        summary['INFO'] += 1
                    elif 'WARNING' in line:
                        summary['WARNING'] += 1
                    elif 'ERROR' in line:
                        summary['ERROR'] += 1
                    elif 'CRITICAL' in line:
                        summary['CRITICAL'] += 1
        except Exception as e:
            logging.error(f"Error summarizing logs: {e}")
        
        return summary


# 簡單使用函數
def create_logger(name: str) -> logging.Logger:
    """快速創建日誌記錄器"""
    manager = LogManager()
    return manager.get_logger(name)


def log_event(
    category: str,
    level: str,
    message: str,
    **kwargs
) -> None:
    """快速記錄事件"""
    manager = LogManager()
    manager.log_event(category, level, message, **kwargs)


if __name__ == "__main__":
    # 測試
    print("✅ 日誌模組已載入")
    
    manager = LogManager()
    logger = manager.get_logger("test")
    logger.info("Test log entry")
    
    query = LogQueryTool()
    summary = query.get_log_summary("test")
    print(f"Log Summary: {summary}")
