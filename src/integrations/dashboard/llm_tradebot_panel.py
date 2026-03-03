#!/usr/bin/env python3
"""
LLM-TradeBot Panel Integration
集成 LLM-TradeBot 和 Cosmic AI 交易系統的統一面版

Features:
- 實時監控 LLM-TradeBot 多代理狀態
- Cosmic 系統交易信號展示
- 統一控制和配置面板
- 實時性能指標追蹤
- 代理交互和協調監控
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """代理狀態數據結構"""
    agent_name: str
    agent_type: str  # 'Trend', 'Setup', 'Trigger', 'Reflection', 'Risk'
    status: str  # 'running', 'idle', 'error'
    confidence: float = 0.0
    last_signal: Optional[str] = None
    last_update: str = ""
    performance_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }
        if not self.last_update:
            self.last_update = datetime.now().isoformat()


@dataclass
class CosmicSignal:
    """Cosmic 系統信號數據結構"""
    signal_id: str
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    sharpe_ratio: float
    confidence: float
    quantum_score: float
    timestamp: str
    resonance_level: float = 0.0
    arbitrage_opportunity: Optional[Dict[str, Any]] = None


@dataclass
class TradingMetrics:
    """交易性能指標"""
    timestamp: str
    total_trades: int
    win_rate: float
    total_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    current_balance: float
    active_positions: int
    average_trade_duration: float


class LLMTradeBotPanelManager:
    """LLM-TradeBot 面版管理器"""
    
    def __init__(self, llm_tradebot_path: str = "/workspaces/cosmic-ai.uk/external/llm_tradebot"):
        """初始化面版管理器"""
        self.llm_tradebot_path = Path(llm_tradebot_path)
        self.cosmic_path = Path("/workspaces/cosmic-ai.uk/src")
        
        # 狀態存儲
        self.agents_state: Dict[str, AgentState] = {}
        self.cosmic_signals: List[CosmicSignal] = []
        self.trading_metrics: Optional[TradingMetrics] = None
        self.active_websockets: Set[WebSocket] = set()
        
        # 加載配置
        self._load_config()
        
    def _load_config(self):
        """加載配置文件"""
        try:
            config_path = self.llm_tradebot_path / "config.example.yaml"
            if config_path.exists():
                logger.info(f"配置文件已找到: {config_path}")
        except Exception as e:
            logger.error(f"加載配置文件失敗: {e}")
    
    async def initialize(self):
        """初始化系統"""
        logger.info("初始化 LLM-TradeBot 面版管理器")
        
        # 初始化代理狀態
        agent_types = ['Trend', 'Setup', 'Trigger', 'Reflection', 'Risk']
        for agent_type in agent_types:
            agent_name = f"{agent_type}Agent"
            self.agents_state[agent_name] = AgentState(
                agent_name=agent_name,
                agent_type=agent_type,
                status="idle"
            )
        
        logger.info(f"初始化了 {len(self.agents_state)} 個代理")
    
    async def broadcast_update(self, message: Dict[str, Any]):
        """廣播更新消息給所有 WebSocket 客戶端"""
        disconnected = set()
        for ws in self.active_websockets:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"廣播消息失敗: {e}")
                disconnected.add(ws)
        
        # 清理斷開的連接
        self.active_websockets -= disconnected
    
    def get_agents_summary(self) -> Dict[str, Any]:
        """獲取所有代理的摘要"""
        return {
            "total_agents": len(self.agents_state),
            "agents": {
                name: asdict(state) for name, state in self.agents_state.items()
            }
        }
    
    def update_agent_state(self, agent_name: str, **kwargs):
        """更新代理狀態"""
        if agent_name in self.agents_state:
            agent = self.agents_state[agent_name]
            for key, value in kwargs.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)
            agent.last_update = datetime.now().isoformat()
    
    def add_cosmic_signal(self, signal: CosmicSignal):
        """添加 Cosmic 信號"""
        self.cosmic_signals.append(signal)
        # 保持最近 100 個信號
        if len(self.cosmic_signals) > 100:
            self.cosmic_signals = self.cosmic_signals[-100:]
    
    def get_cosmic_signals(self, limit: int = 20) -> List[Dict[str, Any]]:
        """獲取最近的 Cosmic 信號"""
        return [asdict(s) for s in self.cosmic_signals[-limit:]]
    
    def update_trading_metrics(self, metrics: TradingMetrics):
        """更新交易指標"""
        self.trading_metrics = metrics
    
    def get_trading_metrics(self) -> Optional[Dict[str, Any]]:
        """獲取交易指標"""
        if self.trading_metrics:
            return asdict(self.trading_metrics)
        return None


class LLMTradeBotAPI:
    """LLM-TradeBot API 端點"""
    
    def __init__(self, manager: LLMTradeBotPanelManager):
        """初始化 API"""
        self.manager = manager
        self.app = FastAPI(title="LLM-TradeBot Cosmic Panel")
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """設置中間件"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """設置 API 路由"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """啟動事件"""
            await self.manager.initialize()
            logger.info("面版 API 已啟動")
        
        @self.app.get("/api/health")
        async def health_check():
            """健康檢查"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agents_online": len(self.manager.agents_state)
            }
        
        @self.app.get("/api/agents/summary")
        async def agents_summary():
            """獲取代理摘要"""
            return self.manager.get_agents_summary()
        
        @self.app.post("/api/agents/{agent_name}/update")
        async def update_agent(agent_name: str, data: Dict[str, Any]):
            """更新代理狀態"""
            self.manager.update_agent_state(agent_name, **data)
            return {"status": "updated"}
        
        @self.app.get("/api/signals/cosmic")
        async def get_cosmic_signals(limit: int = 20):
            """獲取 Cosmic 信號"""
            return self.manager.get_cosmic_signals(limit)
        
        @self.app.post("/api/signals/cosmic")
        async def add_cosmic_signal(signal: Dict[str, Any]):
            """添加 Cosmic 信號"""
            try:
                cosmic_signal = CosmicSignal(**signal)
                self.manager.add_cosmic_signal(cosmic_signal)
                
                # 廣播更新
                await self.manager.broadcast_update({
                    "type": "cosmic_signal",
                    "data": asdict(cosmic_signal)
                })
                
                return {"status": "added"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/metrics/trading")
        async def get_trading_metrics():
            """獲取交易指標"""
            metrics = self.manager.get_trading_metrics()
            if metrics:
                return metrics
            return {
                "timestamp": datetime.now().isoformat(),
                "total_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }
        
        @self.app.post("/api/metrics/trading")
        async def update_trading_metrics(metrics: Dict[str, Any]):
            """更新交易指標"""
            try:
                trading_metrics = TradingMetrics(**metrics)
                self.manager.update_trading_metrics(trading_metrics)
                
                # 廣播更新
                await self.manager.broadcast_update({
                    "type": "metrics_update",
                    "data": asdict(trading_metrics)
                })
                
                return {"status": "updated"}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.websocket("/ws/live-updates")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket 實時更新端點"""
            await websocket.accept()
            self.manager.active_websockets.add(websocket)
            
            try:
                while True:
                    # 接收客戶端消息
                    data = await websocket.receive_text()
                    logger.info(f"收到 WebSocket 消息: {data}")
                    
                    # 廣播給所有客戶端
                    await self.manager.broadcast_update({
                        "type": "message",
                        "data": data
                    })
            except WebSocketDisconnect:
                self.manager.active_websockets.discard(websocket)
                logger.info("WebSocket 客戶端已斷開連接")
            except Exception as e:
                logger.error(f"WebSocket 錯誤: {e}")
                self.manager.active_websockets.discard(websocket)


def create_panel_app() -> FastAPI:
    """創建面版應用"""
    manager = LLMTradeBotPanelManager()
    api = LLMTradeBotAPI(manager)
    return api.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_panel_app()
    
    # 運行服務器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
