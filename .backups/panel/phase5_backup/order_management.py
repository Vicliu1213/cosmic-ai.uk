#!/usr/bin/env python3
"""
Order Management System
訂單管理系統

Complete order lifecycle management for multi-exchange trading:
- Order placement and tracking
- Multiple order types (limit, market, stop-loss)
- Position management
- Portfolio tracking
- Trade settlement and reporting

This module provides:
1. Order data structures and enums
2. Order manager for lifecycle management
3. Portfolio tracker for positions
4. Trade settlement engine
5. Performance reporting
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal

from src.phase5.exchange_connector import ExchangeType, AccountBalance


# ============================================================================
# Enums
# ============================================================================

class OrderType(Enum):
    """Order type classification."""
    LIMIT = "limit"
    MARKET = "market"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(Enum):
    """Order direction."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order lifecycle status."""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PositionStatus(Enum):
    """Position status."""
    OPENING = "opening"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class OrderPrice:
    """Order pricing information."""
    limit_price: Optional[float] = None  # For limit orders
    market_price: Optional[float] = None  # Current market price
    stop_price: Optional[float] = None  # For stop-loss orders
    trailing_stop_percent: Optional[float] = None  # For trailing stops
    average_fill_price: Optional[float] = None  # Average execution price


@dataclass
class OrderQuantity:
    """Order quantity tracking."""
    original_quantity: float
    filled_quantity: float = 0.0
    remaining_quantity: float = field(init=False)

    def __post_init__(self):
        self.remaining_quantity = self.original_quantity - self.filled_quantity

    def fill(self, amount: float) -> bool:
        """Fill order quantity.
        
        Args:
            amount: Amount to fill
            
        Returns:
            True if successful
        """
        if amount > self.remaining_quantity:
            return False
        self.filled_quantity += amount
        self.remaining_quantity -= amount
        return True

    def fill_percent(self) -> float:
        """Get fill percentage (0-100)."""
        if self.original_quantity == 0:
            return 0.0
        return (self.filled_quantity / self.original_quantity) * 100


@dataclass
class Order:
    """Complete order representation."""
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exchange_type: ExchangeType = None
    order_type: OrderType = None
    side: OrderSide = None
    symbol: str = ""
    quantity: OrderQuantity = None
    price: OrderPrice = None
    status: OrderStatus = OrderStatus.PENDING
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Exchange reference
    exchange_order_id: Optional[str] = None
    
    # Fees and costs
    fee_amount: float = 0.0
    fee_percent: float = 0.0
    total_cost: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Strategy reference
    strategy_id: Optional[str] = None
    position_id: Optional[str] = None

    def get_pnl(self) -> Optional[float]:
        """Calculate P&L for filled orders."""
        if self.status not in [OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED]:
            return None
        
        if not self.price.average_fill_price or self.quantity.filled_quantity == 0:
            return None
        
        if self.side == OrderSide.BUY:
            # For buys, negative P&L = loss
            return -(self.quantity.filled_quantity * self.price.average_fill_price)
        else:
            # For sells, positive P&L = gain
            return self.quantity.filled_quantity * self.price.average_fill_price

    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED

    def is_partially_filled(self) -> bool:
        """Check if order is partially filled."""
        return self.status == OrderStatus.PARTIALLY_FILLED

    def is_open(self) -> bool:
        """Check if order is still open (can be filled)."""
        return self.status in [OrderStatus.PENDING, OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]

    def is_terminal(self) -> bool:
        """Check if order is in terminal state (no more changes)."""
        return self.status in [
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED
        ]


