# LLM-TradeBot Cosmic Panel 集成指南

## 📋 概述

本面版集成了 **LLM-TradeBot** 的多代理交易系統與 **Cosmic AI** 的量子優化交易引擎，提供統一的實時監控、控制和分析界面。

### 核心特性

- 🤖 **多代理監控**: 實時監控 Trend、Setup、Trigger、Reflection、Risk 5 個代理
- 📡 **Cosmic 信號集成**: 展示 Cosmic 系統的交易信號和性能指標
- 📊 **實時指標**: 展示 Sharpe 比率、勝率、PnL、回撤等關鍵指標
- 🎮 **控制面板**: 一鍵啟動、暫停、停止、重置交易系統
- 🔌 **WebSocket 實時更新**: 實時推送代理狀態、信號和指標變化
- 🌐 **多語言**: 支援繁體中文和英文

---

## 🏗️ 系統架構

### 層級結構

```
┌─────────────────────────────────────┐
│    前端 UI (index.html)              │
│  - 儀表板、圖表、控制面板            │
├─────────────────────────────────────┤
│    API 服務器 (main.py)             │
│  - FastAPI + WebSocket              │
│  - REST 端點 + 實時推送              │
├─────────────────────────────────────┤
│    統一橋接層 (bridge.py)           │
│  - LLMTradeBotBridge               │
│  - CosmicSignalBridge              │
│  - UnifiedPanelBridge              │
├─────────────────────────────────────┤
│  LLM-TradeBot        Cosmic AI      │
│  (決策層)            (優化層)       │
└─────────────────────────────────────┘
```

### 數據流

```
Cosmic 系統           LLM-TradeBot
   │                      │
   ├─ 信號 ──────────────┤
   ├─ 指標 ──────────────┤
   └─ 套利機會 ────────────┤
                          │
                   橋接層
                    │
                API 服務器
                 /    \
               REST   WebSocket
                 \    /
                前端界面
```

---

## 🚀 快速啟動

### 1. 安裝依賴

```bash
pip install fastapi uvicorn websockets aiohttp
```

### 2. 啟動面版服務器

```bash
# 進入面版目錄
cd /workspaces/cosmic-ai.uk/src/integrations/dashboard

# 啟動服務器
python main.py
```

或使用自定義端口：

```bash
PORT=8888 python main.py
```

### 3. 訪問面版

打開瀏覽器訪問：

```
http://localhost:8000
```

---

## 📡 API 端點

### 健康檢查

**GET** `/api/health`

```bash
curl http://localhost:8000/api/health
```

響應示例：

```json
{
  "status": "healthy",
  "timestamp": "2026-03-03T10:30:45.123456",
  "components": {
    "llm_bridge": "connected",
    "cosmic_bridge": "connected",
    "websocket_clients": 5
  }
}
```

### 獲取代理摘要

**GET** `/api/agents/summary`

```bash
curl http://localhost:8000/api/agents/summary
```

響應示例：

```json
{
  "total_agents": 5,
  "agents": {
    "TrendAgent": {
      "agent_name": "TrendAgent",
      "agent_type": "Trend",
      "status": "running",
      "confidence": 0.85,
      "last_signal": "UPTREND",
      "last_update": "2026-03-03T10:30:45.123456",
      "performance_metrics": {
        "win_rate": 0.72,
        "avg_profit": 250.5,
        "sharpe_ratio": 2.3,
        "max_drawdown": -0.08
      }
    }
  },
  "timestamp": "2026-03-03T10:30:45.123456"
}
```

### 更新代理狀態

**POST** `/api/agents/{agent_name}/update`

```bash
curl -X POST http://localhost:8000/api/agents/TrendAgent/update \
  -H "Content-Type: application/json" \
  -d '{
    "status": "running",
    "confidence": 0.92,
    "last_signal": "STRONG_UPTREND"
  }'
```

### 獲取 Cosmic 信號

