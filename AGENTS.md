# AGENTS.md - Developer Guide for Cosmic AI

Quick reference for agents working in this repository.

## Essential Commands

```bash
# Install dependencies
pip install -r requirements.txt
conda env update --file environment.yml --name base

# Run all tests
pytest

# Run specific test file
pytest src/tests/test_risk_audit_agent.py -v

# Single test function
pytest src/tests/test_risk_audit_agent.py::test_function_name -v

# Lint (this repo uses these tools)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
black --line-length=127 .
isort --profile=black --line-length=127 .
mypy --ignore-missing-imports .

# Type check
mypy src/ --ignore-missing-imports
```

## Project Architecture

- **`src/`** - Main application code (CLI, core modules, tests)
- **`cosmic_engine/`** - Quantum computing engine & biological systems
- **`config/`** - YAML configuration files
- **`docs/`** - Documentation
- **`agents/`** - Multi-agent system definitions

Entry points vary - check README.md for the specific system you need.

## Key Conventions

- **Line length**: 127 chars max (flake8 config)
- **Python**: 3.10+ (3.12 in pre-commit)
- **Testing**: pytest, some tests require specific fixtures or services
- **Language**: English + Chinese in comments/docs (both accepted)
- **Import order**: stdlib → third-party → local (use isort)

## Order of Operations

When modifying code:
1. `flake8` → `mypy` → `pytest` (run in this order)
2. Before commit: `pre-commit run --all-files`

## Test Locations

Tests are spread across multiple directories:
- `src/tests/` - Core tests
- `src/marketbot/tests/` - Market bot tests
- `src/tests/legacy/` - Legacy tests
- `src/tests/phase_tests/` - Phase-specific tests
- `src/tests/integration/` - Integration tests
- `cosmic_engine/tests/` - Engine tests

## Important Files

- `README.md` - System overview
- `.pre-commit-config.yaml` - Pre-commit hooks
- `requirements.txt` - pip dependencies
- `environment.yml` - conda dependencies
- `.env` - Environment variables (secret, don't commit)

## Environment Setup

This repo uses `.env` for environment variables. Copy from template:
```bash
cp .env.example .env
`` ｜

Required API keys (get from exchange dashboards):
- `OPENAI_API_KEY` - OpenAI GPT access
- `BINANCE_API_KEY` / `BINANCE_SECRET_KEY` - Binance futures
- `BITGET_API_KEY` / `BITGET_SECRET_KEY` - Bitget trading
- `BYBIT_API_KEY` / `BYBIT_SECRET` - Bybit
- `OKX_API_KEY` / `OKX_SECRET_KEY` - OKX
- `QISKIT_IBM_TOKEN` - IBM Quantum (optional)

## Git Commit Prefixes

Use: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
