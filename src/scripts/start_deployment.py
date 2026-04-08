#!/usr/bin/env python3
"""
部署腳本 - CI/CD 自動部署
支援多環境部署和容器化
"""

import os
import sys
import subprocess
import json
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

class DeploymentManager:
    """部署管理器"""
    
    def __init__(self):
        self.config = self._load_deployment_config()
        self.environment = os.getenv('DEPLOYMENT_ENV', 'development')
        self.api_key = os.getenv('API_KEY')
        self.deploy_token = os.getenv('DEPLOY_TOKEN')
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
        
    def _load_deployment_config(self) -> Dict[str, Any]:
        """載入部署配置"""
        try:
            with open('config/deployment.yaml', 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認部署配置"""
        return {
            'environments': {
                'development': {
                    'host': 'localhost',
                    'port': 8080,
                    'ssl': False,
                    'debug': True
                },
                'staging': {
                    'host': 'staging.comic-ai.com',
                    'port': 443,
                    'ssl': True,
                    'debug': False
                },
                'production': {
                    'host': 'comic-ai.com',
                    'port': 443,
                    'ssl': True,
                    'debug': False
                }
            },
            'deployment_strategy': 'blue_green',
            'health_check_endpoint': '/api/health',
            'rollback_timeout': 300
        }
        
    def pre_deployment_checks(self) -> bool:
        """部署前檢查"""
        self.logger.info("Running pre-deployment checks...")
        
        checks = [
            self._check_dependencies(),
            self._check_environment_config(),
            self._check_service_health(),
            self._check_permissions(),
            self._check_disk_space()
        ]
        
        if all(checks):
            self.logger.info("✅ All pre-deployment checks passed")
            return True
        else:
            self.logger.error("❌ Pre-deployment checks failed")
            return False
            
    def _check_dependencies(self) -> bool:
        """檢查依賴"""
        try:
            required_packages = ['docker', 'docker-compose', 'python3']
            for package in required_packages:
                subprocess.run(['which', package], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            self.logger.error(f"Missing dependency: {package}")
            return False
            
    def _check_environment_config(self) -> bool:
        """檢查環境配置"""
        env_config = self.config['environments'].get(self.environment)
        if not env_config:
            self.logger.error(f"Unknown environment: {self.environment}")
            return False
        return True
        
    def _check_service_health(self) -> bool:
        """檢查服務健康狀態"""
        try:
            # 檢查現有服務
            result = subprocess.run(
                ['curl', '-f', 'http://localhost:8080/api/status'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            # 服務未運行是正常的（首次部署）
            return True
            
    def _check_permissions(self) -> bool:
        """檢查權限"""
        required_permissions = ['write', 'execute']
        for perm in required_permissions:
            if not os.access('.', getattr(os, f'W_OK' if perm == 'write' else 'X_OK')):
                self.logger.error(f"Missing permission: {perm}")
                return False
        return True
        
    def _check_disk_space(self) -> bool:
        """檢查磁盤空間"""
        try:
            result = subprocess.run(['df', '.'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    usage_line = lines[1].split()
                    if len(usage_line) > 4:
                        usage_percent = int(usage_line[4].rstrip('%'))
                        return usage_percent < 80
            return False
        except Exception:
            return False
            
    def deploy(self) -> bool:
        """執行部署"""
        try:
            self.logger.info(f"Starting deployment to {self.environment} environment")
            
            # 1. 部署前檢查
            if not self.pre_deployment_checks():
                return False
                
            # 2. 備份現有部署
            if not self._create_backup():
                self.logger.error("Backup failed, aborting deployment")
                return False
                
            # 3. 構建應用
            if not self._build_application():
                self.logger.error("Build failed, aborting deployment")
                return False
                
            # 4. 部署應用
            if not self._deploy_application():
                self.logger.error("Deployment failed")
                return False
                
            # 5. 健康檢查
            if not self._post_deployment_health_check():
                self.logger.error("Post-deployment health check failed")
                self._rollback()
                return False
                
            # 6. 清理
            self._cleanup()
            
            self.logger.info("✅ Deployment completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            self._rollback()
            return False
            
    def _create_backup(self) -> bool:
        """創建備份"""
        self.logger.info("Creating backup...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f"backups/backup_{timestamp}"
            
            subprocess.run(['mkdir', '-p', 'backups'], check=True)
            subprocess.run(['cp', '-r', '.', backup_dir], check=True)
            
            self.logger.info(f"Backup created: {backup_dir}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Backup failed: {e}")
            return False
            
    def _build_application(self) -> bool:
        """構建應用"""
        self.logger.info("Building application...")
        
        try:
            # 構建Docker鏡像
            subprocess.run([
                'docker', 'build', 
                '-t', 'comic-ai:latest',
                '.'
            ], check=True)
            
            self.logger.info("Docker image built successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Build failed: {e}")
            return False
            
    def _deploy_application(self) -> bool:
        """部署應用"""
        self.logger.info("Deploying application...")
        
        try:
            # 根據環境配置調整docker-compose
            self._update_docker_compose()
            
            # 啟動服務
            subprocess.run([
                'docker-compose', 'up', '-d'
            ], check=True)
            
            # 等待服務啟動
            import time
            time.sleep(30)
            
            self.logger.info("Application deployed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
            
    def _update_docker_compose(self) -> None:
        """更新docker-compose配置"""
        env_config = self.config['environments'][self.environment]
        
        # 讀取現有配置
        with open('docker-compose.yml', 'r') as f:
            compose_config = yaml.safe_load(f)
            
        # 更新環境變量
        if 'services' in compose_config:
            for service in compose_config['services'].values():
                if 'environment' not in service:
                    service['environment'] = []
                    
                service['environment'].extend([
                    f'ENVIRONMENT={self.environment}',
                    f'DEBUG={str(env_config.get("debug", False)).lower()}',
                    f'SSL={str(env_config.get("ssl", False)).lower()}'
                ])
                
        # 寫回文件
        with open('docker-compose.yml', 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False)
            
    def _post_deployment_health_check(self) -> bool:
        """部署後健康檢查"""
        self.logger.info("Running post-deployment health checks...")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                result = subprocess.run([
                    'curl', '-f', 
                    'http://localhost:8080/api/status'
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    if response.get('status') == 'running':
                        self.logger.info("Health check passed")
                        return True
                        
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError):
                pass
                
            self.logger.info(f"Health check attempt {attempt + 1}/{max_attempts}")
            import time
            time.sleep(10)
            
        return False
        
    def _rollback(self) -> None:
        """回滾部署"""
        self.logger.info("Initiating rollback...")
        
        try:
            # 停止現有服務
            subprocess.run(['docker-compose', 'down'], check=True)
            
            # 恢復最新備份
            backups = [d for d in os.listdir('backups') if d.startswith('backup_')]
            if backups:
                latest_backup = sorted(backups)[-1]
                backup_path = f"backups/{latest_backup}"
                
                subprocess.run(['rm', '-rf', '.'], check=True)
                subprocess.run(['cp', '-r', f'{backup_path}/.', '.'], check=True)
                
                self.logger.info(f"Rollback completed using {latest_backup}")
            else:
                self.logger.error("No backups available for rollback")
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Rollback failed: {e}")
            
    def _cleanup(self) -> None:
        """清理部署文件"""
        self.logger.info("Cleaning up...")
        
        try:
            # 清理舊的Docker鏡像
            subprocess.run(['docker', 'image', 'prune', '-f'], check=True)
            
            # 保留最近5個備份
            backups = [d for d in os.listdir('backups') if d.startswith('backup_')]
            if len(backups) > 5:
                backups.sort()
                old_backups = backups[:-5]
                for backup in old_backups:
                    subprocess.run(['rm', '-rf', f'backups/{backup}'], check=True)
                    
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Cleanup warning: {e}")

def main():
    """主部署函數"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'deploy':
            deployer = DeploymentManager()
            success = deployer.deploy()
            sys.exit(0 if success else 1)
        elif command == 'health':
            # 健康檢查命令
            try:
                result = subprocess.run([
                    'curl', '-f', 'http://localhost:8080/api/status'
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    print("✅ Service is healthy")
                    sys.exit(0)
                else:
                    print("❌ Service is unhealthy")
                    sys.exit(1)
            except Exception:
                print("❌ Service check failed")
                sys.exit(1)
        else:
            print("Usage: python deploy.py [deploy|health]")
            sys.exit(1)
    else:
        # 默認執行部署
        deployer = DeploymentManager()
        success = deployer.deploy()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()