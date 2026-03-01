# 量子態配置指南 (Quantum State Configuration Guide)

## 概述

本文檔提供量子態系統的完整配置規範，涵蓋：
- YAML 配置文件結構
- 環境變量設置
- VSCode settings.json 配置
- 超參數調優指南

---

## 1. 量子態配置文件 (YAML)

目前項目中**缺少**專用的量子態配置文件。建議創建以下配置文件結構：

### 1.1 推薦的配置文件層次

```
config/
├── core/
│   ├── main_system_config.yaml          # ✅ 已存在
│   └── quantum_state_config.yaml        # ❌ 需要創建
├── services/
│   ├── engine_config.yaml               # ✅ 已存在
│   └── hybrid_quantum_config.yaml       # ❌ 需要創建
└── optimization/
    └── quantum_algorithm_config.yaml    # ❌ 需要創建
```

### 1.2 量子態核心配置文件

**建議位置**: `/workspaces/cosmic-ai.uk/config/core/quantum_state_config.yaml`

```yaml
# 量子態配置 (Quantum State Configuration)
version: "1.0"
description: "Configuration for Quantum State System"

# ============================================================================
# 1. 量子啟發式算法配置 (Hybrid Quantum-Enhanced Algorithm)
# ============================================================================
hybrid_quantum_algorithm:
  enabled: true
  version: "2.0.0"
  
  # 基本參數
  population_size: 50
  max_iterations: 100
  
  # 量子操作參數
  quantum_gates: 10  # 每迭代的量子門操作數
  
  # 糾纏參數
  entanglement:
    strength: 0.8           # 糾纏耦合強度 [0.3, 0.9]
    analysis_enabled: true
    measure_entanglement: true
  
  # 量子隧穿參數
  tunneling:
    base_probability: 0.15  # 基礎隧穿概率 [0.05, 0.3]
    scale_with_entanglement: true  # 與糾纏度一起縮放
  
  # 量子相位參數
  phase:
    initialization: "random"  # "random" 或 "uniform"
    phase_shift_range: [-3.14159, 3.14159]  # [-π, π]
    coherence_preservation: true
  
  # 振幅參數
  amplitude:
    initialization_method: "uniform_superposition"
    normalization_enabled: true
    clip_bounds: [0.0, 1.0]
  
  # 收斂控制
  convergence:
    tolerance: 1e-6
    improvement_threshold: 1e-8
    stagnation_generations: 20
  
  # 優化邊界（可動態設置）
  optimization_bounds:
    signal_quality:
      - min: 0.0
        max: 1.0
        name: "momentum_weight"
      - min: 0.0
        max: 1.0
        name: "volume_weight"
      - min: 0.0
        max: 1.0
        name: "volatility_weight"

# ============================================================================
# 2. 古典量子態配置 (Classical Quantum State)
# ============================================================================
classical_quantum_state:
  enabled: true
  version: "1.0"
  
  # 狀態空間優化器
  state_space_optimizer:
    dimension: 128              # 狀態空間維度
    learning_rate: 0.01        # 梯度下降學習率
    pca_components: "auto"     # PCA 組件數
    normalization: "standard"  # "standard", "minmax", 或 "robust"
  
  # 概率決策引擎
  probabilistic_decision:
    coherence_threshold: 0.85   # 決策相干性閾值 [0.7, 0.95]
    signal_strength_weight: 1.0
    
  # 相關性分析
  correlation_analyzer:
    method: "pearson"           # "pearson" 或 "spearman"
    mutual_information_bins: 10 # 互信息直方圖分箱數
    
  # 信號處理
  signal_processor:
    resonance_analysis:
      sampling_frequency: 100   # Hz
      quality_factor: 10.0      # 共振濾波品質因子
      filter_order: 4           # Butterworth 濾波器階數
    
    fft_settings:
      nperseg: 256              # FFT 段大小
      overlap: 0.5              # 50% 重疊

# ============================================================================
# 3. 量子信號生成器配置 (Quantum Signal Generator)
# ============================================================================
quantum_signal_generator:
  enabled: true
  market_lookback: 20           # 回看周期（K線數）
  
  # 目標函數參數
  objective_function:
    momentum_window: 5          # 動量計算窗口
    volume_normalize_window: 20 # 成交量歸一化窗口
    sigmoid_scaling: true
  
  # 量子集合預測器
  ensemble_predictor:
    num_predictors: 5           # 集合中的預測器數量
    population_size_base: 20    # 基礎種群大小
    gates_increment: 1          # 每個預測器的門增量
    iterations_increment: 10    # 每個預測器的迭代增量

# ============================================================================
# 4. 性能和穩定性配置
# ============================================================================
performance:
  # 內存管理
  memory:
    max_population_storage: "1GB"
    cache_enabled: true
    cache_size: "500MB"
  
  # 數值穩定性
  numerical_stability:
    epsilon: 1e-10              # 數值精度閾值
    overflow_limit: 1e308       # IEEE 754 上限
    underflow_limit: 1e-323     # IEEE 754 下限
    clipping_enabled: true
  
  # 並行化
  parallelization:
    enabled: true
    num_workers: 4              # 並行工作進程數
    backend: "ray"              # "ray", "multiprocessing", 或 "threading"

# ============================================================================
# 5. 日志和監控配置
# ============================================================================
logging:
  level: "INFO"                 # "DEBUG", "INFO", "WARNING", "ERROR"
  file: "logs/quantum_state.log"
  max_size: "10MB"
  backup_count: 5
  
  # 監控
  monitoring:
    track_fitness_evolution: true
    track_entanglement_levels: true
    track_phase_alignment: true
    track_amplitude_distribution: true
    sample_interval: 5          # 每 N 次迭代採樣一次

# ============================================================================
# 6. 驗證和檢查點
# ============================================================================
validation:
  # 狀態驗證
  check_amplitude_normalization: true
  check_probability_conservation: true
  check_phase_continuity: true
  check_entanglement_bounds: true
  
  # 檢查點
  checkpoint:
    enabled: true
    save_interval: 10           # 每 10 次迭代保存一次
    checkpoint_dir: "checkpoints/quantum_state"
    max_checkpoints: 10         # 最多保存 10 個檢查點
```

