#!/usr/bin/env python3
"""
Comic AI 日誌和報告整合指南
Logging & Reports Integration Guide

本文檔說明如何將日誌系統、報告生成器與現有的多智能體交易系統整合
"""

# ============================================================================
# 📖 整合架構圖
# ============================================================================

"""
┌─────────────────────────────────────────────────────────────────────┐
│                   Comic AI 整合系統架構                             │
└─────────────────────────────────────────────────────────────────────┘

┌─── 應用層 ───────────────────────────────────────────────────────┐
│                                                                    │
│  多智能體交易系統 (src/plugins/multi_agent_trading.py)            │
│  ├─ PortfolioManager (投資組合管理)                              │
│  ├─ RiskManager (風險管理)                                        │
│  └─ SignalAnalyst (信號分析)                                     │
│                                                                    │
│  ↓ 記錄所有交易決策和事件                                         │
│                                                                    │
│  日誌系統 (src/core/logging_integration.py)                       │
│  ├─ LogManager (統一日誌管理)                                    │
│  ├─ trading.log (交易日誌)                                        │
│  ├─ system.log (系統日誌)                                         │
│  └─ api.log (API 調用日誌)                                        │
│                                                                    │
│  ↓ 生成報告                                                        │
│                                                                    │
└─────────────────────────────────────────────────────────────────┘

┌─── 報告層 ───────────────────────────────────────────────────────┐
│                                                                    │
│  回測報告 (src/core/backtest_report_generator.py)                 │
│  ├─ 必看項目 CSV (9 個關鍵指標)                                  │
│  ├─ 詳細版 CSV (17 個完整指標)                                   │
│  └─ JSON 格式 (結構化數據)                                        │
│                                                                    │
│  日常報告 (src/core/daily_report_generator.py)                    │
│  ├─ 簡潔版 CSV (8 個關鍵指標)                                    │
│  ├─ 詳細版 CSV (15 個完整指標)                                   │
│  ├─ 投資組合報告 (按交易對分組)                                  │
│  └─ JSON 格式 (結構化數據)                                        │
│                                                                    │
└─────────────────────────────────────────────────────────────────┘

┌─── 存儲層 ───────────────────────────────────────────────────────┐
│                                                                    │
│  logs/                 # 日誌文件                                 │
│  ├─ trading.log        # 交易相關                                 │
│  ├─ system.log         # 系統相關                                 │
│  └─ api.log            # API 相關                                 │
│                                                                    │
│  reports/              # 報告檔案                                 │
│  ├─ backtest/          # 回測報告                                 │
│  └─ daily/             # 日常報告                                 │
│                                                                    │
│  config/               # 配置檔案                                 │
│  ├─ report_config.yaml # 報告配置                                │
│  └─ logging_config.yaml # 日誌配置                               │
│                                                                    │
└─────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# 🔌 集成多智能體系統的日誌記錄
# ============================================================================

"""
### 方案 1: 直接集成到多智能體系統

步驟 1: 修改 src/plugins/multi_agent_trading.py

```python
from src.core.logging_integration import LogManager

class BaseAgent(ABC):
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        
        # 新增: 初始化日誌管理器
        self.log_manager = LogManager()
        self.logger = self.log_manager.get_logger(f"agent_{agent_id}")
    
    @abstractmethod
    async def make_decision(
        self,
        market_data: MarketData,
        portfolio_state: PortfolioState
    ) -> TradingDecision:
        pass
    
    def _log_decision(self, decision: TradingDecision):
        '''記錄交易決策'''
        self.logger.info(
            f"決策: {decision.decision_type.value} {decision.symbol}",
            extra={
                'quantity': decision.quantity,
                'price': decision.price,
                'confidence': decision.confidence,
                'risk_score': decision.risk_score,
                'rationale': decision.rationale
            }
        )
```

步驟 2: 在每個智能體中記錄事件

