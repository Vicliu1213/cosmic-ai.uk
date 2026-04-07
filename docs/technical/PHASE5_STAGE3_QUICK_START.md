# Phase 5 Stage 3 - Order Management System Quick Start Guide
訂單管理系統快速入門指南

## Installation & Setup

### Prerequisites

```bash
# Ensure Python 3.10+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Import Required Modules

```python
from src.phase5.order_management import (
    OrderManager, PositionManager, PortfolioManager,
    OrderType, OrderSide, OrderStatus, PositionStatus
)
from src.phase5.order_execution import (
    OrderExecutionEngine, ExecutionMode
)
from src.phase5.order_monitoring import (
    OrderStatusMonitor, PortfolioMonitor, EventNotifier,
    AlertType, AlertLevel
)
from src.phase5.trade_settlement import (
    TradeSettlementEngine, PerformanceReporter,
    ReportExporter, ReportFormat
)
from src.phase5.exchange_connector import ExchangeType
```

---

## Basic Order Management

### 1. Create an Order

```python
# Initialize manager
order_mgr = OrderManager()

# Create a limit buy order
order = await order_mgr.create_order(
    exchange_type=ExchangeType.BINANCE,
    order_type=OrderType.LIMIT,
    side=OrderSide.BUY,
    symbol="BTC/USDT",
    quantity=1.0,
    limit_price=50000.0
)

print(f"Order created: {order.order_id}")
print(f"Status: {order.status.value}")  # Output: pending
```

### 2. Submit Order

```python
# Submit to exchange
success = await order_mgr.submit_order(order)

if success:
    print(f"Order submitted successfully")
    print(f"New status: {order.status.value}")  # Output: open
else:
    print("Order submission failed")
```

### 3. Fill Order

```python
# Simulate order fill
await order_mgr.fill_order(
    order_id=order.order_id,
    filled_quantity=1.0,
    fill_price=49950.0,
    fee_amount=10.0
)

print(f"Order status: {order.status.value}")  # Output: filled
print(f"Average fill price: {order.price.average_fill_price}")
print(f"Total cost: {order.total_cost}")
```

### 4. Cancel Order

```python
# Create another order
order2 = await order_mgr.create_order(
    exchange_type=ExchangeType.BINANCE,
    order_type=OrderType.LIMIT,
    side=OrderSide.SELL,
    symbol="BTC/USDT",
    quantity=0.5,
    limit_price=51000.0
)

await order_mgr.submit_order(order2)

# Cancel it
await order_mgr.cancel_order(order2.order_id)
print(f"Order cancelled: {order2.status.value}")  # Output: cancelled
```

---

## Position Management

### 1. Open a Position

```python
position_mgr = PositionManager()

# Open a long position from the filled order
position = await position_mgr.open_position(
    exchange_type=ExchangeType.BINANCE,
    symbol="BTC/USDT",
    side=OrderSide.BUY,
    entry_price=49950.0,
    quantity=1.0,
    stop_loss_price=49000.0,        # Risk management
    take_profit_price=51000.0,      # Profit target
    entry_orders=[order.order_id]
)

print(f"Position opened: {position.position_id}")
print(f"Entry price: ${position.entry_price}")
print(f"Current quantity: {position.current_quantity}")
```

### 2. Monitor Position P&L

```python
# Update position price
position.current_price = 50500.0

# Get unrealized P&L
unrealized_pnl = position.get_unrealized_pnl()
unrealized_roi = position.get_unrealized_roi()

print(f"Unrealized P&L: ${unrealized_pnl:.2f}")
print(f"Unrealized ROI: {unrealized_roi:.2f}%")

# Check if stop loss or take profit hit
if position.hit_stop_loss():
    print("⚠️ Stop loss hit!")
elif position.hit_take_profit():
    print("✅ Take profit hit!")
```

### 3. Close Position

```python
# Close the position at current price
success = await position_mgr.reduce_position(
    position_id=position.position_id,
    quantity=1.0,  # Close entire position
    exit_price=50500.0
)

if success:
    # Get the completed trade
    trade = position_mgr.trades[-1]
    print(f"Position closed!")
    print(f"Realized P&L: ${trade.realized_pnl:.2f}")
    print(f"ROI: {trade.roi_percent:.2f}%")
```

### 4. Partial Close

```python
# Close part of position
success = await position_mgr.reduce_position(
    position_id=position.position_id,
    quantity=0.5,  # Partial close
    exit_price=50500.0
)

