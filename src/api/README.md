# API Module README

## Overview

The API module provides REST API endpoints for the Comic AI trading system, enabling external applications to interact with the trading engine, monitor system status, and retrieve market data and signals.

API 模塊為 Comic AI 交易系統提供 REST API 端點，使外部應用程式能夠與交易引擎交互、監控系統狀態並檢索市場數據和信號。

## Module Purpose

This module provides:
- Health check and system status endpoints
- Portfolio management and monitoring
- Trading signal retrieval
- Market data access
- Real-time system updates
- Error handling and validation

## Key Endpoints

### Health Check
**GET** `/health`

Check API and system health status.

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-02-13T12:00:00",
  "version": "2.0.0",
  "environment": "production"
}
```

### API Status
**GET** `/api/status`

Get comprehensive API status information.

```bash
curl http://localhost:5000/api/status
```

Response:
```json
{
  "api_version": "2.0.0",
  "active_systems": 3,
  "active_agents": 12,
  "timestamp": "2024-02-13T12:00:00",
  "uptime": 3600
}
```

### Get Portfolio
**GET** `/api/portfolio`

Retrieve current portfolio state.

```bash
curl http://localhost:5000/api/portfolio
```

Response:
```json
{
  "cash": 50000.0,
  "total_value": 250000.0,
  "unrealized_pnl": 5000.0,
  "realized_pnl": 1000.0,
  "positions": {
    "AAPL": 100,
    "MSFT": 50,
    "GOOGL": 25
  },
  "timestamp": "2024-02-13T12:00:00"
}
```

### Get Trading Signals
**GET** `/api/signals`

Retrieve recent trading signals from all agents.

Query Parameters:
- `limit` (int): Maximum number of signals (default: 100)
- `symbol` (str): Filter by symbol (optional)

```bash
curl http://localhost:5000/api/signals?limit=50&symbol=AAPL
```

Response:
```json
{
  "signals": [
    {
      "symbol": "AAPL",
      "signal_type": "buy",
      "confidence": 0.85,
      "price": 150.75,
      "timestamp": "2024-02-13T12:00:00",
      "agent_id": "sa_agent_1",
      "reason": "SMA crossover"
    }
  ],
  "total": 15
}
```

### Get Market Data
**GET** `/api/market/<symbol>`

Retrieve current market data for a symbol.

```bash
curl http://localhost:5000/api/market/AAPL
```

Response:
```json
{
  "symbol": "AAPL",
  "price": 150.75,
  "bid": 150.70,
  "ask": 150.80,
  "volume": 1000000,
  "timestamp": "2024-02-13T12:00:00",
  "change": 1.25,
  "change_percent": 0.84
}
```

### Execute Trade
**POST** `/api/trade`

Execute a trade order.

Request Body:
```json
{
  "symbol": "AAPL",
  "type": "buy",
  "quantity": 10,
  "price": 150.75,
  "order_type": "market"
}
```

Response:
```json
{
  "order_id": "ORD_001",
  "symbol": "AAPL",
  "type": "buy",
  "quantity": 10,
  "executed_price": 150.76,
  "status": "executed",
  "timestamp": "2024-02-13T12:00:00"
}
```

### Get Agent Status
**GET** `/api/agents`

Retrieve status of all registered agents.

```bash
curl http://localhost:5000/api/agents
```

Response:
```json
{
  "agents": [
    {
      "agent_id": "pm_agent_1",
      "role": "portfolio_manager",
      "status": "active",
      "decisions_made": 150,
      "last_decision": "2024-02-13T12:00:00"
    },
    {
      "agent_id": "rm_agent_1",
      "role": "risk_manager",
      "status": "active",
      "decisions_made": 200,
      "last_decision": "2024-02-13T12:00:00"
    }
  ],
  "total": 3
}
```

## Usage Examples

### Example 1: Monitor System Health

```bash
#!/bin/bash

# Check health every 60 seconds
while true; do
    curl -s http://localhost:5000/health | jq .
    sleep 60
done
```

### Example 2: Retrieve Recent Signals

```python
import requests
import json

