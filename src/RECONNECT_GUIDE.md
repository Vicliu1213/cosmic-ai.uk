# 自動重連系統文檔

## 概述

自動重連系統是為 Cosmic AI 交易系統設計的容錯機制。當系統發生意外閃退或連接中斷時，系統會自動嘗試重新連接和重啟，確保交易的連續性。

## 🎯 核心功能

### 1. 自動重連 (AutoReconnect)
- **指數退避算法**: 智能計算重連等待時間
- **抖動機制**: 防止同時重連導致的連鎖故障
- **可配置重試**: 支持自定義重試次數和延遲

### 2. 系統守護 (SystemGuard)
- **系統監控**: 持續監控系統健康狀態
- **自動重啟**: 系統異常時自動重啟
- **崩潰計數**: 追蹤系統崩潰次數，防止無限重啟

### 3. 健康檢查
- **定期檢查**: 每 3 秒檢查一次系統狀態
- **狀態驗證**: 檢查系統是否正常運行
- **故障定位**: 記錄詳細的故障信息

## ⚙️ 配置參數

```python
ReconnectConfig(
    max_retries=5,          # 最大重試次數
    initial_delay=1.0,      # 初始延遲（秒）
    max_delay=60.0,         # 最大延遲（秒）
    backoff_factor=2.0,     # 退避因子（倍數增長）
    jitter=True             # 是否添加隨機抖動
)
```

### 參數說明

- **max_retries**: 在放棄前最多重試的次數
  - 默認: 5次
  - 範圍: 1-100

- **initial_delay**: 第一次重連的等待時間
  - 默認: 1.0 秒
  - 用途: 給系統恢復的時間

- **max_delay**: 最大等待時間上限
  - 默認: 60.0 秒
  - 作用: 防止等待時間過長

- **backoff_factor**: 每次重試的延遲倍增因子
  - 默認: 2.0
  - 計算: 延遲 = initial_delay × (backoff_factor ^ 重試次數)
  - 例: 1s → 2s → 4s → 8s → 16s

- **jitter**: 是否添加隨機抖動
  - 默認: True
  - 作用: 減少同時重連的概率

## 🚀 使用方式

### 1. 啟用自動重連（推薦）

```python
import asyncio
from main import main, SystemConfig

# 自動重連已在 main() 中默認啟用
config = SystemConfig(
    mode="live",
    symbols=["BTCUSDT", "ETHUSDT"]
)

# 啟用自動重連
await main(config, enable_auto_reconnect=True)
```

### 2. 禁用自動重連

```python
# 如果需要關閉自動重連
await main(config, enable_auto_reconnect=False)
```

### 3. 自定義重連配置

```python
from core.reconnect_manager import SystemGuard, ReconnectConfig

# 創建自定義配置
config = ReconnectConfig(
    max_retries=10,        # 增加重試次數
    initial_delay=2.0,     # 增加初始延遲
    max_delay=120.0,       # 增加最大延遲
    backoff_factor=1.5,    # 減小增長因子
    jitter=True
)

# 使用自定義配置
guard = SystemGuard(system, config)
```

### 4. 直接使用 AutoReconnect

```python
from core.reconnect_manager import AutoReconnect, ReconnectConfig

reconnect = AutoReconnect()

# 執行操作並自動重連
result = await reconnect.execute_with_retry(
    operation=async_operation,
    operation_name="數據同步"
)
```

## 📊 重連流程

```
操作執行
    ↓
[成功] → 返回結果，重置計數
    ↓
[失敗] → 記錄錯誤
    ↓
是否超過重試次數?
    ├─ [是] → 放棄，拋出異常
    └─ [否] → 計算等待時間
            ↓
        等待 (with jitter)
            ↓
        重試操作
```

## 🔍 日誌輸出示例

### 成功情況
```
2026-04-07 16:30:45 [INFO] 🔄 執行 系統啟動...
2026-04-07 16:30:46 [INFO] ✓ 系統啟動 成功
```

