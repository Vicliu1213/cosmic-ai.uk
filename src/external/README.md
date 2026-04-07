# 統一交易系統 - 快速入門指南

統一交易系統（Unified Trading System）是一個多 Bot 集成框架，允許你在同一個儀表板上管理和切換多個交易 Bot。

## 架構概覽

```
┌─────────────────────────────────────────────┐
│     Unified Trading System Dashboard        │
│  (統一儀表板 - 多 Bot 管理和監控)           │
└─────────────────────────────────────────────┘
           ↓↓↓
┌─────────────────────────────────────────────┐
│         BotManager                          │
│  (統一管理所有 Bot 實例)                     │
├──────┬──────────┬──────────┬───────────────┤
│      │          │          │               │
↓      ↓          ↓          ↓               ↓
Hummingbot  LLM-TradeBot  MarketBot   Custom Bot
```

## 系統特性

### 1. 統一的 Bot 介面
所有 Bot（Hummingbot、LLM-TradeBot、MarketBot）都實現統一的 `TradingBot` 基類，提供一致的 API：
- `connect()` - 連接
- `disconnect()` - 斷開
- `execute_signal()` - 執行交易信號
- `get_position()` - 取得持倉
- `cancel_order()` - 取消訂單
- `get_status()` - 取得狀態

### 2. 集中化 Bot 管理
`BotManager` 提供：
- 多 Bot 註冊和管理
- 統一的信號路由
- Bot 切換和激活控制
- 性能指標聚合
- 風險管理

### 3. 儀表板和 API
Web 儀表板提供：
- 實時 Bot 狀態監控
- Bot 性能對比
- 交易信號執行
- 一鍵 Bot 切換
- WebSocket 實時更新

### 4. 配置管理系統
集中化配置管理：
- YAML 配置文件
- 環境變數支持
- 配置驗證
- 持久化存儲

## 快速開始

### 1. 初始化系統

```bash
cd /workspaces/cosmic-ai.uk
python -m src.external.init_trading_system --setup
```

這會創建配置文件結構：
```
config/trading_system/
├── system_config.json      # 系統配置
├── bots_config.yaml        # Bot 配置
├── system_config.example.json
└── bots_config.example.yaml
```

### 2. 配置 Bot

編輯 `config/trading_system/bots_config.yaml`：

```yaml
Hummingbot-1:
  bot_type: hummingbot
  enabled: true
  config_data:
    host: localhost
    port: 8000
  risk_limit: 1000.0
  max_concurrent_trades: 10

LLM-TradeBot-1:
  bot_type: llm_tradebot
  enabled: true
  config_data: {}
  risk_limit: 500.0
  max_concurrent_trades: 5

MarketBot-1:
  bot_type: marketbot
  enabled: true
  config_data: {}
  risk_limit: 2000.0
  max_concurrent_trades: 20
```

### 3. 啟動儀表板

```bash
python -m src.external.init_trading_system --dashboard --port 8000
```

訪問：http://localhost:8000/api/docs

### 4. 運行測試

```bash
python -m src.external.init_trading_system --test
```

### 5. 交互式 Shell

```bash
python -m src.external.init_trading_system --shell
```

## API 文檔

### Bot 管理 API

#### 取得 Bot 列表
```
GET /api/bots
```

響應：
```json
{
  "bots": [
    {
      "name": "Hummingbot-1",
      "type": "hummingbot",
      "enabled": true,
      "connected": true,
      "status": "running"
    }
  ],
  "active_bot": "Hummingbot-1"
}
```

#### 取得 Bot 狀態
```
GET /api/bots/{bot_name}/status
```

#### 連接 Bot
```
POST /api/bots/{bot_name}/connect
```

#### 斷開 Bot
```
POST /api/bots/{bot_name}/disconnect
```

#### 切換活躍 Bot
```
POST /api/bots/{bot_name}/switch
```

#### 取得 Bot 指標
```
GET /api/bots/{bot_name}/metrics
```

### 儀表板 API

#### 取得儀表板數據
```
GET /api/dashboard
```

響應包含：
- 系統指標（總交易、PnL、勝率等）
- 所有 Bot 信息和狀態
- 活躍 Bot

#### 取得系統指標
```
GET /api/metrics
```

#### 取得所有 Bot 指標
```
GET /api/metrics/all-bots
```

### 交易信號 API

#### 執行交易信號
```
POST /api/signals/execute?bot_name={bot_name}

{
  "signal_id": "SIG_001",
  "signal_type": "buy",
  "symbol": "BTC/USDT",
  "quantity": 1.0,
  "confidence": 0.8
}
```

#### 取得執行歷史
```
GET /api/executions?limit=50
```

### WebSocket API

#### 實時更新
```
WS /ws/updates
```

客戶端可以發送命令：
```json
// 取得儀表板數據
{
  "command": "get_dashboard"
}

// 切換 Bot
{
  "command": "switch_bot",
  "bot_name": "LLM-TradeBot-1"
}

// 執行信號
{
  "command": "execute_signal",
  "signal": {
    "signal_id": "SIG_001",
    "signal_type": "buy",
    "symbol": "BTC/USDT",
    "quantity": 1.0
  },
  "bot_name": "Hummingbot-1"
}
```

