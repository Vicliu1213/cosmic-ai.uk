#!/usr/bin/env python3
"""
Order Execution Engine
訂單執行引擎

Real-time order execution engine for multi-exchange trading:
- Market order execution
- Limit order matching
- Order book tracking
- Execution simulation
- Trade confirmation

This module provides:
1. Order book management
2. Execution engine for different order types
3. Slippage and fee calculations
4. Execution simulation for backtesting
5. Trade confirmation and settlement
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from src.phase5.order_management import (
    Order, OrderType, OrderSide, OrderStatus, Position,
    PortfolioManager
)
from src.phase5.exchange_connector import ExchangeType


# ============================================================================
# Enums
# ============================================================================

class ExecutionStatus(Enum):
    """Execution result status."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    INSUFFICIENT_LIQUIDITY = "insufficient_liquidity"
    PRICE_SLIPPAGE = "price_slippage"
    TIMEOUT = "timeout"


class ExecutionMode(Enum):
    """Execution mode for backtesting vs live."""
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class OrderBook:
    """Order book for a trading pair."""
    symbol: str
    exchange_type: ExchangeType
    timestamp: datetime
    
    # Bid side (buy orders)
    bids: List[Tuple[float, float]] = field(default_factory=list)  # (price, quantity)
    
    # Ask side (sell orders)
    asks: List[Tuple[float, float]] = field(default_factory=list)  # (price, quantity)
    
    # Statistics
    last_trade_price: Optional[float] = None
    bid_ask_spread: Optional[float] = None


@dataclass
class ExecutionResult:
    """Result of order execution attempt."""
    order_id: str
    status: ExecutionStatus
    executed: bool = False
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    total_cost: float = 0.0
    fee: float = 0.0
    slippage: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStats:
    """Statistics for order executions."""
    total_executions: int = 0
    successful_executions: int = 0
    partial_executions: int = 0
    failed_executions: int = 0
    total_slippage: float = 0.0
    total_fees: float = 0.0
    average_fill_price: float = 0.0


# ============================================================================
# Order Book Manager
# ============================================================================

class OrderBookManager:
    """Manages order books for trading pairs."""

    def __init__(self):
        """Initialize order book manager."""
        self.logger = logging.getLogger("OrderBookManager")
        self.order_books: Dict[Tuple[ExchangeType, str], OrderBook] = {}
        self.book_history: List[OrderBook] = []

    async def update_order_book(
        self,
        symbol: str,
        exchange_type: ExchangeType,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
        last_trade_price: Optional[float] = None
    ) -> OrderBook:
        """Update order book for a symbol.
        
        Args:
            symbol: Trading pair symbol
            exchange_type: Exchange
            bids: Bid levels [(price, quantity), ...]
            asks: Ask levels [(price, quantity), ...]
            last_trade_price: Last executed trade price
            
        Returns:
            Updated OrderBook
        """
        key = (exchange_type, symbol)
        
        book = OrderBook(
            symbol=symbol,
            exchange_type=exchange_type,
            timestamp=datetime.utcnow(),
            bids=bids,
            asks=asks,
            last_trade_price=last_trade_price
        )
        
        # Calculate bid-ask spread
        if bids and asks:
            best_bid = bids[0][0]
            best_ask = asks[0][0]
            book.bid_ask_spread = best_ask - best_bid
        
        self.order_books[key] = book
        self.book_history.append(book)
        
        return book

    def get_order_book(
        self,
        symbol: str,
        exchange_type: ExchangeType
    ) -> Optional[OrderBook]:
        """Get current order book for symbol.
        
        Args:
            symbol: Trading pair symbol
            exchange_type: Exchange
            
        Returns:
            OrderBook or None if not available
        """
        key = (exchange_type, symbol)
        return self.order_books.get(key)

    def get_best_bid(
        self,
        symbol: str,
        exchange_type: ExchangeType
    ) -> Optional[float]:
        """Get best bid price."""
        book = self.get_order_book(symbol, exchange_type)
        if book and book.bids:
            return book.bids[0][0]
        return None

    def get_best_ask(
        self,
        symbol: str,
        exchange_type: ExchangeType
    ) -> Optional[float]:
        """Get best ask price."""
        book = self.get_order_book(symbol, exchange_type)
        if book and book.asks:
            return book.asks[0][0]
        return None

    def get_mid_price(
        self,
        symbol: str,
        exchange_type: ExchangeType
    ) -> Optional[float]:
        """Get mid price (average of best bid and ask)."""
        best_bid = self.get_best_bid(symbol, exchange_type)
        best_ask = self.get_best_ask(symbol, exchange_type)
        
        if best_bid and best_ask:
            return (best_bid + best_ask) / 2
        return None