print(f"Position now has: {position.current_quantity} contracts")
```

---

## Portfolio Management

### 1. Initialize Portfolio

```python
portfolio_mgr = PortfolioManager(initial_capital=10000.0)

print(f"Initial capital: ${portfolio_mgr.initial_capital}")
print(f"Current value: ${portfolio_mgr.get_portfolio_value()}")
```

### 2. Get Portfolio Statistics

```python
stats = portfolio_mgr.get_portfolio_stats()

print(f"Portfolio value: ${stats['portfolio_value']:.2f}")
print(f"Unrealized P&L: ${stats['unrealized_pnl']:.2f}")
print(f"Realized P&L: ${stats['realized_pnl']:.2f}")
print(f"ROI: {stats['roi_percent']:.2f}%")
print(f"Open positions: {stats['num_open_positions']}")
print(f"Closed positions: {stats['num_closed_positions']}")
```

### 3. Analyze Position Exposure

```python
# Get exposure to each symbol
btc_exposure = portfolio_mgr.get_symbol_exposure("BTC/USDT")
print(f"BTC/USDT exposure: ${btc_exposure:.2f}")

# Get largest positions
largest = portfolio_mgr.get_largest_positions(limit=5)
for position, value in largest:
    print(f"{position.symbol}: ${value:.2f}")
```

---

## Order Execution

### 1. Setup Execution Engine

```python
execution_engine = OrderExecutionEngine(
    mode=ExecutionMode.BACKTEST,
    slippage_percent=0.05,      # 0.05% slippage
    fee_percent=0.1             # 0.1% fee
)
```

### 2. Update Order Book

```python
# Add market data
await execution_engine.order_book_manager.update_order_book(
    symbol="BTC/USDT",
    exchange_type=ExchangeType.BINANCE,
    bids=[(50000.0, 1.0), (49900.0, 2.0)],
    asks=[(50100.0, 1.5), (50200.0, 2.5)],
    last_trade_price=50050.0
)
```

### 3. Execute Market Order

```python
# Create market order
market_order = await order_mgr.create_order(
    exchange_type=ExchangeType.BINANCE,
    order_type=OrderType.MARKET,
    side=OrderSide.BUY,
    symbol="BTC/USDT",
    quantity=1.0
)

await order_mgr.submit_order(market_order)

# Execute
result = await execution_engine.execute_market_order(market_order)

print(f"Executed: {result.executed}")
print(f"Filled quantity: {result.filled_quantity}")
print(f"Filled price: ${result.filled_price}")
print(f"Slippage: {result.slippage:.4f}%")
print(f"Fee: ${result.fee_amount:.2f}")

# Update order
await order_mgr.fill_order(
    order_id=market_order.order_id,
    filled_quantity=result.filled_quantity,
    fill_price=result.filled_price,
    fee_amount=result.fee_amount
)
```

### 4. Execute Limit Order

```python
# Create limit order
limit_order = await order_mgr.create_order(
    exchange_type=ExchangeType.BINANCE,
    order_type=OrderType.LIMIT,
    side=OrderSide.SELL,
    symbol="BTC/USDT",
    quantity=1.0,
    limit_price=51000.0
)

await order_mgr.submit_order(limit_order)

# Try to execute (will only execute if price crossed)
result = await execution_engine.execute_limit_order(limit_order)

if result.executed:
    print("Limit order executed!")
else:
    print("Limit not crossed, order remains open")
```

---

## Real-Time Monitoring

### 1. Monitor Order Status

```python
order_monitor = OrderStatusMonitor(order_mgr)

# Start monitoring orders
await order_monitor.monitor_order(order.order_id)

# Check for status changes
changes = await order_monitor.check_status_updates()

for order_obj, old_status, new_status in changes:
    print(f"{order_obj.order_id}: {old_status.value} → {new_status.value}")
```

### 2. Register Status Callbacks

```python
def on_order_status_changed(order, old_status, new_status):
    print(f"Order {order.order_id} status changed!")
    if new_status == OrderStatus.FILLED:
        print("Order filled - opening position...")
    elif new_status == OrderStatus.CANCELLED:
        print("Order was cancelled")

order_monitor.register_status_callback(on_order_status_changed)
```

### 3. Monitor Portfolio

```python
portfolio_monitor = PortfolioMonitor(portfolio_mgr)

