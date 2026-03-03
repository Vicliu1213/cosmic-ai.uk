#!/usr/bin/env python3
"""
Base Bridge Module - EthanAlgoX 集成基礎層
基礎橋接層 | 為 MarketBot 和 LLM-TradeBot 提供統一介面

提供所有橋接器需要實現的基礎類和接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json
from typing import Generic, TypeVar

logger = logging.getLogger(__name__)

# ============================================================================
# 數據模型定義
# ============================================================================

class SignalType(Enum):
    """交易信號類型"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE = "CLOSE"
    HEDGE = "HEDGE"


class ChannelType(Enum):
    """消息渠道類型"""
    DINGTALK = "dingtalk"
    WECOM = "wecom"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class PriorityLevel(Enum):
    """優先級別"""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class TradingSignal:
    """統一交易信號格式"""
    signal_id: str
    symbol: str
    signal_type: SignalType
    confidence: float  # 0-1
    price: float
    quantity: float
    strategy: str  # 策略名稱
    timestamp: datetime
    
    # 可選字段
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "signal_type": self.signal_type.value,
            "confidence": self.confidence,
            "price": self.price,
            "quantity": self.quantity,
            "strategy": self.strategy,
            "timestamp": self.timestamp.isoformat(),
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "metadata": self.metadata,
        }


@dataclass
class NotificationMessage:
    """通知消息格式"""
    title: str
    content: str
    channels: List[ChannelType]
    priority: PriorityLevel = PriorityLevel.NORMAL
    tags: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "title": self.title,
            "content": self.content,
            "channels": [ch.value for ch in self.channels],
            "priority": self.priority.value,
            "tags": self.tags,
            "data": self.data,
        }


# ============================================================================
# 基礎橋接器類
# ============================================================================

class BaseBridge(ABC):
    """所有橋接器的基類"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        初始化基礎橋接器
        
        Args:
            name: 橋接器名稱
            config: 配置字典
        """
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"bridge.{name}")
        self._is_connected = False
        self._error_handlers: List[Callable] = []
    
    @property
    def is_connected(self) -> bool:
        """檢查是否已連接"""
        return self._is_connected
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        連接到外部系統
        
        Returns:
            bool: 連接是否成功
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        斷開連接
        
        Returns:
            bool: 斷開是否成功
        """
        pass
    
    @abstractmethod
    async def send_signal(self, signal: TradingSignal) -> bool:
        """
        發送交易信號
        
        Args:
            signal: 交易信號
            
        Returns:
            bool: 發送是否成功
        """
        pass
    
    @abstractmethod
    async def send_notification(self, msg: NotificationMessage) -> bool:
        """
        發送通知消息
        
        Args:
            msg: 通知消息
            
        Returns:
            bool: 發送是否成功
        """
        pass
    
    @abstractmethod
    async def receive_data(self) -> Optional[Dict[str, Any]]:
        """
        接收數據
        
        Returns:
            Optional[Dict]: 接收到的數據或 None
        """
        pass
    
    def add_error_handler(self, handler: Callable) -> None:
        """添加錯誤處理器"""
        self._error_handlers.append(handler)
    
    async def handle_error(self, error: Exception, context: str = "") -> None:
        """
        處理錯誤
        
        Args:
            error: 異常
            context: 錯誤上下文
        """
        self.logger.error(f"Error in {context}: {error}")
        for handler in self._error_handlers:
            try:
                await handler(error, context)
            except Exception as e:
                self.logger.error(f"Error in error handler: {e}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' connected={self._is_connected}>"


# ============================================================================
# 橋接管理器
# ============================================================================

class BridgeManager:
    """管理多個橋接器"""
    
    def __init__(self):
        """初始化橋接管理器"""
        self.bridges: Dict[str, BaseBridge] = {}
        self.logger = logging.getLogger("bridge.manager")
    
    def register_bridge(self, bridge: BaseBridge) -> None:
        """
        註冊橋接器
        
        Args:
            bridge: 橋接器實例
        """
        self.bridges[bridge.name] = bridge
        self.logger.info(f"Registered bridge: {bridge.name}")
    
    def get_bridge(self, name: str) -> Optional[BaseBridge]:
        """
        獲取橋接器
        
        Args:
            name: 橋接器名稱
            
        Returns:
            Optional[BaseBridge]: 橋接器或 None
        """
        return self.bridges.get(name)
    
    async def connect_all(self) -> bool:
        """
        連接所有橋接器
        
        Returns:
            bool: 是否全部成功
        """
        results = []
        for name, bridge in self.bridges.items():
            try:
                result = await bridge.connect()
                results.append(result)
                self.logger.info(f"Connected to {name}: {result}")
            except Exception as e:
                self.logger.error(f"Failed to connect to {name}: {e}")
                results.append(False)
        return all(results)
    
    async def disconnect_all(self) -> bool:
        """
        斷開所有橋接器
        
        Returns:
            bool: 是否全部成功
        """
        results = []
        for name, bridge in self.bridges.items():
            try:
                result = await bridge.disconnect()
                results.append(result)
                self.logger.info(f"Disconnected from {name}: {result}")
            except Exception as e:
                self.logger.error(f"Failed to disconnect from {name}: {e}")
                results.append(False)
        return all(results)
    
    async def broadcast_signal(self, signal: TradingSignal) -> Dict[str, bool]:
        """
        廣播信號到所有橋接器
        
        Args:
            signal: 交易信號
            
        Returns:
            Dict: 各橋接器的發送結果
        """
        results = {}
        for name, bridge in self.bridges.items():
            try:
                result = await bridge.send_signal(signal)
                results[name] = result
                self.logger.info(f"Signal sent to {name}: {result}")
            except Exception as e:
                self.logger.error(f"Failed to send signal to {name}: {e}")
                results[name] = False
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取所有橋接器狀態
        
        Returns:
            Dict: 狀態信息
        """
        return {
            "total_bridges": len(self.bridges),
            "connected_bridges": sum(1 for b in self.bridges.values() if b.is_connected),
            "bridges": {
                name: {
                    "connected": bridge.is_connected,
                    "type": bridge.__class__.__name__
                }
                for name, bridge in self.bridges.items()
            }
        }


# ============================================================================
# 工具函數
# ============================================================================

def load_bridge_config(config_file: str) -> Dict[str, Any]:
    """
    加載橋接配置文件
    
    Args:
        config_file: 配置文件路徑
        
    Returns:
        Dict: 配置字典
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def create_signal_from_dict(data: Dict[str, Any]) -> Optional[TradingSignal]:
    """
    從字典創建交易信號
    
    Args:
        data: 信號數據
        
    Returns:
        Optional[TradingSignal]: 信號或 None
    """
    try:
        return TradingSignal(
            signal_id=data["signal_id"],
            symbol=data["symbol"],
            signal_type=SignalType(data["signal_type"]),
            confidence=data["confidence"],
            price=data["price"],
            quantity=data["quantity"],
            strategy=data["strategy"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            metadata=data.get("metadata", {}),
        )
    except Exception as e:
        logger.error(f"Failed to create signal: {e}")
        return None
