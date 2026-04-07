# 快速开始指南

## 🚀 5 分钟快速开始

### 1. 查看项目结构
```bash
# 查看根目录结构
ls -la

# 查看 docs 文件夹
ls -la docs/

# 查看 src/engine/config
ls -la src/engine/config/
```

### 2. 查阅关键文档

| 需求 | 文档位置 |
|------|--------|
| 📖 项目概览 | [README.md](README.md) |
| 📝 组织总结 | [ORGANIZATION_COMPLETION_SUMMARY.md](ORGANIZATION_COMPLETION_SUMMARY.md) |
| 📚 文档导航 | [docs/README.md](docs/README.md) |
| 🔧 技术文档索引 | [docs/technical/INDEX.md](docs/technical/INDEX.md) |
| 💾 安装指南 | [docs/technical/INSTALLATION_GUIDE.md](docs/technical/INSTALLATION_GUIDE.md) |
| 🔌 API 参考 | [docs/technical/API_REFERENCE.md](docs/technical/API_REFERENCE.md) |
| 🏗️ 系统架构 | [docs/technical/ARCHITECTURE.md](docs/technical/ARCHITECTURE.md) |
| ⚙️ 配置指南 | [docs/technical/CONFIGURATION_DEPLOYMENT_GUIDE.md](docs/technical/CONFIGURATION_DEPLOYMENT_GUIDE.md) |

### 3. 验证配置部署

```bash
# 运行配置验证脚本
python src/scripts/deploy_config.py

# 期望输出：✅ 所有检查通过！
```

### 4. 在代码中使用配置

```python
# 导入配置接口
from src.engine import get_engine_config, get_system_defaults

# 加载引擎配置
engine_config = get_engine_config()
print(engine_config['engine']['name'])  # HybridQuantumClassicalEngine

# 加载系统默认值
sys_defaults = get_system_defaults()
print(sys_defaults['system']['version'])  # 1.0.0
```

### 5. 验证配置导入

```python
from src.engine.config import EngineConfigLoader

loader = EngineConfigLoader()
config = loader.get_engine_config()
print(f"引擎配置已加载: {len(config)} 个配置项")
```

## 📂 文件夹导航

```
项目根目录 /
│
├── 📄 README.md                           ← 项目主文档
├── 📄 QUICK_START.md                      ← 你在这里
├── 📄 ORGANIZATION_COMPLETION_SUMMARY.md  ← 组织完成报告
│
├── 📁 docs/                               ← 文档中心
│   ├── README.md                          ← 文档导航
│   ├── technical/                         ← 技术文档 (69个)
│   │   ├── INDEX.md                       ← 技术文档索引
│   │   ├── INSTALLATION_GUIDE.md          ← 安装指南
│   │   ├── API_REFERENCE.md               ← API 参考
│   │   ├── ARCHITECTURE.md                ← 架构文档
│   │   └── ...
│   ├── reports/                           ← 报告文档 (35个)
│   │   ├── CONFIGURATION_ALIGNMENT_REPORT.md
│   │   └── ...
│   ├── guides/                            ← 操作指南
│   ├── strategies/                        ← 策略文档
│   ├── system/                            ← 系统文档
│   └── archive/                           ← 归档文档
│
├── 📁 src/
│   ├── engine/
│   │   └── config/                        ← 引擎配置核心 ⭐
│   │       ├── __init__.py                ← 配置加载器
│   │       ├── engine_config.json         ← 引擎配置
│   │       ├── system_defaults.json       ← 系统默认值
│   │       └── config_schema.json         ← Schema 验证
│   │
│   └── scripts/                           ← 脚本文件夹
│       └── deploy_config.py               ← 配置部署验证 ⭐
│
├── 📁 data/                               ← 数据文件夹
│   ├── COMPLETE_SYSTEM_STRUCTURE.json
│   ├── ERROR_FIXES_DICTIONARY.json
│   └── ...
│
├── 📁 config/                             ← 项目配置
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── ...
│
└── ... (其他配置文件夹)
```

## 🎯 常见任务

### 查看系统架构
```bash
cat docs/technical/ARCHITECTURE.md
```

### 安装系统
```bash
cat docs/technical/INSTALLATION_GUIDE.md
# 然后按步骤执行
```

### 查看 API 文档
```bash
cat docs/technical/API_REFERENCE.md
```

### 了解配置系统
```bash
cat docs/technical/CONFIGURATION_DEPLOYMENT_GUIDE.md
```

### 查看完整技术文档清单
```bash
cat docs/technical/INDEX.md
```

## 📋 配置文件快速查询

### 主要配置文件位置

| 文件名 | 位置 | 用途 |
|--------|------|------|
| engine_config.json | `src/engine/config/` | 引擎核心配置 |
| system_defaults.json | `src/engine/config/` | 系统默认值 |
| config_schema.json | `src/engine/config/` | Schema 验证规则 |
| docker-compose.yml | `config/` | Docker 配置 |
| requirements.txt | `config/` | Python 依赖 |

### 配置加载优先级

```
1. 环境变量 (最高)
   ↓
2. engine_config.json
   ↓
3. system_defaults.json
   ↓
4. 硬编码默认值 (最低)
```

## 🔍 文件查询

### 查找特定文档

```bash
# 查找所有 quantum 相关文档
ls docs/technical/ | grep -i quantum

# 查找所有报告
ls docs/reports/

# 查找所有脚本
ls src/scripts/
```

### 查找配置项

```bash
# 查看引擎配置内容
cat src/engine/config/engine_config.json | head -20

# 查看系统默认值
cat src/engine/config/system_defaults.json
```

## ✅ 验证清单

- [ ] 能够查看 docs/ 文件夹
- [ ] 能够访问 src/engine/config/ 配置文件
- [ ] 能够运行 deploy_config.py 脚本
- [ ] 能够从 Python 代码导入配置
- [ ] 能够阅读技术文档索引

## 🆘 常见问题

### Q: 配置文件在哪里？
A: 在 `src/engine/config/` 文件夹中，包含三个主要文件：
- engine_config.json
- system_defaults.json  
- config_schema.json

### Q: 如何验证配置已正确部署？
A: 运行 `python src/scripts/deploy_config.py`

### Q: 我想了解系统架构？
A: 查看 `docs/technical/ARCHITECTURE.md`

### Q: 如何在代码中加载配置？
A: 使用 `from src.engine import get_engine_config`

### Q: 技术文档在哪里？
A: 在 `docs/technical/` 文件夹中，共 69 个文档

## 📞 相关文档快速链接

- 📖 [项目 README](README.md)
- 📊 [组织完成总结](ORGANIZATION_COMPLETION_SUMMARY.md)
- 📚 [文档中心](docs/README.md)
- 🔧 [技术文档索引](docs/technical/INDEX.md)
- 💾 [安装指南](docs/technical/INSTALLATION_GUIDE.md)
- 🔌 [API 参考](docs/technical/API_REFERENCE.md)
- 🏗️ [系统架构](docs/technical/ARCHITECTURE.md)
- ⚙️ [配置部署指南](docs/technical/CONFIGURATION_DEPLOYMENT_GUIDE.md)
- 📋 [配置对齐报告](docs/reports/CONFIGURATION_ALIGNMENT_REPORT.md)

---

**🎉 现在你已经准备好开始使用 Cosmic AI 系统了！**

如需更多帮助，请参考相关文档。
