#!/usr/bin/env python3
"""
MarketBot Connector - Cosmic AI 與 MarketBot 的高級連接層
MarketBot 連接器 | 支持 25+ 多渠道交付

功能:
  1. 將 Cosmic 交易信號轉換為 MarketBot 消息格式
  2. 支持多渠道交付 (DingTalk, WeChat, Telegram 等)
  3. 實時監控面板更新
  4. 交易記錄同步和性能追蹤
"""

from typing import Dict, List, Optional, Any, Set
import asyncio
import aiohttp
from dataclasses import dataclass
from datetime import datetime
import logging
import json
from enum import Enum
import time

from .base_bridge import (
    BaseBridge, TradingSignal, NotificationMessage, 
    ChannelType, PriorityLevel, SignalType
)

logger = logging.getLogger(__name__)


# ============================================================================
# MarketBot 特定數據類型
# ============================================================================

class MarketBotChannelMapping(Enum):
    """MarketBot 渠道映射"""
    DINGTALK = "dingtalk"      # 釘釘 (中文)
    WECOM = "wecom"            # 企業微信 (中文)
    FEISHU = "feishu"          # 飛書 (中文)
    LARK = "lark"              # Lark (國際)
    TELEGRAM = "telegram"      # Telegram (國際)
    DISCORD = "discord"        # Discord (國際)
    SLACK = "slack"            # Slack (國際)
    EMAIL = "email"            # Email
    SMS = "sms"                # SMS
    WEBHOOK = "webhook"        # 通用 Webhook


@dataclass
class MarketBotMessage:
    """MarketBot 消息格式"""
    title: str
    content: str
    channels: List[str]  # 選用 MarketBot 通道列表
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    tags: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "title": self.title,
            "content": self.content,
            "channels": self.channels,
            "priority": self.priority,
            "tags": self.tags or [],
            "data": self.data or {},
        }


# ============================================================================
# MarketBot 連接器
# ============================================================================