## Python 代碼示例

### 基礎使用

```python
from src.external import (
    get_bot_manager, 
    get_config_manager,
    TradingSignal, 
    SignalType
)
import asyncio

async def main():
    # 初始化配置
    config_manager = get_config_manager()
    config_manager.load_all()
    
    # 初始化 Bot 管理器
    bot_manager = get_bot_manager()
    config_manager.apply_to_bot_manager(bot_manager)
    
    # 連接所有 Bot
    await bot_manager.connect_all()
    
    # 查看 Bot 列表
    bots = bot_manager.get_bot_list()
    print(f"Available bots: {bots}")
    
    # 切換活躍 Bot
    bot_manager.switch_active_bot("Hummingbot-1")
    
    # 創建交易信號
    signal = TradingSignal(
        signal_id="SIG_001",
        signal_type=SignalType.BUY,
        symbol="BTC/USDT",
        quantity=1.0,
        confidence=0.8
    )
    
    # 執行信號
    execution = await bot_manager.execute_signal(signal)
    print(f"Execution: {execution.status}")
    
    # 獲取系統指標
    metrics = bot_manager.get_system_metrics()
    print(f"Total trades: {metrics['total_trades']}")
    print(f"Total PnL: ${metrics['total_pnl']}")
    
    # 斷開所有 Bot
    await bot_manager.disconnect_all()

# 運行
asyncio.run(main())
```

### 創建自定義 Bot

```python
from src.external import TradingBot, BotConfig, BotType, TradeExecution

class CustomBot(TradingBot):
    """自定義交易 Bot"""
    
    async def connect(self) -> bool:
        # 實現連接邏輯
        self.is_connected = True
        return True
    
    async def disconnect(self) -> bool:
        # 實現斷開邏輯
        self.is_connected = False
        return True
    
    async def execute_signal(self, signal) -> TradeExecution:
        # 實現信號執行邏輯
        execution = TradeExecution(
            execution_id=f"EXEC_{datetime.now().timestamp()}",
            signal_id=signal.signal_id,
            bot_name=self.config.bot_name,
            bot_type=BotType.CUSTOM,
            status="EXECUTED"
        )
        return execution
    
    async def get_position(self, symbol: str):
        # 實現取得持倉邏輯
        return {"symbol": symbol, "quantity": 0.0}
    
    async def cancel_order(self, order_id: str) -> bool:
        # 實現取消訂單邏輯
        return True
    
    async def get_status(self) -> dict:
        # 實現取得狀態邏輯
        return {"status": "running"}

# 使用自定義 Bot
config = BotConfig(
    bot_name="Custom-Bot-1",
    bot_type=BotType.CUSTOM
)

bot = CustomBot(config)
```

### 儀表板集成

```python
from src.external import create_dashboard_app
import uvicorn

# 創建儀表板應用
app = create_dashboard_app()

# 啟動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 文件結構

```
src/external/
├── __init__.py
├── unified_trading_system.py    # 核心系統 (BotManager, Bot 實現)
├── config_manager.py             # 配置管理系統
├── unified_dashboard.py           # 儀表板和 API
├── init_trading_system.py         # 初始化腳本
├── README.md                      # 此文件
└── hummingbot_integration_layer.py  # (來自 src/core)
```

## 監控和維護

### 日誌
系統使用 Python 標準 logging。在 `init_trading_system.py` 配置日誌級別。

### 性能指標
每個 Bot 追蹤：
- 總交易次數
- 勝率
- 總 PnL（利潤/損失）
- 平均每筆交易 PnL
- 最後更新時間

### 風險管理
- 每個 Bot 有每日風險限制 (`risk_limit`)
- 最多並發交易數限制 (`max_concurrent_trades`)
- 執行超時設置 (`timeout`)
- 重試次數限制 (`retry_attempts`)

## 常見問題

### Q: 如何添加新的 Bot？
A: 
1. 建立新的配置條目在 `bots_config.yaml`
2. 實現 `TradingBot` 基類（如果是自定義 Bot）
3. 通過 API 或 Python 代碼註冊 Bot

### Q: 如何在多個 Bot 上同時執行信號？
A: 使用 `execute_signal_multi_bot()` 方法：
```python
results = await bot_manager.execute_signal_multi_bot(
    signal,
    bot_names=["Bot1", "Bot2", "Bot3"]
)
```

### Q: 儀表板支持自定義樣式嗎？
A: 當前版本提供 RESTful API，可以構建自定義前端。

### Q: 如何備份和恢復配置？
A: 配置文件存儲在 `config/trading_system/` 目錄，可以直接備份 YAML 和 JSON 文件。

## 技術支持

有問題？
1. 查看日誌輸出
2. 運行 `python -m src.external.init_trading_system --test`
3. 檢查 API 端點狀態：`GET /api/health`

## 許可證

MIT License
