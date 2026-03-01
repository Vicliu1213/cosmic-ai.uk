# Phase 5 Stage 3 - Order Management System API Reference
訂單管理系統 API 參考

## Overview

Complete API documentation for the Order Management System (Phase 5 Stage 3) including order lifecycle management, execution, monitoring, settlement, and reporting.

### File Structure

```
src/phase5/
├── order_management.py        # Core order and position management
├── order_execution.py         # Order execution engine and book management
├── order_monitoring.py        # Real-time monitoring and alerts
└── trade_settlement.py        # Settlement, reporting, and compliance
```

---

## 1. Order Management Module (`order_management.py`)

### Data Classes

#### `OrderPrice`
Tracks price information for orders.

```python
@dataclass
class OrderPrice:
    limit_price: Optional[float] = None
    average_fill_price: float = 0.0
    highest_fill_price: float = 0.0
    lowest_fill_price: float = 0.0
```

#### `OrderQuantity`
Tracks quantity information for orders.

```python
@dataclass
class OrderQuantity:
    total_quantity: float
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    cancelled_quantity: float = 0.0
```

#### `Order`
Represents a single trading order with full lifecycle tracking.

```python
@dataclass
class Order:
    order_id: str
    exchange_type: ExchangeType
    order_type: OrderType
    side: OrderSide
    symbol: str
    price: OrderPrice
    quantity: OrderQuantity
    
    # Status tracking
    status: OrderStatus = OrderStatus.PENDING
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Fees and costs
    fee_amount: float = 0.0
    total_cost: float = 0.0
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Key Properties:**
- `is_filled`: Returns True if order is completely filled
- `is_partially_filled`: Returns True if partially filled
- `fill_percentage`: Returns fill percentage (0-100)

#### `Position`
Represents an open or closed trading position.

```python
@dataclass
class Position:
    position_id: str
    exchange_type: ExchangeType
    symbol: str
    side: OrderSide
    entry_price: float
    entry_quantity: float
    current_quantity: float
    current_price: float
    
    # Status tracking
    status: PositionStatus = PositionStatus.OPENING
    opened_at: datetime = field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    
    # Risk management
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    
    # Order tracking
    entry_orders: List[str] = field(default_factory=list)
    exit_orders: List[str] = field(default_factory=list)
    
    # Fees and metadata
    entry_fees: float = 0.0
    exit_fees: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Key Methods:**
- `get_unrealized_pnl()` → float: Calculate unrealized profit/loss
- `get_unrealized_roi()` → float: Calculate unrealized return on investment
- `hit_stop_loss()` → bool: Check if stop loss triggered
- `hit_take_profit()` → bool: Check if take profit triggered

#### `Trade`
Represents a completed trade with full P&L calculation.

```python
@dataclass
class Trade:
    position_id: str
    exchange_type: ExchangeType
    symbol: str
    side: OrderSide
    entry_price: float
    entry_quantity: float
    entry_time: datetime
    entry_fees: float
    exit_price: float
    exit_quantity: float
    exit_time: datetime
    exit_fees: float
    
    # P&L tracking
    realized_pnl: float = 0.0
    roi_percent: float = 0.0
    hold_time: Optional[timedelta] = None
```

---

### OrderManager Class

Manages order lifecycle from creation to settlement.

#### Methods

##### `async def create_order(...) -> Order`

Create a new order.

```python
async def create_order(
    self,
    exchange_type: ExchangeType,
    order_type: OrderType,
    side: OrderSide,
    symbol: str,
    quantity: float,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    take_profit_price: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Order
```

**Parameters:**
- `exchange_type`: BINANCE, COINBASE, etc.
- `order_type`: MARKET, LIMIT, STOP_LOSS, TAKE_PROFIT, TRAILING_STOP
- `side`: BUY or SELL
- `symbol`: Trading pair (e.g., "BTC/USDT")
- `quantity`: Amount to trade
- `limit_price`: Price limit (for LIMIT orders)
- `stop_price`: Stop trigger price
- `take_profit_price`: Take profit trigger
- `metadata`: Custom metadata dictionary

**Returns:** Order object with status PENDING

##### `async def submit_order(order: Order) -> bool`

Submit order to exchange.

```python
async def submit_order(self, order: Order) -> bool
```

**Status Change:** PENDING → OPEN

**Returns:** True if successful

##### `async def fill_order(...) -> bool`

