# Phase 5 Stage 3 - Order Management System Architecture
訂單管理系統架構設計

## System Overview

The Order Management System (Phase 5 Stage 3) is a comprehensive trading infrastructure that manages the complete lifecycle of trading orders, from creation through settlement.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORDER MANAGEMENT SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ ORDER MANAGER  │  │ POSITION MGMT  │  │ PORTFOLIO MGMT   │  │
│  ├────────────────┤  ├────────────────┤  ├──────────────────┤  │
│  │ Order Creation │  │ Position Open  │  │ Capital Tracking │  │
│  │ Submission     │  │ Position Close │  │ P&L Aggregation  │  │
│  │ Fill Tracking  │  │ P&L Calculation│  │ Exposure Calc    │  │
│  │ Cancellation   │  │ Risk Mgmt      │  │ Stats Generation │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│         │                    │                     │             │
└─────────┼────────────────────┼─────────────────────┼─────────────┘
          │                    │                     │
          ├────────────────────┴─────────────────────┤
          │   Data Layer (Orders, Positions, Trades)│
          └────────────────────┬─────────────────────┘
                               │
┌──────────────────────────────────────────────────────────────────┐
│              EXECUTION & MONITORING LAYER                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐  │
│  │ EXECUTION ENGINE    │  │ MONITORING & ALERTS              │  │
│  ├─────────────────────┤  ├──────────────────────────────────┤  │
│  │ Market Orders       │  │ Order Status Monitoring          │  │
│  │ Limit Orders        │  │ Order Book Watching              │  │
│  │ Stop Loss/TP        │  │ Portfolio Snapshots              │  │
│  │ Order Book Mgmt     │  │ Alert Generation & Callbacks     │  │
│  │ Slippage Calc       │  │ Trend Analysis                   │  │
│  └─────────────────────┘  └──────────────────────────────────┘  │
│         │                              │                         │
└─────────┼──────────────────────────────┼─────────────────────────┘
          │                              │
          ├──────────────────────────────┤
          │   Settlement & Reporting     │
          └──────────────────────────────┘
                     │
┌────────────────────────────────────────────────────────────────┐
│          SETTLEMENT & REPORTING LAYER                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ SETTLEMENT       │  │ REPORTING        │                   │
│  ├──────────────────┤  ├──────────────────┤                   │
│  │ Trade Confirm    │  │ Metrics Calc     │                   │
│  │ Settlement Log   │  │ Analytics        │                   │
│  │ Compliance Track │  │ Export Reports   │                   │
│  │ P&L Finalization │  │ Compliance Docs  │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Module Organization

### 1. Core Management Layer

#### `order_management.py` (840 lines)
Core order and position management with lifecycle tracking.

**Components:**
- **OrderManager**: Manages order creation, submission, filling, cancellation
- **PositionManager**: Manages position opening, closing, price updates
- **PortfolioManager**: Aggregates portfolio metrics and valuations
- **Data Classes**: Order, Position, Trade with complete type hints

**Key Responsibilities:**
- Order state transitions (PENDING → OPEN → FILLED → CLOSED)
- Position P&L tracking (unrealized and realized)
- Risk management (stop loss, take profit)
- Portfolio valuation and statistics

**Dependencies:**
- ExchangeType from exchange_connector
- Standard library (dataclasses, datetime, logging, typing)

---

### 2. Execution Layer

#### `order_execution.py` (700 lines)
Order execution engine with order book management.

**Components:**
- **OrderBookManager**: Maintains order book state for all symbols
- **OrderExecutionEngine**: Executes orders with different strategies
- **ExecutionResult**: Tracks execution outcomes and metrics

**Execution Modes:**
- **BACKTEST**: Simulated execution for backtesting
- **LIVE**: Real exchange execution (future)

**Order Execution Strategies:**
- **Market Orders**: Immediate execution at best available price
- **Limit Orders**: Execution only if price crosses limit
- **Stop Loss Orders**: Triggered at stop price, then market execute
- **Take Profit Orders**: Similar to stop loss but for profits
- **Trailing Stop**: Dynamic stop that follows price

**Slippage & Fees:**
- Configurable slippage percentage (default: 0.05%)
- Configurable fee percentage (default: 0.1%)
- Tracked per execution

**Dependencies:**
- OrderManager from order_management
- Order book data structures
- Standard library

---

### 3. Monitoring & Alerts Layer

#### `order_monitoring.py` (932 lines)
Real-time monitoring system with alert generation.

**Components:**
- **OrderStatusMonitor**: Tracks order status changes
- **OrderBookWatcher**: Monitors order book dynamics
- **PortfolioMonitor**: Tracks portfolio snapshots
- **EventNotifier**: Manages alert creation and distribution
- **MonitoringDashboard**: Integrated monitoring and reporting

