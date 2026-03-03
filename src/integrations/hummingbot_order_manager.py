#!/usr/bin/env python3
"""
Hummingbot 订单管理器
Hummingbot Order Manager

管理订单完整生命周期、持仓追踪、性能计算
Manages complete order lifecycle, position tracking, performance calculations
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ==================== 数据类型定义 ====================

class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class OrderSnapshot:
    """订单快照"""
    order_id: str
    exchange: str
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    filled_quantity: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    average_fill_price: float = 0.0
    commission: float = 0.0


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: float
    average_cost: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def update_price(self, new_price: float):
        """更新当前价格和未实现 P&L"""
        self.current_price = new_price
        self.unrealized_pnl = (new_price - self.average_cost) * self.quantity
        self.last_updated = datetime.utcnow()
    
    def get_total_value(self) -> float:
        """获取持仓总值"""
        return self.quantity * self.current_price
    
    def get_pnl_percentage(self) -> float:
        """获取 P&L 百分比"""
        if self.average_cost == 0:
            return 0.0
        return ((self.current_price - self.average_cost) / self.average_cost) * 100


@dataclass
class PositionSummary:
    """持仓汇总"""
    positions: Dict[str, Position]
    total_value: float = 0.0
    total_unrealized_pnl: float = 0.0
    total_realized_pnl: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_totals(self):
        """计算总值"""
        self.total_value = sum(p.get_total_value() for p in self.positions.values())
        self.total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        self.total_realized_pnl = sum(p.realized_pnl for p in self.positions.values())
    
    def get_portfolio_return_pct(self) -> float:
        """获取投资组合收益率"""
        if self.total_value == 0:
            return 0.0
        return (self.total_unrealized_pnl / self.total_value) * 100 if self.total_value > 0 else 0.0


@dataclass
class TradeMetrics:
    """交易指标"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    max_consecutive_losses: int = 0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    def update_from_trades(self, trades: List[Dict]):
        """从交易列表更新指标"""
        if not trades:
            return
        
        self.total_trades = len(trades)
        pnls = [t.get('pnl', 0) for t in trades]
        
        # 计算赢和亏
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        
        self.winning_trades = len(wins)
        self.losing_trades = len(losses)
        
        if self.winning_trades > 0:
            self.gross_profit = sum(wins)
            self.average_win = self.gross_profit / self.winning_trades
            self.largest_win = max(wins)
        
        if self.losing_trades > 0:
            self.gross_loss = sum(losses)
            self.average_loss = self.gross_loss / self.losing_trades
            self.largest_loss = abs(min(losses))
        
        # 计算总 P&L 和赢率
        self.total_pnl = sum(pnls)
        self.win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # 计算利润因子
        if self.gross_loss != 0:
            self.profit_factor = abs(self.gross_profit / self.gross_loss)
        else:
            self.profit_factor = float('inf') if self.gross_profit > 0 else 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_pnl': self.total_pnl,
            'gross_profit': self.gross_profit,
            'gross_loss': abs(self.gross_loss),
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'average_win': self.average_win,
            'average_loss': abs(self.average_loss) if self.average_loss != 0 else 0,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
        }


# ==================== 主要类 ====================