Fill order completely or partially.

```python
async def fill_order(
    self,
    order_id: str,
    filled_quantity: float,
    fill_price: float,
    partial: bool = False,
    fee_amount: float = 0.0
) -> bool
```

**Parameters:**
- `order_id`: Order to fill
- `filled_quantity`: Quantity filled
- `fill_price`: Price at which filled
- `partial`: If True, allows partial fill
- `fee_amount`: Trading fees

**Status Changes:**
- If completely filled: OPEN → FILLED
- If partially filled: OPEN → PARTIALLY_FILLED (if `partial=True`)

**Returns:** True if successful

##### `async def cancel_order(order_id: str) -> bool`

Cancel an open order.

```python
async def cancel_order(self, order_id: str) -> bool
```

**Status Changes:**
- OPEN or PARTIALLY_FILLED → CANCELLED

**Returns:** True if successful

##### `def get_order(order_id: str) -> Optional[Order]`

Retrieve order by ID.

```python
def get_order(self, order_id: str) -> Optional[Order]
```

**Returns:** Order object or None if not found

##### `def get_orders_by_symbol(symbol: str) -> List[Order]`

Get all orders for a symbol.

```python
def get_orders_by_symbol(self, symbol: str) -> List[Order]
```

**Returns:** List of Order objects

##### `def get_orders_by_status(status: OrderStatus) -> List[Order]`

Get all orders with specific status.

```python
def get_orders_by_status(self, status: OrderStatus) -> List[Order]
```

**Returns:** List of Order objects

---

### PositionManager Class

Manages trading positions and tracks P&L.

#### Methods

##### `async def open_position(...) -> Position`

Open a new position.

```python
async def open_position(
    self,
    exchange_type: ExchangeType,
    symbol: str,
    side: OrderSide,
    entry_price: float,
    quantity: float,
    stop_loss_price: Optional[float] = None,
    take_profit_price: Optional[float] = None,
    entry_orders: List[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Position
```

**Parameters:**
- `exchange_type`: Exchange where position is opened
- `symbol`: Trading pair
- `side`: BUY or SELL
- `entry_price`: Entry price
- `quantity`: Position size
- `stop_loss_price`: Optional stop loss level
- `take_profit_price`: Optional take profit level
- `entry_orders`: List of order IDs that opened position
- `metadata`: Custom metadata

**Returns:** Position with status OPENING

##### `async def update_position_price(position_id: str, current_price: float) -> Optional[Position]`

Update position with current market price.

```python
async def update_position_price(
    self,
    position_id: str,
    current_price: float
) -> Optional[Position]
```

**Updates:**
- Current price
- Checks for stop loss/take profit triggers
- Logs warnings if triggered

**Returns:** Updated Position or None if not found

##### `async def reduce_position(position_id: str, quantity: float, exit_price: float) -> bool`

Reduce or completely close a position.

```python
async def reduce_position(
    self,
    position_id: str,
    quantity: float,
    exit_price: float
) -> bool
```

**Parameters:**
- `position_id`: Position to reduce
- `quantity`: Amount to close
- `exit_price`: Exit price

**Behavior:**
- If quantity < position size: Position becomes PARTIALLY_CLOSED
- If quantity == position size: Position becomes CLOSED, Trade record created
- If quantity > position size: Returns False

**Returns:** True if successful

**Side Effect:** Creates Trade record if position is completely closed

##### `def get_position(position_id: str) -> Optional[Position]`

Retrieve position by ID.

```python
def get_position(self, position_id: str) -> Optional[Position]
```

**Returns:** Position or None if not found

##### `def get_positions_by_symbol(symbol: str) -> List[Position]`

Get all open positions for a symbol.

```python
def get_positions_by_symbol(self, symbol: str) -> List[Position]
```

**Returns:** List of open Position objects

##### `def get_open_positions() -> List[Position]`

Get all open positions.

```python
def get_open_positions(self) -> List[Position]
```

**Returns:** List of all positions with status OPEN

##### `def get_closed_positions() -> List[Position]`

Get all closed positions.

```python
def get_closed_positions(self) -> List[Position]
```

**Returns:** List of closed Position objects

---

### PortfolioManager Class

Manages aggregated portfolio metrics and valuation.

#### Constructor

```python
def __init__(self, initial_capital: float)
```

**Parameters:**
- `initial_capital`: Starting portfolio capital

#### Methods