# Take a snapshot
snapshot = await portfolio_monitor.take_snapshot()
print(f"Portfolio value: ${snapshot.portfolio_value}")
print(f"Unrealized P&L: ${snapshot.unrealized_pnl}")

# Get historical snapshots
history = portfolio_monitor.get_portfolio_history(lookback_minutes=60)
print(f"Snapshots in last hour: {len(history)}")
```

### 4. Setup Alerts

```python
notifier = EventNotifier()

# Register alert callback
def on_alert(alert):
    print(f"[{alert.level.value.upper()}] {alert.message}")
    if alert.level == AlertLevel.CRITICAL:
        # Take action on critical alerts
        print("CRITICAL ALERT - Take immediate action!")

notifier.register_alert_callback(on_alert)

# Emit alerts
await notifier.emit_alert(
    alert_type=AlertType.POSITION_OPENED,
    level=AlertLevel.INFO,
    message="Long position opened on BTC/USDT",
    symbol="BTC/USDT",
    value=1.0
)
```

---

## Trade Settlement & Reporting

### 1. Settle Trade

```python
settlement_engine = TradeSettlementEngine()

# Get completed trade
trade = position_mgr.trades[-1]

# Settle it
settlement = await settlement_engine.settle_trade(
    trade=trade,
    fee_amount=20.0  # Total fees
)

print(f"Settlement status: {settlement.status.value}")
print(f"Settlement ID: {settlement.settlement_id}")
```

### 2. Calculate Performance Metrics

```python
reporter = PerformanceReporter()

# Calculate metrics from trades
metrics = await reporter.calculate_metrics(
    trades=position_mgr.trades,
    initial_capital=10000.0,
    current_capital=portfolio_mgr.get_portfolio_value()
)

print(f"Total trades: {metrics.total_trades}")
print(f"Winning trades: {metrics.winning_trades}")
print(f"Win rate: {metrics.win_rate:.2f}%")
print(f"Profit factor: {metrics.profit_factor:.2f}")
print(f"Sharpe ratio: {metrics.sharpe_ratio:.2f}")
print(f"Max drawdown: {metrics.max_drawdown_percent:.2f}%")
```

### 3. Analyze Trades

```python
from src.phase5.trade_settlement import TradeAnalytics

analytics = TradeAnalytics()

# Get statistics by symbol
symbol_stats = analytics.get_symbol_statistics(position_mgr.trades)
for symbol, stats in symbol_stats.items():
    print(f"\n{symbol}:")
    print(f"  Trades: {stats['total_trades']}")
    print(f"  Win rate: {stats['win_rate']:.2f}%")
    print(f"  Total P&L: ${stats['total_pnl']:.2f}")

# Analyze drawdowns
dd_analysis = analytics.get_drawdown_analysis(position_mgr.trades)
print(f"\nMax drawdown: {dd_analysis['max_drawdown_percent']:.2f}%")
print(f"Drawdown trades: {len(dd_analysis['drawdown_trades'])}")
```

### 4. Export Reports

```python
exporter = ReportExporter()

# Export trades as CSV
csv_report = await exporter.export_trades(
    trades=position_mgr.trades,
    format=ReportFormat.CSV
)

# Export metrics as JSON
json_report = await exporter.export_metrics(
    metrics=metrics,
    format=ReportFormat.JSON
)

# Export metrics as readable text
text_report = await exporter.export_metrics(
    metrics=metrics,
    format=ReportFormat.TEXT
)

print("Reports generated successfully!")
```

---

## Complete Example: Full Trading Workflow

```python
import asyncio
from datetime import datetime