class HummingbotOrderManager:
    """
    Hummingbot 订单管理器
    
    管理订单生命周期，追踪持仓，计算性能指标
    
    Hummingbot Order Manager
    
    Manages order lifecycle, tracks positions, calculates performance metrics
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        初始化订单管理器
        
        Args:
            initial_balance: 初始资金
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        self.orders: Dict[str, OrderSnapshot] = {}  # 所有订单
        self.positions: Dict[str, Position] = {}  # 当前持仓
        self.closed_trades: List[Dict] = []  # 已平仓交易
        
        self.logger = logging.getLogger(f"{__name__}.HummingbotOrderManager")
    
    def add_order(
        self,
        order_id: str,
        exchange: str,
        symbol: str,
        side: str,
        price: float,
        quantity: float,
    ) -> OrderSnapshot:
        """
        添加新订单
        
        Args:
            order_id: 订单 ID
            exchange: 交易所
            symbol: 交易对
            side: "buy" or "sell"
            price: 价格
            quantity: 数量
            
        Returns:
            OrderSnapshot
        """
        order = OrderSnapshot(
            order_id=order_id,
            exchange=exchange,
            symbol=symbol,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            price=price,
            quantity=quantity,
            filled_quantity=0,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        self.orders[order_id] = order
        self.logger.info(f"Order added: {order_id} {side} {quantity} {symbol} @ {price}")
        return order
    
    def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        filled_quantity: float = 0,
        average_price: float = 0,
        commission: float = 0,
    ):
        """
        更新订单状态
        
        Args:
            order_id: 订单 ID
            status: 新状态
            filled_quantity: 成交数量
            average_price: 平均价格
            commission: 手续费
        """
        if order_id not in self.orders:
            self.logger.error(f"Order not found: {order_id}")
            return
        
        order = self.orders[order_id]
        order.status = status
        order.filled_quantity = filled_quantity
        order.average_fill_price = average_price
        order.commission = commission
        order.updated_at = datetime.utcnow()
        
        self.logger.info(f"Order updated: {order_id} status={status.value} filled={filled_quantity}")
        
        # 如果订单已成交，更新持仓
        if status == OrderStatus.FILLED:
            self._update_position(order)
        
        # 如果订单已平仓，记录交易
        elif status == OrderStatus.CANCELLED:
            if order.filled_quantity > 0:
                self._record_trade(order)
    
    def _update_position(self, order: OrderSnapshot):
        """更新持仓"""
        symbol = order.symbol
        
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=0,
                average_cost=0,
                current_price=order.average_fill_price,
                unrealized_pnl=0.0,
            )
        
        pos = self.positions[symbol]
        
        if order.side == OrderSide.BUY:
            # 买入：更新平均成本
            total_quantity = pos.quantity + order.filled_quantity
            if total_quantity > 0:
                pos.average_cost = (
                    (pos.quantity * pos.average_cost +
                     order.filled_quantity * order.average_fill_price) /
                    total_quantity
                )
            pos.quantity = total_quantity
        
        else:  # SELL
            # 卖出：减少持仓
            pos.quantity -= order.filled_quantity
            if pos.quantity < 0:
                pos.quantity = 0
                self.logger.warning(f"Position {symbol} went negative")
        
        pos.current_price = order.average_fill_price
        self.logger.info(f"Position updated: {symbol} qty={pos.quantity} cost={pos.average_cost}")
    
    def _record_trade(self, order: OrderSnapshot):
        """记录已平仓交易"""
        trade = {
            'order_id': order.order_id,
            'symbol': order.symbol,
            'side': order.side.value,
            'quantity': order.filled_quantity,
            'price': order.average_fill_price,
            'commission': order.commission,
            'closed_at': datetime.utcnow(),
        }
        
        self.closed_trades.append(trade)
    
    def update_market_price(self, symbol: str, price: float):
        """
        更新市场价格
        用于计算未实现 P&L
        """
        if symbol in self.positions:
            self.positions[symbol].update_price(price)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取单个持仓"""
        return self.positions.get(symbol)
    
    def get_position_summary(self) -> PositionSummary:
        """
        获取持仓汇总
        
        Returns:
            PositionSummary 对象
        """
        summary = PositionSummary(positions=self.positions.copy())
        summary.calculate_totals()
        return summary
    
    def get_order(self, order_id: str) -> Optional[OrderSnapshot]:
        """获取单个订单"""
        return self.orders.get(order_id)
    
    def get_orders(self, symbol: Optional[str] = None, limit: int = 100) -> List[OrderSnapshot]:
        """
        获取订单列表
        
        Args:
            symbol: 可选的交易对过滤
            limit: 返回数量限制
            
        Returns:
            订单列表
        """
        orders = list(self.orders.values())
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        
        # 按时间倒序排列
        orders.sort(key=lambda o: o.created_at, reverse=True)
        return orders[:limit]
    
    def get_trade_metrics(self) -> TradeMetrics:
        """
        获取交易指标
        
        Returns:
            TradeMetrics 对象
        """
        metrics = TradeMetrics()
        
        # 从已平仓交易计算指标
        if self.closed_trades:
            trades_data = []
            for trade in self.closed_trades:
                # 这里需要配对买卖订单来计算 P&L
                # 简化版本：假设有 pnl 字段
                if 'pnl' in trade:
                    trades_data.append(trade)
            
            metrics.update_from_trades(trades_data)
        
        return metrics
    
    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        计算投资组合总值
        
        Args:
            current_prices: 各交易对的当前价格
            
        Returns:
            投资组合总值
        """
        total = self.current_balance
        
        for symbol, price in current_prices.items():
            if symbol in self.positions:
                pos = self.positions[symbol]
                total += pos.quantity * price
        
        return total
    
    def get_unrealized_pnl(self) -> float:
        """获取未实现 P&L"""
        summary = self.get_position_summary()
        return summary.total_unrealized_pnl
    
    def get_realized_pnl(self) -> float:
        """获取已实现 P&L"""
        summary = self.get_position_summary()
        return summary.total_realized_pnl
    
    def get_total_pnl(self) -> float:
        """获取总 P&L"""
        return self.get_realized_pnl() + self.get_unrealized_pnl()
    
    def export_order_history(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        导出订单历史
        
        Args:
            symbol: 可选的交易对过滤
            
        Returns:
            订单列表的字典形式
        """
        orders = self.get_orders(symbol=symbol, limit=10000)
        
        return [
            {
                'order_id': o.order_id,
                'exchange': o.exchange,
                'symbol': o.symbol,
                'side': o.side.value,
                'price': o.price,
                'quantity': o.quantity,
                'filled_quantity': o.filled_quantity,
                'status': o.status.value,
                'created_at': o.created_at.isoformat(),
                'updated_at': o.updated_at.isoformat(),
                'average_fill_price': o.average_fill_price,
                'commission': o.commission,
            }
            for o in orders
        ]
    
    def export_position_summary(self) -> Dict:
        """
        导出持仓汇总
        
        Returns:
            持仓汇总的字典形式
        """
        summary = self.get_position_summary()
        
        return {
            'timestamp': summary.timestamp.isoformat(),
            'total_value': summary.total_value,
            'total_unrealized_pnl': summary.total_unrealized_pnl,
            'total_realized_pnl': summary.total_realized_pnl,
            'positions': {
                symbol: {
                    'quantity': pos.quantity,
                    'average_cost': pos.average_cost,
                    'current_price': pos.current_price,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'realized_pnl': pos.realized_pnl,
                }
                for symbol, pos in summary.positions.items()
            }
        }


