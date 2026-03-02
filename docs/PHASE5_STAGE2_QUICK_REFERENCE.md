# Phase 5 Stage 2 - Quick Reference Guide
## API密鑰配置快速參考

**Quick Links**: 
- [Full Documentation](./PHASE5_STAGE2_API_CONFIGURATION_COMPLETE.md)
- [Setup Guide](#setup-in-3-steps)
- [Testing](#test-api-connections)

---

## 📦 What's Included

### 3 New Modules (2,100+ lines)

1. **Exchange Connector** (`src/phase5/exchange_connector.py`)
   - Binance, Kraken, Coinbase connectors
   - Rate limiting, error handling
   - Multi-exchange support

2. **API Configuration** (`src/phase5/api_configuration.py`)
   - .env loading and validation
   - YAML configuration management
   - Environment variable substitution

3. **Connectivity Tests** (`scripts/test_api_connectivity.py`)
   - 7 test categories
   - 14+ individual tests
   - JSON report generation

---

## Setup in 3 Steps

### Step 1: Copy Templates (1 minute)

```bash
cp .env.template .env
cp config/trading_config_template.yaml config/trading_config.yaml
```

### Step 2: Add API Keys (2 minutes)

Edit `.env` with your API credentials:

```bash
# Binance Testnet: https://testnet.binance.vision/
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here

# Kraken: https://www.kraken.com/ → Settings → API
KRAKEN_API_KEY=your_key_here
KRAKEN_API_SECRET=your_secret_here

# Optional: Coinbase (can enable later)
# COINBASE_API_KEY=your_key_here
# COINBASE_API_SECRET=your_secret_here
```

### Step 3: Configure Exchanges (1 minute)

Edit `config/trading_config.yaml`:

```yaml
system:
  mode: "sandbox"  # Use sandbox for testing
  start_capital: 500

exchanges:
  binance:
    enabled: true
    testnet: true
    sandbox: true
  
  kraken:
    enabled: true
    sandbox: true
```

---

## Test API Connections

```bash
# Run full connectivity test suite
python scripts/test_api_connectivity.py
```

Expected output:
```
✅ Exchange Manager initialized
✅ Basic Connectivity - BINANCE & KRAKEN
✅ Authentication - API keys validated
✅ Balance Retrieval - Accounts loaded
✅ Rate Limiting - Active
✅ Error Handling - Working
✅ Performance - Response times < 200ms

📊 TEST SUMMARY
Total Tests: 14
✅ Passed: 14
❌ Failed: 0
🎯 Success Rate: 100.0%
```

---

## Usage Examples

### Example 1: Connect to Binance

```python
from src.phase5.exchange_connector import (
    ExchangeConfig, ExchangeType, TradingMode, ExchangeConnectorFactory
)

config = ExchangeConfig(
    exchange_type=ExchangeType.BINANCE,
    api_key="your_key",
    api_secret="your_secret",
    mode=TradingMode.TESTNET,
    testnet=True
)

async with ExchangeConnectorFactory.create(config) as connector:
    result = await connector.test_connection()
    balance = await connector.get_balance()
    print(f"Balance: ${balance.total_balance}")
```

### Example 2: Multi-Exchange Manager

```python
from src.phase5.api_configuration import setup_api_configuration

# Initialize all configured exchanges
manager = await setup_api_configuration()

# Connect to all
results = await manager.connect_all()

# Get all balances
balances = await manager.get_all_balances()
for exchange_type, balance in balances.items():
    print(f"{exchange_type.value}: ${balance.total_balance}")

# Cleanup
manager.disconnect_all()
```

### Example 3: Validation

```python
from src.phase5.api_configuration import APIConfigurationManager

manager = APIConfigurationManager()
manager.load_environment()
manager.load_configuration()

validation = manager.validate_all()
manager.print_summary()

if validation.status.value == "valid":
    print("✅ Configuration valid - ready to trade!")
else:
    print(f"❌ Configuration error: {validation.message}")
```

---

## File Locations

```
Project Root
├── .env                           ← Add your API keys here
├── config/
│   ├── trading_config.yaml       ← Exchange configuration
│   ├── trading_config_template.yaml
│   └── .env.template             ← Copy to .env
├── src/phase5/
│   ├── exchange_connector.py      ← 1,000+ lines
│   ├── api_configuration.py       ← 500+ lines
│   └── trading_system_init.py
├── scripts/
│   ├── test_api_connectivity.py   ← 600+ lines
│   └── enhanced_validate_environment.py
└── reports/
    └── api_connectivity_tests.json ← Test results
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing API Key" | Copy `.env.template` → `.env`, add your keys |
| "ModuleNotFoundError" | Set `export PYTHONPATH=/workspaces/cosmic-ai.uk` |
| "Connection timeout" | Check internet, verify exchange APIs are online |
| "Invalid signature" | Verify API secret (no extra spaces) |
| "Rate limited" | Wait 60 seconds, system handles automatically |

---

## Key Classes

### BaseExchangeConnector
All exchange connectors inherit from this base class:

```python
async def test_connection() -> ConnectionResult
async def get_balance() -> AccountBalance
async def check_rate_limit() -> bool
async def wait_for_rate_limit() -> None
```

### BinanceConnector, KrakenConnector, CoinbaseConnector
Exchange-specific implementations with custom authentication.

### MultiExchangeManager
Manages multiple exchange connections simultaneously:

```python
def add_exchange(config: ExchangeConfig)
async def connect_all() -> Dict[ExchangeType, bool]
async def get_all_balances() -> Dict[ExchangeType, AccountBalance]
def disconnect_all()
```

### APIConfigurationManager
Loads and validates configurations:

```python
def load_environment() -> bool
def load_configuration() -> bool
async def initialize_exchange_manager() -> MultiExchangeManager
def validate_all() -> ValidationResult
```

---

## Next Steps

1. **Setup API Keys** → Complete the 3-step setup above
2. **Run Tests** → Verify connections work
3. **Integrate with Phase 1-4** → Use in your trading strategies
4. **Monitor Performance** → Track response times and success rates

---

## Support

**For detailed information**: See [PHASE5_STAGE2_API_CONFIGURATION_COMPLETE.md](./PHASE5_STAGE2_API_CONFIGURATION_COMPLETE.md)

**Exchange APIs**:
- Binance: https://binance-docs.github.io/apidocs/
- Kraken: https://docs.kraken.com/rest/
- Coinbase: https://docs.cloud.coinbase.com/

**Status**: ✅ Production Ready  
**Code Quality**: 100% type hints, complete documentation

