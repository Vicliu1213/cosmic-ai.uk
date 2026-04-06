# 配置模板

预置的配置模板，快速启动系统。

## 模板列表

- `quick-start/config.json` - 快速开始（最小化配置）
- `enterprise/config.json` - 企业级（完整配置）
- `minimal/config.json` - 最小化（核心配置）

## 使用模板

```bash
# 使用快速开始模板
cp config/templates/quick-start/config.json .env.local

# 使用企业级模板
cp config/templates/enterprise/config.json .env.local

# 根据需要修改配置
nano .env.local
```

最后更新: 2026-04-05
