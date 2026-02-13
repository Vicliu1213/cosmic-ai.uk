# Multi-Agent Trading System README

## Overview

The Multi-Agent Trading System is a sophisticated framework for autonomous trading using multiple intelligent agents with specialized roles. Each agent operates independently while coordinating through a central coordinator to make collective trading decisions.

多智能體交易系統是一個使用具有專門角色的多個智能智能體進行自主交易的複雜框架。每個智能體獨立運作，同時通過中央協調器進行協調以做出集體交易決策。

## Module Purpose

This module provides:
- **Agent Base Class**: Foundation for all trading agents with decision-making capabilities
- **Portfolio Management Agent**: Handles position sizing and portfolio rebalancing
- **Risk Management Agent**: Monitors and controls portfolio risk
- **Signal Analysis Agent**: Identifies trading opportunities based on technical indicators
- **Multi-Agent Coordinator**: Aggregates decisions and applies consensus mechanisms

## Key Classes and Functions

### BaseAgent

Abstract base class for all trading agents.

```python
from src.plugins.multi_agent_trading import BaseAgent, AgentRole

class CustomAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentRole.SIGNAL_ANALYST)
    
    def analyze(self, market_data, portfolio):
        # Implementation here
        pass
```

### PortfolioManagementAgent

Manages portfolio allocation and rebalancing.

```python
from src.plugins.multi_agent_trading import PortfolioManagementAgent

agent = PortfolioManagementAgent(
    agent_id='pm_agent_1',
    target_allocations={'AAPL': 0.5, 'MSFT': 0.3, 'GOOGL': 0.2},
    rebalance_threshold=0.05
)

decision = agent.analyze(market_data, portfolio)
```

### RiskManagementAgent

Enforces risk limits and position controls.

```python
from src.plugins.multi_agent_trading import RiskManagementAgent

agent = RiskManagementAgent(
    agent_id='rm_agent_1',
    max_position_size=0.1,  # 10% of portfolio
    max_portfolio_loss=0.02  # 2% max loss
)

decision = agent.analyze(market_data, portfolio)
```

### SignalAnalysisAgent

Generates trading signals from technical indicators.

```python
from src.plugins.multi_agent_trading import SignalAnalysisAgent

agent = SignalAnalysisAgent(
    agent_id='sa_agent_1',
    sma_short=20,
    sma_long=50,
    rsi_threshold=0.3
)

decision = agent.analyze(market_data, portfolio)
```

### MultiAgentCoordinator

Coordinates decisions from multiple agents using voting mechanism.

```python
from src.plugins.multi_agent_trading import MultiAgentCoordinator

coordinator = MultiAgentCoordinator()
coordinator.register_agent(pm_agent)
coordinator.register_agent(rm_agent)
coordinator.register_agent(sa_agent)

final_decision = coordinator.coordinate_decisions(
    market_data=market_data,
    portfolio=portfolio,
    voting_threshold=0.5
)
```

## Usage Examples

### Example 1: Basic Trading Decision

```python
from src.plugins.multi_agent_trading import (
    PortfolioManagementAgent,
    PortfolioState,
    MarketData
)
from datetime import datetime

# Create agent
agent = PortfolioManagementAgent()

# Prepare data
portfolio = PortfolioState(
    positions={'AAPL': 100, 'MSFT': 50},
    cash=50000.0,
    total_value=250000.0
)

market_data = MarketData(
    symbol='AAPL',
    price=150.75,
    volume=1000000,
    bid=150.70,
    ask=150.80,
    timestamp=datetime.now()
)

# Get decision
decision = agent.analyze(market_data, portfolio)
if decision:
    print(f"Decision: {decision.decision_type.value}")
    print(f"Confidence: {decision.confidence}")
```

### Example 2: Multi-Agent Coordination

