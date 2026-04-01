#!/usr/bin/env python3
"""
混合云管理面板
Hybrid Cloud Management Dashboard

支持:
- 本地服务监控 (SQLite, Redis)
- Azure 云服务监控
- GCP 云服务监控
- AWS 云服务监控 (可选)
- 统一仪表板
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# 数据类
# ============================================================================

@dataclass
class ServiceStatus:
    """服务状态"""
    name: str
    type: str  # local, azure, gcp, aws
    status: str  # connected, disconnected, error
    location: str  # 位置/区域
    last_check: str  # 最后检查时间
    details: Dict[str, Any]  # 详细信息


# ============================================================================
# 混合云管理器
# ============================================================================

class HybridCloudManager:
    """混合云管理器 - 统一管理所有云服务"""
    
    def __init__(self):
        """初始化混合云管理器"""
        self.services: List[ServiceStatus] = []
        self.local_services = {}
        self.azure_services = {}
        self.gcp_services = {}
        self.aws_services = {}
    
    def check_local_services(self) -> Dict[str, Any]:
        """检查本地服务"""
        logger.info("📊 检查本地服务...")
        
        local_status = {
            'database': self._check_local_database(),
            'redis': self._check_redis(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.local_services = local_status
        return local_status
    
    def check_azure_services(self) -> Dict[str, Any]:
        """检查 Azure 服务"""
        logger.info("☁️ 检查 Azure 服务...")
        
        azure_status = {
            'sql_database': self._check_azure_sql(),
            'redis_cache': self._check_azure_redis(),
            'app_service': self._check_azure_app(),
            'storage_account': self._check_azure_storage(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.azure_services = azure_status
        return azure_status
    
    def check_gcp_services(self) -> Dict[str, Any]:
        """检查 GCP 服务"""
        logger.info("☁️ 检查 GCP 服务...")
        
        gcp_status = {
            'cloud_sql': self._check_gcp_cloudsql(),
            'memorystore': self._check_gcp_memorystore(),
            'compute': self._check_gcp_compute(),
            'storage': self._check_gcp_storage(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.gcp_services = gcp_status
        return gcp_status
    
    def check_aws_services(self) -> Dict[str, Any]:
        """检查 AWS 服务"""
        logger.info("☁️ 检查 AWS 服务...")
        
        aws_status = {
            'rds': self._check_aws_rds(),
            'elasticache': self._check_aws_elasticache(),
            'ec2': self._check_aws_ec2(),
            's3': self._check_aws_s3(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.aws_services = aws_status
        return aws_status
    
    # ========================================================================
    # 本地服务检查
    # ========================================================================
    
    def _check_local_database(self) -> Dict[str, Any]:
        """检查本地数据库"""
        db_type = os.getenv('DATABASE_TYPE', 'sqlite')
        db_path = os.getenv('DATABASE_PATH', 'data/comic_ai.db')
        
        if db_type == 'sqlite':
            db_exists = os.path.exists(db_path)
            db_size = os.path.getsize(db_path) if db_exists else 0
            
            return {
                'type': 'SQLite',
                'status': '✅ 正常' if db_exists else '❌ 不存在',
                'path': db_path,
                'size_mb': round(db_size / (1024 * 1024), 2),
                'connected': db_exists
            }
        else:
            return {
                'type': db_type.upper(),
                'status': '📝 需要配置',
                'connected': False
            }
    
    def _check_redis(self) -> Dict[str, Any]:
        """检查 Redis 缓存"""
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        try:
            import redis
            r = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=2)
            r.ping()
            
            info = r.info()
            return {
                'type': 'Redis',
                'status': '✅ 运行中',
                'host': redis_host,
                'port': redis_port,
                'memory_mb': round(info.get('used_memory', 0) / (1024 * 1024), 2),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_days': info.get('uptime_in_days', 0),
                'connected': True
            }
        except Exception as e:
            return {
                'type': 'Redis',
                'status': '❌ 离线',
                'host': redis_host,
                'port': redis_port,
                'error': str(e),
                'connected': False
            }
    
    # ========================================================================
    # Azure 服务检查
    # ========================================================================
    
    def _check_azure_sql(self) -> Dict[str, Any]:
        """检查 Azure SQL Database"""
        return {
            'service': 'Azure SQL Database',
            'status': '📝 未配置',
            'region': os.getenv('AZURE_REGION', '未知'),
            'configured': bool(os.getenv('AZURE_SQL_SERVER'))
        }
    
    def _check_azure_redis(self) -> Dict[str, Any]:
        """检查 Azure Cache for Redis"""
        return {
            'service': 'Azure Cache for Redis',
            'status': '📝 未配置',
            'region': os.getenv('AZURE_REGION', '未知'),
            'configured': bool(os.getenv('AZURE_REDIS_HOST'))
        }
    
    def _check_azure_app(self) -> Dict[str, Any]:
        """检查 Azure App Service"""
        return {
            'service': 'Azure App Service',
            'status': '📝 未配置',
            'configured': bool(os.getenv('AZURE_APP_NAME'))
        }
    
    def _check_azure_storage(self) -> Dict[str, Any]:
        """检查 Azure Storage Account"""
        return {
            'service': 'Azure Storage Account',
            'status': '📝 未配置',
            'configured': bool(os.getenv('AZURE_STORAGE_ACCOUNT'))
        }
    
    # ========================================================================
    # GCP 服务检查
    # ========================================================================
    
    def _check_gcp_cloudsql(self) -> Dict[str, Any]:
        """检查 GCP Cloud SQL"""
        return {
            'service': 'Google Cloud SQL',
            'status': '📝 未配置',
            'region': os.getenv('GCP_REGION', '未知'),
            'configured': bool(os.getenv('GCP_CLOUDSQL_CONNECTION_NAME'))
        }
    
    def _check_gcp_memorystore(self) -> Dict[str, Any]:
        """检查 GCP Memorystore for Redis"""
        return {
            'service': 'Google Memorystore',
            'status': '📝 未配置',
            'region': os.getenv('GCP_REGION', '未知'),
            'configured': bool(os.getenv('GCP_REDIS_HOST'))
        }
    
    def _check_gcp_compute(self) -> Dict[str, Any]:
        """检查 GCP Compute Engine"""
        return {
            'service': 'Google Compute Engine',
            'status': '📝 未配置',
            'configured': bool(os.getenv('GCP_PROJECT_ID'))
        }
    
    def _check_gcp_storage(self) -> Dict[str, Any]:
        """检查 GCP Cloud Storage"""
        return {
            'service': 'Google Cloud Storage',
            'status': '📝 未配置',
            'configured': bool(os.getenv('GCP_PROJECT_ID'))
        }
    
    # ========================================================================
    # AWS 服务检查
    # ========================================================================
    
    def _check_aws_rds(self) -> Dict[str, Any]:
        """检查 AWS RDS"""
        return {
            'service': 'AWS RDS',
            'status': '📝 未配置',
            'configured': bool(os.getenv('AWS_ACCESS_KEY_ID'))
        }
    
    def _check_aws_elasticache(self) -> Dict[str, Any]:
        """检查 AWS ElastiCache"""
        return {
            'service': 'AWS ElastiCache',
            'status': '📝 未配置',
            'configured': bool(os.getenv('AWS_ACCESS_KEY_ID'))
        }
    
    def _check_aws_ec2(self) -> Dict[str, Any]:
        """检查 AWS EC2"""
        return {
            'service': 'AWS EC2',
            'status': '📝 未配置',
            'configured': bool(os.getenv('AWS_ACCESS_KEY_ID'))
        }
    
    def _check_aws_s3(self) -> Dict[str, Any]:
        """检查 AWS S3"""
        return {
            'service': 'AWS S3',
            'status': '📝 未配置',
            'configured': bool(os.getenv('AWS_ACCESS_KEY_ID'))
        }
    
    def get_full_status(self) -> Dict[str, Any]:
        """获取完整状态"""
        return {
            'local': self.local_services,
            'azure': self.azure_services,
            'gcp': self.gcp_services,
            'aws': self.aws_services,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        summary = {
            'local': {
                'total': 2,
                'connected': sum(1 for s in self.local_services.values() 
                               if isinstance(s, dict) and s.get('connected'))
            },
            'azure': {
                'total': 4,
                'configured': sum(1 for s in self.azure_services.values() 
                                if isinstance(s, dict) and s.get('configured'))
            },
            'gcp': {
                'total': 4,
                'configured': sum(1 for s in self.gcp_services.values() 
                                if isinstance(s, dict) and s.get('configured'))
            },
            'aws': {
                'total': 4,
                'configured': sum(1 for s in self.aws_services.values() 
                                if isinstance(s, dict) and s.get('configured'))
            }
        }
        return summary


# ============================================================================
# 仪表板渲染
# ============================================================================

class HybridCloudDashboard:
    """混合云仪表板"""
    
    def __init__(self, manager: HybridCloudManager):
        """初始化仪表板"""
        self.manager = manager
    
    def render(self):
        """渲染仪表板"""
        print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                  🌐 混合云管理仪表板                                     ║
║             Hybrid Cloud Management Dashboard                           ║
╚══════════════════════════════════════════════════════════════════════════╝
        """)
        
        # 本地服务
        self._render_local_services()
        
        # Azure 服务
        self._render_azure_services()
        
        # GCP 服务
        self._render_gcp_services()
        
        # AWS 服务
        self._render_aws_services()
        
        # 摘要
        self._render_summary()
    
    def _render_local_services(self):
        """渲染本地服务"""
        print("\n" + "=" * 70)
        print("🏠 本地服务")
        print("=" * 70)
        
        for name, service in self.manager.local_services.items():
            if isinstance(service, dict):
                status = service.get('status', '未知')
                print(f"\n{name.upper()}:")
                for key, value in service.items():
                    if key != 'status':
                        print(f"  {key:20} {value}")
                print(f"  状态: {status}")
    
    def _render_azure_services(self):
        """渲染 Azure 服务"""
        print("\n" + "=" * 70)
        print("☁️ Azure 云服务")
        print("=" * 70)
        
        for name, service in self.manager.azure_services.items():
            if isinstance(service, dict):
                status = service.get('status', '未知')
                print(f"\n{name.upper()}:")
                print(f"  服务: {service.get('service', 'N/A')}")
                print(f"  状态: {status}")
                if service.get('region'):
                    print(f"  地区: {service.get('region')}")
    
    def _render_gcp_services(self):
        """渲染 GCP 服务"""
        print("\n" + "=" * 70)
        print("☁️ GCP 云服务")
        print("=" * 70)
        
        for name, service in self.manager.gcp_services.items():
            if isinstance(service, dict):
                status = service.get('status', '未知')
                print(f"\n{name.upper()}:")
                print(f"  服务: {service.get('service', 'N/A')}")
                print(f"  状态: {status}")
                if service.get('region'):
                    print(f"  地区: {service.get('region')}")
    
    def _render_aws_services(self):
        """渲染 AWS 服务"""
        print("\n" + "=" * 70)
        print("☁️ AWS 云服务")
        print("=" * 70)
        
        for name, service in self.manager.aws_services.items():
            if isinstance(service, dict):
                status = service.get('status', '未知')
                print(f"\n{name.upper()}:")
                print(f"  服务: {service.get('service', 'N/A')}")
                print(f"  状态: {status}")
    
    def _render_summary(self):
        """渲染摘要"""
        print("\n" + "=" * 70)
        print("📊 服务摘要")
        print("=" * 70)
        
        summary = self.manager.get_summary()
        
        print(f"\n🏠 本地服务:")
        print(f"   总数: {summary['local']['total']}")
        print(f"   已连接: {summary['local']['connected']}")
        
        print(f"\n☁️ Azure:")
        print(f"   总数: {summary['azure']['total']}")
        print(f"   已配置: {summary['azure']['configured']}")
        
        print(f"\n☁️ GCP:")
        print(f"   总数: {summary['gcp']['total']}")
        print(f"   已配置: {summary['gcp']['configured']}")
        
        print(f"\n☁️ AWS:")
        print(f"   总数: {summary['aws']['total']}")
        print(f"   已配置: {summary['aws']['configured']}")


def main():
    """主函数"""
    import sys
    sys.path.insert(0, '/root/comic_ai')
    
    # 创建管理器
    manager = HybridCloudManager()
    
    # 检查所有服务
    print("🔍 正在检查所有服务...\n")
    
    manager.check_local_services()
    manager.check_azure_services()
    manager.check_gcp_services()
    manager.check_aws_services()
    
    # 渲染仪表板
    dashboard = HybridCloudDashboard(manager)
    dashboard.render()
    
    # 输出 JSON 格式
    print("\n" + "=" * 70)
    print("📋 完整状态 (JSON)")
    print("=" * 70)
    print(json.dumps(manager.get_full_status(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
