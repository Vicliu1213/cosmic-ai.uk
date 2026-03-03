#!/usr/bin/env python3
"""
Phase 5 MarketBot Bridge - Phase 5 实盘交易部署层与 MarketBot 集成
Phase 5 MarketBot 桥接 | 交易部署与监控

功能:
  1. 交易订单到 MarketBot 通知
  2. 实时投资组合监控展示
  3. 交易结果回调处理
  4. 性能指标更新
"""

from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import logging

from ..integrations.marketbot_connector import MarketBotConnector
from ..integrations.base_bridge import TradingSignal, NotificationMessage, ChannelType, PriorityLevel

logger = logging.getLogger(__name__)


class Phase5MarketBotBridge:
    """Phase 5 交易部署与 MarketBot 集成"""
    
    def __init__(self, connector: MarketBotConnector):
        """
        初始化 Phase 5 MarketBot 桥接
        
        Args:
            connector: MarketBot 连接器实例
        """
        self.connector = connector
        self.portfolio_update_callbacks = []
        self.order_callbacks = []
    
    async def notify_order_placed(
        self,
        order_id: str,
        symbol: str,
        quantity: float,
        price: float,
        order_type: str,
    ) -> bool:
        """
        通知订单已下达
        
        Args:
            order_id: 订单 ID
            symbol: 交易品种
            quantity: 数量
            price: 价格
            order_type: 订单类型 (LIMIT, MARKET, STOP_LOSS)
            
        Returns:
            bool: 通知是否成功
        """
        try:
            msg = NotificationMessage(
                title=f"📝 订单已下达 - {symbol}",
                content=f"""
订单详情:
- 订单ID: {order_id}
- 品种: {symbol}
- 类型: {order_type}
- 数量: {quantity:.4f}
- 价格: {price:.2f}
- 时间: {datetime.now().isoformat()}
                """.strip(),
                channels=[ChannelType.DINGTALK, ChannelType.TELEGRAM],
                priority=PriorityLevel.NORMAL,
                tags=["order", "placed", symbol],
            )
            
            return await self.connector.send_notification(msg)
        except Exception as e:
            logger.error(f"Error notifying order: {e}")
            return False
    
    async def notify_portfolio_update(
        self,
        total_value: float,
        cash: float,
        positions: Dict[str, Any],
        pnl: float,
    ) -> bool:
        """
        通知投资组合更新
        
        Args:
            total_value: 总价值
            cash: 现金余额
            positions: 持仓信息
            pnl: 损益
            
        Returns:
            bool: 通知是否成功
        """
        try:
            pnl_str = f"+{pnl:.2f}" if pnl >= 0 else f"{pnl:.2f}"
            msg = NotificationMessage(
                title=f"📊 投资组合更新 | {pnl_str}",
                content=f"""
投资组合快照:
- 总价值: ${total_value:,.2f}
- 现金: ${cash:,.2f}
- 损益: {pnl_str}
- 持仓数: {len(positions)}
- 更新时间: {datetime.now().isoformat()}
                """.strip(),
                channels=[ChannelType.DINGTALK],
                priority=PriorityLevel.NORMAL,
                tags=["portfolio", "update"],
            )
            
            return await self.connector.send_notification(msg)
        except Exception as e:
            logger.error(f"Error notifying portfolio: {e}")
            return False
    
    async def notify_trade_filled(
        self,
        trade_id: str,
        order_id: str,
        symbol: str,
        quantity: float,
        filled_price: float,
        commission: float,
    ) -> bool:
        """
        通知交易成交
        
        Args:
            trade_id: 交易 ID
            order_id: 订单 ID
            symbol: 交易品种
            quantity: 成交数量
            filled_price: 成交价格
            commission: 佣金
            
        Returns:
            bool: 通知是否成功
        """
        try:
            msg = NotificationMessage(
                title=f"✅ 交易成交 - {symbol}",
                content=f"""
成交详情:
- 交易ID: {trade_id}
- 订单ID: {order_id}
- 品种: {symbol}
- 成交量: {quantity:.4f}
- 成交价: {filled_price:.2f}
- 佣金: {commission:.4f}
- 时间: {datetime.now().isoformat()}
                """.strip(),
                channels=[ChannelType.DINGTALK, ChannelType.TELEGRAM],
                priority=PriorityLevel.HIGH,
                tags=["trade", "filled", symbol],
            )
            
            return await self.connector.send_notification(msg)
        except Exception as e:
            logger.error(f"Error notifying trade: {e}")
            return False
    
    async def notify_risk_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "HIGH",
    ) -> bool:
        """
        发送风险告警
        
        Args:
            alert_type: 告警类型 (MAX_DRAWDOWN, CONCENTRATION, etc.)
            message: 告警消息
            severity: 严重程度 (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            bool: 通知是否成功
        """
        try:
            priority_map = {
                "LOW": PriorityLevel.LOW,
                "MEDIUM": PriorityLevel.NORMAL,
                "HIGH": PriorityLevel.HIGH,
                "CRITICAL": PriorityLevel.CRITICAL,
            }
            
            msg = NotificationMessage(
                title=f"⚠️ 风险告警 - {alert_type}",
                content=message,
                channels=[ChannelType.DINGTALK, ChannelType.WECOM],
                priority=priority_map.get(severity, PriorityLevel.HIGH),
                tags=["alert", alert_type.lower()],
            )
            
            return await self.connector.send_notification(msg)
        except Exception as e:
            logger.error(f"Error sending risk alert: {e}")
            return False
