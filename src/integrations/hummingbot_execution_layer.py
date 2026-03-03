#!/usr/bin/env python3
"""
Hummingbot 执行层 - 主集成模块
Hummingbot Execution Layer - Main Integration Module

将 Hummingbot 与 Cosmic Core、LLMTradeBotRouter、MarketBot UI 整合
Integrates Hummingbot with Cosmic Core, LLMTradeBotRouter, MarketBot UI
"""

import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum

from src.integrations.hummingbot_execution_bridge import (
    HummingbotExecutionBridge,
    TradingSignal,
    ExecutionContext,
    RiskParameters,
    ExecutionStatus,
)
from src.integrations.hummingbot_order_manager import (
    HummingbotOrderManager,
    TradeMetrics,
)
from src.integrations.hummingbot_status_monitor import (
    HummingbotStatusMonitor,
    HummingbotStatus,
    ProcessStatus,
)

logger = logging.getLogger(__name__)


# ==================== 事件类型定义 ====================

class HummingbotEventType(Enum):
    """Hummingbot 事件类型"""
    SIGNAL_RECEIVED = "signal_received"
    SIGNAL_EXECUTED = "signal_executed"
    ORDER_CREATED = "order_created"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    POSITION_UPDATED = "position_updated"
    TRADE_CLOSED = "trade_closed"
    STATUS_CHANGED = "status_changed"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class HummingbotEvent:
    """Hummingbot 事件"""
    event_type: HummingbotEventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "hummingbot_execution_layer"


# ==================== 回调接口 ====================

class HummingbotEventListener:
    """Hummingbot 事件监听器接口"""
    
    async def on_signal_received(self, signal: TradingSignal):
        """信号接收回调"""
        pass
    
    async def on_signal_executed(self, result: Dict[str, Any]):
        """信号执行回调"""
        pass
    
    async def on_order_filled(self, order_id: str, details: Dict[str, Any]):
        """订单成交回调"""
        pass
    
    async def on_status_changed(self, status: HummingbotStatus):
        """状态变化回调"""
        pass


# ==================== 主集成层 ====================

