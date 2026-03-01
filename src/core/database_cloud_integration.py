#!/usr/bin/env python3
"""
数据库和云服务集成模块
Database and Cloud Services Integration Module

支持:
- SQLite (本地)
- MySQL/PostgreSQL (远程)
- Redis (缓存)
- Azure/GCP (云服务)
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from abc import ABC, abstractmethod

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 数据库基类
# ============================================================================

class DatabaseConnector(ABC):
    """数据库连接器基类"""
    
    @abstractmethod
    def connect(self) -> bool:
        """连接到数据库"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """断开数据库连接"""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: tuple = None) -> Any:
        """执行查询"""
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """获取所有结果"""
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """获取单条结果"""
        pass

# ============================================================================
# SQLite 实现
# ============================================================================

class SQLiteConnector(DatabaseConnector):
    """SQLite 数据库连接器"""
    
    def __init__(self, db_path: str = "data/comic_ai.db") -> Any:
        """
        初始化 SQLite 连接器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """连接到 SQLite 数据库"""
        try:
            import sqlite3
            
            # 创建目录
            os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            
            logger.info(f"✅ SQLite 连接成功: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ SQLite 连接失败: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开 SQLite 连接"""
        try:
            if self.connection:
                self.connection.close()
            logger.info("✅ SQLite 连接已关闭")
            return True
        except Exception as e:
            logger.error(f"❌ 断开 SQLite 连接失败: {e}")
            return False
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """执行 SQL 查询"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"❌ SQL 执行失败: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """获取所有查询结果"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ 查询失败: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """获取单条查询结果"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ 查询失败: {e}")
            return None

# ============================================================================
# MySQL 实现
# ============================================================================