```python
from src.plugins.multi_agent_trading import (
    MultiAgentCoordinator,
    PortfolioManagementAgent,
    RiskManagementAgent,
    SignalAnalysisAgent
)

# Create coordinator
coordinator = MultiAgentCoordinator()

# Register agents
coordinator.register_agent(PortfolioManagementAgent('pm_1'))
coordinator.register_agent(RiskManagementAgent('rm_1'))
coordinator.register_agent(SignalAnalysisAgent('sa_1'))

# Get coordinated decision
final_decision = coordinator.coordinate_decisions(
    market_data=market_data,
    portfolio=portfolio,
    voting_threshold=0.5
)

# Get coordination history
history = coordinator.get_coordination_history(limit=100)
```

### Example 3: Decision Recording and History

```python
agent = PortfolioManagementAgent('pm_1')

# Analyze and record decisions
decision = agent.analyze(market_data, portfolio)
if decision:
    agent.record_decision(decision)

# Retrieve decision history
history = agent.get_decision_history(limit=50)
for past_decision in history:
    print(f"{past_decision.timestamp}: {past_decision.rationale}")
```

## Configuration

### Agent Parameters

#### PortfolioManagementAgent
- `agent_id` (str): Unique identifier
- `target_allocations` (Dict[str, float]): Target portfolio weights
- `rebalance_threshold` (float): Trigger rebalance when drift exceeds this threshold

#### RiskManagementAgent
- `agent_id` (str): Unique identifier
- `max_position_size` (float): Maximum position as % of portfolio (0.1 = 10%)
- `max_portfolio_loss` (float): Maximum loss as % of portfolio (0.02 = 2%)
- `var_threshold` (float): Value at Risk confidence level (0.95 = 95%)

#### SignalAnalysisAgent
- `agent_id` (str): Unique identifier
- `sma_short` (int): Short SMA period (default: 20)
- `sma_long` (int): Long SMA period (default: 50)
- `rsi_threshold` (float): RSI threshold for signals (default: 0.3)

## Data Structures

### TradingDecision
```python
@dataclass
class TradingDecision:
    agent_id: str                    # Agent making decision
    decision_type: DecisionType      # BUY, SELL, HOLD, REBALANCE
    symbol: str                      # Trading symbol
    quantity: float                  # Number of shares
    price: float                     # Price per share
    confidence: float                # Confidence 0.0-1.0
    timestamp: datetime              # Decision time
    rationale: str                   # Reason for decision
    risk_score: float                # Associated risk
```

### PortfolioState
```python
@dataclass
class PortfolioState:
    positions: Dict[str, float]      # Holdings by symbol
    cash: float                      # Available cash
    total_value: float               # Total portfolio value
    unrealized_pnl: float            # Unrealized P&L
    realized_pnl: float              # Realized P&L
    timestamp: datetime              # State timestamp
```

### MarketData
```python
@dataclass
class MarketData:
    symbol: str                      # Trading symbol
    price: float                     # Current price
    volume: float                    # Trading volume
    bid: float                       # Bid price
    ask: float                       # Ask price
    timestamp: datetime              # Data timestamp
    indicators: Dict[str, float]     # Technical indicators
```

## Error Handling

All agents include comprehensive error handling:

```python
try:
    decision = agent.analyze(market_data, portfolio)
except Exception as e:
    logger.error(f"Error in agent analysis: {e}")
    decision = None
```

## Logging

Enable detailed logging for debugging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('src.plugins.multi_agent_trading')
```

## Advanced Features

- **Decision History**: Track all agent decisions with timestamps and rationale
- **Consensus Mechanism**: Voting-based coordination with configurable thresholds
- **Risk Scoring**: Each decision includes associated risk metrics
- **Confidence Levels**: All decisions include confidence scores
- **Audit Trail**: Complete logging of all agent activities

## Testing

Run unit tests for the trading system:

```bash
pytest src/tests/test_trading.py -v
```

## Performance Considerations

- Agents operate independently for minimal latency
- Coordination happens at the frame/tick level
- Decision history stored in memory (configurable limits)
- Suitable for real-time trading up to 1000 symbols

## Related Modules

- `data/__init__.py`: Market data loading and feature extraction
- `optimizer/`: Classical optimization algorithms
- `src/api/server.py`: REST API integration
- `src/tests/test_trading.py`: Unit tests

## License

Part of Comic AI trading system