async def complete_trading_workflow():
    """Complete example of creating, executing, monitoring, and settling a trade."""
    
    # Initialize managers
    order_mgr = OrderManager()
    position_mgr = PositionManager()
    portfolio_mgr = PortfolioManager(initial_capital=10000.0)
    execution_engine = OrderExecutionEngine(mode=ExecutionMode.BACKTEST)
    order_monitor = OrderStatusMonitor(order_mgr)
    portfolio_monitor = PortfolioMonitor(portfolio_mgr)
    settlement_engine = TradeSettlementEngine()
    reporter = PerformanceReporter()
    exporter = ReportExporter()
    
    print("=== COMPLETE TRADING WORKFLOW ===\n")
    
    # 1. CREATE AND SUBMIT ORDER
    print("1. Creating order...")
    order = await order_mgr.create_order(
        exchange_type=ExchangeType.BINANCE,
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        symbol="BTC/USDT",
        quantity=1.0,
        limit_price=50000.0
    )
    print(f"   Order ID: {order.order_id}")
    
    print("2. Submitting order...")
    await order_mgr.submit_order(order)
    await order_monitor.monitor_order(order.order_id)
    print(f"   Status: {order.status.value}")
    
    # 2. FILL ORDER
    print("3. Filling order...")
    await order_mgr.fill_order(
        order_id=order.order_id,
        filled_quantity=1.0,
        fill_price=49950.0
    )
    print(f"   Filled at ${order.price.average_fill_price}")
    
    # 3. OPEN POSITION
    print("4. Opening position...")
    position = await position_mgr.open_position(
        exchange_type=ExchangeType.BINANCE,
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        entry_price=49950.0,
        quantity=1.0,
        stop_loss_price=49000.0,
        take_profit_price=51000.0
    )
    print(f"   Position ID: {position.position_id}")
    
    # 4. MONITOR POSITION
    print("5. Monitoring position...")
    snapshot1 = await portfolio_monitor.take_snapshot()
    print(f"   Portfolio value: ${snapshot1.portfolio_value:.2f}")
    
    position.current_price = 50500.0
    snapshot2 = await portfolio_monitor.take_snapshot()
    print(f"   Unrealized P&L: ${snapshot2.unrealized_pnl:.2f}")
    
    # 5. CLOSE POSITION
    print("6. Closing position...")
    await position_mgr.reduce_position(
        position_id=position.position_id,
        quantity=1.0,
        exit_price=50500.0
    )
    trade = position_mgr.trades[-1]
    print(f"   Realized P&L: ${trade.realized_pnl:.2f}")
    
    # 6. SETTLE TRADE
    print("7. Settling trade...")
    settlement = await settlement_engine.settle_trade(trade, fee_amount=10.0)
    print(f"   Settlement ID: {settlement.settlement_id}")
    
    # 7. REPORTING
    print("8. Generating reports...")
    metrics = await reporter.calculate_metrics(
        trades=position_mgr.trades,
        initial_capital=portfolio_mgr.initial_capital,
        current_capital=portfolio_mgr.get_portfolio_value()
    )
    
    print("\n=== FINAL METRICS ===")
    print(f"Total trades: {metrics.total_trades}")
    print(f"Winning trades: {metrics.winning_trades}")
    print(f"Win rate: {metrics.win_rate:.2f}%")
    print(f"Total profit: ${metrics.total_profit:.2f}")
    print(f"Sharpe ratio: {metrics.sharpe_ratio:.2f}")
    print(f"Max drawdown: {metrics.max_drawdown_percent:.2f}%")
    
    csv_report = await exporter.export_trades(
        position_mgr.trades,
        ReportFormat.CSV
    )
    print("\n✅ Trading workflow completed!")

# Run the example
if __name__ == "__main__":
    asyncio.run(complete_trading_workflow())
```

---

## Common Tasks

### Monitor Multiple Orders

```python
order_ids = [order1.order_id, order2.order_id, order3.order_id]

for order_id in order_ids:
    await order_monitor.monitor_order(order_id)

# Check all monitored orders periodically
while True:
    changes = await order_monitor.check_status_updates()
    for order, old_status, new_status in changes:
        print(f"Order {order.order_id}: {old_status.value} → {new_status.value}")
    await asyncio.sleep(1)  # Check every 1 second
```

### Set Risk Limits

```python
def enforce_risk_limits(position):
    """Check if position exceeds risk limits."""
    if position.get_unrealized_roi() < -5:  # Stop at 5% loss
        return False  # Reject
    return True

# Before opening position
if enforce_risk_limits(new_position):
    await position_mgr.open_position(...)
```

### Track Symbol Performance

```python
symbol = "BTC/USDT"
symbol_trades = [t for t in position_mgr.trades if t.symbol == symbol]

# Calculate symbol-specific metrics
wins = sum(1 for t in symbol_trades if t.realized_pnl > 0)
win_rate = (wins / len(symbol_trades)) * 100 if symbol_trades else 0
total_pnl = sum(t.realized_pnl for t in symbol_trades)

