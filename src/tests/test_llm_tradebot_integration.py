#!/usr/bin/env python3
"""
LLM-TradeBot 集成测试
Test LLM-TradeBot Integration
"""

import pytest
import asyncio
from datetime import datetime
from src.integrations.llm_tradebot_router import LLMTradeBotRouter, AgentDecision
from src.integrations.base_bridge import TradingSignal, SignalType


@pytest.mark.asyncio
async def test_llm_router_initialization():
    """测试 LLM 路由器初始化"""
    router = LLMTradeBotRouter(config={"max_history": 500})
    
    assert router.name == "llm_tradebot"
    assert not router.is_connected


@pytest.mark.asyncio
async def test_llm_router_connect():
    """测试连接到 LLM-TradeBot"""
    router = LLMTradeBotRouter()
    result = await router.connect()
    
    assert result
    assert router.is_connected


@pytest.mark.asyncio
async def test_agent_decisions():
    """测试多代理决策"""
    router = LLMTradeBotRouter()
    await router.connect()
    
    signal = TradingSignal(
        signal_id="test_001",
        symbol="BTC/USDT",
        signal_type=SignalType.BUY,
        confidence=0.85,
        price=50000.0,
        quantity=1.0,
        strategy="Phase 3",
        timestamp=datetime.now(),
    )
    
    decisions = await router._collect_agent_decisions(signal)
    
    assert len(decisions) == 4  # analyst, strategy, risk, execution
    assert all(isinstance(d, AgentDecision) for d in decisions)


@pytest.mark.asyncio
async def test_decision_aggregation():
    """测试决策聚合"""
    router = LLMTradeBotRouter()
    
    decisions = [
        AgentDecision("analyst", "analyst", "APPROVE", 0.9, "Analysis OK", timestamp=datetime.now()),
        AgentDecision("strategy", "strategy", "APPROVE", 0.85, "Strategy OK", timestamp=datetime.now()),
        AgentDecision("risk", "risk", "APPROVE", 0.7, "Risk OK", timestamp=datetime.now()),
        AgentDecision("execution", "execution", "APPROVE", 0.8, "Ready to execute", timestamp=datetime.now()),
    ]
    
    aggregated = router._aggregate_decisions(decisions)
    
    assert aggregated["approved"]
    assert aggregated["confidence"] > 0.8
    assert aggregated["unanimous"]


@pytest.mark.asyncio
async def test_router_disconnect():
    """测试断开连接"""
    router = LLMTradeBotRouter()
    await router.connect()
    
    result = await router.disconnect()
    
    assert result
    assert not router.is_connected
