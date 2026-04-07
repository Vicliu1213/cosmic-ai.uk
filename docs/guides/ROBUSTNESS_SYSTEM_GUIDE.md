# Comic AI 防閃退和斷線重連系統
Crash Prevention & Auto-Reconnection System

## 📋 概述

本系統為 Comic AI 提供以下功能：

### 1️⃣ **防閃退系統 (Crash Prevention)**
- 全局異常處理
- 信號捕獲 (SIGTERM, SIGINT)
- 優雅關閉流程
- 崩潰恢復機制

### 2️⃣ **斷線重連系統 (Auto-Reconnection)**
- 自動重連機制
- 指數退避策略 (Exponential Backoff)
- 可配置重試次數和延遲
- 連接狀態監控

### 3️⃣ **健康檢查系統 (Health Check)**
- 定期健康檢查
- 自動故障檢測
- 故障自動恢復
- 運行時間追蹤

### 4️⃣ **監控和報告 (Monitoring)**
- 實時連接狀態
- 詳細的連接歷史
- 統計數據收集
- 狀態報告生成

---

## 🛠️ 核心模塊

### `system_robustness.py`

包含以下主要類：

#### 1. `ReconnectionConfig` (配置)
```python
@dataclass
class ReconnectionConfig:
    max_retries: int = 5              # 最大重試次數
    initial_delay: float = 1.0        # 初始延遲 (秒)
    max_delay: float = 60.0           # 最大延遲 (秒)
    backoff_multiplier: float = 2.0   # 指數退避倍數
    timeout: float = 30.0             # 連接超時 (秒)
    health_check_interval: float = 10.0 # 健康檢查間隔
```

#### 2. `RobustConnection` (連接管理器)
- **功能**：管理單個連接的完整生命週期
- **特性**：
  - 自動重連with指數退避
  - 定期健康檢查
  - 連接歷史追蹤
  - 詳細的指標收集

```python
# 用法示例
connection = RobustConnection(
    name="API Server",
    connect_func=lambda: api.connect(),
    health_check_func=lambda: api.is_healthy(),
    config=ReconnectionConfig(max_retries=5)
)

# 連接
connection.connect()

# 啟動健康檢查
connection.start_health_check()

# 獲取狀態
status = connection.get_status()
```

#### 3. `CrashPreventionManager` (防閃退管理器)
- **功能**：全局異常捕獲和處理
- **特性**：
  - 全局異常鉤子
  - 信號處理
  - 崩潰記錄
  - 已註冊的處理器調用

```python
# 用法示例
manager = CrashPreventionManager()

# 註冊崩潰處理器
def cleanup(exc_type, exc_value, exc_traceback):
    print("執行清理")

manager.register_crash_handler(cleanup)

# 啟動
manager.start()
```

#### 4. `SystemRobustness` (系統強健性管理器)
- **功能**：統一管理整個系統的強健性
- **特性**：
  - 集中式連接管理
  - 統一的防閃退保護
  - 系統狀態報告
  - 多連接協調

```python
# 用法示例
robustness = SystemRobustness()

# 註冊連接
robustness.register_connection(
    name="Database",
    connect_func=db_connect,
    health_check_func=db_check
)

# 啟動
robustness.start()

# 獲取狀態
robustness.print_status_report()

# 停止
robustness.stop()
```

---

## 🚀 快速開始

### 安裝

系統已內置，無需額外安裝。

### 基本使用

#### 1. 單個連接的防閃退管理

```python
from system_robustness import RobustConnection

# 定義連接函數
def connect_to_server():
    # 實現實際連接邏輯
    return server_connection

def check_server_health():
    # 實現健康檢查邏輯
    return server.is_alive()

# 創建連接管理器
connection = RobustConnection(
    name="My Server",
    connect_func=connect_to_server,
    health_check_func=check_server_health
)

# 連接
if connection.connect():
    print("連接成功")
    connection.start_health_check()
    
    # ... 執行操作 ...
    
    connection.stop_health_check()
```

#### 2. 系統級別的防閃退管理

```python
from system_robustness import initialize_robustness

# 初始化系統
robustness = initialize_robustness()

# 註冊多個連接
robustness.register_connection(
    name="API",
    connect_func=api_connect
)

robustness.register_connection(
    name="Database",
    connect_func=db_connect
)

# 註冊崩潰處理器
def cleanup(exc_type, exc_value, exc_traceback):
    print("系統崩潰，執行清理...")
    # 清理資源

robustness.register_crash_handler(cleanup)

# 打印狀態
robustness.print_status_report()
```

#### 3. 在主程序中集成

```python
from main_system import ComicAISystem

# 創建系統
system = ComicAISystem()

# 初始化（設置防閃退和連接）
system.initialize()

# 運行
system.run()
```

---

## 📊 指數退避策略

系統使用指數退避算法進行自動重連：

```
第1次重試: 延遲 1s
第2次重試: 延遲 2s (1 × 2)
第3次重試: 延遲 4s (2 × 2)
第4次重試: 延遲 8s (4 × 2)
第5次重試: 延遲 16s (8 × 2)
...
最大延遲: 60s (達到上限後保持)
```

**優勢**：
- ✅ 減少服務器負載
- ✅ 給服務器恢復時間
- ✅ 避免快速失敗循環
- ✅ 提高系統穩定性

---

## 🔍 連接狀態監控

### 連接狀態枚舉

```python
class ConnectionState(Enum):
    CONNECTED = "connected"         # 已連接
    DISCONNECTED = "disconnected"   # 已斷開
    RECONNECTING = "reconnecting"   # 正在重連
    FAILED = "failed"               # 連接失敗
```

### 獲取連接狀態