```python
class PortfolioManager(BaseAgent):
    async def make_decision(self, market_data, portfolio_state):
        decision = TradingDecision(...)
        
        # 記錄決策
        self._log_decision(decision)
        
        # 記錄詳細信息
        self.logger.debug(
            f"投資組合分析完成",
            extra={
                'total_value': portfolio_state.total_value,
                'cash': portfolio_state.cash,
                'positions': portfolio_state.positions
            }
        )
        
        return decision
```

步驟 3: 記錄系統級別的事件

```python
class TradingSystem:
    def __init__(self):
        self.log_manager = LogManager()
        self.system_logger = self.log_manager.get_logger("system")
        
        # 記錄系統啟動
        self.system_logger.info("交易系統已初始化")
    
    async def execute_decisions(self, decisions):
        self.system_logger.info(
            f"執行 {len(decisions)} 個交易決策",
            extra={'decisions': [d.to_dict() for d in decisions]}
        )
        # ... 執行邏輯 ...
        self.system_logger.info("交易執行完成")
```
"""

# ============================================================================
# 📊 生成交易報告
# ============================================================================

"""
### 方案 2: 從日誌生成回測報告

步驟 1: 收集回測結果

```python
from src.core.backtest_report_generator import BacktestResult, BacktestReportGenerator
from src.core.logging_integration import LogQueryTool

def generate_backtest_report():
    '''從日誌生成回測報告'''
    
    # 查詢日誌數據
    query_tool = LogQueryTool()
    trading_logs = query_tool.get_recent_logs('trading', limit=1000)
    
    # 解析日誌並計算統計
    results = parse_logs_to_results(trading_logs)  # 自訂解析函數
    
    # 生成報告
    generator = BacktestReportGenerator()
    
    # 必看項目版本
    filepath = generator.generate_report(results)
    print(f"✅ 回測報告: {filepath}")
    
    # 添加摘要
    generator.add_summary(results, filepath)
    
    # 導出 JSON 版本
    json_path = generator.export_json(results)
    print(f"✅ JSON 報告: {json_path}")
    
    return filepath
```

步驟 2: 定時生成日常報告

```python
import schedule
from datetime import datetime, timezone
from src.core.daily_report_generator import DailyTradingStats, DailyReportGenerator

class DailyReportScheduler:
    def __init__(self):
        self.generator = DailyReportGenerator()
        self.query_tool = LogQueryTool()
    
    def schedule_reports(self):
        '''定時生成日常報告'''
        # 每天下午 5 點生成
        schedule.every().day.at("17:00").do(self.generate_daily_report)
    
    def generate_daily_report(self):
        '''生成今日報告'''
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # 從日誌收集數據
        trading_logs = self.query_tool.get_recent_logs(
            'trading',
            limit=500
        )
        
        # 轉換為 DailyTradingStats
        stats = self._convert_logs_to_stats(trading_logs)
        
        # 生成報告
        filepath = self.generator.generate_daily_report(stats)
        print(f"✅ 日常報告已生成: {filepath}")
        
        # 生成投資組合報告
        portfolio_file = self.generator.generate_portfolio_report(stats)
        print(f"✅ 投資組合報告已生成: {portfolio_file}")
    
    def _convert_logs_to_stats(self, logs):
        '''將日誌轉換為統計數據'''
        # 實現邏輯
        pass
```
"""

# ============================================================================
# 🎯 最佳實踐
# ============================================================================

"""
### 1️⃣ 日誌記錄最佳實踐

✅ DO:
- 記錄所有交易決策和執行結果
- 記錄風險管理事件和警告
- 記錄系統錯誤和異常
- 使用結構化日誌格式（JSON）

❌ DON'T:
- 不要記錄敏感信息（密鑰、密碼）
- 不要記錄過於詳細的細節（每個計算步驟）
- 不要在日誌中硬編碼配置值

### 2️⃣ 報告生成最佳實踐

✅ DO:
- 使用必看項目 CSV 做快速分析
- 每週生成回測報告對比策略
- 每日自動生成交易報告
- 保留 30 天的日誌和報告