### 1.3 混合量子算法配置文件

**建議位置**: `/workspaces/cosmic-ai.uk/config/services/hybrid_quantum_config.yaml`

```yaml
# 混合量子增強算法配置
version: "1.0"
description: "Hybrid Quantum-Enhanced Algorithm Configuration"

# 交易信號生成
trading_signals:
  quantum_enhancement_enabled: true
  base_signal_weight: 0.8
  quantum_boost_weight: 0.2    # 20% 量子增強
  confidence_threshold: 0.65
  
  # 信號成分
  components:
    momentum:
      enabled: true
      weight: 0.4
      lookback: 5
      
    volume:
      enabled: true
      weight: 0.3
      lookback: 20
      
    volatility:
      enabled: true
      weight: 0.3

# 量子集合預測
ensemble:
  num_models: 5
  aggregation_method: "weighted_average"  # 加權平均
  coherence_weight: 0.5                    # 相位相干性權重
  entanglement_weight: 0.5                 # 糾纏度權重

# 市場數據設置
market_data:
  lookback_period: 20
  data_validation:
    check_nan: true
    remove_outliers: true
    outlier_std_threshold: 3.0

# 性能監測
performance_monitoring:
  track_signal_accuracy: true
  track_convergence_speed: true
  track_quantum_advantage: true
  report_interval: 100  # 迭代次數
```

### 1.4 量子優化器配置文件

**建議位置**: `/workspaces/cosmic-ai.uk/config/optimization/quantum_algorithm_config.yaml`

