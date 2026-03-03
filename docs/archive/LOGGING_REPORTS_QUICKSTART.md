
# 日誌和報告系統 - 快速開始指南

## 📁 目錄結構
```
logs/
├── app.log              # 主應用日誌
├── trading.log          # 交易相關日誌
├── system.log           # 系統日誌
└── api.log              # API 調用日誌

reports/
├── backtest/            # 回測報告
│   └── backtest_report_YYYYMMDD_HHMMSS.csv
└── daily/               # 日常報告
    ├── daily_report_YYYYMMDD.csv
    ├── daily_tracking.csv
    └── portfolio_report_YYYYMMDD.csv

config/
├── report_config.yaml   # 報告配置（必看項目定義）
└── logging_config.yaml  # 日誌配置
```

## 🚀 快速使用

### 1. 日誌記錄
```python
from src.core.logging_integration import LogManager

manager = LogManager()
logger = manager.get_logger("trading")

# 記錄交易日誌
logger.info("BTC/USDT 買入信號", extra={
    "price": 53200,
    "volume": 1.5
})
```

### 2. 回測報告
```python
from src.core.backtest_report_generator import BacktestResult, BacktestReportGenerator

results = [
    BacktestResult(
        strategy_name="MA_Crossover",
        symbol="BTC/USDT",
        total_return=45.5,
        # ... 其他字段
    )
]

generator = BacktestReportGenerator()
filepath = generator.generate_report(results)
# 報告文件: reports/backtest/backtest_report_YYYYMMDD_HHMMSS.csv
```

### 3. 日常報告
```python
from src.core.daily_report_generator import DailyTradingStats, DailyReportGenerator

stats = [
    DailyTradingStats(
        date="2024-02-19",
        symbol="BTC/USDT",
        close_price=53200,
        daily_return=2.31,
        total_pnl=1601.25,
        # ... 其他字段
    )
]

generator = DailyReportGenerator()
filepath = generator.generate_daily_report(stats)
# 報告文件: reports/daily/daily_report_YYYYMMDD.csv
```

### 4. 日誌查詢
```python
from src.core.logging_integration import LogQueryTool

query = LogQueryTool()

# 獲取最近日誌
recent = query.get_recent_logs("trading", limit=50)

# 搜索日誌
results = query.search_logs("trading", keyword="BTC")

# 獲取摘要
summary = query.get_log_summary("trading")
```

## 📊 自訂報告列

### 回測報告 - 必看項目
```python
columns = [
    'strategy_name',    # 策略名稱
    'symbol',          # 交易對
    'total_return',    # 總回報
    'sharpe_ratio',    # 夏普比率
    'max_drawdown',    # 最大回撤
    'win_rate',        # 勝率
]

generator.generate_report(results, columns=columns)
```

### 日常報告 - 必看項目
```python
columns = [
    'date',            # 日期
    'symbol',          # 交易對
    'close_price',     # 收盤價
    'daily_return',    # 日回報
    'total_pnl',       # 損益
]

generator.generate_daily_report(stats, columns=columns)
```

## ⚙️ 配置文件 (config/report_config.yaml)

編輯報告配置以自訂必看項目：

```yaml
backtest_report:
  default_columns:
    - strategy_name
    - symbol
    - total_return
    - sharpe_ratio
    - max_drawdown
    - win_rate
    - total_trades

daily_report:
  default_columns:
    - date
    - symbol
    - close_price
    - daily_return
    - total_pnl
```

## 📈 報告類型

### 回測報告
- **簡潔版**: 關鍵績效指標（9 個欄位）
- **詳細版**: 完整交易分析（17 個欄位）
- **對比版**: 策略績效對比

### 日常報告
- **簡潔版**: 當日交易摘要（8 個欄位）
- **詳細版**: 完整價格和交易數據（15 個欄位）
- **投資組合版**: 按交易對分組統計

## 🔍 日誌級別

```
DEBUG    - 詳細調試信息
INFO     - 一般信息
WARNING  - 警告信息
ERROR    - 錯誤信息
CRITICAL - 關鍵錯誤
```

## 📝 .env 配置

```
# 日誌設置
LOG_LEVEL=DEBUG
LOG_DIR=logs
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# 報告設置
REPORT_OUTPUT_DIR=reports
BACKTEST_REPORT_FORMAT=csv
DAILY_REPORT_FORMAT=csv
```

## 🎯 最佳實踐

1. **日誌記錄**
   - 每次交易記錄進入/退出點
   - 記錄策略信號和決策依據
   - 記錄系統錯誤和異常

2. **報告生成**
   - 每週生成回測報告
   - 每日自動生成交易報告
   - 定期檢查投資組合績效

3. **數據管理**
   - 定期備份報告和日誌
   - 保留 30 天的日誌
   - 按月歸檔舊報告

## 🆘 故障排除

### 日誌文件為空
- 檢查日誌級別設置
- 確保日誌目錄可寫
- 檢查磁盤空間

### 報告生成失敗
- 驗證 reports/ 目錄存在
- 檢查數據格式正確
- 確保 CSV 編碼為 UTF-8

### 查詢結果為空
- 確保日誌文件存在
- 檢查搜索關鍵字拼寫
- 驗證日誌級別篩選

