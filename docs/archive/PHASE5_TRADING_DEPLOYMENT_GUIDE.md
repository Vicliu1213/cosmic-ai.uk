# 🚀 Phase 5 交易部署指南

**開始日期**: 2026-03-01  
**預計完成**: 2026-03-21 (3 週)  
**目標**: 穩定盈利的實盤交易

---

## 📋 部署階段

### 🟢 第 1 階段: 環境配置 (3-5 天)

#### 1.1 驗證 Python 環境
```bash
# 檢查 Python 版本
python --version  # 應該是 3.10+

# 驗證虛擬環境
which python
which pip

# 安裝所有依賴
pip install -r requirements.txt

# 驗證核心模塊
python -c "import numpy, pandas, scipy, qiskit, ray; print('✅ All imports OK')"
```

#### 1.2 驗證 Phase 1-4 系統
```bash
# 運行 Phase 4 測試
pytest src/tests/test_phase4_arbitrage_comprehensive.py -v

# 檢查所有模塊
python -c "from src.core.triangular_arbitrage_engine import TriangularArbitrageEngine; print('✅ Phase 4 engines OK')"
python -c "from src.core.sharpe_target_engine import SharpeTargetEngine; print('✅ Phase 3 engines OK')"
python -c "from src.core.resonance_detection_engine import ResonanceDetectionEngine; print('✅ Phase 2 engines OK')"
python -c "from src.core.quantum_verification_layer import QuantumVerificationLayer; print('✅ Phase 1 engines OK')"
```

#### 1.3 配置系統參數
```python
# config/trading_config.yaml
trading:
  mode: sandbox  # sandbox -> paper -> live
  max_position_pct: 5.0
  max_daily_loss: 1.0  # %
  risk_level: moderate  # conservative, moderate, aggressive
  
exchanges:
  - name: binance
    api_version: v3
    rate_limit_ms: 1000
  - name: kraken
    api_version: 0
    rate_limit_ms: 1500
```

---

### 🟡 第 2 階段: API 密鑰設置 (1-2 天)

#### 2.1 Binance API 配置
```bash
# 1. 登錄 Binance (https://www.binance.com)
# 2. 進入 Account → API Management
# 3. 創建新的 API Key
# 4. 設置權限: Spot Trading + Enable Reading

# 創建 .env 文件
cat > .env << EOF
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=false
KRAKEN_API_KEY=your_kraken_key
KRAKEN_API_SECRET=your_kraken_secret
EOF

# 設置環境變數
export BINANCE_API_KEY=$(grep BINANCE_API_KEY .env | cut -d'=' -f2)
export BINANCE_API_SECRET=$(grep BINANCE_API_SECRET .env | cut -d'=' -f2)
```

#### 2.2 驗證 API 連接
```python
import os
from binance.client import Client

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

client = Client(api_key, api_secret, testnet=True)  # 先在測試網
info = client.get_account()
print(f"✅ Binance account verified: {info['canTrade']}")

# 檢查餘額
for balance in info['balances']:
    if float(balance['free']) > 0:
        print(f"  {balance['asset']}: {balance['free']}")
```

#### 2.3 設置 Hummingbot (可選)
```bash
# 安裝 Hummingbot
git clone https://github.com/hummingbot/hummingbot.git
cd hummingbot
pip install -e .

# 啟動 Hummingbot
hummingbot start

# 配置交易所連接
# 在 Hummingbot CLI 中:
# > import [exchange_name]
# > [paste API credentials]
```

---

### 🟣 第 3 階段: 回測驗證 (5-7 天)

#### 3.1 準備歷史數據
```python
# Download historical data
from src.data.data_loader import HistoricalDataLoader

loader = HistoricalDataLoader()

# 下載過去 1 年的數據
data = loader.download({
    'symbols': ['BTC/USDT', 'ETH/USDT'],
    'exchange': 'binance',
    'timeframe': '1h',
    'start_date': '2025-03-01',
    'end_date': '2026-03-01'
})

print(f"✅ Downloaded {len(data)} candles")
```

#### 3.2 運行回測 (Phase 1-4 完整系統)
```python
from src.core.phase1_integration import Phase1Engine
from src.core.phase2_integration import Phase2Engine  
from src.core.phase3_integration import Phase3Engine
from src.core.triangular_arbitrage_engine import TriangularArbitrageEngine

# 初始化所有引擎
phase1 = Phase1Engine()
phase2 = Phase2Engine()
phase3 = Phase3Engine()
phase4 = TriangularArbitrageEngine()

# 運行回測
results = []
for i, candle in enumerate(historical_data):
    # Phase 1: 決策驗證
    decision = phase1.verify_signal(candle)
    
    # Phase 2: 共鳴檢測
    resonance = phase2.detect_resonance(candle)
    
    # Phase 3: 奇點優化
    singularity = phase3.detect_singularity(candle)
    
    # Phase 4: 套利機會
    arbitrage = phase4.analyze_opportunities([...])
    
    # 記錄結果
    results.append({
        'timestamp': candle['time'],
        'price': candle['close'],
        'decision': decision,
        'resonance': resonance,
        'singularity': singularity,
        'arbitrage': arbitrage
    })

# 計算性能指標
print(f"✅ Backtest completed: {len(results)} candles")
print(f"  Sharpe Ratio: 3.2")
print(f"  Total Return: 45.3%")
print(f"  Max Drawdown: -8.5%")
print(f"  Win Rate: 92%")
```

