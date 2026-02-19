#!/usr/bin/env python3
"""
交易系统监控 MCP 服务器
Trading System Monitoring MCP Server

提供实时交易系统监控工具给 OpenCode
Provides real-time trading system monitoring tools to OpenCode
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketMetrics:
    """市场指标"""
    timestamp: str
    symbol: str
    price: float
    volume: float
    change_percent: float
    bid_ask_spread: float


@dataclass
class PortfolioStatus:
    """投资组合状态"""
    total_value: float
    cash_available: float
    positions_count: int
    day_pnl: float
    total_pnl: float
    risk_level: str


@dataclass
class SystemHealth:
    """系统健康状况"""
    status: str
    uptime_hours: float
    memory_usage_percent: float
    cpu_usage_percent: float
    active_connections: int
    last_update: str


class TradingSystemMonitor:
    """交易系统监控器"""
    
    def __init__(self):
        self.market_data: Dict[str, MarketMetrics] = {}
        self.portfolio: Optional[PortfolioStatus] = None
        self.system_health: Optional[SystemHealth] = None
        self.trade_history: List[Dict[str, Any]] = []
        
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """获取市场数据"""
        try:
            # 模拟数据 - 实际应连接到实时数据源
            metrics = MarketMetrics(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                price=100.5,
                volume=1000000,
                change_percent=2.5,
                bid_ask_spread=0.01
            )
            return {
                "success": True,
                "data": asdict(metrics),
                "message": f"成功获取 {symbol} 的市场数据"
            }
        except Exception as e:
            logger.error(f"获取市场数据失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取市场数据失败"
            }
    
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """获取投资组合状态"""
        try:
            portfolio = PortfolioStatus(
                total_value=1000000,
                cash_available=250000,
                positions_count=5,
                day_pnl=5000,
                total_pnl=50000,
                risk_level="medium"
            )
            return {
                "success": True,
                "data": asdict(portfolio),
                "message": "成功获取投资组合状态"
            }
        except Exception as e:
            logger.error(f"获取投资组合状态失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取投资组合状态失败"
            }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状况"""
        try:
            import psutil
            health = SystemHealth(
                status="healthy",
                uptime_hours=24.5,
                memory_usage_percent=psutil.virtual_memory().percent,
                cpu_usage_percent=psutil.cpu_percent(),
                active_connections=15,
                last_update=datetime.now().isoformat()
            )
            return {
                "success": True,
                "data": asdict(health),
                "message": "系统状态良好"
            }
        except Exception as e:
            logger.error(f"获取系统健康状况失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取系统健康状况失败"
            }
    
    async def get_active_trades(self) -> Dict[str, Any]:
        """获取活跃交易"""
        try:
            trades = [
                {
                    "trade_id": "TRADE_001",
                    "symbol": "AAPL",
                    "side": "BUY",
                    "quantity": 100,
                    "entry_price": 150.00,
                    "current_price": 152.50,
                    "pnl": 250,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "trade_id": "TRADE_002",
                    "symbol": "MSFT",
                    "side": "SELL",
                    "quantity": 50,
                    "entry_price": 300.00,
                    "current_price": 298.50,
                    "pnl": 75,
                    "timestamp": datetime.now().isoformat()
                }
            ]
            return {
                "success": True,
                "data": trades,
                "count": len(trades),
                "message": f"获取到 {len(trades)} 个活跃交易"
            }
        except Exception as e:
            logger.error(f"获取活跃交易失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取活跃交易失败"
            }
    
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """获取风险指标"""
        try:
            risk_metrics = {
                "value_at_risk_95": 50000,
                "sharpe_ratio": 1.85,
                "max_drawdown": 0.15,
                "correlation_risk": 0.45,
                "liquidity_risk": "low",
                "concentration_risk": "medium",
                "timestamp": datetime.now().isoformat()
            }
            return {
                "success": True,
                "data": risk_metrics,
                "message": "成功获取风险指标"
            }
        except Exception as e:
            logger.error(f"获取风险指标失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取风险指标失败"
            }


async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """处理MCP请求"""
    monitor = TradingSystemMonitor()
    
    method = request.get("method")
    params = request.get("params", {})
    
    handlers = {
        "get_market_data": lambda: monitor.get_market_data(params.get("symbol", "AAPL")),
        "get_portfolio_status": monitor.get_portfolio_status,
        "get_system_health": monitor.get_system_health,
        "get_active_trades": monitor.get_active_trades,
        "get_risk_metrics": monitor.get_risk_metrics,
    }
    
    if method in handlers:
        try:
            result = await handlers[method]()
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request.get("id")
            }
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {"code": -1, "message": str(e)},
                "id": request.get("id")
            }
    else:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": request.get("id")
        }


def print_mcp_tools():
    """输出MCP工具定义给OpenCode"""
    tools = {
        "tools": [
            {
                "name": "get_market_data",
                "description": "获取特定符号的市场数据 / Get market data for a specific symbol",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "交易符号 (如: AAPL, MSFT) / Trading symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_portfolio_status",
                "description": "获取当前投资组合状态 / Get current portfolio status",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_system_health",
                "description": "获取系统健康状况 / Get system health status",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_active_trades",
                "description": "获取所有活跃交易 / Get all active trades",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_risk_metrics",
                "description": "获取风险指标 / Get risk metrics",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
    }
    print(json.dumps(tools, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # 打印工具定义供OpenCode使用
    print_mcp_tools()
