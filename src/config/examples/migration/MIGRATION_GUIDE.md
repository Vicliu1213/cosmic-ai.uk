# 配置迁移指南

从旧系统迁移配置到 Cosmic AI。

## 步骤 1: 导出旧配置
```bash
python export_old_config.py > old_config.yaml
```

## 步骤 2: 转换配置格式
```bash
python convert_config.py old_config.yaml new_config.json
```

## 步骤 3: 验证新配置
```bash
python validate_config.py new_config.json
```

## 步骤 4: 应用新配置
```bash
cp new_config.json config/environments/production/config.json
```

## 步骤 5: 测试系统
```bash
python test_config.py
```

## 常见问题

### Q: 如何处理不兼容的配置项？
A: 使用配置映射文件进行自动转换

### Q: 如何回滚到旧配置？
A: 使用备份: `cp config/backups/monthly/2026-03-* config/environments/production/`