##### `def get_portfolio_value() -> float`

Calculate total portfolio value.

```python
def get_portfolio_value(self) -> float
```

**Calculation:** initial_capital + sum(unrealized_pnl) + sum(realized_pnl)

**Returns:** Total portfolio value in USD

##### `def get_portfolio_stats() -> Dict[str, float]`

Get portfolio statistics.

```python
def get_portfolio_stats(self) -> Dict[str, float]
```

**Returns:**
```python
{
    "total_capital": float,
    "initial_capital": float,
    "unrealized_pnl": float,
    "realized_pnl": float,
    "portfolio_value": float,
    "roi_percent": float,
    "num_open_positions": int,
    "num_closed_positions": int
}
```

##### `def get_symbol_exposure(symbol: str) -> float`

Get total exposure to a symbol.

```python
def get_symbol_exposure(self, symbol: str) -> float
```

**Returns:** Sum of all position values for symbol

##### `def get_largest_positions(limit: int = 10) -> List[Tuple[Position, float]]`

Get largest positions by value.

```python
def get_largest_positions(self, limit: int = 10) -> List[Tuple[Position, float]]
```

**Returns:** List of (Position, value) tuples sorted by value

---

## 2. Order Execution Module (`order_execution.py`)

### Data Classes

#### `ExecutionResult`
Represents the result of an order execution attempt.

```python
@dataclass
class ExecutionResult:
    executed: bool
    status: ExecutionStatus
    message: str
    order_id: str
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    slippage: float = 0.0
    fee_amount: float = 0.0
```

---

### OrderBookManager Class

Manages order book data for symbols.

#### Methods

##### `async def update_order_book(...) -> None`

Update order book for a symbol.

```python
async def update_order_book(
    self,
    symbol: str,
    exchange_type: ExchangeType,
    bids: List[Tuple[float, float]],
    asks: List[Tuple[float, float]],
    last_trade_price: float,
    timestamp: Optional[datetime] = None
) -> None
```

**Parameters:**
- `symbol`: Trading pair
- `exchange_type`: Exchange
- `bids`: List of (price, quantity) tuples
- `asks`: List of (price, quantity) tuples
- `last_trade_price`: Most recent trade price
- `timestamp`: Book timestamp

##### `def get_order_book(symbol: str) -> Optional[OrderBook]`

Retrieve order book for symbol.

```python
def get_order_book(self, symbol: str) -> Optional[OrderBook]
```

**Returns:** OrderBook object or None

##### `def get_best_bid(symbol: str) -> Optional[float]`

Get best bid price.

```python
def get_best_bid(self, symbol: str) -> Optional[float]
```

**Returns:** Highest bid price or None

##### `def get_best_ask(symbol: str) -> Optional[float]`

Get best ask price.

```python
def get_best_ask(self, symbol: str) -> Optional[float]
```

**Returns:** Lowest ask price or None

##### `def get_spread(symbol: str) -> Optional[float]`

Calculate bid-ask spread.

```python
def get_spread(self, symbol: str) -> Optional[float]
```

**Returns:** ask - bid or None

---

### OrderExecutionEngine Class

Executes orders based on market conditions.

#### Constructor

```python
def __init__(
    self,
    mode: ExecutionMode = ExecutionMode.BACKTEST,
    slippage_percent: float = 0.05,
    fee_percent: float = 0.1
)
```

**Parameters:**
- `mode`: BACKTEST or LIVE
- `slippage_percent`: Default slippage percentage
- `fee_percent`: Default trading fee percentage

#### Methods

##### `async def execute_market_order(order: Order) -> ExecutionResult`

Execute a market order.

```python
async def execute_market_order(
    self,
    order: Order,
    slippage_percent: Optional[float] = None
) -> ExecutionResult
```

**Execution:**
- Buys at best ask
- Sells at best bid
- Applies slippage
- Calculates fees

**Returns:** ExecutionResult with execution details

##### `async def execute_limit_order(order: Order, order_book_check: bool = True) -> ExecutionResult`

Execute a limit order.

```python
async def execute_limit_order(
    self,
    order: Order,
    order_book_check: bool = True
) -> ExecutionResult
```

**Execution:**
- Checks if limit price is crossed
- If crossed, fills at limit price
- If not crossed, remains pending

**Returns:** ExecutionResult

##### `async def execute_stop_loss_order(order: Order) -> ExecutionResult`

Execute a stop loss order.