print(f"{symbol}: {win_rate:.1f}% win rate, ${total_pnl:.2f} P&L")
```

---

## Troubleshooting

### Order Not Filling

```python
# Check order book
order_book = execution_engine.order_book_manager.get_order_book("BTC/USDT")
if order_book:
    print(f"Best bid: ${order_book.best_bid}")
    print(f"Best ask: ${order_book.best_ask}")
    print(f"Spread: ${order_book.spread:.2f}")
else:
    print("No order book data available")
```

### Position Not Opening

```python
# Check if order is filled
if order.status != OrderStatus.FILLED:
    print(f"Order not filled yet: {order.status.value}")
    print(f"Filled quantity: {order.quantity.filled_quantity}")
else:
    # Order is filled, try opening position again
    position = await position_mgr.open_position(...)
```

### Incorrect Portfolio Value

```python
# Recalculate portfolio value manually
positions = position_mgr.get_open_positions()
position_value = sum(p.current_quantity * p.current_price for p in positions)
total_value = portfolio_mgr.initial_capital + sum(t.realized_pnl for t in position_mgr.trades) + position_value
print(f"Manual calculation: ${total_value:.2f}")
print(f"Portfolio value: ${portfolio_mgr.get_portfolio_value():.2f}")
```

---

---

## Advanced Order Management Patterns

### 1. Order Chaining (Conditional Orders)

```python
# Create a take-profit order that triggers when main order fills
async def create_conditional_orders(order_mgr, base_order):
    """Create entry order with automatic exit orders"""
    
    # Submit entry order
    await order_mgr.submit_order(base_order)
    
    # Wait for fill
    while base_order.status != OrderStatus.FILLED:
        await asyncio.sleep(0.1)
    
    # Create take-profit order (triggered after fill)
    tp_order = await order_mgr.create_order(
        exchange_type=base_order.exchange_type,
        order_type=OrderType.LIMIT,
        side=OrderSide.SELL if base_order.side == OrderSide.BUY else OrderSide.BUY,
        symbol=base_order.symbol,
        quantity=base_order.quantity.filled_quantity,
        limit_price=base_order.price.average_fill_price * 1.05  # 5% profit
    )
    
    # Create stop-loss order (protective)
    sl_order = await order_mgr.create_order(
        exchange_type=base_order.exchange_type,
        order_type=OrderType.MARKET,
        side=OrderSide.SELL if base_order.side == OrderSide.BUY else OrderSide.BUY,
        symbol=base_order.symbol,
        quantity=base_order.quantity.filled_quantity
    )
    
    return {
        "entry": base_order,
        "take_profit": tp_order,
        "stop_loss": sl_order
    }
```

### 2. Batch Order Execution

```python
async def submit_batch_orders(order_mgr, orders: List, max_concurrent=5):
    """Execute multiple orders with rate limiting"""
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def submit_with_limit(order):
        async with semaphore:
            try:
                success = await order_mgr.submit_order(order)
                return order.order_id, success, None
            except Exception as e:
                return order.order_id, False, str(e)
    
    results = await asyncio.gather(*[
        submit_with_limit(order) for order in orders
    ])
    
    # Summary
    successful = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)
    
    print(f"Batch result: {successful} success, {failed} failed out of {len(orders)}")
    return results
```

### 3. Dynamic Order Sizing

```python
async def calculate_position_size(position_mgr, portfolio_mgr, 
                                   symbol: str, max_risk_percent=2.0):
    """Calculate order size based on portfolio risk limits"""
    
    portfolio_value = portfolio_mgr.get_portfolio_value()
    risk_amount = portfolio_value * (max_risk_percent / 100)
    
    # Get current symbol price
    current_price = 50000  # Get from market data
    
    # Calculate position size
    position_size = risk_amount / current_price
    
    # Apply portfolio limits
    current_exposure = portfolio_mgr.get_symbol_exposure(symbol)
    max_exposure = portfolio_value * 0.3  # Max 30% in one symbol
    
    if current_exposure + (position_size * current_price) > max_exposure:
        position_size = (max_exposure - current_exposure) / current_price
    
    return position_size

