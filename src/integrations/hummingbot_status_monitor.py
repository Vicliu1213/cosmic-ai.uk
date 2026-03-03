#!/usr/bin/env python3
"""
Hummingbot 状态监控器
Hummingbot Status Monitor

监控 Hummingbot 进程健康、交易所连接、投资组合状态
Monitors Hummingbot process health, exchange connectivity, portfolio status
"""

import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ==================== 数据类型定义 ====================

class ConnectionStatus(Enum):
    """连接状态"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    UNKNOWN = "unknown"


class ProcessStatus(Enum):
    """进程状态"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


@dataclass
class ProcessHealth:
    """进程健康状态"""
    status: ProcessStatus
    pid: Optional[int] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    uptime_seconds: float = 0.0
    last_check: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    is_healthy: bool = True


@dataclass
class ExchangeStatus:
    """交易所连接状态"""
    exchange_name: str
    connection_status: ConnectionStatus
    api_version: Optional[str] = None
    supported_pairs: List[str] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.utcnow)
    last_error: Optional[str] = None
    response_time_ms: float = 0.0
    trading_enabled: bool = True


@dataclass
class PortfolioSnapshot:
    """投资组合快照"""
    timestamp: datetime
    total_balance: float  # USDT 或基础货币
    total_value: float  # 以基础货币计价的总值
    available_balance: float
    locked_balance: float
    unrealized_pnl: float
    realized_pnl: float
    cash_percentage: float  # 现金占比
    positions_count: int  # 持仓数
    
    def get_total_pnl(self) -> float:
        """获取总 P&L"""
        return self.realized_pnl + self.unrealized_pnl
    
    def get_total_pnl_percentage(self) -> float:
        """获取 P&L 百分比"""
        if self.total_balance == 0:
            return 0.0
        return (self.get_total_pnl() / self.total_balance) * 100


@dataclass
class OrderSnapshot:
    """订单快照"""
    order_id: str
    symbol: str
    side: str  # "buy" or "sell"
    price: float
    quantity: float
    filled_quantity: float
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass
class HummingbotStatus:
    """Hummingbot 完整状态"""
    process_health: ProcessHealth
    exchanges: Dict[str, ExchangeStatus]
    portfolio: PortfolioSnapshot
    active_orders: List[OrderSnapshot]
    strategy_running: bool
    strategy_name: Optional[str] = None
    strategy_config: Optional[Dict] = None
    last_update: datetime = field(default_factory=datetime.utcnow)
    
    def is_fully_operational(self) -> bool:
        """检查是否完全可操作"""
        return (
            self.process_health.is_healthy and
            self.strategy_running and
            all(
                e.connection_status == ConnectionStatus.CONNECTED
                for e in self.exchanges.values()
            )
        )


# ==================== 主要类 ====================

