#!/usr/bin/env python3
"""
LLM-TradeBot 與 Cosmic AI 系統集成橋接層

功能：
- 連接 LLM-TradeBot 的多代理系統
- 連接 Cosmic AI 的交易引擎
- 統一面板和實時監控
"""

import asyncio
import json
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LLMTradeBotBridge:
    """LLM-TradeBot 橋接層"""
    
    def __init__(self, llm_tradebot_path: str = "/workspaces/cosmic-ai.uk/external/llm_tradebot"):
        """初始化橋接層"""
        self.llm_path = Path(llm_tradebot_path)
        self.running = False
        self.current_state = {
            "agents": {},
            "signals": [],
            "metrics": {},
            "last_update": datetime.now().isoformat()
        }
    
    async def initialize(self):
        """初始化 LLM-TradeBot 連接"""
        logger.info("初始化 LLM-TradeBot 橋接層")
        
        # 嘗試加載配置
        config_path = self.llm_path / "config.example.yaml"
        if config_path.exists():
            logger.info(f"找到配置文件: {config_path}")
        
        self.running = True
    
    async def get_agent_state(self) -> Dict[str, Any]:
        """獲取代理狀態"""
        return self.current_state.get("agents", {})
    
    async def get_signals(self, limit: int = 20) -> list:
        """獲取最近信號"""
        return self.current_state.get("signals", [])[-limit:]
    
    async def get_metrics(self) -> Dict[str, Any]:
        """獲取交易指標"""
        return self.current_state.get("metrics", {})
    
    async def start_trading(self):
        """開始交易"""
        logger.info("LLM-TradeBot 交易已啟動")
        self.running = True
        self.current_state["last_update"] = datetime.now().isoformat()
    
    async def stop_trading(self):
        """停止交易"""
        logger.info("LLM-TradeBot 交易已停止")
        self.running = False
        self.current_state["last_update"] = datetime.now().isoformat()
    
    async def pause_trading(self):
        """暫停交易"""
        logger.info("LLM-TradeBot 交易已暫停")
        self.running = False
    
    def update_agent_state(self, agent_name: str, state: Dict[str, Any]):
        """更新代理狀態"""
        self.current_state["agents"][agent_name] = state
        self.current_state["last_update"] = datetime.now().isoformat()
    
    def add_signal(self, signal: Dict[str, Any]):
        """添加信號"""
        self.current_state["signals"].append(signal)
        # 保持最近 100 個信號
        if len(self.current_state["signals"]) > 100:
            self.current_state["signals"] = self.current_state["signals"][-100:]
        self.current_state["last_update"] = datetime.now().isoformat()
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """更新指標"""
        self.current_state["metrics"] = metrics
        self.current_state["last_update"] = datetime.now().isoformat()


class CosmicSignalBridge:
    """Cosmic 信號橋接層"""
    
    def __init__(self, cosmic_path: str = "/workspaces/cosmic-ai.uk/src"):
        """初始化 Cosmic 橋接層"""
        self.cosmic_path = Path(cosmic_path)
        self.signals = []
        self.last_update = datetime.now().isoformat()
    
    async def initialize(self):
        """初始化 Cosmic 連接"""
        logger.info("初始化 Cosmic 信號橋接層")
    
    def add_signal(self, signal: Dict[str, Any]):
        """添加 Cosmic 信號"""
        self.signals.append(signal)
        if len(self.signals) > 100:
            self.signals = self.signals[-100:]
        self.last_update = datetime.now().isoformat()
    
    def get_signals(self, limit: int = 20) -> list:
        """獲取最近信號"""
        return self.signals[-limit:]
    
    async def get_arbitrage_opportunities(self) -> list:
        """獲取套利機會"""
        return []
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """獲取性能指標"""
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0
        }


class UnifiedPanelBridge:
    """統一面版橋接層"""
    
    def __init__(self):
        """初始化統一面版"""
        self.llm_bridge = LLMTradeBotBridge()
        self.cosmic_bridge = CosmicSignalBridge()
        self.subscribers = []
    
    async def initialize(self):
        """初始化所有橋接層"""
        await self.llm_bridge.initialize()
        await self.cosmic_bridge.initialize()
        logger.info("統一面版橋接層初始化完成")
    
    def subscribe(self, callback):
        """訂閱更新"""
        self.subscribers.append(callback)
    
    async def publish_update(self, update_type: str, data: Dict[str, Any]):
        """發布更新"""
        for callback in self.subscribers:
            try:
                await callback(update_type, data)
            except Exception as e:
                logger.error(f"訂閱者回調失敗: {e}")
    
    async def get_unified_state(self) -> Dict[str, Any]:
        """獲取統一狀態"""
        return {
            "llm_agents": await self.llm_bridge.get_agent_state(),
            "cosmic_signals": self.cosmic_bridge.get_signals(),
            "metrics": await self.llm_bridge.get_metrics(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def start_system(self):
        """啟動系統"""
        await self.llm_bridge.start_trading()
        await self.publish_update("system_started", {"status": "running"})
    
    async def stop_system(self):
        """停止系統"""
        await self.llm_bridge.stop_trading()
        await self.publish_update("system_stopped", {"status": "stopped"})
    
    async def pause_system(self):
        """暫停系統"""
        await self.llm_bridge.pause_trading()
        await self.publish_update("system_paused", {"status": "paused"})


# 全局實例
unified_bridge = UnifiedPanelBridge()


async def initialize_bridges():
    """初始化所有橋接層"""
    await unified_bridge.initialize()


if __name__ == "__main__":
    asyncio.run(initialize_bridges())