```python
async def execute_stop_loss_order(self, order: Order) -> ExecutionResult
```

**Execution:**
- Waits for price to hit stop level
- Converts to market order
- Executes immediately

**Returns:** ExecutionResult

##### `async def execute_take_profit_order(order: Order) -> ExecutionResult`

Execute a take profit order.

```python
async def execute_take_profit_order(self, order: Order) -> ExecutionResult
```

**Execution:**
- Waits for price to hit take profit level
- Converts to market order
- Executes immediately

**Returns:** ExecutionResult

---

## 3. Order Monitoring Module (`order_monitoring.py`)

### Data Classes

#### `Alert`
Alert for important order/portfolio events.

```python
@dataclass
class Alert:
    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    message: str
    symbol: Optional[str] = None
    value: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
```

---

### OrderStatusMonitor Class

Monitors order status changes and triggers callbacks.

#### Methods

##### `async def monitor_order(order_id: str) -> None`

Start monitoring an order.

```python
async def monitor_order(self, order_id: str) -> None
```

##### `async def stop_monitoring_order(order_id: str) -> None`

Stop monitoring an order.

```python
async def stop_monitoring_order(self, order_id: str) -> None
```

##### `async def check_status_updates() -> List[Tuple[Order, OrderStatus, OrderStatus]]`

Check all monitored orders for status changes.

```python
async def check_status_updates(self) -> List[Tuple[Order, OrderStatus, OrderStatus]]
```

**Returns:** List of (order, old_status, new_status) for changed orders

##### `def register_status_callback(callback: Callable) -> None`

Register callback for status changes.

```python
def register_status_callback(
    self,
    callback: Callable[[Order, OrderStatus, OrderStatus], None]
) -> None
```

**Callback Signature:** `callback(order, old_status, new_status)`

---

### PortfolioMonitor Class

Real-time portfolio monitoring and snapshots.

#### Methods

##### `async def take_snapshot() -> PortfolioSnapshot`

Take portfolio snapshot.

```python
async def take_snapshot(self) -> PortfolioSnapshot
```

**Returns:**
```python
PortfolioSnapshot(
    portfolio_value: float,
    unrealized_pnl: float,
    realized_pnl: float,
    open_positions: int,
    total_trades: int,
    timestamp: datetime
)
```

##### `def get_portfolio_history(lookback_minutes: int = 60) -> List[PortfolioSnapshot]`

Get portfolio snapshot history.

```python
def get_portfolio_history(self, lookback_minutes: int = 60) -> List[PortfolioSnapshot]
```

**Returns:** List of snapshots in time range

---

### EventNotifier Class

Manages alerts and notifications.

#### Methods

##### `async def emit_alert(...) -> Alert`

Emit an alert.

```python
async def emit_alert(
    self,
    alert_type: AlertType,
    level: AlertLevel,
    message: str,
    symbol: Optional[str] = None,
    value: Optional[float] = None
) -> Alert
```

**Returns:** Alert object

##### `def register_alert_callback(callback: Callable) -> None`

Register alert callback.

```python
def register_alert_callback(self, callback: Callable[[Alert], None]) -> None
```

**Callback Signature:** `callback(alert)`

##### `async def acknowledge_alert(alert_id: str, acknowledged_by: str) -> bool`

Acknowledge alert.

```python
async def acknowledge_alert(
    self,
    alert_id: str,
    acknowledged_by: str
) -> bool
```

**Returns:** True if successful

##### `def get_unacknowledged_alerts() -> List[Alert]`

Get all unacknowledged alerts.

```python
def get_unacknowledged_alerts(self) -> List[Alert]
```

**Returns:** List of Alert objects

---

## 4. Trade Settlement Module (`trade_settlement.py`)

### Data Classes

#### `TradeSettlement`
Settlement record for a completed trade.

```python
@dataclass
class TradeSettlement:
    settlement_id: str
    trade: Trade
    status: SettlementStatus
    settlement_time: Optional[datetime] = None
    cleared_at: Optional[datetime] = None
    total_fees: float = 0.0
```

#### `PerformanceMetrics`
Aggregated performance metrics.

```python
@dataclass
class PerformanceMetrics:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_profit: float
    total_loss: float
    average_win: float
    average_loss: float
    risk_reward_ratio: float
    sharpe_ratio: float
    max_drawdown_percent: float
    recovery_factor: float
    total_return: float
    annualized_return: float
    period_start: datetime
    period_end: datetime
```