**GET** `/api/signals/cosmic?limit=20`

```bash
curl http://localhost:8000/api/signals/cosmic
```

響應示例：

```json
{
  "total": 20,
  "signals": [
    {
      "signal_id": "sig_001",
      "symbol": "BTC/USDT",
      "signal_type": "BUY",
      "sharpe_ratio": 2.8,
      "confidence": 0.95,
      "quantum_score": 0.88,
      "timestamp": "2026-03-03T10:30:45.123456",
      "resonance_level": 0.91
    }
  ],
  "timestamp": "2026-03-03T10:30:45.123456"
}
```

### 添加 Cosmic 信號

**POST** `/api/signals/cosmic`

```bash
curl -X POST http://localhost:8000/api/signals/cosmic \
  -H "Content-Type: application/json" \
  -d '{
    "signal_id": "sig_002",
    "symbol": "ETH/USDT",
    "signal_type": "SELL",
    "sharpe_ratio": 2.5,
    "confidence": 0.88,
    "quantum_score": 0.85
  }'
```

### 獲取交易指標

**GET** `/api/metrics/trading`

```bash
curl http://localhost:8000/api/metrics/trading
```

### 控制交易系統

#### 啟動交易

**POST** `/api/control/start`

```bash
curl -X POST http://localhost:8000/api/control/start
```

#### 停止交易

**POST** `/api/control/stop`

```bash
curl -X POST http://localhost:8000/api/control/stop
```

#### 暫停交易

**POST** `/api/control/pause`

```bash
curl -X POST http://localhost:8000/api/control/pause
```

#### 重置系統

**POST** `/api/control/reset`

```bash
curl -X POST http://localhost:8000/api/control/reset
```

---

## 🔌 WebSocket 實時更新

### 連接 WebSocket

```javascript
// 自動連接 (前端會自動處理)
const ws = new WebSocket('ws://localhost:8000/ws/live-updates');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'metrics_update') {
        updateMetrics(data.data);
    } else if (data.type === 'cosmic_signal') {
        addSignal(data.data);
    } else if (data.type === 'agent_update') {
        updateAgent(data.data);
    }
};
```

### 消息類型

| 類型 | 用途 | 數據結構 |
|------|------|--------|
| `metrics_update` | 交易指標更新 | `{...TradingMetrics}` |
| `cosmic_signal` | 新 Cosmic 信號 | `{...CosmicSignal}` |
| `agent_update` | 代理狀態更新 | `{...AgentState}` |
| `system_event` | 系統事件 | `{event: 'started'\|'stopped'\|'paused'\|'reset'}` |
| `initial_state` | 初始連接狀態 | `{...UnifiedState}` |

---

## 🔧 配置

### 環境變量

```bash
# 服務器配置
HOST=0.0.0.0
PORT=8000

# LLM-TradeBot 路徑
LLM_TRADEBOT_PATH=/workspaces/cosmic-ai.uk/external/llm_tradebot

# Cosmic AI 路徑
COSMIC_PATH=/workspaces/cosmic-ai.uk/src
```

### 配置文件

在 `/workspaces/cosmic-ai.uk/src/integrations/dashboard/` 目錄下創建 `.env` 文件：

```bash
HOST=0.0.0.0
PORT=8000
LLM_TRADEBOT_PATH=/workspaces/cosmic-ai.uk/external/llm_tradebot
COSMIC_PATH=/workspaces/cosmic-ai.uk/src
```

---

## 📊 前端界面

### 儀表板布局

1. **頂部標題區**
   - 系統狀態指示器
   - 實時連接狀態

2. **控制面板**
   - ▶ 開始交易
   - ⏸ 暫停
   - ⏹ 停止
   - 🔄 重置
   - 🔃 刷新數據

3. **交易指標卡**
   - 總交易數
   - 勝率
   - 總 PnL
   - Sharpe 比率
   - 最大回撤
   - 當前餘額

