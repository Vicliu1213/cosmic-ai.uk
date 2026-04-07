"""
External module - External integrations and third-party libraries

統一交易系統 (Unified Trading System)
=====================================

核心模組:
  - unified_trading_system: Bot 基類、管理器、數據結構
  - config_manager: 配置管理系統
  - unified_dashboard: 儀表板和 API

使用方式:
  from src.external import (
      BotManager, get_bot_manager, TradingSignal, SignalType,
      ConfigManager, get_config_manager,
      create_dashboard_app
  )
"""

# 匯出核心類和函數
from .unified_trading_system import (
    BotType,
    BotStatus,
    SignalType,
    TradingSignal,
    TradeExecution,
    BotMetrics,
    BotConfig,
    TradingBot,
    HummingbotImpl,
    LLMTradebotImpl,
    MarketBotImpl,
    BotManager,
    get_bot_manager,
    initialize_bot_manager,
)

from .config_manager import (
    SystemConfig,
    ConfigManager,
    create_example_configs,
    get_config_manager,
)

from .unified_dashboard import (
    DashboardBotInfo,
    DashboardMetrics,
    UnifiedTradingDashboardManager,
    UnifiedTradingDashboardAPI,
    create_dashboard_app,
)

__all__ = [
    # 交易系統枚舉和數據結構
    "BotType",
    "BotStatus",
    "SignalType",
    "TradingSignal",
    "TradeExecution",
    "BotMetrics",
    "BotConfig",
    
    # Bot 實現
    "TradingBot",
    "HummingbotImpl",
    "LLMTradebotImpl",
    "MarketBotImpl",
    
    # Bot 管理器
    "BotManager",
    "get_bot_manager",
    "initialize_bot_manager",
    
    # 配置管理
    "SystemConfig",
    "ConfigManager",
    "create_example_configs",
    "get_config_manager",
    
    # 儀表板
    "DashboardBotInfo",
    "DashboardMetrics",
    "UnifiedTradingDashboardManager",
    "UnifiedTradingDashboardAPI",
    "create_dashboard_app",
]
