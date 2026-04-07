# SQL、Redis 和 Azure 云服务集成指南
# SQL, Redis and Azure Cloud Services Integration Guide

## 📋 目录
1. [快速开始](#快速开始)
2. [数据库配置](#数据库配置)
3. [Redis 缓存](#redis-缓存)
4. [Azure 云服务](#azure-云服务)
5. [完整集成示例](#完整集成示例)
6. [故障排除](#故障排除)

---

## 🚀 快速开始

### 最简单的配置（本地开发）

```bash
# 1. 使用默认配置（SQLite + 本地 Redis）
# .env 已预先配置好

# 2. 启动 Redis（如已安装）
redis-server

# 3. 测试连接
python /root/comic_ai/setup_database_cloud.py

# 4. 在代码中使用
from src.core.database_cloud_integration import DatabaseManager

manager = DatabaseManager(db_type="sqlite")
manager.setup_database()
manager.setup_cache()
```

---

## 🗄️ 数据库配置

### 选项 1: SQLite（本地，推荐用于开发）

**配置**
```ini
# .env
DATABASE_TYPE=sqlite
DATABASE_PATH=data/comic_ai.db
DATABASE_BACKUP_PATH=data/backups
```

**代码使用**
```python
from src.core.database_cloud_integration import DatabaseManager

manager = DatabaseManager(db_type="sqlite")
manager.setup_database(db_path="data/comic_ai.db")

# 执行查询
manager.db.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"
)

# 获取数据
users = manager.db.fetch_all("SELECT * FROM users")
```

**优点**
- ✅ 开箱即用，无需配置
- ✅ 无需额外服务
- ✅ 文件式存储

**缺点**
- ❌ 单用户
- ❌ 不支持并发写入
- ❌ 性能有限

---

### 选项 2: MySQL（远程，推荐用于生产）

**安装 MySQL**

```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# 或使用 Docker
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -p 3306:3306 \
  mysql:8.0
```

**配置**
```ini
# .env
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=comic_ai
```

**创建数据库**
```bash
mysql -u root -p -e "CREATE DATABASE comic_ai;"
```

**代码使用**
```python
from src.core.database_cloud_integration import DatabaseManager

manager = DatabaseManager(db_type="mysql")
manager.setup_database(
    host="localhost",
    port=3306,
    user="root",
    password="your_password",
    database="comic_ai"
)

# 执行查询
manager.db.execute(
    """
    CREATE TABLE IF NOT EXISTS portfolio (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(10),
        quantity INT,
        price FLOAT
    )
    """
)
```

**优点**
- ✅ 支持多用户并发
- ✅ 适合生产环境
- ✅ 强大的查询能力

**缺点**
- ❌ 需要服务器配置
- ❌ 需要备份管理
- ❌ 性能取决于服务器

---

### 选项 3: PostgreSQL

类似 MySQL，使用不同的连接器。

---

## ⚡ Redis 缓存

### 本地 Redis 设置

**安装 Redis**

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# 或使用 Docker
docker run -d -p 6379:6379 redis:latest

# 验证运行
redis-cli ping  # 应该返回 PONG
```

**配置**
```ini
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_CACHE_TTL=3600
```

**代码使用**
```python
from src.core.database_cloud_integration import DatabaseManager

manager = DatabaseManager()
manager.setup_cache(
    host="localhost",
    port=6379,
    db=0,
    password=None
)

# 设置缓存
manager.cache.set("user:123", {"name": "Alice", "age": 30}, ttl=3600)

# 获取缓存
user = manager.cache.get("user:123")
# 输出: {"name": "Alice", "age": 30}

# 删除缓存
manager.cache.delete("user:123")

# 清空所有缓存
manager.cache.clear()

# 获取统计
stats = manager.cache.get_stats()
print(stats)
```

### 云端 Redis

**Azure Cache for Redis**

```ini
# .env
REDIS_CLOUD_HOST=your-redis.redis.cache.windows.net
REDIS_CLOUD_PORT=6380
REDIS_CLOUD_PASSWORD=[REPLACE_WITH_YOUR_PASSWORD]

# 代码
manager.setup_cache(
    host="your-redis.redis.cache.windows.net",
    port=6380,
    password="your-password"
)
```

**AWS ElastiCache**

```ini
REDIS_HOST=your-redis-endpoint.cache.amazonaws.com
REDIS_PORT=6379
REDIS_PASSWORD=[REPLACE_WITH_YOUR_PASSWORD]
```

**Redis Cloud（第三方）**

1. 访问 https://app.redislabs.com/
2. 创建免费数据库
3. 获取连接字符串
4. 配置到 .env

---

## ☁️ Azure 云服务

### Azure 认证设置

**第 1 步：创建 Azure 应用**

1. 访问 https://portal.azure.com/
2. 进入 "应用注册"
3. 点击 "新建注册"
4. 填写应用名称并注册

**第 2 步：获取凭证**

1. 在应用概览中记录：
   - 应用（客户端）ID
   - 租户 ID

2. 进入 "证书和密码"
3. 新建客户端密码
4. 复制密码值

**第 3 步：配置权限**

1. 进入 "API 权限"
2. 添加权限：
   - Azure Service Management
   - 权限：user_impersonation

**第 4 步：填写 .env**

```ini
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

**代码使用**

```python
from src.core.database_cloud_integration import DatabaseManager

manager = DatabaseManager()
manager.setup_azure(
    subscription_id="your-subscription-id",
    resource_group="your-resource-group",
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id"
)

# 列出资源
resources = manager.azure.list_resources()
for resource in resources:
    print(f"{resource['name']} ({resource['type']})")
```

### Azure SQL Database

**创建 SQL 数据库**

1. Azure Portal → "SQL 数据库"
2. 创建新数据库
3. 配置服务器和认证
4. 等待部署完成

**连接字符串**
```
Server=tcp:your-server.database.windows.net,1433;
Initial Catalog=comic_ai_db;
Persist Security Info=False;
User ID=sqladmin;
Password=your-password;
MultipleActiveResultSets=False;
Encrypt=True;
TrustServerCertificate=False;
Connection Timeout=30;
```

**在代码中使用**
```python
# 使用 Azure SQL 作为数据库
manager.setup_database(
    host="your-server.database.windows.net",
    port=1433,
    user="sqladmin",
    password="your-password",
    database="comic_ai_db"
)
```

### Azure Cache for Redis

**创建 Redis 缓存**

1. Azure Portal → "Azure Cache for Redis"
2. 创建新资源
3. 选择定价层
4. 配置防火墙规则

**获取连接字符串**

1. 在资源页面选择 "访问密钥"
2. 复制主连接字符串或密钥

**在代码中使用**
```python
manager.setup_cache(
    host="your-redis.redis.cache.windows.net",
    port=6380,
    password="your-password"
)
```

---

## 🔗 完整集成示例

### 完整的多服务配置

```python
from src.core.database_cloud_integration import DatabaseManager

# 创建管理器
manager = DatabaseManager(db_type="mysql")

# 配置所有服务
success_db = manager.setup_database(
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="comic_ai"
)

success_cache = manager.setup_cache(
    host="localhost",
    port=6379,
    db=0
)

# 检查状态
status = manager.get_status()
print(status)

# 使用数据库
manager.db.execute("""
    INSERT INTO users (name, email)
    VALUES (%s, %s)
""", ("Alice", "alice@example.com"))

users = manager.db.fetch_all("SELECT * FROM users")
print(users)

# 使用缓存
manager.cache.set("user:1", {"id": 1, "name": "Alice"})
user = manager.cache.get("user:1")
print(user)
```

### 在交易系统中使用

```python
from src.core.database_cloud_integration import DatabaseManager

class TradingSystem:
    def __init__(self):
        self.manager = DatabaseManager(db_type="mysql")
        self.manager.setup_database(
            host="your-db-server",
            user="trader",
            password="password",
            database="trading_db"
        )
        self.manager.setup_cache()
    
    def get_portfolio(self, user_id):
        # 先查缓存
        cache_key = f"portfolio:{user_id}"
        portfolio = self.manager.cache.get(cache_key)
        
        if portfolio:
            return portfolio
        
        # 如果缓存不存在，从数据库查询
        portfolio = self.manager.db.fetch_all(
            "SELECT * FROM portfolio WHERE user_id = %s",
            (user_id,)
        )
        
        # 存入缓存，30 分钟有效期
        self.manager.cache.set(cache_key, portfolio, ttl=1800)
        
        return portfolio
```

---

## 🆘 故障排除

### 问题 1: SQLite 数据库文件权限问题

```bash
# 检查权限
ls -la data/comic_ai.db

# 修改权限
chmod 644 data/comic_ai.db
chmod 755 data/
```

### 问题 2: MySQL 连接失败

```bash
# 检查 MySQL 是否运行
sudo systemctl status mysql

# 或启动 MySQL
sudo systemctl start mysql

# 测试连接
mysql -u root -p -h localhost
```

### 问题 3: Redis 连接超时

```bash
# 检查 Redis 是否运行
redis-cli ping

# 或启动 Redis
redis-server

# 检查端口
netstat -tuln | grep 6379
```

### 问题 4: Azure 认证失败

```bash
# 检查环境变量
echo $AZURE_SUBSCRIPTION_ID
echo $AZURE_CLIENT_ID

# 验证凭证
az login --service-principal \
  -u $AZURE_CLIENT_ID \
  -p $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

---

## 📊 配置矩阵

| 组件 | 本地开发 | 远程生产 | Azure | GCP |
|------|---------|---------|-------|-----|
| 数据库 | SQLite | MySQL | SQL DB | Cloud SQL |
| 缓存 | Redis | Redis Cloud | Redis Cache | Memorystore |
| 认证 | 无 | 用户名/密码 | 应用认证 | 服务账户 |
| 备份 | 本地文件 | 托管备份 | Azure Backup | Cloud Backup |

## 实践代码示例

### 连接管理

```python
import mysql.connector
import redis
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """数据库连接管理"""
    
    def __init__(self):
        self.mysql_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME')
        }
        self.connection = None
    
    def connect(self):
        """建立连接"""
        try:
            self.connection = mysql.connector.connect(**self.mysql_config)
            print("✓ 数据库连接成功")
            return self.connection
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return None
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
            print("✓ 连接已关闭")

class CacheManager:
    """Redis 缓存管理"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
    
    def set_cache(self, key, value, ttl=3600):
        """设置缓存"""
        self.redis_client.setex(key, ttl, value)
        print(f"✓ 缓存已设置: {key}")
    
    def get_cache(self, key):
        """获取缓存"""
        value = self.redis_client.get(key)
        if value:
            print(f"✓ 缓存命中: {key}")
        else:
            print(f"✗ 缓存未命中: {key}")
        return value
```

### 性能测试

```python
def benchmark_database_performance():
    """数据库性能基准测试"""
    
    db = DatabaseManager()
    db.connect()
    
    import time
    
    print("数据库性能测试")
    print("="*60)
    
    # 1. 插入性能
    start = time.time()
    for i in range(1000):
        db.execute_query(
            "INSERT INTO test_table (value) VALUES (%s)",
            (f"value_{i}",)
        )
    insert_time = time.time() - start
    print(f"插入 1000 行: {insert_time:.2f}秒")
    
    # 2. 查询性能
    start = time.time()
    result = db.execute_query("SELECT * FROM test_table LIMIT 1000")
    query_time = time.time() - start
    print(f"查询 1000 行: {query_time*1000:.2f}毫秒")
    
    # 3. 缓存性能
    cache = CacheManager()
    start = time.time()
    for i in range(1000):
        cache.set_cache(f"key_{i}", f"value_{i}")
    cache_time = time.time() - start
    print(f"缓存写入 1000 条: {cache_time*1000:.2f}毫秒")
    
    db.disconnect()
```

### 故障恢复

```python
def test_failover():
    """测试故障转移"""
    
    db = DatabaseManager()
    
    print("故障转移测试")
    print("="*60)
    
    # 1. 主数据库故障
    try:
        db.connect()
        print("✓ 主数据库已连接")
    except:
        print("✗ 主数据库连接失败，尝试备用...")
        
        # 切换到备用数据库
        db.mysql_config['host'] = os.getenv('DB_BACKUP_HOST')
        if db.connect():
            print("✓ 已切换到备用数据库")
    
    # 2. 缓存故障
    cache = CacheManager()
    try:
        cache.get_cache('test')
        print("✓ 缓存服务可用")
    except:
        print("✗ 缓存服务不可用，使用直接数据库查询")
```

## 故障排除指南

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| MySQL 连接失败 | 主机/密码错误 | 检查 .env 文件和防火墙 |
| Redis 超时 | 网络问题 | 检查 Redis 服务状态 |
| 认证失败 | 凭证无效 | 重新生成密钥和密码 |
| 性能下降 | 缓存未使用 | 增加 Redis TTL 时间 |

---

## 🔐 安全建议

✅ **必做事项**
- 使用 `.env` 存储敏感信息
- 定期更新密码
- 启用 SSL/TLS 加密
- 设置防火墙规则

❌ **禁止事项**
- 硬编码密码
- 使用弱密码
- 允许任何 IP 访问
- 在日志中打印凭证

---

## 📚 相关资源

- **MySQL**: https://dev.mysql.com/
- **Redis**: https://redis.io/
- **Azure**: https://azure.microsoft.com/
- **PostgreSQL**: https://www.postgresql.org/

---

**最后更新**: 2026-03-01  
**版本**: 1.1 (含实践代码和故障排除)
**增强内容**: +连接管理代码、+性能测试、+故障恢复、+故障排除表

