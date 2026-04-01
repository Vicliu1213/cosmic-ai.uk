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

---

## System Integration Patterns

### 1. Multi-Exchange Order Management

```python
# Unified interface for multiple exchanges
class MultiExchangeOrderManager:
    """Manage orders across multiple exchanges simultaneously"""
    
    def __init__(self):
        self.exchanges = {}  # exchange_type -> OrderManager
        self.order_mapping = {}  # order_id -> (exchange_type, local_order_id)
    
    async def add_exchange(self, exchange_type: ExchangeType, config: Dict):
        """Register a new exchange"""
        self.exchanges[exchange_type] = OrderManager(exchange_type, config)
    
    async def create_order_on_exchange(self, exchange_type: ExchangeType, **kwargs) -> Order:
        """Create order on specific exchange"""
        if exchange_type not in self.exchanges:
            raise ValueError(f"Exchange {exchange_type} not registered")
        
        order = await self.exchanges[exchange_type].create_order(**kwargs)
        self.order_mapping[order.order_id] = (exchange_type, order.order_id)
        return order
    
    async def submit_orders_to_all_exchanges(self, order_specs: List[Dict]):
        """Submit same order to multiple exchanges (arbitrage strategy)"""
        results = []
        
        for spec in order_specs:
            exchange_type = spec.pop("exchange_type")
            order = await self.create_order_on_exchange(exchange_type, **spec)
            results.append(order)
        
        return results
    
    async def get_order_from_any_exchange(self, order_id: str) -> Order:
        """Retrieve order from its exchange"""
        if order_id not in self.order_mapping:
            raise ValueError(f"Order {order_id} not tracked")
        
        exchange_type, local_id = self.order_mapping[order_id]
        return await self.exchanges[exchange_type].get_order(local_id)
```

### 2. Event-Driven Architecture

```python
# Event bus for system-wide communication
from dataclasses import dataclass
from typing import Callable, List
import asyncio

@dataclass
class OrderEvent:
    event_type: str  # "order.created", "order.filled", "order.cancelled"
    order_id: str
    data: Dict[str, Any]
    timestamp: datetime

class OrderEventBus:
    """Central event distribution system"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def publish(self, event: OrderEvent):
        """Publish event to all subscribers"""
        if event.event_type in self.subscribers:
            tasks = [
                cb(event) for cb in self.subscribers[event.event_type]
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Remove callback"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)

# Usage
bus = OrderEventBus()

async def on_order_filled(event: OrderEvent):
    print(f"Order {event.order_id} filled!")
    # Trigger position opening

bus.subscribe("order.filled", on_order_filled)

# In OrderManager
event = OrderEvent(
    event_type="order.filled",
    order_id=order.order_id,
    data={"fill_price": 50000, "quantity": 1.0},
    timestamp=datetime.now()
)
await bus.publish(event)
```

### 3. Circuit Breaker Pattern

```python
# Prevent cascading failures
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failures detected, block calls
    HALF_OPEN = "half_open"  # Testing if system recovered

class OrderSubmissionCircuitBreaker:
    """Protect order submission from repeated failures"""
    
    def __init__(self, failure_threshold=5, recovery_timeout_seconds=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_seconds)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            # Check if ready to recover
            if datetime.now() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print("Circuit breaker: HALF_OPEN (testing recovery)")
            else:
                raise RuntimeError("Circuit breaker: OPEN (service unavailable)")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset state
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print("Circuit breaker: CLOSED (recovered)")
            
            self.last_success_time = datetime.now()
            return result
        
        except Exception as e:
            # Failure - increment counter
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"Circuit breaker: OPEN (failures: {self.failure_count})")
            
            raise
```

---

## Scaling Strategies

### 1. Horizontal Scaling with Load Balancing