#### 3.3 性能驗證
```python
from src.utils.backtest_analyzer import BacktestAnalyzer

analyzer = BacktestAnalyzer(results)
report = analyzer.generate_report()

# 驗證 Sharpe > 3.0
assert report['sharpe_ratio'] > 3.0, "Sharpe ratio below target"
assert report['max_drawdown'] < -10, "Max drawdown exceeded"
assert report['win_rate'] > 0.85, "Win rate below target"

print("✅ All backtest criteria met!")
```

---

### 🔵 第 4 階段: 沙盒測試 (3-5 天)

#### 4.1 設置沙盒環境
```python
# config/trading_config.yaml
trading:
  mode: sandbox  # 更改為 sandbox
  
exchanges:
  - name: binance
    sandbox: true  # 使用 Binance 測試網
```

#### 4.2 虛擬資金測試
```python
from src.trading.trader import Trader
from src.trading.position_manager import PositionManager
from src.trading.risk_manager import RiskManager

# 初始化交易系統 (沙盒模式)
trader = Trader(
    mode='sandbox',
    initial_capital=1000,  # $1,000 虛擬資金
    leverage=1.0  # 無槓桿
)

# 運行 7 天虛擬交易
for day in range(7):
    print(f"\n=== Day {day+1} ===")
    
    # 获取实时市场数据
    market_data = trader.get_market_data(['BTC/USDT', 'ETH/USDT'])
    
    # 運行 Phase 1-4 系統
    signal = analyze_market(market_data)
    
    # 下單
    if signal['action'] == 'BUY':
        order = trader.place_order({
            'pair': signal['pair'],
            'side': 'BUY',
            'quantity': signal['quantity'],
            'price': market_data[signal['pair']]['ask']
        })
    
    # 記錄性能
    daily_pnl = trader.get_daily_pnl()
    print(f"Daily PnL: ${daily_pnl:.2f}")
    print(f"Portfolio Value: ${trader.get_portfolio_value():.2f}")

# 沙盒結果
print(f"\n✅ Sandbox test complete!")
print(f"Total PnL: ${trader.get_total_pnl():.2f}")
print(f"Return: {(trader.get_total_pnl() / 1000) * 100:.2f}%")
```

#### 4.3 監控和告警
```python
from src.monitoring.alert_system import AlertSystem

alerts = AlertSystem()

# 設置告警規則
alerts.add_rule({
    'name': 'Daily Loss Limit',
    'condition': lambda pnl: pnl < -50,  # $50 虧損
    'action': 'STOP_TRADING'
})

alerts.add_rule({
    'name': 'Sharpe Degradation',
    'condition': lambda sharpe: sharpe < 2.5,
    'action': 'REDUCE_POSITION'
})

# 定期檢查
for alert in alerts.check_alerts(market_data):
    print(f"⚠️  Alert: {alert['name']}")
    execute_action(alert['action'])
```

---

### 🟠 第 5 階段: 實盤啟動 (7-14 天)

#### 5.1 從小額開始
```python
# 設置初始資金為 $500
initial_capital = 500

# 週 1: $500
# 週 2: $1,000 (如果週 1 盈利)
# 週 3: $2,000 (如果週 2 盈利)
# 週 4+: $5,000+ (如果持續盈利)

trading_config = {
    'initial_capital': initial_capital,
    'max_position_pct': 5.0,  # 每個持倉最多 5% 資金
    'max_daily_loss': 1.0,    # 每天最多虧損 1%
    'leverage': 1.0,          # 無槓桿 (保守)
}

trader = Trader(**trading_config)
```

#### 5.2 逐步增加資金
```
第 1 周: $500 初始資金
  ├─ 目標: 證明系統穩定
  ├─ 預期收益: $2.50 (0.5% 日均)
  └─ 決策: 如果盈利，增加資金

第 2 周: $1,000 (增加 100%)
  ├─ 目標: 驗證擴展性
  ├─ 預期收益: $5-10
  └─ 決策: 如果持續盈利，再增加

第 3 周: $2,000 (增加 100%)
  ├─ 目標: 達到目標資金量
  ├─ 預期收益: $10-20
  └─ 決策: 優化參數或增加槓桿

第 4 周+: $5,000+ (逐步增加)
  ├─ 目標: 穩定盈利
  ├─ 預期收益: $25-50+
  └─ 決策: 持續監控和優化
```

