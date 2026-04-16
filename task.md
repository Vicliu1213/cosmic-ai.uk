curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc   # 或 source ~/.zshrc
hermes setup
#!/bin/bash
# rename.sh - 将 quantnexus 项目重命名为 cosmic-ai-uk

OLD="quantnexus"
NEW="cosmic-ai-uk"
OLD_NET="trading-net"
NEW_NET="cosmic-net"

# 1. 停止所有运行中的容器
docker-compose down

# 2. 修改文件名和目录名（如果需要）
# 这里不自动改目录名，只改文件内容

# 3. 修改 deploy.sh
sed -i "s/$OLD/$NEW/g" deploy.sh
sed -i "s/$OLD_NET/$NEW_NET/g" deploy.sh
sed -i "s/aeron-driver/cosmic-aeron-driver/g" deploy.sh
sed -i "s/market-publisher/cosmic-publisher/g" deploy.sh
sed -i "s/market-subscriber/cosmic-subscriber/g" deploy.sh
sed -i "s/flink-jobmanager/cosmic-flink-jm/g" deploy.sh
sed -i "s/flink-taskmanager/cosmic-flink-tm/g" deploy.sh
sed -i "s/clickhouse-01/cosmic-clickhouse/g" deploy.sh
sed -i "s/redis-master/cosmic-redis/g" deploy.sh

# 4. 修改已生成的配置文件（如果存在）
if [ -f docker-compose.yml ]; then
    sed -i "s/$OLD/$NEW/g" docker-compose.yml
    sed -i "s/$OLD_NET/$NEW_NET/g" docker-compose.yml
    sed -i "s/aeron-driver/cosmic-aeron-driver/g" docker-compose.yml
    sed -i "s/market-publisher/cosmic-publisher/g" docker-compose.yml
    sed -i "s/market-subscriber/cosmic-subscriber/g" docker-compose.yml
    sed -i "s/flink-jobmanager/cosmic-flink-jm/g" docker-compose.yml
    sed -i "s/flink-taskmanager/cosmic-flink-tm/g" docker-compose.yml
    sed -i "s/clickhouse-01/cosmic-clickhouse/g" docker-compose.yml
    sed -i "s/redis-master/cosmic-redis/g" docker-compose.yml
fi

# 5. 修改验证和基准脚本
for f in verify.sh benchmark.sh; do
    if [ -f $f ]; then
        sed -i "s/aeron-driver/cosmic-aeron-driver/g" $f
        sed -i "s/market-publisher/cosmic-publisher/g" $f
        sed -i "s/market-subscriber/cosmic-subscriber/g" $f
        sed -i "s/flink-jobmanager/cosmic-flink-jm/g" $f
        sed -i "s/flink-taskmanager/cosmic-flink-tm/g" $f
        sed -i "s/clickhouse-01/cosmic-clickhouse/g" $f
        sed -i "s/redis-master/cosmic-redis/g" $f
    fi
done

# 6. 修改 Prometheus 配置
if [ -f prometheus/prometheus.yml ]; then
    sed -i "s/flink-jobmanager/cosmic-flink-jm/g" prometheus/prometheus.yml
    sed -i "s/clickhouse-01/cosmic-clickhouse/g" prometheus/prometheus.yml
    sed -i "s/redis-master/cosmic-redis/g" prometheus/prometheus.yml
fi

# 7. 修改 Grafana 数据源
if [ -f grafana/datasources/prometheus.yml ]; then
    sed -i "s/flink-jobmanager/cosmic-flink-jm/g" grafana/datasources/prometheus.yml
    sed -i "s/clickhouse-01/cosmic-clickhouse/g" grafana/datasources/prometheus.yml
    sed -i "s/redis-master/cosmic-redis/g" grafana/datasources/prometheus.yml
fi

echo "✅ 重命名完成。请运行 ./deploy.sh 重新生成并启动服务。"
docker volume ls | grep quantnexus
docker volume rm <old_volume>   # 确认无数据后再删除sed -i 's/quantnexus/cosmic-ai-uk/g' deploy.sh
sed -i 's/trading-net/cosmic-net/g' deploy.sh
sed -i 's/aeron-driver/cosmic-aeron-driver/g' deploy.sh
sed -i 's/market-publisher/cosmic-publisher/g' deploy.sh
sed -i 's/market-subscriber/cosmic-subscriber/g' deploy.sh
sed -i 's/flink-jobmanager/cosmic-flink-jm/g' deploy.sh
sed -i 's/flink-taskmanager/cosmic-flink-tm/g' deploy.sh
sed -i 's/clickhouse-01/cosmic-clickhouse/g' deploy.sh
sed -i 's/redis-master/cosmic-redis/g' deploy.sh
sed -i 's/aeron-driver/cosmic-aeron-driver/g' verify.sh benchmark.sh
sed -i 's/market-publisher/cosmic-publisher/g' verify.sh benchmark.sh
# ... 同理其他服务
