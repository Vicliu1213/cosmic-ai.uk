#!/usr/bin/env python3
"""
LLM-TradeBot Cosmic Panel 啟動腳本
"""

import uvicorn
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from datetime import datetime
from typing import Dict, Any, Set

from bridge import (
    unified_bridge, 
    initialize_bridges,
    LLMTradeBotBridge,
    CosmicSignalBridge
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 存儲活躍的 WebSocket 連接
active_connections: Set[WebSocket] = set()


# === 應用生命週期 ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動
    logger.info("=== LLM-TradeBot Cosmic Panel 啟動 ===")
    await initialize_bridges()
    logger.info("✓ 所有橋接層已初始化")
    yield
    # 關閉
    logger.info("=== LLM-TradeBot Cosmic Panel 關閉 ===")


# 創建應用
app = FastAPI(
    title="LLM-TradeBot Cosmic Panel",
    description="統一交易監控面板",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態文件路徑
PANEL_DIR = Path(__file__).parent
STATIC_DIR = PANEL_DIR / "web" if (PANEL_DIR / "web").exists() else PANEL_DIR

# 掛載靜態文件
try:
    if (PANEL_DIR / "web").exists():
        app.mount("/static", StaticFiles(directory=PANEL_DIR / "web"), name="static")
except Exception as e:
    logger.warning(f"無法掛載靜態文件: {e}")


# === 根頁面 ===
@app.get("/")
async def root():
    """返回主面板頁面"""
    index_file = PANEL_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "LLM-TradeBot Cosmic Panel"}


# === 健康檢查 ===
@app.get("/api/health")
async def health_check():
    """系統健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "llm_bridge": "connected",
            "cosmic_bridge": "connected",
            "websocket_clients": len(active_connections)
        }
    }


# === 代理相關 API ===
@app.get("/api/agents/summary")
async def get_agents_summary():
    """獲取代理摘要"""
    agents = await unified_bridge.llm_bridge.get_agent_state()
    return {
        "total_agents": len(agents),
        "agents": agents,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/agents/{agent_name}/update")
async def update_agent_state(agent_name: str, data: Dict[str, Any]):
    """更新代理狀態"""
    unified_bridge.llm_bridge.update_agent_state(agent_name, data)
    
    # 廣播更新
    await broadcast_update({
        "type": "agent_update",
        "data": {
            "agent_name": agent_name,
            **data
        }
    })
    
    return {"status": "updated", "agent": agent_name}


# === 信號相關 API ===
@app.get("/api/signals/cosmic")
async def get_cosmic_signals(limit: int = 20):
    """獲取 Cosmic 信號"""
    signals = unified_bridge.cosmic_bridge.get_signals(limit)
    return {
        "total": len(signals),
        "signals": signals,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/signals/cosmic")
async def add_cosmic_signal(signal: Dict[str, Any]):
    """添加 Cosmic 信號"""
    try:
        # 添加時間戳
        if "timestamp" not in signal:
            signal["timestamp"] = datetime.now().isoformat()
        
        unified_bridge.cosmic_bridge.add_signal(signal)
        
        # 廣播更新
        await broadcast_update({
            "type": "cosmic_signal",
            "data": signal
        })
        
        return {"status": "added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# === 指標相關 API ===
@app.get("/api/metrics/trading")
async def get_trading_metrics():
    """獲取交易指標"""
    metrics = await unified_bridge.llm_bridge.get_metrics()
    return {
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/metrics/trading")
async def update_trading_metrics(data: Dict[str, Any]):
    """更新交易指標"""
    try:
        unified_bridge.llm_bridge.update_metrics(data)
        
        # 廣播更新
        await broadcast_update({
            "type": "metrics_update",
            "data": data
        })
        
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# === 統一狀態 API ===
@app.get("/api/system/state")
async def get_system_state():
    """獲取完整系統狀態"""
    state = await unified_bridge.get_unified_state()
    return state


# === 控制 API ===
@app.post("/api/control/start")
async def control_start():
    """啟動交易"""
    await unified_bridge.start_system()
    
    await broadcast_update({
        "type": "system_event",
        "event": "started"
    })
    
    return {"status": "started"}


@app.post("/api/control/stop")
async def control_stop():
    """停止交易"""
    await unified_bridge.stop_system()
    
    await broadcast_update({
        "type": "system_event",
        "event": "stopped"
    })
    
    return {"status": "stopped"}


@app.post("/api/control/pause")
async def control_pause():
    """暫停交易"""
    await unified_bridge.pause_system()
    
    await broadcast_update({
        "type": "system_event",
        "event": "paused"
    })
    
    return {"status": "paused"}


@app.post("/api/control/reset")
async def control_reset():
    """重置系統"""
    logger.info("系統重置")
    
    await broadcast_update({
        "type": "system_event",
        "event": "reset"
    })
    
    return {"status": "reset"}


# === WebSocket 實時更新 ===
@app.websocket("/ws/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 實時更新端點"""
    await websocket.accept()
    active_connections.add(websocket)
    
    logger.info(f"WebSocket 客戶端已連接 (總數: {len(active_connections)})")
    
    # 發送初始狀態
    try:
        state = await unified_bridge.get_unified_state()
        await websocket.send_json({
            "type": "initial_state",
            "data": state
        })
    except Exception as e:
        logger.error(f"發送初始狀態失敗: {e}")
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"收到 WebSocket 消息: {data[:100]}")
            
            # 廣播給所有客戶端
            await broadcast_update({
                "type": "message",
                "data": data
            })
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        logger.info(f"WebSocket 客戶端已斷開 (剩餘: {len(active_connections)})")
    except Exception as e:
        logger.error(f"WebSocket 錯誤: {e}")
        active_connections.discard(websocket)


# === 輔助函數 ===
async def broadcast_update(message: Dict[str, Any]):
    """廣播更新消息給所有 WebSocket 客戶端"""
    disconnected = set()
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"發送 WebSocket 消息失敗: {e}")
            disconnected.add(connection)
    
    # 清理已斷開的連接
    active_connections.difference_update(disconnected)


# === 運行服務器 ===
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"啟動面版服務器: http://{host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False
    )
