# Testing Documentation README

## Overview

Comprehensive test suite for the Cosmic AI trading system. Tests are organized into logical categories for better maintainability and clarity.

宇宙AI交易系統的綜合測試套件。測試按邏輯分類組織，便於維護和理解。

## 📁 新的目錄結構 (2026-04-07)

```
src/tests/
├── unit/              # 3 個單元測試 - 基本功能測試
├── integration/       # 9 個集成測試 - 模組互動測試  
├── e2e/              # 2 個端到端測試 - 完整流程測試
├── phase_tests/      # 5 個階段驗證 - 開發階段測試
├── specialized/      # 9 個專門領域測試 - 深度功能測試
├── backtesting/      # 6 個回測測試 - 策略回測
├── demos/            # 2 個演示代碼 - 示例程序
├── legacy/           # 5 個遺留測試 - 需要維護的舊測試
├── fixtures/         # 共用測試數據
└── README.md         # 本文檔
```

## Test Suite Structure

### test_utils.py
Tests for utility functions and helpers.
- DateTime utilities
- Numeric operations
- String utilities
- Collection utilities
- File operations
- Logging functionality

### test_api.py
Tests for REST API endpoints.
- Health check endpoint
- API status endpoint
- Portfolio endpoint
- Trading signals endpoint
- Market data endpoint
- Error handling
- Authentication

### test_optimizers.py
Tests for optimization algorithms.
- Genetic algorithm
- Particle swarm optimization
- Simulated annealing
- Gradient descent
- Differential evolution
- Objective functions

### test_trading.py
Tests for trading components and multi-agent system.
- Trading decisions
- Portfolio state tracking
- Market data structures
- Portfolio management agent
- Risk management agent
- Signal analysis agent
- Multi-agent coordinator
- Decision history

## 🚀 快速執行命令

### Run All Tests (運行所有測試)
```bash
pytest src/tests/ -v
```

### Run by Category (按分類運行)
```bash
pytest src/tests/unit/              # 運行所有單元測試
pytest src/tests/integration/       # 運行所有集成測試
pytest src/tests/e2e/              # 運行所有 E2E 測試
pytest src/tests/phase_tests/      # 運行所有階段測試
pytest src/tests/specialized/      # 運行所有專門測試
pytest src/tests/backtesting/      # 運行所有回測測試
```

### Run Specific Test File (運行特定檔案)
```bash
pytest src/tests/unit/test_utils.py -v
pytest src/tests/unit/test_api.py -v
pytest src/tests/specialized/test_optimizers.py -v
pytest src/tests/specialized/test_trading.py -v
```

### Run Specific Test Class
```bash
pytest src/tests/test_trading.py::TestPortfolioManagementAgent -v
```

### Run Specific Test Method
```bash
pytest src/tests/test_trading.py::TestPortfolioManagementAgent::test_agent_initialization -v
```

### Run with Coverage
```bash
pytest src/tests/ --cov=src --cov-report=html
```

## Test Categories

### Utility Tests (test_utils.py)

#### DateTime Tests
- Parsing various date formats
- ISO format conversion
- Timestamp handling

#### Numeric Tests
- Basic arithmetic operations
- Percentage calculations
- Floating-point precision

#### String Tests
- Formatting and interpolation
- Parsing delimited strings
- Unicode handling

#### Collection Tests
- Dictionary operations
- List manipulations
- Sorting and filtering

#### File Tests
- File existence checking
- Path operations
- Temporary file handling

#### Logging Tests
- Logger creation and configuration
- Log levels
- Error logging

### API Tests (test_api.py)

#### Health Check Endpoint
- Response structure validation
- Status field verification
- Timestamp presence

#### API Status
- Version information
- System state tracking
- Agent counts

#### Portfolio Endpoints
- Portfolio structure validation
- P&L calculations
- Position tracking

#### Trading Signals
- Signal data structure
- Confidence levels
- Signal type validation

#### Market Data
- Price bid-ask validation
- Volume verification
- Timestamp accuracy

#### Error Handling
- 404 Not Found responses
- 400 Bad Request handling
- 500 Server Error responses

