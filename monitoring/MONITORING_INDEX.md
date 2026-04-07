# 监控系统完整索引

## 监控框架

### 指标收集 (Metrics)
- [Prometheus 配置](metrics/prometheus/)
- [自定义指标](metrics/custom/)
- [Grafana 仪表板](metrics/grafana/)

### 日志管理 (Logs)
- [日志聚合](logs/aggregation/)
- [日志分析](logs/analysis/)
- [日志保留](logs/retention/)

### 告警系统 (Alerts)
- [告警规则](alerts/rules/)
- [升级策略](alerts/escalation/)
- [通知方式](alerts/notifications/)

### 仪表板 (Dashboards)
- [性能仪表板](dashboards/performance/)
- [交易仪表板](dashboards/trading/)
- [系统仪表板](dashboards/system/)
- [健康仪表板](dashboards/health/)

### 健康检查 (Health)
- [健康检查](health/checks/)
- [就绪探针](health/probes/)
- [状态报告](health/status/)

## 主要指标

### 系统指标
- CPU 使用率
- 内存使用率
- 磁盘使用率
- 网络流量

### 应用指标
- 请求数
- 响应时间
- 错误率
- 吞吐量

### 业务指标
- 交易成功率
- 收益率
- 最大回撤
- 夏普比率

## 告警配置

### 性能告警
- HighCPUUsage
- HighMemoryUsage
- SlowDatabase

### 可用性告警
- ServiceDown
- DatabaseDown
- CacheDown

### 业务告警
- TradeFailure
- HighDrawdown
- LossExceeded

## 快速命令

### 启动监控
```bash
docker-compose -f monitoring/docker-compose.yml up
```

### 健康检查
```bash
curl http://localhost:8000/health/detailed
```

### 查看指标
```bash
curl http://localhost:9090/api/v1/query
```

### 查看告警
```bash
curl http://localhost:9093/api/v1/alerts
```

最后更新: 2026-04-05
