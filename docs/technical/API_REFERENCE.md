# API 参考手册

Cosmic AI 提供多种 API 接口用于系统集成和扩展。

## 目录

- [REST API](#rest-api)
- [Python API](#python-api)
- [WebSocket API](#websocket-api)
- [外部 API 集成](#外部-api-集成)

## REST API

### 基础信息

- **基础 URL**: `http://localhost:8000/api/v1`
- **认证**: Bearer Token 或 API Key
- **响应格式**: JSON

### 核心端点

#### 交易端点

```
POST /api/v1/trades
GET /api/v1/trades/{trade_id}
GET /api/v1/trades/history
PUT /api/v1/trades/{trade_id}
DELETE /api/v1/trades/{trade_id}
```

#### 市场数据端点

```
GET /api/v1/market/price/{symbol}
GET /api/v1/market/indicators/{symbol}
GET /api/v1/market/history/{symbol}
```

#### 系统端点

```
GET /api/v1/system/status
GET /api/v1/system/health
POST /api/v1/system/restart
```

## Python API

### 导入核心模块

```python
from src.engine import HybridEngine
from src.models import TradeSignal
from src.algorithms import QuantumOptimizer
```

### 基本使用示例

```python
# 初始化引擎
engine = HybridEngine()
engine.initialize()

# 获取市场数据
market_data = engine.fetch_market_data('BTC/USDT')

# 计算交易信号
signal = engine.generate_signal(market_data)

# 执行交易
trade = engine.execute_trade(signal)
```

详见: [MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES.py](MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES.py)

## WebSocket API

### 连接

```python
import asyncio
import websockets

async def connect():
    async with websockets.connect('ws://localhost:8000/ws') as websocket:
        await websocket.send('{"action": "subscribe", "channel": "trades"}')
        async for message in websocket:
            print(message)

asyncio.run(connect())
```

### 事件类型

- `trade_created` - 交易创建
- `trade_updated` - 交易更新
- `trade_closed` - 交易关闭
- `market_alert` - 市场警告

## 外部 API 集成

### Gemini API

参考: [GEMINI_API_INTEGRATION_GUIDE.md](GEMINI_API_INTEGRATION_GUIDE.md)

### Vertex AI

参考: [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md)

### Hummingbot API

参考: [ETHANALGOX_HUMMINGBOT_INTEGRATION_GUIDE.md](ETHANALGOX_HUMMINGBOT_INTEGRATION_GUIDE.md)

## 错误处理

### 常见错误代码

| 代码 | 描述 |
|------|------|
| 400 | 请求格式错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 未找到 |
| 500 | 服务器错误 |

### 错误响应示例

```json
{
  "error": "Invalid request",
  "code": 400,
  "message": "Missing required field: symbol"
}
```

## 版本信息

当前版本: v1.0.0
最后更新: 2026-04-05
