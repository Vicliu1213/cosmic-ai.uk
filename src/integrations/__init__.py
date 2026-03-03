#!/usr/bin/env python3
"""
Cosmic AI 集成模塊
Cosmic AI Integration Module

提供與外部系統的集成橋接:
- MarketBot: 25+ 多渠道通知系統
- LLM-TradeBot: 多代理決策系統
- AgentOlympics: 代理信誉與競技場系統
- 其他交易 Bot 集成
"""

from .base_bridge import (
    BaseBridge,
    TradingSignal,
    NotificationMessage,
    SignalType,
    ChannelType,
    PriorityLevel,
    BridgeManager,
)
from .marketbot_connector import (
    MarketBotConnector,
    MarketBotMessage,
    MarketBotChannelMapping,
)
from .llm_tradebot_router import (
    LLMTradeBotRouter,
    AgentDecision,
)
from .agentolympics_connector import (
    AgentOlympicsConnector,
    AgentProfile,
    ReputationScore,
    ArenaCompetition,
    AuditLog,
    CompetitionType,
    AuditLevel,
)

__all__ = [
    # Base classes
    "BaseBridge",
    "BridgeManager",
    # Data models
    "TradingSignal",
    "NotificationMessage",
    "MarketBotMessage",
    "AgentDecision",
    "AgentProfile",
    "ReputationScore",
    "ArenaCompetition",
    "AuditLog",
    # Enums
    "SignalType",
    "ChannelType",
    "PriorityLevel",
    "MarketBotChannelMapping",
    "CompetitionType",
    "AuditLevel",
    # Connectors
    "MarketBotConnector",
    "LLMTradeBotRouter",
    "AgentOlympicsConnector",
]
