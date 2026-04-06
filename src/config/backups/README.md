# 配置备份

配置文件的自动备份和版本管理。

## 备份策略

- **daily/** - 每日备份（保留7天）
- **weekly/** - 周备份（保留4周）
- **monthly/** - 月备份（保留12个月）

## 备份操作

### 创建备份
```bash
cp -r config/environments/production \
  config/backups/daily/$(date +%Y-%m-%d)
```

### 查看备份
```bash
ls -la config/backups/daily/
ls -la config/backups/weekly/
ls -la config/backups/monthly/
```

### 恢复备份
```bash
cp -r config/backups/daily/2026-04-05/* \
  config/environments/production/
```

## 自动备份

配置系统支持自动备份（详见部署文档）

最后更新: 2026-04-05
