# Ray 分布式計算集成指南
# Comic AI Ray Distribution Integration Guide

## 概述

這個指南說明如何在 Comic AI 項目中使用 Ray 分布式計算框架，以實現**量子優勢級別**的計算能力提升。

### 主要改進

- ✅ **並行量子分析**: 使用 Ray 在多個 CPU 核心上並行運行量子分析
- ✅ **分布式數據壓縮**: 加速大規模文件壓縮和解壓縮
- ✅ **並行遺傳算法**: 分布式進化算法加速
- ✅ **能源效率**: 優化計算資源利用率
- ✅ **自動擴展**: 支持本地多進程和遠程集群

---

## 快速開始

### 1. 安裝 Ray

```bash
# 安裝依賴
pip install -r requirements.txt

# 驗證 Ray 安裝
python -c "import ray; print(ray.__version__)"
```

### 2. 基本使用

#### 使用分布式量子引擎

```python
from engine.quantum_engine import QuantumEngine
import numpy as np

# 創建啟用分布式的量子引擎
quantum_engine = QuantumEngine(use_distributed=True)

# 創建數據批次
data_batches = [np.random.randn(100, 50) for _ in range(4)]

# 並行運行分析
results = quantum_engine.run_parallel_analysis(
    data_batches=data_batches,
    theory_name='heisenberg'
)

print(f"Processed {len(results)} batches")

# 清理資源
quantum_engine.shutdown()
```

#### 使用分布式數據管理器

```python
from data.data_manager import DataManager

# 創建啟用分布式的數據管理器
dm = DataManager(use_distributed=True)

# 並行壓縮文件
files = ['file1.csv', 'file2.json', 'file3.txt']
results = dm.batch_compress(files)

print(f"Compressed {len(results)} files")

# 獲取存儲統計
stats = dm.get_storage_stats()
print(f"Compression ratio: {stats['compression_ratio_percent']:.1f}%")

dm.shutdown()
```

#### 分布式遺傳算法

```python
from engine.quantum_engine import QuantumEngine

# 創建引擎
qe = QuantumEngine(use_distributed=True)

# 運行分布式進化算法
result = qe.distributed_genetic_analysis(
    population_size=100,
    generations=50
)

print(f"Best fitness: {result['best_fitness']}")
print(f"Speedup: {result.get('speedup', 'N/A')}")

qe.shutdown()
```

---

## 配置

### Ray 配置文件

位置: `config/ray_config.yaml`

主要配置選項:

```yaml
cluster:
  num_cpus: null           # null 表示自動檢測
  num_gpus: 0
  memory_gb: null
  dashboard: true          # 啟用 Ray 儀表板

distributed_computing:
  quantum_engine:
    use_distribution: true
    batch_size: auto       # 自動計算批次大小
    workers: auto          # 自動檢測工作者數量
  
  data_manager:
    use_distribution: true
    compression_workers: auto
    max_parallel_tasks: 8
  
  genetic_algorithm:
    use_distribution: true
    workers: auto
```

### 程序化配置

```python
from config.ray_config import RayConfig

# 加載配置
config = RayConfig('config/ray_config.yaml')

# 獲取集群配置
cluster_config = config.get_cluster_config()

# 獲取量子引擎配置
qe_config = config.get_distributed_computing_config('quantum_engine')
```

---

## 性能優化

### 1. 自動批次大小調整

```python
from engine.quantum_engine import QuantumEngine
import numpy as np

# Ray 會自動根據 CPU 數量調整批次大小
qe = QuantumEngine(use_distributed=True)

# 大規模數據分析
large_data = np.random.randn(100000, 1000)
batches = [large_data[i:i+10000] for i in range(0, len(large_data), 10000)]

results = qe.run_parallel_analysis(batches, 'heisenberg')
```

### 2. 並行度控制

```python
from engine.ray_distributed_engine import RayDistributedEngine

# 指定 CPU 核心數
ray_engine = RayDistributedEngine(num_cpus=8)

print(ray_engine.get_cluster_status())
# 輸出: {'total_cpus': 8, 'available_cpus': 8, ...}

ray_engine.shutdown()
```

### 3. 監控性能