# Usage
size = await calculate_position_size(position_mgr, portfolio_mgr, "BTC/USDT")
print(f"Recommended position size: {size:.4f} BTC")
```

---

## Error Handling & Recovery

### 1. Resilient Order Submission

```python
async def submit_order_with_retry(order_mgr, order, max_retries=3):
    """Submit order with automatic retry on failure"""
    
    for attempt in range(max_retries):
        try:
            success = await order_mgr.submit_order(order)
            if success:
                print(f"Order {order.order_id} submitted successfully")
                return True
        except ConnectionError as e:
            print(f"Connection error (attempt {attempt+1}/{max_retries}): {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except ValueError as e:
            print(f"Validation error: {e}")
            return False  # Don't retry validation errors
        except Exception as e:
            print(f"Unexpected error (attempt {attempt+1}/{max_retries}): {e}")
            await asyncio.sleep(2 ** attempt)
    
    print(f"Failed to submit order after {max_retries} attempts")
    return False
```

### 2. Order State Recovery

```python
async def recover_incomplete_orders(order_mgr, position_mgr):
    """Recover from system failure by checking incomplete orders"""
    
    incomplete_orders = [
        o for o in order_mgr.orders
        if o.status in [OrderStatus.PENDING, OrderStatus.OPEN]
    ]
    
    for order in incomplete_orders:
        print(f"Recovering order {order.order_id}: {order.status.value}")
        
        try:
            # Query exchange for actual status
            actual_status = await order_mgr.query_order_status(order.order_id)
            
            if actual_status == OrderStatus.FILLED:
                # Update with fill info
                await order_mgr.fill_order(
                    order_id=order.order_id,
                    filled_quantity=order.quantity.original_quantity,
                    fill_price=order.price.limit_price
                )
                print(f"✓ Order {order.order_id} recovered as FILLED")
            
            elif actual_status == OrderStatus.CANCELLED:
                order.status = OrderStatus.CANCELLED
                print(f"✓ Order {order.order_id} recovered as CANCELLED")
        
        except Exception as e:
            print(f"✗ Failed to recover order {order.order_id}: {e}")
```

### 3. Position Safety Checks

```python
async def perform_position_safety_checks(position_mgr, portfolio_mgr):
    """Verify position integrity and take corrective action"""
    
    issues = []
    
    for position in position_mgr.positions:
        # Check 1: Quantity mismatch
        order_quantity = sum(
            o.quantity.filled_quantity for o in position.entry_orders
            if o.status == OrderStatus.FILLED
        )
        
        if position.current_quantity != order_quantity:
            issues.append({
                "type": "QUANTITY_MISMATCH",
                "position_id": position.position_id,
                "expected": order_quantity,
                "actual": position.current_quantity
            })
        
        # Check 2: Stop loss below entry price
        if position.side == OrderSide.BUY:
            if position.stop_loss_price >= position.entry_price:
                issues.append({
                    "type": "INVALID_STOP_LOSS",
                    "position_id": position.position_id,
                    "entry": position.entry_price,
                    "stop_loss": position.stop_loss_price
                })
        
        # Check 3: Position size exceeds portfolio
        position_value = position.current_quantity * position.current_price
        portfolio_value = portfolio_mgr.get_portfolio_value()
        
        if position_value > portfolio_value * 0.5:
            issues.append({
                "type": "EXCESSIVE_EXPOSURE",
                "position_id": position.position_id,
                "position_value": position_value,
                "portfolio_value": portfolio_value
            })
    
    if issues:
        print(f"Found {len(issues)} safety issues:")
        for issue in issues:
            print(f"  - {issue['type']}: {issue}")
    
    return issues
```

---

## Performance Optimization

### 1. Order Batching for Reporting

```python
async def batch_report_generation(position_mgr, reporter, batch_size=100):
    """Generate reports efficiently using batching"""
    
    all_trades = position_mgr.trades
    
    for i in range(0, len(all_trades), batch_size):
        batch = all_trades[i:i+batch_size]
        
        metrics = await reporter.calculate_metrics(
            trades=batch,
            initial_capital=10000.0,
            current_capital=10000.0  # Simplified
        )
        
        print(f"Batch {i//batch_size + 1}: {metrics.total_trades} trades, "
              f"Win rate: {metrics.win_rate:.1f}%")
    
    # Final aggregated metrics
    full_metrics = await reporter.calculate_metrics(
        trades=all_trades,
        initial_capital=10000.0,
        current_capital=10000.0
    )
    
    return full_metrics
```

### 2. Caching for Frequent Queries

```python
class CachedPortfolioManager:
    """Portfolio manager with caching to reduce computation"""
    
    def __init__(self, portfolio_mgr, cache_ttl_seconds=5):
        self.portfolio_mgr = portfolio_mgr
        self.cache_ttl = cache_ttl_seconds
        self._cache = {}
        self._cache_time = {}
    
    async def get_portfolio_value(self, force_refresh=False):
        """Get portfolio value with caching"""
        
        if not force_refresh and "portfolio_value" in self._cache:
            cache_age = asyncio.get_event_loop().time() - self._cache_time["portfolio_value"]
            if cache_age < self.cache_ttl:
                return self._cache["portfolio_value"]
        
        # Compute fresh value
        value = self.portfolio_mgr.get_portfolio_value()
        
        self._cache["portfolio_value"] = value
        self._cache_time["portfolio_value"] = asyncio.get_event_loop().time()
        
        return value
    
    def invalidate_cache(self):
        """Force cache refresh"""
        self._cache.clear()
        self._cache_time.clear()
```

---

## Integration Patterns

### 1. Strategy-To-Order Flow

```python
async def strategy_to_order_pipeline(strategy, order_mgr, position_mgr):
    """Pipeline: Strategy signal → Order → Position"""
    
    # Get trading signal from strategy
    signal = await strategy.generate_signal()
    
    if signal is None:
        return None
    
    print(f"Signal: {signal.side.value} {signal.quantity} {signal.symbol} @ {signal.price}")
    
    try:
        # 1. Create order
        order = await order_mgr.create_order(
            exchange_type=signal.exchange,
            order_type=signal.order_type,
            side=signal.side,
            symbol=signal.symbol,
            quantity=signal.quantity,
            limit_price=signal.price
        )
        
        # 2. Submit order
        success = await order_mgr.submit_order(order)
        if not success:
            print(f"Order submission failed")
            return None
        
        # 3. Wait for fill
        max_wait = 60  # seconds
        start = asyncio.get_event_loop().time()
        
        while order.status != OrderStatus.FILLED:
            if asyncio.get_event_loop().time() - start > max_wait:
                print(f"Order timeout, cancelling...")
                await order_mgr.cancel_order(order.order_id)
                return None
            
            await asyncio.sleep(0.5)
        
        # 4. Open position
        position = await position_mgr.open_position(
            exchange_type=signal.exchange,
            symbol=signal.symbol,
            side=signal.side,
            entry_price=order.price.average_fill_price,
            quantity=order.quantity.filled_quantity,
            stop_loss_price=signal.stop_loss,
            take_profit_price=signal.take_profit
        )
        
        print(f"✓ Position opened: {position.position_id}")
        return position
    
    except Exception as e:
        print(f"✗ Pipeline error: {e}")
        return None
```

### 2. Multi-Symbol Monitoring

```python
async def monitor_multiple_symbols(order_monitor, portfolio_monitor, 
                                   symbols: List[str], interval_seconds=1):
    """Monitor orders and portfolio across multiple symbols"""
    
    while True:
        try:
            # Get portfolio snapshot
            portfolio_snapshot = await portfolio_monitor.take_snapshot()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Portfolio value: ${portfolio_snapshot.portfolio_value:.2f}")
            
            # Check each symbol exposure
            for symbol in symbols:
                exposure = portfolio_monitor.portfolio_mgr.get_symbol_exposure(symbol)
                print(f"  {symbol}: ${exposure:.2f}")
            
            # Check order status changes
            order_changes = await order_monitor.check_status_updates()
            for order, old_status, new_status in order_changes:
                print(f"  Order {order.order_id}: {old_status.value} → {new_status.value}")
            
            await asyncio.sleep(interval_seconds)
        
        except Exception as e:
            print(f"Monitoring error: {e}")
            await asyncio.sleep(interval_seconds)
```

---

## Next Steps

1. **Read full API documentation**: [API Reference](PHASE5_STAGE3_API_REFERENCE.md)
2. **Understand architecture**: [Architecture Guide](PHASE5_STAGE3_ARCHITECTURE.md)
3. **Run tests**: `pytest src/tests/test_phase5_*.py -v`
4. **Build your strategy**: Use these APIs to implement your trading logic
5. **Deploy to production**: See deployment checklist in architecture guide

---

## Support & Resources

- **API Reference**: Full method documentation
- **Architecture Guide**: System design and patterns
- **Test Suite**: Real-world usage examples (src/tests/test_phase5_*.py)
- **Code**: Well-documented source code in src/phase5/

---

**Start trading with Phase 5 Stage 3 - Order Management System!**
