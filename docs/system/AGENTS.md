# AGENTS.md - Development Guide for Comic AI

This guide provides essential information for agentic coding agents working in the Comic AI repository.

## Quick Commands

### Build & Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup conda environment (if using conda)
conda env update --file environment.yml --name base
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest src/tests/ktzen_test.py

# Run with verbose output
pytest -v

# Run single test function
pytest src/tests/ktzen_test.py::test_environment -v
```

### Linting & Code Quality
```bash
# Lint with flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127

# Check syntax errors
python -m py_compile <file.py>
```

### Running Code
```bash
# Run main CLI
python src/cli/cli.py

# Run environment test
python src/tests/ktzen_test.py

# Run demo systems
python demo_singularity_system.py
python demo_singularity_simple.py
```

## Project Structure

```
/root/comic_ai/
├── src/
│   ├── cli/           # Command-line interfaces
│   ├── core/          # Core modules (trading, singularity systems)
│   ├── plugins/       # Plugin system
│   ├── tests/         # Test files
│   └── utils/         # Utility functions
├── engine/            # Quantum & ML engines
├── optimizer/         # Optimization modules
├── dashboard/         # Web dashboard (Flask)
├── config/            # YAML configuration files
├── data/              # Data management & agents
└── scripts/           # Deployment & utility scripts
```

## Code Style Guidelines

### Imports
- Order: standard library → third-party → local modules
- Use absolute imports from project root (e.g., `from src.core.module import Class`)
- Group related imports together

```python
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple, Any
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

import numpy as np
import yaml
import logging
```

### Formatting
- **Line Length**: Max 127 characters (per flake8 config)
- **Indentation**: 4 spaces (no tabs)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Use triple-quoted docstrings for modules, classes, and functions

```python
def analyze_market_quantum(self, market_data: Dict[str, Any]) -> Dict[str, float]:
    """Analyze market data using quantum algorithms.
    
    Args:
        market_data: Dictionary containing market information
        
    Returns:
        Dictionary with quantum analysis results
    """
```

### Type Hints
- Always use type hints for function parameters and returns
- Use `from typing import` for complex types: Dict, List, Optional, Tuple, Any, Callable
- Use dataclasses for data structures

```python
def process_data(
    values: List[float],
    multiplier: int = 1,
    cache: Optional[Dict[str, Any]] = None
) -> Tuple[np.ndarray, float]:
    """Process input values."""
```

### Classes
- Use dataclasses for simple data structures: `@dataclass`
- Use Enum for enumerations
- Class methods document with docstrings
- Private methods prefix with `_`

```python
@dataclass
class MarketSignal:
    """Market trading signal."""
    symbol: str
    signal_type: str
    confidence: float
    timestamp: datetime

class TradingStrategy(Enum):
    """Enumeration of trading strategies."""
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
```

### Error Handling
- Use try/except blocks for known failure points
- Log errors with `logging` module
- Provide context in error messages

```python
try:
    result = risky_operation()
except ValueError as e:
    logging.error(f"Invalid value in operation: {e}")
    return None
except Exception as e:
    logging.exception(f"Unexpected error: {e}")
    raise
```

### Naming Conventions
- **Functions/Variables**: `snake_case` (e.g., `analyze_market_quantum`)
- **Classes**: `PascalCase` (e.g., `QuantumMarketAnalyzer`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ITERATIONS`)
- **Private**: Leading underscore (e.g., `_calculate_quantum_resonance`)

### Documentation
- Module docstrings at the top of file
- Chinese comments allowed (project uses both English & Chinese)
- Use emoji for status indicators (✅, ❌, 📦, 🧪, etc.)

```python
#!/usr/bin/env python3
"""
Module name in English
模組中文名稱 (Chinese translation)
"""
```

### Common Patterns

**Async functions** (used for system components):
```python
async def initialize_system(self) -> None:
    """Initialize the trading system."""
    await self._setup_components()
```

**Configuration loading** (YAML):
```python
def _load_config(self, config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    with open(config_path) as f:
        return yaml.safe_load(f)
```

**Logging setup**:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Message")
```

## Key Technologies

- **Python 3.10+** (per GitHub Actions workflow)
- **NumPy/SciPy**: Numerical & scientific computing
- **Qiskit**: Quantum computing
- **PyYAML**: Configuration management
- **Semantic Kernel**: Multi-agent systems
- **Flask**: Web dashboard
- **Pytest**: Testing framework
- **Flake8**: Linting

## Git Workflow

- Use meaningful commit messages
- Keep commits focused on single features/fixes
- Prefix commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`

## Important Notes

- Project uses both English and Chinese in comments/documentation
- Focus areas: quantum computing, trading systems, multi-agent AI
- Core quantitative components in `engine/` and `src/core/`
- Tests must pass: `pytest` before deployment

## Common File Types

- **YAML configs**: `engine_config.yaml`, `dashboard_config.yaml`, `*.control.yaml`
- **Python tests**: `src/tests/*.py`
- **Demo files**: `demo_*.py` for quick feature testing
- **Requirements**: `requirements.txt` (pip) and `environment.yml` (conda)