class HummingbotExecutionLayer:
    """
    Hummingbot 执行层 - 主集成类
    
    将所有 Hummingbot 组件整合成统一的执行层，提供给上层应用使用
    Integrates all Hummingbot components into a unified execution layer
    for use by upper layer applications
    """
    
    def __init__(
        self,
        hummingbot_host: str = "localhost",
        hummingbot_port: int = 8000,
        initial_balance: float = 10000.0,
        auto_monitoring: bool = True,
    ):
        """
        初始化 Hummingbot 执行层
        
        Args:
            hummingbot_host: Hummingbot 主机地址
            hummingbot_port: Hummingbot 端口号
            initial_balance: 初始资金
            auto_monitoring: 是否启用自动监控
        """
        self.host = hummingbot_host
        self.port = hummingbot_port
        
        # 初始化子组件
        self.execution_bridge = HummingbotExecutionBridge(
            hummingbot_host=hummingbot_host,
            hummingbot_port=hummingbot_port,
        )
        self.order_manager = HummingbotOrderManager(initial_balance=initial_balance)
        self.status_monitor = HummingbotStatusMonitor(
            hummingbot_host=hummingbot_host,
            hummingbot_port=hummingbot_port,
        )
        
        # 事件系统
        self.listeners: List[HummingbotEventListener] = []
        self.event_history: List[HummingbotEvent] = []
        self._max_event_history = 1000
        
        # 监控状态
        self.auto_monitoring = auto_monitoring
        self._is_running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(f"{__name__}.HummingbotExecutionLayer")
    
    # ==================== 执行方法 ====================
    
    async def execute_trading_signal(
        self,
        signal: TradingSignal,
        market_data: Dict[str, Any],
        risk_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行交易信号
        
        Execute trading signal
        
        Args:
            signal: 交易信号
            market_data: 市场数据
            risk_config: 风险配置
            
        Returns:
            执行结果字典
        """
        self.logger.info(f"Executing signal {signal.signal_id}")
        
        # 触发信号接收事件
        await self._emit_event(
            HummingbotEventType.SIGNAL_RECEIVED,
            {'signal': signal},
        )
        
        # 构建执行上下文
        context = ExecutionContext(
            market_price=market_data.get('price', 0),
            bid_price=market_data.get('bid', 0),
            ask_price=market_data.get('ask', 0),
            bid_volume=market_data.get('bid_volume', 0),
            ask_volume=market_data.get('ask_volume', 0),
            volatility=market_data.get('volatility', 0),
        )
        
        # 构建风险参数
        risk_params = RiskParameters(
            max_position_size=risk_config.get('max_position_size', 1.0) if risk_config else 1.0,
            max_order_size=risk_config.get('max_order_size', 0.5) if risk_config else 0.5,
            max_slippage=risk_config.get('max_slippage', 0.5) if risk_config else 0.5,
            max_daily_loss=risk_config.get('max_daily_loss', 5000) if risk_config else 5000,
            portfolio_value=self.order_manager.current_balance,
        )
        
        # 执行信号
        exec_result = await self.execution_bridge.execute_signal(
            signal=signal,
            context=context,
            risk_params=risk_params,
        )
        
        # 触发信号执行事件
        await self._emit_event(
            HummingbotEventType.SIGNAL_EXECUTED,
            {
                'signal_id': signal.signal_id,
                'status': exec_result.status.value,
                'order_id': exec_result.hummingbot_order_id,
            },
        )
        
        return {
            'signal_id': signal.signal_id,
            'status': exec_result.status.value,
            'order_id': exec_result.hummingbot_order_id,
            'message': exec_result.message,
            'errors': exec_result.errors,
        }
    
    # ==================== 订单管理方法 ====================
    
    def add_order(
        self,
        order_id: str,
        symbol: str,
        side: str,
        price: float,
        quantity: float,
        exchange: str = "binance",
    ) -> Dict[str, Any]:
        """
        添加订单
        
        Add order
        
        Args:
            order_id: 订单 ID
            symbol: 交易对
            side: 买卖方向
            price: 价格
            quantity: 数量
            exchange: 交易所
            
        Returns:
            订单信息字典
        """
        order = self.order_manager.add_order(
            order_id=order_id,
            exchange=exchange,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
        )
        
        return {
            'order_id': order.order_id,
            'symbol': order.symbol,
            'side': order.side.value,
            'status': order.status.value,
        }
    
    def update_order_status(
        self,
        order_id: str,
        status: str,
        filled_quantity: float = 0,
        average_price: float = 0,
        commission: float = 0,
    ):
        """
        更新订单状态
        
        Update order status
        """
        from src.integrations.hummingbot_order_manager import OrderStatus
        
        self.order_manager.update_order_status(
            order_id=order_id,
            status=OrderStatus[status.upper()],
            filled_quantity=filled_quantity,
            average_price=average_price,
            commission=commission,
        )
        
        # 触发订单成交事件
        if status.upper() == "FILLED":
            asyncio.create_task(
                self._emit_event(
                    HummingbotEventType.ORDER_FILLED,
                    {
                        'order_id': order_id,
                        'filled_quantity': filled_quantity,
                        'average_price': average_price,
                    },
                )
            )
    
    def get_order_history(
        self,
        symbol: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取订单历史"""
        return self.order_manager.export_order_history(symbol=symbol)
    
    # ==================== 持仓管理方法 ====================
    
    def get_position_summary(self) -> Dict[str, Any]:
        """获取持仓汇总"""
        summary = self.order_manager.get_position_summary()
        return {
            'total_value': summary.total_value,
            'total_unrealized_pnl': summary.total_unrealized_pnl,
            'total_realized_pnl': summary.total_realized_pnl,
            'positions': {
                symbol: {
                    'quantity': pos.quantity,
                    'average_cost': pos.average_cost,
                    'current_price': pos.current_price,
                    'unrealized_pnl': pos.unrealized_pnl,
                }
                for symbol, pos in summary.positions.items()
            },
        }
    
    def update_market_price(self, symbol: str, price: float):
        """更新市场价格"""
        self.order_manager.update_market_price(symbol, price)
    
    # ==================== 监控方法 ====================
    
    async def get_status(self) -> Dict[str, Any]:
        """
        获取完整状态
        
        Get full status
        
        Returns:
            状态字典
        """
        status = await self.status_monitor.get_full_status()
        
        return {
            'process': {
                'status': status.process_health.status.value,
                'is_healthy': status.process_health.is_healthy,
            },
            'portfolio': {
                'total_value': status.portfolio.total_value,
                'unrealized_pnl': status.portfolio.unrealized_pnl,
            },
            'active_orders': len(status.active_orders),
            'strategy_running': status.strategy_running,
            'is_operational': status.is_fully_operational(),
        }
    
    async def start(self):
        """启动执行层"""
        self.logger.info("Starting Hummingbot execution layer")
        self._is_running = True
        
        if self.auto_monitoring:
            await self.status_monitor.start_monitoring()
        
        self.logger.info("Hummingbot execution layer started")
    
    async def stop(self):
        """停止执行层"""
        self.logger.info("Stopping Hummingbot execution layer")
        self._is_running = False
        
        if self.auto_monitoring:
            await self.status_monitor.stop_monitoring()
        
        self.logger.info("Hummingbot execution layer stopped")
    
    # ==================== 事件系统 ====================
    
    def add_listener(self, listener: HummingbotEventListener):
        """添加事件监听器"""
        self.listeners.append(listener)
    
    def remove_listener(self, listener: HummingbotEventListener):
        """移除事件监听器"""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    async def _emit_event(
        self,
        event_type: HummingbotEventType,
        data: Dict[str, Any],
    ):
        """发送事件"""
        event = HummingbotEvent(event_type=event_type, data=data)
        self.event_history.append(event)
        
        # 限制历史记录大小
        if len(self.event_history) > self._max_event_history:
            self.event_history.pop(0)
        
        # 通知所有监听器
        tasks = []
        for listener in self.listeners:
            if event_type == HummingbotEventType.SIGNAL_RECEIVED:
                tasks.append(listener.on_signal_received(data.get('signal')))
            elif event_type == HummingbotEventType.SIGNAL_EXECUTED:
                tasks.append(listener.on_signal_executed(data))
            elif event_type == HummingbotEventType.ORDER_FILLED:
                tasks.append(listener.on_order_filled(
                    data.get('order_id'),
                    data,
                ))
            elif event_type == HummingbotEventType.STATUS_CHANGED:
                tasks.append(listener.on_status_changed(data.get('status')))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取事件历史"""
        return [
            {
                'event_type': e.event_type.value,
                'timestamp': e.timestamp.isoformat(),
                'data': e.data,
            }
            for e in self.event_history[-limit:]
        ]
    
    # ==================== 性能指标 ====================
    
    def get_trade_metrics(self) -> Dict[str, Any]:
        """获取交易指标"""
        metrics = self.order_manager.get_trade_metrics()
        return metrics.to_dict()
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """获取投资组合价值"""
        return self.order_manager.calculate_portfolio_value(current_prices)
    
    def get_total_pnl(self) -> float:
        """获取总 P&L"""
        return self.order_manager.get_total_pnl()


# ==================== 工厂函数 ====================

def create_hummingbot_execution_layer(
    hummingbot_host: str = "localhost",
    hummingbot_port: int = 8000,
    initial_balance: float = 10000.0,
) -> HummingbotExecutionLayer:
    """
    创建 Hummingbot 执行层
    
    Create Hummingbot execution layer
    """
    return HummingbotExecutionLayer(
        hummingbot_host=hummingbot_host,
        hummingbot_port=hummingbot_port,
        initial_balance=initial_balance,
    )


# ==================== 示例事件监听器 ====================

class LoggingEventListener(HummingbotEventListener):
    """日志事件监听器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.LoggingEventListener")
    
    async def on_signal_received(self, signal: TradingSignal):
        """记录收到的信号"""
        if signal:
            self.logger.info(
                f"Signal received: {signal.signal_id}, "
                f"symbol={signal.symbol}, "
                f"direction={signal.direction}"
            )
    
    async def on_signal_executed(self, result: Dict[str, Any]):
        """记录执行结果"""
        self.logger.info(
            f"Signal executed: {result.get('signal_id')}, "
            f"status={result.get('status')}"
        )
    
    async def on_order_filled(self, order_id: str, details: Dict[str, Any]):
        """记录订单成交"""
        self.logger.info(
            f"Order filled: {order_id}, "
            f"quantity={details.get('filled_quantity')}, "
            f"price={details.get('average_price')}"
        )
    
    async def on_status_changed(self, status: HummingbotStatus):
        """记录状态变化"""
        if status:
            self.logger.info(f"Status changed: operational={status.is_fully_operational()}")


if __name__ == "__main__":
    # 演示代码
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        # 创建执行层
        exec_layer = create_hummingbot_execution_layer()
        
        # 添加事件监听器
        exec_layer.add_listener(LoggingEventListener())
        
        # 启动
        await exec_layer.start()
        
        # 获取状态
        status = await exec_layer.get_status()
        print(f"\nStatus: {status}")
        
        # 停止
        await exec_layer.stop()
    
    asyncio.run(demo())
