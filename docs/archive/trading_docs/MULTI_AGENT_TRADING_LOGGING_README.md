# Multi-Agent Trading System - LogManager Integration

## Overview

This guide explains how to integrate the **LogManager** logging system with the **Multi-Agent Trading System** to enable comprehensive event logging for trading operations.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Integration Architecture](#integration-architecture)
3. [Key Components](#key-components)
4. [Usage Examples](#usage-examples)
5. [Logging Events](#logging-events)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Integration (3 Steps)

```python
from src.core.logging_integration import LogManager, LogConfig
from src.plugins.multi_agent_trading import (
    SignalAnalysisAgent, RiskManagementAgent,
    MultiAgentCoordinator, MarketData, PortfolioState
)

# Step 1: Initialize LogManager
config = LogConfig(log_dir="logs", log_level=logging.INFO)
log_manager = LogManager(config)

# Step 2: Create agents with LogManager
signal_agent = SignalAnalysisAgent(
    agent_id="signal_1",
    log_manager=log_manager  # Pass LogManager here
)

risk_agent = RiskManagementAgent(
    agent_id="risk_1",
    log_manager=log_manager
)

# Step 3: Create coordinator and start trading
coordinator = MultiAgentCoordinator(
    coordinator_id="main",
    log_manager=log_manager
)
coordinator.register_agent(signal_agent)
coordinator.register_agent(risk_agent)

# Now all trading operations are automatically logged!
final_decision = coordinator.coordinate_decisions(market_data, portfolio)
```

### View Logs

```bash
# Interactive dashboard
python logging_dashboard.py

# View specific log file
tail -f logs/trading_decisions.log

# Search for events
grep "[ERROR]" logs/trading_agents.log
```

---

## Integration Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────┐
│     Application Layer (Agents)          │
│  - SignalAnalysisAgent                  │
│  - RiskManagementAgent                  │
│  - PortfolioManagementAgent             │
│  - MultiAgentCoordinator                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Transport Layer (LogManager)        │
│  - Event logging                        │
│  - Log rotation                         │
│  - Multi-logger management              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Storage Layer (Log Files)           │
│  - logs/trading_agents.log              │
│  - logs/trading_decisions.log           │
│  - logs/trading_portfolio.log           │
│  - logs/trading_risk.log                │
└─────────────────────────────────────────┘
```

### LogManager Initialization

```python
log_manager = LogManager(config)

# Creates dedicated loggers for different aspects
log_manager.create_logger(
    name="trading.agents",
    level=logging.INFO,
    filename="logs/trading_agents.log"
)

log_manager.create_logger(
    name="trading.decisions",
    level=logging.INFO,
    filename="logs/trading_decisions.log"
)

log_manager.create_logger(
    name="trading.portfolio",
    level=logging.INFO,
    filename="logs/trading_portfolio.log"
)

log_manager.create_logger(
    name="trading.risk",
    level=logging.WARNING,
    filename="logs/trading_risk.log"
)
```

---

## Key Components

### 1. BaseAgent

**Modified to support LogManager:**

```python
class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        confidence_threshold: float = 0.6,
        log_manager: Optional[Any] = None  # NEW PARAMETER
    ):
        # ... existing code ...
        self.log_manager = log_manager
        self.event_logger = None
        if log_manager:
            self.event_logger = log_manager.get_logger("trading.agents")
```

**Automatic logging on decision:**

```python
def record_decision(self, decision: TradingDecision) -> None:
    """Record decision with optional event logging."""
    self.decision_history.append(decision)
    
    # Logs to centralized event logger if available
    if self.event_logger:
        self.event_logger.info(
            f"[DECISION_RECORDED] Agent: {decision.agent_id} | "
            f"Type: {decision.decision_type.value} | "
            f"Symbol: {decision.symbol} | "
            f"Qty: {decision.quantity:.2f} | "
            f"Confidence: {decision.confidence:.2%}"
        )
```

### 2. SignalAnalysisAgent

**Trading signals are automatically logged:**

```python
signal_agent = SignalAnalysisAgent(
    agent_id="signal_1",
    log_manager=log_manager
)

# Automatically logs:
# [NO_INDICATORS] AAPL: No indicators available
# [SMA_CHECK] AAPL | Short: 151.00 | Long: 148.00
# [SMA_SIGNAL_BUY] AAPL: Bullish crossover detected
# [RSI_SIGNAL_SELL] AAPL: Overbought condition (RSI: 0.75)
```

### 3. RiskManagementAgent

**Risk events are logged with appropriate severity:**

```python
risk_agent = RiskManagementAgent(
    agent_id="risk_1",
    log_manager=log_manager,
    max_position_size=0.1
)

# Automatically logs:
# [RISK_CHECK] AAPL | Position: $50000.00 | Max: $10000.00
# [POSITION_LIMIT_EXCEEDED] AAPL: $50000.00 > $10000.00
# [EMERGENCY_EXIT] Portfolio loss 5.00% exceeds limit 2.00%
```

### 4. MultiAgentCoordinator

**Coordination decisions are logged with full details:**

```python
coordinator = MultiAgentCoordinator(
    coordinator_id="main",
    log_manager=log_manager
)

# Automatically logs:
# [COORDINATION_START] Symbol: AAPL | Agents: 3 | Portfolio: $100000.00
# [DECISIONS_COLLECTED] 3 decision(s) collected
# [COORDINATION_COMPLETE] Symbol: AAPL | Final decision: BUY | Confidence: 75.00%
# [AGENT_DECISION] signal_1: BUY | Confidence: 75.00% | Rationale: SMA crossover
```

---

## Usage Examples

### Example 1: Basic Setup with Logging

```python
from src.core.logging_integration import LogManager, LogConfig
from src.plugins.multi_agent_trading import (
    SignalAnalysisAgent, RiskManagementAgent,
    MultiAgentCoordinator, MarketData, PortfolioState
)
import logging

# Initialize LogManager
config = LogConfig(
    log_dir="logs",
    log_level=logging.INFO,
    max_bytes=10485760,  # 10 MB
    backup_count=5
)
log_manager = LogManager(config)

# Create agents with logging
signal_agent = SignalAnalysisAgent(
    agent_id="signal_analyst_1",
    log_manager=log_manager
)

risk_agent = RiskManagementAgent(
    agent_id="risk_manager_1",
    log_manager=log_manager
)

# Create coordinator
coordinator = MultiAgentCoordinator(
    coordinator_id="coordinator_1",
    log_manager=log_manager
)

coordinator.register_agent(signal_agent)
coordinator.register_agent(risk_agent)

# Trade with automatic logging
portfolio = PortfolioState(
    positions={"AAPL": 100},
    cash=50000.0,
    total_value=100000.0
)

market_data = MarketData(
    symbol="AAPL",
    price=150.0,
    volume=1000000.0,
    bid=149.95,
    ask=150.05,
    timestamp=datetime.now(),
    indicators={'sma_short': 151.0, 'sma_long': 148.0, 'rsi': 0.65}
)

final_decision = coordinator.coordinate_decisions(market_data, portfolio)
```

### Example 2: Portfolio Tracking

```python
from MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES import PortfolioStateTracker

tracker = PortfolioStateTracker(log_manager)

# Initial state
portfolio = PortfolioState(total_value=100000.0, cash=50000.0)
tracker.track_state_change(portfolio, "initialization")

# After trading
portfolio.total_value = 105000.0
portfolio.cash = 45000.0
tracker.track_state_change(portfolio, "signal_execution")
# Logs: [PORTFOLIO_UPDATE] Trigger: signal_execution | Value: $105000.00 (change: +$5000.00)
```

### Example 3: Custom Event Logging

```python
# Get trading logger
trading_logger = log_manager.get_logger("trading.agents")

# Log custom events
trading_logger.info("[CUSTOM_EVENT] Market analysis started")
trading_logger.warning("[CUSTOM_WARNING] High volatility detected")
trading_logger.error("[CUSTOM_ERROR] Data connection lost")

# Get decision logger
decision_logger = log_manager.get_logger("trading.decisions")
decision_logger.info("[CUSTOM_DECISION] Manual override applied")
```

---

## Logging Events

### Agent Initialization

```
[AGENT_INIT] Agent: signal_analyst_1 | Role: signal_analyst | Confidence threshold: 0.60
[AGENT_INIT] Agent: risk_manager_1 | Role: risk_manager | Confidence threshold: 0.60
[COORDINATOR_INIT] Coordinator initialized: coordinator_1
```

### Signal Detection

```
[NO_INDICATORS] AAPL: No indicators available
[SMA_CHECK] AAPL | Short: 151.00 | Long: 148.00
[SMA_SIGNAL_BUY] AAPL: Bullish crossover detected
[SMA_SIGNAL_SELL] AAPL: Bearish crossover detected
[RSI_CHECK] AAPL | RSI: 0.65
[RSI_SIGNAL_BUY] AAPL: Oversold condition (RSI: 0.25)
[RSI_SIGNAL_SELL] AAPL: Overbought condition (RSI: 0.75)
```

### Decision Recording

```
[DECISION_RECORDED] Agent: signal_analyst_1 | Type: BUY | Symbol: AAPL | Qty: 1.00 | Confidence: 75.00% | Risk: 25.00%
[DECISION_RECORDED] Agent: risk_manager_1 | Type: HOLD | Symbol: AAPL | Qty: 0.00 | Confidence: 90.00% | Risk: 10.00%
```

### Risk Management

```
[RISK_CHECK] AAPL | Position: $50000.00 | Max: $10000.00
[POSITION_LIMIT_EXCEEDED] AAPL: $50000.00 > $10000.00
[EMERGENCY_EXIT] Portfolio loss 5.00% exceeds limit 2.00%
```

### Portfolio Updates

```
[PORTFOLIO_INIT] Total value: $100000.00 | Cash: $50000.00 | Positions: 2
[PORTFOLIO_UPDATE] Trigger: decision_execution | Value: $105000.00 (change: +$5000.00) | P&L: $5000.00
```

### Coordination

```
[COORDINATION_START] Symbol: AAPL | Agents: 2 | Portfolio: $100000.00
[DECISIONS_COLLECTED] 2 decision(s) collected
[COORDINATION_COMPLETE] Symbol: AAPL | Final decision: BUY | Confidence: 75.00% | Agent votes: BUY: 2
[AGENT_DECISION] signal_analyst_1: BUY | Confidence: 75.00% | Rationale: SMA crossover: 151.00 > 148.00
```

---

## Best Practices

### 1. Initialize LogManager at System Start

```python
# In your main application startup
def initialize_trading_system():
    config = LogConfig(log_dir="logs", log_level=logging.INFO)
    log_manager = LogManager(config)
    
    # Create and configure all agents
    # ... rest of initialization ...
    
    return log_manager
```

### 2. Pass LogManager to All Agents

```python
# Good - all agents share one LogManager
log_manager = setup_trading_logging()

signal_agent = SignalAnalysisAgent(log_manager=log_manager)
risk_agent = RiskManagementAgent(log_manager=log_manager)
coordinator = MultiAgentCoordinator(log_manager=log_manager)

# Don't do this - each agent would have separate loggers
signal_agent = SignalAnalysisAgent()  # No logging
```

### 3. Monitor Different Log Levels

```bash
# All events
tail -f logs/trading_decisions.log

# Only warnings and errors
grep -E "^\[WARNING\]|\[ERROR\]|\[CRITICAL\]" logs/trading_*.log

# Specific event type
grep "\[DECISION_RECORDED\]" logs/trading_decisions.log

# Real-time search
tail -f logs/trading_decisions.log | grep "AAPL"
```

### 4. Use Dashboard for Exploration

```bash
# View stats
python logging_dashboard.py stats

# View backtest reports
python logging_dashboard.py backtest

# View daily reports
python logging_dashboard.py daily

# Interactive mode
python logging_dashboard.py
```

### 5. Archive Logs Regularly

```python
# Old logs are automatically rotated by LogManager
# Configure in LogConfig:
config = LogConfig(
    max_bytes=10485760,  # Rotate at 10 MB
    backup_count=5       # Keep 5 backup files
)
```

---

## Troubleshooting

### Issue: No logs are being created

**Solution**: Verify LogManager initialization:

```python
log_manager = LogManager(config)

# Check if loggers were created
print(log_manager.get_log_files())  # Should show log files

# Verify agent has log_manager
print(agent.event_logger)  # Should not be None
```

### Issue: Logs not appearing in expected file

**Solution**: Check logger name matches the filename:

```python
# Create logger with specific file
log_manager.create_logger(
    name="trading.decisions",
    filename="logs/trading_decisions.log"
)

# Use it in agent
agent.event_logger = log_manager.get_logger("trading.decisions")
```

### Issue: Too many log files

**Solution**: Adjust rotation settings:

```python
config = LogConfig(
    max_bytes=52428800,  # Larger: 50 MB instead of 10 MB
    backup_count=3       # Keep only 3 backups
)
```

### Issue: Sensitive data in logs

**Solution**: Use appropriate log levels:

```python
# Log non-sensitive info
self.event_logger.info(f"Decision: {decision_type}")

# Don't log sensitive data, use warning/error level
# self.event_logger.debug(f"API Key: {api_key}")  # Never do this!
```

---

## Log File Reference

| File | Purpose | Level | Contents |
|------|---------|-------|----------|
| `logs/trading_agents.log` | Agent events | INFO | Initialization, analysis, errors |
| `logs/trading_decisions.log` | Trading decisions | INFO | Signals, decisions, coordination |
| `logs/trading_portfolio.log` | Portfolio changes | INFO | State updates, P&L tracking |
| `logs/trading_risk.log` | Risk alerts | WARNING | Limits, emergencies, issues |

---

## Integration with Existing Code

### Before (Without Logging)

```python
signal_agent = SignalAnalysisAgent(agent_id="signal_1")
risk_agent = RiskManagementAgent(agent_id="risk_1")
coordinator = MultiAgentCoordinator()

coordinator.register_agent(signal_agent)
coordinator.register_agent(risk_agent)

decision = coordinator.coordinate_decisions(market_data, portfolio)
```

### After (With Logging)

```python
# Just add log_manager parameter!
log_manager = LogManager(config)

signal_agent = SignalAnalysisAgent(agent_id="signal_1", log_manager=log_manager)
risk_agent = RiskManagementAgent(agent_id="risk_1", log_manager=log_manager)
coordinator = MultiAgentCoordinator(log_manager=log_manager)

coordinator.register_agent(signal_agent)
coordinator.register_agent(risk_agent)

decision = coordinator.coordinate_decisions(market_data, portfolio)
# All operations now have comprehensive logging!
```

---

## Advanced Features

### Get Trading Statistics

```python
from MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES import get_trading_statistics

stats = get_trading_statistics(log_manager)
print(stats)  # Returns log stats, file counts, etc.
```

### Create Trading Summary

```python
from MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES import create_trading_summary

summary = create_trading_summary(log_manager)
print(summary)
```

### Query Logs

```python
# Search for specific events
results = log_manager.query_logs(
    pattern="[DECISION_RECORDED]",
    limit=10
)

# Get log statistics
stats = log_manager.get_statistics()
```

---

## Files Reference

- **Modified**: `src/plugins/multi_agent_trading.py` - Added LogManager support to all agent classes
- **Created**: `MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES.py` - Complete integration examples (700+ lines)
- **Created**: `MULTI_AGENT_TRADING_LOGGING_README.md` - This file
- **Existing**: `src/core/logging_integration.py` - Core LogManager system
- **Dashboard**: `logging_dashboard.py` - View logs and reports

---

## Summary

The Multi-Agent Trading System now has **optional, non-intrusive integration** with LogManager:

✅ **All agents support logging** - Just pass `log_manager` parameter  
✅ **Automatic event logging** - No manual logging code needed  
✅ **Backward compatible** - Works with or without LogManager  
✅ **Structured logging** - All events follow consistent format  
✅ **Easy debugging** - All operations are traceable  
✅ **Production-ready** - Log rotation, multi-level logging, etc.

**Start logging now:**

```bash
python MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES.py
python logging_dashboard.py
```
