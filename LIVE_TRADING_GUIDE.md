# 🚀 Comic AI 實盤交易系統 - 完整整合文檔

## 📋 目錄

1. [系統概覽](#系統概覽)
2. [快速開始](#快速開始)
3. [核心模組](#核心模組)
4. [實盤交易](#實盤交易)
5. [數據整合](#數據整合)
6. [統合API](#統合api)
7. [儀表板](#儀表板)
8. [完整示例](#完整示例)
9. [API參考](#api參考)

---

## 系統概覽

### 🎯 核心功能

Comic AI 是一個完整的智能交易系統，集成以下功能：

- **多宇宙模擬系統** - 16個平行宇宙，8種市場類型
- **6層認知記憶** - 完整的記憶和學習系統
- **實盤交易引擎** - 完整的訂單執行和風險管理
- **數據整合層** - 支持多種數據源和格式
- **統合API** - 統一的Python接口
- **現代儀表板** - 實時監控和控制

### 🏗️ 系統架構

```
┌─────────────────────────────────────────────────┐
│          Comic AI Trading System                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │   Interactive Web Dashboard              │  │
│  │   (HTML5 + Chart.js + WebSocket)         │  │
│  └──────────────────────────────────────────┘  │
│                    ↑                            │
│  ┌──────────────────────────────────────────┐  │
│  │   統合API (ComicAIUnifiedAPI)            │  │
│  │   - 系統管理                             │  │
│  │   - 模擬控制                             │  │
│  │   - 性能監控                             │  │
│  └──────────────────────────────────────────┘  │
│    ↑              ↑              ↑              │
│  ┌───────────┐ ┌────────────┐ ┌───────────┐   │
│  │ 實盤交易  │ │ 數據整合   │ │ 多宇宙    │   │
│  │           │ │ 層         │ │ 系統      │   │
│  ├───────────┤ ├────────────┤ ├───────────┤   │
│  │ • 訂單    │ │ • CSV      │ │ • 16宇宙  │   │
│  │ • 倉位    │ │ • JSON     │ │ • 16代理  │   │
│  │ • 風控    │ │ • OHLCV    │ │ • 知識交換│   │
│  │ • 帳戶    │ │ • Mock     │ │ • 性能優化│   │
│  └───────────┘ └────────────┘ └───────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 快速開始

### 📦 安裝

```bash
cd /root/comic_ai
pip install -r requirements.txt
```

### ⚡ 5分鐘示例

```python
import asyncio
from opencode import ComicAIUnifiedAPI, SimulationConfig

async def main():
    # 1. 創建API實例
    config = SimulationConfig(
        num_universes=16,
        num_steps=100,
        enable_optimization=True,
    )
    api = ComicAIUnifiedAPI(config)
    
    # 2. 初始化系統
    await api.initialize()
    
    # 3. 運行模擬
    results = await api.run_simulation()
    
    # 4. 查看結果
    print(f"總步數: {results['total_steps']}")
    print(f"執行時間: {results['execution_time_sec']}秒")
    print(f"平均收益: {results['metrics']['avg_return']}%")

asyncio.run(main())
```

### 🎮 實盤交易示例

```python
import asyncio
from opencode import LiveTradingEngine

async def main():
    # 1. 創建交易引擎
    engine = LiveTradingEngine(
        account_id="DEMO_ACCOUNT",
        initial_balance=10000.0,
    )
    
    # 2. 初始化
    await engine.initialize()
    await engine.start_trading()
    
    # 3. 下單
    order_id = await engine.place_buy_order("BTC/USD", 50000, 0.1)
    print(f"買單提交: {order_id}")
    
    # 4. 查看倉位
    for pos in engine.get_positions():
        print(f"{pos.symbol}: {pos.quantity} @ {pos.entry_price}")
    
    # 5. 平倉
    await engine.close_position("BTC/USD")
    
    # 6. 查看統計
    stats = engine.get_stats()
    print(f"交易統計: {stats}")

asyncio.run(main())
```

---

## 核心模組

### 1️⃣ 實盤交易模組 (`live_trading.py`)

完整的實時交易引擎，包括：

#### 訂單管理
```python
from opencode import LiveTradingEngine, OrderType

engine = LiveTradingEngine("ACCOUNT_1", 10000)
await engine.initialize()

# 下單
buy_order = await engine.place_buy_order("BTC/USD", 50000, 0.1)
sell_order = await engine.place_sell_order("ETH/USD", 3000, 1.0)
```

#### 倉位管理
```python
# 獲取倉位
positions = engine.get_positions()

for pos in positions:
    print(f"倉位: {pos.symbol}")
    print(f"方向: {pos.side.value}")
    print(f"數量: {pos.quantity}")
    print(f"入場價: {pos.entry_price}")
    print(f"當前價: {pos.current_price}")
    print(f"未實現損益: {pos.unrealized_pnl}")
    print(f"收益率: {pos.return_rate}%")
```

#### 風險管理
```python
from opencode import RiskManager

risk_mgr = RiskManager(
    max_position_size=10000,      # 最大倉位
    max_daily_loss=5000,          # 最大日損失
    max_leverage=10.0,             # 最大槓桿
    stop_loss_percent=2.0,         # 止損百分比
)

# 檢查風險
is_safe = risk_mgr.check_position_size(position_value, equity)
is_safe = risk_mgr.check_daily_loss(current_loss)
```

#### 帳戶信息
```python
# 獲取帳戶信息
account = engine.get_account_info()
print(f"餘額: ${account.balance}")
print(f"淨值: ${account.equity}")
print(f"可用保證金: ${account.free_margin}")
print(f"保證金率: {account.margin_level}%")
```

#### 交易統計
```python
# 獲取統計
stats = engine.get_stats()
print(f"總交易: {stats['total_trades']}")
print(f"勝率: {stats['win_rate']}%")
print(f"總收益: ${stats['total_pnl']}")
print(f"ROI: {stats['roi']}%")
```

### 2️⃣ 數據整合模組 (`data_integration.py`)

支持多種數據源和格式：

#### 數據加載
```python
from opencode import DataManager, DataFormat

manager = DataManager()

# 從CSV加載
await manager.load_and_buffer_data(
    "data/btc_data.csv",
    format=DataFormat.CSV,
    symbol="BTC/USD"
)

# 從JSON加載
await manager.load_and_buffer_data(
    "data/eth_data.json",
    format=DataFormat.JSON,
    symbol="ETH/USD"
)

# 加載模擬數據
await manager.load_mock_data("BTC/USD", num_records=1000)
```

#### 技術分析
```python
# 獲取分析
analysis = manager.get_analysis("BTC/USD", analysis_type="all")

print(f"價格統計: {analysis['price_stats']}")
print(f"SMA 20: {analysis['sma_20']}")
print(f"RSI 14: {analysis['rsi_14']}")
print(f"波動性: {analysis['volatility']}")
```

#### 特定指標
```python
from opencode import DataAnalyzer

analyzer = DataAnalyzer()

# 移動平均線
sma = analyzer.calculate_sma(ohlcvs, period=20)
ema = analyzer.calculate_ema(ohlcvs, period=20)

# 相對強弱指標
rsi = analyzer.calculate_rsi(ohlcvs, period=14)

# 波動率
volatility = analyzer.calculate_volatility(ohlcvs, period=20)

# 價格統計
stats = analyzer.get_price_stats(ohlcvs)
```

### 3️⃣ 統合API (`unified_api.py`)

統一的系統管理接口：

#### 初始化
```python
from opencode import ComicAIUnifiedAPI, SimulationConfig

config = SimulationConfig(
    num_universes=16,
    agents_per_universe=1,
    num_steps=100,
    enable_optimization=True,
    cache_size=5000,
)

api = ComicAIUnifiedAPI(config)

# 初始化所有子系統
await api.initialize()
```

#### 運行模擬
```python
# 運行模擬
results = await api.run_simulation(num_steps=100)

# 查看結果
print(f"總步數: {results['total_steps']}")
print(f"執行時間: {results['execution_time_sec']}秒")
print(f"指標: {results['metrics']}")
```

#### 控制系統
```python
# 暫停
api.pause_simulation()

# 繼續
api.resume_simulation()

# 停止
await api.stop_simulation()
```

#### 回調函數
```python
def on_metrics_update(metrics):
    print(f"模擬步數: {metrics.simulation_steps}")
    print(f"性能: {metrics.agent_efficiency}%")

def on_status_change(status):
    print(f"系統狀態: {status.value}")

api.register_metrics_callback(on_metrics_update)
api.register_status_callback(on_status_change)
```

#### 導出結果
```python
# 導出結果到JSON
await api.export_results("results.json")

# 導入配置
await api.import_configuration("config.yaml")
```

---

## 實盤交易

### 完整交易流程

```python
import asyncio
from opencode import LiveTradingEngine

async def trading_example():
    # 1. 創建引擎
    engine = LiveTradingEngine(
        account_id="LIVE_ACCOUNT",
        initial_balance=100000,
    )
    
    # 2. 初始化
    await engine.initialize()
    await engine.start_trading()
    
    # 3. 行情查詢
    btc_price = await engine.get_market_price("BTC/USD")
    print(f"BTC當前價格: {btc_price.close}")
    
    # 4. 下單
    order = await engine.place_buy_order(
        symbol="BTC/USD",
        price=btc_price.close,
        quantity=1.0
    )
    print(f"買單: {order}")
    
    # 5. 監控倉位
    positions = engine.get_positions()
    for pos in positions:
        print(f"倉位價值: ${pos.position_value}")
        print(f"未實現損益: ${pos.unrealized_pnl}")
    
    # 6. 帳戶管理
    account = engine.get_account_info()
    print(f"帳戶淨值: ${account.equity}")
    
    # 7. 平倉
    await engine.close_position("BTC/USD")
    
    # 8. 交易記錄
    trades = engine.get_trades()
    stats = engine.get_stats()
    print(f"交易統計: {stats}")
    
    # 9. 停止
    await engine.stop_trading()

asyncio.run(trading_example())
```

### 回調系統

```python
def on_order_filled(order_id):
    print(f"訂單成交: {order_id}")

def on_position_changed(symbol):
    print(f"倉位變化: {symbol}")

def on_account_updated(account_id):
    print(f"帳戶更新: {account_id}")

engine.register_callback('order_filled', on_order_filled)
engine.register_callback('position_changed', on_position_changed)
engine.register_callback('account_updated', on_account_updated)
```

---

## 數據整合

### 支持的格式

#### CSV 格式
```
timestamp,open,high,low,close,volume
2024-01-01T00:00:00,100.0,101.5,99.5,100.5,1000000
2024-01-01T01:00:00,100.5,102.0,99.8,101.0,1100000
```

#### JSON 格式
```json
[
    {
        "timestamp": "2024-01-01T00:00:00",
        "symbol": "BTC/USD",
        "open": 100.0,
        "high": 101.5,
        "low": 99.5,
        "close": 100.5,
        "volume": 1000000
    }
]
```

#### OHLCV 對象
```python
from opencode import OHLCV
from datetime import datetime

ohlcv = OHLCV(
    timestamp=datetime.now(),
    symbol="BTC/USD",
    open=100.0,
    high=101.5,
    low=99.5,
    close=100.5,
    volume=1000000,
)

# 轉換為字典
data_dict = ohlcv.to_dict()
```

### 數據分析

```python
from opencode import DataManager

manager = DataManager()
await manager.load_mock_data("BTC/USD", 1000)

# 完整分析
analysis = manager.get_analysis("BTC/USD", "all")

# 單項分析
price_stats = analysis['price_stats']
sma = analysis['sma_20']
rsi = analysis['rsi_14']
```

---

## 統合API

### 完整示例

```python
import asyncio
from opencode import ComicAIUnifiedAPI, SimulationConfig

async def main():
    # 配置
    config = SimulationConfig(
        num_universes=16,
        agents_per_universe=1,
        num_steps=1000,
        enable_optimization=True,
        cache_size=10000,
        memory_limit_mb=200.0,
        log_interval=100,
    )
    
    # 創建API
    api = ComicAIUnifiedAPI(config)
    
    # 回調
    def on_metrics(metrics):
        print(f"進度: {metrics.simulation_steps} 步")
    
    api.register_metrics_callback(on_metrics)
    
    # 初始化
    success = await api.initialize()
    if not success:
        print("初始化失敗")
        return
    
    # 運行
    results = await api.run_simulation()
    
    # 結果
    print(f"完成！耗時: {results['execution_time_sec']:.2f}秒")
    print(f"結果已保存到: results_summary.json")

asyncio.run(main())
```

---

## 儀表板

### 訪問儀表板

```bash
# 啟動儀表板服務器
python3 -m http.server 8000 --directory dashboard/

# 訪問
# http://localhost:8000/integrated_dashboard.html
```

### 儀表板功能

- 📊 **概覽** - 系統狀態和核心指標
- 🌌 **多宇宙系統** - 宇宙狀態和代理性能
- 🧠 **記憶系統** - 6層記憶層級和知識蒸餾
- ⚡ **性能分析** - 優化成果和基準線
- 🤖 **代理管理** - 代理狀態和統計

---

## 完整示例

### 🎯 示例1：完整交易系統

```python
import asyncio
from opencode import (
    ComicAIUnifiedAPI, 
    LiveTradingEngine,
    DataManager,
    SimulationConfig,
    DataFormat,
)

async def complete_trading_system():
    # 1. 初始化系統
    config = SimulationConfig(num_universes=16, num_steps=100)
    api = ComicAIUnifiedAPI(config)
    await api.initialize()
    
    # 2. 加載市場數據
    data_manager = DataManager()
    await data_manager.load_mock_data("BTC/USD", 1000)
    
    # 3. 啟動實盤交易
    trading = LiveTradingEngine("LIVE_1", 50000)
    await trading.initialize()
    await trading.start_trading()
    
    # 4. 運行模擬並交易
    await api.run_simulation(num_steps=50)
    
    # 5. 執行交易決策
    btc_price = await trading.get_market_price("BTC/USD")
    order_id = await trading.place_buy_order("BTC/USD", btc_price.close, 0.5)
    
    # 6. 查看結果
    stats = trading.get_stats()
    account = trading.get_account_info()
    
    print(f"系統運行完成!")
    print(f"帳戶淨值: ${account.equity}")
    print(f"交易統計: {stats}")
    
    await trading.stop_trading()

asyncio.run(complete_trading_system())
```

### 🎯 示例2：數據分析與決策

```python
import asyncio
from opencode import DataManager, DataAnalyzer

async def data_analysis():
    manager = DataManager()
    
    # 加載數據
    await manager.load_mock_data("BTC/USD", 500)
    await manager.load_mock_data("ETH/USD", 500)
    
    # 分析
    for symbol in ["BTC/USD", "ETH/USD"]:
        analysis = manager.get_analysis(symbol)
        
        stats = analysis['price_stats']
        print(f"\n{symbol}:")
        print(f"  最小價: ${stats['min']:.2f}")
        print(f"  最大價: ${stats['max']:.2f}")
        print(f"  平均價: ${stats['avg']:.2f}")
        print(f"  變化: {stats['change_percent']:.2f}%")

asyncio.run(data_analysis())
```

---

## API參考

### ComicAIUnifiedAPI

```python
class ComicAIUnifiedAPI:
    # 初始化與控制
    async def initialize() -> bool
    async def run_simulation(num_steps: Optional[int]) -> Dict
    def pause_simulation() -> None
    def resume_simulation() -> None
    async def stop_simulation() -> None
    
    # 狀態與指標
    def get_status() -> Dict
    def get_metrics() -> SystemMetrics
    def update_metrics(**kwargs) -> None
    
    # 回調
    def register_metrics_callback(callback) -> None
    def register_status_callback(callback) -> None
    
    # 數據
    async def export_results(filepath: str) -> bool
    async def import_configuration(config_path: str) -> bool
    async def get_agent_memory(agent_id: str) -> Optional[Dict]
    async def optimize_memory() -> Dict
    def get_system_info() -> Dict
```

### LiveTradingEngine

```python
class LiveTradingEngine:
    # 初始化
    async def initialize() -> bool
    async def start_trading() -> None
    async def stop_trading() -> None
    
    # 訂單
    async def place_buy_order(symbol, price, quantity) -> str
    async def place_sell_order(symbol, price, quantity) -> str
    async def close_position(symbol) -> Optional[str]
    
    # 查詢
    async def get_market_price(symbol) -> Optional[MarketPrice]
    def get_account_info() -> AccountInfo
    def get_positions() -> List[Position]
    def get_trades() -> List[Dict]
    def get_stats() -> Dict
    
    # 回調
    def register_callback(event: str, callback) -> None
```

### DataManager

```python
class DataManager:
    # 數據加載
    async def load_and_buffer_data(filepath, format, symbol) -> bool
    async def load_mock_data(symbol, num_records) -> bool
    
    # 分析
    def get_analysis(symbol, analysis_type) -> Dict
    def get_buffer_stats() -> Dict
```

---

## 📝 注意事項

1. **實盤交易** - 使用模擬數據源進行測試，不涉及真實資金
2. **數據格式** - 確保CSV/JSON數據包含所有必需欄位
3. **性能** - 系統已優化，查詢延遲 < 1ms
4. **備份** - 所有代碼已備份到 `backup_comic_ai_*.tar.gz`

---

## 🚀 後續步驟

1. **整合真實數據源** - 連接實時行情API (Binance, Kraken等)
2. **實盤對接** - 連接交易所API進行真實下單
3. **監控儀表板** - 部署Web服務供遠程監控
4. **量化策略** - 開發更複雜的交易策略
5. **機器學習** - 集成深度學習模型進行預測

---

## 📞 支持

如有問題，請查看：
- 源代碼註解和文檔字符串
- 完整的日誌輸出 (logging模塊)
- GitHub提交消息和更改日誌
- 集成測試用例 (tests目錄)

---

**祝您使用Comic AI系統愉快！** 🎉