4. **代理狀態卡**
   - 5 個代理卡片
   - 實時狀態指示
   - 信心度百分比
   - 最後更新時間

5. **信號列表**
   - Cosmic 系統的最近信號
   - BUY/SELL 信號顏色區分
   - 滾動查看歷史信號

---

## 💡 使用示例

### Python 客戶端示例

```python
import asyncio
import aiohttp
from datetime import datetime

async def main():
    async with aiohttp.ClientSession() as session:
        # 健康檢查
        async with session.get('http://localhost:8000/api/health') as resp:
            print(await resp.json())
        
        # 獲取代理摘要
        async with session.get('http://localhost:8000/api/agents/summary') as resp:
            print(await resp.json())
        
        # 添加信號
        signal = {
            "signal_id": "test_001",
            "symbol": "BTC/USDT",
            "signal_type": "BUY",
            "sharpe_ratio": 2.8,
            "confidence": 0.95,
            "quantum_score": 0.88
        }
        
        async with session.post(
            'http://localhost:8000/api/signals/cosmic',
            json=signal
        ) as resp:
            print(await resp.json())

asyncio.run(main())
```

### 更新指標

```python
metrics = {
    "timestamp": datetime.now().isoformat(),
    "total_trades": 42,
    "win_rate": 0.72,
    "total_pnl": 1250.50,
    "sharpe_ratio": 2.5,
    "max_drawdown": -0.08,
    "current_balance": 11250.50,
    "active_positions": 2,
    "average_trade_duration": 45.5
}

async with session.post(
    'http://localhost:8000/api/metrics/trading',
    json=metrics
) as resp:
    print(await resp.json())
```

---

## 🔧 故障排除

### 問題：無法連接到面版

**解決方案**：
1. 檢查服務器是否運行：`ps aux | grep main.py`
2. 檢查端口是否被佔用：`lsof -i :8000`
3. 檢查防火牆設置

### 問題：WebSocket 連接失敗

**解決方案**：
1. 確保使用正確的協議（ws:// 或 wss://）
2. 檢查是否在代理後面
3. 確保 FastAPI 版本 ≥ 0.68

### 問題：代理狀態不更新

**解決方案**：
1. 檢查是否通過 API 更新了狀態
2. 確保 WebSocket 連接活躍
3. 檢查瀏覽器控制台是否有錯誤

---

## 📈 性能優化

### 建議配置

| 設置項 | 推薦值 | 說明 |
|--------|--------|------|
| 工作進程數 | 4 | CPU 核心數 |
| 數據刷新間隔 | 5 秒 | 前端自動刷新 |
| 信號保留數量 | 100 | 內存限制 |
| WebSocket 超時 | 60 秒 | 連接保活 |

### 監控

```bash
# 查看服務器日誌
tail -f /tmp/panel.log

# 監控系統資源
watch -n 1 "ps aux | grep main.py"
```

---

## 🚀 生產部署

### Docker 運行

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### 運行容器

```bash
docker build -t llm-tradebot-panel .
docker run -p 8000:8000 \
  -e PORT=8000 \
  -e HOST=0.0.0.0 \
  llm-tradebot-panel
```

### Kubernetes 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-tradebot-panel
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: panel
        image: llm-tradebot-panel:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
```

---

## 📚 相關文件

| 文件 | 用途 |
|------|------|
| `main.py` | FastAPI 服務器啟動入口 |
| `llm_tradebot_panel.py` | 面版核心應用 |
| `bridge.py` | 橋接層實現 |
| `index.html` | 前端界面 |
| `__init__.py` | 模塊初始化 |

---

## 📞 支援

如有問題或建議，請：

1. 檢查 API 文檔
2. 查看日誌文件
3. 測試 API 端點
4. 提交 Issue

---

**版本**: 1.0.0  
**最後更新**: 2026-03-03  
**狀態**: 🟢 生產就緒