class MySQLConnector(DatabaseConnector):
    """MySQL 数据库连接器"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 3306,
                 user: str = "root",
                 password: str = "",
                 database: str = "comic_ai") -> Any:
        """
        初始化 MySQL 连接器
        
        Args:
            host: 数据库主机
            port: 数据库端口
            user: 用户名
            password: 密码
            database: 数据库名
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """连接到 MySQL 数据库"""
        try:
            import mysql.connector
            
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            
            logger.info(f"✅ MySQL 连接成功: {self.user}@{self.host}")
            return True
        except Exception as e:
            logger.error(f"❌ MySQL 连接失败: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开 MySQL 连接"""
        try:
            if self.connection:
                self.connection.close()
            logger.info("✅ MySQL 连接已关闭")
            return True
        except Exception as e:
            logger.error(f"❌ 断开 MySQL 连接失败: {e}")
            return False
    
    def execute(self, query: str, params: tuple = None) -> Any:
        """执行 SQL 查询"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"❌ SQL 执行失败: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """获取所有查询结果"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ 查询失败: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """获取单条查询结果"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"❌ 查询失败: {e}")
            return None

# ============================================================================
# Redis 缓存实现
# ============================================================================

class RedisCache:
    """Redis 缓存管理器"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None) -> Any:
        """
        初始化 Redis 缓存
        
        Args:
            host: Redis 主机
            port: Redis 端口
            db: 数据库号
            password: 密码（可选）
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = None
    
    def connect(self) -> bool:
        """连接到 Redis"""
        try:
            import redis
            
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            
            # 测试连接
            self.redis_client.ping()
            logger.info(f"✅ Redis 连接成功: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"❌ Redis 连接失败: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开 Redis 连接"""
        try:
            if self.redis_client:
                self.redis_client.close()
            logger.info("✅ Redis 连接已关闭")
            return True
        except Exception as e:
            logger.error(f"❌ 断开 Redis 连接失败: {e}")
            return False
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        try:
            if isinstance(value, dict):
                value = json.dumps(value)
            
            self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"❌ 设置缓存失败: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"❌ 获取缓存失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ 删除缓存失败: {e}")
            return False
    
    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            self.redis_client.flushdb()
            logger.info("✅ 缓存已清空")
            return True
        except Exception as e:
            logger.error(f"❌ 清空缓存失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取 Redis 统计信息"""
        try:
            info = self.redis_client.info()
            return {
                'memory_usage': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'uptime_days': info.get('uptime_in_days', 0)
            }
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {}

# ============================================================================
# 云服务集成
# ============================================================================

class AzureCloudConnector:
    """Azure 云服务连接器"""
    
    def __init__(self,
                 subscription_id: str,
                 resource_group: str,
                 client_id: str,
                 client_secret: str,
                 tenant_id: str) -> Any:
        """
        初始化 Azure 连接器
        
        Args:
            subscription_id: Azure 订阅 ID
            resource_group: 资源组名称
            client_id: 应用 ID
            client_secret: 应用密钥
            tenant_id: 租户 ID
        """
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.credentials = None
    
    def authenticate(self) -> bool:
        """认证 Azure"""
        try:
            from azure.identity import ClientSecretCredential
            
            self.credentials = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            logger.info("✅ Azure 认证成功")
            return True
        except Exception as e:
            logger.error(f"❌ Azure 认证失败: {e}")
            return False
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """列出资源组中的所有资源"""
        try:
            from azure.mgmt.resource import ResourceManagementClient
            
            client = ResourceManagementClient(
                self.credentials,
                self.subscription_id
            )
            
            resources = client.resources.list_by_resource_group(
                self.resource_group
            )
            
            return [
                {
                    'name': r.name,
                    'type': r.type,
                    'location': r.location
                }
                for r in resources
            ]
        except Exception as e:
            logger.error(f"❌ 列出资源失败: {e}")
            return []
    
    def get_connection_string(self, 
                             resource_name: str,
                             resource_type: str) -> Optional[str]:
        """获取资源连接字符串"""
        try:
            # 这是一个示例方法，实际实现需要根据资源类型调整
            logger.info(f"获取 {resource_type} 连接字符串: {resource_name}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取连接字符串失败: {e}")
            return None

# ============================================================================
# 统一管理器
# ============================================================================

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_type: str = "sqlite") -> Any:
        """
        初始化数据库管理器
        
        Args:
            db_type: 数据库类型 (sqlite, mysql, postgresql)
        """
        self.db_type = db_type
        self.db = None
        self.cache = None
        self.azure = None
    
    def setup_database(self, **kwargs) -> bool:
        """设置数据库连接"""
        try:
            if self.db_type == "sqlite":
                db_path = kwargs.get("db_path", "data/comic_ai.db")
                self.db = SQLiteConnector(db_path)
            
            elif self.db_type == "mysql":
                self.db = MySQLConnector(
                    host=kwargs.get("host", "localhost"),
                    port=kwargs.get("port", 3306),
                    user=kwargs.get("user", "root"),
                    password=kwargs.get("password", ""),
                    database=kwargs.get("database", "comic_ai")
                )
            
            # 连接数据库
            if self.db.connect():
                logger.info(f"✅ {self.db_type.upper()} 数据库已配置")
                return True
            else:
                logger.error(f"❌ {self.db_type.upper()} 数据库配置失败")
                return False
        
        except Exception as e:
            logger.error(f"❌ 设置数据库失败: {e}")
            return False
    
    def setup_cache(self, **kwargs) -> bool:
        """设置 Redis 缓存"""
        try:
            self.cache = RedisCache(
                host=kwargs.get("host", "localhost"),
                port=kwargs.get("port", 6379),
                db=kwargs.get("db", 0),
                password=kwargs.get("password")
            )
            
            if self.cache.connect():
                logger.info("✅ Redis 缓存已配置")
                return True
            else:
                logger.error("❌ Redis 缓存配置失败")
                return False
        
        except Exception as e:
            logger.error(f"❌ 设置缓存失败: {e}")
            return False
    
    def setup_azure(self, **kwargs) -> bool:
        """设置 Azure 云服务"""
        try:
            self.azure = AzureCloudConnector(
                subscription_id=kwargs.get("subscription_id"),
                resource_group=kwargs.get("resource_group"),
                client_id=kwargs.get("client_id"),
                client_secret=kwargs.get("client_secret"),
                tenant_id=kwargs.get("tenant_id")
            )
            
            if self.azure.authenticate():
                logger.info("✅ Azure 云服务已配置")
                return True
            else:
                logger.error("❌ Azure 云服务配置失败")
                return False
        
        except Exception as e:
            logger.error(f"❌ 设置 Azure 失败: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有服务状态"""
        status = {
            'database': {
                'type': self.db_type,
                'connected': bool(self.db and self.db.connection)
            },
            'cache': {
                'connected': bool(self.cache and self.cache.redis_client)
            },
            'azure': {
                'authenticated': bool(self.azure and self.azure.credentials)
            }
        }
        
        if self.cache and self.cache.redis_client:
            status['cache']['stats'] = self.cache.get_stats()
        
        return status

def main() -> Any:
    """演示用法"""
    print("🚀 数据库和云服务集成演示\n")
    
    # 创建管理器
    manager = DatabaseManager(db_type="sqlite")
    
    # 设置 SQLite 数据库
    print("=" * 70)
    print("1️⃣  设置 SQLite 数据库")
    print("=" * 70)
    manager.setup_database(db_path="data/comic_ai.db")
    
    # 设置 Redis 缓存
    print("\n" + "=" * 70)
    print("2️⃣  设置 Redis 缓存")
    print("=" * 70)
    manager.setup_cache(host="localhost", port=6379)
    
    # 获取状态
    print("\n" + "=" * 70)
    print("📊 服务状态")
    print("=" * 70)
    status = manager.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    print("\n✅ 集成完成！")

if __name__ == "__main__":
    main()
