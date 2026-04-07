# 生产环境配置

用于生产环境部署的环境配置。

## 文件列表

- `config.json` - 生产环境主配置文件

## 特点

- 性能优化
- 日志级别：WARNING
- PostgreSQL + SSL
- Redis 集群模式
- 速率限制启用

## 使用

```bash
export ENV=production
python app.py
```

## 安全提示

- 从环境变量中读取敏感信息
- 启用 SSL/TLS
- 定期备份数据库
- 监控系统状态

最后更新: 2026-04-05
