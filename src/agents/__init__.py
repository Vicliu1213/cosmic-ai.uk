"""
Multi-Agent Trading System

基于异步并发的多Agent交易架构

Core Agents (always enabled):
- DataSyncAgent: Market data fetching
- QuantAnalystAgent: Technical analysis
- RiskAuditAgent: Risk control

Optional Agents (configurable via AgentConfig):
- PredictAgent, ReflectionAgent, RegimeDetectorAgent, etc.
"""

import logging

logger = logging.getLogger(__name__)

# 使用延遲導入以避免在模塊載入時失敗
def __getattr__(name):
    """延遲導入"""
    try:
        if name == 'AgentConfig':
            from .agent_config import AgentConfig
            return AgentConfig
        elif name == 'BaseAgent':
            from .base_agent import BaseAgent
            return BaseAgent
        elif name == 'AgentResult':
            from .base_agent import AgentResult
            return AgentResult
        elif name == 'AgentRegistry':
            from .agent_registry import AgentRegistry
            return AgentRegistry
        elif name == 'DataSyncAgent':
            from .data_sync_agent import DataSyncAgent
            return DataSyncAgent
        elif name == 'MarketSnapshot':
            from .data_sync_agent import MarketSnapshot
            return MarketSnapshot
        elif name == 'QuantAnalystAgent':
            from .quant_analyst_agent import QuantAnalystAgent
            return QuantAnalystAgent
        elif name == 'DecisionCoreAgent':
            from .decision_core_agent import DecisionCoreAgent
            return DecisionCoreAgent
        elif name == 'VoteResult':
            from .decision_core_agent import VoteResult
            return VoteResult
        elif name == 'SignalWeight':
            from .decision_core_agent import SignalWeight
            return SignalWeight
        elif name == 'RiskAuditAgent':
            from .risk_audit_agent import RiskAuditAgent
            return RiskAuditAgent
        elif name == 'RiskCheckResult':
            from .risk_audit_agent import RiskCheckResult
            return RiskCheckResult
        elif name == 'PositionInfo':
            from .risk_audit_agent import PositionInfo
            return PositionInfo
        elif name == 'RiskLevel':
            from .risk_audit_agent import RiskLevel
            return RiskLevel
        elif name == 'PredictAgent':
            from .predict_agent import PredictAgent
            return PredictAgent
        elif name == 'PredictResult':
            from .predict_agent import PredictResult
            return PredictResult
        elif name == 'ReflectionAgent':
            from .reflection_agent import ReflectionAgent
            return ReflectionAgent
        elif name == 'ReflectionAgentLLM':
            from .reflection_agent import ReflectionAgentLLM
            return ReflectionAgentLLM
        elif name == 'ReflectionResult':
            from .reflection_agent import ReflectionResult
            return ReflectionResult
        elif name == 'MultiPeriodParserAgent':
            from .multi_period_agent import MultiPeriodParserAgent
            return MultiPeriodParserAgent
    except Exception as e:
        logger.warning(f"⚠️ 無法導入 {name}: {e}")
        return None
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Framework
    'AgentConfig',
    'BaseAgent',
    'AgentResult',
    'AgentRegistry',
    # Core Agents
    'DataSyncAgent',
    'MarketSnapshot',
    'QuantAnalystAgent',
    'DecisionCoreAgent',
    'VoteResult',
    'SignalWeight',
    'RiskAuditAgent',
    'RiskCheckResult',
    'PositionInfo',
    'RiskLevel',
    # Optional Agents
    'PredictAgent',
    'PredictResult',
    'ReflectionAgent',
    'ReflectionAgentLLM',
    'ReflectionResult',
    'MultiPeriodParserAgent',
]
