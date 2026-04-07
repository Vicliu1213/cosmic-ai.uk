# 統一交易系統 - 快速參考卡

## 🎯 系統概述

統一交易系統已成功集成 3 個主要 Bot（Hummingbot、LLM-TradeBot、MarketBot）到一個統一的儀表板，支持在同一介面上進行管理和切換。

## 📁 核心模組結構

```
src/external/
├── unified_trading_system.py    ← 核心 Bot 管理器和介面
├── config_manager.py             ← 集中配置管理
├── unified_dashboard.py           ← Web 儀表板 API
├── init_trading_system.py         ← 初始化和啟動腳本
└── README.md                      ← 完整文檔
```

## 🚀 快速啟動

### 1️⃣ 初始化配置
```bash
python -m src.external.init_trading_system --setup
```

### 2️⃣ 啟動儀表板
```bash
python -m src.external.init_trading_system --dashboard --port 8000
```

### 3️⃣ 訪問儀表板
- **API 文檔**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/updates

## 🔧 核心 API 端點

### Bot 管理
| 端點 | 方法 | 功能 |
|------|------|------|
| `/api/bots` | GET | 列出所有 Bot |
| `/api/bots/{name}/status` | GET | 取得 Bot 狀態 |
| `/api/bots/{name}/switch` | POST | 切換活躍 Bot |
| `/api/bots/{name}/metrics` | GET | 取得 Bot 指標 |

### 交易系統
| 端點 | 方法 | 功能 |
|------|------|------|
| `/api/signals/execute` | POST | 執行交易信號 |
| `/api/metrics` | GET | 系統整體指標 |
| `/api/dashboard` | GET | 儀表板數據 |
| `/api/executions` | GET | 交易執行歷史 |

## 💻 Python 代碼示例

### 基礎使用
```python
from src.external import get_bot_manager, TradingSignal, SignalType
import asyncio

async def main():
    manager = get_bot_manager()
    
    # 連接所有 Bot
    await manager.connect_all()
    
    # 執行信號
    signal = TradingSignal(
        signal_id="SIG_001",
        signal_type=SignalType.BUY,
        symbol="BTC/USDT",
        quantity=1.0,
        confidence=0.8
    )
    
    execution = await manager.execute_signal(signal)
    print(f"Status: {execution.status}")

asyncio.run(main())
```

### 切換 Bot
```python
# 切換到特定 Bot
manager.switch_active_bot("LLM-TradeBot-1")

# 執行信號到新的活躍 Bot
execution = await manager.execute_signal(signal)
```

## 📊 系統指標

每個 Bot 追蹤以下指標：
- ✅ 總交易次數
- ✅ 勝率（win_rate）
- ✅ 總利潤/損失（PnL）
- ✅ 平均每筆交易利潤
- ✅ 最後更新時間

## ⚙️ 配置文件位置

```
config/trading_system/
├── system_config.json       ← 系統配置（日誌、監控間隔等）
└── bots_config.yaml         ← Bot 配置（類型、風險限制、超時等）
```

### 配置 Bot 例子
```yaml
Hummingbot-1:
  bot_type: hummingbot
  enabled: true
  config_data:
    host: localhost
    port: 8000
  risk_limit: 1000.0
  max_concurrent_trades: 10
  timeout: 30
  retry_attempts: 3
```

## 🔄 Bot 類型支持

| Bot 類型 | 狀態 | 說明 |
|---------|------|------|
| Hummingbot | ✅ | 跨交易所套利交易 |
| LLM-TradeBot | ✅ | 多代理 AI 決策系統 |
| MarketBot | ✅ | 市場監控 Bot |
| Custom | ✅ | 支持自定義實現 |

## 🎮 WebSocket 命令示例

### 取得儀表板數據
```json
{
  "command": "get_dashboard"
}
```

### 切換 Bot
```json
{
  "command": "switch_bot",
  "bot_name": "LLM-TradeBot-1"
}
```

### 執行信號
```json
{
  "command": "execute_signal",
  "signal": {
    "signal_id": "SIG_001",
    "signal_type": "buy",
    "symbol": "BTC/USDT",
    "quantity": 1.0,
    "confidence": 0.8
  },
  "bot_name": "Hummingbot-1"
}
```

## 🛡️ 風險管理特性

- **每日風險限制**: 每個 Bot 可設置最大每日損失
- **最大並發交易**: 限制同時開啟的交易數
- **執行超時**: 訂單執行的最大等待時間
- **重試機制**: 自動重試失敗的操作

## 📈 性能對比

儀表板自動追蹤並展示：
- 各 Bot 的個別表現
- 系統整體表現
- 最佳表現 Bot
- 實時交易統計

## 🧪 測試和調試

### 運行測試
```bash
python -m src.external.init_trading_system --test
```

### 交互式 Shell
```bash
python -m src.external.init_trading_system --shell
```

命令列表：
- `list_bots` - 列出所有 Bot
- `status` - 顯示 Bot 狀態
- `switch <bot>` - 切換 Bot
- `execute` - 執行測試信號
- `metrics` - 顯示指標

## 📝 檔案大小總結

| 模組 | 大小 | 行數 |
|------|------|------|
| unified_trading_system.py | 27K | ~920 |
| unified_dashboard.py | 21K | ~680 |
| config_manager.py | 14K | ~450 |
| init_trading_system.py | 8.2K | ~280 |
| 總計 | 70K+ | 2,330+ |

## 🔗 關鍵特性

✅ **統一介面** - 所有 Bot 實現相同的基類  
✅ **集中管理** - 一個 BotManager 管理所有 Bot  
✅ **即時切換** - 在 Bot 之間無縫切換  
✅ **Web 儀表板** - FastAPI + WebSocket 實時更新  
✅ **配置管理** - YAML/JSON 配置文件  
✅ **性能追蹤** - 自動聚合所有指標  
✅ **風險管理** - 內置風險限制  
✅ **可擴展性** - 支持添加自定義 Bot  

## 🚀 下一步

1. **配置 Bot**：編輯 `config/trading_system/bots_config.yaml`
2. **啟動系統**：運行啟動命令
3. **監控儀表板**：訪問 Web 界面
4. **執行交易**：通過 API 或儀表板執行信號
5. **監控性能**：追蹤各 Bot 的表現

## ❓ 常見命令

```bash
# 初始化
python -m src.external.init_trading_system --setup

# 測試
python -m src.external.init_trading_system --test

# 啟動儀表板
python -m src.external.init_trading_system --dashboard

# 交互式模式
python -m src.external.init_trading_system --shell
```

---

📖 更多詳情，請參考 `src/external/README.md`