class MarketBotConnector(BaseBridge):
    """
    MarketBot 高級連接器
    
    功能:
    - 多渠道消息發送
    - 實時監控更新
    - 交易信號轉換
    - 性能追蹤
    """
    
    # 默認通道列表 (支持中文IM優先)
    DEFAULT_CHANNELS = [
        MarketBotChannelMapping.DINGTALK.value,      # 釘釘 (主要)
        MarketBotChannelMapping.WECOM.value,         # 企業微信
        MarketBotChannelMapping.TELEGRAM.value,      # Telegram
        MarketBotChannelMapping.DISCORD.value,       # Discord
    ]
    
    # 優先級映射
    PRIORITY_MAPPING = {
        PriorityLevel.LOW: "LOW",
        PriorityLevel.NORMAL: "NORMAL",
        PriorityLevel.HIGH: "HIGH",
        PriorityLevel.CRITICAL: "CRITICAL",
    }
    
    def __init__(
        self, 
        gateway_url: str = "http://127.0.0.1:18789",
        gateway_token: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 MarketBot 連接器
        
        Args:
            gateway_url: MarketBot Gateway URL
            gateway_token: 認證 token
            config: 配置字典
        """
        config = config or {}
        super().__init__("marketbot", config)
        
        self.gateway_url = gateway_url
        self.gateway_token = gateway_token
        self.session: Optional[aiohttp.ClientSession] = None
        self.default_channels = config.get("channels", self.DEFAULT_CHANNELS)
        self.monitor_enabled = config.get("monitor_enabled", True)
        
        # 統計信息
        self.stats = {
            "messages_sent": 0,
            "messages_failed": 0,
            "signals_received": 0,
            "last_update": None,
        }
    
    async def connect(self) -> bool:
        """連接到 MarketBot Gateway"""
        try:
            if self.session is not None:
                await self.session.close()
            
            self.session = aiohttp.ClientSession()
            
            # 測試連接
            headers = self._get_headers()
            async with self.session.get(
                f"{self.gateway_url}/health",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    self._is_connected = True
                    self.logger.info(f"Connected to MarketBot at {self.gateway_url}")
                    return True
                else:
                    self.logger.error(f"Failed to connect: HTTP {resp.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            await self.handle_error(e, "connect")
            return False
    
    async def disconnect(self) -> bool:
        """斷開連接"""
        try:
            if self.session:
                await self.session.close()
            self._is_connected = False
            self.logger.info("Disconnected from MarketBot")
            return True
        except Exception as e:
            self.logger.error(f"Disconnection error: {e}")
            return False
    
    async def send_signal(self, signal: TradingSignal) -> bool:
        """
        發送交易信號到 MarketBot
        
        Args:
            signal: 交易信號
            
        Returns:
            bool: 是否發送成功
        """
        if not self.is_connected:
            self.logger.warning("Not connected to MarketBot")
            return False
        
        try:
            # 轉換信號為 MarketBot 消息
            msg = self._convert_signal_to_message(signal)
            
            # 發送消息
            result = await self._send_message(msg)
            
            if result:
                self.stats["messages_sent"] += 1
                self.stats["signals_received"] += 1
                self.logger.info(f"Signal sent: {signal.signal_id}")
                return True
            else:
                self.stats["messages_failed"] += 1
                return False
        except Exception as e:
            self.logger.error(f"Error sending signal: {e}")
            await self.handle_error(e, "send_signal")
            self.stats["messages_failed"] += 1
            return False
    
    async def send_notification(self, msg: NotificationMessage) -> bool:
        """
        發送通知消息
        
        Args:
            msg: 通知消息
            
        Returns:
            bool: 是否發送成功
        """
        if not self.is_connected:
            self.logger.warning("Not connected to MarketBot")
            return False
        
        try:
            # 轉換通知為 MarketBot 消息
            mb_msg = self._convert_notification_to_message(msg)
            
            # 發送消息
            result = await self._send_message(mb_msg)
            
            if result:
                self.stats["messages_sent"] += 1
                self.logger.info(f"Notification sent: {msg.title}")
                return True
            else:
                self.stats["messages_failed"] += 1
                return False
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            await self.handle_error(e, "send_notification")
            self.stats["messages_failed"] += 1
            return False
    
    async def receive_data(self) -> Optional[Dict[str, Any]]:
        """
        從 MarketBot 接收數據 (webhook 回調)
        
        Returns:
            Optional[Dict]: 接收到的數據
        """
        # 這通常由 webhook 端點處理
        # 此方法可用於拉取待處理消息
        try:
            if not self.is_connected or self.session is None:
                return None
            
            headers = self._get_headers()
            async with self.session.get(
                f"{self.gateway_url}/pending",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                return None
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            return None
    
    # ========================================================================
    # 私有方法
    # ========================================================================
    
    def _get_headers(self) -> Dict[str, str]:
        """獲取請求頭"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CosmicAI/1.0",
        }
        if self.gateway_token:
            headers["Authorization"] = f"Bearer {self.gateway_token}"
        return headers
    
    def _convert_signal_to_message(self, signal: TradingSignal) -> MarketBotMessage:
        """
        將交易信號轉換為 MarketBot 消息
        
        Args:
            signal: 交易信號
            
        Returns:
            MarketBotMessage: MarketBot 消息
        """
        # 根據信號類型和信心度判斷優先級
        if signal.confidence >= 0.9 and signal.signal_type != SignalType.HOLD:
            priority = "CRITICAL"
        elif signal.confidence >= 0.7:
            priority = "HIGH"
        else:
            priority = "NORMAL"
        
        # 構建消息內容
        title = f"🎯 {signal.strategy} - {signal.signal_type.value} {signal.symbol}"
        
        content = f"""
📊 交易信號詳情
─────────────────
🔔 信號: {signal.signal_type.value}
📈 品種: {signal.symbol}
💰 價格: {signal.price:.2f}
📦 數量: {signal.quantity:.4f}
💪 信心度: {signal.confidence * 100:.1f}%
🎯 策略: {signal.strategy}
⏰ 時間: {signal.timestamp.isoformat()}

{'🛑 止損: {signal.stop_loss:.2f}' if signal.stop_loss else ''}
{'🎁 止盈: {signal.take_profit:.2f}' if signal.take_profit else ''}
        """.strip()
        
        # 構建標籤
        tags = [
            signal.strategy,
            signal.symbol,
            signal.signal_type.value,
            f"confidence-{int(signal.confidence * 10)}0",
        ]
        
        return MarketBotMessage(
            title=title,
            content=content,
            channels=self.default_channels,
            priority=priority,
            tags=tags,
            data={
                "signal_id": signal.signal_id,
                "symbol": signal.symbol,
                "signal_type": signal.signal_type.value,
                "confidence": signal.confidence,
                "price": signal.price,
                "quantity": signal.quantity,
            }
        )
    
    def _convert_notification_to_message(
        self, 
        notification: NotificationMessage
    ) -> MarketBotMessage:
        """
        將通知轉換為 MarketBot 消息
        
        Args:
            notification: 通知消息
            
        Returns:
            MarketBotMessage: MarketBot 消息
        """
        # 選擇通道 (優先使用中文IM)
        channels = []
        for ch in notification.channels:
            if ch == ChannelType.DINGTALK:
                channels.append(MarketBotChannelMapping.DINGTALK.value)
            elif ch == ChannelType.WECOM:
                channels.append(MarketBotChannelMapping.WECOM.value)
            elif ch == ChannelType.TELEGRAM:
                channels.append(MarketBotChannelMapping.TELEGRAM.value)
            elif ch == ChannelType.DISCORD:
                channels.append(MarketBotChannelMapping.DISCORD.value)
        
        if not channels:
            channels = self.default_channels
        
        return MarketBotMessage(
            title=notification.title,
            content=notification.content,
            channels=channels,
            priority=self.PRIORITY_MAPPING.get(notification.priority, "NORMAL"),
            tags=notification.tags,
            data=notification.data,
        )
    
    async def _send_message(self, msg: MarketBotMessage) -> bool:
        """
        發送消息到 MarketBot Gateway
        
        Args:
            msg: MarketBot 消息
            
        Returns:
            bool: 是否發送成功
        """
        if not self.session:
            return False
        
        try:
            headers = self._get_headers()
            payload = msg.to_dict()
            
            async with self.session.post(
                f"{self.gateway_url}/send",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status in [200, 201]:
                    return True
                else:
                    self.logger.error(f"Send failed: HTTP {resp.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        self.stats["last_update"] = datetime.now().isoformat()
        return self.stats.copy()
