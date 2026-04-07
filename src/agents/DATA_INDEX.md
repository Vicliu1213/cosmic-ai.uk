# Agents 数据组织索引

## 概览
- **总数据组**: 24 组
- **组织位置**: `src/agents/`
- **最后更新**: 2026-04-07

---

## 📊 数据组织结构

### 1️⃣ 宇宙策略优化 (4 组)
**路径**: `src/agents/cosmic_optimizations/`

| 文件名 | 大小 | 用途 | 说明 |
|--------|------|------|------|
| `cosmic_strategies___original.json` | 708B | 基础策略 | 原始的宇宙策略配置 |
| `cosmic_strategies___optimized_v1_(aggressive).json` | 1.0KB | 激进策略 | 高风险高收益优化版本 |
| `cosmic_strategies___optimized_v2_(balanced).json` | 915B | 平衡策略 | 风险收益均衡版本 |
| `cosmic_strategies___optimized_v3_(resonance_focused).json` | 1.2KB | 共振策略 | 专注于量子共振的版本 |

---

### 2️⃣ 智能体快照 (4 组)
**路径**: `src/agents/engine/snapshots/`

| 文件名 | 大小 | 用途 | 说明 |
|--------|------|------|------|
| `agent_1_snapshot.json` | 2.3KB | Agent 1 状态 | 智能体1的当前状态快照 |
| `agent_2_snapshot.json` | 1.4KB | Agent 2 状态 | 智能体2的当前状态快照 |
| `agent_3_snapshot.json` | 1.4KB | Agent 3 状态 | 智能体3的当前状态快照 |
| `market_snapshot.json` | 701B | 市场数据 | 市场状态快照 |

---

### 3️⃣ 引擎配置文件 (16 组)
**路径**: `src/agents/engine/config/`

所有文件均为 YAML 格式，包含不同引擎的配置参数。

| 配置名称 | 用途 |
|---------|------|
| `cosmic_config.yaml` | 宇宙系统主配置 |
| `cosmic_intelligence.yaml` | 宇宙智能配置 |
| `cosmic_engineering.yaml` | 宇宙工程配置 |
| `quantum_singularity.yaml` | 量子奇点配置 |
| `quantum_bio_fusion.yaml` | 量子-生物融合配置 |
| `quantum_holography.yaml` | 量子全息配置 |
| `neuro_quantum_synergy.yaml` | 神经-量子协同配置 |
| `consciousness_field.yaml` | 意识场配置 |
| `reality_programming.yaml` | 现实编程配置 |
| `temporal_dominance.yaml` | 时间统治配置 |
| `bio_photonics.yaml` | 生物光子配置 |
| `chaos_resonance.yaml` | 混沌共振配置 |
| `fractal_recursion.yaml` | 分形递归配置 |
| `topological_bio.yaml` | 拓扑生物配置 |
| `platform_heterogeneous.yaml` | 异构平台配置 |
| `perfect_fortress.yaml` | 完美堡垒配置 |

---

## 🔄 其他配置文件
**路径**: `src/agents/`

### 核心系统配置
- `api_config.yaml` - API 配置
- `database_config.yaml` - 数据库配置
- `deployment_config.yaml` - 部署配置
- `integration_config.yaml` - 集成配置
- `llm_tradebot_config.yaml` - LLM 交易机器人配置
- `marketbot_config.yaml` - 市场机器人配置
- `trading_config.yaml` - 交易配置
- `network_config.yaml` - 网络配置
- `monitoring_config.yaml` - 监控配置
- `logging_config.yaml` - 日志配置
- `ray_config.yaml` - Ray 分布式配置
- `performance_config.yaml` - 性能配置
- `security_config.yaml` - 安全配置
- `privacy_config.yaml` - 隐私配置
- `optimization_config.yaml` - 优化配置

### 模式配置
- `settings.json` - 基础设置
- `settings_enhanced.json` - 增强设置

### 数据记录
- `evolution_history.jsonl` - 进化历史记录

---

## 📁 核心子目录结构

```
agents/
├── cosmic_optimizations/      # 4组策略优化
├── engine/
│   ├── config/               # 16组引擎配置
│   └── snapshots/            # 4组智能体快照
├── core/                      # 核心模块配置
├── engines/                   # 多个引擎配置
├── deployment/               # 部署配置
├── optimization/             # 优化配置
├── schemas/                  # JSON 模式定义
├── security/                 # 安全配置
├── services/                 # 服务配置
└── systems/                  # 系统配置
```

---

## 💡 使用指南

### 访问策略配置
```python
import json
with open('src/agents/cosmic_optimizations/cosmic_strategies___optimized_v2_(balanced).json') as f:
    strategy = json.load(f)
```

### 访问智能体快照
```python
import json
with open('src/agents/engine/snapshots/agent_1_snapshot.json') as f:
    snapshot = json.load(f)
```

### 访问引擎配置
```python
import yaml
with open('src/agents/engine/config/quantum_singularity.yaml') as f:
    config = yaml.safe_load(f)
```

---

## 🔍 数据分类统计

| 类型 | 数量 | 格式 |
|-----|------|------|
| JSON 文件 | 10 | .json |
| YAML 文件 | 83 | .yaml / .yml |
| 其他配置 | 1 | .jsonl |
| **总计** | **94** | - |

---

## 📝 维护建议

1. **定期备份**: 这些是关键配置，请定期提交到 Git
2. **版本控制**: 新建优化版本时保持命名一致
3. **文档更新**: 当添加新配置时更新本索引
4. **配置验证**: 在使用前验证 YAML/JSON 格式正确性

---

**创建日期**: 2026-04-07  
**维护者**: Cosmic AI System  
**状态**: ✅ 整理完成