```python
# Distribute order load across multiple instances
class LoadBalancedOrderManagementCluster:
    """Manage orders across multiple OM nodes"""
    
    def __init__(self, num_nodes=3):
        self.nodes = [OrderManager() for _ in range(num_nodes)]
        self.current_index = 0
        self.order_to_node = {}  # order_id -> node_index
    
    def _get_next_node(self):
        """Round-robin node selection"""
        node = self.nodes[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.nodes)
        return node
    
    async def create_order(self, **kwargs) -> Order:
        """Create order on least-loaded node"""
        node = self._get_next_node()
        order = await node.create_order(**kwargs)
        self.order_to_node[order.order_id] = node
        return order
    
    async def get_order(self, order_id: str) -> Order:
        """Retrieve order from correct node"""
        if order_id not in self.order_to_node:
            # Search all nodes
            for node in self.nodes:
                orders = node.orders
                if order_id in orders:
                    return orders[order_id]
        
        node = self.order_to_node[order_id]
        return await node.get_order(order_id)
```

### 2. Caching Layer

```python
# Reduce database/API calls with intelligent caching
class CachedOrderManager:
    """Order manager with caching for frequent queries"""
    
    def __init__(self, base_manager: OrderManager, cache_ttl_seconds=5):
        self.base_manager = base_manager
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self.cache = {}
        self.cache_time = {}
    
    async def get_portfolio_stats(self, force_refresh=False) -> Dict:
        """Get cached portfolio stats"""
        cache_key = "portfolio_stats"
        
        if not force_refresh and cache_key in self.cache:
            if datetime.now() - self.cache_time[cache_key] < self.cache_ttl:
                return self.cache[cache_key]
        
        # Fetch fresh data
        stats = self.base_manager.get_portfolio_stats()
        
        self.cache[cache_key] = stats
        self.cache_time[cache_key] = datetime.now()
        
        return stats
    
    def invalidate_cache(self, key: str = None):
        """Invalidate specific or all cache"""
        if key:
            self.cache.pop(key, None)
            self.cache_time.pop(key, None)
        else:
            self.cache.clear()
            self.cache_time.clear()
```

### 3. Rate Limiting

```python
# Control API call rate
import time
from collections import deque

class RateLimiter:
    """Rate limiter for order submissions"""
    
    def __init__(self, max_requests_per_minute=100):
        self.max_requests = max_requests_per_minute
        self.window_size = 60  # seconds
        self.request_times = deque()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old requests outside window
        while self.request_times and self.request_times[0] < now - self.window_size:
            self.request_times.popleft()
        
        # If at limit, wait
        if len(self.request_times) >= self.max_requests:
            wait_time = self.window_size - (now - self.request_times[0])
            await asyncio.sleep(wait_time)
        
        self.request_times.append(now)
    
    async def execute_with_limit(self, func: Callable, *args, **kwargs):
        """Execute function respecting rate limits"""
        await self.wait_if_needed()
        return await func(*args, **kwargs)

# Usage
limiter = RateLimiter(max_requests_per_minute=50)
order = await limiter.execute_with_limit(order_mgr.submit_order, order)
```

---

## Deployment Architecture

### Production Deployment

```yaml
# kubernetes_deployment.yaml - Example K8s deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-management-system
  labels:
    app: oms
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oms
  template:
    metadata:
      labels:
        app: oms
    spec:
      containers:
      - name: order-manager
        image: cosmic-ai:phase5-oms-latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: CACHE_TTL
          value: "5"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Monitoring & Observability

```python
# Prometheus metrics for monitoring
from prometheus_client import Counter, Histogram, Gauge

# Metrics definitions
orders_created = Counter('orders_created_total', 'Total orders created')
orders_filled = Counter('orders_filled_total', 'Total orders filled')
order_duration = Histogram('order_duration_seconds', 'Order lifetime in seconds')
active_positions = Gauge('active_positions', 'Number of active positions')
portfolio_value = Gauge('portfolio_value_usd', 'Portfolio total value')

# Instrument the order manager
class InstrumentedOrderManager(OrderManager):
    async def create_order(self, **kwargs) -> Order:
        order = await super().create_order(**kwargs)
        orders_created.inc()
        return order
    
    async def fill_order(self, order_id: str, **kwargs):
        result = await super().fill_order(order_id, **kwargs)
        orders_filled.inc()
        order_duration.observe((datetime.now() - result.created_time).total_seconds())
        return result
```

---

## Related Documentation

- [API Reference](PHASE5_STAGE3_API_REFERENCE.md)
- [Quick Start Guide](PHASE5_STAGE3_QUICK_START.md)
- [Testing Guide](PHASE5_STAGE3_TESTING.md)
- [Phase 5 Overview](PHASE5_OVERVIEW.md)