### 重連情況
```
2026-04-07 16:30:45 [INFO] 🔄 執行 模塊初始化...
2026-04-07 16:30:46 [ERROR] ✗ 模塊初始化 失敗 (嘗試 1/5)
2026-04-07 16:30:46 [ERROR]   錯誤: Connection timeout
2026-04-07 16:30:46 [INFO] ⏳ 將在 1.2 秒後重試...
2026-04-07 16:30:47 [INFO] 🔄 執行 模塊初始化...
2026-04-07 16:30:48 [INFO] ✓ 模塊初始化 成功
```

### 失敗情況
```
2026-04-07 16:30:45 [INFO] 🔄 執行 系統啟動...
2026-04-07 16:30:46 [ERROR] ✗ 系統啟動 失敗 (嘗試 1/5)
2026-04-07 16:30:46 [INFO] ⏳ 將在 1.2 秒後重試...
2026-04-07 16:30:47 [INFO] 🔄 執行 系統啟動...
...
2026-04-07 16:30:56 [ERROR] ✗ 系統啟動 失敗 (嘗試 5/5)
2026-04-07 16:30:56 [ERROR] ❌ 達到最大重試次數，放棄 系統啟動
```

## 🛡️ 系統守護者 (SystemGuard)

### 功能

自動監控系統狀態，當系統異常時自動重啟。

### 使用示例

```python
from core.reconnect_manager import SystemGuard, ReconnectConfig

# 創建守護者
guard = SystemGuard(system, ReconnectConfig())

# 啟動帶保護的系統
success = await guard.start_with_protection()

if success:
    # 監控並自動重啟
    await guard.monitor_and_restart()
else:
    print("系統啟動失敗")
```

### 監控策略

- **檢查間隔**: 每 3 秒檢查一次
- **崩潰限制**: 最多允許 10 次崩潰
- **自動重啟**: 超過限制時放棄重啟

## 📈 性能影響

| 操作 | 響應時間 | CPU | 記憶體 |
|------|---------|-----|--------|
| 首次啟動 | 正常 | 正常 | 正常 |
| 健康檢查 | <100ms | <1% | <5MB |
| 重連等待 | 1-60s | <0.1% | <1MB |

## 🔐 最佳實踐

### 1. 配置建議

```python
# 保守配置（適合生產環境）
ReconnectConfig(
    max_retries=5,
    initial_delay=2.0,
    max_delay=30.0,
    backoff_factor=2.0
)

# 激進配置（適合開發環境）
ReconnectConfig(
    max_retries=10,
    initial_delay=0.5,
    max_delay=60.0,
    backoff_factor=1.5
)
```

### 2. 錯誤處理

```python
try:
    result = await reconnect.execute_with_retry(operation)
except RuntimeError as e:
    logger.error(f"操作失敗: {e}")
    # 進行善後處理
```

### 3. 監控和告警

```python
status = guard.get_status()
if status['crash_count'] > 5:
    # 觸發告警
    send_alert(f"系統多次崩潰: {status['crash_count']} 次")
```

## 🐛 故障排查

### 問題：無限重試

**原因**: 根本問題未解決
**解決**: 
- 增加 `max_retries`
- 檢查根本原因（日誌）
- 増加 `initial_delay`

### 問題：重試太頻繁

**原因**: `initial_delay` 太小
**解決**: 增加 `initial_delay` 值

### 問題：等待時間過長

**原因**: `max_delay` 太大
**解決**: 減小 `max_delay` 或增加 `backoff_factor`

### 問題：重連不工作

**原因**: RECONNECT_ENABLED 為 False
**解決**: 確保 `reconnect_manager` 模塊可以導入

## 📝 事件日誌

所有重連事件都被記錄在 `src/logs/cosmic_ai.log` 中：

```bash
# 查看最近的重連事件
tail -f src/logs/cosmic_ai.log | grep -E "重試|重連|重啟"

# 統計重連次數
grep "執行" src/logs/cosmic_ai.log | wc -l
```

## 🔄 更新日誌

- **2026-04-07**: 初始版本發佈
  - 實現自動重連機制
  - 添加系統守護者
  - 支持自定義配置

---

**版本**: 1.0
**狀態**: ✅ 生產就緒
**最後更新**: 2026-04-07
