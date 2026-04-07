# 📊 記憶系統分層管理指南

**版本**: 1.0 | **更新日期**: 2026-04-05 | **狀態**: ✅ 生產就緒

---

## 📑 目錄

1. [分層架構概述](#分層架構概述)
2. [各層責任](#各層責任)
3. [層級間數據流](#層級間數據流)
4. [重要性評分系統](#重要性評分系統)
5. [分層管理策略](#分層管理策略)
6. [監控分層性能](#監控分層性能)
7. [實踐最佳方案](#實踐最佳方案)

---

## 分層架構概述

### 完整分層模型

```
┌──────────────────────────────────────────────────────────┐
│                  應用層 (Application Layer)               │
│              (業務邏輯、決策制定)                         │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────────────────────┐
│            訪問層 (Access Layer)                           │
│    ├─ 讀操作 (GET)  → 優先 L1 → L2 → L3 → ST → LT      │
│    └─ 寫操作 (PUT)  → L1, 同時寫 ST 或 LT               │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────┬──────┴──────┬────┐
        ↓    ↓             ↓    ↓
┌──────────────────────────────────────────────────────────┐
│             緩存層 (Memory Hierarchy)                      │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ L1 快速內存緩存 (100MB)                          │    │
│  │ • 訪問時間: <1ms                                │    │
│  │ • 優先級: 最高                                  │    │
│  │ • 策略: LRU 驅逐                               │    │
│  │ • 壓縮: 無                                      │    │
│  └──────────┬────────────────────────────────────┘    │
│             ↓ (滿載/冷卻)                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 短期記憶 (ST: 1000條, TTL=300s)                 │    │
│  │ • 訪問時間: 1-5ms                              │    │
│  │ • 優先級: 高                                    │    │
│  │ • 策略: LRU 驅逐 + TTL 過期                     │    │
│  │ • 壓縮: 基於重要性                              │    │
│  │ • 重要性 > 0.6 → 遷移至長期                    │    │
│  └──────────┬────────────────────────────────────┘    │
│             ↓ (冷卻/歷史)                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 長期記憶 (LT: 無限, 持久化)                      │    │
│  │ • 訪問時間: 5-20ms                             │    │
│  │ • 優先級: 中                                    │    │
│  │ • 策略: 按重要性管理                             │    │
│  │ • 壓縮: 基於重要性                              │    │
│  │ • 存儲: .memory/long_term/                     │    │
│  └──────────┬────────────────────────────────────┘    │
│             ↓ (存檔/導出)                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │ L2 磁盤緩存 (.cache/l2)                         │    │
│  │ • 訪問時間: 10-50ms                            │    │
│  │ • 優先級: 低                                    │    │
│  │ • 策略: 溢出存儲                                │    │
│  │ • 壓縮: 標準                                    │    │
│  └──────────┬────────────────────────────────────┘    │
│             ↓ (長期存檔)                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │ L3 壓縮緩存 (.cache/l3)                         │    │
│  │ • 訪問時間: 50-200ms                           │    │
│  │ • 優先級: 極低                                  │    │
│  │ • 策略: 高度壓縮                                │    │
│  │ • 壓縮: 最大 (Level 9)                         │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 各層責任

### L1 快速內存緩存

**職責**:
- 存儲最頻繁訪問的數據
- 提供最低延遲的訪問
- 自動 LRU 驅逐管理

**特性**:
```python
{
    "capacity": "100 MB",
    "access_time": "<1ms",
    "eviction_policy": "LRU",
    "compression": "None",
    "expiration": "None",
    "priority": "HIGHEST"
}
```

**何時使用**:
- 實時交易信息
- 當前用戶會話
- 頻繁訪問的配置

### 短期記憶 (ST)

**職責**:
- 存儲臨時數據
- 自動過期管理
- 自動重要性評分
- 周期性遷移至長期

**特性**:
```python
{
    "capacity": "1000 entries",
    "access_time": "1-5ms",
    "ttl": "300 seconds",
    "eviction_policy": "LRU + TTL Expiration",
    "compression": "Importance-based",
    "migration_threshold": 0.6,
    "priority": "HIGH"
}
```

**何時使用**:
- API 響應緩存
- 中間計算結果
- 臨時存儲數據
- 日誌和事件流

**清理週期**:
```python
# 每 10 次自動保存清理一次
save_count = 0
def auto_save():
    global save_count
    save_count += 1
    if save_count % 10 == 0:
        cleanup_short_term_memory()
```

### 長期記憶 (LT)

**職責**:
- 存儲關鍵和重要數據
- 持久化管理
- 搜索和檢索功能
- 元數據維護

**特性**:
```python
{
    "capacity": "Unlimited (Disk)",
    "access_time": "5-20ms",
    "storage_format": "Pickle + JSON",
    "storage_location": ".memory/long_term/",
    "compression": "Importance-based",
    "expiration": "None (Persistent)",
    "priority": "MEDIUM"
}
```

**何時使用**:
- 模型配置和參數
- 交易歷史記錄
- 用戶持久化數據
- 系統配置
- 分析結果

### L2 磁盤緩存

**職責**:
- L1 溢出存儲
- 中期數據保存
- 備份和恢復

**特性**:
```python
{
    "location": ".cache/l2",
    "compression": "Standard",
    "expiration": "Auto-cleanup",
    "priority": "LOW"
}
```

### L3 壓縮緩存

**職責**:
- 長期存檔
- 高度壓縮
- 節省磁盤空間

**特性**:
```python
{
    "location": ".cache/l3",
    "compression": "Maximum (Level 9)",
    "expiration": "Manual cleanup",
    "priority": "VERY_LOW"
}
```

---

## 層級間數據流

### 寫入流程 (PUT)

```
應用寫入數據
    ↓
1. 確定目標層級
    ├─ 臨時數據? → 短期記憶
    ├─ 關鍵數據? → 長期記憶
    └─ 頻繁訪問? → L1 + 短期
    ↓
2. 計算重要性分數 (0.0-1.0)
    ├─ API鑰匙、配置 → 0.8-0.9 (CRITICAL)
    ├─ 結構化數據 → 0.5-0.7 (HIGH)
    ├─ 臨時數據 → 0.2-0.5 (MEDIUM)
    └─ 日誌 → 0.0-0.3 (LOW)
    ↓
3. 決定壓縮策略
    ├─ 重要性 > 0.8 → 不壓縮 (原質量)
    ├─ 重要性 0.5-0.8 → 輕度壓縮
    ├─ 重要性 0.2-0.5 → 標準壓縮
    └─ 重要性 < 0.2 → 最大壓縮
    ↓
4. 寫入存儲
    ├─ 寫入目標層級
    └─ 記錄元數據 (時間戳、重要性、訪問計數)
    ↓
應用確認完成
```

### 讀取流程 (GET)

```
應用請求數據
    ↓
1. 檢查 L1 快速內存
    ├─ 命中 (HIT) → 返回數據 (記錄訪問)
    └─ 缺失 (MISS) ↓
    
2. 檢查短期記憶
    ├─ 命中 ✓
    │   ├─ 檢查 TTL (未過期?) → 返回數據
    │   └─ 過期? → 檢查重要性 → 遷移或刪除
    └─ 缺失 ↓
    
3. 檢查長期記憶
    ├─ 命中 ✓ → 返回數據 (晉升至 L1)
    └─ 缺失 ↓
    
4. 檢查 L2/L3 磁盤緩存
    ├─ 命中 ✓ → 返回數據 (晉升至 L1)
    └─ 缺失 ↓
    
5. 數據不存在 → 返回 None
    (可能觸發數據庫或外部源查詢)

應用獲得數據
```

### 遷移流程 (MIGRATION)

```
短期記憶清理週期 (每 10 次自動保存)
    ↓
1. 掃描過期條目 (age > TTL)
    ├─ 未過期 → 保留在短期
    └─ 已過期 ↓
    
2. 計算重要性分數
    ├─ > 0.6 (重要) ↓
    ├─ ≤ 0.6 (不重要) → 刪除 ✓
    
3. 遷移至長期記憶
    ├─ 保存數據 (Pickle)
    ├─ 保存元數據 (JSON)
    ├─ 記錄源信息
    └─ 刪除短期副本
    ↓
4. 生成清理統計
    ├─ expired_count: 過期條目數
    ├─ migrated_count: 遷移至長期數
    ├─ deleted_count: 刪除條目數
    └─ memory_freed_mb: 釋放內存
    ↓
清理完成，更新記憶系統報告
```

---

## 重要性評分系統

### 評分規則

```python
IMPORTANCE_LEVELS = {
    "CRITICAL": (0.8, 1.0),    # API鑰匙、配置、密鑰
    "HIGH": (0.5, 0.8),         # 交易記錄、模型參數
    "MEDIUM": (0.2, 0.5),       # 臨時結果、計算中間值
    "LOW": (0.0, 0.2)           # 日誌、診斷信息
}
```

### 自動評分邏輯

```python
def calculate_importance(key: str, value: Any) -> float:
    """計算內容重要性分數"""
    
    score = 0.5  # 基礎分數
    
    # 1. 鍵名分析
    critical_keywords = [
        'api_key', 'secret', 'config', 'model', 
        'password', 'token', 'private'
    ]
    for keyword in critical_keywords:
        if keyword in key.lower():
            score += 0.3  # 高優先級關鍵詞
            break
    
    # 2. 值類型分析
    if isinstance(value, dict):
        score += 0.2  # 結構化數據更重要
    elif isinstance(value, (list, tuple)):
        score += 0.1
    elif isinstance(value, str):
        if len(value) > 1000:  # 大字符串
            score -= 0.1
    
    # 3. 訪問頻率 (如果有歷史)
    if hasattr(value, '_access_count'):
        if value._access_count > 100:
            score += 0.2
        elif value._access_count < 5:
            score -= 0.1
    
    # 4. 時間敏感性
    current_time = time.time()
    if hasattr(value, '_created_at'):
        age = current_time - value._created_at
        if age < 60:  # 剛創建
            score += 0.1
        elif age > 3600:  # 超過 1 小時
            score -= 0.2
    
    # 正規化到 0.0-1.0
    return max(0.0, min(1.0, score))
```

### 壓縮決策矩陣

| 重要性 | 範圍 | 壓縮級別 | 質量損失 | 存儲節省 |
|--------|------|---------|---------|---------|
| CRITICAL | 0.8-1.0 | 無 (0) | 0% | 0% |
| HIGH | 0.5-0.8 | 輕度 (3) | 5% | 40% |
| MEDIUM | 0.2-0.5 | 標準 (6) | 15% | 70% |
| LOW | 0.0-0.2 | 最大 (9) | 30% | 90% |

```python
def get_compression_level(importance: float) -> int:
    """根據重要性確定壓縮級別"""
    if importance >= 0.8:
        return 0    # 無壓縮
    elif importance >= 0.5:
        return 3    # 輕度壓縮
    elif importance >= 0.2:
        return 6    # 標準壓縮
    else:
        return 9    # 最大壓縮
```

---

## 分層管理策略

### 自動分層決策

```python
def decide_storage_tier(
    key: str, 
    value: Any, 
    access_pattern: str = "UNKNOWN"
) -> str:
    """自動決定存儲層級"""
    
    # 1. 計算重要性
    importance = calculate_importance(key, value)
    
    # 2. 分析訪問模式
    is_frequent = (access_pattern == "FREQUENT")
    is_transient = (access_pattern == "TRANSIENT")
    is_permanent = (access_pattern == "PERMANENT")
    
    # 3. 決定層級
    if is_frequent and importance > 0.7:
        # 頻繁訪問 + 重要 → L1 + 短期
        return "L1_AND_SHORT_TERM"
    
    elif is_permanent or importance > 0.6:
        # 永久存儲或重要數據 → 長期
        return "LONG_TERM"
    
    elif is_transient or importance < 0.3:
        # 臨時數據或低價值 → 短期
        return "SHORT_TERM"
    
    else:
        # 默認: 短期 → 定期檢查重要性
        return "SHORT_TERM"
```

### 分層容量管理

```python
class TierCapacityManager:
    """管理各層級容量"""
    
    TIER_LIMITS = {
        "L1": 100,              # MB
        "SHORT_TERM": 500,      # MB (估計)
        "LONG_TERM": 5000,      # MB (可擴展)
        "L2": 10000,            # MB
        "L3": 50000             # MB
    }
    
    def check_capacity(self, tier: str) -> Tuple[float, str]:
        """檢查層級容量使用率和狀態"""
        current_usage = self.get_tier_usage(tier)
        limit = self.TIER_LIMITS[tier]
        utilization = (current_usage / limit) * 100
        
        if utilization < 50:
            status = "HEALTHY"
        elif utilization < 75:
            status = "WARNING"
        elif utilization < 90:
            status = "CRITICAL"
        else:
            status = "FULL"
        
        return utilization, status
    
    def handle_overflow(self, tier: str):
        """處理層級溢出"""
        if tier == "L1":
            # 將冷數據遷移至短期
            self.demote_cold_data_to_short_term()
        
        elif tier == "SHORT_TERM":
            # 清理過期條目，遷移重要數據
            self.cleanup_and_migrate()
        
        elif tier == "LONG_TERM":
            # 存檔至磁盤
            self.archive_to_disk()
```

### 自動調整策略

```python
class AdaptiveTierManager:
    """自適應分層管理"""
    
    def adjust_tiers_based_on_metrics(self):
        """根據性能指標調整層級"""
        
        # 收集指標
        hit_rate = self.get_cache_hit_rate()
        memory_pressure = self.get_memory_pressure()
        access_patterns = self.analyze_access_patterns()
        
        # 決定調整
        if hit_rate < 0.80:
            # 命中率低，增加 L1 大小或短期容量
            self.increase_l1_capacity()
        
        if memory_pressure > 0.85:
            # 內存壓力大，啟用更激進的清理
            self.enable_aggressive_cleanup()
        
        # 根據訪問模式調整 TTL
        hot_access_rate = access_patterns.get('hot_access_rate', 0)
        if hot_access_rate > 0.5:
            # 頻繁訪問，增加短期 TTL
            self.short_term.ttl_seconds = 600
        else:
            # 少量訪問，減少 TTL
            self.short_term.ttl_seconds = 180
```

---

## 監控分層性能

### 性能指標

```python
class TierPerformanceMonitor:
    """監控各層級性能"""
    
    def collect_metrics(self) -> Dict[str, Any]:
        """收集所有層級性能指標"""
        return {
            "L1": {
                "capacity_mb": 100,
                "used_mb": self.get_l1_usage(),
                "entries": len(self.l1_cache),
                "hit_rate": self.calculate_hit_rate("L1"),
                "avg_access_time_ms": 0.5,
                "eviction_rate": self.calculate_eviction_rate("L1")
            },
            "SHORT_TERM": {
                "capacity_entries": 1000,
                "entries": len(self.short_term),
                "expired_entries": len(self.get_expired_entries()),
                "avg_ttl_remaining": self.calculate_avg_ttl(),
                "importance_distribution": self.get_importance_dist(),
                "hit_rate": self.calculate_hit_rate("ST")
            },
            "LONG_TERM": {
                "entries": len(self.long_term),
                "size_mb": self.get_long_term_size(),
                "importance_distribution": self.get_importance_dist("LT"),
                "search_time_ms": self.measure_search_time(),
                "hit_rate": self.calculate_hit_rate("LT")
            },
            "L2": {
                "size_mb": self.get_l2_size(),
                "entries": self.count_l2_entries(),
                "compression_ratio": self.get_l2_compression_ratio()
            },
            "L3": {
                "size_mb": self.get_l3_size(),
                "entries": self.count_l3_entries(),
                "compression_ratio": self.get_l3_compression_ratio()
            }
        }
```

### 分層報告

```bash
# 查看分層性能報告
python3 -m memory.memory_cli summary

# 輸出示例:
"""
📊 Memory System Summary

[SHORT-TERM MEMORY]
  Entries: 250/1000 (25% utilization)
  TTL Remaining: Avg 180s (min: 1s, max: 300s)
  Important (>0.6): 85 entries (34%)
  
[LONG-TERM MEMORY]
  Total Entries: 1,250
  Total Size: 45.6 MB
  
  Importance Distribution:
    Critical (>0.8): 150 entries (12%) → 未壓縮
    High (0.5-0.8): 450 entries (36%) → 輕度壓縮
    Medium (0.2-0.5): 500 entries (40%) → 標準壓縮
    Low (<0.2): 150 entries (12%) → 最大壓縮

[CACHE PERFORMANCE]
  L1 Hit Rate: 92.3%
  ST Hit Rate: 78.5%
  LT Hit Rate: 45.2%
  Overall Compression Ratio: 2.45x
  
[TIER UTILIZATION]
  L1: 87MB / 100MB (87%)
  ST: ~350MB (估計, 適度)
  LT: 45.6MB (未限制)
  L2: 120MB / 10GB (1.2%)
  L3: 850MB / 50GB (1.7%)
"""
```

---

## 實踐最佳方案

### 最佳實踐檢查清單

```python
class BestPracticesChecker:
    """驗證是否遵循最佳實踐"""
    
    def validate_all(self) -> Dict[str, bool]:
        """驗證所有最佳實踐"""
        return {
            "use_short_term_for_temp": self.check_temp_data_in_st(),
            "use_long_term_for_critical": self.check_critical_in_lt(),
            "monitor_hit_rates": self.check_hit_rate_monitoring(),
            "periodic_cleanup": self.check_cleanup_schedule(),
            "importance_scores": self.check_importance_scoring(),
            "compression_by_importance": self.check_compression_strategy(),
            "tier_capacity_limits": self.check_capacity_limits(),
            "access_pattern_analysis": self.check_access_analysis()
        }
```

### 常見錯誤和糾正

| 錯誤 | 症狀 | 原因 | 解決方案 |
|------|------|------|---------|
| 所有數據都放在 L1 | 內存爆炸 | 沒有分層 | 使用短期/長期 |
| 短期記憶不清理 | 命中率下降 | 沒有 TTL | 定期執行 cleanup |
| 沒有重要性評分 | 壓縮比低 | 不區分數據 | 實現重要性計算 |
| 忽視訪問模式 | 性能差 | 層級分配不當 | 監控並調整 |

### 調優建議

```python
# 1. 監控和調整
if hit_rate < 0.80:
    # 增加 L1 大小或短期容量
    l1_size = increase_l1(+20)

# 2. 清理頻率
if memory_usage > 0.80 * limit:
    # 更頻繁的清理
    cleanup_interval = 30  # 每 30 秒

# 3. TTL 調整
if short_term_utilization > 0.90:
    # 減少 TTL
    ttl = 180  # 從 300 改為 180

# 4. 壓縮級別
if disk_usage > 0.85 * limit:
    # 提高壓縮級別
    compression_level = 9
```

---

## 總結

### 分層管理的核心原則

1. **按優先級分層**: L1 > ST > LT > L2 > L3
2. **按重要性決策**: 重要性高 → 快速層級 + 低壓縮
3. **自動化流程**: TTL 過期 → 重要性評分 → 自動遷移
4. **持續監控**: 定期檢查性能指標，動態調整
5. **容量管理**: 監控各層使用率，防止溢出

### 性能目標

| 指標 | 目標值 |
|------|--------|
| L1 命中率 | > 90% |
| 整體命中率 | > 85% |
| 平均訪問時間 | < 5ms |
| 整體壓縮比 | > 2.0x |
| 清理延遲 | < 100ms |

---

**最後更新**: 2026-04-05  
**維護者**: Cosmic AI Team  
**許可證**: MIT
