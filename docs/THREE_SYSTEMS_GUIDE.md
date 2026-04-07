# 三大系统完整指南

本指南介绍 Cosmic AI 的三大核心系统的使用。

## 快速概览

Cosmic AI 现在拥有三个完全独立且相互协作的系统：

| 系统 | 位置 | 功能 | 文件夹数 | 配置文件 |
|------|------|------|--------|--------|
| **配置系统** | `config/` | 管理应用配置 | 6 | 17 |
| **文档系统** | `docs/` | 提供文档和指南 | 20+ | - |
| **监控系统** | `monitoring/` | 监控和告警 | 5 | 3 |

## 一、配置系统 (Config)

### 用途
集中管理所有应用配置，支持多环境部署。

### 核心内容

**环境配置** (`environments/`)
- 开发环境 (`development/`) - 本地开发配置
- 测试环境 (`staging/`) - 测试部署配置
- 生产环境 (`production/`) - 生产环境配置

**配置规则** (`schemas/`)
- 引擎配置 Schema
- 系统配置 Schema
- API 配置 Schema
- 交易配置 Schema

**配置模板** (`templates/`)
- 快速开始模板 - 最小化配置
- 企业级模板 - 完整功能
- 最小化模板 - 核心配置

**配置示例** (`examples/`)
- 完整示例 - 展示所有选项
- 自定义示例 - 常见场景
- 迁移指南 - 升级帮助

**备份管理** (`backups/`)
- 日备份 - 保留 7 天
- 周备份 - 保留 4 周
- 月备份 - 保留 12 个月

### 快速开始

```bash
# 1. 进入配置系统
cd config

# 2. 选择环境
export ENV=development

# 3. 应用配置
python ../app.py

# 4. 验证配置
python ../scripts/validate_config.py
```

### 关键文件

- `README.md` - 系统导航
- `INDEX.md` - 完整索引
- `environments/*/config.json` - 环境配置
- `schemas/*/schema.json` - Schema 规则

---

## 二、文档系统 (Documentation)

### 用途
提供完整的系统文档、指南、教程和参考资料。

### 核心内容

**技术文档** (`technical/`)
- 核心系统 (`core/`) - 系统设计
- 集成文档 (`integration/`) - 第三方集成
- 高级话题 (`advanced/`) - 性能优化
- 参考文档 (`reference/`) - 速查表
- 技术索引 (`INDEX.md`) - 69 个文档汇总

**快速指南** (`guides/`)
- 快速开始 (`quickstart/`) - 5 分钟快速启动
- 部署指南 (`deployment/`) - 多种部署方式
- 故障排除 (`troubleshooting/`) - 常见问题解决
- 管理指南 (`administration/`) - 系统管理

**API 文档** (`api/`)
- REST API (`rest/`) - HTTP 接口
- Python API (`python/`) - Python 库
- WebSocket (`websocket/`) - 实时推送
- Webhook (`webhooks/`) - 事件集成

**报告** (`reports/`)
- 日报告 (`daily/`) - 每日摘要
- 周报告 (`weekly/`) - 周总结
- 月报告 (`monthly/`) - 月度统计
- 年报告 (`annual/`) - 年度总结

**策略** (`strategies/`)
- 算法交易 (`algorithmic/`) - 传统算法
- 机器学习 (`ml/`) - ML 模型
- 量子策略 (`quantum/`) - 量子算法
- 混合策略 (`hybrid/`) - 多算法融合

**系统文档** (`system/`)
- 系统架构 (`architecture/`) - 整体设计
- 部署架构 (`deployment/`) - 网络拓扑
- 安全文档 (`security/`) - 安全加固
- 性能文档 (`performance/`) - 性能优化

**学习教程** (`tutorials/`)
- 初级教程 (`beginner/`) - 基础概念
- 中级教程 (`intermediate/`) - 深入功能
- 高级教程 (`advanced/`) - 源码分析

**常见问题** (`faq/`)
- 产品问题
- 技术问题
- 使用问题
- 故障问题

### 快速开始

```bash
# 1. 查看导航
cat docs/README.md

# 2. 查看技术索引
cat docs/technical/INDEX.md

# 3. 查看安装指南
cat docs/technical/INSTALLATION_GUIDE.md

# 4. 查看 API
cat docs/api/REST.md
```

### 关键文件

- `README.md` - 文档导航中心
- `DOCUMENTATION_INDEX.md` - 完整索引
- `technical/INDEX.md` - 技术文档索引 (69 个)
- `api/REST.md` - API 参考

---

## 三、监控系统 (Monitoring)

### 用途
实时监控系统性能、收集日志、发送告警、可视化仪表板。

### 核心内容

**指标收集** (`metrics/`)
- Prometheus (`prometheus/`) - 时间序列数据库
- Grafana (`grafana/`) - 可视化仪表板
- 自定义指标 (`custom/`) - 业务指标