# ============================================================================
# Execution Engine
# ============================================================================

class OrderExecutionEngine:
    """Executes orders based on order book data."""

    def __init__(
        self,
        mode: ExecutionMode = ExecutionMode.BACKTEST,
        slippage_percent: float = 0.1,
        fee_percent: float = 0.1
    ):
        """Initialize execution engine.
        
        Args:
            mode: Execution mode (backtest, paper, live)
            slippage_percent: Expected slippage percentage
            fee_percent: Trading fee percentage
        """
        self.logger = logging.getLogger("OrderExecutionEngine")
        self.mode = mode
        self.slippage_percent = slippage_percent
        self.fee_percent = fee_percent
        self.order_book_manager = OrderBookManager()
        self.execution_history: List[ExecutionResult] = []
        self.stats = ExecutionStats()

    async def execute_market_order(
        self,
        order: Order
    ) -> ExecutionResult:
        """Execute market order immediately at best available price.
        
        Args:
            order: Order to execute
            
        Returns:
            ExecutionResult with execution details
        """
        self.logger.info(f"Executing market order {order.order_id} for {order.quantity.original_quantity} {order.symbol}")
        
        # Get order book
        book = self.order_book_manager.get_order_book(
            order.symbol,
            order.exchange_type
        )
        
        if not book:
            return ExecutionResult(
                order_id=order.order_id,
                status=ExecutionStatus.FAILED,
                message="No order book available"
            )

        result = await self._execute_against_orderbook(order, book)
        self.execution_history.append(result)
        self._update_stats(result)
        
        return result

    async def execute_limit_order(
        self,
        order: Order
    ) -> ExecutionResult:
        """Execute limit order - only fill if limit price is met.
        
        Args:
            order: Limit order to execute
            
        Returns:
            ExecutionResult with execution details
        """
        self.logger.info(
            f"Executing limit order {order.order_id} at ${order.price.limit_price} "
            f"for {order.quantity.original_quantity} {order.symbol}"
        )
        
        book = self.order_book_manager.get_order_book(
            order.symbol,
            order.exchange_type
        )
        
        if not book:
            return ExecutionResult(
                order_id=order.order_id,
                status=ExecutionStatus.FAILED,
                message="No order book available"
            )

        # Check if limit price can be met
        if order.side == OrderSide.BUY:
            best_ask = self.order_book_manager.get_best_ask(
                order.symbol,
                order.exchange_type
            )
            if not best_ask or best_ask > order.price.limit_price:
                return ExecutionResult(
                    order_id=order.order_id,
                    status=ExecutionStatus.FAILED,
                    message=f"Current ask ${best_ask} exceeds limit ${order.price.limit_price}",
                    details={"best_ask": best_ask}
                )
        else:  # SELL
            best_bid = self.order_book_manager.get_best_bid(
                order.symbol,
                order.exchange_type
            )
            if not best_bid or best_bid < order.price.limit_price:
                return ExecutionResult(
                    order_id=order.order_id,
                    status=ExecutionStatus.FAILED,
                    message=f"Current bid ${best_bid} below limit ${order.price.limit_price}",
                    details={"best_bid": best_bid}
                )

        result = await self._execute_against_orderbook(order, book)
        self.execution_history.append(result)
        self._update_stats(result)
        
        return result

    async def execute_stop_loss_order(
        self,
        order: Order,
        current_price: float
    ) -> ExecutionResult:
        """Execute stop-loss order if price triggers.
        
        Args:
            order: Stop-loss order
            current_price: Current market price
            
        Returns:
            ExecutionResult with execution details
        """
        self.logger.info(
            f"Checking stop-loss order {order.order_id} (trigger: ${order.price.stop_price}, "
            f"current: ${current_price})"
        )
        
        # Check if stop price is triggered
        if order.side == OrderSide.BUY:
            if current_price > order.price.stop_price:
                return ExecutionResult(
                    order_id=order.order_id,
                    status=ExecutionStatus.FAILED,
                    message=f"Stop not triggered (current ${current_price} < stop ${order.price.stop_price})"
                )
        else:  # SELL
            if current_price < order.price.stop_price:
                return ExecutionResult(
                    order_id=order.order_id,
                    status=ExecutionStatus.FAILED,
                    message=f"Stop not triggered (current ${current_price} > stop ${order.price.stop_price})"
                )

        # Execute as market order once triggered
        return await self.execute_market_order(order)

    async def _execute_against_orderbook(
        self,
        order: Order,
        book: OrderBook
    ) -> ExecutionResult:
        """Execute order against order book with slippage calculation.
        
        Args:
            order: Order to execute
            book: Order book
            
        Returns:
            ExecutionResult
        """
        result = ExecutionResult(order_id=order.order_id, status=ExecutionStatus.SUCCESS)
        
        if order.side == OrderSide.BUY:
            # Buy: execute at ask side
            fill_price, filled_qty = await self._fill_from_asks(
                order.quantity.original_quantity,
                book.asks
            )
        else:  # SELL
            # Sell: execute at bid side
            fill_price, filled_qty = await self._fill_from_bids(
                order.quantity.original_quantity,
                book.bids
            )

        if filled_qty == 0:
            result.status = ExecutionStatus.INSUFFICIENT_LIQUIDITY
            result.message = "Insufficient liquidity to fill order"
            return result

        # Calculate slippage
        if order.side == OrderSide.BUY:
            best_ask = book.asks[0][0] if book.asks else fill_price
            slippage = fill_price - best_ask
        else:
            best_bid = book.bids[0][0] if book.bids else fill_price
            slippage = best_bid - fill_price

        # Calculate fees
        fee = (filled_qty * fill_price) * (self.fee_percent / 100)

        result.executed = True
        result.filled_quantity = filled_qty
        result.filled_price = fill_price
        result.total_cost = filled_qty * fill_price
        result.fee = fee
        result.slippage = slippage
        
        if filled_qty < order.quantity.original_quantity:
            result.status = ExecutionStatus.PARTIAL
            result.message = f"Partially filled: {filled_qty}/{order.quantity.original_quantity}"
        else:
            result.message = f"Successfully executed {filled_qty} @ ${fill_price}"

        return result

    async def _fill_from_asks(
        self,
        quantity_needed: float,
        asks: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Fill buy order from ask side of order book.
        
        Args:
            quantity_needed: Quantity to buy
            asks: Ask levels
            
        Returns:
            Tuple of (average_fill_price, filled_quantity)
        """
        total_cost = 0.0
        total_filled = 0.0

        for ask_price, ask_qty in asks:
            if total_filled >= quantity_needed:
                break
            
            qty_to_fill = min(ask_qty, quantity_needed - total_filled)
            total_cost += qty_to_fill * ask_price
            total_filled += qty_to_fill

        if total_filled == 0:
            return 0.0, 0.0

        average_price = total_cost / total_filled
        # Add slippage
        average_price += (average_price * self.slippage_percent / 100)
        
        return average_price, total_filled

    async def _fill_from_bids(
        self,
        quantity_needed: float,
        bids: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Fill sell order from bid side of order book.
        
        Args:
            quantity_needed: Quantity to sell
            bids: Bid levels
            
        Returns:
            Tuple of (average_fill_price, filled_quantity)
        """
        total_proceeds = 0.0
        total_filled = 0.0

        for bid_price, bid_qty in bids:
            if total_filled >= quantity_needed:
                break
            
            qty_to_fill = min(bid_qty, quantity_needed - total_filled)
            total_proceeds += qty_to_fill * bid_price
            total_filled += qty_to_fill

        if total_filled == 0:
            return 0.0, 0.0

        average_price = total_proceeds / total_filled
        # Subtract slippage
        average_price -= (average_price * self.slippage_percent / 100)
        
        return average_price, total_filled

    def _update_stats(self, result: ExecutionResult) -> None:
        """Update execution statistics.
        
        Args:
            result: Execution result
        """
        self.stats.total_executions += 1
        
        if result.status == ExecutionStatus.SUCCESS:
            self.stats.successful_executions += 1
        elif result.status == ExecutionStatus.PARTIAL:
            self.stats.partial_executions += 1
        else:
            self.stats.failed_executions += 1

        self.stats.total_slippage += result.slippage
        self.stats.total_fees += result.fee

        if self.stats.successful_executions + self.stats.partial_executions > 0:
            total_cost = sum(
                e.total_cost for e in self.execution_history
                if e.status in [ExecutionStatus.SUCCESS, ExecutionStatus.PARTIAL]
            )
            total_filled = sum(
                e.filled_quantity for e in self.execution_history
                if e.status in [ExecutionStatus.SUCCESS, ExecutionStatus.PARTIAL]
            )
            if total_filled > 0:
                self.stats.average_fill_price = total_cost / total_filled

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics.
        
        Returns:
            Dict with execution statistics
        """
        return {
            "total_executions": self.stats.total_executions,
            "successful_executions": self.stats.successful_executions,
            "partial_executions": self.stats.partial_executions,
            "failed_executions": self.stats.failed_executions,
            "success_rate_percent": (
                (self.stats.successful_executions + self.stats.partial_executions) /
                self.stats.total_executions * 100
                if self.stats.total_executions > 0 else 0
            ),
            "total_slippage": self.stats.total_slippage,
            "total_fees": self.stats.total_fees,
            "average_fill_price": self.stats.average_fill_price
        }


# ============================================================================
# Integrated Trading Engine
# ============================================================================

class TradingEngine:
    """Complete trading engine combining order management and execution."""

    def __init__(
        self,
        portfolio_manager: PortfolioManager,
        execution_mode: ExecutionMode = ExecutionMode.BACKTEST,
        slippage_percent: float = 0.1,
        fee_percent: float = 0.1
    ):
        """Initialize trading engine.
        
        Args:
            portfolio_manager: Portfolio manager instance
            execution_mode: Execution mode
            slippage_percent: Expected slippage
            fee_percent: Trading fee percentage
        """
        self.logger = logging.getLogger("TradingEngine")
        self.portfolio_manager = portfolio_manager
        self.execution_engine = OrderExecutionEngine(
            mode=execution_mode,
            slippage_percent=slippage_percent,
            fee_percent=fee_percent
        )

    async def execute_buy(
        self,
        symbol: str,
        quantity: float,
        limit_price: Optional[float] = None
    ) -> ExecutionResult:
        """Execute buy order.
        
        Args:
            symbol: Symbol to buy
            quantity: Quantity to buy
            limit_price: Limit price (None = market order)
            
        Returns:
            ExecutionResult
        """
        order = await self.portfolio_manager.order_manager.create_order(
            exchange_type=ExchangeType.BINANCE,  # Default to Binance
            order_type=OrderType.MARKET if not limit_price else OrderType.LIMIT,
            side=OrderSide.BUY,
            symbol=symbol,
            quantity=quantity,
            limit_price=limit_price
        )

        if limit_price:
            result = await self.execution_engine.execute_limit_order(order)
        else:
            result = await self.execution_engine.execute_market_order(order)

        if result.executed and result.filled_quantity > 0:
            await self.portfolio_manager.order_manager.fill_order(
                order.order_id,
                result.filled_quantity,
                result.filled_price,
                partial=(result.status == ExecutionStatus.PARTIAL)
            )

        return result

    async def execute_sell(
        self,
        symbol: str,
        quantity: float,
        limit_price: Optional[float] = None
    ) -> ExecutionResult:
        """Execute sell order.
        
        Args:
            symbol: Symbol to sell
            quantity: Quantity to sell
            limit_price: Limit price (None = market order)
            
        Returns:
            ExecutionResult
        """
        order = await self.portfolio_manager.order_manager.create_order(
            exchange_type=ExchangeType.BINANCE,  # Default to Binance
            order_type=OrderType.MARKET if not limit_price else OrderType.LIMIT,
            side=OrderSide.SELL,
            symbol=symbol,
            quantity=quantity,
            limit_price=limit_price
        )

        if limit_price:
            result = await self.execution_engine.execute_limit_order(order)
        else:
            result = await self.execution_engine.execute_market_order(order)

        if result.executed and result.filled_quantity > 0:
            await self.portfolio_manager.order_manager.fill_order(
                order.order_id,
                result.filled_quantity,
                result.filled_price,
                partial=(result.status == ExecutionStatus.PARTIAL)
            )

        return result

    def print_execution_summary(self) -> None:
        """Print execution summary."""
        stats = self.execution_engine.get_execution_stats()
        
        print("\n" + "=" * 80)
        print("⚡ EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Total Executions: {stats['total_executions']}")
        print(f"Successful: {stats['successful_executions']}")
        print(f"Partial: {stats['partial_executions']}")
        print(f"Failed: {stats['failed_executions']}")
        print(f"Success Rate: {stats['success_rate_percent']:.1f}%")
        print(f"Total Slippage: ${stats['total_slippage']:.2f}")
        print(f"Total Fees: ${stats['total_fees']:.2f}")
        print(f"Average Fill Price: ${stats['average_fill_price']:.2f}")
        print("=" * 80 + "\n")


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(level: str = "INFO") -> None:
    """Setup logging for execution engine.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


if __name__ == "__main__":
    setup_logging()
    print("Order Execution Engine - Import this module to use")
