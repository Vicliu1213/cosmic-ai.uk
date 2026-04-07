#!/usr/bin/env python3
"""
統一交易系統 - 多 Bot 集成架構
Unified Trading System - Multi-Bot Integration Framework

功能:
  1. 統一的交易 Bot 介面 (TradingBot Base)
  2. Bot 管理器 (BotManager) - 統一管理多個 Bot
  3. 統一的信號路由系統
  4. 統一的配置系統
  5. 統一的監控和報表
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime
from enum import Enum
import logging
import asyncio
import json

logger = logging.getLogger(__name__)


# ============================================================================
# 通用枚舉和數據結構
# ============================================================================

class BotType(Enum):
    """Bot 類型"""
    HUMMINGBOT = "hummingbot"
    LLM_TRADEBOT = "llm_tradebot"
    MARKETBOT = "marketbot"
    CUSTOM = "custom"


class BotStatus(Enum):
    """Bot 狀態"""
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class SignalType(Enum):
    """信號類型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE_POSITION = "close_position"


@dataclass
class TradingSignal:
    """統一交易信號"""
    signal_id: str
    signal_type: SignalType
    symbol: str
    quantity: float
    price: Optional[float] = None
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    source_bot: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeExecution:
    """交易執行結果"""
    execution_id: str
    signal_id: str
    bot_name: str
    bot_type: BotType
    status: str  # PENDING, EXECUTED, FAILED
    timestamp: datetime = field(default_factory=datetime.now)
    order_ids: List[str] = field(default_factory=list)
    pnl: float = 0.0
    error_message: Optional[str] = None


@dataclass
class BotMetrics:
    """Bot 性能指標"""
    bot_name: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    average_pnl: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    daily_trades: int = 0
    monthly_pnl: float = 0.0


@dataclass
class BotConfig:
    """Bot 配置"""
    bot_name: str
    bot_type: BotType
    enabled: bool = True
    config_data: Dict[str, Any] = field(default_factory=dict)
    risk_limit: float = 1000.0  # 單日風險限制
    max_concurrent_trades: int = 10
    timeout: int = 30  # 秒
    retry_attempts: int = 3


# ============================================================================
# 基礎交易 Bot 介面
# ============================================================================

