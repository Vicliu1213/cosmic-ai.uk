# Data Layer

This layer is a compliant market-data acquisition core.

## Included sources
- ccxt exchange aggregator
- rss news feeds
- onchain public data
- regulatory filings

## Policy
- public / licensed / compliant sources only
- third-party connectors may be added only when compliant and auditable

## Run
```python
from src.layers.data_layer import build_default_data_pipeline
print(build_default_data_pipeline().run())
```