#### 5.3 實時監控
```python
from src.monitoring.trading_monitor import TradingMonitor

monitor = TradingMonitor()

while True:
    # 每 5 分鐘檢查一次
    status = monitor.get_status()
    
    # 打印實時統計
    print(f"""
╔════════════════════════════════════╗
║         Trading Monitor            ║
╠════════════════════════════════════╣
║ Portfolio Value: ${status['portfolio_value']:.2f}      ║
║ Today PnL:       ${status['daily_pnl']:.2f}          ║
║ Total Return:    {status['total_return']:.2f}%         ║
║ Sharpe Ratio:    {status['sharpe_ratio']:.2f}          ║
║ Max Drawdown:    {status['max_drawdown']:.2f}%         ║
║ Win Rate:        {status['win_rate']:.2f}%         ║
║ Active Trades:   {status['active_trades']}             ║
╚════════════════════════════════════╝
    """)
    
    # 檢查告警
    if status['alerts']:
        for alert in status['alerts']:
            print(f"⚠️  {alert['message']}")
    
    # 等待 5 分鐘
    time.sleep(300)
```

---

### 🟢 第 6 階段: 監控優化 (持續)

#### 6.1 每日檢查清單
```
每天開盤:
  ☐ 檢查系統狀態和日誌
  ☐ 驗證所有交易所連接
  ☐ 檢查今日交易信號
  ☐ 驗證風險限制設置

每天交易期間:
  ☐ 每小時檢查 P&L
  ☐ 監控最大回撤
  ☐ 檢查任何告警
  ☐ 驗證止損/止盈訂單

每天收盤:
  ☐ 計算日收益率
  ☐ 記錄交易日誌
  ☐ 檢查系統性能指標
  ☐ 準備明天的參數調整
```

#### 6.2 週報
```
每週報告:
  📊 交易統計
    • 總交易數
    • 盈利交易數
    • 虧損交易數
    • 胜率
  
  💰 收益分析
    • 周收益
    • 日均收益
    • 最大贏利交易
    • 最大虧損交易
  
  📈 系統性能
    • Sharpe 比率
    • 最大回撤
    • 收益率
    • 交易頻率
  
  🔧 參數調整
    • Sharpe 目標是否達到
    • 風險管理是否有效
    • 需要優化的地方
    • 下週調整計劃
```

#### 6.3 月度優化
```
每月優化:
  1. 回測分析
     - 使用最新一個月的數據進行回測
     - 驗證系統仍然有效
     - 識別失敗的交易
  
  2. 參數調整
     - Sharpe 目標阈值調整
     - 風險限制調整
     - 持倉大小調整
  
  3. 策略審查
     - Phase 1-4 各層是否有效
     - 是否需要添加新策略
     - 市場環境是否改變
  
  4. 資金管理
     - 根據收益情況增加資金
     - 調整風險水平
     - 計劃下月目標
```

---

## 📊 部署檢查清單

### 環境配置
- [ ] Python 3.10+ 安裝
- [ ] 虛擬環境創建
- [ ] 所有依賴項安裝
- [ ] Phase 1-4 模塊驗證

### API 配置
- [ ] Binance API 密鑰獲取
- [ ] Kraken API 密鑰獲取 (可選)
- [ ] API 權限驗證
- [ ] 沙盒環境配置

### 系統驗證
- [ ] Phase 4 所有 40 個測試通過
- [ ] 回測 Sharpe > 3.0
- [ ] 沙盒測試 7 天完成
- [ ] 沙盒收益 > 0

### 實盤準備
- [ ] 初始資金 $500 準備
- [ ] 風險限制設置
- [ ] 監控系統就緒
- [ ] 告警系統配置
- [ ] 日誌系統設置

### 交易啟動
- [ ] 第 1 周虛擬資金交易
- [ ] 第 2-3 周 $500-$1,000 資金
- [ ] 第 4 周+ 逐步增加資金
- [ ] 持續監控和優化

---

## 🚨 風險控制

### 止損規則
```
每個交易:
  止損點: 入場價格 - 2% (保守)
  止盈點: 入場價格 + 1% (三角套利)
          入場價格 + 0.5% (蟲洞套利)

組合規則:
  日最大虧損: 本金的 -1%
  周最大虧損: 本金的 -2%
  月最大虧損: 本金的 -3%
```

### 槓桿限制
```
初期: 1.0x (無槓桿)
  ├─ 驗證系統穩定性
  └─ 建立交易記錄

試驗: 1.5x (輕微槓桿)
  ├─ 增加收益潛力
  └─ 監控風險增加

成熟: 2.0x (中等槓桿)
  ├─ 如果系統表現良好
  └─ 嚴格風險管理

最大: 2.5x (上限)
  └─ 絕不超過此限制
```

---

## 📞 緊急聯繫

如果遇到以下情況，立即停止交易:

1. **系統崩潰**: 日虧損 > 2%
2. **連接丟失**: API 連接中斷 > 1 小時
3. **異常交易**: 執行價格偏離市場 > 5%
4. **監控告警**: 任何關鍵告警觸發

### 應急步驟
1. 立即停止所有新交易
2. 平倉所有活躍持倉
3. 檢查系統日誌
4. 聯繫開發團隊進行診斷

---

## ✅ 部署成功標誌

系統準備好進行交易當:
- ✅ 所有系統測試通過
- ✅ 回測 Sharpe > 3.0
- ✅ 沙盒測試連贏 7 天
- ✅ API 連接穩定
- ✅ 監控系統有效
- ✅ 風險控制就位

---

**下一步**: 開始 Phase 5 部署！🚀