```python
from engine.quantum_engine import QuantumEngine

qe = QuantumEngine(use_distributed=True)

# 檢查分布式狀態
status = qe.get_distributed_status()
print(status)
# 輸出: {'status': 'active', 'distributed': True, 'cluster': {...}}
```

---

## 性能基準測試

### 運行基準測試

```bash
# 運行完整基準測試
python test_ray_distribution.py

# 測試項目:
# - 量子引擎並行分析
# - 遺傳算法並行進化
# - 數據壓縮性能
```

### 預期性能提升

根據系統配置，預期以下性能提升:

| 任務 | 4核心 | 8核心 | 16核心 |
|------|-------|-------|--------|
| 量子分析 | 2.5x | 4.5x | 8x+ |
| 數據壓縮 | 2.8x | 5.2x | 9x+ |
| 遺傳算法 | 2.2x | 4.0x | 7x+ |

---

## 進階使用

### 自定義並行函數

```python
from engine.ray_distributed_engine import RayDistributedEngine
import numpy as np

ray_engine = RayDistributedEngine()

# 定義自定義分析函數
def custom_analysis(data):
    return {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'sum': float(np.sum(data))
    }

# 並行應用
data_batches = [np.random.randn(100) for _ in range(10)]
results = ray_engine._parallel_map(custom_analysis, data_batches)

print(f"Processed {len(results)} batches")
```

### 分布式批量處理

```python
from data.data_manager import DataManager

dm = DataManager(use_distributed=True)

# 定義處理函數
def load_and_analyze(file_path):
    # 你的處理邏輯
    return {'file': file_path, 'status': 'processed'}

# 批量處理
files = ['data/file1.csv', 'data/file2.csv', 'data/file3.csv']
result = dm.distributed_batch_process(files, load_and_analyze)

print(result)
```

---

## 故障排除

### 問題: Ray 無法初始化

**解決方案:**
```python
import ray

# 清除舊的 Ray 進程
ray.shutdown()

# 重新初始化
ray.init(num_cpus=4, _temp_dir="/tmp/ray_custom")
```

### 問題: 內存不足

**解決方案:**
```python
from engine.ray_distributed_engine import RayDistributedEngine

# 指定內存限制
ray_engine = RayDistributedEngine(
    num_cpus=4,
    memory_gb=16
)
```

### 問題: 性能沒有改善

**檢查清單:**
- 確認 Ray 正確初始化: `ray.is_initialized()`
- 檢查 CPU 使用率: `ray.available_resources()`
- 驗證批次大小是否合適
- 檢查是否有 I/O 瓶頸

---

## Ray 儀表板

### 訪問儀表板

```python
from engine.quantum_engine import QuantumEngine

qe = QuantumEngine(use_distributed=True)

# Ray 儀表板 URL
print("Ray Dashboard: http://127.0.0.1:8265")

# 執行任務...
qe.shutdown()
```

儀表板提供:
- 實時任務監控
- 資源使用統計
- 性能指標

---

## 最佳實踐

### 1. 資源管理

```python
# 不推薦: 每次都創建新引擎
for i in range(100):
    qe = QuantumEngine(use_distributed=True)
    # ...
    qe.shutdown()

# 推薦: 複用引擎實例
qe = QuantumEngine(use_distributed=True)
for i in range(100):
    # ...
qe.shutdown()
```

### 2. 批次大小優化

```python
# 根據 CPU 數量選擇批次大小
import ray

num_cpus = int(ray.available_resources()['CPU'])
batch_size = max(1, total_tasks // (num_cpus * 2))
```

### 3. 錯誤處理

```python
try:
    qe = QuantumEngine(use_distributed=True)
    results = qe.run_parallel_analysis(batches, 'heisenberg')
except Exception as e:
    logger.error(f"Analysis failed: {e}")
finally:
    qe.shutdown()
```

---

## 相關文件

- `engine/ray_distributed_engine.py` - Ray 分布式引擎核心
- `engine/quantum_engine.py` - 啟用 Ray 的量子引擎
- `data/data_manager.py` - 啟用 Ray 的數據管理器
- `config/ray_config.yaml` - Ray 配置文件
- `test_ray_distribution.py` - 性能基準測試

---

## 支援和反饋

如有問題或建議，請提交 Issue 或聯繫開發團隊。

**量子優勢能源自洽完全啟用！** 🚀⚡
