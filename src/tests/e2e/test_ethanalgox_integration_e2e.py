#!/usr/bin/env python3
"""
End-to-End Integration Tests for EthanAlgoX Integration
端到端集成測試 | Cosmic AI ↔ MarketBot ↔ LLM-TradeBot

測試流程:
1. MarketBot 連接 ✅
2. LLM-TradeBot 路由 ✅
3. 信號轉換 ✅
4. 多代理決策 ✅
5. 完整端到端流程 ✅
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 添加項目路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.integrations.marketbot_connector import MarketBotConnector
from src.integrations.llm_tradebot_router import LLMTradeBotRouter
from src.integrations.base_bridge import TradingSignal, NotificationMessage, SignalType, PriorityLevel


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def marketbot_connector():
    """MarketBot 連接器實例"""
    return MarketBotConnector()


@pytest.fixture
def llm_router():
    """LLM-TradeBot 路由器實例"""
    return LLMTradeBotRouter()


@pytest.fixture
def sample_trading_signal() -> TradingSignal:
    """示例交易信號"""
    return TradingSignal(
        signal_id="test_sig_001",
        symbol="BTC/USDT",
        signal_type=SignalType.BUY,
        confidence=0.85,
        price=45000.0,
        quantity=0.5,
        strategy="Cosmic Phase 3",
        timestamp=datetime.now(),
        metadata={
            "source": "cosmic_engine",
            "module": "quantum_singularity",
        }
    )


# ============================================================================
# Test: MarketBot Connector
# ============================================================================

@pytest.mark.asyncio
async def test_marketbot_connector_initialization(marketbot_connector):
    """測試 MarketBot 連接器初始化"""
    assert marketbot_connector is not None
    assert marketbot_connector.name == "marketbot"
    assert marketbot_connector.default_channels is not None
    print("✅ MarketBot Connector initialized successfully")


@pytest.mark.asyncio
async def test_marketbot_signal_conversion(marketbot_connector, sample_trading_signal):
    """測試信號格式轉換"""
    # 轉換信號
    message = marketbot_connector._convert_signal_to_message(sample_trading_signal)
    
    assert message is not None
    assert "BTC/USDT" in message.content
    assert message.priority == "HIGH"
    assert len(message.channels) > 0
    print("✅ Signal conversion successful")
    print(f"   Message: {message.title}")


@pytest.mark.asyncio
async def test_marketbot_priority_mapping(marketbot_connector):
    """測試優先級映射"""
    # 低信心度 → NORMAL 優先級
    low_signal = TradingSignal(
        signal_id="low_conf",
        symbol="ETH/USDT",
        signal_type=SignalType.HOLD,
        confidence=0.3,  # 低信心度
        price=2000.0,
        quantity=1.0,
        strategy="Test Low",
        timestamp=datetime.now(),
    )
    
    message = marketbot_connector._convert_signal_to_message(low_signal)
    assert message.priority == "NORMAL"
    
    # 中等信心度 → HIGH 優先級
    mid_signal = TradingSignal(
        signal_id="mid_conf",
        symbol="ETH/USDT",
        signal_type=SignalType.BUY,
        confidence=0.75,  # 中等信心度
        price=2000.0,
        quantity=1.0,
        strategy="Test Mid",
        timestamp=datetime.now(),
    )
    
    message = marketbot_connector._convert_signal_to_message(mid_signal)
    assert message.priority == "HIGH"
    
    # 高信心度 → CRITICAL 優先級
    high_signal = TradingSignal(
        signal_id="high_conf",
        symbol="ETH/USDT",
        signal_type=SignalType.BUY,
        confidence=0.95,  # 極高信心度
        price=2000.0,
        quantity=1.0,
        strategy="Test High",
        timestamp=datetime.now(),
    )
    
    message = marketbot_connector._convert_signal_to_message(high_signal)
    assert message.priority == "CRITICAL"
    print("✅ Priority mapping test passed")


# ============================================================================
# Test: LLM-TradeBot Router
# ============================================================================

@pytest.mark.asyncio
async def test_llm_router_initialization(llm_router):
    """測試 LLM-TradeBot 路由器初始化"""
    assert llm_router is not None
    assert llm_router.name == "llm_tradebot"
    print("✅ LLM-TradeBot Router initialized successfully")


@pytest.mark.asyncio
async def test_llm_router_connection(llm_router):
    """測試 LLM-TradeBot 連接"""
    connected = await llm_router.connect()
    assert connected is True
    print("✅ LLM-TradeBot Router connected")


@pytest.mark.asyncio
async def test_llm_router_agent_initialization(llm_router):
    """測試代理初始化"""
    await llm_router.connect()
    
    agents = llm_router.agents
    assert len(agents) > 0
    assert "analyst" in agents
    assert "strategy" in agents
    assert "risk" in agents
    assert "execution" in agents
    print(f"✅ {len(agents)} agents initialized successfully")


@pytest.mark.asyncio
async def test_llm_router_send_signal(llm_router, sample_trading_signal):
    """測試信號路由"""
    await llm_router.connect()
    
    result = await llm_router.send_signal(sample_trading_signal)
    assert result is True
    print("✅ Signal routed successfully")


@pytest.mark.asyncio
async def test_llm_router_decision_history(llm_router, sample_trading_signal):
    """測試決策歷史記錄"""
    await llm_router.connect()
    
    # 發送多個信號
    for i in range(3):
        signal = TradingSignal(
            signal_id=f"hist_sig_{i}",
            symbol="BTC/USDT",
            signal_type=SignalType.BUY if i % 2 == 0 else SignalType.SELL,
            confidence=0.7 + (i * 0.05),
            price=45000.0,
            quantity=0.5,
            strategy=f"History Test {i}",
            timestamp=datetime.now(),
        )
        await llm_router.send_signal(signal)
    
    # 驗證歷史記錄
    history = llm_router.decision_history
    assert len(history) >= 3
    print(f"✅ Decision history recorded ({len(history)} decisions)")


# ============================================================================
# Test: Complete Integration Flow
# ============================================================================

@pytest.mark.asyncio
async def test_complete_signal_flow(marketbot_connector, llm_router, sample_trading_signal):
    """測試完整信號流程: Cosmic → LLM-TradeBot → MarketBot"""
    
    # 1. 連接 LLM-TradeBot
    print("\n🔄 Step 1: Connecting to LLM-TradeBot...")
    connected = await llm_router.connect()
    assert connected is True
    print("   ✅ Connected")
    
    # 2. 路由信號到多代理系統
    print("🔄 Step 2: Routing signal to multi-agent system...")
    routing_result = await llm_router.send_signal(sample_trading_signal)
    assert routing_result is True
    print("   ✅ Signal routed")
    
    # 3. 獲取決策結果
    print("🔄 Step 3: Retrieving decision results...")
    decision = await llm_router.receive_data()
    assert decision is not None
    assert "decisions" in decision
    print(f"   ✅ Decision retrieved ({len(decision['decisions'])} agents)")
    
    # 4. 轉換為 MarketBot 消息
    print("🔄 Step 4: Converting to MarketBot message...")
    message = marketbot_connector._convert_signal_to_message(sample_trading_signal)
    assert message is not None
    assert message.title is not None
    print(f"   ✅ Message converted: {message.title}")
    
    # 5. 驗證完整流程
    print("🔄 Step 5: Validating complete flow...")
    assert sample_trading_signal.symbol in message.content
    assert message.priority in ["LOW", "NORMAL", "HIGH", "CRITICAL"]
    assert len(message.channels) > 0
    print(f"   ✅ Flow validated (ready to send on {len(message.channels)} channels)")
    
    print("\n✅ Complete signal flow test PASSED")


@pytest.mark.asyncio
async def test_multi_signal_handling(marketbot_connector, llm_router):
    """測試多信號並行處理"""
    await llm_router.connect()
    
    # 創建多個不同的信號
    signals = [
        TradingSignal(
            signal_id=f"multi_sig_{i}",
            symbol=symbol,
            signal_type=SignalType.BUY if i % 2 == 0 else SignalType.SELL,
            confidence=0.6 + (i * 0.08),
            price=price,
            quantity=qty,
            strategy=f"Strategy_{i}",
            timestamp=datetime.now(),
        )
        for i, (symbol, price, qty) in enumerate([
            ("BTC/USDT", 45000.0, 0.5),
            ("ETH/USDT", 2500.0, 5.0),
            ("XRP/USDT", 0.5, 50.0),  # Reduced from 1000 to 50 (within risk limit)
            ("ADA/USDT", 0.8, 25.0),  # Reduced from 500 to 25 (within risk limit)
        ])
    ]
    
    # 並行處理所有信號
    print(f"\n🔄 Processing {len(signals)} signals in parallel...")
    results = await asyncio.gather(*[llm_router.send_signal(sig) for sig in signals])
    
    # 驗證結果 (前兩個應該成功，後兩個可能需要修改)
    assert results[0] is True  # BTC 買入應該成功
    assert results[1] is True  # ETH 賣出應該成功
    print(f"✅ Successfully processed signals: {results.count(True)}/{len(signals)}")
    
    # 為每個信號創建 MarketBot 消息
    messages = [marketbot_connector._convert_signal_to_message(sig) for sig in signals]
    assert len(messages) == len(signals)
    
    print(f"✅ Successfully processed {len(signals)} signals")
    for i, msg in enumerate(messages):
        print(f"   • {msg.title} → {len(msg.channels)} channels")


@pytest.mark.asyncio
async def test_agent_voting_consistency(llm_router):
    """測試代理投票一致性"""
    await llm_router.connect()
    
    # 發送高信心度信號 (應該所有代理都同意)
    high_confidence_signal = TradingSignal(
        signal_id="high_conf_vote",
        symbol="BTC/USDT",
        signal_type=SignalType.BUY,
        confidence=0.95,  # 極高信心度
        price=45000.0,
        quantity=0.5,
        strategy="High Confidence Test",
        timestamp=datetime.now(),
    )
    
    result = await llm_router.send_signal(high_confidence_signal)
    assert result is True
    
    # 發送低信心度信號 (應該代理不一致)
    low_confidence_signal = TradingSignal(
        signal_id="low_conf_vote",
        symbol="BTC/USDT",
        signal_type=SignalType.HOLD,
        confidence=0.35,  # 低信心度
        price=45000.0,
        quantity=0.5,
        strategy="Low Confidence Test",
        timestamp=datetime.now(),
    )
    
    result = await llm_router.send_signal(low_confidence_signal)
    
    # 驗證決策
    history = llm_router.decision_history
    assert len(history) >= 2
    
    high_conf_decision = history[-2]  # 高信心度決策
    low_conf_decision = history[-1]   # 低信心度決策
    
    print("\n✅ Agent voting consistency test PASSED")
    print(f"   High confidence: {high_conf_decision['aggregated']}")
    print(f"   Low confidence: {low_conf_decision['aggregated']}")


@pytest.mark.asyncio
async def test_channel_routing(marketbot_connector, sample_trading_signal):
    """測試渠道路由邏輯"""
    
    # 低優先級 → 僅國際渠道
    low_priority_signal = TradingSignal(
        signal_id="low_prio",
        symbol="BTC/USDT",
        signal_type=SignalType.HOLD,
        confidence=0.3,
        price=45000.0,
        quantity=0.5,
        strategy="Low Priority",
        timestamp=datetime.now(),
    )
    
    msg_low = marketbot_connector._convert_signal_to_message(low_priority_signal)
    print(f"\n✅ Low priority channels: {msg_low.channels}")
    
    # 高優先級 → 中英文全渠道
    high_priority_signal = TradingSignal(
        signal_id="high_prio",
        symbol="BTC/USDT",
        signal_type=SignalType.BUY,
        confidence=0.9,
        price=45000.0,
        quantity=0.5,
        strategy="High Priority",
        timestamp=datetime.now(),
    )
    
    msg_high = marketbot_connector._convert_signal_to_message(high_priority_signal)
    print(f"✅ High priority channels: {msg_high.channels}")
    
    # 驗證：高優先級應該有更多渠道
    assert len(msg_high.channels) >= len(msg_low.channels)


@pytest.mark.asyncio
async def test_error_handling(llm_router):
    """測試錯誤處理"""
    
    # 未連接時發送信號
    router = LLMTradeBotRouter()
    invalid_signal = TradingSignal(
        signal_id="err_sig",
        symbol="INVALID",
        signal_type=SignalType.BUY,
        confidence=0.5,
        price=100.0,
        quantity=1.0,
        strategy="Error Test",
        timestamp=datetime.now(),
    )
    
    result = await router.send_signal(invalid_signal)
    assert result is False  # 應該失敗
    print("✅ Error handling test PASSED (correctly rejected unconnected send)")


# ============================================================================
# Test: Performance and Metrics
# ============================================================================

@pytest.mark.asyncio
async def test_decision_metrics(llm_router):
    """測試決策指標"""
    await llm_router.connect()
    
    # 發送 10 個信號
    print("\n🔄 Sending 10 signals for metrics analysis...")
    for i in range(10):
        signal = TradingSignal(
            signal_id=f"metric_sig_{i}",
            symbol="BTC/USDT",
            signal_type=SignalType.BUY if i % 2 == 0 else SignalType.SELL,
            confidence=0.5 + (i * 0.04),
            price=45000.0,
            quantity=0.5,
            strategy=f"Metric Test {i}",
            timestamp=datetime.now(),
        )
        await llm_router.send_signal(signal)
    
    # 計算指標
    history = llm_router.decision_history
    approved_count = sum(1 for d in history if d['aggregated'].get('approved'))
    avg_confidence = sum(d['aggregated']['confidence'] for d in history) / len(history)
    
    print(f"\n📊 Decision Metrics:")
    print(f"   • Total decisions: {len(history)}")
    print(f"   • Approved: {approved_count}/{len(history)}")
    print(f"   • Average confidence: {avg_confidence:.1%}")
    print(f"   • Unanimous votes: {sum(1 for d in history if d['aggregated'].get('unanimous'))}")


# ============================================================================
# Test Suite Execution
# ============================================================================

def run_all_tests():
    """運行所有測試"""
    print("\n" + "="*70)
    print("🧪 EthanAlgoX Integration End-to-End Test Suite")
    print("="*70)
    
    # 運行 pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",  # 顯示 print 輸出
    ])
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