class HummingbotOrderFactory:
    """
    订单工厂
    便捷创建各种类型的订单
    """
    
    def __init__(self, manager: HummingbotOrderManager):
        self.manager = manager
    
    def create_market_order(
        self,
        order_id: str,
        exchange: str,
        symbol: str,
        side: str,
        quantity: float,
        market_price: float,
    ) -> OrderSnapshot:
        """创建市价订单"""
        return self.manager.add_order(
            order_id=order_id,
            exchange=exchange,
            symbol=symbol,
            side=side,
            price=market_price,
            quantity=quantity,
        )
    
    def create_limit_order(
        self,
        order_id: str,
        exchange: str,
        symbol: str,
        side: str,
        quantity: float,
        limit_price: float,
    ) -> OrderSnapshot:
        """创建限价订单"""
        return self.manager.add_order(
            order_id=order_id,
            exchange=exchange,
            symbol=symbol,
            side=side,
            price=limit_price,
            quantity=quantity,
        )


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 创建订单管理器
    manager = HummingbotOrderManager(initial_balance=10000.0)
    
    # 添加订单
    order1 = manager.add_order(
        order_id="ORD-001",
        exchange="binance",
        symbol="BTC-USDT",
        side="buy",
        price=45000,
        quantity=0.1,
    )
    
    # 更新订单状态
    manager.update_order_status(
        order_id="ORD-001",
        status=OrderStatus.FILLED,
        filled_quantity=0.1,
        average_price=45000,
        commission=1.0,
    )
    
    # 更新市场价格
    manager.update_market_price("BTC-USDT", 46000)
    
    # 获取持仓汇总
    summary = manager.get_position_summary()
    print(f"\nPosition Summary:")
    print(f"Total Value: ${summary.total_value:.2f}")
    print(f"Unrealized PnL: ${summary.total_unrealized_pnl:.2f}")
    print(f"Positions: {len(summary.positions)}")
