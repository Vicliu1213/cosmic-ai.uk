# 配置系统

Cosmic AI 的完整配置管理系统。

## 目录结构

```
config/
├── README.md (本文件)
├── environments/         # 环境特定配置
│   ├── development/      # 开发环境
│   ├── staging/          # 测试环境
│   └── production/       # 生产环境
├── schemas/              # 配置 Schema 定义
│   ├── engine/           # 引擎配置 Schema
│   ├── system/           # 系统配置 Schema
│   ├── api/              # API 配置 Schema
│   └── trading/          # 交易配置 Schema
├── templates/            # 配置模板
│   ├── quick-start/      # 快速开始模板
│   ├── enterprise/       # 企业级模板
│   └── minimal/          # 最小化模板
├── examples/             # 配置示例
│   ├── complete/         # 完整示例
│   ├── custom/           # 自定义示例
│   └── migration/        # 迁移示例
├── backups/              # 配置备份
│   ├── daily/            # 日备份
│   ├── weekly/           # 周备份
│   └── monthly/          # 月备份
│
├── docker-compose.yml    # Docker 配置
├── requirements.txt      # Python 依赖
├── environment.yml       # Conda 环境
└── main.tf              # Terraform 配置
```

## 快速开始

### 1. 选择环境配置
```bash
# 复制相应环境配置
cp config/environments/development/* .env.local
```

### 2. 加载配置
```bash
# 从 Python 加载
from src.config import load_environment_config
config = load_environment_config('development')
```

### 3. 验证配置
```bash
python scripts/validate_config.py
```

## 环境配置

### development/ (开发环境)
- 调试模式启用
- 日志级别：DEBUG
- 本地数据库
- 开发 API 密钥

### staging/ (测试环境)
- 完整功能测试
- 日志级别：INFO
- 测试数据库
- 测试 API 密钥

### production/ (生产环境)
- 优化性能
- 日志级别：WARNING
- 生产数据库
- 正式 API 密钥

## Schema 定义

### engine/ - 引擎配置 Schema
定义引擎各项参数的数据类型和约束

### system/ - 系统配置 Schema
定义系统级别的配置结构

### api/ - API 配置 Schema
定义 API 端点和认证配置

### trading/ - 交易配置 Schema
定义交易参数和策略配置

## 配置模板

### quick-start/ - 快速开始
最小化配置，快速启动系统

### enterprise/ - 企业级
完整功能配置，适合生产环境

### minimal/ - 最小化
仅包含必需配置，低资源占用

## 配置示例

### complete/ - 完整示例
展示所有配置选项的完整示例

### custom/ - 自定义示例
常用的定制配置示例

### migration/ - 迁移示例
从旧系统迁移配置的示例

## 配置备份

### daily/ - 日备份
每日自动备份一份配置

### weekly/ - 周备份
每周保存一份完整备份

### monthly/ - 月备份
每月存档备份

## 配置优先级

```
1. 环境变量
   ↓
2. 环境特定配置 (environments/)
   ↓
3. 模板配置 (templates/)
   ↓
4. 默认配置
```

## 文件说明

- **docker-compose.yml** - Docker Compose 配置
- **requirements.txt** - Python 项目依赖
- **environment.yml** - Conda 虚拟环境配置
- **main.tf** - Terraform 基础设施配置

## 常见任务

### 创建新的环境配置
```bash
cp -r config/templates/enterprise config/environments/custom-env
```

### 验证所有配置
```bash
python scripts/validate_all_configs.py
```

### 备份当前配置
```bash
cp -r config/environments/production config/backups/weekly/$(date +%Y-%m-%d)
```

### 恢复配置
```bash
cp config/backups/weekly/2026-04-05/* config/environments/production/
```

## 相关文档

- [配置部署指南](../docs/technical/CONFIGURATION_DEPLOYMENT_GUIDE.md)
- [系统架构](../docs/technical/ARCHITECTURE.md)
- [安装指南](../docs/technical/INSTALLATION_GUIDE.md)

最后更新: 2026-04-05
