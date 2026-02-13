# Testing Documentation README

## Overview

Comprehensive unit tests for the Comic AI trading system covering utilities, API endpoints, optimization algorithms, and trading components.

Comic AI 交易系統的綜合單位測試，涵蓋工具程序、API 端點、優化算法和交易組件。

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

## Running Tests

### Run All Tests
```bash
pytest src/tests/ -v
```

### Run Specific Test File
```bash
pytest src/tests/test_utils.py -v
pytest src/tests/test_api.py -v
pytest src/tests/test_optimizers.py -v
pytest src/tests/test_trading.py -v
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