**Monitoring Capabilities:**
- Order fill time tracking
- Spread monitoring and alerts
- Price spike detection
- Portfolio P&L tracking
- Position risk monitoring

**Alert System:**
- Alert types: ORDER, POSITION, PRICE, PORTFOLIO events
- Alert levels: INFO, WARNING, ERROR, CRITICAL
- Callback-based notifications
- Alert acknowledgment tracking

**Portfolio Snapshots:**
- Point-in-time portfolio state
- P&L tracking over time
- Historical analysis capability

**Dependencies:**
- OrderManager from order_management
- PortfolioManager from order_management
- Alert data classes
- Standard library

---

### 4. Settlement & Reporting Layer

#### `trade_settlement.py` (790 lines)
Trade settlement, performance reporting, and compliance.

**Components:**
- **TradeSettlementEngine**: Settlement confirmation and logging
- **PerformanceReporter**: Comprehensive metrics calculation
- **TradeAnalytics**: Trade classification and analysis
- **ReportExporter**: Multi-format report generation
- **ComplianceTracker**: Regulatory record keeping

**Performance Metrics Calculated:**
- Win rate: percentage of winning trades
- Profit factor: total profit / total loss
- Sharpe ratio: risk-adjusted returns
- Max drawdown: peak-to-trough decline
- Recovery factor: profit / max drawdown
- Risk-reward ratio: average win / average loss
- Annualized return: extrapolated return

**Analytics:**
- Symbol-based statistics
- Drawdown analysis
- Trade duration analysis
- Fee impact analysis

**Report Formats:**
- CSV: Spreadsheet compatible
- JSON: Machine-readable structured data
- TEXT: Human-readable formatted report

**Compliance Features:**
- Trade audit trail
- Settlement records
- Regulatory reporting

**Dependencies:**
- Trade data from order_management
- Standard library

---

## Data Flow Architecture

### Complete Order Lifecycle

```
1. CREATE ORDER
   OrderManager.create_order()
   → Order (PENDING status)
   └─ OrderStatusMonitor registers for monitoring

2. SUBMIT ORDER
   OrderManager.submit_order()
   → Order (OPEN status)
   └─ OrderStatusMonitor.check_status_updates() detects change
   └─ Callbacks triggered if registered

3. ORDER EXECUTION
   OrderExecutionEngine.execute_*_order()
   → ExecutionResult with fill price/quantity/fees
   
4. FILL ORDER
   OrderManager.fill_order()
   → Order (FILLED status)
   └─ OrderStatusMonitor detects status change
   └─ Portfolio value updates due to new position

5. POSITION MANAGEMENT
   PositionManager.open_position()
   → Position (OPENING/OPEN status)
   ├─ OrderStatusMonitor.check_status_updates() confirms
   └─ PortfolioMonitor.take_snapshot() records state

6. PRICE UPDATES
   PositionManager.update_position_price()
   → Position with new current_price
   ├─ Unrealized P&L calculated
   ├─ Stop loss/take profit checked
   └─ PortfolioMonitor tracks changes

7. POSITION CLOSE
   PositionManager.reduce_position()
   → Position (CLOSED status) + Trade record
   ├─ Realized P&L calculated
   └─ Trade stored in PositionManager.trades[]

8. TRADE SETTLEMENT
   TradeSettlementEngine.settle_trade()
   → TradeSettlement record
   └─ ComplianceTracker records transaction

9. REPORTING
   PerformanceReporter.calculate_metrics()
   → PerformanceMetrics with all statistics
   └─ ReportExporter.export_*() generates reports
```

---

## Key Design Patterns

### 1. State Machine Pattern (Orders)
```
PENDING ──submit──→ OPEN ──fill──→ FILLED
                    │              ↑
                    └─cancel→ CANCELLED
```

### 2. Observer Pattern (Monitoring)
```
OrderManager (Subject)
    ├─ OrderStatusMonitor (Observer 1)
    ├─ PortfolioMonitor (Observer 2)
    └─ EventNotifier (Observer 3)
```

### 3. Strategy Pattern (Execution)
```
OrderExecutionEngine
    ├─ execute_market_order()
    ├─ execute_limit_order()
    ├─ execute_stop_loss_order()
    ├─ execute_take_profit_order()
    └─ execute_trailing_stop_order()
```

### 4. Facade Pattern (Settlement)
```
TradeSettlementEngine (Facade)
    ├─ Uses: TradeSettlement
    ├─ Uses: PerformanceReporter
    ├─ Uses: TradeAnalytics
    ├─ Uses: ReportExporter
    └─ Uses: ComplianceTracker
```

---

## Async/Await Architecture

All I/O operations use async/await for non-blocking performance:

```python
# Order Creation (async)
order = await order_mgr.create_order(...)

# Monitoring (async)
changes = await order_monitor.check_status_updates()

# Settlement (async)
settlement = await settlement_engine.settle_trade(...)

# Reporting (async)
metrics = await reporter.calculate_metrics(...)
```

Benefits:
- Non-blocking concurrent operations
- Scalable to handle many orders
- Better resource utilization
- Native integration with async event loops

---

## Error Handling Strategy

### Try-Except Blocks
```python
try:
    result = await risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    return None
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

### Validation
```python
if not order:
    logger.error(f"Order not found")
    return None

if quantity > position.current_quantity:
    logger.error(f"Insufficient quantity")
    return False
```

### Callbacks
```python
def on_error(error):
    logger.error(f"Callback error: {error}")

try:
    callback(data)
except Exception as e:
    on_error(e)
```

---

## Type System

### 100% Type Coverage

All functions have complete type hints:

```python
async def create_order(
    self,
    exchange_type: ExchangeType,
    order_type: OrderType,
    side: OrderSide,
    symbol: str,
    quantity: float,
    limit_price: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Order:
```

### Type Checking

Use `mypy` for static type checking:
```bash
mypy src/phase5/ --strict
```

---

## Testing Architecture

### Test Organization

```
src/tests/
├── test_phase5_monitoring.py      # 445 lines, 6 tests
├── test_phase5_settlement.py      # 434 lines, 6 tests
└── test_phase5_comprehensive.py   # 416 lines, 6 tests
```

### Test Coverage

- **Unit Tests**: Individual method testing
- **Integration Tests**: Multi-module interactions
- **End-to-End Tests**: Complete workflows
- **Mock Data**: Simulated orders and positions

### Running Tests

```bash
# Run all Phase 5 tests
pytest src/tests/test_phase5_*.py -v

# Run specific test
pytest src/tests/test_phase5_comprehensive.py::test_complete_order_lifecycle -v

# Run with coverage
pytest src/tests/test_phase5_*.py --cov=src/phase5
```

---

## Performance Considerations

### Scalability

**Current Limitations:**
- In-memory storage (suitable for backtesting)
- Single-threaded event loop
- No database integration

**Future Enhancements:**
- Redis for distributed caching
- PostgreSQL for persistent storage
- Multi-threaded execution for live trading
- Pub/Sub for distributed monitoring

### Memory Usage

**Estimates:**
- Order: ~500 bytes
- Position: ~600 bytes
- Trade: ~400 bytes
- Alert: ~300 bytes

**Example:** 10,000 trades ≈ 4 MB memory

---

## Configuration

### Runtime Configuration

```python
# Execution
execution_engine = OrderExecutionEngine(
    mode=ExecutionMode.BACKTEST,
    slippage_percent=0.05,
    fee_percent=0.1
)

# Portfolio
portfolio = PortfolioManager(initial_capital=10000.0)

# Monitoring
monitor = MonitoringDashboard(
    order_manager=order_mgr,
    position_manager=position_mgr,
    portfolio_manager=portfolio_mgr
)
```

---

## Extension Points

### Custom Alert Handlers

```python
def custom_alert_handler(alert):
    if alert.level == AlertLevel.CRITICAL:
        send_email_alert(alert)
    
notifier.register_alert_callback(custom_alert_handler)
```

### Custom Order Execution

```python
class CustomExecutionEngine(OrderExecutionEngine):
    async def execute_market_order(self, order: Order) -> ExecutionResult:
        # Custom implementation
        pass
```

### Custom Analytics

```python
class CustomAnalytics(TradeAnalytics):
    def get_advanced_metrics(self, trades: List[Trade]) -> Dict:
        # Custom metrics calculation
        pass
```

---

## Integration with Phase 5 Stages

### Stage 1: Trading System Setup
- Provides: API configuration, exchange connection

### Stage 2: Exchange Connectivity
- Depends on: ExchangeConnector
- Provides: Order management foundation

### Stage 3: Order Management (CURRENT)
- Integrates: All 4 modules
- Builds: Complete trading workflow

### Stage 4: Advanced Features (Future)
- Will use: Order Management APIs
- Add: Machine learning, optimization

---

## Deployment Checklist

- [ ] All tests passing (18/18)
- [ ] Type checking passing (mypy --strict)
- [ ] Linting passing (flake8)
- [ ] Documentation complete
- [ ] Performance testing done
- [ ] Error handling verified
- [ ] Logging configured
- [ ] Security review complete

---

## Related Documentation

- [API Reference](PHASE5_STAGE3_API_REFERENCE.md)
- [Quick Start Guide](PHASE5_STAGE3_QUICK_START.md)
- [Testing Guide](PHASE5_STAGE3_TESTING.md)
- [Phase 5 Overview](PHASE5_OVERVIEW.md)