### Optimizer Tests (test_optimizers.py)

#### Genetic Algorithm
- Population initialization
- Fitness calculations
- Mutation operations
- Crossover mechanisms

#### Particle Swarm Optimization
- Particle initialization
- Velocity updates
- Position updates
- Convergence tracking

#### Simulated Annealing
- Temperature scheduling
- Acceptance probability
- Cooling rate testing

#### Gradient Descent
- Gradient calculations
- Parameter updates
- Convergence criteria

#### Differential Evolution
- Mutation vector generation
- Crossover operations
- Population evolution

### Trading Tests (test_trading.py)

#### Trading Decision
- Decision creation
- Serialization to dict
- Decision validation

#### Portfolio State
- Portfolio creation
- State tracking
- Serialization

#### Market Data
- Data structure validation
- Indicator storage
- Price relationships

#### Portfolio Management Agent
- Agent initialization
- Analysis capability
- Decision generation

#### Risk Management Agent
- Position size validation
- Loss limit checking
- Risk scoring

#### Signal Analysis Agent
- SMA signal detection
- RSI signal detection
- Indicator interpretation

#### Multi-Agent Coordinator
- Coordinator initialization
- Agent registration/unregistration
- Decision coordination
- Consensus mechanisms

#### Decision History
- Decision recording
- History retrieval
- History limits

## Test Coverage Goals

| Module | Target Coverage |
|--------|-----------------|
| utils | >95% |
| api | >90% |
| optimizers | >85% |
| trading | >90% |
| data | >85% |

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Nightly builds

Run CI tests locally:
```bash
./scripts/run_tests.sh
```

## Test Data

Mock data used in tests:

### Stock Symbols
- AAPL: Apple Inc.
- MSFT: Microsoft Corporation
- GOOGL: Alphabet Inc.

### Price Ranges
- AAPL: $150-152
- MSFT: $300-302
- GOOGL: $140-142

### Portfolio Values
- Default: $250,000
- Small: $50,000
- Large: $1,000,000

## Debugging Tests

### Enable Verbose Output
```bash
pytest -vv src/tests/test_trading.py
```

### Show Print Statements
```bash
pytest -s src/tests/test_trading.py
```

### Drop to Debugger
```python
import pdb; pdb.set_trace()
```

### Use pytest fixtures
```bash
pytest --fixtures src/tests/
```

## Writing New Tests

Template for new test class:
```python
import unittest

class TestNewFeature(unittest.TestCase):
    """Test new feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize test data
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_something(self):
        """Test something specific."""
        # Arrange
        expected = 5
        
        # Act
        result = 2 + 3
        
        # Assert
        self.assertEqual(result, expected)
```

## Common Test Patterns

### Testing with Mock Objects
```python
from unittest.mock import Mock, patch

def test_with_mock(self):
    mock_agent = Mock()
    mock_agent.analyze.return_value = decision
```

### Testing Exceptions
```python
def test_exception(self):
    with self.assertRaises(ValueError):
        risky_operation()
```

### Testing Properties
```python
def test_property(self):
    obj = MyClass()
    self.assertEqual(obj.property, expected_value)
```

## Performance Testing

For performance-critical code:
```bash
pytest --benchmark src/tests/test_performance.py
```

## Test Maintenance

- Update tests when requirements change
- Add tests for new features before implementation (TDD)
- Remove obsolete tests
- Keep test data realistic
- Document complex test logic

## Troubleshooting

### Import Errors
Ensure PYTHONPATH includes project root:
```bash
export PYTHONPATH=/root/comic_ai:$PYTHONPATH
```

### Test Failures
1. Check recent code changes
2. Verify test data is correct
3. Look for environment-specific issues
4. Run tests in isolation

### Slow Tests
1. Identify slow tests: `pytest --durations=10`
2. Optimize or split slow tests
3. Use mocks for external calls

## Related Documentation

- `AGENTS.md`: Development guide
- `README.md`: Project overview
- Test files themselves for implementation details

## Contact

For test-related issues, refer to the development guide or create a test issue.
