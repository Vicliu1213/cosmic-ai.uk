# Cosmic Core - 核心類組織文檔

## 概述

**位置**: `src/core/cosmic/`  
**狀態**: ✅ 已組織  
**核心類數量**: 9 個主要類  
**子模塊**: 5 個

## 目錄結構

```
src/core/cosmic/
├── __init__.py                           # 核心層主入口
├── CORE_ORGANIZATION.md                  # 本文檔
│
├── agents/                               # 智能體系統
│   ├── __init__.py
│   ├── agent.py                         # Agent 類 - Ray 遠程智能體
│   └── consensus.py                     # Consensus 協議
│
├── quantum/                              # 量子系統
│   ├── __init__.py
│   ├── simulator.py                     # QiskitQuantumSimulator
│   ├── error_correction.py              # 量子糾錯 (RepetitionCode, ShorCode, SurfaceCode)
│   └── tasks.py                         # 量子任務執行
│
├── fault_tolerance/                      # 容錯系統
│   ├── __init__.py
│   ├── topology.py                      # FaultDetectionEngine, FaultIsolationManager, FailoverManager
│   └── auto_repair.py                   # AutoRepairConfig, 自修復機制
│
├── learning/                             # 自進化學習
│   ├── __init__.py
│   └── evolution.py                     # SelfEvolutionEngine (PPO, CMAES, KnowledgeDistiller)
│
└── utilities/                            # 工具和輔助模塊
    ├── __init__.py
    ├── knowledge_base.py                # KnowledgeBase 知識庫
    ├── encoding_protection.py           # EncodingProtection 編碼保護
    ├── data_interface.py                # DataInterface 數據接口
    └── utils.py                         # 通用工具函數
```

## 核心類詳解

### 1. 智能體系統 (Agents)

#### 1.1 Agent (`agents/agent.py`)
```python
@ray.remote
class Agent:
    """Ray 遠程執行的分佈式智能體"""
    
    def __init__(self, agent_id, genome_config, resources, kb_ref)
    def vote(self, proposal) -> Dict
    def update_reputation(self, delta)
    def query_theory(self, theory_name)
    def perform_quantum_task(self, task_type, **kwargs)
```

**功能**:
- 基於 Ray 的分佈式智能體
- 支援多元理論基因組
- 聲譽機制
- 量子任務執行

**用途**: 多智能體共識和協作

#### 1.2 Consensus (`agents/consensus.py`)
**功能**: 多智能體共識機制

---

### 2. 量子系統 (Quantum)

#### 2.1 QiskitQuantumSimulator (`quantum/simulator.py`)
```python
class QiskitQuantumSimulator:
    """真實的 Qiskit 量子模擬器 (Qiskit 2.x 相容)"""
    
    def __init__(self, simulator_type: str = "aer_simulator")
    def run_grover(self, ...)
    def run_shor(self, ...)
    def run_vqe(self, ...)
    def run_qaoa(self, ...)
    def run_annealing(self, ...)
```

**支持的算法**:
- Grover 搜索
- Shor 因式分解
- VQE (變分量子特徵求解器)
- QAOA (量子近似優化)
- 量子退火

#### 2.2 Error Correction (`quantum/error_correction.py`)
```python
class RepetitionCode          # 3-qubit 重複碼
class ShorCode               # 9-qubit Shor 碼
class SurfaceCode            # 5x5 表面碼
class QuantumErrorCorrectionEngine  # Ray actor
```

**功能**:
- 多層量子糾錯
- 症狀檢測
- 錯誤恢復

#### 2.3 Quantum Tasks (`quantum/tasks.py`)
**功能**: 量子任務的標準化接口

---

### 3. 容錯系統 (Fault Tolerance)

#### 3.1 FaultDetectionEngine (`fault_tolerance/topology.py`)
```python
class FaultDetectionEngine:
    """實時故障檢測引擎"""
    
    def monitor_health(self, component_id)
    def detect_anomalies(self)
    def predict_failures(self)
```

