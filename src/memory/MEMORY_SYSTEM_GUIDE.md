# 🧠 Cosmic AI 記憶系統完整指南

**版本**: 1.0 | **更新日期**: 2026-04-05 | **狀態**: ✅ 生產就緒

---

## 📑 目錄

1. [系統概述](#系統概述)
2. [目錄結構](#目錄結構)
3. [核心模塊](#核心模塊)
4. [CLI 命令參考](#cli-命令參考)
5. [Python API 指南](#python-api-指南)
6. [配置和自定義](#配置和自定義)
7. [監控和維護](#監控和維護)
8. [故障排除](#故障排除)

---

## 系統概述

### 設計目標

Cosmic AI 記憶系統是一個分層、自適應的數據管理框架，用於：

- 🚀 **高性能緩存**: 多層次緩存 (L1/L2/L3) + 短期/長期分層
- 🧠 **智能管理**: 自動過期、重要性評分、智能遷移
- 🔒 **數據持久化**: 關鍵數據自動保存至長期存儲
- 📊 **實時監控**: 性能指標、清理統計、訪問追蹤
- ♻️ **自動優化**: 壓縮策略、LRU 驅逐、動態適應

### 三層記憶架構

```
┌─────────────────────────────────────────┐
│     L1 快速內存緩存 (100MB)              │
│  ├─ 最快訪問 (<1ms)                     │
│  ├─ 自動壓縮和驅逐                      │
│  └─ 適配器: 到短期/長期記憶            │
├─────────────────────────────────────────┤
│  短期記憶 (TTL = 300s)                  │
│  ├─ 容量: 1000 條條目                  │
│  ├─ LRU 驅逐策略                       │
│  ├─ 自動重要性評分                      │
│  └─ 週期性遷移至長期                   │
├─────────────────────────────────────────┤
│  長期記憶 (持久化)                      │
│  ├─ 存儲: .memory/long_term/            │
│  ├─ 格式: Pickle + JSON 元數據          │
│  ├─ 搜索: 標籤、重要性、內容            │
│  └─ 無限容量 (受磁盤限制)              │
├─────────────────────────────────────────┤
│  L2 磁盤緩存 + L3 壓縮緩存              │
│  └─ 長期存儲和高度壓縮                  │
└─────────────────────────────────────────┘
```

---

## 目錄結構

```
src/memory/
├── __init__.py                           # 包初始化
├── MEMORY_SYSTEM_GUIDE.md                # 本文檔
├── MEMORY_SYSTEM_ARCHITECTURE.md         # 架構詳解
├── QUICK_START.md                        # 快速開始指南
│
├── 核心模塊 (Core Modules)
├── memory_manager.py                     # 記憶管理器
├── memory_cache_optimization.py          # 緩存優化引擎
├── memory_cli.py                         # CLI 命令行工具
├── trade_memory.py                       # 交易記憶模塊
│
├── 配置文件 (Configuration)
├── memory_config.yaml                    # 記憶系統配置
├── cleanup_policy.yaml                   # 清理策略配置
│
├── 工具和實用程序 (Utilities)
├── memory_utils.py                       # 工具函數
├── importance_calculator.py              # 重要性計算
├── compression_policy.py                 # 壓縮策略
│
└── 文檔 (Documentation)
    ├── API_REFERENCE.md                  # API 參考
    └── EXAMPLES.md                       # 使用示例
```

---

## 核心模塊

### 1. memory_manager.py (24KB)

**主要功能**:
- 初始化和管理整個記憶系統
- 協調 L1/L2/L3 緩存層
- 管理短期和長期記憶
- 自動保存和清理機制

**關鍵類**:
```python
class MemoryManager:
    def __init__(memory_file, l1_size_mb, enable_auto_save)
    def get_cache_stats()
    def generate_memory_report()
    def cleanup_short_term_memory()
    def migrate_short_to_long_term(key)
    def memory_summary()
```

**使用示例**:
```python
from memory_manager import init_memory_manager

manager = init_memory_manager(
    memory_file="memory.md",
    l1_size_mb=100,
    enable_auto_save=True,
    auto_save_interval=60
)

# 獲取統計信息
stats = manager.get_cache_stats()

# 執行清理
cleanup_stats = manager.cleanup_short_term_memory()

# 完整摘要
summary = manager.memory_summary()
```

### 2. memory_cache_optimization.py (40KB)

**主要功能**:
- 多層緩存實現 (L1/L2/L3)
- 短期和長期記憶類
- 壓縮和去重引擎
- AI 學習和優化

**關鍵類**:
```python
class AdvancedMemoryCache:
    class ShortTermMemory      # TTL 短期存儲
    class LongTermMemory       # 持久化長期存儲
    class CompressionEngine    # 智能壓縮
    class DeduplicationEngine  # 去重處理
    class MemoryOptimizer      # 優化引擎
```

**特性**:
- 短期記憶: 300 秒 TTL + LRU 驅逐
- 長期記憶: 持久化 + 元數據追蹤
- 壓縮決策: 按內容重要性分級
- 去重機制: SHA256 哈希驗證
- 學習系統: 訪問模式分析

### 3. memory_cli.py (30KB)

**主要功能**:
- 命令行界面 (CLI)
- 記憶系統管理和監控
- 統計信息查詢
- 手動清理和遷移

**命令列表**:
```bash
python3 memory_cli.py <command> [options]

Commands:
  init                  初始化記憶系統
  status                顯示系統狀態
  report                生成記憶報告
  cache                 管理緩存操作
  optimize              運行優化
  analyze               分析模式
  short-term            管理短期記憶
  long-term             管理長期記憶
  migrate               執行遷移清理
  summary               完整摘要
```

### 4. trade_memory.py (1.1KB)

**功能**:
- 交易特定的記憶存儲
- 保存交易記錄和歷史
- 快速交易數據檢索

---

## CLI 命令參考

### 短期記憶命令

```bash
# 列出所有短期記憶條目
python3 -m memory.memory_cli short-term --action list

# 查看統計信息
python3 -m memory.memory_cli short-term --action stats
# 輸出:
# Total Entries: 0/1000
# Max Entries: 1000
# TTL (seconds): 300
# Utilization: 0.0%

# 清空所有短期記憶
python3 -m memory.memory_cli short-term --action clear
```

### 長期記憶命令

```bash
# 列出所有長期記憶條目
python3 -m memory.memory_cli long-term --action list

# 按標籤篩選
python3 -m memory.memory_cli long-term --action list --tag "models"

# 按重要性篩選
python3 -m memory.memory_cli long-term --action list --min-importance 0.8

# 搜索條目
python3 -m memory.memory_cli long-term --action search --query "config"

# 查看統計信息
python3 -m memory.memory_cli long-term --action stats
# 輸出:
# Total Entries: 15
# Total Size: 2.45 MB
# Importance Distribution:
#   - Critical (>0.8): 3
#   - High (0.5-0.8): 7
#   - Medium (0.2-0.5): 4
#   - Low (<0.2): 1
```

### 清理和遷移命令

```bash
# 執行自動清理和遷移
python3 -m memory.memory_cli migrate
# 輸出:
# 🔄 Running cleanup and migration from short-term to long-term...
# ✅ Migration completed!
#   Expired entries: 5
#   Migrated to long-term: 3
#   Deleted entries: 2
```

### 完整摘要命令

```bash
# 查看完整的記憶系統摘要
python3 -m memory.memory_cli summary
# 輸出:
# [SHORT-TERM MEMORY]
#   Entries: 0/1000
#   Utilization: 0.0%
#   TTL: 300s
#
# [LONG-TERM MEMORY]
#   Entries: 15
#   Total Size: 2.45 MB
#
# [CACHE PERFORMANCE]
#   Hit Rate: 87.3%
#   Compression Ratio: 2.15x
#
# [AI METRICS]
#   Learning Enabled: True
#   Adaptive L1 Size: 100 MB
```

---

## Python API 指南

### 初始化

```python
from src.memory.memory_manager import init_memory_manager
from src.memory.memory_cache_optimization import AdvancedMemoryCache

# 方式 1: 使用管理器
manager = init_memory_manager(
    memory_file="memory.md",
    l1_size_mb=100,
    enable_auto_save=True,
    auto_save_interval=60  # 60 秒自動保存一次
)

# 方式 2: 直接使用緩存
cache = AdvancedMemoryCache(
    l1_max_size_mb=100,
    short_term_ttl=300,        # 300 秒 (5 分鐘)
    short_term_max_entries=1000,
    enable_compression=True,
    enable_learning=True
)
```

### 存儲操作

```python
# 短期存儲 (自動過期)
cache.short_term.put("temp_key", data)

# 長期存儲 (持久化)
cache.long_term.put(
    key="model_config",
    value=config_data,
    importance=0.95,        # 0.0-1.0
    tags=["models", "critical"]
)

# L1 快速緩存
cache.put("fast_key", value)

# 檢索
temp_data = cache.short_term.get("temp_key")
config = cache.long_term.get("model_config")
cached = cache.get("fast_key")
```

### 搜索操作

```python
# 按標籤搜索
results = cache.long_term.search(
    tags=["models"],
    min_importance=0.8
)

# 搜索條目
results = cache.long_term.search(
    tags=["config"]
)

# 按重要性篩選
critical_items = cache.long_term.search(
    min_importance=0.8
)
```

### 統計和報告

```python
# 短期記憶統計
st_stats = cache.short_term.stats()
print(f"短期記憶: {st_stats['entries']} 條")

# 長期記憶統計
lt_stats = cache.long_term.stats()
print(f"長期記憶: {lt_stats['entries']} 條")

# 完整緩存統計
cache_stats = manager.get_cache_stats()

# 完整摘要
summary = manager.memory_summary()
print(summary)

# 報告生成
report = manager.generate_memory_report()
```

### 清理和遷移

```python
# 執行清理和遷移
cleanup_stats = manager.cleanup_short_term_memory()
print(f"遷移: {cleanup_stats['migrated_count']} 條")
print(f"刪除: {cleanup_stats['deleted_count']} 條")

# 手動遷移單個項目
success = manager.migrate_short_to_long_term("key_name")

# 清空短期記憶
cache.short_term.clear()

# 清空長期記憶
cache.long_term.clear()
```

---

## 配置和自定義

### 短期記憶配置

```python
# 修改 TTL (需要重新初始化)
cache.short_term.ttl_seconds = 600  # 改為 10 分鐘

# 修改最大條目數
cache.short_term.max_entries = 2000

# 查看配置
stats = cache.short_term.stats()
print(f"TTL: {stats['ttl_seconds']} 秒")
print(f"最大: {stats['max_entries']} 條")
```

### 壓縮策略

```python
# 啟用/禁用壓縮
manager.cache.enable_compression = True

# 設置壓縮級別 (0-9)
manager.cache.compressor.compression_level = 9  # 最大壓縮

# 查看壓縮統計
stats = manager.get_cache_stats()
print(f"壓縮比: {stats['overall']['compression_ratio']:.2f}x")
```

### 學習和優化

```python
# 啟用 AI 學習
manager.cache.enable_learning = True

# 獲取學習統計
if hasattr(manager.cache, 'get_learning_stats'):
    learn_stats = manager.cache.get_learning_stats()
    print(f"訪問模式: {learn_stats['total_access_patterns']}")
    print(f"熱鍵數: {learn_stats['hot_keys_count']}")

# 運行優化
optimizer = manager.cache.optimizer
suggestions = optimizer.get_optimization_suggestions()
```

---

## 監控和維護

### 性能監控

```python
import json
from src.memory.memory_manager import init_memory_manager

manager = init_memory_manager()

# 定期檢查性能
while True:
    stats = manager.get_cache_stats()
    
    # 監控關鍵指標
    hit_rate = stats['overall']['hit_rate_percent']
    memory_mb = stats['overall']['current_memory_mb']
    
    print(f"命中率: {hit_rate:.2f}%")
    print(f"內存: {memory_mb:.2f} MB")
    
    # 如果內存超過 80% 則警告
    if memory_mb > 80:
        print("⚠️  內存使用超過 80%，執行清理")
        manager.cleanup_short_term_memory()
    
    time.sleep(60)  # 每分鐘檢查一次
```

### 定期維護

```bash
# 每日執行清理
0 2 * * * /usr/bin/python3 -m memory.memory_cli migrate

# 每周生成報告
0 3 * * 0 /usr/bin/python3 -m memory.memory_cli report --output /var/log/memory_report.txt

# 每月完整優化
0 4 1 * * /usr/bin/python3 -m memory.memory_cli optimize --auto-fix
```

### 日誌和調試

```python
import logging

# 啟用詳細日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('memory_system')

# 追蹤操作
manager = init_memory_manager()
stats = manager.get_cache_stats()
logger.debug(f"L1 命中: {stats['l1']['current_size_mb']} MB")
logger.debug(f"短期記憶: {stats['short_term']['entries']} 條")
```

---

## 故障排除

### 常見問題

**問題 1: 短期記憶快速填滿**
```python
# 症狀: 短期記憶利用率 > 90%
# 解決方案 1: 增加容量
cache.short_term.max_entries = 2000

# 解決方案 2: 減少 TTL
cache.short_term.ttl_seconds = 180

# 解決方案 3: 執行清理
manager.cleanup_short_term_memory()
```

**問題 2: 壓縮率低**
```python
# 症狀: 壓縮比 < 1.5x
# 原因: 不可壓縮的數據或質量設置太高

# 解決方案: 提高壓縮級別
manager.cache.compressor.compression_level = 9

# 檢查數據類型
stats = manager.get_cache_stats()
if stats['l3']['entries'] < 100:
    print("L3 條目少，考慮更激進的壓縮")
```

**問題 3: 記憶搜索緩慢**
```python
# 症狀: 長期記憶搜索 > 1 秒
# 原因: 元數據索引未建立或條目過多

# 解決方案: 重建索引
# (注意: 這是在下一版本中實現)

# 臨時方案: 減少長期記憶大小
# 遷移部分數據到外部存儲
for entry in cache.long_term.metadata.values():
    if entry['importance'] < 0.3:
        # 備份並刪除
        pass
```

**問題 4: 自動保存失敗**
```python
# 症狀: "Auto-save failed" 警告
# 原因: 磁盤滿或權限問題

# 解決方案 1: 檢查磁盤空間
import shutil
usage = shutil.disk_usage("/")
print(f"可用空間: {usage.free / (1024**3):.2f} GB")

# 解決方案 2: 檢查權限
import os
os.chmod(".memory_state.json", 0o644)

# 解決方案 3: 清空舊快照
import glob
for f in glob.glob(".memory_snapshot_*.json"):
    os.remove(f)
```

### 調試命令

```bash
# 完整診斷
python3 -m memory.memory_cli status
python3 -m memory.memory_cli analyze

# 詳細報告
python3 -m memory.memory_cli report --output memory_report.txt

# 強制優化
python3 -m memory.memory_cli optimize --auto-fix

# 檢查配置
cat config/memory_config.yaml
```

---

## 性能基準

### 預期性能指標

| 操作 | 延遲 | 吞吐量 | 備註 |
|------|------|--------|------|
| L1 get | <1ms | 10K+ ops/s | 內存訪問 |
| 短期 get | 1-5ms | 1K+ ops/s | LRU 查找 |
| 長期 get | 5-20ms | 100+ ops/s | 磁盤讀取 |
| 搜索 | <50ms | 100+ ops/s | 元數據索引 |
| 清理 | <100ms | 1K+ entries/s | 後台任務 |

### 優化建議

1. **減少短期記憶 TTL** (如果快速填滿)
2. **增加 L1 大小** (如果命中率 < 80%)
3. **啟用壓縮** (如果磁盤空間受限)
4. **減少長期記憶條目** (如果搜索變慢)
5. **定期清理** (每天自動執行)

---

## 相關文檔

- [架構詳解](MEMORY_SYSTEM_ARCHITECTURE.md)
- [快速開始](QUICK_START.md)
- [API 參考](API_REFERENCE.md)
- [使用示例](EXAMPLES.md)

---

**最後更新**: 2026-04-05  
**維護者**: Cosmic AI Team  
**許可證**: MIT
