# Agents 數據組織索引

## 概覽
- **總數據組**: 24 組
- **組織位置**: `src/agents/`
- **最後更新**: 2026-04-07

---

## 📊 數據組織結構

### 1️⃣ 宇宙策略優化 (4 組)
**路徑**: `src/agents/cosmic_optimizations/`

| 檔案名 | 大小 | 用途 | 說明 |
|--------|------|------|------|
| `cosmic_strategies___original.json` | 708B | 基礎策略 | 原始的宇宙策略配置 |
| `cosmic_strategies___optimized_v1_(aggressive).json` | 1.0KB | 激進策略 | 高風險高收益優化版本 |
| `cosmic_strategies___optimized_v2_(balanced).json` | 915B | 平衡策略 | 風險收益均衡版本 |
| `cosmic_strategies___optimized_v3_(resonance_focused).json` | 1.2KB | 共振策略 | 專注於量子共振的版本 |

---

### 2️⃣ 智能體快照 (4 組)
**路徑**: `src/agents/engine/snapshots/`

| 檔案名 | 大小 | 用途 | 說明 |
|--------|------|------|------|
| `agent_1_snapshot.json` | 2.3KB | Agent 1 狀態 | 智能體1的當前狀態快照 |
| `agent_2_snapshot.json` | 1.4KB | Agent 2 狀態 | 智能體2的當前狀態快照 |
| `agent_3_snapshot.json` | 1.4KB | Agent 3 狀態 | 智能體3的當前狀態快照 |
| `market_snapshot.json` | 701B | 市場數據 | 市場狀態快照 |

---

### 3️⃣ 引擎配置文件 (16 組)
**路徑**: `src/agents/engine/config/`

所有檔案均為 YAML 格式，包含不同引擎的配置參數。

| 配置名稱 | 用途 |
|---------|------|
| `cosmic_config.yaml` | 宇宙系統主配置 |
| `cosmic_intelligence.yaml` | 宇宙智能配置 |
| `cosmic_engineering.yaml` | 宇宙工程配置 |
| `quantum_singularity.yaml` | 量子奇點配置 |
| `quantum_bio_fusion.yaml` | 量子-生物融合配置 |
| `quantum_holography.yaml` | 量子全息配置 |
| `neuro_quantum_synergy.yaml` | 神經-量子協同配置 |
| `consciousness_field.yaml` | 意識場配置 |
| `reality_programming.yaml` | 現實編程配置 |
| `temporal_dominance.yaml` | 時間統治配置 |
| `bio_photonics.yaml` | 生物光子配置 |
| `chaos_resonance.yaml` | 混沌共振配置 |
| `fractal_recursion.yaml` | 分形遞迴配置 |
| `topological_bio.yaml` | 拓撲生物配置 |
| `platform_heterogeneous.yaml` | 異構平台配置 |
| `perfect_fortress.yaml` | 完美堡壘配置 |

---

## 📁 完整數據清單

### 策略組 (cosmic_optimizations/)
```
✓ cosmic_strategies___original.json
✓ cosmic_strategies___optimized_v1_(aggressive).json
✓ cosmic_strategies___optimized_v2_(balanced).json
✓ cosmic_strategies___optimized_v3_(resonance_focused).json
```

### 快照組 (engine/snapshots/)
```
✓ agent_1_snapshot.json
✓ agent_2_snapshot.json
✓ agent_3_snapshot.json
✓ market_snapshot.json
```

### 配置組 (engine/config/ - 16 個 YAML 檔案)
```
✓ bio_photonics.yaml
✓ chaos_resonance.yaml
✓ consciousness_field.yaml
✓ cosmic_config.yaml
✓ cosmic_engineering.yaml
✓ cosmic_intelligence.yaml
✓ fractal_recursion.yaml
✓ neuro_quantum_synergy.yaml
✓ perfect_fortress.yaml
✓ platform_heterogeneous.yaml
✓ quantum_bio_fusion.yaml
✓ quantum_holography.yaml
✓ quantum_singularity.yaml
✓ reality_programming.yaml
✓ temporal_dominance.yaml
✓ topological_bio.yaml
```

---

## 💡 使用指南

### 訪問策略配置
```python
import json
with open('src/agents/cosmic_optimizations/cosmic_strategies___optimized_v2_(balanced).json') as f:
    strategy = json.load(f)
```

### 訪問智能體快照
```python
import json
with open('src/agents/engine/snapshots/agent_1_snapshot.json') as f:
    snapshot = json.load(f)
```

### 訪問引擎配置
```python
import yaml
with open('src/agents/engine/config/quantum_singularity.yaml') as f:
    config = yaml.safe_load(f)
```

---

**創建日期**: 2026-04-07
**維護者**: Cosmic AI System
**狀態**: ✅ 數據已整理並索引