---

### TradeSettlementEngine Class

Handles trade settlement and confirmation.

#### Methods

##### `async def settle_trade(trade: Trade, fee_amount: float = 0.0) -> TradeSettlement`

Settle a completed trade.

```python
async def settle_trade(
    self,
    trade: Trade,
    fee_amount: float = 0.0
) -> TradeSettlement
```

**Returns:** TradeSettlement object

##### `async def confirm_settlement(settlement_id: str) -> bool`

Confirm settlement.

```python
async def confirm_settlement(self, settlement_id: str) -> bool
```

**Status Change:** PENDING → CONFIRMED

**Returns:** True if successful

---

### PerformanceReporter Class

Calculates comprehensive performance metrics.

#### Methods

##### `async def calculate_metrics(...) -> PerformanceMetrics`

Calculate performance metrics from trades.

```python
async def calculate_metrics(
    self,
    trades: List[Trade],
    initial_capital: float,
    current_capital: float,
    risk_free_rate: float = 0.02
) -> PerformanceMetrics
```

**Parameters:**
- `trades`: List of completed trades
- `initial_capital`: Starting capital
- `current_capital`: Current portfolio value
- `risk_free_rate`: Risk-free rate for Sharpe ratio

**Calculations Include:**
- Win rate: (winning_trades / total_trades) * 100
- Profit factor: total_profit / total_loss
- Average win/loss
- Risk-reward ratio: average_win / average_loss
- Sharpe ratio: excess return / volatility
- Max drawdown: maximum peak-to-trough decline
- Recovery factor: total_profit / max_drawdown

**Returns:** PerformanceMetrics object

---

### TradeAnalytics Class

Trade classification and analysis.

#### Methods

##### `def get_symbol_statistics(trades: List[Trade]) -> Dict[str, Dict[str, Any]]`

Get statistics by symbol.

```python
def get_symbol_statistics(
    self,
    trades: List[Trade]
) -> Dict[str, Dict[str, Any]]
```

**Returns:**
```python
{
    "BTC/USDT": {
        "total_trades": int,
        "winning_trades": int,
        "win_rate": float,
        "total_pnl": float,
        "avg_hold_time": timedelta
    },
    ...
}
```

##### `def get_drawdown_analysis(trades: List[Trade]) -> Dict[str, Any]`

Analyze drawdowns.

```python
def get_drawdown_analysis(
    self,
    trades: List[Trade]
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "max_drawdown": float,
    "max_drawdown_percent": float,
    "drawdown_trades": List[Trade],
    "recovery_trades": int
}
```

---

### ReportExporter Class

Export reports in multiple formats.

#### Methods

##### `async def export_trades(trades: List[Trade], format: ReportFormat) -> str`

Export trades to file format.

```python
async def export_trades(
    self,
    trades: List[Trade],
    format: ReportFormat
) -> str
```

**Formats:**
- ReportFormat.CSV: Comma-separated values
- ReportFormat.JSON: JSON format
- ReportFormat.TEXT: Human-readable text

**Returns:** Formatted report string

##### `async def export_metrics(metrics: PerformanceMetrics, format: ReportFormat) -> str`

Export performance metrics.

```python
async def export_metrics(
    self,
    metrics: PerformanceMetrics,
    format: ReportFormat
) -> str
```

**Returns:** Formatted metrics string

---

## Enumerations

### OrderStatus
```python
class OrderStatus(Enum):
    PENDING = "pending"          # Created but not submitted
    OPEN = "open"                # Submitted to exchange
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"            # Completely filled
    CANCELLED = "cancelled"      # Cancelled by user or exchange
    REJECTED = "rejected"        # Rejected by exchange
    EXPIRED = "expired"          # Expired without fill
```

### OrderType
```python
class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
```

### OrderSide
```python
class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"
```

### PositionStatus
```python
class PositionStatus(Enum):
    OPENING = "opening"
    OPEN = "open"
    PARTIALLY_CLOSED = "partially_closed"
    CLOSED = "closed"
```

### AlertLevel
```python
class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

### AlertType
```python
class AlertType(Enum):
    ORDER_CREATED = "order_created"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    STOP_LOSS_HIT = "stop_loss_hit"
    TAKE_PROFIT_HIT = "take_profit_hit"
    HIGH_SPREAD = "high_spread"
    LARGE_PRICE_SPIKE = "large_price_spike"
    PORTFOLIO_ALERT = "portfolio_alert"
