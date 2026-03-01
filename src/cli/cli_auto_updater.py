#!/usr/bin/env python3
"""
CLI 自動更新管理器
Auto-Update Manager for CLI
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import logging
import threading

logger = logging.getLogger(__name__)

class CLIAutoUpdater:
    """CLI 自動更新管理器"""
    
    def __init__(self, project_root: Path = Path("/workspaces/cosmic-ai.uk"), 
                 update_interval_hours: int = 1):
        """初始化自動更新管理器
        
        Args:
            project_root: 項目根目錄
            update_interval_hours: 更新檢查間隔（小時）
        """
        self.project_root = Path(project_root)
        self.update_interval = timedelta(hours=update_interval_hours)
        self.config_dir = self.project_root / ".cli_config"
        self.config_file = self.config_dir / "update_config.json"
        self.version_file = self.project_root / "src" / "cli" / "version.json"
        
        # 確保配置目錄存在
        self.config_dir.mkdir(exist_ok=True)
        self._load_config()
    
    def _load_config(self) -> None:
        """加載配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
            self._save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "auto_update_enabled": True,
            "check_interval_hours": 1,
            "last_check": None,
            "last_update": None,
            "auto_restart": True,
            "notifications": True,
            "current_version": "1.0.0"
        }
    
    def _save_config(self) -> None:
        """保存配置"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def should_check_updates(self) -> bool:
        """判斷是否應檢查更新"""
        if not self.config.get("auto_update_enabled", True):
            return False
        
        last_check = self.config.get("last_check")
        if last_check is None:
            return True
        
        try:
            last_check_time = datetime.fromisoformat(last_check)
            return datetime.now() - last_check_time >= self.update_interval
        except Exception:
            return True
    
    def check_updates(self) -> Dict[str, Any]:
        """檢查更新
        
        Returns:
            更新檢查結果
        """
        result = {
            "status": "checking",
            "timestamp": datetime.now().isoformat(),
            "updates_available": False,
            "details": {}
        }
        
        try:
            # 檢查 Git 更新
            os.chdir(self.project_root)
            
            # 獲取遠程更新
            subprocess.run(["git", "fetch", "--quiet"], timeout=30, check=False)
            
            # 比較本地和遠程
            result_compare = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "HEAD...@{u}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_compare.returncode == 0:
                behind, ahead = result_compare.stdout.strip().split()
                behind = int(behind)
                ahead = int(ahead)
                
                if ahead > 0:
                    result["updates_available"] = True
                    result["details"]["commits_behind"] = ahead
                    
                    # 獲取更新日誌
                    log_result = subprocess.run(
                        ["git", "log", "--oneline", f"HEAD..@{{u}}", "-n", "5"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if log_result.returncode == 0:
                        result["details"]["recent_updates"] = log_result.stdout.strip().split('\n')
            
            result["status"] = "checked"
            self.config["last_check"] = datetime.now().isoformat()
            self._save_config()
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"Update check failed: {e}")
        
        return result
    
    def apply_updates(self) -> Dict[str, Any]:
        """應用更新
        
        Returns:
            更新結果
        """
        result = {
            "status": "updating",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "details": {}
        }
        
        try:
            os.chdir(self.project_root)
            
            # 執行 git pull
            pull_result = subprocess.run(
                ["git", "pull", "--rebase"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if pull_result.returncode == 0:
                result["success"] = True
                result["status"] = "updated"
                result["details"]["output"] = pull_result.stdout
                
                # 更新配置中的最後更新時間
                self.config["last_update"] = datetime.now().isoformat()
                self._save_config()
                
                logger.info("✅ CLI updated successfully")
            else:
                result["status"] = "failed"
                result["details"]["error"] = pull_result.stderr
                logger.error(f"Update failed: {pull_result.stderr}")
        
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"Apply updates failed: {e}")
        
        return result
    
    def start_background_check(self, callback: Optional[Callable] = None) -> threading.Thread:
        """啟動後台更新檢查
        
        Args:
            callback: 發現更新時的回調函數
            
        Returns:
            後台線程
        """
        def background_worker():
            while True:
                try:
                    if self.should_check_updates():
                        result = self.check_updates()
                        
                        if result["updates_available"] and self.config.get("notifications", True):
                            msg = f"🔄 CLI 有新版本可用 ({result['details'].get('commits_behind', 0)} 個提交)"
                            logger.info(msg)
                            
                            if callback:
                                callback(result)
                            
                            # 自動應用更新
                            if self.config.get("auto_restart", False):
                                logger.info("🚀 自動應用更新...")
                                self.apply_updates()
                    
                    # 等待到下一次檢查
                    time.sleep(self.update_interval.total_seconds() / 2)
                
                except Exception as e:
                    logger.warning(f"Background update check error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        return thread
    
    def get_status(self) -> Dict[str, Any]:
        """獲取更新狀態
        
        Returns:
            狀態信息
        """
        return {
            "auto_update_enabled": self.config.get("auto_update_enabled", True),
            "last_check": self.config.get("last_check"),
            "last_update": self.config.get("last_update"),
            "current_version": self.config.get("current_version"),
            "check_interval_hours": self.config.get("check_interval_hours", 1)
        }

class CLIUpdateManager:
    """CLI 更新管理器 - 簡化接口"""
    
    _instance = None
    _updater = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._updater is None:
            self._updater = CLIAutoUpdater()
    
    def enable_auto_update(self) -> None:
        """啟用自動更新"""
        self._updater.config["auto_update_enabled"] = True
        self._updater._save_config()
        logger.info("✅ Auto-update enabled")
    
    def disable_auto_update(self) -> None:
        """禁用自動更新"""
        self._updater.config["auto_update_enabled"] = False
        self._updater._save_config()
        logger.info("✅ Auto-update disabled")
    
    def check_now(self) -> Dict[str, Any]:
        """立即檢查更新"""
        return self._updater.check_updates()
    
    def update_now(self) -> Dict[str, Any]:
        """立即更新"""
        return self._updater.apply_updates()
    
    def get_status(self) -> Dict[str, Any]:
        """獲取狀態"""
        return self._updater.get_status()
    
    def start_background(self, callback: Optional[Callable] = None) -> None:
        """啟動後台更新檢查"""
        self._updater.start_background_check(callback)
