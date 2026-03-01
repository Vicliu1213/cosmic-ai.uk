#!/usr/bin/env python3
"""
Order Monitoring System
訂單監控系統

Real-time monitoring and alerting for orders, positions, and portfolios:
- Order status tracking and change detection
- Order book monitoring
- Portfolio tracking
- Event notifications
- Performance alerts

This module provides:
1. OrderStatusMonitor for tracking order lifecycle
2. OrderBookWatcher for market data monitoring
3. PortfolioMonitor for real-time portfolio metrics
4. EventNotifier for alert generation
5. MonitoringDashboard for aggregate reporting
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
import uuid

from src.phase5.order_management import (
    Order, OrderStatus, Position, PositionStatus, OrderSide,
    OrderManager, PositionManager, PortfolioManager
)
from src.phase5.order_execution import (
    OrderBook, ExecutionResult, OrderBookManager, ExecutionMode
)
from src.phase5.exchange_connector import ExchangeType


# ============================================================================
# Enums
# ============================================================================

class AlertLevel(Enum):
    """Alert severity level."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """Type of alert event."""
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_REJECTED = "order_rejected"
    ORDER_EXPIRED = "order_expired"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    STOP_LOSS_HIT = "stop_loss_hit"
    TAKE_PROFIT_HIT = "take_profit_hit"
    PRICE_SPIKE = "price_spike"
    LIQUIDITY_WARNING = "liquidity_warning"
    PORTFOLIO_MILESTONE = "portfolio_milestone"
    LARGE_FILL = "large_fill"


class MonitoringState(Enum):
    """State of a monitoring session."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class OrderStatusSnapshot:
    """Snapshot of order status at a point in time."""
    order_id: str
    status: OrderStatus
    timestamp: datetime
    filled_quantity: float
    average_fill_price: Optional[float]
    total_cost: float
    fee_amount: float


@dataclass
class PortfolioSnapshot:
    """Snapshot of portfolio state at a point in time."""
    timestamp: datetime
    total_value: float
    cash_balance: float
    position_count: int
    open_positions_value: float
    unrealized_pnl: float
    realized_pnl: float
    total_trades: int
    win_rate: float


