# 监控系统

Cosmic AI 的完整监控、日志、告警和健康检查系统。

## 目录结构

```
monitoring/
├── README.md (本文件)
├── metrics/                 # 性能指标收集
│   ├── prometheus/          # Prometheus 配置
│   ├── grafana/             # Grafana 配置
│   └── custom/              # 自定义指标
├── logs/                    # 日志管理系统
│   ├── aggregation/         # 日志聚合配置
│   ├── analysis/            # 日志分析脚本
│   └── retention/           # 日志保留策略
├── alerts/                  # 告警系统
│   ├── rules/               # 告警规则
│   ├── escalation/          # 升级策略
│   └── notifications/       # 通知配置
├── dashboards/              # 监控仪表板
│   ├── performance/         # 性能仪表板
│   ├── trading/             # 交易仪表板
│   ├── system/              # 系统仪表板
│   └── health/              # 健康检查仪表板
└── health/                  # 系统健康检查
    ├── checks/              # 健康检查脚本
    ├── probes/              # 活性/就绪探针
    └── status/              # 状态报告
```

## 核心功能

### 1. 指标收集 (Metrics)
实时收集系统和应用级别的性能指标

**支持的指标:**
- CPU 和内存使用率
- 磁盘 I/O 性能
- 网络流量
- 数据库连接数
- API 响应时间
- 交易成功率
- 算法准确率

### 2. 日志管理 (Logs)
集中收集、聚合和分析系统日志

**功能:**
- 多源日志聚合
- 实时日志分析
- 自动日志保留
- 搜索和过滤

### 3. 告警系统 (Alerts)
检测异常情况并发出告警

**告警规则:**
- 性能告警 (高CPU、高内存)
- 可用性告警 (服务宕机)
- 业务告警 (交易失败、亏损过大)
- 安全告警 (异常登录、配置变更)

**通知方式:**
- 邮件
- Slack
- 电话
- SMS

### 4. 仪表板 (Dashboards)
可视化实时监控数据

**仪表板类型:**
- 性能仪表板 - CPU、内存、磁盘、网络
- 交易仪表板 - 成交量、收益率、风险指标
- 系统仪表板 - 服务健康、可用性、延迟
- 健康仪表板 - 整体系统健康状态

### 5. 健康检查 (Health)
定期检查系统各组件的状态

**检查项:**
- 数据库连接
- 缓存可用性
- 外部 API 可达性
- 磁盘空间
- 服务响应时间

## 快速开始

### 启动 Prometheus
```bash
docker run -d \
  -p 9090:9090 \
  -v $(pwd)/monitoring/metrics/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 启动 Grafana
```bash
docker run -d \
  -p 3000:3000 \
  grafana/grafana
```

### 检查系统健康
```bash
curl http://localhost:8000/health
```

## 指标详解

### 系统指标
- `system_cpu_usage` - CPU 使用率 (%)
- `system_memory_usage` - 内存使用率 (%)
- `system_disk_usage` - 磁盘使用率 (%)
- `system_disk_io` - 磁盘 I/O (bytes/s)
- `system_network_in` - 网络入站 (bytes/s)
- `system_network_out` - 网络出站 (bytes/s)

### 应用指标
- `app_requests_total` - 请求总数
- `app_request_duration_seconds` - 请求延迟 (秒)
- `app_errors_total` - 错误总数
- `app_trades_total` - 交易总数

### 业务指标
- `trading_profit_loss` - 收益/亏损
- `trading_win_rate` - 成功率 (%)
- `trading_drawdown` - 最大回撤 (%)
- `trading_sharpe_ratio` - 夏普比率

## 告警规则示例

### 高 CPU 使用率
```
alert: HighCPUUsage
expr: system_cpu_usage > 80
for: 5m
severity: warning
```

### 服务不可用
```
alert: ServiceDown
expr: app_health_status != 1
for: 1m
severity: critical
```

### 高错误率
```
alert: HighErrorRate
expr: app_errors_total / app_requests_total > 0.05
for: 5m
severity: critical
```

## 日志采样

### Prometheus 配置
```yaml
# monitoring/metrics/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cosmic-ai'
    static_configs:
      - targets: ['localhost:8000']
```

### 告警规则
```yaml
# monitoring/alerts/rules/alerts.yml
groups:
  - name: cosmic_ai_alerts
    rules:
      - alert: HighCPUUsage
        expr: system_cpu_usage > 80
        for: 5m
```

## 健康检查端点

### 活性检查 (Liveness)
```
GET /health/live
Response: 200 OK (service is running)
```

### 就绪检查 (Readiness)
```
GET /health/ready
Response: 200 OK (service is ready to accept requests)
```

### 详细健康状态
```
GET /health/detailed
Response:
{
  "status": "healthy",
  "components": {
    "database": "ok",
    "cache": "ok",
    "api": "ok"
  },
  "timestamp": "2026-04-05T12:00:00Z"
}
```

## 监控流程

```
[应用] 
   ↓ 暴露指标
[Prometheus] 
   ↓ 存储时间序列数据
[Grafana] 
   ↓ 可视化仪表板
[告警引擎] 
   ↓ 检测异常
[通知系统] 
   ↓ 发送告警
[工程师] 
   ↓ 响应和修复
```

## 最佳实践

1. **定期审查仪表板** - 每日检查关键指标
2. **调整告警阈值** - 根据实际情况调整
3. **保留日志** - 至少保留 30 天的日志
4. **性能优化** - 定期分析瓶颈
5. **容量规划** - 基于历史数据做规划

## 常见问题

### Q: 如何自定义指标？
A: 在 `metrics/custom/` 中创建新的指标采集器

### Q: 告警如何升级？
A: 在 `alerts/escalation/` 中配置升级规则

### Q: 日志保留多久？
A: 在 `logs/retention/` 中配置保留策略

### Q: 如何添加新的仪表板？
A: 在 `dashboards/` 中创建新的 JSON 配置

## 相关文档

- [部署指南](../docs/guides/deployment/)
- [系统架构](../docs/system/architecture/)
- [性能优化](../docs/system/performance/)

最后更新: 2026-04-05
