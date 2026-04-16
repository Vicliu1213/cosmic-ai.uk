#!/bin/bash
echo "🔍 验证系统健康状态..."
PASS=0; FAIL=0
for svc in aeron-driver market-publisher market-subscriber flink-jobmanager flink-taskmanager clickhouse redis prometheus grafana pyroscope tempo chaos-mesh; do
    if docker ps --format '{{.Names}}' | grep -q "^$svc$"; then
        echo "✅ $svc"
        ((PASS++))
    else
        echo "❌ $svc"
        ((FAIL++))
    fi
done
echo -n "Aeron 通信: "
docker logs market-subscriber 2>&1 | tail -5 | grep -q "接收速率" && echo "✅" || echo "❌"
echo -n "ClickHouse: "
docker exec clickhouse clickhouse-client --query "SELECT 1" 2>/dev/null | grep -q 1 && echo "✅" || echo "❌"
echo -n "Redis: "
docker exec redis redis-cli -a trading2024 ping 2>/dev/null | grep -q PONG && echo "✅" || echo "❌"
echo -n "Prometheus: "
curl -s http://localhost:9090/-/healthy | grep -q OK && echo "✅" || echo "❌"
echo -n "Grafana: "
curl -s http://localhost:3000/api/health | grep -q "ok" && echo "✅" || echo "❌"
echo "验证完成: $PASS 通过, $FAIL 失败"