```

---

## Usage Examples

### Complete Order Lifecycle

```python
# Create manager
order_mgr = OrderManager()
position_mgr = PositionManager()

# Create order
order = await order_mgr.create_order(
    exchange_type=ExchangeType.BINANCE,
    order_type=OrderType.LIMIT,
    side=OrderSide.BUY,
    symbol="BTC/USDT",
    quantity=1.0,
    limit_price=50000.0
)

# Submit order
await order_mgr.submit_order(order)

# Simulate fill
await order_mgr.fill_order(
    order_id=order.order_id,
    filled_quantity=1.0,
    fill_price=49950.0
)

# Open position
position = await position_mgr.open_position(
    exchange_type=ExchangeType.BINANCE,
    symbol="BTC/USDT",
    side=OrderSide.BUY,
    entry_price=49950.0,
    quantity=1.0,
    stop_loss_price=49000.0,
    take_profit_price=51000.0
)

# Monitor price
position.current_price = 51000.0
print(f"Unrealized P&L: ${position.get_unrealized_pnl()}")

# Close position
await position_mgr.reduce_position(
    position_id=position.position_id,
    quantity=1.0,
    exit_price=51000.0
)

# Settlement
settlement_engine = TradeSettlementEngine()
trade = position_mgr.trades[-1]
settlement = await settlement_engine.settle_trade(trade, fee_amount=10.0)
```

### Portfolio Monitoring

```python
portfolio_mgr = PortfolioManager(initial_capital=10000.0)
portfolio_monitor = PortfolioMonitor(portfolio_mgr)
notifier = EventNotifier()

# Register alert callback
def on_alert(alert):
    print(f"Alert: {alert.message}")

notifier.register_alert_callback(on_alert)

# Take snapshot
snapshot = await portfolio_monitor.take_snapshot()
print(f"Portfolio Value: ${snapshot.portfolio_value}")

# Get history
history = portfolio_monitor.get_portfolio_history(lookback_minutes=60)
print(f"Snapshots: {len(history)}")
```

### Performance Reporting

```python
reporter = PerformanceReporter()
exporter = ReportExporter()

# Calculate metrics
metrics = await reporter.calculate_metrics(
    trades=trades,
    initial_capital=10000.0,
    current_capital=10500.0
)

print(f"Win Rate: {metrics.win_rate:.2f}%")
print(f"Profit Factor: {metrics.profit_factor:.2f}")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")

