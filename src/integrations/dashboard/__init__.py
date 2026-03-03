"""
LLM-TradeBot 集成面版模塊

包含：
- llm_tradebot_panel.py: FastAPI 面版應用
- bridge.py: LLM-TradeBot 和 Cosmic 橋接層
- main.py: 完整啟動服務器
- index.html: 前端界面
"""

from .llm_tradebot_panel import (
    LLMTradeBotPanelManager,
    LLMTradeBotAPI,
    create_panel_app,
    AgentState,
    CosmicSignal,
    TradingMetrics
)

from .bridge import (
    LLMTradeBotBridge,
    CosmicSignalBridge,
    UnifiedPanelBridge,
    unified_bridge,
    initialize_bridges
)

__all__ = [
    "LLMTradeBotPanelManager",
    "LLMTradeBotAPI",
    "create_panel_app",
    "AgentState",
    "CosmicSignal",
    "TradingMetrics",
    "LLMTradeBotBridge",
    "CosmicSignalBridge",
    "UnifiedPanelBridge",
    "unified_bridge",
    "initialize_bridges",
]
