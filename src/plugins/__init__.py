#!/usr/bin/env python3
"""
Plugins Module
插件模塊

Plugin system for Comic AI including multi-agent trading components.
Comic AI 的插件系統，包括多智能體交易組件。
"""

import logging

logger = logging.getLogger(__name__)

# Export main components
from .multi_agent_trading import (
    BaseAgent,
    PortfolioManagementAgent,
    RiskManagementAgent,
    SignalAnalysisAgent,
    MultiAgentCoordinator,
    TradingDecision,
    DecisionType,
    AgentRole,
    PortfolioState,
    MarketData
)

__all__ = [
    'BaseAgent',
    'PortfolioManagementAgent',
    'RiskManagementAgent',
    'SignalAnalysisAgent',
    'MultiAgentCoordinator',
    'TradingDecision',
    'DecisionType',
    'AgentRole',
    'PortfolioState',
    'MarketData'
]