**日志管理** (`logs/`)
- 日志聚合 (`aggregation/`) - 集中收集
- 日志分析 (`analysis/`) - 数据分析
- 日志保留 (`retention/`) - 保留策略

**告警系统** (`alerts/`)
- 告警规则 (`rules/`) - 检测规则
- 升级策略 (`escalation/`) - 分级处理
- 通知方式 (`notifications/`) - 多渠道通知

**仪表板** (`dashboards/`)
- 性能仪表板 (`performance/`) - CPU、内存、磁盘
- 交易仪表板 (`trading/`) - 成交、收益、风险
- 系统仪表板 (`system/`) - 可用性、延迟
- 健康仪表板 (`health/`) - 整体状态

**健康检查** (`health/`)
- 健康检查脚本 (`checks/`) - 定期检查
- 就绪/活性探针 (`probes/`) - K8s 探针
- 状态报告 (`status/`) - 状态输出

### 快速开始

```bash
# 1. 启动 Prometheus
docker run -d -p 9090:9090 \
  -v $(pwd)/monitoring/metrics/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# 2. 启动 Grafana
docker run -d -p 3000:3000 grafana/grafana

# 3. 运行健康检查
python monitoring/health/checks/health_check.py

# 4. 查看监控状态
curl http://localhost:9090
curl http://localhost:3000
```

### 关键文件

- `README.md` - 监控系统导航
- `MONITORING_INDEX.md` - 完整索引
- `metrics/prometheus/prometheus.yml` - Prometheus 配置
- `alerts/rules/alert_rules.yml` - 告警规则
- `health/checks/health_check.py` - 健康检查脚本

---

## 系统集成

### 三个系统如何配合

```
应用启动
   ↓
加载配置 (配置系统)
   ↓
查阅文档 (文档系统)
   ↓
运行应用
   ↓
监控运行 (监控系统)
   ↓
查看告警 (监控系统)
   ↓
按文档排查 (文档系统)
   ↓
调整配置 (配置系统)
```

---

## 常用命令速查

### 配置系统

```bash
# 验证配置
python scripts/validate_config.py

# 查看环境配置
cat config/environments/production/config.json

# 创建备份
cp -r config/environments/production config/backups/daily/$(date +%Y-%m-%d)

# 恢复配置
cp config/backups/daily/2026-04-05/* config/environments/production/
```

### 文档系统

```bash
# 查看所有文档
ls docs/

# 查看技术文档
ls docs/technical/

# 查看 API 文档
cat docs/api/REST.md

# 查看教程
ls docs/tutorials/
```

### 监控系统

```bash
# 启动监控
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3000:3000 grafana/grafana

# 检查健康状态
curl http://localhost:8000/health

# 查看 Prometheus 指标
curl http://localhost:9090/api/v1/query

# 查看告警状态
curl http://localhost:9093/api/v1/alerts
```

---

## 文档链接

### 系统总体
- [项目 README](README.md)
- [项目组织完成总结](ORGANIZATION_COMPLETION_SUMMARY.md)
- [系统完整设置报告](SYSTEM_COMPLETE_SETUP.md)
- [快速开始指南](QUICK_START.md)

### 配置系统
- [配置系统 README](config/README.md)
- [配置系统索引](config/INDEX.md)

### 文档系统
- [文档导航中心](docs/README.md)
- [文档完整索引](docs/DOCUMENTATION_INDEX.md)
- [技术文档索引](docs/technical/INDEX.md)

### 监控系统
- [监控系统 README](monitoring/README.md)
- [监控系统索引](monitoring/MONITORING_INDEX.md)

---

## 最佳实践

### 配置管理
1. ✅ 使用环境配置分离
2. ✅ 定期备份重要配置
3. ✅ 验证配置的合法性
4. ✅ 版本控制所有配置

### 文档查阅
1. ✅ 先查看相关 README
2. ✅ 使用索引快速定位
3. ✅ 参考具体示例
4. ✅ 查看 FAQ 解决问题

### 监控告警
1. ✅ 定期检查仪表板
2. ✅ 调整告警阈值
3. ✅ 保留充足的日志
4. ✅ 建立响应流程

---

## 获取帮助

### 查找文档
```bash
# 查看完整索引
cat SYSTEM_COMPLETE_SETUP.md

# 查看快速导航
cat QUICK_START.md

# 查看三系统指南
cat THREE_SYSTEMS_GUIDE.md
```

### 常见问题
参考 `docs/faq/` 文件夹

### 更多信息
查看各系统的 `README.md` 文件

---

**最后更新:** 2026-04-05  
**系统状态:** ✅ 完全就绪  
**准备就绪:** 🚀 可立即使用
