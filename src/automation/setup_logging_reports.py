#!/usr/bin/env python3
"""
日誌和報告快速設置腳本 (Setup Logging & Reports)
设置日志和报告系统 - 開箱即用
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

def create_directories():
    """創建必要的目錄結構"""
    dirs = [
        'logs',
        'reports/backtest',
        'reports/daily',
        'config'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    return dirs


def create_logging_config():
    """創建日誌配置文件"""
    config_path = 'config/logging_config.yaml'
    
    if os.path.exists(config_path):
        print(f"✅ 日誌配置文件已存在: {config_path}")
        return config_path
    
    # 使用 report_config.yaml 中的 logging 部分
    print(f"✅ 日誌配置應從 config/report_config.yaml 中配置")
    return config_path


def create_example_reports():
    """創建示例報告檔案"""
    print("\n📊 創建示例報告...")
    
    # 回測報告示例
    backtest_example = """strategy_name,symbol,total_return,annual_return,sharpe_ratio,max_drawdown,win_rate,total_trades,profit_factor
MA_Crossover,BTC/USDT,45.50,45.50,1.85,-12.30,0.62,156,3.20
RSI_Divergence,ETH/USDT,32.10,32.10,1.45,-18.50,0.55,203,2.10
Bollinger_Bands,BTC/USDT,28.70,28.70,1.22,-15.60,0.58,142,2.45
"""
    
    backtest_file = 'reports/backtest/example_backtest_report.csv'
    with open(backtest_file, 'w', encoding='utf-8') as f:
        f.write(backtest_example)
    print(f"✅ 回測報告示例: {backtest_file}")
    
    # 日常報告示例
    daily_example = """date,symbol,close_price,daily_return,trades_count,win_rate,realized_pnl,total_pnl
2024-02-19,BTC/USDT,53200.00,2.31,12,0.67,1250.50,1601.25
2024-02-19,ETH/USDT,3020.00,4.14,8,0.63,750.25,870.75
2024-02-18,BTC/USDT,52100.00,1.95,10,0.70,980.50,1120.75
2024-02-18,ETH/USDT,2900.00,3.45,7,0.57,620.30,750.50
"""
    
    daily_file = 'reports/daily/example_daily_report.csv'
    with open(daily_file, 'w', encoding='utf-8') as f:
        f.write(daily_example)
    print(f"✅ 日常報告示例: {daily_file}")
    
    return backtest_file, daily_file


def test_logging_module():
    """測試日誌模組"""
    print("\n🧪 測試日誌模組...")
    
    try:
        from src.core.logging_integration import LogManager, LogQueryTool
        
        # 創建日誌管理器
        manager = LogManager()
        logger = manager.get_logger("test")
        logger.info("✅ 日誌系統已初始化")
        
        # 測試日誌查詢
        query = LogQueryTool()
        summary = query.get_log_summary("test")
        print(f"✅ 日誌查詢工具已測試: {summary}")
        
        return True
    except Exception as e:
        print(f"❌ 日誌模組測試失敗: {e}")
        return False


def test_backtest_report_generator():
    """測試回測報告生成器"""
    print("\n🧪 測試回測報告生成器...")
    
    try:
        from src.core.backtest_report_generator import BacktestResult, BacktestReportGenerator
        
        # 創建示例數據
        results = [
            BacktestResult(
                strategy_name="Test_Strategy",
                symbol="BTC/USDT",
                start_date="2024-01-01",
                end_date="2024-02-19",
                total_return=25.5,
                annual_return=25.5,
                sharpe_ratio=1.5,
                max_drawdown=-10.0,
                win_rate=0.60,
                total_trades=50,
                winning_trades=30,
                losing_trades=20,
                avg_win=1.5,
                avg_loss=-1.0,
                profit_factor=2.5,
                best_trade=5.0,
                worst_trade=-4.0
            )
        ]
        
        # 生成報告
        generator = BacktestReportGenerator()
        filepath = generator.generate_report(results)
        print(f"✅ 回測報告已生成: {filepath}")
        
        return True
    except Exception as e:
        print(f"❌ 回測報告生成失敗: {e}")
        return False


def test_daily_report_generator():
    """測試日常報告生成器"""
    print("\n🧪 測試日常報告生成器...")
    
    try:
        from src.core.daily_report_generator import DailyTradingStats, DailyReportGenerator
        
        # 創建示例數據
        stats = [
            DailyTradingStats(
                date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                symbol="BTC/USDT",
                open_price=52000,
                high_price=53500,
                low_price=51800,
                close_price=53200,
                volume=1500.5,
                trades_count=12,
                wins=8,
                losses=4,
                win_rate=0.67,
                daily_return=2.31,
                realized_pnl=1250.50,
                unrealized_pnl=350.75,
                total_pnl=1601.25
            )
        ]
        
        # 生成報告
        generator = DailyReportGenerator()
        filepath = generator.generate_daily_report(stats)
        print(f"✅ 日常報告已生成: {filepath}")
        
        return True
    except Exception as e:
        print(f"❌ 日常報告生成失敗: {e}")
        return False


def create_quickstart_guide():
    """創建快速開始指南"""
    guide = """
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

"""
    
    guide_file = 'LOGGING_REPORTS_QUICKSTART.md'
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return guide_file


def main():
    """主程序"""
    print("=" * 60)
    print("🚀 Comic AI 日誌和報告系統 - 快速設置")
    print("=" * 60)
    
    # 1. 創建目錄
    print("\n📁 創建目錄結構...")
    dirs = create_directories()
    for d in dirs:
        print(f"  ✅ {d}")
    
    # 2. 創建配置文件
    print("\n⚙️  創建配置文件...")
    create_logging_config()
    
    # 3. 創建示例報告
    print("\n📊 創建示例報告...")
    create_example_reports()
    
    # 4. 測試模組
    print("\n🧪 測試模組...")
    logging_ok = test_logging_module()
    backtest_ok = test_backtest_report_generator()
    daily_ok = test_daily_report_generator()
    
    # 5. 創建快速開始指南
    print("\n📖 創建快速開始指南...")
    guide_file = create_quickstart_guide()
    print(f"✅ 指南文件: {guide_file}")
    
    # 6. 總結
    print("\n" + "=" * 60)
    print("✅ 設置完成！")
    print("=" * 60)
    
    print("\n📂 關鍵目錄:")
    print("  - logs/              # 日誌文件")
    print("  - reports/backtest/  # 回測報告")
    print("  - reports/daily/     # 日常報告")
    print("  - config/            # 配置文件")
    
    print("\n📖 下一步:")
    print("  1. 查看快速開始指南: LOGGING_REPORTS_QUICKSTART.md")
    print("  2. 編輯配置文件: config/report_config.yaml")
    print("  3. 開始使用日誌和報告系統")
    
    print("\n🔧 測試結果:")
    print(f"  {'✅' if logging_ok else '❌'} 日誌模組")
    print(f"  {'✅' if backtest_ok else '❌'} 回測報告生成器")
    print(f"  {'✅' if daily_ok else '❌'} 日常報告生成器")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
