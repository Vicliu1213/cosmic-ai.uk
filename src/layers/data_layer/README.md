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

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
