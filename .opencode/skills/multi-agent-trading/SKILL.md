---
name: multi-agent-trading
description: Integrate and manage multi-agent trading system with LogManager
license: MIT
compatibility: opencode
metadata:
  audience: developers
  categories:
    - trading
    - multi-agent
    - logging
  version: 1.0.0
  tags:
    - agents
    - signals
    - risk-management
    - coordination
---

## What I do

- Integrate LogManager logging into multi-agent trading system
- Set up signal analysis agents with comprehensive event logging
- Configure risk management with automated alerts
- Enable multi-agent coordination with decision tracking
- Generate trading reports and performance metrics
- Monitor portfolio state changes in real-time

## When to use me

Use this skill when:
- Setting up a new multi-agent trading system
- Adding logging to existing trading agents
- Debugging trading decisions and agent interactions
- Monitoring risk violations and portfolio changes
- Analyzing trading performance and metrics
- Creating automated trading reports

## Key Features

### Automatic Logging Integration
```python
from src.core.logging_integration import LogManager, LogConfig
from src.plugins.multi_agent_trading import SignalAnalysisAgent

# Just 3 lines to enable full logging!
config = LogConfig(log_dir="logs")
log_manager = LogManager(config)
agent = SignalAnalysisAgent(log_manager=log_manager)
```

### Event Types
- **Signal Events**: SMA crossovers, RSI signals, technical analysis
- **Risk Events**: Position limits, emergency exits, loss thresholds
- **Decision Events**: Trading decisions with confidence and rationale
- **Coordination Events**: Agent voting, consensus decisions
- **Portfolio Events**: State changes, P&L tracking, rebalancing

### Log Files
- `logs/trading_agents.log` - Agent analysis and operations
- `logs/trading_decisions.log` - Trading signals and decisions
- `logs/trading_portfolio.log` - Portfolio state changes
- `logs/trading_risk.log` - Risk warnings and alerts

## Files Reference

- **Main Integration**: `src/plugins/multi_agent_trading.py`
- **Examples**: `MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES.py`
- **Documentation**: `MULTI_AGENT_TRADING_LOGGING_README.md`
- **Tests**: `test_multi_agent_logging_integration.py`

## Quick Start

1. **Initialize LogManager**:
   ```python
   from src.core.logging_integration import LogManager, LogConfig
   config = LogConfig(log_dir="logs", log_level=logging.INFO)
   log_manager = LogManager(config)
   ```

2. **Create Agents with Logging**:
   ```python
   signal_agent = SignalAnalysisAgent(log_manager=log_manager)
   risk_agent = RiskManagementAgent(log_manager=log_manager)
   ```

3. **Setup Coordinator**:
   ```python
   coordinator = MultiAgentCoordinator(log_manager=log_manager)
   coordinator.register_agent(signal_agent)
   coordinator.register_agent(risk_agent)
   ```

4. **Execute with Full Logging**:
   ```python
   decision = coordinator.coordinate_decisions(market_data, portfolio)
   ```

## Supported Agents

- **SignalAnalysisAgent** - Technical analysis and signal generation
- **RiskManagementAgent** - Risk monitoring and mitigation
- **PortfolioManagementAgent** - Portfolio allocation and rebalancing
- **MultiAgentCoordinator** - Decision aggregation and consensus

## Related Skills

- `logging-system` - Core LogManager logging framework
- `git-release` - Automated release management