```python
status = connection.get_status()

# 返回結構:
{
    "name": "API Server",
    "state": "connected",
    "metrics": {
        "total_connections": 1,
        "successful_connections": 1,
        "failed_connections": 0,
        "total_reconnections": 0,
        "last_connection_time": "2026-02-20T15:44:31...",
        "uptime_seconds": 305.2,
        "last_error": None
    },
    "connection_history": [...]
}
```

---

## 📈 關鍵指標

| 指標 | 說明 |
|------|------|
| `total_connections` | 總連接次數 |
| `successful_connections` | 成功連接次數 |
| `failed_connections` | 失敗連接次數 |
| `total_reconnections` | 自動重連次數 |
| `uptime_seconds` | 運行時間（秒） |
| `connection_history` | 連接歷史記錄 |

---

## 🎯 常見使用場景

### 場景1: API 連接管理

```python
from system_robustness import RobustConnection, ReconnectionConfig

# 為 API 連接配置特定的重試策略
api_config = ReconnectionConfig(
    max_retries=10,           # API 允許更多重試
    initial_delay=2.0,
    max_delay=120.0,          # 允許更長的最大延遲
    backoff_multiplier=2.0
)

api_connection = RobustConnection(
    name="Trading API",
    connect_func=api.connect,
    health_check_func=api.ping,
    config=api_config
)

api_connection.connect()
```

### 場景2: 數據庫連接管理

```python
db_config = ReconnectionConfig(
    max_retries=5,
    initial_delay=1.0,
    max_delay=30.0,
    health_check_interval=5.0  # 更頻繁的檢查
)

db_connection = RobustConnection(
    name="Database",
    connect_func=db.connect,
    health_check_func=db.is_connected,
    config=db_config
)

db_connection.connect()
```

### 場景3: 多服務協調

```python
robustness = SystemRobustness()

# 添加多個服務連接
services = {
    "API": (api_connect, api_health),
    "Database": (db_connect, db_health),
    "Cache": (cache_connect, cache_health)
}

for name, (connect_fn, health_fn) in services.items():
    robustness.register_connection(
        name=name,
        connect_func=connect_fn,
        health_check_func=health_fn
    )

robustness.start()

# 所有服務自動管理連接和健康檢查
```

---

## 🔧 配置最佳實踐

### 為不同服務選擇不同配置

```python
# 關鍵服務：更積極的重試
CRITICAL_SERVICE_CONFIG = ReconnectionConfig(
    max_retries=10,
    initial_delay=1.0,
    max_delay=60.0
)

# 普通服務：標準重試
NORMAL_SERVICE_CONFIG = ReconnectionConfig(
    max_retries=5,
    initial_delay=2.0,
    max_delay=30.0
)

# 次要服務：較少重試
OPTIONAL_SERVICE_CONFIG = ReconnectionConfig(
    max_retries=3,
    initial_delay=5.0,
    max_delay=15.0
)
```

---

## 📋 故障排查

### 問題：連接一直失敗

**檢查清單**：
1. 驗證 `connect_func` 是否正確實現
2. 檢查網絡連接
3. 查看最後的錯誤信息 (`status['last_error']`)
4. 增加日誌級別以獲取更多詳情

### 問題：頻繁斷線重連

**解決方案**：
1. 檢查 `health_check_func` 邏輯
2. 增加 `health_check_interval`
3. 檢查遠程服務的穩定性
4. 查看連接歷史以識別模式

### 問題：重試次數過多

**調整**：
```python
config = ReconnectionConfig(
    max_retries=3,           # 減少重試次數
    initial_delay=5.0,       # 增加初始延遲
    backoff_multiplier=3.0   # 增加退避倍數
)
```

---

## 📝 日誌示例

```
2026-02-20 15:44:31,430 - SystemRobustness - INFO - 🚀 Comic AI 防閃退和斷線重連系統啟動
2026-02-20 15:44:31,430 - SystemRobustness - INFO - 🛡️ 防閃退保護已啟動
2026-02-20 15:44:31,430 - SystemRobustness - INFO - [API Server] 開始連接...
2026-02-20 15:44:31,431 - SystemRobustness - INFO - [API Server] ✅ 連接成功 (嘗試 #1)
2026-02-20 15:44:31,430 - SystemRobustness - INFO - [API Server] 🏥 健康檢查已啟動
```

---

## 🎓 完整示例

```python
#!/usr/bin/env python3
from system_robustness import (
    initialize_robustness,
    ReconnectionConfig
)
import time

# 初始化系統
robustness = initialize_robustness()

# 定義連接函數
def connect_api():
    print("連接到 API...")
    return {"type": "api", "status": "ok"}

def check_api_health():
    print("檢查 API 健康...")
    return True

# 註冊連接
api = robustness.register_connection(
    name="Trading API",
    connect_func=connect_api,
    health_check_func=check_api_health,
    config=ReconnectionConfig(max_retries=5)
)

# 連接
api.connect()

# 運行5秒
try:
    for i in range(5):
        print(f"✅ 系統運行中... ({i+1}s)")
        time.sleep(1)
except KeyboardInterrupt:
    print("\n中斷")
finally:
    robustness.stop()
    robustness.print_status_report()
```

---

## ✅ 系統功能清單

- ✅ 全局異常捕獲和處理
- ✅ 自動重連 with 指數退避
- ✅ 定期健康檢查
- ✅ 連接狀態監控
- ✅ 詳細指標收集
- ✅ 優雅關閉機制
- ✅ 信號處理 (SIGTERM, SIGINT)
- ✅ 多連接管理
- ✅ 可配置的重試策略
- ✅ 實時狀態報告

---

## 📞 支持

如有問題或建議，請查看日誌文件或代碼註釋。

---

**最後更新**: 2026-02-20