```yaml
# 量子算法優化配置
version: "1.0"
description: "Quantum Algorithm Optimization Parameters"

# 演化策略
evolutionary:
  mutation:
    type: "gaussian"            # "gaussian" 或 "uniform"
    std_dev: 0.1
    adaptive: true              # 根據進度自適應變異率
    
  crossover:
    type: "blend"               # "single_point", "two_point", 或 "blend"
    blend_alpha: 0.5
    
  selection:
    method: "tournament"        # "tournament" 或 "roulette"
    tournament_size: 3

# 粒子群優化
particle_swarm:
  enabled: true
  num_particles: 30
  inertia_weight: 0.7
  cognitive_coefficient: 1.5   # c1
  social_coefficient: 1.5      # c2
  max_velocity: 0.5

# 差分進化
differential_evolution:
  enabled: true
  strategy: "best/1/bin"        # DE 策略
  f: 0.8                        # 縮放因子
  cr: 0.9                       # 交叉概率
  population_size: 50

# 遺傳算法
genetic_algorithm:
  enabled: true
  population_size: 50
  elite_preservation: 0.1       # 保留 10% 精英
  mutation_rate: 0.05
  crossover_rate: 0.9

# 模擬退火
simulated_annealing:
  enabled: true
  initial_temperature: 100
  cooling_rate: 0.95
  min_temperature: 0.01
  iterations_per_temp: 10
```

---

## 2. 環境變量配置

### 2.1 推薦的環境變量

```bash
# 量子態系統環境變量
export QUANTUM_STATE_ENABLED=true
export HYBRID_QUANTUM_ALGORITHM_ENABLED=true
export CLASSICAL_QUANTUM_STATE_ENABLED=true

# 性能配置
export QUANTUM_POPULATION_SIZE=50
export QUANTUM_MAX_ITERATIONS=100
export QUANTUM_NUM_THREADS=4

# 數值精度
export QUANTUM_EPSILON=1e-10
export QUANTUM_AMPLITUDE_CLIP=true

# 日志級別
export QUANTUM_LOG_LEVEL=INFO

# 檢查點
export QUANTUM_CHECKPOINT_ENABLED=true
export QUANTUM_CHECKPOINT_INTERVAL=10
```

### 2.2 容器部署環境變量

```dockerfile
# Dockerfile 示例
ENV QUANTUM_STATE_ENABLED=true
ENV QUANTUM_POPULATION_SIZE=50
ENV QUANTUM_MAX_ITERATIONS=100
ENV PYTHONPATH=/workspace/src:/workspace/optimizer:/workspace/engine
ENV RAY_memory=2000000000
```

---

## 3. VSCode 設置配置

### 3.1 當前 settings.json 中的量子態相關設置

**位置**: `.vscode/settings.json`

```json
{
  "cSpell.ignoreWords": [
    "quantum",
    "Qiskit",
    "Grover",
    "teleport",
    "algo",
    ...
  ],
  "todo-tree.general.tags": [
    "QUANTUM",
    ...
  ],
  "python.analysis.extraPaths": [
    "${workspaceFolder}/src",
    "${workspaceFolder}/optimizer",
    "${workspaceFolder}/engine"
  ]
}
```

### 3.2 推薦的增強設置

**建議添加到 `.vscode/settings.json`**:

```json
{
  "// ========== 量子態開發設置 ==========": "",
  
  "python.analysis.extraPaths": [
    "${workspaceFolder}/src",
    "${workspaceFolder}/optimizer",
    "${workspaceFolder}/engine",
    "${workspaceFolder}/config"
  ],
  
  "python.linting.ruffArgs": [
    "--select=E,F,W,C,I",
    "--ignore=E501,E741",
    "--max-line-length=127"
  ],
  
  "[python]": {
    "editor.rulers": [88, 120, 127],
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  
  "// ========== YAML 配置支持 ==========": "",
  "[yaml]": {
    "editor.insertSpaces": true,
    "editor.tabSize": 2,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  
  "// ========== 文件關聯 ==========": "",
  "files.associations": {
    "*_config.yaml": "yaml",
    "*_config.yml": "yaml",
    "*.strategy": "python",
    "quantum_*.py": "python",
    "hybrid_*.py": "python"
  },
  
  "// ========== 搜索排除 ==========": "",
  "search.exclude": {
    "checkpoints/": true,
    "logs/quantum_*": true
  },
  
  "// ========== 拼寫檢查 ==========": "",
  "cSpell.ignoreWords": [
    "quantum",
    "Qiskit",
    "Grover",
    "entanglement",
    "superposition",
    "amplitude",
    "coherence",
    "teleport",
    "hadamard",
    "pauli",
    "cnot",
    "eigenvalue"
  ],
  
  "// ========== 代碼片段支持 ==========": "",
  "python.testing.pytestArgs": [
    "-v",
    "--tb=short",
    "src/tests/test_quantum*.py",
    "src/tests/test_hybrid*.py"
  ],
  
  "// ========== 調試配置 ==========": "",
  "debug.logOutput": "verbose"
}
```

