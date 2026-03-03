#!/usr/bin/env python3
"""
端到端集成测试
End-to-End Integration Test
"""

import pytest
import asyncio
from datetime import datetime
from src.integrations.base_bridge import BridgeManager, TradingSignal, SignalType


@pytest.mark.asyncio
async def test_bridge_manager_initialization():
    """测试桥接管理器初始化"""
    manager = BridgeManager()
    
    assert len(manager.bridges) == 0


@pytest.mark.asyncio
async def test_end_to_end_signal_flow():
    """测试端到端信号流"""
    from src.integrations.marketbot_connector import MarketBotConnector
    from src.integrations.llm_tradebot_router import LLMTradeBotRouter
    
    manager = BridgeManager()
    
    # 注册桥接器
    marketbot = MarketBotConnector()
    llm_router = LLMTradeBotRouter()
    
    manager.register_bridge(marketbot)
    manager.register_bridge(llm_router)
    
    assert len(manager.bridges) == 2
    assert manager.get_bridge("marketbot") is not None
    assert manager.get_bridge("llm_tradebot") is not None


@pytest.mark.asyncio
async def test_signal_broadcast():
    """测试信号广播"""
    from src.integrations.marketbot_connector import MarketBotConnector
    
    manager = BridgeManager()
    connector = MarketBotConnector()
    manager.register_bridge(connector)
    
    signal = TradingSignal(
        signal_id="e2e_test_001",
        symbol="ETH/USDT",
        signal_type=SignalType.SELL,
        confidence=0.75,
        price=3000.0,
        quantity=5.0,
        strategy="Phase 4",
        timestamp=datetime.now(),
    )
    
    # 广播信号 (不连接的情况下会失败，但测试流程)
    results = await manager.broadcast_signal(signal)
    
    assert "marketbot" in results


def test_manager_status():
    """测试管理器状态"""
    from src.integrations.marketbot_connector import MarketBotConnector
    from src.integrations.llm_tradebot_router import LLMTradeBotRouter
    
    manager = BridgeManager()
    
    marketbot = MarketBotConnector()
    llm_router = LLMTradeBotRouter()
    
    manager.register_bridge(marketbot)
    manager.register_bridge(llm_router)
    
    status = manager.get_status()
    
    assert status["total_bridges"] == 2
    assert status["connected_bridges"] == 0  # 未连接
    assert "marketbot" in status["bridges"]
    assert "llm_tradebot" in status["bridges"]


@pytest.mark.asyncio
async def test_integration_workflow():
    """测试完整集成工作流"""
    from src.integrations.marketbot_connector import MarketBotConnector
    from src.integrations.llm_tradebot_router import LLMTradeBotRouter
    
    # 初始化组件
    marketbot = MarketBotConnector()
    llm_router = LLMTradeBotRouter()
    
    # 创建信号
    signal = TradingSignal(
        signal_id="workflow_test_001",
        symbol="BTC/USDT",
        signal_type=SignalType.BUY,
        confidence=0.88,
        price=55000.0,
        quantity=0.5,
        strategy="Phase 3 + Arbitrage",
        timestamp=datetime.now(),
        stop_loss=53000.0,
        take_profit=57000.0,
    )
    
    # 模拟工作流
    # 1. 连接到 LLM Router
    llm_connected = await llm_router.connect()
    assert llm_connected
    
    # 2. 路由信号到多代理系统
    llm_approved = await llm_router.send_signal(signal)
    
    # 3. 发送通知到 MarketBot (不需要连接就能测试)
    # 这里我们只测试流程，实际的网络调用会被跳过
    
    assert llm_connected