class TradingBot(ABC):
    """
    統一的交易 Bot 基類
    所有 Bot 實現都應繼承此類
    """
    
    def __init__(self, config: BotConfig):
        """
        初始化 Bot
        
        Args:
            config: Bot 配置
        """
        self.config = config
        self.status = BotStatus.OFFLINE
        self.metrics = BotMetrics(bot_name=config.bot_name)
        self.execution_history: List[TradeExecution] = []
        self.is_connected = False
        
        logger.info(f"Initialized {config.bot_type.value} bot: {config.bot_name}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """連接 Bot"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """斷開 Bot 連接"""
        pass
    
    @abstractmethod
    async def execute_signal(self, signal: TradingSignal) -> TradeExecution:
        """執行交易信號"""
        pass
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """取得持倉"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """取消訂單"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """取得 Bot 狀態"""
        pass
    
    async def update_metrics(self):
        """更新性能指標"""
        if self.execution_history:
            total = len(self.execution_history)
            winning = len([e for e in self.execution_history if e.pnl > 0])
            losing = len([e for e in self.execution_history if e.pnl < 0])
            
            self.metrics.total_trades = total
            self.metrics.winning_trades = winning
            self.metrics.losing_trades = losing
            self.metrics.win_rate = winning / total if total > 0 else 0.0
            self.metrics.total_pnl = sum(e.pnl for e in self.execution_history)
            self.metrics.average_pnl = self.metrics.total_pnl / total if total > 0 else 0.0
            self.metrics.last_updated = datetime.now()
    
    def get_metrics(self) -> BotMetrics:
        """取得性能指標"""
        return self.metrics


# ============================================================================
# 具體 Bot 實現 (Adapter Pattern)
# ============================================================================

class HummingbotImpl(TradingBot):
    """Hummingbot 實現"""
    
    def __init__(self, config: BotConfig):
        """初始化 Hummingbot"""
        if config.bot_type != BotType.HUMMINGBOT:
            raise ValueError("Config must be for HUMMINGBOT type")
        super().__init__(config)
        self.connector = None
        self.orders: Dict[str, Any] = {}
    
    async def connect(self) -> bool:
        """連接 Hummingbot"""
        try:
            # 導入 hummingbot_integration_layer
            from src.core.hummingbot_integration_layer import HummingbotIntegrationLayer
            
            self.connector = HummingbotIntegrationLayer(
                hummingbot_host=self.config.config_data.get("host", "localhost"),
                hummingbot_port=self.config.config_data.get("port", 8000)
            )
            
            success = self.connector.initialize_connection()
            if success:
                self.status = BotStatus.RUNNING
                self.is_connected = True
                logger.info(f"Connected to Hummingbot: {self.config.bot_name}")
            return success
        except Exception as e:
            self.status = BotStatus.ERROR
            logger.error(f"Failed to connect to Hummingbot: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """斷開 Hummingbot"""
        try:
            if self.connector:
                self.connector.shutdown()
            self.status = BotStatus.SHUTDOWN
            self.is_connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting Hummingbot: {e}")
            return False
    
    async def execute_signal(self, signal: TradingSignal) -> TradeExecution:
        """執行信號"""
        execution = TradeExecution(
            execution_id=f"EXEC_{datetime.now().timestamp()}",
            signal_id=signal.signal_id,
            bot_name=self.config.bot_name,
            bot_type=BotType.HUMMINGBOT,
            status="PENDING"
        )
        
        try:
            if not self.is_connected:
                execution.status = "FAILED"
                execution.error_message = "Hummingbot not connected"
                return execution
            
            # 執行信號邏輯
            if signal.signal_type == SignalType.BUY:
                order = self.connector.order_executor.create_order(
                    exchange="default",
                    pair=signal.symbol,
                    side="BUY",
                    price=signal.price or 0.0,
                    amount=signal.quantity
                )
                if order:
                    execution.order_ids.append(order.order_id)
                    execution.status = "EXECUTED"
            
            elif signal.signal_type == SignalType.SELL:
                order = self.connector.order_executor.create_order(
                    exchange="default",
                    pair=signal.symbol,
                    side="SELL",
                    price=signal.price or 0.0,
                    amount=signal.quantity
                )
                if order:
                    execution.order_ids.append(order.order_id)
                    execution.status = "EXECUTED"
            
            self.execution_history.append(execution)
            await self.update_metrics()
            
        except Exception as e:
            execution.status = "FAILED"
            execution.error_message = str(e)
            logger.error(f"Hummingbot execution error: {e}")
        
        return execution
    
    async def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """取得持倉"""
        if not self.is_connected:
            return None
        # TODO: 實現取得持倉邏輯
        return {"symbol": symbol, "quantity": 0.0}
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消訂單"""
        if not self.is_connected:
            return False
        try:
            return self.connector.order_executor.cancel_order(order_id)
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """取得狀態"""
        if self.connector:
            return self.connector.get_system_status()
        return {
            "status": self.status.value,
            "connected": self.is_connected,
            "timestamp": datetime.now().isoformat()
        }


class LLMTradebotImpl(TradingBot):
    """LLM-TradeBot 實現"""
    
    def __init__(self, config: BotConfig):
        """初始化 LLM-TradeBot"""
        if config.bot_type != BotType.LLM_TRADEBOT:
            raise ValueError("Config must be for LLM_TRADEBOT type")
        super().__init__(config)
        self.router = None
        self.decisions: List[Dict[str, Any]] = []
    
    async def connect(self) -> bool:
        """連接 LLM-TradeBot"""
        try:
            # 導入 llm_tradebot_router
            from src.integrations.llm_tradebot_router import LLMTradeBotRouter
            
            self.router = LLMTradeBotRouter(self.config.config_data)
            success = await self.router.connect()
            
            if success:
                self.status = BotStatus.RUNNING
                self.is_connected = True
                logger.info(f"Connected to LLM-TradeBot: {self.config.bot_name}")
            return success
        except Exception as e:
            self.status = BotStatus.ERROR
            logger.error(f"Failed to connect to LLM-TradeBot: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """斷開 LLM-TradeBot"""
        try:
            if self.router:
                await self.router.disconnect()
            self.status = BotStatus.SHUTDOWN
            self.is_connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting LLM-TradeBot: {e}")
            return False
    
    async def execute_signal(self, signal: TradingSignal) -> TradeExecution:
        """執行信號"""
        execution = TradeExecution(
            execution_id=f"EXEC_{datetime.now().timestamp()}",
            signal_id=signal.signal_id,
            bot_name=self.config.bot_name,
            bot_type=BotType.LLM_TRADEBOT,
            status="PENDING"
        )
        
        try:
            if not self.is_connected:
                execution.status = "FAILED"
                execution.error_message = "LLM-TradeBot not connected"
                return execution
            
            # 路由信號到多代理系統
            success = await self.router.send_signal(signal)
            
            if success:
                execution.status = "EXECUTED"
                self.decisions.append({
                    "signal_id": signal.signal_id,
                    "decision": "approved",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                execution.status = "FAILED"
                execution.error_message = "Multi-agent decision rejected"
            
            self.execution_history.append(execution)
            await self.update_metrics()
            
        except Exception as e:
            execution.status = "FAILED"
            execution.error_message = str(e)
            logger.error(f"LLM-TradeBot execution error: {e}")
        
        return execution
    
    async def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """取得持倉"""
        if not self.is_connected:
            return None
        # TODO: 實現取得持倉邏輯
        return {"symbol": symbol, "quantity": 0.0}
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消訂單"""
        # LLM-TradeBot 通過多代理系統取消
        logger.info(f"Attempting to cancel order {order_id} via LLM-TradeBot")
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """取得狀態"""
        return {
            "status": self.status.value,
            "connected": self.is_connected,
            "decisions_count": len(self.decisions),
            "timestamp": datetime.now().isoformat()
        }


class MarketBotImpl(TradingBot):
    """MarketBot 實現"""
    
    def __init__(self, config: BotConfig):
        """初始化 MarketBot"""
        if config.bot_type != BotType.MARKETBOT:
            raise ValueError("Config must be for MARKETBOT type")
        super().__init__(config)
        self.market_data: Dict[str, Any] = {}
    
    async def connect(self) -> bool:
        """連接 MarketBot"""
        try:
            self.status = BotStatus.RUNNING
            self.is_connected = True
            logger.info(f"Connected to MarketBot: {self.config.bot_name}")
            return True
        except Exception as e:
            self.status = BotStatus.ERROR
            logger.error(f"Failed to connect to MarketBot: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """斷開 MarketBot"""
        try:
            self.status = BotStatus.SHUTDOWN
            self.is_connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting MarketBot: {e}")
            return False
    
    async def execute_signal(self, signal: TradingSignal) -> TradeExecution:
        """執行信號"""
        execution = TradeExecution(
            execution_id=f"EXEC_{datetime.now().timestamp()}",
            signal_id=signal.signal_id,
            bot_name=self.config.bot_name,
            bot_type=BotType.MARKETBOT,
            status="EXECUTED"
        )
        
        try:
            self.execution_history.append(execution)
            await self.update_metrics()
        except Exception as e:
            execution.status = "FAILED"
            execution.error_message = str(e)
            logger.error(f"MarketBot execution error: {e}")
        
        return execution
    
    async def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """取得持倉"""
        return {"symbol": symbol, "quantity": 0.0}
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消訂單"""
        logger.info(f"MarketBot canceling order {order_id}")
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """取得狀態"""
        return {
            "status": self.status.value,
            "connected": self.is_connected,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# Bot 管理器 - 統一管理所有 Bot
# ============================================================================

class BotManager:
    """
    統一的 Bot 管理器
    負責: 
      1. 管理多個 Bot 實例
      2. 路由信號到指定 Bot
      3. 監控 Bot 健康狀態
      4. 聚合性能指標
    """
    
    def __init__(self):
        """初始化 Bot 管理器"""
        self.bots: Dict[str, TradingBot] = {}
        self.bot_configs: Dict[str, BotConfig] = {}
        self.active_bot: Optional[str] = None
        self.execution_history: List[TradeExecution] = []
        self.max_history = 10000
        
        logger.info("BotManager initialized")
    
    def register_bot(self, config: BotConfig) -> bool:
        """
        註冊新 Bot
        
        Args:
            config: Bot 配置
            
        Returns:
            bool: 是否成功
        """
        try:
            if config.bot_name in self.bots:
                logger.warning(f"Bot {config.bot_name} already exists")
                return False
            
            # 根據類型創建對應的 Bot 實例
            if config.bot_type == BotType.HUMMINGBOT:
                bot = HummingbotImpl(config)
            elif config.bot_type == BotType.LLM_TRADEBOT:
                bot = LLMTradebotImpl(config)
            elif config.bot_type == BotType.MARKETBOT:
                bot = MarketBotImpl(config)
            else:
                logger.error(f"Unknown bot type: {config.bot_type}")
                return False
            
            self.bots[config.bot_name] = bot
            self.bot_configs[config.bot_name] = config
            
            if not self.active_bot:
                self.active_bot = config.bot_name
            
            logger.info(f"Bot registered: {config.bot_name} ({config.bot_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering bot: {e}")
            return False
    
    async def connect_bot(self, bot_name: str) -> bool:
        """
        連接指定 Bot
        
        Args:
            bot_name: Bot 名稱
            
        Returns:
            bool: 是否成功
        """
        if bot_name not in self.bots:
            logger.error(f"Bot not found: {bot_name}")
            return False
        
        try:
            bot = self.bots[bot_name]
            success = await bot.connect()
            if success:
                logger.info(f"Bot connected: {bot_name}")
            return success
        except Exception as e:
            logger.error(f"Error connecting bot {bot_name}: {e}")
            return False
    
    async def disconnect_bot(self, bot_name: str) -> bool:
        """斷開指定 Bot"""
        if bot_name not in self.bots:
            logger.error(f"Bot not found: {bot_name}")
            return False
        
        try:
            bot = self.bots[bot_name]
            success = await bot.disconnect()
            logger.info(f"Bot disconnected: {bot_name}")
            return success
        except Exception as e:
            logger.error(f"Error disconnecting bot {bot_name}: {e}")
            return False
    
    async def connect_all(self) -> Dict[str, bool]:
        """連接所有 Bot"""
        results = {}
        for bot_name in self.bots:
            results[bot_name] = await self.connect_bot(bot_name)
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """斷開所有 Bot"""
        results = {}
        for bot_name in self.bots:
            results[bot_name] = await self.disconnect_bot(bot_name)
        return results
    
    def switch_active_bot(self, bot_name: str) -> bool:
        """
        切換活躍 Bot
        
        Args:
            bot_name: Bot 名稱
            
        Returns:
            bool: 是否成功
        """
        if bot_name not in self.bots:
            logger.error(f"Bot not found: {bot_name}")
            return False
        
        self.active_bot = bot_name
        logger.info(f"Switched to bot: {bot_name}")
        return True
    
    async def execute_signal(
        self,
        signal: TradingSignal,
        bot_name: Optional[str] = None
    ) -> TradeExecution:
        """
        執行信號
        
        Args:
            signal: 交易信號
            bot_name: 指定 Bot 名稱 (若為 None，使用活躍 Bot)
            
        Returns:
            TradeExecution: 執行結果
        """
        target_bot = bot_name or self.active_bot
        
        if not target_bot or target_bot not in self.bots:
            logger.error(f"Invalid bot: {target_bot}")
            return TradeExecution(
                execution_id=f"EXEC_{datetime.now().timestamp()}",
                signal_id=signal.signal_id,
                bot_name="SYSTEM",
                bot_type=BotType.CUSTOM,
                status="FAILED",
                error_message="Bot not available"
            )
        
        try:
            bot = self.bots[target_bot]
            execution = await bot.execute_signal(signal)
            
            self.execution_history.append(execution)
            if len(self.execution_history) > self.max_history:
                self.execution_history = self.execution_history[-self.max_history:]
            
            return execution
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return TradeExecution(
                execution_id=f"EXEC_{datetime.now().timestamp()}",
                signal_id=signal.signal_id,
                bot_name=target_bot,
                bot_type=self.bots[target_bot].config.bot_type,
                status="FAILED",
                error_message=str(e)
            )
    
    async def execute_signal_multi_bot(
        self,
        signal: TradingSignal,
        bot_names: Optional[List[str]] = None
    ) -> Dict[str, TradeExecution]:
        """
        同時在多個 Bot 上執行信號
        
        Args:
            signal: 交易信號
            bot_names: Bot 名稱列表 (若為 None，執行所有 Bot)
            
        Returns:
            Dict: {bot_name: execution}
        """
        targets = bot_names or list(self.bots.keys())
        results = {}
        
        tasks = [
            self.execute_signal(signal, bot_name)
            for bot_name in targets
        ]
        
        executions = await asyncio.gather(*tasks, return_exceptions=True)
        
        for bot_name, execution in zip(targets, executions):
            if isinstance(execution, Exception):
                results[bot_name] = TradeExecution(
                    execution_id=f"EXEC_{datetime.now().timestamp()}",
                    signal_id=signal.signal_id,
                    bot_name=bot_name,
                    bot_type=self.bots[bot_name].config.bot_type,
                    status="FAILED",
                    error_message=str(execution)
                )
            else:
                results[bot_name] = execution
        
        return results
    
    def get_bot_list(self) -> List[Dict[str, Any]]:
        """取得 Bot 列表"""
        return [
            {
                "name": name,
                "type": config.bot_type.value,
                "enabled": config.enabled,
                "connected": bot.is_connected,
                "status": bot.status.value
            }
            for name, config in self.bot_configs.items()
            for bot in [self.bots.get(name)] if bot
        ]
    
    async def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """取得所有 Bot 狀態"""
        results = {}
        for bot_name, bot in self.bots.items():
            results[bot_name] = await bot.get_status()
        return results
    
    def get_all_metrics(self) -> Dict[str, BotMetrics]:
        """取得所有 Bot 的性能指標"""
        return {
            bot_name: bot.get_metrics()
            for bot_name, bot in self.bots.items()
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """取得系統整體指標"""
        all_metrics = self.get_all_metrics()
        
        total_trades = sum(m.total_trades for m in all_metrics.values())
        total_winning = sum(m.winning_trades for m in all_metrics.values())
        total_pnl = sum(m.total_pnl for m in all_metrics.values())
        
        return {
            "total_bots": len(self.bots),
            "active_bots": sum(1 for b in self.bots.values() if b.is_connected),
            "total_trades": total_trades,
            "total_winning_trades": total_winning,
            "total_pnl": total_pnl,
            "win_rate": total_winning / total_trades if total_trades > 0 else 0.0,
            "executions_count": len(self.execution_history),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_position(
        self,
        symbol: str,
        bot_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        取得持倉
        
        Args:
            symbol: 交易對
            bot_name: Bot 名稱 (若為 None，查詢所有 Bot)
            
        Returns:
            Dict: 持倉信息
        """
        if bot_name:
            if bot_name not in self.bots:
                return {"error": f"Bot not found: {bot_name}"}
            
            position = await self.bots[bot_name].get_position(symbol)
            return {"bot": bot_name, "position": position}
        else:
            results = {}
            for name, bot in self.bots.items():
                position = await bot.get_position(symbol)
                results[name] = position
            return results


# ============================================================================
# 全局 Bot 管理器實例
# ============================================================================

_bot_manager: Optional[BotManager] = None


def get_bot_manager() -> BotManager:
    """取得全局 Bot 管理器"""
    global _bot_manager
    if _bot_manager is None:
        _bot_manager = BotManager()
    return _bot_manager


def initialize_bot_manager(configs: List[BotConfig]) -> BotManager:
    """
    初始化 Bot 管理器並註冊 Bot
    
    Args:
        configs: Bot 配置列表
        
    Returns:
        BotManager: 初始化的管理器
    """
    manager = get_bot_manager()
    for config in configs:
        manager.register_bot(config)
    return manager


if __name__ == "__main__":
    # 測試代碼
    logging.basicConfig(level=logging.INFO)
    
    # 創建配置
    configs = [
        BotConfig(
            bot_name="Hummingbot-1",
            bot_type=BotType.HUMMINGBOT,
            config_data={"host": "localhost", "port": 8000}
        ),
        BotConfig(
            bot_name="LLM-TradeBot-1",
            bot_type=BotType.LLM_TRADEBOT,
            config_data={}
        ),
        BotConfig(
            bot_name="MarketBot-1",
            bot_type=BotType.MARKETBOT,
            config_data={}
        ),
    ]
    
    # 初始化管理器
    manager = initialize_bot_manager(configs)
    print(f"Registered {len(manager.bots)} bots")
    print(manager.get_bot_list())
