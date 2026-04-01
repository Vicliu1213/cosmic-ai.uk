#!/usr/bin/env python3
"""
SQL、Redis 和 Azure 云服务配置和设置指南
Database, Redis, and Azure Cloud Services Setup Guide
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.database_cloud_integration import DatabaseManager


def setup_local_services():
    """设置本地服务（SQLite + Redis）"""
    print("\n" + "=" * 70)
    print("🏠 本地服务设置")
    print("=" * 70)
    
    # 创建管理器
    manager = DatabaseManager(db_type="sqlite")
    
    # 设置 SQLite
    print("\n📝 配置 SQLite 数据库...")
    db_path = os.getenv('DATABASE_PATH', 'data/comic_ai.db')
    if manager.setup_database(db_path=db_path):
        print(f"✅ SQLite 数据库已连接: {db_path}")
    else:
        print("❌ SQLite 连接失败")
    
    # 设置 Redis
    print("\n⚡ 配置 Redis 缓存...")
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_db = int(os.getenv('REDIS_DB', 0))
    redis_password = os.getenv('REDIS_PASSWORD')
    
    if manager.setup_cache(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password
    ):
        print(f"✅ Redis 缓存已连接: {redis_host}:{redis_port}")
    else:
        print("❌ Redis 连接失败（可能是 Redis 未运行）")
    
    # 显示状态
    print("\n📊 服务状态:")
    status = manager.get_status()
    print(f"  数据库: {status['database']['type']} "
          f"({'已连接' if status['database']['connected'] else '未连接'})")
    print(f"  缓存: {'已连接' if status['cache']['connected'] else '未连接'}")
    
    return manager


def setup_remote_mysql():
    """设置远程 MySQL 数据库"""
    print("\n" + "=" * 70)
    print("🌐 远程 MySQL 数据库设置")
    print("=" * 70)
    
    # 从环境变量或配置获取
    mysql_host = os.getenv('MYSQL_HOST', 'your-db-server.com')
    mysql_port = int(os.getenv('MYSQL_PORT', 3306))
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD', '')
    mysql_database = os.getenv('MYSQL_DATABASE', 'comic_ai')
    
    print(f"\n连接信息:")
    print(f"  主机: {mysql_host}:{mysql_port}")
    print(f"  用户: {mysql_user}")
    print(f"  数据库: {mysql_database}")
    
    # 创建管理器
    manager = DatabaseManager(db_type="mysql")
    
    if manager.setup_database(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    ):
        print("\n✅ MySQL 数据库已连接")
        return manager
    else:
        print("\n❌ MySQL 连接失败")
        print("\n💡 确保:")
        print("  1. MySQL 服务器正在运行")
        print("  2. 网络连接可用")
        print("  3. 凭证正确")
        return None


def setup_azure_cloud():
    """设置 Azure 云服务"""
    print("\n" + "=" * 70)
    print("☁️ Azure 云服务设置")
    print("=" * 70)
    
    # 从环境变量获取
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    # 检查必需的环境变量
    if not all([subscription_id, resource_group, client_id, client_secret, tenant_id]):
        print("❌ 缺少必要的 Azure 环境变量")
        print("\n需要设置:")
        print("  - AZURE_SUBSCRIPTION_ID")
        print("  - AZURE_RESOURCE_GROUP")
        print("  - AZURE_CLIENT_ID")
        print("  - AZURE_CLIENT_SECRET")
        print("  - AZURE_TENANT_ID")
        return None
    
    # 创建管理器
    manager = DatabaseManager()
    
    print("\n🔐 认证 Azure...")
    if manager.setup_azure(
        subscription_id=subscription_id,
        resource_group=resource_group,
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id
    ):
        print("✅ Azure 认证成功")
        
        # 列出资源
        print("\n📋 资源列表:")
        resources = manager.azure.list_resources()
        for resource in resources:
            print(f"  - {resource['name']} ({resource['type']})")
        
        return manager
    else:
        print("❌ Azure 认证失败")
        return None


def main():
    """主函数"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║               SQL、Redis 和 Azure 云服务集成设置                        ║
║       SQL, Redis and Azure Cloud Services Integration Setup             ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("""
🎯 可用的配置选项:

1. 本地服务
   - SQLite 数据库
   - Redis 缓存

2. 远程服务
   - MySQL/PostgreSQL 数据库
   - Redis 云服务

3. Azure 云集成
   - Azure SQL Database
   - Azure Cache for Redis
   - Azure 资源管理

4. 混合配置
   - 本地 + 云服务
   - 多数据库支持
    """)
    
    # 设置本地服务
    print("\n" + "=" * 70)
    print("📌 第 1 步: 配置本地服务")
    print("=" * 70)
    
    local_manager = setup_local_services()
    
    # 选项：设置远程 MySQL
    print("\n" + "=" * 70)
    print("📌 第 2 步: 配置远程 MySQL（可选）")
    print("=" * 70)
    
    mysql_manager = setup_remote_mysql()
    
    # 选项：设置 Azure
    print("\n" + "=" * 70)
    print("📌 第 3 步: 配置 Azure 云服务（可选）")
    print("=" * 70)
    
    azure_manager = setup_azure_cloud()
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 配置总结")
    print("=" * 70)
    
    config_summary = {
        "SQLite": "✅" if local_manager and local_manager.db else "❌",
        "Redis": "✅" if local_manager and local_manager.cache else "❌",
        "MySQL": "✅" if mysql_manager else "❌",
        "Azure": "✅" if azure_manager else "❌"
    }
    
    for service, status in config_summary.items():
        print(f"{service:20} {status}")
    
    print("\n✨ 配置完成！")
    print("\n💡 下一步:")
    print("  1. 在 .env 中填入配置信息")
    print("  2. 运行应用进行连接测试")
    print("  3. 在代码中使用 DatabaseManager")


if __name__ == "__main__":
    main()