# Export report
csv_report = await exporter.export_trades(trades, ReportFormat.CSV)
metrics_report = await exporter.export_metrics(metrics, ReportFormat.TEXT)
```

---

## Quality Standards

- **Type Hints**: 100% type coverage
- **Documentation**: All classes and methods fully documented
- **Error Handling**: Comprehensive error handling with logging
- **Async/Await**: Full async support for all I/O operations
- **Testing**: Complete unit and integration test coverage

---

## Best Practices Guide

### 1. Order Submission Best Practices

```python
# ✓ GOOD: Comprehensive error handling with retry logic
async def submit_order_safely(order_mgr, order, max_retries=3):
    """Submit order with comprehensive error handling"""
    
    for attempt in range(max_retries):
        try:
            # Validate order before submission
            if order.quantity.total_quantity <= 0:
                raise ValueError("Invalid quantity")
            
            if order.price.limit_price and order.price.limit_price <= 0:
                raise ValueError("Invalid limit price")
            
            # Submit order
            success = await order_mgr.submit_order(order)
            
            if success:
                logger.info(f"Order {order.order_id} submitted successfully")
                return True
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return False  # Don't retry validation errors
        
        except ConnectionError as e:
            logger.warning(f"Connection error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    
    logger.error(f"Failed to submit order after {max_retries} attempts")
    return False

# ✗ BAD: No error handling
async def submit_order_poorly(order_mgr, order):
    """Don't do this - no error handling"""
    await order_mgr.submit_order(order)  # Might crash silently
```

### 2. Position Risk Management

```python
# ✓ GOOD: Proper risk limits and checks
async def open_position_with_risk_management(position_mgr, portfolio_mgr, 
                                             symbol, entry_price, quantity):
    """Open position with comprehensive risk checks"""
    
    # Check 1: Portfolio risk exposure
    portfolio_value = portfolio_mgr.get_portfolio_value()
    position_value = entry_price * quantity
    max_position_risk = portfolio_value * 0.05  # Max 5% risk per position
    
    if position_value > max_position_risk:
        logger.warning(f"Position value {position_value} exceeds risk limit {max_position_risk}")
        return None
    
    # Check 2: Symbol concentration
    current_symbol_exposure = portfolio_mgr.get_symbol_exposure(symbol)
    max_symbol_exposure = portfolio_value * 0.30  # Max 30% per symbol
    
    if current_symbol_exposure + position_value > max_symbol_exposure:
        logger.warning(f"Symbol exposure would exceed limit for {symbol}")
        return None
    
    # Check 3: Calculate appropriate stop loss based on volatility
    volatility_adjustment = 0.02  # 2% stop loss
    stop_loss_price = entry_price * (1 - volatility_adjustment)
    
    # Open position with safety parameters
    position = await position_mgr.open_position(
        exchange_type=ExchangeType.BINANCE,
        symbol=symbol,
        side=OrderSide.BUY,
        entry_price=entry_price,
        quantity=quantity,
        stop_loss_price=stop_loss_price,
        take_profit_price=entry_price * 1.05  # 5% profit target
    )
    
    logger.info(f"Position opened with safety checks: {position.position_id}")
    return position

# ✗ BAD: No risk management
async def open_position_risky(position_mgr, symbol, entry_price, quantity):
    """Don't do this - ignores risk limits"""
    position = await position_mgr.open_position(
        exchange_type=ExchangeType.BINANCE,
        symbol=symbol,
        side=OrderSide.BUY,
        entry_price=entry_price,
        quantity=quantity
    )
    return position
```

### 3. Monitoring Best Practices

```python
# ✓ GOOD: Structured monitoring with callbacks
async def setup_monitoring_system(order_mgr, position_mgr, portfolio_mgr):
    """Setup comprehensive monitoring system"""
    
    # Create monitors
    order_monitor = OrderStatusMonitor(order_mgr)
    portfolio_monitor = PortfolioMonitor(portfolio_mgr)
    notifier = EventNotifier()
    
    # Define alert callbacks
    async def on_order_filled(alert):
        logger.info(f"Order filled: {alert.message}")
        # Trigger automated actions
        if alert.alert_type == AlertType.ORDER_FILLED:
            # Open position if needed
            pass
    
    async def on_critical_alert(alert):
        if alert.level == AlertLevel.CRITICAL:
            logger.critical(f"CRITICAL ALERT: {alert.message}")
            # Take immediate action
            # Send notifications
            # Execute emergency procedures
    
    # Register callbacks
    notifier.register_alert_callback(on_order_filled)
    notifier.register_alert_callback(on_critical_alert)
    
    # Start continuous monitoring
    while True:
        try:
            # Check order status changes
            changes = await order_monitor.check_status_updates()
            for order, old_status, new_status in changes:
                print(f"Order status: {old_status.value} → {new_status.value}")
            
            # Get portfolio snapshot
            snapshot = await portfolio_monitor.take_snapshot()
            print(f"Portfolio: ${snapshot.portfolio_value:.2f}")
            
            await asyncio.sleep(1)
        
        except Exception as e:
            logger.exception(f"Monitoring error: {e}")
            await asyncio.sleep(1)

# ✗ BAD: Polling without structure
async def monitor_poorly(order_mgr):
    """Don't do this - inefficient and error-prone"""
    while True:
        for order in order_mgr.orders:
            print(order.status)
        await asyncio.sleep(0.1)
```

### 4. Reporting and Compliance

```python
# ✓ GOOD: Comprehensive reporting with compliance
async def generate_compliant_reports(position_mgr, reporter, exporter):
    """Generate reports meeting compliance requirements"""
    
    # Calculate comprehensive metrics
    metrics = await reporter.calculate_metrics(
        trades=position_mgr.trades,
        initial_capital=10000.0,
        current_capital=10500.0
    )
    
    # Generate multiple report formats for different audiences
    
    # 1. Executive Summary (TEXT)
    exec_report = await exporter.export_metrics(
        metrics=metrics,
        format=ReportFormat.TEXT
    )
    print("=" * 50)
    print("EXECUTIVE SUMMARY")
    print("=" * 50)
    print(exec_report)
    
    # 2. Detailed Analytics (JSON for systems)
    analytics = TradeAnalytics()
    symbol_stats = analytics.get_symbol_statistics(position_mgr.trades)
    drawdown_analysis = analytics.get_drawdown_analysis(position_mgr.trades)
    
    json_report = json.dumps({
        "metrics": metrics.__dict__,
        "symbol_stats": symbol_stats,
        "drawdown_analysis": drawdown_analysis,
        "timestamp": datetime.now().isoformat()
    }, indent=2)
    
    # 3. Trade-by-trade export (CSV for auditing)
    csv_report = await exporter.export_trades(
        trades=position_mgr.trades,
        format=ReportFormat.CSV
    )
    
    # Save reports
    with open("report_executive.txt", "w") as f:
        f.write(exec_report)
    
    with open("report_analytics.json", "w") as f:
        f.write(json_report)
    
    with open("report_trades.csv", "w") as f:
        f.write(csv_report)
    
    logger.info("Reports generated successfully")
    return {
        "executive": exec_report,
        "analytics": json_report,
        "trades": csv_report
    }

# ✗ BAD: Minimal reporting
async def report_poorly(position_mgr):
    """Don't do this - insufficient for compliance"""
    print(f"Total trades: {len(position_mgr.trades)}")
    print(f"Total P&L: ${sum(t.realized_pnl for t in position_mgr.trades)}")
```

---

## Common Patterns & Recipes

### Pattern 1: DCA (Dollar-Cost Averaging) Orders

```python
async def create_dca_orders(order_mgr, symbol: str, total_amount: float, 
                            num_orders: int, interval_minutes: int):
    """Create dollar-cost averaging orders"""
    
    amount_per_order = total_amount / num_orders
    orders = []
    
    for i in range(num_orders):
        order = await order_mgr.create_order(
            exchange_type=ExchangeType.BINANCE,
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            symbol=symbol,
            quantity=amount_per_order / 50000  # Current price estimate
        )
        orders.append(order)
        
        # Submit after interval
        if i > 0:
            await asyncio.sleep(interval_minutes * 60)
    
    return orders
```

### Pattern 2: Trailing Stop Orders

```python
async def monitor_trailing_stop(position_mgr, position_id: str, 
                               trail_percent: float = 2.0):
    """Monitor and update trailing stop loss"""
    
    position = position_mgr.positions.get(position_id)
    if not position:
        return
    
    highest_price = position.current_price
    
    while position.status == PositionStatus.OPEN:
        position.current_price = get_current_price(position.symbol)
        
        # Update highest price
        if position.current_price > highest_price:
            highest_price = position.current_price
        
        # Update stop loss
        new_stop_loss = highest_price * (1 - trail_percent / 100)
        if new_stop_loss > position.stop_loss_price:
            position.stop_loss_price = new_stop_loss
        
        # Check if hit
        if position.hit_stop_loss():
            logger.info(f"Trailing stop hit at {position.current_price}")
            break
        
        await asyncio.sleep(1)
```

### Pattern 3: Portfolio Rebalancing

```python
async def rebalance_portfolio(position_mgr, portfolio_mgr, target_allocations: Dict[str, float]):
    """Rebalance portfolio to target allocations"""
    
    portfolio_value = portfolio_mgr.get_portfolio_value()
    
    for symbol, target_percent in target_allocations.items():
        target_value = portfolio_value * (target_percent / 100)
        current_value = portfolio_mgr.get_symbol_exposure(symbol)
        
        diff_value = target_value - current_value
        
        if diff_value > 100:  # Need to buy
            quantity = diff_value / get_current_price(symbol)
            order = await position_mgr.open_position(
                symbol=symbol,
                side=OrderSide.BUY,
                entry_price=get_current_price(symbol),
                quantity=quantity
            )
            logger.info(f"Bought {quantity} of {symbol}")
        
        elif diff_value < -100:  # Need to sell
            quantity = abs(diff_value) / get_current_price(symbol)
            await position_mgr.reduce_position(
                position_id=find_position_id(symbol),
                quantity=quantity,
                exit_price=get_current_price(symbol)
            )
            logger.info(f"Sold {quantity} of {symbol}")
```

---

## Related Documentation

- [Architecture Guide](PHASE5_STAGE3_ARCHITECTURE.md)
- [Quick Start Guide](PHASE5_STAGE3_QUICK_START.md)
- [Phase 5 Overview](PHASE5_OVERVIEW.md)