@dataclass
class Position:
    """Trading position (open trade)."""
    position_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exchange_type: ExchangeType = None
    symbol: str = ""
    side: OrderSide = None
    entry_price: float = 0.0
    entry_quantity: float = 0.0
    current_quantity: float = 0.0
    current_price: float = 0.0
    status: PositionStatus = PositionStatus.OPENING
    
    # Timing
    opened_at: datetime = field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    
    # Orders
    entry_orders: List[str] = field(default_factory=list)  # Order IDs
    exit_orders: List[str] = field(default_factory=list)
    
    # Stop loss and take profit
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    
    # Fees
    entry_fees: float = 0.0
    exit_fees: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_unrealized_pnl(self) -> float:
        """Calculate unrealized P&L."""
        if self.current_quantity == 0:
            return 0.0
        
        if self.side == OrderSide.BUY:
            return self.current_quantity * (self.current_price - self.entry_price)
        else:
            return self.current_quantity * (self.entry_price - self.current_price)

    def get_realized_pnl(self) -> float:
        """Calculate realized P&L (for closed positions)."""
        if self.status != PositionStatus.CLOSED:
            return 0.0
        
        gross_pnl = self.get_unrealized_pnl()
        return gross_pnl - (self.entry_fees + self.exit_fees)

    def get_roi_percent(self) -> float:
        """Get return on investment percentage."""
        if self.entry_price == 0 or self.entry_quantity == 0:
            return 0.0
        
        total_cost = self.entry_price * self.entry_quantity
        pnl = self.get_unrealized_pnl()
        return (pnl / total_cost) * 100

    def is_in_profit(self) -> bool:
        """Check if position is currently in profit."""
        return self.get_unrealized_pnl() > 0

    def hit_stop_loss(self) -> bool:
        """Check if position hit stop loss."""
        if not self.stop_loss_price:
            return False
        
        if self.side == OrderSide.BUY:
            return self.current_price <= self.stop_loss_price
        else:
            return self.current_price >= self.stop_loss_price

    def hit_take_profit(self) -> bool:
        """Check if position hit take profit."""
        if not self.take_profit_price:
            return False
        
        if self.side == OrderSide.BUY:
            return self.current_price >= self.take_profit_price
        else:
            return self.current_price <= self.take_profit_price


@dataclass
class Trade:
    """Executed trade (closed position)."""
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position_id: str = ""
    exchange_type: ExchangeType = None
    symbol: str = ""
    side: OrderSide = None
    
    # Entry
    entry_price: float = 0.0
    entry_quantity: float = 0.0
    entry_time: datetime = field(default_factory=datetime.utcnow)
    entry_fees: float = 0.0
    
    # Exit
    exit_price: float = 0.0
    exit_quantity: float = 0.0
    exit_time: datetime = field(default_factory=datetime.utcnow)
    exit_fees: float = 0.0
    
    # P&L
    realized_pnl: float = 0.0
    roi_percent: float = 0.0
    
    # Metadata
    entry_orders: List[str] = field(default_factory=list)
    exit_orders: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_duration(self) -> timedelta:
        """Get trade duration."""
        return self.exit_time - self.entry_time

    def get_duration_hours(self) -> float:
        """Get trade duration in hours."""
        return self.get_duration().total_seconds() / 3600


# ============================================================================
# Order Manager
# ============================================================================

