# 配置部署指南

本指南介绍如何在 Cosmic AI 系统中部署和管理配置文件。

## 概述

系统配置已集中部署到引擎核心 (`src/engine/config/`)，确保配置的统一管理和一致性。

## 配置文件结构

```
src/engine/config/
├── __init__.py                 # 配置加载器模块
├── engine_config.json          # 引擎核心配置
├── system_defaults.json        # 系统默认值
├── config_schema.json          # JSON Schema 验证规则
└── schemas/                    # 其他 schema 文件
    └── (future expansion)
```

## 配置文件说明

### 1. engine_config.json
引擎的核心配置文件，包含：
- 元数据（版本、类型、部署日期）
- 引擎设置（名称、类型、模式）
- 量子引擎配置
- 经典引擎配置
- 数据层配置（缓存、数据库）
- API 集成配置
- 算法配置
- 监控设置

**示例：**
```json
{
  "metadata": {
    "version": "1.0.0",
    "engine_type": "hybrid_quantum_classical",
    "deployment_date": "2026-04-05"
  },
  "engine": {
    "name": "HybridQuantumClassicalEngine",
    "type": "hybrid",
    "enabled": true,
    "mode": "production"
  }
}
```

### 2. system_defaults.json
系统运行时的默认配置，包含：
- 系统信息（名称、版本、环境）
- 性能参数（并发数、队列大小、超时时间）
- 交易参数（默认交易对、间隔、头寸大小）
- 风险管理参数（最大回撤、日亏损限额）
- 通知配置
- 日志配置

**示例：**
```json
{
  "system": {
    "name": "Cosmic AI Trading System",
    "version": "1.0.0",
    "environment": "production"
  },
  "performance": {
    "max_concurrent_trades": 100,
    "timeout_seconds": 30
  }
}
```

### 3. config_schema.json
JSON Schema 验证规则，用于验证配置文件的合法性。

## 使用方法

### 在 Python 代码中加载配置

```python
from src.engine import get_engine_config, get_system_defaults

# 加载引擎配置
engine_config = get_engine_config()
print(engine_config['engine']['name'])

# 加载系统默认配置
sys_defaults = get_system_defaults()
print(sys_defaults['system']['version'])
```

### 从引擎模块导入

```python
from src.engine.config import EngineConfigLoader

loader = EngineConfigLoader()
config = loader.get_engine_config()
```

### 验证配置

```python
from src.engine import validate_config

config = {"engine": {"name": "Test"}}
if validate_config(config):
    print("配置有效")
else:
    print("配置无效")
```

## 配置对齐

### 配置来源汇总

| 位置 | 文件 | 用途 | 迁移状态 |
|------|------|------|--------|
| `data/` | ERROR_FIXES_DICTIONARY.json | 错误字典 | 📁 已保留 |
| `data/` | COMPLETE_SYSTEM_STRUCTURE.json | 系统结构 | 📁 已保留 |
| `config/` | docker-compose.yml | Docker 配置 | 📁 已保留 |
| `config/` | requirements.txt | 依赖配置 | 📁 已保留 |
| `src/engine/config/` | engine_config.json | 引擎配置 | ✅ 已部署 |
| `src/engine/config/` | system_defaults.json | 系统默认 | ✅ 已部署 |

### 配置优先级

系统按以下顺序优先级加载配置：

1. **环境变量** - 最高优先级
2. **engine_config.json** - 引擎配置
3. **system_defaults.json** - 系统默认值
4. **硬编码默认值** - 最低优先级

## 部署验证

运行部署验证脚本检查配置完整性：

```bash
python src/scripts/deploy_config.py
```

输出示例：
```
✅ 所有检查通过！配置已成功部署到引擎核心。
```

## 扩展配置

### 添加新的配置文件

1. 在 `src/engine/config/` 中创建新的 JSON 文件
2. 在 `config_schema.json` 中定义对应的 schema
3. 在 `EngineConfigLoader` 中添加加载方法

```python
def get_custom_config(self) -> Dict[str, Any]:
    """Get custom configuration."""
    return self.load_config("custom_config")
```

### 验证新配置

确保新配置：
- 符合 JSON 格式
- 通过 schema 验证
- 包含必要的字段

## 最佳实践

1. **保持配置文件简洁** - 只存储必要的配置
2. **使用环境变量覆盖** - 不同环境使用不同配置
3. **定期验证** - 运行部署验证脚本
4. **版本控制** - 跟踪配置文件的变更
5. **文档化** - 记录每个配置项的用途

## 故障排除

### 配置文件找不到

```
Error: Configuration file not found
```

**解决方案：**
- 检查文件是否存在于 `src/engine/config/`
- 确认文件名拼写正确
- 验证文件权限

### JSON 解析错误

```
Error: Failed to parse configuration file
```

**解决方案：**
- 使用 JSON 验证工具检查语法
- 确保没有拖尾逗号
- 验证所有字符串都用双引号括起

### Schema 验证失败

```
Error: Configuration validation failed
```

**解决方案：**
- 检查配置是否符合 schema 定义
- 验证必需字段是否存在
- 检查数据类型是否匹配

## 相关文档

- [系统架构](ARCHITECTURE.md)
- [安装指南](INSTALLATION_GUIDE.md)
- [API 参考](API_REFERENCE.md)

## 更新日志

### 版本 1.0.0 (2026-04-05)
- 初始配置系统部署
- 支持 engine_config.json 和 system_defaults.json
- 集成 JSON Schema 验证
- 创建配置加载器模块