---

## 4. 超參數調優指南

### 4.1 超參數敏感性分析

| 超參數 | 推薦範圍 | 影響 | 調優策略 |
|--------|---------|------|---------|
| `population_size` | 20-100 | 精度 vs 速度 | 從 50 開始，根據 GPU 內存增減 |
| `max_iterations` | 50-500 | 收斂質量 | 監控適應度改善，早停（stagnation_generations） |
| `quantum_gates` | 5-20 | 探索 vs 利用 | 增大→更好的探索，可能影響速度 |
| `entanglement_strength` | 0.3-0.9 | 種群多樣性 | 0.8 是平衡點；增大→易陷入局部最優 |
| `tunneling_probability` | 0.05-0.3 | 逃逸能力 | 0.15 平衡；過大→不穩定 |
| `learning_rate` | 0.001-0.1 | 收斂速度 | 0.01 推薦；過大→震蕩，過小→收斂慢 |

### 4.2 超參數調優工作流

```python
# 使用 Optuna 進行超參數優化（示例）
import optuna

def objective(trial):
    population_size = trial.suggest_int('population_size', 20, 100)
    entanglement = trial.suggest_float('entanglement_strength', 0.3, 0.9)
    tunneling = trial.suggest_float('tunneling_probability', 0.05, 0.3)
    
    algo = HybridQuantumEnhancedAlgorithm(
        population_size=population_size,
        entanglement_strength=entanglement,
        tunneling_probability=tunneling
    )
    
    result = algo.optimize(objective_func, bounds)
    return result['best_fitness']

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)
best_params = study.best_params
```

### 4.3 配置模板

**低精度、高速度模板（實時交易）**:
```yaml
population_size: 20
max_iterations: 50
quantum_gates: 5
entanglement_strength: 0.6
tunneling_probability: 0.1
```

**高精度、低速度模板（歷史回測）**:
```yaml
population_size: 100
max_iterations: 200
quantum_gates: 15
entanglement_strength: 0.85
tunneling_probability: 0.2
```

**平衡模板**:
```yaml
population_size: 50
max_iterations: 100
quantum_gates: 10
entanglement_strength: 0.8
tunneling_probability: 0.15
```

---

## 5. 配置驗證

### 5.1 配置檢查清單

```python
def validate_quantum_config(config_dict):
    """驗證量子態配置的有效性"""
    checks = {
        'population_size': (20, 200, "整數"),
        'max_iterations': (10, 1000, "整數"),
        'quantum_gates': (1, 50, "整數"),
        'entanglement_strength': (0.0, 1.0, "浮點數"),
        'tunneling_probability': (0.0, 1.0, "浮點數"),
        'learning_rate': (0.0001, 1.0, "浮點數"),
        'coherence_threshold': (0.5, 1.0, "浮點數"),
    }
    
    errors = []
    for param, (min_val, max_val, ptype) in checks.items():
        if param not in config_dict:
            errors.append(f"缺失參數: {param}")
        elif not min_val <= config_dict[param] <= max_val:
            errors.append(f"{param} 超出範圍 [{min_val}, {max_val}]")
    
    return len(errors) == 0, errors
```

### 5.2 運行時驗證

```bash
# 驗證 YAML 配置文件語法
python -c "import yaml; yaml.safe_load(open('config/core/quantum_state_config.yaml'))"

# 驗證配置參數
python -c "from src.config import load_quantum_config; cfg = load_quantum_config(); print(cfg)"

# 檢查必要的依賴
pip check
python -m pip show qiskit numpy scipy scikit-learn
```

---

## 6. 常見配置問題排查

### 問題1: 振幅歸一化失敗
```
症狀: 振幅總和 ≠ 1
解決: 檢查 normalization_enabled = true
       確認 amplitude 初始化為 1/sqrt(population_size)
```

