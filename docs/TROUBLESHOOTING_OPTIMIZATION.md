# 🔧 故障排查和性能優化完整指南
**Troubleshooting & Performance Optimization Guide**

**版本**: 2.0 | **日期**: 2026-03-02 | **狀態**: ✅ 完全集成

---

## 目錄
1. [常見故障](#常見故障)
2. [診斷工具](#診斷工具)
3. [性能優化](#性能優化)
4. [快速修復](#快速修復)
5. [深度調查](#深度調查)

---

## 常見故障

### 量子引擎故障

#### 問題 1: 相干性快速下降
```
症狀: quantum_coherence 從 0.98 → 0.85 在 1 分鐘內
原因: 環境噪聲、溫度變化、功率波動
解決:
  1. 立即停止計算任務
  2. 運行相干性校準: python -m cosmic_ai.quantum.calibrate_coherence
  3. 檢查硬件溫度: sensors
  4. 驗證電源穩定性
  5. 重啟量子引擎
```

#### 問題 2: 門操作失敗
```
症狀: GateExecutionError | Circuit compilation failed
原因: 不支持的門組合、電路深度過深
解決:
  1. 檢查電路深度: python -m cosmic_ai.quantum.analyze_circuit_depth
  2. 減少 gate_depth: 從 20 → 15
  3. 啟用自動優化: circuit_optimization: aggressive
  4. 嘗試備用編譯方法
```

### 多智能體故障

#### 問題 3: 智能體無響應
```
症狀: Agent timeout | Response latency > 5000ms
原因: 消息隊列堆積、智能體過載、死鎖
解決:
  1. 檢查隊列深度:
     redis-cli LLEN agent_tasks
  2. 監控智能體進程:
     ps aux | grep agent
  3. 清理隊列:
     redis-cli DEL agent_tasks
  4. 增加智能體副本:
     kubernetes scale deployment multi-agent-system --replicas=5
  5. 重啟協調器
```

#### 問題 4: 決策衝突
```
症狀: Conflicting signals | Consensus failed
原因: 智能體意見分歧 > 50%
解決:
  1. 檢查智能體準確率:
     curl http://localhost:8001/metrics/agent_accuracy
  2. 調整投票權重:
     weights:
       technical_analyst: 0.40  # 提高
       sentiment_analyzer: 0.25 # 降低
  3. 增加智能體多樣性
  4. 重新培訓低性能智能體
```

### 交易引擎故障

#### 問題 5: 訂單執行延遲
```
症狀: Order execution latency > 200ms
原因: 網絡延遲、訂單簿阻塞、智能路由不佳
解決:
  1. 檢查網絡延遲:
     ping exchange-api.example.com
  2. 測試交易所連接:
     python -m cosmic_ai.trading.test_exchange_connection
  3. 優化訂單路由:
     num_splits: 3  # 減少從 5 到 3
     venue_selection: "fastest"
  4. 啟用直連模式:
     smart_routing:
       enabled: false  # 使用直連
```

#### 問題 6: 滑點過大
```
症狀: Average slippage > 5 bp
原因: 訂單過大、流動性不足、市場波動
解決:
  1. 檢查訂單大小:
     max_position_size: 0.05  # 減少
  2. 改進執行算法:
     default: "vwap"  # 改為 VWAP
  3. 動態調整參與率:
     participation_rate: 0.5  # 降低
  4. 使用冰山訂單:
     order_type: "iceberg"
     visible_quantity: 10%
```

### 風險管理故障

#### 問題 7: 回撤超限
```
症狀: Current drawdown > 20% (hard limit)
原因: 持續虧損、風險控制失效
解決:
  1. 立即停止交易:
     cosmic trade stop
  2. 檢查風險配置:
     max_drawdown: 0.20  # 驗證設置
  3. 分析虧損原因:
     python -m cosmic_ai.analysis.drawdown_analysis
  4. 進入安全模式:
     risk_mode: "safe"
  5. 重新校準策略
```

### 系統故障

#### 問題 8: 內存洩漏
```
症狀: Memory usage steadily increasing
原因: 快取未清理、連接未關閉
解決:
  1. 檢查內存使用:
     free -h
     docker stats cosmic_quantum_engine
  2. 清理快取:
     redis-cli FLUSHALL
     python -m cosmic_ai.cache.clear_cache
  3. 重啟服務:
     docker restart cosmic_quantum_engine
  4. 檢查代碼洩漏:
     python -m memory_profiler cosmic_ai/main.py
```

---

## 診斷工具

### 系統診斷命令

```bash
# 完整系統診斷
cosmic diagnose system --verbose

# 量子引擎診斷
cosmic diagnose quantum
  ├─ 檢查相干性
  ├─ 驗證糾纏態
  ├─ 測試門操作
  └─ 報告性能指標

# 多智能體診斷
cosmic diagnose agents
  ├─ 檢查所有智能體狀態
  ├─ 驗證通信延遲
  ├─ 測試協調機制
  └─ 報告準確率

# 交易引擎診斷
cosmic diagnose trading
  ├─ 測試交易所連接
  ├─ 驗證訂單執行
  ├─ 檢查風險系統
  └─ 報告性能指標

# 數據庫診斷
cosmic diagnose database
  ├─ MongoDB 健康檢查
  ├─ Redis 連接測試
  ├─ 數據完整性驗證
  └─ 性能基準測試
```

### 實時監控面板

```bash
# 啟動監控儀表板
cosmic monitor dashboard

# 實時日誌流
cosmic monitor logs --follow --filter="ERROR|WARNING"

# 性能實時監控
cosmic monitor performance
  ├─ CPU: ████░░░░░░ 45%
  ├─ 內存: ██████░░░░ 62%
  ├─ 量子相干性: █████████░ 95%
  ├─ 活躍智能體: 50/50 ✅
  ├─ 訂單執行延遲: 47ms ✅
  └─ 系統狀態: 🟢 優秀
```

### 日誌分析工具

```bash
# 查詢錯誤日誌
cosmic logs search "ERROR" --time=last_1h

# 分析性能瓶頸
cosmic logs analyze --metric=latency

# 導出日誌報告
cosmic logs export --format=pdf --output=report.pdf

# 實時日誌過濾
cosmic logs tail --grep="quantum|agent|risk" -f
```

---

## 性能優化

### 優化層級

#### 第 1 層: 硬件優化

```yaml
CPU 優化:
  - 使用高性能 CPU (3.5+ GHz)
  - 啟用 CPU 親和性:
    taskset -c 0-15 python cosmic_ai_main.py
  - 禁用頻率縮放:
    echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

內存優化:
  - 使用 NUMA 感知內存:
    numactl --interleave=all python cosmic_ai_main.py
  - 大頁支持:
    echo 2048 > /proc/sys/vm/nr_hugepages
  - 內存預分配:
    memory_preallocation: true

網絡優化:
  - 增加 TCP 緩衝:
    net.core.rmem_max = 268435456
    net.core.wmem_max = 268435456
  - 使用 jumbo frames:
    ip link set dev eth0 mtu 9000
  - 低延遲優先:
    net.core.netdev_budget = 600
```

#### 第 2 層: 軟件優化

```yaml
應用層優化:
  - 編譯熱點代碼:
    cython_compilation: true
    numba_jit: true
  
  - 向量化操作:
    use_numpy_vectorization: true
    avoid_python_loops: true
  
  - 併發控制:
    asyncio_workers: 16
    thread_pool_size: 32
    process_pool_size: 8

算法優化:
  - 使用快速路徑:
    fast_path_enabled: true
  
  - 快取優化:
    l1_cache_size: 1000
    l2_cache_size: 10000
    l3_cache_size: 100000
  
  - 索引優化:
    use_approximate_indices: true
```

#### 第 3 層: 系統優化

```yaml
操作系統優化:
  - 文件描述符限制:
    ulimit -n 1000000
  
  - 進程優先級:
    nice -n -10 python cosmic_ai_main.py
  
  - I/O 調度:
    echo deadline > /sys/block/sda/queue/scheduler

數據庫優化:
  - MongoDB 優化:
    wiredTigerCacheSizeGB: 50
    directoryPerDB: true
    compression: zlib
  
  - Redis 優化:
    maxmemory-policy: allkeys-lru
    tcp-backlog: 65535
    tcp-keepalive: 300
```

#### 第 4 層: 量子優化

```yaml
量子電路優化:
  - 減少門深度:
    max_gate_depth: 15  # 從 20 降至 15
  
  - 自動編譯優化:
    optimization_level: "aggressive"
  
  - 參數化編譯:
    parameterized_compilation: true
  
  - 並行執行:
    parallel_execution: true
    max_parallel_circuits: 16
```

### 優化結果預期

```
優化前:
  CPU 利用率: 45%
  內存使用: 32GB
  量子相干性: 0.93
  訂單執行延遲: 120ms
  系統吞吐量: 5000 ops/s

優化後 (第 1-2 層):
  CPU 利用率: 75%
  內存使用: 28GB
  量子相干性: 0.96
  訂單執行延遲: 65ms
  系統吞吐量: 12000 ops/s
  性能提升: 2.4x

優化後 (全部層級):
  CPU 利用率: 85%
  內存使用: 24GB
  量子相干性: 0.98
  訂單執行延遲: 35ms
  系統吞吐量: 20000 ops/s
  性能提升: 4.0x
```

---

## 快速修復

### 5 分鐘快速修復清單

```bash
# 1. 系統反應遲鈍
cosmic system restart

# 2. 智能體無響應
redis-cli DEL agent_tasks
docker restart cosmic_multi_agent

# 3. 高延遲
cosmic config set execution.num_splits 3
cosmic config set quantum_resonance.coupling_strength 0.8

# 4. 內存不足
docker exec cosmic_redis redis-cli FLUSHDB
python -m cosmic_ai.cache.clear_old_entries --days=1

# 5. 回撤超限
cosmic trade stop
cosmic risk reset
cosmic trade start --profile=conservative
```

---

## 深度調查

### 根本原因分析 (RCA)

```yaml
故障報告:
  時間: 2026-03-02 10:30:00 UTC
  嚴重性: CRITICAL
  描述: 系統回撤達到 25%，觸發硬限制

根本原因分析:
  1. 表面原因: 連續虧損 5 筆交易
  
  2. 深層原因:
     - 市場突變未被檢測
     - 情感分析智能體準確率下降至 72%
     - 風險管理參數過於激進
  
  3. 根本原因:
     - 訓練數據不包含此類市場場景
     - 智能體重新訓練計劃未執行
     - 市場監測算法需要更新

改正措施:
  - 立即: 切換至保守配置
  - 短期: 收集新市場數據並重新訓練
  - 長期: 改進異常檢測系統

預防措施:
  - 增加壓力測試場景
  - 改進市場異常檢測
  - 更頻繁的智能體績效評估
```

### 性能瓶頸分析

```bash
# 使用 profiler 分析
python -m cProfile -o stats.prof cosmic_ai_main.py

# 可視化結果
snakeviz stats.prof

# 熱點分析
pyflame --interval=1000 --pid=<PID> | flamegraph.pl > graph.svg

# 內存分析
memory_profiler cosmic_ai_main.py
```

---

## 維護清單

### 每日維護
```
□ 檢查系統健康狀態
□ 驗證備份完成
□ 查看告警日誌
□ 檢查磁盤空間
```

### 每週維護
```
□ 更新安全補丁
□ 性能基準測試
□ 備份驗證和恢復測試
□ 日誌歸檔
□ 容量規劃審查
```

### 每月維護
```
□ 完整系統診斷
□ 配置審查
□ 災難恢復演練
□ 性能趨勢分析
□ 安全審計
```

---

**最後更新**: 2026-03-02  
**維護者**: Cosmic AI Support Team  
**授權**: MIT License