❌ DON'T:
- 不要生成過大的報告（性能問題）
- 不要混淆回測數據和實盤數據
- 不要忽視異常值和錯誤

### 3️⃣ 配置管理最佳實踐

✅ DO:
- 使用 config/report_config.yaml 自訂必看項目
- 定期備份配置和日誌
- 按環境（開發/生產）使用不同配置

❌ DON'T:
- 不要硬編碼報告列名
- 不要混淆環境配置
- 不要跳過配置驗證

### 4️⃣ 多智能體系統中的日誌

✅ DO:
- 每個智能體使用獨立的日誌記錄器
- 記錄智能體之間的通信
- 記錄協調者的決策邏輯

❌ DON'T:
- 不要使用全局日誌記錄
- 不要混淆不同智能體的日誌
- 不要忽視異步操作的日誌順序
"""

# ============================================================================
# 📝 使用示例
# ============================================================================

"""
### 完整工作流示例

1. 初始化系統

```python
from src.core.logging_integration import LogManager
from src.core.daily_report_generator import DailyReportGenerator
from src.plugins.multi_agent_trading import TradingSystem

# 初始化日誌系統
log_manager = LogManager()
trading_logger = log_manager.get_logger("trading")
system_logger = log_manager.get_logger("system")

# 初始化交易系統
trading_system = TradingSystem()

# 初始化報告生成器
report_generator = DailyReportGenerator()

system_logger.info("系統初始化完成")
```

2. 執行交易

```python
async def run_trading_cycle():
    # 獲取市場數據
    market_data = await fetch_market_data()
    
    # 智能體做出決策
    decisions = await trading_system.get_decisions(market_data)
    
    # 記錄決策
    for decision in decisions:
        trading_logger.info(
            f"交易信號: {decision.symbol}",
            extra=decision.to_dict()
        )
    
    # 執行交易
    results = await trading_system.execute_decisions(decisions)
    
    # 記錄執行結果
    for result in results:
        trading_logger.info(
            f"交易執行: {result['symbol']}",
            extra=result
        )

asyncio.run(run_trading_cycle())
```

3. 生成報告

```python
# 生成日常報告
daily_stats = collect_daily_stats()
report_path = report_generator.generate_daily_report(daily_stats)
print(f"日常報告已保存到: {report_path}")

# 查詢日誌
from src.core.logging_integration import LogQueryTool
query = LogQueryTool()

# 獲取今日所有交易
today_trades = query.search_logs('trading', keyword='交易信號')
print(f"今日交易數: {len(today_trades)}")

# 獲取日誌摘要
summary = query.get_log_summary('trading')
print(f"交易統計: {summary}")
```
"""

# ============================================================================
# 🔧 配置示例
# ============================================================================

"""
### config/report_config.yaml 自訂示例

# 回測報告 - 只顯示最重要的 5 個指標
backtest_report:
  default_columns:
    - strategy_name    # 策略
    - total_return     # 回報
    - sharpe_ratio     # 夏普比率
    - max_drawdown     # 最大回撤
    - win_rate         # 勝率

# 日常報告 - 顯示 6 個重點指標
daily_report:
  default_columns:
    - date            # 日期
    - symbol          # 交易對
    - daily_return    # 日回報
    - trades_count    # 交易數
    - win_rate        # 勝率
    - total_pnl       # 損益
"""

# ============================================================================
# 🚀 快速開始
# ============================================================================

"""
### 5 分鐘快速開始

1️⃣ 運行設置腳本
```bash
cd /root/comic_ai
python3 setup_logging_reports.py
```

2️⃣ 測試日誌系統
```python
from src.core.logging_integration import LogManager

manager = LogManager()
logger = manager.get_logger("test")
logger.info("Hello, Logging System!")
```