# Get trading signals
response = requests.get(
    'http://localhost:5000/api/signals',
    params={'limit': 50, 'symbol': 'AAPL'}
)

signals = response.json()
for signal in signals['signals']:
    print(f"{signal['timestamp']}: {signal['signal_type']} {signal['symbol']}")
    print(f"  Confidence: {signal['confidence']}")
    print(f"  Reason: {signal['reason']}")
```

### Example 3: Monitor Portfolio

```python
import requests
import time

while True:
    response = requests.get('http://localhost:5000/api/portfolio')
    portfolio = response.json()
    
    print(f"Portfolio Value: ${portfolio['total_value']:.2f}")
    print(f"Cash: ${portfolio['cash']:.2f}")
    print(f"Unrealized P&L: ${portfolio['unrealized_pnl']:.2f}")
    
    # Print top positions
    for symbol, quantity in sorted(portfolio['positions'].items()):
        print(f"  {symbol}: {quantity} shares")
    
    time.sleep(5)
```

### Example 4: Execute Trade

```python
import requests

# Buy 10 shares of AAPL at market price
trade_request = {
    "symbol": "AAPL",
    "type": "buy",
    "quantity": 10,
    "order_type": "market"
}

response = requests.post(
    'http://localhost:5000/api/trade',
    json=trade_request
)

order = response.json()
print(f"Order {order['order_id']} executed at ${order['executed_price']}")
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing authentication |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Server Error | Internal error |

### Error Response Format

```json
{
  "error": "Invalid symbol provided",
  "code": "INVALID_SYMBOL",
  "status": 400,
  "timestamp": "2024-02-13T12:00:00"
}
```

### Handling Errors in Python

```python
import requests

try:
    response = requests.get('http://localhost:5000/api/signals')
    response.raise_for_status()  # Raise for HTTP errors
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
except requests.exceptions.ConnectionError:
    print("Connection Error: Could not connect to API")
```

## Authentication

API endpoints may require authentication tokens:

```python
headers = {
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'Content-Type': 'application/json'
}

response = requests.get(
    'http://localhost:5000/api/portfolio',
    headers=headers
)
```

## Rate Limiting

Recommended request rates:
- Health check: 1 request/minute
- Portfolio: 1 request/minute
- Signals: 1 request/minute
- Market data: 1 request/minute

## WebSocket Support

For real-time updates, connect to WebSocket endpoint:

```python
import websocket

def on_message(ws, message):
    print(f"Received: {message}")

ws = websocket.WebSocketApp(
    "ws://localhost:5000/api/stream",
    on_message=on_message
)

ws.run_forever()
```

## Configuration

API configuration in `config/api_config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 5000
  debug: false

security:
  enable_auth: true
  require_https: true

rate_limiting:
  enabled: true
  requests_per_minute: 100

cors:
  enabled: true
  origins:
    - http://localhost:3000
    - https://example.com
```

## Deployment

### Local Development
```bash
python src/api/server.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.api.server:app
```

### Docker
```bash
docker run -p 5000:5000 comic_ai_api
```

## Testing API Endpoints

### Using curl
```bash
curl -X GET http://localhost:5000/health
curl -X GET http://localhost:5000/api/portfolio
curl -X POST http://localhost:5000/api/trade -d '{"symbol":"AAPL","type":"buy","quantity":10}'
```

### Using Postman
1. Import API collection
2. Set environment variables
3. Run requests
4. View responses

### Using Python requests
```bash
pytest src/tests/test_api.py -v
```

## Logging

API requests are logged with:
- Timestamp
- HTTP method
- Endpoint path
- Response status
- Response time
- Error details

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Metrics

Typical response times:
- Health check: <10ms
- Portfolio: <50ms
- Signals: <100ms
- Market data: <50ms

## Related Modules

- `src/plugins/multi_agent_trading.py`: Trading agents
- `data/__init__.py`: Market data
- `src/tests/test_api.py`: API tests

## Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [REST API Best Practices](https://restfulapi.net/)
- Project AGENTS.md

## License

Part of Comic AI trading system
