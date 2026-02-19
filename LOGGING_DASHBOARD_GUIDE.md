# 📊 日誌面板使用指南

## 🎯 三種查看方式

### 方式 1️⃣：交互菜單 (推薦用於探索)

```bash
cd /root/comic_ai
python3 logging_dashboard.py
```

**輸出**:
```
================================================================================
  📊 日誌和報告查看面板
================================================================================

選項:
  1. 查看最近日誌 (trading.log)
  2. 查看系統日誌 (system.log)
  3. 查看 API 日誌 (api.log)
  4. 查看日誌統計
  5. 查看回測報告
  6. 查看日常報告
  7. 查看目錄結構
  8. 查看整體統計
  9. 搜索日誌
  0. 退出

請選擇 (0-9): 
```

**選擇示例**:
- 輸入 `1` → 查看最近交易日誌
- 輸入 `5` → 查看回測報告
- 輸入 `6` → 查看日常報告
- 輸入 `0` → 退出


### 方式 2️⃣：命令行快速查看 (推薦用於自動化)

#### 查看最近日誌

```bash
# 查看最近 20 行交易日誌 (默認)
python3 logging_dashboard.py logs

# 查看最近 50 行交易日誌
python3 logging_dashboard.py logs trading 50

# 查看最近 30 行系統日誌
python3 logging_dashboard.py logs system 30

# 查看最近 40 行 API 日誌
python3 logging_dashboard.py logs api 40
```

#### 查看日誌統計

```bash
# 查看交易日誌統計 (默認)
python3 logging_dashboard.py summary

# 查看系統日誌統計
python3 logging_dashboard.py summary system

# 查看 API 日誌統計
python3 logging_dashboard.py summary api
```

**輸出示例**:
```
日誌級別分布:
  🔵 DEBUG    :   150 條
  🟢 INFO     :  1234 條
  🟡 WARNING  :    45 條
  🔴 ERROR    :    12 條
  ⚫ CRITICAL :     2 條
  ────────────────────
  📈 總計     :  1443 條
```

#### 查看報告

```bash
# 查看回測報告
python3 logging_dashboard.py backtest

# 查看日常報告
python3 logging_dashboard.py daily
```

#### 查看結構和統計

```bash
# 查看目錄結構
python3 logging_dashboard.py dir

# 查看整體統計
python3 logging_dashboard.py stats
```

#### 搜索日誌

```bash
# 搜索包含 "BTC" 的交易日誌
python3 logging_dashboard.py search "BTC"

# 搜索包含 "error" 的系統日誌
python3 logging_dashboard.py search "error" system

# 搜索包含 "API_KEY" 的 API 日誌
python3 logging_dashboard.py search "API_KEY" api
```


### 方式 3️⃣：直接查看文件 (推薦用於詳細分析)

```bash
# 查看交易日誌 (所有行)
cat logs/trading.log

# 查看系統日誌
cat logs/system.log

# 查看回測報告 CSV
cat reports/backtest/backtest_report_*.csv

# 查看日常報告 CSV
cat reports/daily/daily_report_*.csv

# 用 Excel 打開 (Windows/Mac)
open reports/backtest/backtest_report_*.csv
```

---

## 📊 查看報告的 5 種方法

### 1️⃣ 在終端查看 (快速)

```bash
python3 logging_dashboard.py backtest
```

**顯示**:
- 報告文件列表
- 最新報告的前 10 行

### 2️⃣ 在 Excel 中打開 (詳細)

```bash
# Windows
start reports\backtest\backtest_report_*.csv

# Mac
open reports/backtest/backtest_report_*.csv

# Linux
xdg-open reports/backtest/backtest_report_*.csv
```

### 3️⃣ 用 Python 分析 (程式化)

```python
import csv

# 讀取回測報告
with open('reports/backtest/backtest_report_*.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"策略: {row['strategy_name']}, 回報: {row['total_return']}%")
```

### 4️⃣ 用 grep 搜索 (快速過濾)

```bash
# 查找所有 BTC 相關的回測
grep "BTC" reports/backtest/*.csv

# 查找回報大於 30% 的策略
awk -F',' '$3 > 30 {print}' reports/backtest/*.csv
```

### 5️⃣ 用自訂腳本處理 (高級)

```python
from src.core.backtest_report_generator import BacktestReportGenerator
from src.core.logging_integration import LogQueryTool

# 查詢日誌
query = LogQueryTool()
recent_logs = query.get_recent_logs('trading', limit=100)

# 生成報告
generator = BacktestReportGenerator()
report_path = generator.generate_report(results)
```

---

## 🎨 日誌面板輸出示例

### 查看最近日誌

```
================================================================================
  📋 最近 20 行日誌 (trading.log)
================================================================================
  1. 2026-02-19 16:17:41,675 - trading - INFO - ✅ 日誌系統已初始化
  2. 2026-02-19 16:18:15,234 - trading - DEBUG - 分析市場數據: BTC/USDT
  3. 2026-02-19 16:18:20,456 - trading - INFO - 買入信號: BTC/USDT @ 53200
  4. 2026-02-19 16:18:25,789 - trading - INFO - 訂單已執行
  5. 2026-02-19 16:19:10,234 - trading - DEBUG - 計算風險: 2%
  ...
 20. 2026-02-19 16:25:30,567 - trading - INFO - 日常報告已生成

✅ 共 1443 行日誌
```

### 查看日誌統計

