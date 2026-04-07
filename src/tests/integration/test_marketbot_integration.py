#!/usr/bin/env python3
"""
MarketBot 集成测试
Test MarketBot Integration
"""

import pytest
import asyncio
from datetime import datetime
from src.integrations.marketbot_connector import MarketBotConnector
from src.integrations.base_bridge import TradingSignal, SignalType, NotificationMessage, ChannelType, PriorityLevel


@pytest.mark.asyncio
async def test_marketbot_connector_initialization():
    """测试 MarketBot 连接器初始化"""
    connector = MarketBotConnector(
        gateway_url="http://127.0.0.1:18789",
        config={"channels": ["dingtalk", "telegram"]}
    )
    
    assert connector.name == "marketbot"
    assert connector.gateway_url == "http://127.0.0.1:18789"
    assert not connector.is_connected


@pytest.mark.asyncio
async def test_signal_to_message_conversion():
    """测试交易信号转换"""
    connector = MarketBotConnector()
    
    signal = TradingSignal(
        signal_id="test_001",
        symbol="BTC/USDT",
        signal_type=SignalType.BUY,
        confidence=0.95,
        price=50000.0,
        quantity=1.5,
        strategy="Phase 3",
        timestamp=datetime.now(),
        stop_loss=48000.0,
        take_profit=52000.0,
    )
    
    msg = connector._convert_signal_to_message(signal)
    
    assert msg.title == "🎯 Phase 3 - BUY BTC/USDT"
    assert "BTC/USDT" in msg.content
    assert msg.priority == "CRITICAL"  # 95% confidence


@pytest.mark.asyncio
async def test_notification_conversion():
    """测试通知转换"""
    connector = MarketBotConnector()
    
    notification = NotificationMessage(
        title="Test Alert",
        content="This is a test alert",
        channels=[ChannelType.DINGTALK, ChannelType.TELEGRAM],
        priority=PriorityLevel.HIGH,
    )
    
    msg = connector._convert_notification_to_message(notification)
    
    assert msg.title == "Test Alert"
    assert msg.priority == "HIGH"
    assert "dingtalk" in msg.channels


def test_marketbot_stats():
    """测试统计信息"""
    connector = MarketBotConnector()
    
    stats = connector.get_stats()
    
    assert stats["messages_sent"] == 0
    assert stats["messages_failed"] == 0
    assert stats["signals_received"] == 0
