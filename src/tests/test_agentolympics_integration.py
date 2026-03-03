#!/usr/bin/env python3
"""
AgentOlympics 集成測試
Test AgentOlympics Connector Integration

功能測試:
  1. 連接器初始化
  2. 代理註冊
  3. 信誉追蹤
  4. 競技場操作
  5. 自反思提交
"""

import pytest
import asyncio
from datetime import datetime

from src.integrations.agentolympics_connector import (
    AgentOlympicsConnector,
    CompetitionType,
    AuditLevel,
)
from src.integrations.base_bridge import TradingSignal, SignalType


@pytest.mark.asyncio
async def test_agentolympics_connector_initialization():
    """測試 AgentOlympics 連接器初始化"""
    config = {
        "agent_name": "TestAgent",
        "agent_type": "trading_strategy",
        "reputation_enabled": True,
        "arena_enabled": True,
    }
    
    connector = AgentOlympicsConnector(
        api_url="https://api.agenolympics.com",
        api_key="test_key_123",
        workspace_id="workspace_456",
        config=config,
    )
    
    assert connector.agent_name == "TestAgent"
    assert connector.agent_type == "trading_strategy"
    assert connector.reputation_enabled is True
    assert connector.arena_enabled is True
    assert connector.is_connected is False


@pytest.mark.asyncio
async def test_agentolympics_stats():
    """測試統計信息"""
    connector = AgentOlympicsConnector()
    stats = connector.get_stats()
    
    assert "agent_registered" in stats
    assert "reputation_updates" in stats
    assert "competitions_joined" in stats
    assert "audit_logs_submitted" in stats
    assert "reflections_submitted" in stats
    
    assert stats["agent_registered"] is False
    assert stats["reputation_updates"] == 0
    assert stats["competitions_joined"] == 0


@pytest.mark.asyncio
async def test_agent_profile_creation():
    """測試代理檔案創建"""
    from src.integrations.agentolympics_connector import AgentProfile
    
    profile = AgentProfile(
        agent_id="agent_001",
        agent_name="CosmicAI",
        agent_type="trading",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        reputation_score=85.5,
        total_trades=100,
        win_rate=0.65,
    )
    
    assert profile.agent_id == "agent_001"
    assert profile.agent_name == "CosmicAI"
    assert profile.reputation_score == 85.5
    assert profile.win_rate == 0.65


@pytest.mark.asyncio
async def test_reputation_score_tracking():
    """測試信誉分數追蹤"""
    from src.integrations.agentolympics_connector import ReputationScore
    
    score = ReputationScore(
        agent_id="agent_001",
        current_score=90.0,
        previous_score=85.0,
        change=5.0,
        components={
            "performance": 0.4,
            "consistency": 0.3,
            "innovation": 0.3,
        },
        timestamp=datetime.utcnow(),
        reason="Strong performance in Q1",
    )
    
    assert score.current_score == 90.0
    assert score.change == 5.0
    assert "performance" in score.components


@pytest.mark.asyncio
async def test_arena_competition_creation():
    """測試競技場競賽創建"""
    from src.integrations.agentolympics_connector import ArenaCompetition
    
    competition = ArenaCompetition(
        competition_id="comp_001",
        competition_type=CompetitionType.PERFORMANCE,
        agent_ids=["agent_001", "agent_002", "agent_003"],
        start_time=datetime.utcnow(),
    )
    
    assert competition.competition_id == "comp_001"
    assert competition.competition_type == CompetitionType.PERFORMANCE
    assert len(competition.agent_ids) == 3


@pytest.mark.asyncio
async def test_audit_log_creation():
    """測試審計日誌創建"""
    from src.integrations.agentolympics_connector import AuditLog
    
    log = AuditLog(
        log_id="log_001",
        agent_id="agent_001",
        action="trade_executed",
        details={
            "symbol": "BTC/USDT",
            "side": "BUY",
            "quantity": 1.0,
            "price": 45000.0,
        },
        timestamp=datetime.utcnow(),
        blockchain_hash="0xabc123def456",
        verified=True,
    )
    
    assert log.log_id == "log_001"
    assert log.action == "trade_executed"
    assert log.verified is True
    assert "symbol" in log.details


@pytest.mark.asyncio
async def test_competition_type_enum():
    """測試競賽類型枚舉"""
    assert CompetitionType.STRATEGY.value == "strategy"
    assert CompetitionType.PERFORMANCE.value == "performance"
    assert CompetitionType.RISK_ADJUSTED.value == "risk_adjusted"
    assert CompetitionType.CONSISTENCY.value == "consistency"
    assert CompetitionType.INNOVATION.value == "innovation"


@pytest.mark.asyncio
async def test_audit_level_enum():
    """測試審計級別枚舉"""
    assert AuditLevel.MINIMAL.value == "minimal"
    assert AuditLevel.STANDARD.value == "standard"
    assert AuditLevel.DETAILED.value == "detailed"
    assert AuditLevel.BLOCKCHAIN.value == "blockchain"


@pytest.mark.asyncio
async def test_connector_with_all_features():
    """測試連接器的所有功能開關"""
    config = {
        "agent_name": "FullFeaturedAgent",
        "reputation_enabled": True,
        "arena_enabled": True,
        "audit_enabled": True,
        "learning_enabled": True,
        "audit_level": "blockchain",
        "blockchain_enabled": True,
    }
    
    connector = AgentOlympicsConnector(config=config)
    
    assert connector.reputation_enabled is True
    assert connector.arena_enabled is True
    assert connector.audit_enabled is True
    assert connector.learning_enabled is True
    assert connector.audit_level == AuditLevel.BLOCKCHAIN
    assert connector.blockchain_enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