3️⃣ 生成回測報告
```python
from src.core.backtest_report_generator import BacktestResult, BacktestReportGenerator

results = [BacktestResult(...)]
generator = BacktestReportGenerator()
filepath = generator.generate_report(results)
```

4️⃣ 生成日常報告
```python
from src.core.daily_report_generator import DailyTradingStats, DailyReportGenerator

stats = [DailyTradingStats(...)]
generator = DailyReportGenerator()
filepath = generator.generate_daily_report(stats)
```

5️⃣ 查詢日誌
```python
from src.core.logging_integration import LogQueryTool

query = LogQueryTool()
recent = query.get_recent_logs("trading", limit=50)
summary = query.get_log_summary("trading")
```
"""

# ============================================================================
# 📚 文件位置
# ============================================================================

"""
核心模組:
- src/core/logging_integration.py       (300+ 行) - 日誌系統
- src/core/backtest_report_generator.py (200+ 行) - 回測報告
- src/core/daily_report_generator.py    (300+ 行) - 日常報告

配置檔:
- config/report_config.yaml             (200+ 行) - 報告配置
- .env                                   (更新) - 環境變數

設置腳本:
- setup_logging_reports.py              (400+ 行) - 自動設置

快速指南:
- LOGGING_REPORTS_QUICKSTART.md         (300+ 行) - 快速開始

現有插件:
- src/plugins/multi_agent_trading.py    (675 行) - 多智能體系統
"""

# ============================================================================
# ✨ 特點總結
# ============================================================================

"""
✅ 自動化日誌記錄
  - 所有交易和系統事件自動記錄
  - 支持多個日誌級別和類別
  - 自動日誌輪轉和備份

✅ 靈活的報告生成
  - 必看項目 CSV - 快速分析
  - 詳細版 CSV - 完整數據
  - JSON 格式 - 結構化數據
  - 自訂列選擇

✅ 方便的日誌查詢
  - 獲取最近日誌
  - 搜索關鍵字
  - 生成摘要統計

✅ 與多智能體系統無縫集成
  - 記錄每個智能體的決策
  - 追蹤決策執行過程
  - 生成性能報告

✅ 生產就緒
  - 支持本地和雲端日誌
  - 支持日誌備份和歸檔
  - 支持多環境配置
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     Comic AI 日誌和報告系統                              ║
║                   整合指南已準備好 ✅                                     ║
╚════════════════════════════════════════════════════════════════════════════╝

📁 已創建:
  ✅ src/core/logging_integration.py         (日誌系統)
  ✅ src/core/backtest_report_generator.py   (回測報告)
  ✅ src/core/daily_report_generator.py      (日常報告)
  ✅ config/report_config.yaml               (報告配置)
  ✅ setup_logging_reports.py                (設置腳本)
  ✅ LOGGING_REPORTS_QUICKSTART.md           (快速指南)

🔌 與現有系統集成:
  - src/plugins/multi_agent_trading.py       (多智能體系統)
  - 可直接集成日誌記錄功能
  - 自動生成交易報告

🚀 下一步:
  1. 查看 LOGGING_REPORTS_QUICKSTART.md
  2. 編輯 config/report_config.yaml 自訂必看項目
  3. 將日誌功能集成到您的交易系統
  4. 開始自動生成報告

📊 報告特性:
  - CSV 格式，可在 Excel 中打開
  - 自訂列選擇，精簡或詳細版本
  - 自動摘要統計
  - JSON 結構化數據

🎯 系統化分類:
  - logs/              (日誌文件)
  - reports/backtest/  (回測報告)
  - reports/daily/     (日常報告)
  - config/            (配置檔案)

✨ 已集成:
  ✅ Google Gemini API
  ✅ SQL 數據庫 (SQLite/MySQL)
  ✅ Redis 緩存
  ✅ 多雲支持 (Azure/GCP/AWS)
  ✅ 日誌系統
  ✅ 回測和日常報告
  ✅ 多智能體交易系統

完整的企業級集成解決方案已準備好！🎉
""")
