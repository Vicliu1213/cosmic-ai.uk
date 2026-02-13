# Data Processing Utilities README

## Overview

The Data Processing Utilities module provides comprehensive functionality for market data handling, including loading from various formats, validation, caching, and feature extraction for technical analysis.

數據處理工具模塊提供全面的市場數據處理功能，包括從各種格式加載、驗證、緩存和特徵提取，用於技術分析。

## Module Purpose

This module provides:
- **DataLoader**: Load market data from CSV and JSON files
- **DataValidator**: Validate data quality and integrity
- **DataCache**: Cache historical data to optimize I/O
- **FeatureExtractor**: Calculate technical indicators

## Key Classes and Functions

### DataLoader

Load market data from various file formats.

```python
from data import DataLoader, DataPoint

loader = DataLoader()

# Load from CSV
csv_data = loader.load_csv(
    filepath='data/market_data.csv',
    symbol='AAPL',
    date_column='date',
    close_col='close'
)

# Load from JSON
json_data = loader.load_json(
    filepath='data/market_data.json',
    symbol='MSFT'
)
```

### DataValidator

Validate data quality and integrity.

```python
from data import DataValidator

validator = DataValidator()

is_valid, report = validator.validate(data_points)

if is_valid:
    print("Data is valid")
else:
    for issue in report['issues']:
        print(f"Issue: {issue}")
```

### DataCache

Cache data to avoid repeated file I/O.

```python
from data import DataCache

cache = DataCache(cache_dir='.cache', ttl_hours=24)

# Get from cache
cached_data = cache.get('AAPL_daily')

# Put in cache
cache.put('AAPL_daily', data_points, persist=True)

# Clear cache
cache.clear()
```

### FeatureExtractor

Calculate technical indicators.

```python
from data import FeatureExtractor

extractor = FeatureExtractor()

features = extractor.extract_features(
    data_points=data_points,
    indicators=['sma_short', 'sma_long', 'rsi', 'macd', 'volatility']
)

for feature_set in features:
    print(f"SMA Short: {feature_set.get('sma_short')}")
    print(f"RSI: {feature_set.get('rsi')}")
```

## Usage Examples

### Example 1: Complete Data Loading Pipeline

```python
from data import DataLoader, DataValidator, DataCache, FeatureExtractor

# Initialize components
loader = DataLoader()
validator = DataValidator()
cache = DataCache()
extractor = FeatureExtractor()

# Try to load from cache
data = cache.get('AAPL_daily_2024')

if data is None:
    # Load from file
    data = loader.load_csv(
        'data/aapl_daily.csv',
        symbol='AAPL'
    )
    
    # Validate
    is_valid, report = validator.validate(data)
    if not is_valid:
        print("Validation issues:", report['issues'])
    
    # Cache for future use
    cache.put('AAPL_daily_2024', data)

# Extract features
features = extractor.extract_features(
    data,
    indicators=['sma_short', 'sma_long', 'rsi']
)

print(f"Loaded {len(data)} data points with features")
```

### Example 2: CSV Data Loading with Custom Columns

```python
loader = DataLoader()

data = loader.load_csv(
    filepath='market_data.csv',
    symbol='TSLA',
    date_column='Date',
    open_col='Open',
    high_col='High',
    low_col='Low',
    close_col='Close',
    volume_col='Volume'
)

print(f"Loaded {len(data)} records for TSLA")
```

### Example 3: Data Validation and Quality Report

```python
from data import DataValidator

validator = DataValidator()
is_valid, report = validator.validate(data_points)

print(f"Total points: {report['total_points']}")
print(f"Valid points: {report['valid_points']}")

if report['statistics']:
    stats = report['statistics']
    print(f"Price range: {stats['price_range']}")
    print(f"Average price: {stats['avg_price']:.2f}")
    print(f"Std deviation: {stats['std_price']:.4f}")
```

### Example 4: Technical Indicator Calculation

