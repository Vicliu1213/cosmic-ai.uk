#!/usr/bin/env python3
"""
統一交易系統配置管理
Unified Trading System Configuration Management

提供:
  1. 配置加載和驗證
  2. 環境變數支持
  3. 配置持久化
  4. 配置校驗
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict, dataclass
import yaml

from .unified_trading_system import (
    BotConfig, BotType, BotManager, get_bot_manager
)

logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """系統整體配置"""
    system_name: str = "Cosmic AI Trading System"
    log_level: str = "INFO"
    max_execution_history: int = 10000
    risk_limit_daily: float = 10000.0
    risk_limit_monthly: float = 100000.0
    data_dir: str = "./data"
    config_dir: str = "./config"
    enable_monitoring: bool = True
    monitoring_interval: int = 60  # 秒


class ConfigManager:
    """統一的配置管理器"""
    
    DEFAULT_CONFIG_DIR = Path("./config/trading_system")
    DEFAULT_SYSTEM_CONFIG = {
        "system_name": "Cosmic AI Trading System",
        "log_level": "INFO",
        "max_execution_history": 10000,
        "risk_limit_daily": 10000.0,
        "risk_limit_monthly": 100000.0,
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目錄
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.system_config: SystemConfig = SystemConfig()
        self.bot_configs: Dict[str, BotConfig] = {}
        
        logger.info(f"ConfigManager initialized with dir: {self.config_dir}")
    
    def load_system_config(self, config_file: Optional[str] = None) -> SystemConfig:
        """
        加載系統配置
        
        Args:
            config_file: 配置文件名 (默認: system_config.json)
            
        Returns:
            SystemConfig: 加載的配置
        """
        config_file = config_file or "system_config.json"
        config_path = self.config_dir / config_file
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.system_config = SystemConfig(**data)
                logger.info(f"Loaded system config from {config_path}")
            except Exception as e:
                logger.error(f"Error loading system config: {e}")
                self.system_config = SystemConfig()
        else:
            logger.info(f"System config not found, using defaults")
            self.system_config = SystemConfig()
        
        return self.system_config
    
    def save_system_config(self, config: Optional[SystemConfig] = None):
        """
        保存系統配置
        
        Args:
            config: 要保存的配置 (默認: 當前配置)
        """
        config = config or self.system_config
        config_path = self.config_dir / "system_config.json"
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2)
            logger.info(f"Saved system config to {config_path}")
        except Exception as e:
            logger.error(f"Error saving system config: {e}")
    
    def load_bot_configs(self, config_file: Optional[str] = None) -> Dict[str, BotConfig]:
        """
        加載 Bot 配置
        
        Args:
            config_file: 配置文件名 (默認: bots_config.yaml)
            
        Returns:
            Dict: Bot 配置映射
        """
        config_file = config_file or "bots_config.yaml"
        config_path = self.config_dir / config_file
        
        self.bot_configs = {}
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                for bot_name, bot_data in data.items():
                    try:
                        bot_config = self._parse_bot_config(bot_name, bot_data)
                        self.bot_configs[bot_name] = bot_config
                    except Exception as e:
                        logger.error(f"Error parsing bot config {bot_name}: {e}")
                
                logger.info(f"Loaded {len(self.bot_configs)} bot configs from {config_path}")
            except Exception as e:
                logger.error(f"Error loading bot configs: {e}")
        else:
            logger.info(f"Bot config file not found: {config_path}")
        
        return self.bot_configs
    
    def save_bot_configs(self, configs: Optional[Dict[str, BotConfig]] = None):
        """
        保存 Bot 配置
        
        Args:
            configs: 要保存的配置 (默認: 當前配置)
        """
        configs = configs or self.bot_configs
        config_path = self.config_dir / "bots_config.yaml"
        
        try:
            data = {}
            for bot_name, config in configs.items():
                data[bot_name] = {
                    "bot_type": config.bot_type.value,
                    "enabled": config.enabled,
                    "config_data": config.config_data,
                    "risk_limit": config.risk_limit,
                    "max_concurrent_trades": config.max_concurrent_trades,
                    "timeout": config.timeout,
                    "retry_attempts": config.retry_attempts,
                }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            logger.info(f"Saved {len(configs)} bot configs to {config_path}")
        except Exception as e:
            logger.error(f"Error saving bot configs: {e}")
    
    def _parse_bot_config(self, bot_name: str, data: Dict[str, Any]) -> BotConfig:
        """
        解析單個 Bot 配置
        
        Args:
            bot_name: Bot 名稱
            data: 配置數據
            
        Returns:
            BotConfig: 解析後的配置
        """
        bot_type = BotType(data.get("bot_type", "custom"))
        
        return BotConfig(
            bot_name=bot_name,
            bot_type=bot_type,
            enabled=data.get("enabled", True),
            config_data=data.get("config_data", {}),
            risk_limit=float(data.get("risk_limit", 1000.0)),
            max_concurrent_trades=int(data.get("max_concurrent_trades", 10)),
            timeout=int(data.get("timeout", 30)),
            retry_attempts=int(data.get("retry_attempts", 3)),
        )
    
    def add_bot_config(self, config: BotConfig) -> bool:
        """
        添加 Bot 配置
        
        Args:
            config: Bot 配置
            
        Returns:
            bool: 是否成功
        """
        if config.bot_name in self.bot_configs:
            logger.warning(f"Bot config already exists: {config.bot_name}")
            return False
        
        self.bot_configs[config.bot_name] = config
        logger.info(f"Added bot config: {config.bot_name}")
        return True
    
    def remove_bot_config(self, bot_name: str) -> bool:
        """
        移除 Bot 配置
        
        Args:
            bot_name: Bot 名稱
            
        Returns:
            bool: 是否成功
        """
        if bot_name not in self.bot_configs:
            logger.warning(f"Bot config not found: {bot_name}")
            return False
        
        del self.bot_configs[bot_name]
        logger.info(f"Removed bot config: {bot_name}")
        return True
    
    def get_bot_config(self, bot_name: str) -> Optional[BotConfig]:
        """取得 Bot 配置"""
        return self.bot_configs.get(bot_name)
    
    def get_all_bot_configs(self) -> Dict[str, BotConfig]:
        """取得所有 Bot 配置"""
        return dict(self.bot_configs)
    
    def validate_configs(self) -> Dict[str, List[str]]:
        """
        驗證所有配置
        
        Returns:
            Dict: {config_name: [errors]}
        """
        errors = {}
        
        # 驗證系統配置
        if not self.system_config.system_name:
            errors["system_config"] = ["system_name is required"]
        
        # 驗證 Bot 配置
        for bot_name, config in self.bot_configs.items():
            bot_errors = []
            
            if not config.bot_name:
                bot_errors.append("bot_name is required")
            
            if config.risk_limit <= 0:
                bot_errors.append("risk_limit must be positive")
            
            if config.max_concurrent_trades <= 0:
                bot_errors.append("max_concurrent_trades must be positive")
            
            if config.timeout <= 0:
                bot_errors.append("timeout must be positive")
            
            if bot_errors:
                errors[bot_name] = bot_errors
        
        if errors:
            logger.warning(f"Config validation errors: {errors}")
        else:
            logger.info("All configs validated successfully")
        
        return errors
    
    def apply_to_bot_manager(self, manager: Optional[BotManager] = None) -> BotManager:
        """
        將配置應用到 Bot 管理器
        
        Args:
            manager: Bot 管理器 (默認: 全局實例)
            
        Returns:
            BotManager: 配置後的管理器
        """
        manager = manager or get_bot_manager()
        
        # 註冊所有 Bot
        for bot_name, config in self.bot_configs.items():
            manager.register_bot(config)
        
        logger.info(f"Applied {len(self.bot_configs)} bot configs to manager")
        return manager
    
    def load_all(self, system_config_file: Optional[str] = None,
                 bot_config_file: Optional[str] = None) -> tuple:
        """
        一次性加載所有配置
        
        Args:
            system_config_file: 系統配置文件
            bot_config_file: Bot 配置文件
            
        Returns:
            tuple: (system_config, bot_configs)
        """
        system_config = self.load_system_config(system_config_file)
        bot_configs = self.load_bot_configs(bot_config_file)
        return system_config, bot_configs
    
    def save_all(self):
        """保存所有配置"""
        self.save_system_config()
        self.save_bot_configs()


# ============================================================================
# 創建示例配置文件
# ============================================================================

def create_example_configs(config_dir: Optional[Path] = None):
    """
    創建示例配置文件
    
    Args:
        config_dir: 配置目錄
    """
    config_dir = config_dir or ConfigManager.DEFAULT_CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 創建示例系統配置
    system_config_path = config_dir / "system_config.example.json"
    if not system_config_path.exists():
        with open(system_config_path, 'w', encoding='utf-8') as f:
            json.dump(ConfigManager.DEFAULT_SYSTEM_CONFIG, f, indent=2)
        logger.info(f"Created example system config: {system_config_path}")
    
    # 創建示例 Bot 配置
    bots_config_path = config_dir / "bots_config.example.yaml"
    if not bots_config_path.exists():
        example_bots = {
            "Hummingbot-1": {
                "bot_type": "hummingbot",
                "enabled": True,
                "config_data": {
                    "host": "localhost",
                    "port": 8000,
                },
                "risk_limit": 1000.0,
                "max_concurrent_trades": 10,
                "timeout": 30,
                "retry_attempts": 3,
            },
            "LLM-TradeBot-1": {
                "bot_type": "llm_tradebot",
                "enabled": True,
                "config_data": {},
                "risk_limit": 500.0,
                "max_concurrent_trades": 5,
                "timeout": 60,
                "retry_attempts": 3,
            },
            "MarketBot-1": {
                "bot_type": "marketbot",
                "enabled": True,
                "config_data": {},
                "risk_limit": 2000.0,
                "max_concurrent_trades": 20,
                "timeout": 30,
                "retry_attempts": 2,
            },
        }
        
        with open(bots_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(example_bots, f, default_flow_style=False)
        
        logger.info(f"Created example bots config: {bots_config_path}")


# ============================================================================
# 全局配置管理器實例
# ============================================================================

_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_dir: Optional[Path] = None) -> ConfigManager:
    """取得全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_dir)
    return _config_manager


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 創建示例配置
    create_example_configs()
    
    # 加載配置
    manager = get_config_manager()
    system_config, bot_configs = manager.load_all()
    
    print(f"System Config: {system_config}")
    print(f"Bot Configs: {bot_configs}")
    
    # 驗證配置
    errors = manager.validate_configs()
    print(f"Validation Errors: {errors}")
