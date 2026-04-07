# Prometheus 配置

Prometheus 时间序列数据库的配置和使用。

## 文件列表

- `prometheus.yml` - 主配置文件

## 功能

- 指标采集
- 时间序列存储
- 告警评估

## 启动

```bash
docker run -d -p 9090:9090 \
  -v $(pwd)/monitoring/metrics/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

## 查询指标

访问 http://localhost:9090 使用 Prometheus 查询界面。

最后更新: 2026-04-05