### 問題2: 糾纏度過高（種群退化）
```
症狀: 所有個體聚集到同一點
解決: 減小 entanglement_strength（從 0.8 降至 0.6）
       增加 tunneling_probability（從 0.15 增至 0.25）
       增加 quantum_gates 數量
```

### 問題3: 收斂速度過慢
```
症狀: 適應度改善停滯
解決: 增加 population_size
       增加 max_iterations
       調整 learning_rate（若使用 SGD）
       減小 stagnation_generations 以啟用早停
```

### 問題4: 內存溢出
```
症狀: Out of Memory 錯誤
解決: 減小 population_size
       減小 dimension（狀態空間維度）
       啟用 checkpoint（定期保存，釋放舊數據）
       檢查 cache_size 設置
```

---

## 7. 生產部署配置

### 7.1 生產環境配置示例

```yaml
# config/services/quantum_state_production.yaml
hybrid_quantum_algorithm:
  population_size: 50
  max_iterations: 100
  quantum_gates: 10
  entanglement:
    strength: 0.8
  tunneling:
    base_probability: 0.15
  convergence:
    improvement_threshold: 1e-8
    stagnation_generations: 15

performance:
  parallelization:
    enabled: true
    num_workers: 8
  memory:
    max_population_storage: "2GB"
    cache_enabled: true

logging:
  level: "WARNING"  # 生產中更少日志
  monitoring:
    track_fitness_evolution: true
    sample_interval: 10

validation:
  checkpoint:
    enabled: true
    save_interval: 20
    checkpoint_dir: "/mnt/storage/checkpoints"
```

### 7.2 Docker Compose 配置

```yaml
# config/deployment/docker-compose.yml (片段)
services:
  quantum_engine:
    image: cosmic-ai:quantum-latest
    environment:
      QUANTUM_STATE_ENABLED: "true"
      QUANTUM_CONFIG_PATH: "/config/quantum_state_config.yaml"
      QUANTUM_LOG_LEVEL: "INFO"
    volumes:
      - ./config:/config:ro
      - ./logs:/logs
      - ./checkpoints:/checkpoints
    resources:
      limits:
        cpus: '8'
        memory: 16G
```

---

## 8. 配置文件模板總結

| 文件 | 位置 | 用途 | 優先級 |
|------|------|------|--------|
| quantum_state_config.yaml | config/core/ | 核心量子態配置 | 🔴 高 |
| hybrid_quantum_config.yaml | config/services/ | 混合量子算法 | 🔴 高 |
| quantum_algorithm_config.yaml | config/optimization/ | 優化器配置 | 🟡 中 |
| settings.json | .vscode/ | 開發環境 | 🟢 低 |
| main_system_config.yaml | config/core/ | 系統全局 | 🔴 高 |

---

## 9. 參考資源

### 相關文檔
- `docs/12_quantum_state_technical_documentation.md` - 技術實現細節
- `docs/01_quantum_entanglement_system.md` - 量子糾纏系統
- `docs/03_quantum_field_theory_system.md` - 量子場論

### 代碼示例
- `optimizer/hybrid_quantum_algorithm.py` - 混合量子算法
- `engine/enhanced_quantum_engine.py` - 古典量子引擎
- `src/core/enhanced_quantum_market_analyzer.py` - 交易應用

### 配置文件
- `config/core/main_system_config.yaml` - 系統配置
- `config/services/engine_config.yaml` - 引擎配置
- `.vscode/settings.json` - 開發設置

---

## 10. 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2026-03-01 | 初始版本，涵蓋全面配置指南 |

---

**文檔維護者**: OpenCode Agent  
**最後更新**: 2026-03-01  
**狀態**: ✅ 完成

**待創建配置文件**:
- [ ] `/workspaces/cosmic-ai.uk/config/core/quantum_state_config.yaml`
- [ ] `/workspaces/cosmic-ai.uk/config/services/hybrid_quantum_config.yaml`
- [ ] `/workspaces/cosmic-ai.uk/config/optimization/quantum_algorithm_config.yaml`