```
================================================================================
  📊 日誌統計摘要 (trading.log)
================================================================================
日誌級別分布:
  🔵 DEBUG    :   150 條 (10%)
  🟢 INFO     :  1234 條 (85%)
  🟡 WARNING  :    45 條 (3%)
  🔴 ERROR    :    12 條 (1%)
  ⚫ CRITICAL :     2 條 (0%)
  ────────────────────
  📈 總計     :  1443 條
```

### 查看回測報告

```
================================================================================
  📊 回測報告列表
================================================================================
1. backtest_report_20260219_161741.csv      (   0.2 KB) - 2026-02-19 16:17:41
2. strategy_comparison_20260219_161741.csv  (   0.3 KB) - 2026-02-19 16:17:41

📄 最新報告: strategy_comparison_20260219_161741.csv
────────────────────────────────────────────────────────────────────────────────
strategy_name,symbol,total_return,annual_return,sharpe_ratio,max_drawdown,win_rate,total_trades,profit_factor
MA_Crossover,BTC/USDT,45.50,45.50,1.85,-12.30,0.62,156,3.20
RSI_Divergence,ETH/USDT,32.10,32.10,1.45,-18.50,0.55,203,2.10
```

---

## 🔍 日誌搜索示例

### 搜索交易信號

```bash
python3 logging_dashboard.py search "買入信號" trading
```

### 搜索錯誤

```bash
python3 logging_dashboard.py search "error" system
```

### 搜索特定交易對

```bash
python3 logging_dashboard.py search "ETH/USDT" trading
```

---

## 📁 目錄結構查看

```bash
python3 logging_dashboard.py dir
```

**輸出**:
```
📂 logs/ (日誌文件存儲)
  📄 trading.log             (150.2 KB)
  📄 system.log              ( 45.8 KB)
  📄 api.log                 ( 23.4 KB)

📂 reports/backtest/ (回測報告)
  📄 backtest_report_20260219_161741.csv (  0.2 KB)
  📄 strategy_comparison_20260219_161741.csv (  0.3 KB)

📂 reports/daily/ (日常報告)
  📄 daily_report_20260219.csv (  0.1 KB)
  📄 daily_tracking.csv        (  2.5 KB)
  📄 portfolio_report_20260219.csv (  0.3 KB)

📂 config/ (配置文件)
  📄 report_config.yaml      (  5.4 KB)
  📄 logging_config.yaml     (  3.2 KB)
```

---

## 💡 常見用途

### 1. 監控交易執行

```bash
# 查看最近 100 行交易日誌，檢查執行情況
python3 logging_dashboard.py logs trading 100

# 搜索特定交易對
python3 logging_dashboard.py search "BTC/USDT" trading
```

### 2. 檢查系統性能

```bash
# 查看系統日誌統計
python3 logging_dashboard.py summary system

# 搜索 WARNING 或 ERROR
python3 logging_dashboard.py search "WARNING" system
```

### 3. 分析策略績效

```bash
# 查看最新回測報告
python3 logging_dashboard.py backtest

# 在 Excel 中打開進行詳細分析
open reports/backtest/backtest_report_*.csv
```

### 4. 檢查每日交易

```bash
# 查看日常報告
python3 logging_dashboard.py daily

# 查看投資組合報告
cat reports/daily/portfolio_report_*.csv
```

### 5. 定期生成報告摘要

```bash
# 創建定時任務 (Cron 或 Task Scheduler)
# 每小時運行一次

# 生成報告摘要
python3 logging_dashboard.py stats > daily_summary.txt

# 發送郵件 (可選)
# mail -s "Daily Summary" user@example.com < daily_summary.txt
```

---

## 🚀 快速參考

| 命令 | 功能 | 示例 |
|------|------|------|
| `logs [category] [lines]` | 查看最近日誌 | `logs trading 50` |
| `summary [category]` | 查看日誌統計 | `summary system` |
| `backtest` | 查看回測報告 | `backtest` |
| `daily` | 查看日常報告 | `daily` |
| `dir` | 查看目錄結構 | `dir` |
| `stats` | 查看整體統計 | `stats` |
| `search <keyword> [category]` | 搜索日誌 | `search "BTC" trading` |

---

## 🎯 最佳實踐

1. **定期檢查日誌**
   - 每天開始時查看系統日誌
   - 每次交易後檢查交易日誌

2. **使用搜索功能**
   - 搜索 "error" 查找問題
   - 搜索特定交易對追蹤交易

3. **分析報告數據**
   - 用 Excel 打開報告進行深入分析
   - 對比多個回測結果

4. **設置定期檢查**
   - 每小時生成一次統計
   - 每天生成完整報告摘要

5. **保留歷史記錄**
   - 定期備份日誌和報告
   - 按月歸檔舊記錄

---

## 🆘 故障排除

### 問題：找不到日誌文件
**解決**：
```bash
# 先運行設置腳本
python3 setup_logging_reports.py

# 檢查目錄是否存在
ls -la logs/
```

### 問題：報告內容為空
**解決**：
```bash
# 生成示例報告
python3 setup_logging_reports.py

# 查看示例
python3 logging_dashboard.py backtest
```

### 問題：搜索找不到結果
**解決**：
```bash
# 檢查關鍵字拼寫
# 嘗試不同的日誌類別
python3 logging_dashboard.py search "keyword" system

# 查看日誌是否存在
python3 logging_dashboard.py dir
```

---

## 📞 需要幫助？

查看相關文檔：
- `LOGGING_REPORTS_QUICKSTART.md` - 快速開始
- `COMPLETE_INTEGRATION_SUMMARY.md` - 完整指南
- `config/report_config.yaml` - 配置選項