**功能**:
- 實時健康監測
- 異常偵測
- 故障預測

#### 3.2 FaultIsolationManager
```python
class FaultIsolationManager:
    """故障隔離和斷路器"""
    
    def isolate_component(self, component_id)
    def apply_circuit_breaker(self, service_id)
    def set_timeout_protection(self, service_id, timeout)
```

#### 3.3 FailoverManager
```python
class FailoverManager:
    """自動故障轉移"""
    
    def activate_backup_replica(self, component_id)
    def coordinate_failover(self, primary_id, backup_id)
    def verify_failover_success(self)
```

#### 3.4 AutoRepairConfig (`fault_tolerance/auto_repair.py`)
**功能**: 自動修復配置和機制

---

### 4. 自進化學習 (Learning)

#### 4.1 SelfEvolutionEngine (`learning/evolution.py`)
```python
class PPOLearner:
    """代理策略優化學習器"""
    pass

class CMAESEvolutionStrategy:
    """協方差矩陣自適應進化策略"""
    pass

class KnowledgeDistiller:
    """師生知識轉移"""
    pass

class SelfEvolutionEngine:
    """統一的自進化引擎"""
    pass
```

**功能**:
- PPO 強化學習
- 進化策略 (CMA-ES)
- 知識蒸餾
- 持續優化

---

### 5. 工具和輔助 (Utilities)

#### 5.1 KnowledgeBase (`utilities/knowledge_base.py`)
```python
class KnowledgeBase:
    """集中式知識庫管理"""
    
    def add_theory(self, name, content)
    def get_theory(self, name)
    def query_theories(self, keywords)
```

#### 5.2 EncodingProtection (`utilities/encoding_protection.py`)
**功能**: 信息編碼和保護

#### 5.3 DataInterface (`utilities/data_interface.py`)
**功能**: 統一的數據接口

#### 5.4 Utils (`utilities/utils.py`)
**功能**: 通用工具函數

---

## 導入方式

### 方式 1: 導入特定類
```python
from src.core.cosmic.agents import Agent
from src.core.cosmic.quantum import QiskitQuantumSimulator
from src.core.cosmic.fault_tolerance import FaultDetectionEngine
from src.core.cosmic.learning import SelfEvolutionEngine
```

### 方式 2: 從主模塊導入
```python
from src.core.cosmic import (
    Agent,
    QiskitQuantumSimulator,
    FaultDetectionEngine,
    FailoverManager,
    SelfEvolutionEngine,
    KnowledgeBase,
    EncodingProtection,
    DataInterface
)
```

### 方式 3: 導入整個子模塊
```python
from src.core import cosmic

# 使用
agent = cosmic.agents.Agent(...)
simulator = cosmic.quantum.QiskitQuantumSimulator()
```

---

## 依賴關係

```
utilities (工具層)
    ↓
quantum (量子層) + agents (智能體層)
    ↓
learning (學習層) + fault_tolerance (容錯層)
    ↓
応用層
```

---

## 配置文件位置

- **全局配置**: `src/config/` (用於整體系統配置)
- **特定配置**:
  - 量子配置: `src/cosmic-global/config/quantum_*.yaml`
  - 容錯配置: `src/cosmic-global/configs/immortal_perpetual_config.yaml`
  - 學習配置: (待添加)

---

## 版本信息

**核心版本**: 1.0.0  
**最後更新**: 2026-04-08  
**狀態**: ✅ 已激活  

---

## 相關位置

| 位置 | 用途 |
|------|------|
| `src/core/cosmic/` | 核心類集合 (本目錄) |
| `src/cosmic-global/cosmic/` | 完整 cosmic 實現 |
| `src/cosmic-global/` | 全局配置和文檔 |
| `cosmic_engine/` | 原始 cosmic 引擎 (備用) |
| `agents/engines/` | 代理引擎配置 |

---

> Cosmic Core 是異變全知宇宙智能體系統的心臟。  
> 所有高級功能都建立在這個核心層之上。