class OrderManager:
    """Manages order lifecycle and tracking."""

    def __init__(self):
        """Initialize order manager."""
        self.logger = logging.getLogger("OrderManager")
        self.orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []
        self.pending_orders: Dict[str, Order] = {}

    async def create_order(
        self,
        exchange_type: ExchangeType,
        order_type: OrderType,
        side: OrderSide,
        symbol: str,
        quantity: float,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in_seconds: Optional[int] = None
    ) -> Order:
        """Create new order.
        
        Args:
            exchange_type: Exchange type
            order_type: Type of order
            side: Buy or sell
            symbol: Trading pair symbol
            quantity: Order quantity
            limit_price: Limit price (for limit orders)
            stop_price: Stop price (for stop-loss)
            metadata: Additional metadata
            expires_in_seconds: Order expiration time
            
        Returns:
            Created Order object
        """
        order = Order(
            exchange_type=exchange_type,
            order_type=order_type,
            side=side,
            symbol=symbol,
            quantity=OrderQuantity(original_quantity=quantity),
            price=OrderPrice(
                limit_price=limit_price,
                stop_price=stop_price
            ),
            metadata=metadata or {},
            status=OrderStatus.PENDING
        )

        if expires_in_seconds:
            order.expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)

        self.orders[order.order_id] = order
        self.pending_orders[order.order_id] = order
        self.logger.info(f"Created {order_type.value} order {order.order_id} for {side.value} {quantity} {symbol}")

        return order

    async def submit_order(self, order: Order) -> bool:
        """Submit order to exchange.
        
        Args:
            order: Order to submit
            
        Returns:
            True if submission successful
        """
        try:
            order.status = OrderStatus.OPEN
            order.opened_at = datetime.utcnow()
            self.logger.info(f"Submitted order {order.order_id} to exchange")
            return True
        except Exception as e:
            order.status = OrderStatus.REJECTED
            self.logger.error(f"Failed to submit order {order.order_id}: {e}")
            return False

    async def fill_order(
        self,
        order_id: str,
        filled_quantity: float,
        fill_price: float,
        partial: bool = False
    ) -> bool:
        """Fill order (partially or completely).
        
        Args:
            order_id: Order to fill
            filled_quantity: Quantity filled
            fill_price: Price at which filled
            partial: Is this a partial fill?
            
        Returns:
            True if successful
        """
        order = self.orders.get(order_id)
        if not order:
            self.logger.error(f"Order {order_id} not found")
            return False

        if not order.quantity.fill(filled_quantity):
            self.logger.error(f"Cannot fill {filled_quantity}, exceeds remaining quantity")
            return False

        order.price.average_fill_price = fill_price
        
        if partial:
            order.status = OrderStatus.PARTIALLY_FILLED
        else:
            order.status = OrderStatus.FILLED
            order.closed_at = datetime.utcnow()
            if order_id in self.pending_orders:
                del self.pending_orders[order_id]

        self.logger.info(
            f"Filled {filled_quantity} of order {order_id} at {fill_price} "
            f"({order.quantity.fill_percent():.1f}% filled)"
        )
        return True

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order.
        
        Args:
            order_id: Order to cancel
            
        Returns:
            True if successful
        """
        order = self.orders.get(order_id)
        if not order:
            self.logger.error(f"Order {order_id} not found")
            return False

        if order.is_terminal():
            self.logger.warning(f"Cannot cancel terminal order {order_id}")
            return False

        order.status = OrderStatus.CANCELLED
        order.closed_at = datetime.utcnow()
        if order_id in self.pending_orders:
            del self.pending_orders[order_id]

        self.logger.info(f"Cancelled order {order_id}")
        return True

    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        return list(self.pending_orders.values())

    def get_open_orders(self) -> List[Order]:
        """Get all open orders."""
        return [o for o in self.orders.values() if o.is_open()]

    def get_filled_orders(self) -> List[Order]:
        """Get all filled orders."""
        return [o for o in self.orders.values() if o.is_filled()]

    def get_order_stats(self) -> Dict[str, Any]:
        """Get order statistics."""
        total_orders = len(self.orders)
        filled_orders = len(self.get_filled_orders())
        open_orders = len(self.get_open_orders())
        pending_orders = len(self.get_pending_orders())

        return {
            "total_orders": total_orders,
            "filled_orders": filled_orders,
            "open_orders": open_orders,
            "pending_orders": pending_orders,
            "fill_rate_percent": (filled_orders / total_orders * 100) if total_orders > 0 else 0
        }


# ============================================================================
# Position Manager
# ============================================================================

class PositionManager:
    """Manages trading positions."""

    def __init__(self):
        """Initialize position manager."""
        self.logger = logging.getLogger("PositionManager")
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        self.trades: List[Trade] = []

    async def open_position(
        self,
        exchange_type: ExchangeType,
        symbol: str,
        side: OrderSide,
        entry_price: float,
        quantity: float,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Position:
        """Open new position.
        
        Args:
            exchange_type: Exchange type
            symbol: Trading pair
            side: Buy or sell
            entry_price: Entry price
            quantity: Position quantity
            stop_loss_price: Stop loss level
            take_profit_price: Take profit level
            metadata: Additional metadata
            
        Returns:
            Created Position object
        """
        position = Position(
            exchange_type=exchange_type,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            entry_quantity=quantity,
            current_quantity=quantity,
            current_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            metadata=metadata or {}
        )

        self.positions[position.position_id] = position
        self.logger.info(
            f"Opened {side.value} position {position.position_id} on {symbol} "
            f"({quantity} @ {entry_price})"
        )
        return position

    async def update_position_price(
        self,
        position_id: str,
        current_price: float
    ) -> Optional[Position]:
        """Update position current price.
        
        Args:
            position_id: Position to update
            current_price: Current market price
            
        Returns:
            Updated Position or None
        """
        position = self.positions.get(position_id)
        if not position:
            self.logger.error(f"Position {position_id} not found")
            return None

        position.current_price = current_price
        
        # Check stop loss and take profit
        if position.hit_stop_loss():
            self.logger.warning(f"Position {position_id} hit stop loss at {current_price}")
        elif position.hit_take_profit():
            self.logger.info(f"Position {position_id} hit take profit at {current_price}")

        return position

    async def reduce_position(
        self,
        position_id: str,
        quantity: float,
        exit_price: float
    ) -> bool:
        """Reduce or close position.
        
        Args:
            position_id: Position to reduce
            quantity: Quantity to exit
            exit_price: Exit price
            
        Returns:
            True if successful
        """
        position = self.positions.get(position_id)
        if not position:
            self.logger.error(f"Position {position_id} not found")
            return False

        if quantity > position.current_quantity:
            self.logger.error(f"Cannot reduce by {quantity}, only {position.current_quantity} available")
            return False

        position.current_quantity -= quantity

        if position.current_quantity == 0:
            # Position completely closed
            position.status = PositionStatus.CLOSED
            position.closed_at = datetime.utcnow()
            
            # Record as trade
            trade = Trade(
                position_id=position_id,
                exchange_type=position.exchange_type,
                symbol=position.symbol,
                side=position.side,
                entry_price=position.entry_price,
                entry_quantity=position.entry_quantity,
                entry_time=position.opened_at,
                entry_fees=position.entry_fees,
                exit_price=exit_price,
                exit_quantity=quantity,
                exit_time=datetime.utcnow(),
                exit_fees=position.exit_fees
            )
            
            trade.realized_pnl = self._calculate_pnl(
                position.side, position.entry_price, exit_price, quantity
            )
            trade.roi_percent = (trade.realized_pnl / (position.entry_price * quantity)) * 100
            
            self.trades.append(trade)
            del self.positions[position_id]
            self.closed_positions.append(position)
            
            self.logger.info(
                f"Closed position {position_id}: "
                f"PnL ${trade.realized_pnl:.2f} ({trade.roi_percent:.2f}%)"
            )
        else:
            position.status = PositionStatus.OPEN
            self.logger.info(f"Reduced position {position_id} by {quantity}")

        return True

    def _calculate_pnl(
        self,
        side: OrderSide,
        entry_price: float,
        exit_price: float,
        quantity: float
    ) -> float:
        """Calculate P&L for a trade."""
        if side == OrderSide.BUY:
            return (exit_price - entry_price) * quantity
        else:
            return (entry_price - exit_price) * quantity

    def get_open_positions(self) -> List[Position]:
        """Get all open positions."""
        return list(self.positions.values())

    def get_position_stats(self) -> Dict[str, Any]:
        """Get position statistics."""
        open_positions = self.get_open_positions()
        
        total_unrealized_pnl = sum(p.get_unrealized_pnl() for p in open_positions)
        total_realized_pnl = sum(t.realized_pnl for t in self.trades)
        winning_trades = sum(1 for t in self.trades if t.realized_pnl > 0)
        losing_trades = sum(1 for t in self.trades if t.realized_pnl < 0)

        return {
            "open_positions": len(open_positions),
            "closed_positions": len(self.closed_positions),
            "total_trades": len(self.trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate_percent": (winning_trades / len(self.trades) * 100) if self.trades else 0,
            "unrealized_pnl": total_unrealized_pnl,
            "realized_pnl": total_realized_pnl,
            "total_pnl": total_unrealized_pnl + total_realized_pnl
        }


# ============================================================================
# Portfolio Manager
# ============================================================================

class PortfolioManager:
    """Manages overall portfolio and account."""

    def __init__(self, initial_capital: float):
        """Initialize portfolio manager.
        
        Args:
            initial_capital: Starting capital in USD
        """
        self.logger = logging.getLogger("PortfolioManager")
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.order_manager = OrderManager()
        self.position_manager = PositionManager()
        self.cash_balance = initial_capital
        self.last_update = datetime.utcnow()

    async def update_portfolio(self, balances: Dict[str, AccountBalance]) -> None:
        """Update portfolio with exchange balances.
        
        Args:
            balances: Dict of exchange balances
        """
        # Recalculate portfolio value
        total_positions_value = sum(
            p.current_quantity * p.current_price
            for p in self.position_manager.get_open_positions()
        )
        
        total_balance = self.cash_balance + total_positions_value
        self.current_capital = total_balance
        self.last_update = datetime.utcnow()
        
        self.logger.info(
            f"Portfolio updated: ${total_balance:.2f} "
            f"(positions: ${total_positions_value:.2f})"
        )

    def get_portfolio_value(self) -> float:
        """Get total portfolio value."""
        open_positions = self.position_manager.get_open_positions()
        positions_value = sum(
            p.current_quantity * p.current_price for p in open_positions
        )
        return self.cash_balance + positions_value

    def get_portfolio_stats(self) -> Dict[str, Any]:
        """Get comprehensive portfolio statistics."""
        position_stats = self.position_manager.get_position_stats()
        order_stats = self.order_manager.get_order_stats()
        
        portfolio_value = self.get_portfolio_value()
        total_return = ((portfolio_value - self.initial_capital) / self.initial_capital) * 100

        return {
            "portfolio_value": portfolio_value,
            "initial_capital": self.initial_capital,
            "total_return_percent": total_return,
            "cash_balance": self.cash_balance,
            **position_stats,
            **order_stats
        }

    async def execute_buy_order(
        self,
        exchange_type: ExchangeType,
        symbol: str,
        quantity: float,
        price: float
    ) -> Optional[Order]:
        """Execute buy order."""
        cost = quantity * price
        if cost > self.cash_balance:
            self.logger.error(f"Insufficient funds: need ${cost}, have ${self.cash_balance}")
            return None

        order = await self.order_manager.create_order(
            exchange_type=exchange_type,
            order_type=OrderType.LIMIT,
            side=OrderSide.BUY,
            symbol=symbol,
            quantity=quantity,
            limit_price=price
        )

        # Reserve cash
        self.cash_balance -= cost
        return order

    async def execute_sell_order(
        self,
        exchange_type: ExchangeType,
        symbol: str,
        quantity: float,
        price: float
    ) -> Optional[Order]:
        """Execute sell order."""
        order = await self.order_manager.create_order(
            exchange_type=exchange_type,
            order_type=OrderType.LIMIT,
            side=OrderSide.SELL,
            symbol=symbol,
            quantity=quantity,
            limit_price=price
        )

        # Add proceeds to cash
        proceeds = quantity * price
        self.cash_balance += proceeds
        return order

    def print_portfolio_summary(self) -> None:
        """Print portfolio summary to console."""
        stats = self.get_portfolio_stats()
        
        print("\n" + "=" * 80)
        print("📊 PORTFOLIO SUMMARY")
        print("=" * 80)
        print(f"Portfolio Value: ${stats['portfolio_value']:.2f}")
        print(f"Initial Capital: ${stats['initial_capital']:.2f}")
        print(f"Total Return: {stats['total_return_percent']:.2f}%")
        print(f"Cash Balance: ${stats['cash_balance']:.2f}")
        print(f"\nPositions: {stats['open_positions']} open, {stats['closed_positions']} closed")
        print(f"Trades: {stats['total_trades']} total ({stats['winning_trades']} wins, {stats['losing_trades']} losses)")
        print(f"Win Rate: {stats['win_rate_percent']:.1f}%")
        print(f"Unrealized P&L: ${stats['unrealized_pnl']:.2f}")
        print(f"Realized P&L: ${stats['realized_pnl']:.2f}")
        print(f"Total P&L: ${stats['total_pnl']:.2f}")
        print("=" * 80 + "\n")


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(level: str = "INFO") -> None:
    """Setup logging for order management.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


if __name__ == "__main__":
    setup_logging()
    print("Order Management System - Import this module to use")