```python
extractor = FeatureExtractor()

features = extractor.extract_features(
    data_points,
    indicators=[
        'sma_short',     # 20-period SMA
        'sma_long',      # 50-period SMA
        'rsi',           # Relative Strength Index
        'macd',          # MACD indicator
        'volatility'     # Standard deviation
    ]
)

# Access features
for i, feature in enumerate(features[-5:]):  # Last 5
    print(f"Date: {feature['timestamp']}")
    if 'sma_short' in feature:
        print(f"  SMA(20): {feature['sma_short']:.2f}")
    if 'rsi' in feature:
        print(f"  RSI: {feature['rsi']:.4f}")
```

## Configuration

### DataCache Configuration

```python
cache = DataCache(
    cache_dir='.cache',        # Directory for cache files
    ttl_hours=24,              # Time to live in hours
    max_cache_size=1000        # Maximum entries
)
```

### FeatureExtractor Indicators

Supported technical indicators:
- `sma_short`: Short-term Simple Moving Average (default 20)
- `sma_long`: Long-term Simple Moving Average (default 50)
- `rsi`: Relative Strength Index
- `macd`: MACD and signal line
- `volatility`: Standard deviation

## Data Structures

### DataPoint
```python
@dataclass
class DataPoint:
    timestamp: datetime    # Date/time of data
    symbol: str           # Trading symbol
    open_price: float     # Opening price
    high_price: float     # High price
    low_price: float      # Low price
    close_price: float    # Closing price
    volume: float         # Trading volume
```

## Supported File Formats

### CSV Format
```csv
date,open,high,low,close,volume
2024-01-15,150.00,151.50,149.75,150.50,1000000
2024-01-16,150.50,152.00,150.25,151.75,1100000
```

### JSON Format
```json
{
  "data": [
    {
      "timestamp": "2024-01-15",
      "open": 150.00,
      "high": 151.50,
      "low": 149.75,
      "close": 150.50,
      "volume": 1000000
    }
  ]
}
```

## Validation Rules

Data is validated for:
- Non-negative prices
- High ≥ Low
- Close within High-Low range
- Non-negative volume
- Chronological order
- Valid symbols

## Caching Strategy

- **Memory Cache**: Fast access for recent data
- **Disk Cache**: Persistent storage with MD5 hashing
- **TTL-based Expiration**: Automatic cleanup of old data
- **LRU Eviction**: Oldest entries removed when max size reached

## Performance Characteristics

| Operation | Time | Space |
|-----------|------|-------|
| Load CSV (1000 rows) | ~50ms | ~100KB |
| Validate (1000 points) | ~10ms | ~10KB |
| Extract features | ~20ms | ~50KB |
| Cache lookup | <1ms | ~1KB |

## Error Handling

All methods include error handling:

```python
try:
    data = loader.load_csv(filepath)
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid data: {e}")
```

## Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('data')
```

## Date Format Support

Supported date formats:
- YYYY-MM-DD
- YYYY-MM-DD HH:MM:SS
- MM/DD/YYYY
- DD/MM/YYYY
- YYYY/MM/DD
- Unix timestamp (int/float)

## Technical Indicators Explained

### SMA (Simple Moving Average)
Average price over N periods. Used to identify trends.

### RSI (Relative Strength Index)
Range 0-1 measuring momentum. Values <0.3 indicate oversold, >0.7 overbought.

### MACD (Moving Average Convergence Divergence)
Relationship between two EMAs. Signals trend changes.

### Volatility
Standard deviation of prices. Higher values indicate more price variation.

## Related Modules

- `src/plugins/multi_agent_trading.py`: Uses extracted features for trading signals
- `optimizer/`: Classical algorithms for optimization
- `src/api/server.py`: REST API integration
- `src/tests/test_trading.py`: Unit tests

## Performance Tips

1. Use caching for frequently accessed data
2. Batch load data when possible
3. Extract only needed indicators
4. Pre-validate data on import
5. Use appropriate TTL for cache

## License

Part of Comic AI trading system