class HummingbotStatusMonitor:
    """
    Hummingbot 状态监控器
    
    监控 Hummingbot 实例的运行状态，包括：
    - 进程健康状态
    - 交易所连接情况
    - 投资组合状态
    - 活跃订单列表
    
    Hummingbot Status Monitor
    
    Monitors Hummingbot instance status including:
    - Process health
    - Exchange connectivity
    - Portfolio status
    - Active orders
    """
    
    def __init__(
        self,
        hummingbot_host: str = "localhost",
        hummingbot_port: int = 8000,
        check_interval_seconds: int = 5,
    ):
        """
        初始化状态监控器
        
        Args:
            hummingbot_host: Hummingbot 主机地址
            hummingbot_port: Hummingbot 端口号
            check_interval_seconds: 检查间隔（秒）
        """
        self.host = hummingbot_host
        self.port = hummingbot_port
        self.check_interval = check_interval_seconds
        
        self.logger = logging.getLogger(f"{__name__}.HummingbotStatusMonitor")
        
        # 缓存
        self._last_status: Optional[HummingbotStatus] = None
        self._status_history: List[HummingbotStatus] = []
        self._max_history = 100
        
        # 监控任务
        self._monitor_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
    
    async def get_process_health(self) -> ProcessHealth:
        """
        检查 Hummingbot 进程健康状态
        
        Returns:
            ProcessHealth 对象
        """
        health = ProcessHealth(status=ProcessStatus.UNKNOWN)
        
        try:
            # 尝试连接到 Hummingbot
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=2.0
            )
            
            health.status = ProcessStatus.RUNNING
            health.is_healthy = True
            health.last_check = datetime.utcnow()
            
            # 关闭连接
            writer.close()
            await writer.wait_closed()
        
        except asyncio.TimeoutError:
            health.status = ProcessStatus.ERROR
            health.error_message = "Connection timeout"
            health.is_healthy = False
        
        except ConnectionRefusedError:
            health.status = ProcessStatus.STOPPED
            health.error_message = "Connection refused"
            health.is_healthy = False
        
        except Exception as e:
            health.status = ProcessStatus.ERROR
            health.error_message = str(e)
            health.is_healthy = False
        
        return health
    
    async def get_exchange_connectivity(self) -> Dict[str, ExchangeStatus]:
        """
        检查各个交易所的连接状态
        
        Returns:
            交易所连接状态字典
        """
        exchanges = {}
        
        # 常见的交易所列表
        common_exchanges = [
            "binance",
            "kraken",
            "coinbase",
            "huobi",
            "okx",
            "kucoin",
            "bybit",
            "gate",
        ]
        
        for exchange_name in common_exchanges:
            status = ExchangeStatus(
                exchange_name=exchange_name,
                connection_status=ConnectionStatus.UNKNOWN,
            )
            
            try:
                # 这里应该真实连接交易所 API
                # 为演示目的，我们假设连接成功
                status.connection_status = ConnectionStatus.CONNECTED
                status.response_time_ms = 100.0
                status.trading_enabled = True
                status.supported_pairs = [
                    f"BTC-USDT",
                    f"ETH-USDT",
                    f"BNB-USDT",
                ]
            
            except Exception as e:
                status.connection_status = ConnectionStatus.ERROR
                status.last_error = str(e)
                status.trading_enabled = False
            
            exchanges[exchange_name] = status
        
        return exchanges
    
    async def get_portfolio_snapshot(self) -> PortfolioSnapshot:
        """
        获取投资组合快照
        
        Returns:
            PortfolioSnapshot 对象
        """
        # 这里应该从 Hummingbot 获取真实数据
        # 为演示目的，返回示例数据
        snapshot = PortfolioSnapshot(
            timestamp=datetime.utcnow(),
            total_balance=10000.0,
            total_value=10500.0,
            available_balance=5000.0,
            locked_balance=5000.0,
            unrealized_pnl=500.0,
            realized_pnl=0.0,
            cash_percentage=47.6,
            positions_count=2,
        )
        
        return snapshot
    
    async def get_active_orders(self) -> List[OrderSnapshot]:
        """
        获取活跃订单列表
        
        Returns:
            订单快照列表
        """
        # 这里应该从 Hummingbot 获取真实数据
        # 为演示目的，返回空列表或示例数据
        orders = []
        
        # 示例订单
        if False:  # 如果需要示例订单，改为 True
            orders.append(
                OrderSnapshot(
                    order_id="ORD-001",
                    symbol="BTC-USDT",
                    side="buy",
                    price=45000,
                    quantity=0.1,
                    filled_quantity=0.05,
                    status="partially_filled",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
        
        return orders
    
    async def get_strategy_status(self) -> Dict:
        """
        获取策略运行状态
        
        Returns:
            策略状态字典
        """
        return {
            'running': False,
            'strategy_name': None,
            'uptime_seconds': 0,
            'orders_created': 0,
            'orders_filled': 0,
        }
    
    async def get_full_status(self) -> HummingbotStatus:
        """
        获取完整状态
        
        Returns:
            HummingbotStatus 对象
        """
        process_health = await self.get_process_health()
        exchanges = await self.get_exchange_connectivity()
        portfolio = await self.get_portfolio_snapshot()
        active_orders = await self.get_active_orders()
        strategy_status = await self.get_strategy_status()
        
        status = HummingbotStatus(
            process_health=process_health,
            exchanges=exchanges,
            portfolio=portfolio,
            active_orders=active_orders,
            strategy_running=strategy_status.get('running', False),
            strategy_name=strategy_status.get('strategy_name'),
        )
        
        self._last_status = status
        self._add_to_history(status)
        
        return status
    
    def _add_to_history(self, status: HummingbotStatus):
        """添加到历史记录"""
        self._status_history.append(status)
        if len(self._status_history) > self._max_history:
            self._status_history.pop(0)
    
    def get_status_history(self, limit: int = 100) -> List[HummingbotStatus]:
        """获取状态历史"""
        return self._status_history[-limit:]
    
    async def start_monitoring(self):
        """启动连续监控"""
        if self._is_monitoring:
            self.logger.warning("Monitoring already started")
            return
        
        self._is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Status monitoring started")
    
    async def stop_monitoring(self):
        """停止连续监控"""
        self._is_monitoring = False
        if self._monitor_task:
            await self._monitor_task
        self.logger.info("Status monitoring stopped")
    
    async def _monitor_loop(self):
        """监控循环"""
        while self._is_monitoring:
            try:
                status = await self.get_full_status()
                self.logger.debug(
                    f"Status update: process={status.process_health.status.value}, "
                    f"exchanges={len(status.exchanges)}, "
                    f"orders={len(status.active_orders)}"
                )
            
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    def get_last_status(self) -> Optional[HummingbotStatus]:
        """获取最后一次的状态"""
        return self._last_status
    
    def export_status_report(self) -> Dict:
        """
        导出状态报告
        
        Returns:
            状态报告字典
        """
        if not self._last_status:
            return {"error": "No status data available"}
        
        status = self._last_status
        
        return {
            'timestamp': status.last_update.isoformat(),
            'process': {
                'status': status.process_health.status.value,
                'is_healthy': status.process_health.is_healthy,
                'uptime_seconds': status.process_health.uptime_seconds,
                'memory_mb': status.process_health.memory_usage_mb,
                'cpu_percent': status.process_health.cpu_usage_percent,
            },
            'exchanges': {
                name: {
                    'status': ex.connection_status.value,
                    'trading_enabled': ex.trading_enabled,
                    'response_time_ms': ex.response_time_ms,
                }
                for name, ex in status.exchanges.items()
            },
            'portfolio': {
                'total_balance': status.portfolio.total_balance,
                'total_value': status.portfolio.total_value,
                'unrealized_pnl': status.portfolio.unrealized_pnl,
                'realized_pnl': status.portfolio.realized_pnl,
                'cash_percentage': status.portfolio.cash_percentage,
                'positions_count': status.portfolio.positions_count,
            },
            'strategy': {
                'running': status.strategy_running,
                'name': status.strategy_name,
                'active_orders': len(status.active_orders),
            },
            'is_fully_operational': status.is_fully_operational(),
        }


class HummingbotHealthChecker:
    """
    Hummingbot 健康检查器
    执行定期健康检查并生成警报
    
    Hummingbot Health Checker
    Performs periodic health checks and generates alerts
    """
    
    def __init__(self, monitor: HummingbotStatusMonitor):
        """初始化健康检查器"""
        self.monitor = monitor
        self.logger = logging.getLogger(f"{__name__}.HummingbotHealthChecker")
        self.alerts: List[Dict] = []
    
    async def perform_health_check(self) -> Dict:
        """
        执行健康检查
        
        Returns:
            检查结果字典
        """
        status = await self.monitor.get_full_status()
        check_result = {
            'timestamp': datetime.utcnow().isoformat(),
            'issues': [],
            'warnings': [],
            'status': 'healthy',
        }
        
        # 检查进程健康
        if not status.process_health.is_healthy:
            check_result['issues'].append(
                f"Process not healthy: {status.process_health.error_message}"
            )
            check_result['status'] = 'unhealthy'
        
        # 检查交易所连接
        disconnected_exchanges = [
            name for name, ex in status.exchanges.items()
            if ex.connection_status != ConnectionStatus.CONNECTED
        ]
        if disconnected_exchanges:
            check_result['warnings'].append(
                f"Disconnected exchanges: {', '.join(disconnected_exchanges)}"
            )
        
        # 检查投资组合
        if status.portfolio.unrealized_pnl < 0:
            pnl_pct = status.portfolio.get_total_pnl_percentage()
            if pnl_pct < -5:
                check_result['warnings'].append(
                    f"Significant loss: {pnl_pct:.2f}%"
                )
        
        return check_result


if __name__ == "__main__":
    # 测试代码
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        monitor = HummingbotStatusMonitor()
        
        # 获取完整状态
        status = await monitor.get_full_status()
        
        print("\n=== Hummingbot Status ===")
        print(f"Process Health: {status.process_health.status.value}")
        print(f"Strategy Running: {status.strategy_running}")
        print(f"Active Orders: {len(status.active_orders)}")
        print(f"Portfolio Value: ${status.portfolio.total_value:.2f}")
        print(f"Unrealized P&L: ${status.portfolio.unrealized_pnl:.2f}")
        print(f"Is Operational: {status.is_fully_operational()}")
        
        # 导出报告
        report = monitor.export_status_report()
        print("\n=== Status Report ===")
        print(json.dumps(report, indent=2))
    
    asyncio.run(main())