@dataclass
class Alert:
    """Alert notification event."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: Optional[AlertType] = None
    level: AlertLevel = AlertLevel.INFO
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message: str = ""
    order_id: Optional[str] = None
    position_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


@dataclass
class MonitoringMetrics:
    """Aggregate monitoring metrics."""
    monitoring_start: datetime
    monitoring_duration: timedelta
    active_orders: int
    filled_orders: int
    cancelled_orders: int
    active_positions: int
    closed_positions: int
    total_alerts: int
    critical_alerts: int
    average_fill_time: Optional[float]
    average_position_duration: Optional[float]


# ============================================================================
# Order Status Monitor
# ============================================================================

class OrderStatusMonitor:
    """Tracks order status changes and state transitions."""

    def __init__(self, order_manager: OrderManager):
        """Initialize order status monitor.
        
        Args:
            order_manager: OrderManager instance to monitor
        """
        self.logger = logging.getLogger("OrderStatusMonitor")
        self.order_manager = order_manager
        self.status_snapshots: Dict[str, List[OrderStatusSnapshot]] = {}
        self.status_callbacks: List[Callable] = []
        self.monitored_orders: Set[str] = set()

    def register_status_callback(
        self,
        callback: Callable[[Order, OrderStatus, OrderStatus], None]
    ) -> None:
        """Register callback for order status changes.
        
        Args:
            callback: Function called when status changes (order, old_status, new_status)
        """
        self.status_callbacks.append(callback)
        self.logger.debug(f"Registered status callback: {callback.__name__}")

    async def monitor_order(self, order_id: str) -> None:
        """Start monitoring an order.
        
        Args:
            order_id: Order ID to monitor
        """
        self.monitored_orders.add(order_id)
        self.status_snapshots[order_id] = []
        self.logger.info(f"Started monitoring order {order_id}")

    async def stop_monitoring_order(self, order_id: str) -> None:
        """Stop monitoring an order.
        
        Args:
            order_id: Order ID to stop monitoring
        """
        self.monitored_orders.discard(order_id)
        self.logger.info(f"Stopped monitoring order {order_id}")

    async def check_status_updates(self) -> List[Tuple[Order, OrderStatus, OrderStatus]]:
        """Check all monitored orders for status changes.
        
        Returns:
            List of (order, old_status, new_status) tuples for changed orders
        """
        status_changes: List[Tuple[Order, OrderStatus, OrderStatus]] = []

        for order_id in list(self.monitored_orders):
            order = self.order_manager.orders.get(order_id)
            if not order:
                self.monitored_orders.discard(order_id)
                continue

            # Get last known status
            snapshots = self.status_snapshots[order_id]
            old_status = snapshots[-1].status if snapshots else order.status

            # Create snapshot
            snapshot = OrderStatusSnapshot(
                order_id=order.order_id,
                status=order.status,
                timestamp=datetime.utcnow(),
                filled_quantity=order.quantity.filled_quantity,
                average_fill_price=order.price.average_fill_price,
                total_cost=order.total_cost,
                fee_amount=order.fee_amount
            )
            snapshots.append(snapshot)

            # Check for status change
            if order.status != old_status:
                status_changes.append((order, old_status, order.status))
                self.logger.info(
                    f"Order {order_id} status changed: {old_status.value} → {order.status.value}"
                )

                # Trigger callbacks
                for callback in self.status_callbacks:
                    try:
                        callback(order, old_status, order.status)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")

        return status_changes

    def get_order_history(self, order_id: str) -> List[OrderStatusSnapshot]:
        """Get status history for an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            List of status snapshots in chronological order
        """
        return self.status_snapshots.get(order_id, [])

    def get_fill_time(self, order_id: str) -> Optional[timedelta]:
        """Calculate time from submission to fill.
        
        Args:
            order_id: Order ID
            
        Returns:
            Time delta or None if not filled
        """
        snapshots = self.get_order_history(order_id)
        if not snapshots:
            return None

        # Find submission (OPEN) and fill timestamps
        open_snapshot = None
        fill_snapshot = None

        for snapshot in snapshots:
            if snapshot.status == OrderStatus.OPEN and not open_snapshot:
                open_snapshot = snapshot
            if snapshot.status == OrderStatus.FILLED:
                fill_snapshot = snapshot

        if open_snapshot and fill_snapshot:
            return fill_snapshot.timestamp - open_snapshot.timestamp

        return None


# ============================================================================
# Order Book Watcher
# ============================================================================

class OrderBookWatcher:
    """Monitors order book changes and market conditions."""

    def __init__(self, book_manager: OrderBookManager):
        """Initialize order book watcher.
        
        Args:
            book_manager: OrderBookManager instance
        """
        self.logger = logging.getLogger("OrderBookWatcher")
        self.book_manager = book_manager
        self.watched_symbols: Dict[Tuple[ExchangeType, str], List[OrderBook]] = {}
        self.spread_history: Dict[Tuple[ExchangeType, str], List[float]] = {}
        self.price_alerts: Dict[Tuple[ExchangeType, str], Tuple[float, float]] = {}
        self.book_callbacks: List[Callable] = []

    def register_book_callback(
        self,
        callback: Callable[[OrderBook, Optional[OrderBook]], None]
    ) -> None:
        """Register callback for order book updates.
        
        Args:
            callback: Function called with (new_book, previous_book)
        """
        self.book_callbacks.append(callback)
        self.logger.debug(f"Registered book callback: {callback.__name__}")

    def watch_symbol(
        self,
        symbol: str,
        exchange_type: ExchangeType,
        price_lower_alert: Optional[float] = None,
        price_upper_alert: Optional[float] = None
    ) -> None:
        """Start watching a trading pair.
        
        Args:
            symbol: Trading pair symbol
            exchange_type: Exchange
            price_lower_alert: Alert if price drops below this
            price_upper_alert: Alert if price rises above this
        """
        key = (exchange_type, symbol)
        self.watched_symbols[key] = []
        self.spread_history[key] = []
        
        if price_lower_alert or price_upper_alert:
            self.price_alerts[key] = (price_lower_alert or 0, price_upper_alert or float('inf'))
        
        self.logger.info(f"Started watching {symbol} on {exchange_type.value}")

    async def check_book_updates(self) -> List[Tuple[OrderBook, Optional[OrderBook]]]:
        """Check for order book updates.
        
        Returns:
            List of (new_book, previous_book) tuples
        """
        updates: List[Tuple[OrderBook, Optional[OrderBook]]] = []

        for key in list(self.watched_symbols.keys()):
            exchange_type, symbol = key
            book = self.book_manager.get_order_book(symbol, exchange_type)
            
            if not book:
                continue

            history = self.watched_symbols[key]
            previous_book = history[-1] if history else None

            # Store book
            history.append(book)

            # Track spread
            if book.bid_ask_spread:
                self.spread_history[key].append(book.bid_ask_spread)

            # Check for update
            if previous_book is None or book.timestamp > previous_book.timestamp:
                updates.append((book, previous_book))

                # Trigger callbacks
                for callback in self.book_callbacks:
                    try:
                        callback(book, previous_book)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")

        return updates

    def get_average_spread(
        self,
        symbol: str,
        exchange_type: ExchangeType,
        window: int = 100
    ) -> Optional[float]:
        """Get average bid-ask spread.
        
        Args:
            symbol: Trading pair symbol
            exchange_type: Exchange
            window: Number of recent spreads to average
            
        Returns:
            Average spread or None
        """
        key = (exchange_type, symbol)
        spreads = self.spread_history.get(key, [])
        
        if not spreads:
            return None
        
        recent = spreads[-window:] if len(spreads) > window else spreads
        return sum(recent) / len(recent)

    def detect_price_spike(
        self,
        symbol: str,
        exchange_type: ExchangeType,
        threshold_percent: float = 2.0
    ) -> bool:
        """Detect significant price movement.
        
        Args:
            symbol: Trading pair symbol
            exchange_type: Exchange
            threshold_percent: Price movement threshold %
            
        Returns:
            True if spike detected
        """
        key = (exchange_type, symbol)
        history = self.watched_symbols.get(key, [])
        
        if len(history) < 2:
            return False

        current = history[-1]
        previous = history[-2]

        if not current.last_trade_price or not previous.last_trade_price:
            return False

        price_change_percent = abs(
            (current.last_trade_price - previous.last_trade_price) / previous.last_trade_price
        ) * 100

        return price_change_percent >= threshold_percent


# ============================================================================
# Portfolio Monitor
# ============================================================================

class PortfolioMonitor:
    """Monitors portfolio performance and metrics."""

    def __init__(self, portfolio_manager: PortfolioManager):
        """Initialize portfolio monitor.
        
        Args:
            portfolio_manager: PortfolioManager instance
        """
        self.logger = logging.getLogger("PortfolioMonitor")
        self.portfolio_manager = portfolio_manager
        self.snapshots: List[PortfolioSnapshot] = []
        self.portfolio_callbacks: List[Callable] = []

    def register_portfolio_callback(
        self,
        callback: Callable[[PortfolioSnapshot], None]
    ) -> None:
        """Register callback for portfolio updates.
        
        Args:
            callback: Function called with portfolio snapshot
        """
        self.portfolio_callbacks.append(callback)
        self.logger.debug(f"Registered portfolio callback: {callback.__name__}")

    async def take_snapshot(self) -> PortfolioSnapshot:
        """Take snapshot of current portfolio state.
        
        Returns:
            PortfolioSnapshot
        """
        portfolio = self.portfolio_manager
        
        # Calculate metrics
        open_positions = portfolio.position_manager.get_open_positions()
        closed_positions = [p for p in portfolio.position_manager.positions.values() 
                           if p.status == PositionStatus.CLOSED]
        
        total_unrealized_pnl = sum(p.get_unrealized_pnl() for p in open_positions)
        total_realized_pnl = sum(p.get_realized_pnl() for p in closed_positions)
        open_positions_value = sum(
            p.current_quantity * p.current_price for p in open_positions
        )
        
        # Calculate win rate
        win_rate = 0.0
        if closed_positions:
            wins = sum(1 for p in closed_positions if p.get_realized_pnl() > 0)
            win_rate = (wins / len(closed_positions)) * 100

        snapshot = PortfolioSnapshot(
            timestamp=datetime.utcnow(),
            total_value=portfolio.get_portfolio_value(),
            cash_balance=portfolio.cash_balance,
            position_count=len(open_positions),
            open_positions_value=open_positions_value,
            unrealized_pnl=total_unrealized_pnl,
            realized_pnl=total_realized_pnl,
            total_trades=len(closed_positions),
            win_rate=win_rate
        )
        
        self.snapshots.append(snapshot)
        
        # Trigger callbacks
        for callback in self.portfolio_callbacks:
            try:
                callback(snapshot)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
        
        return snapshot

    def get_portfolio_history(
        self,
        lookback_minutes: int = 60
    ) -> List[PortfolioSnapshot]:
        """Get portfolio snapshots within lookback period.
        
        Args:
            lookback_minutes: Minutes to look back
            
        Returns:
            List of portfolio snapshots
        """
        cutoff = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        return [s for s in self.snapshots if s.timestamp >= cutoff]

    def get_daily_return(self) -> Optional[float]:
        """Calculate daily return percentage.
        
        Returns:
            Daily return % or None
        """
        if not self.snapshots or len(self.snapshots) < 2:
            return None

        day_ago = datetime.utcnow() - timedelta(days=1)
        old_snapshot = None
        
        for snapshot in self.snapshots:
            if snapshot.timestamp <= day_ago:
                old_snapshot = snapshot

        if not old_snapshot:
            return None

        current = self.snapshots[-1]
        if old_snapshot.total_value == 0:
            return None

        return ((current.total_value - old_snapshot.total_value) / old_snapshot.total_value) * 100


# ============================================================================
# Event Notifier
# ============================================================================

class EventNotifier:
    """Generates and manages alerts."""

    def __init__(self):
        """Initialize event notifier."""
        self.logger = logging.getLogger("EventNotifier")
        self.alerts: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.alert_filters: Dict[AlertType, Callable[[Alert], bool]] = {}

    def register_alert_callback(
        self,
        callback: Callable[[Alert], None]
    ) -> None:
        """Register callback for alerts.
        
        Args:
            callback: Function called with alert
        """
        self.alert_callbacks.append(callback)
        self.logger.debug(f"Registered alert callback: {callback.__name__}")

    def set_alert_filter(
        self,
        alert_type: AlertType,
        filter_func: Callable[[Alert], bool]
    ) -> None:
        """Set filter for alert type (suppress certain alerts).
        
        Args:
            alert_type: Type of alert to filter
            filter_func: Function returning True to suppress alert
        """
        self.alert_filters[alert_type] = filter_func
        self.logger.debug(f"Set filter for {alert_type.value}")

    async def emit_alert(
        self,
        alert_type: AlertType,
        level: AlertLevel,
        message: str,
        order_id: Optional[str] = None,
        position_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Emit an alert.
        
        Args:
            alert_type: Type of alert
            level: Severity level
            message: Alert message
            order_id: Related order ID
            position_id: Related position ID
            data: Additional data
            
        Returns:
            Alert object
        """
        alert = Alert(
            alert_type=alert_type,
            level=level,
            message=message,
            order_id=order_id,
            position_id=position_id,
            data=data or {}
        )

        # Check filters
        if alert_type in self.alert_filters:
            if self.alert_filters[alert_type](alert):
                self.logger.debug(f"Alert suppressed by filter: {alert_type.value}")
                return alert

        self.alerts.append(alert)
        
        self.logger.log(
            logging.WARNING if level == AlertLevel.WARNING else logging.ERROR if level == AlertLevel.CRITICAL else logging.INFO,
            f"[{alert_type.value}] {message}"
        )

        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

        return alert

    def get_alerts(
        self,
        alert_type: Optional[AlertType] = None,
        level: Optional[AlertLevel] = None,
        acknowledged: bool = False
    ) -> List[Alert]:
        """Get alerts with optional filtering.
        
        Args:
            alert_type: Filter by type
            level: Filter by level
            acknowledged: Filter by acknowledgement status
            
        Returns:
            List of alerts
        """
        results = self.alerts

        if alert_type:
            results = [a for a in results if a.alert_type == alert_type]

        if level:
            results = [a for a in results if a.level == level]

        results = [a for a in results if a.acknowledged == acknowledged]

        return results

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if successful
        """
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                self.logger.info(f"Alert acknowledged: {alert_id}")
                return True

        return False


# ============================================================================
# Monitoring Dashboard
# ============================================================================

class MonitoringDashboard:
    """Aggregate monitoring dashboard."""

    def __init__(
        self,
        order_monitor: OrderStatusMonitor,
        book_watcher: OrderBookWatcher,
        portfolio_monitor: PortfolioMonitor,
        notifier: EventNotifier
    ):
        """Initialize monitoring dashboard.
        
        Args:
            order_monitor: OrderStatusMonitor instance
            book_watcher: OrderBookWatcher instance
            portfolio_monitor: PortfolioMonitor instance
            notifier: EventNotifier instance
        """
        self.logger = logging.getLogger("MonitoringDashboard")
        self.order_monitor = order_monitor
        self.book_watcher = book_watcher
        self.portfolio_monitor = portfolio_monitor
        self.notifier = notifier
        self.start_time = datetime.utcnow()
        self.state = MonitoringState.IDLE

    async def start(self, refresh_interval_seconds: float = 1.0) -> None:
        """Start monitoring loop.
        
        Args:
            refresh_interval_seconds: Update interval
        """
        self.state = MonitoringState.RUNNING
        self.logger.info("Starting monitoring dashboard")

        try:
            while self.state == MonitoringState.RUNNING:
                # Check order updates
                status_changes = await self.order_monitor.check_status_updates()
                for order, old_status, new_status in status_changes:
                    await self._handle_order_status_change(order, old_status, new_status)

                # Check book updates
                book_updates = await self.book_watcher.check_book_updates()
                for new_book, old_book in book_updates:
                    await self._handle_book_update(new_book, old_book)

                # Take portfolio snapshot
                await self.portfolio_monitor.take_snapshot()

                await asyncio.sleep(refresh_interval_seconds)

        except asyncio.CancelledError:
            self.logger.info("Monitoring dashboard cancelled")
        except Exception as e:
            self.logger.error(f"Dashboard error: {e}")
            raise

    def pause(self) -> None:
        """Pause monitoring."""
        if self.state == MonitoringState.RUNNING:
            self.state = MonitoringState.PAUSED
            self.logger.info("Monitoring paused")

    def resume(self) -> None:
        """Resume monitoring."""
        if self.state == MonitoringState.PAUSED:
            self.state = MonitoringState.RUNNING
            self.logger.info("Monitoring resumed")

    async def stop(self) -> None:
        """Stop monitoring."""
        self.state = MonitoringState.STOPPED
        self.logger.info("Monitoring stopped")

    async def _handle_order_status_change(
        self,
        order: Order,
        old_status: OrderStatus,
        new_status: OrderStatus
    ) -> None:
        """Handle order status change events.
        
        Args:
            order: Order object
            old_status: Previous status
            new_status: New status
        """
        if new_status == OrderStatus.FILLED:
            await self.notifier.emit_alert(
                AlertType.ORDER_FILLED,
                AlertLevel.INFO,
                f"Order {order.order_id} filled: {order.quantity.filled_quantity} @ ${order.price.average_fill_price}",
                order_id=order.order_id,
                data={
                    "filled_quantity": order.quantity.filled_quantity,
                    "average_price": order.price.average_fill_price,
                    "total_cost": order.total_cost
                }
            )

        elif new_status == OrderStatus.CANCELLED:
            await self.notifier.emit_alert(
                AlertType.ORDER_CANCELLED,
                AlertLevel.WARNING,
                f"Order {order.order_id} cancelled",
                order_id=order.order_id
            )

        elif new_status == OrderStatus.REJECTED:
            await self.notifier.emit_alert(
                AlertType.ORDER_REJECTED,
                AlertLevel.CRITICAL,
                f"Order {order.order_id} rejected",
                order_id=order.order_id
            )

    async def _handle_book_update(
        self,
        new_book: OrderBook,
        old_book: Optional[OrderBook]
    ) -> None:
        """Handle order book update events.
        
        Args:
            new_book: New order book
            old_book: Previous order book
        """
        # Check for price spike
        if self.book_watcher.detect_price_spike(new_book.symbol, new_book.exchange_type):
            await self.notifier.emit_alert(
                AlertType.PRICE_SPIKE,
                AlertLevel.WARNING,
                f"Price spike detected for {new_book.symbol}: {new_book.last_trade_price}",
                data={"symbol": new_book.symbol, "price": new_book.last_trade_price}
            )

        # Check liquidity
        if new_book.bid_ask_spread:
            threshold = 0.5  # 0.5% spread threshold
            spread_percent = (new_book.bid_ask_spread / new_book.last_trade_price * 100) if new_book.last_trade_price else 0
            
            if spread_percent > threshold:
                await self.notifier.emit_alert(
                    AlertType.LIQUIDITY_WARNING,
                    AlertLevel.WARNING,
                    f"Low liquidity on {new_book.symbol}: spread {spread_percent:.2f}%",
                    data={"symbol": new_book.symbol, "spread_percent": spread_percent}
                )

    def get_metrics(self) -> MonitoringMetrics:
        """Get aggregate monitoring metrics.
        
        Returns:
            MonitoringMetrics
        """
        monitored_orders = self.order_monitor.monitored_orders
        filled_orders = sum(
            1 for oid in monitored_orders
            if self.order_monitor.order_manager.orders.get(oid, Order()).status == OrderStatus.FILLED
        )
        cancelled_orders = sum(
            1 for oid in monitored_orders
            if self.order_monitor.order_manager.orders.get(oid, Order()).status == OrderStatus.CANCELLED
        )

        portfolio = self.portfolio_monitor.portfolio_manager
        open_positions = sum(1 for p in portfolio.position_manager.positions.values() if p.status == PositionStatus.OPEN)
        closed_positions = sum(1 for p in portfolio.position_manager.positions.values() if p.status == PositionStatus.CLOSED)

        # Calculate average fill times
        fill_times = []
        for oid in monitored_orders:
            fill_time = self.order_monitor.get_fill_time(oid)
            if fill_time:
                fill_times.append(fill_time.total_seconds())

        avg_fill_time = sum(fill_times) / len(fill_times) if fill_times else None

        critical_alerts = len(self.notifier.get_alerts(level=AlertLevel.CRITICAL))

        return MonitoringMetrics(
            monitoring_start=self.start_time,
            monitoring_duration=datetime.utcnow() - self.start_time,
            active_orders=len(monitored_orders),
            filled_orders=filled_orders,
            cancelled_orders=cancelled_orders,
            active_positions=open_positions,
            closed_positions=closed_positions,
            total_alerts=len(self.notifier.alerts),
            critical_alerts=critical_alerts,
            average_fill_time=avg_fill_time,
            average_position_duration=None
        )

    def print_dashboard(self) -> str:
        """Generate dashboard text output.
        
        Returns:
            Formatted dashboard string
        """
        metrics = self.get_metrics()
        latest_portfolio = self.portfolio_monitor.snapshots[-1] if self.portfolio_monitor.snapshots else None

        output = []
        output.append("\n" + "=" * 80)
        output.append("MONITORING DASHBOARD".center(80))
        output.append("=" * 80)

        # Status
        output.append(f"\nStatus: {self.state.value.upper()}")
        output.append(f"Monitoring Duration: {metrics.monitoring_duration}")

        # Orders
        output.append(f"\n--- ORDERS ---")
        output.append(f"Active Orders: {metrics.active_orders}")
        output.append(f"Filled: {metrics.filled_orders}")
        output.append(f"Cancelled: {metrics.cancelled_orders}")
        if metrics.average_fill_time:
            output.append(f"Avg Fill Time: {metrics.average_fill_time:.1f}s")

        # Positions
        output.append(f"\n--- POSITIONS ---")
        output.append(f"Open Positions: {metrics.active_positions}")
        output.append(f"Closed Positions: {metrics.closed_positions}")

        # Portfolio
        if latest_portfolio:
            output.append(f"\n--- PORTFOLIO ---")
            output.append(f"Total Value: ${latest_portfolio.total_value:,.2f}")
            output.append(f"Cash: ${latest_portfolio.cash_balance:,.2f}")
            output.append(f"Unrealized P&L: ${latest_portfolio.unrealized_pnl:+,.2f}")
            output.append(f"Realized P&L: ${latest_portfolio.realized_pnl:+,.2f}")
            output.append(f"Win Rate: {latest_portfolio.win_rate:.1f}%")

        # Alerts
        output.append(f"\n--- ALERTS ---")
        output.append(f"Total: {metrics.total_alerts}")
        output.append(f"Critical: {metrics.critical_alerts}")

        output.append("\n" + "=" * 80)

        return "\n".join(output)
