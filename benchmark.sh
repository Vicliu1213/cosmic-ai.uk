#!/bin/bash
echo "📊 运行性能基准测试..."
echo "1. Aeron Ping-Pong 延迟 (需安装额外工具，此处模拟)"
echo "2. ClickHouse 聚合性能"
docker exec clickhouse clickhouse-client --query "
CREATE TABLE IF NOT EXISTS test_ticks (symbol String, price Float64, volume UInt32, ts DateTime) ENGINE = MergeTree ORDER BY ts;
INSERT INTO test_ticks SELECT 'AAPL', rand()%200+100, rand()%10000, now() - INTERVAL rand()%1000 SECOND FROM numbers(1000000);
SELECT symbol, avg(price), sum(volume) FROM test_ticks GROUP BY symbol FORMAT Pretty"
echo "3. 系统资源"
docker stats --no-stream
