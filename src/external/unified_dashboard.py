#!/usr/bin/env python3
"""
統一交易系統儀表板 - 多 Bot 管理和切換
Unified Trading System Dashboard - Multi-Bot Management & Switching

功能:
  1. 多 Bot 切換和管理
  2. 統一的交易信號展示
  3. 實時性能指標
  4. Bot 健康狀態監控
  5. WebSocket 實時更新
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
from typing import Optional, Dict, List, Any, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
import logging

from .unified_trading_system import (
    BotManager, get_bot_manager, TradingSignal, SignalType, TradeExecution
)
from .config_manager import ConfigManager, get_config_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DashboardBotInfo:
    """儀表板 Bot 信息"""
    bot_name: str
    bot_type: str
    status: str  # OFFLINE, INITIALIZING, RUNNING, PAUSED, ERROR
    connected: bool
    is_active: bool
    total_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    last_execution: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardMetrics:
    """儀表板整體指標"""
    timestamp: str
    total_bots: int
    active_bots: int
    total_trades: int
    total_pnl: float
    system_win_rate: float
    best_performing_bot: Optional[str] = None
    all_bots: List[DashboardBotInfo] = field(default_factory=list)


class UnifiedTradingDashboardManager:
    """統一交易儀表板管理器"""
    
    def __init__(self, bot_manager: Optional[BotManager] = None,
                 config_manager: Optional[ConfigManager] = None):
        """
        初始化儀表板管理器
        
        Args:
            bot_manager: Bot 管理器
            config_manager: 配置管理器
        """
        self.bot_manager = bot_manager or get_bot_manager()
        self.config_manager = config_manager or get_config_manager()
        
        # 狀態存儲
        self.active_websockets: Set[WebSocket] = set()
        self.dashboard_metrics: Optional[DashboardMetrics] = None
        self.execution_history: List[TradeExecution] = []
        self.max_execution_history = 100
        
        # 監控任務
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_enabled = False
        
        logger.info("UnifiedTradingDashboardManager initialized")
    
    async def initialize(self):
        """初始化系統"""
        logger.info("Initializing Unified Trading Dashboard")
        
        # 加載配置
        self.config_manager.load_all()
        
        # 應用配置到 Bot 管理器
        self.config_manager.apply_to_bot_manager(self.bot_manager)
        
        # 連接所有已啟用的 Bot
        await self._connect_enabled_bots()
        
        # 啟動監控
        await self.start_monitoring()
        
        logger.info("Unified Trading Dashboard initialized")
    
    async def _connect_enabled_bots(self):
        """連接所有已啟用的 Bot"""
        enabled_bots = [
            name for name, config in self.bot_manager.bot_configs.items()
            if config.enabled
        ]
        
        if enabled_bots:
            results = await self.bot_manager.connect_all()
            logger.info(f"Connected bots: {results}")
    
    async def start_monitoring(self):
        """啟動監控"""
        if self.monitoring_task is None:
            self.monitoring_enabled = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Monitoring started")
    
    async def stop_monitoring(self):
        """停止監控"""
        self.monitoring_enabled = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        logger.info("Monitoring stopped")
    
    async def _monitoring_loop(self):
        """監控循環"""
        interval = self.config_manager.system_config.monitoring_interval
        
        while self.monitoring_enabled:
            try:
                # 更新指標
                await self.update_metrics()
                
                # 廣播更新
                await self.broadcast_update({
                    "type": "metrics_update",
                    "data": asdict(self.dashboard_metrics) if self.dashboard_metrics else {}
                })
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def update_metrics(self):
        """更新儀表板指標"""
        try:
            system_metrics = self.bot_manager.get_system_metrics()
            all_bots_info = self.bot_manager.get_bot_list()
            all_bot_metrics = self.bot_manager.get_all_metrics()
            
            # 構建詳細的 Bot 信息
            bots_info = []
            best_bot = None
            best_pnl = float('-inf')
            
            for bot_info in all_bots_info:
                bot_name = bot_info["name"]
                bot_metrics = all_bot_metrics.get(bot_name)
                
                if bot_metrics:
                    dashboard_bot = DashboardBotInfo(
                        bot_name=bot_name,
                        bot_type=bot_info["type"],
                        status=bot_info["status"],
                        connected=bot_info["connected"],
                        is_active=(bot_name == self.bot_manager.active_bot),
                        total_trades=bot_metrics.total_trades,
                        win_rate=bot_metrics.win_rate,
                        total_pnl=bot_metrics.total_pnl,
                        metrics={
                            "winning_trades": bot_metrics.winning_trades,
                            "losing_trades": bot_metrics.losing_trades,
                            "average_pnl": bot_metrics.average_pnl,
                        }
                    )
                    
                    bots_info.append(dashboard_bot)
                    
                    # 找出最好的 Bot
                    if bot_metrics.total_pnl > best_pnl:
                        best_pnl = bot_metrics.total_pnl
                        best_bot = bot_name
            
            # 更新整體指標
            self.dashboard_metrics = DashboardMetrics(
                timestamp=datetime.now().isoformat(),
                total_bots=system_metrics["total_bots"],
                active_bots=system_metrics["active_bots"],
                total_trades=system_metrics["total_trades"],
                total_pnl=system_metrics["total_pnl"],
                system_win_rate=system_metrics["win_rate"],
                best_performing_bot=best_bot,
                all_bots=bots_info
            )
            
            logger.debug(f"Metrics updated: {system_metrics['total_trades']} trades")
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    async def broadcast_update(self, message: Dict[str, Any]):
        """廣播更新消息給所有 WebSocket 客戶端"""
        disconnected = set()
        
        for ws in self.active_websockets:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(ws)
        
        # 清理斷開的連接
        self.active_websockets -= disconnected
    
    async def execute_signal(self, signal: TradingSignal,
                            bot_name: Optional[str] = None) -> Dict[str, Any]:
        """執行交易信號"""
        execution = await self.bot_manager.execute_signal(signal, bot_name)
        
        # 記錄執行
        self.execution_history.append(execution)
        if len(self.execution_history) > self.max_execution_history:
            self.execution_history = self.execution_history[-self.max_execution_history:]
        
        # 廣播信號執行
        await self.broadcast_update({
            "type": "signal_executed",
            "data": asdict(execution)
        })
        
        return asdict(execution)
    
    def switch_active_bot(self, bot_name: str) -> bool:
        """切換活躍 Bot"""
        success = self.bot_manager.switch_active_bot(bot_name)
        
        if success:
            # 廣播切換事件
            asyncio.create_task(self.broadcast_update({
                "type": "bot_switched",
                "data": {"active_bot": bot_name}
            }))
        
        return success
    
    def get_bots_list(self) -> List[Dict[str, Any]]:
        """取得 Bot 列表"""
        return self.bot_manager.get_bot_list()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """取得儀表板數據"""
        return {
            "metrics": asdict(self.dashboard_metrics) if self.dashboard_metrics else None,
            "bots": self.get_bots_list(),
            "active_bot": self.bot_manager.active_bot,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """取得執行歷史"""
        return [
            asdict(e) for e in self.execution_history[-limit:]
        ]


class UnifiedTradingDashboardAPI:
    """統一交易系統 API"""
    
    def __init__(self, manager: UnifiedTradingDashboardManager):
        """初始化 API"""
        self.manager = manager
        self.app = FastAPI(
            title="Unified Trading System Dashboard",
            description="Multi-Bot Trading System Management"
        )
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
            logger.info("Unified Trading Dashboard API started")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """關閉事件"""
            await self.manager.stop_monitoring()
            await self.manager.bot_manager.disconnect_all()
            logger.info("Unified Trading Dashboard API shutdown")
        
        # =====================================================================
        # 健康檢查端點
        # =====================================================================
        
        @self.app.get("/api/health")
        async def health_check():
            """健康檢查"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "total_bots": len(self.manager.bot_manager.bots),
                "active_bots": sum(
                    1 for b in self.manager.bot_manager.bots.values()
                    if b.is_connected
                )
            }
        
        # =====================================================================
        # Bot 管理端點
        # =====================================================================
        
        @self.app.get("/api/bots")
        async def get_bots_list():
            """取得所有 Bot 列表"""
            return {
                "bots": self.manager.get_bots_list(),
                "active_bot": self.manager.bot_manager.active_bot,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/bots/{bot_name}/status")
        async def get_bot_status(bot_name: str):
            """取得 Bot 狀態"""
            if bot_name not in self.manager.bot_manager.bots:
                raise HTTPException(status_code=404, detail="Bot not found")
            
            bot = self.manager.bot_manager.bots[bot_name]
            return await bot.get_status()
        
        @self.app.post("/api/bots/{bot_name}/connect")
        async def connect_bot(bot_name: str):
            """連接 Bot"""
            success = await self.manager.bot_manager.connect_bot(bot_name)
            return {
                "status": "connected" if success else "failed",
                "bot_name": bot_name,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/bots/{bot_name}/disconnect")
        async def disconnect_bot(bot_name: str):
            """斷開 Bot"""
            success = await self.manager.bot_manager.disconnect_bot(bot_name)
            return {
                "status": "disconnected" if success else "failed",
                "bot_name": bot_name,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/bots/{bot_name}/switch")
        async def switch_bot(bot_name: str):
            """切換活躍 Bot"""
            success = self.manager.switch_active_bot(bot_name)
            
            if not success:
                raise HTTPException(status_code=404, detail="Bot not found")
            
            return {
                "status": "switched",
                "active_bot": bot_name,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/bots/{bot_name}/metrics")
        async def get_bot_metrics(bot_name: str):
            """取得 Bot 性能指標"""
            if bot_name not in self.manager.bot_manager.bots:
                raise HTTPException(status_code=404, detail="Bot not found")
            
            bot = self.manager.bot_manager.bots[bot_name]
            metrics = bot.get_metrics()
            return asdict(metrics)
        
        # =====================================================================
        # 儀表板和指標端點
        # =====================================================================
        
        @self.app.get("/api/dashboard")
        async def get_dashboard():
            """取得儀表板數據"""
            return self.manager.get_dashboard_data()
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """取得系統指標"""
            if self.manager.dashboard_metrics:
                return asdict(self.manager.dashboard_metrics)
            return {
                "timestamp": datetime.now().isoformat(),
                "total_bots": 0,
                "active_bots": 0,
                "total_trades": 0,
                "total_pnl": 0.0,
                "system_win_rate": 0.0
            }
        
        @self.app.get("/api/metrics/all-bots")
        async def get_all_bots_metrics():
            """取得所有 Bot 指標"""
            all_metrics = self.manager.bot_manager.get_all_metrics()
            return {
                name: asdict(metrics)
                for name, metrics in all_metrics.items()
            }
        
        # =====================================================================
        # 交易信號和執行端點
        # =====================================================================
        
        @self.app.post("/api/signals/execute")
        async def execute_signal(signal: Dict[str, Any], 
                                bot_name: Optional[str] = Query(None)):
            """執行交易信號"""
            try:
                trading_signal = TradingSignal(
                    signal_id=signal.get("signal_id", f"SIG_{datetime.now().timestamp()}"),
                    signal_type=SignalType(signal.get("signal_type", "hold")),
                    symbol=signal.get("symbol", "BTC/USDT"),
                    quantity=float(signal.get("quantity", 1.0)),
                    price=signal.get("price"),
                    confidence=float(signal.get("confidence", 0.5))
                )
                
                return await self.manager.execute_signal(trading_signal, bot_name)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/executions")
        async def get_executions(limit: int = 50):
            """取得執行歷史"""
            return {
                "executions": self.manager.get_execution_history(limit),
                "total": len(self.manager.execution_history),
                "timestamp": datetime.now().isoformat()
            }
        
        # =====================================================================
        # WebSocket 實時更新端點
        # =====================================================================
        
        @self.app.websocket("/ws/updates")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket 實時更新"""
            await websocket.accept()
            self.manager.active_websockets.add(websocket)
            
            try:
                # 發送初始狀態
                await websocket.send_json({
                    "type": "connection_established",
                    "data": self.manager.get_dashboard_data()
                })
                
                while True:
                    # 接收客戶端消息
                    data = await websocket.receive_json()
                    logger.info(f"WebSocket message: {data}")
                    
                    # 處理命令
                    command = data.get("command")
                    
                    if command == "get_dashboard":
                        await websocket.send_json({
                            "type": "dashboard_data",
                            "data": self.manager.get_dashboard_data()
                        })
                    
                    elif command == "switch_bot":
                        bot_name = data.get("bot_name")
                        success = self.manager.switch_active_bot(bot_name)
                        await websocket.send_json({
                            "type": "bot_switched",
                            "data": {
                                "success": success,
                                "active_bot": bot_name
                            }
                        })
                    
                    elif command == "execute_signal":
                        signal_data = data.get("signal")
                        bot_name = data.get("bot_name")
                        result = await self.manager.execute_signal(
                            TradingSignal(
                                signal_id=signal_data.get("signal_id", f"SIG_{datetime.now().timestamp()}"),
                                signal_type=SignalType(signal_data.get("signal_type", "hold")),
                                symbol=signal_data.get("symbol", "BTC/USDT"),
                                quantity=float(signal_data.get("quantity", 1.0)),
                                price=signal_data.get("price"),
                                confidence=float(signal_data.get("confidence", 0.5))
                            ),
                            bot_name
                        )
                        
                        await websocket.send_json({
                            "type": "signal_executed",
                            "data": result
                        })
                    
                    else:
                        # 廣播給其他客戶端
                        await self.manager.broadcast_update(data)
                        
            except WebSocketDisconnect:
                self.manager.active_websockets.discard(websocket)
                logger.info("WebSocket client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.manager.active_websockets.discard(websocket)


def create_dashboard_app(bot_manager: Optional[BotManager] = None,
                        config_manager: Optional[ConfigManager] = None) -> FastAPI:
    """
    創建儀表板應用
    
    Args:
        bot_manager: Bot 管理器
        config_manager: 配置管理器
        
    Returns:
        FastAPI: 儀表板應用
    """
    manager = UnifiedTradingDashboardManager(bot_manager, config_manager)
    api = UnifiedTradingDashboardAPI(manager)
    return api.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_dashboard_app()
    
    # 運行服務器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
