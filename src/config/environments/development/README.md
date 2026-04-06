# 开发环境配置

用于本地开发的环境配置。

## 文件列表

- `config.json` - 开发环境主配置文件

## 特点

- 调试模式启用
- 日志级别：DEBUG
- 本地SQLite数据库
- 内存缓存

## 使用

```bash
export ENV=development
python app.py
```

## 配置项

```json
{
  "environment": "development",
  "debug": true,
  "log_level": "DEBUG",
  "database": {
    "type": "sqlite",
    "path": "data/development.db"
  }
}
```

最后更新: 2026-04-05
