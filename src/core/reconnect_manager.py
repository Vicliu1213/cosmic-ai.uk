#!/usr/bin/env python3
"""
自動重連管理器 - 系統閃退後自動重連機制
"""

import asyncio
import logging
import time
from typing import Callable, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ReconnectConfig:
    """重連配置"""
    max_retries: int = 5
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    log_level: str = "INFO"


class ExponentialBackoff:
    """指數退避算法 - 計算重連等待時間"""
    
    def __init__(self, config: ReconnectConfig):
        self.config = config
        self.attempt = 0
        self.start_time = datetime.now()
    
    def get_wait_time(self) -> float:
        """計算下一次重連的等待時間"""
        wait_time = min(
            self.config.initial_delay * (self.config.backoff_factor ** self.attempt),
            self.config.max_delay
        )
        
        # 添加抖動，防止同時重連
        if self.config.jitter:
            import random
            jitter = random.uniform(0, wait_time * 0.1)
            wait_time += jitter
        
        self.attempt += 1
        return wait_time
    
    def reset(self):
        """重置重連計數"""
        self.attempt = 0
        self.start_time = datetime.now()
    
    def get_duration(self) -> timedelta:
        """獲取總重連耗時"""
        return datetime.now() - self.start_time


class AutoReconnect:
    """自動重連管理器"""
    
    def __init__(self, config: Optional[ReconnectConfig] = None):
        self.config = config or ReconnectConfig()
        self.backoff = ExponentialBackoff(self.config)
        self.is_connected = False
        self.reconnect_count = 0
    
    async def execute_with_retry(
        self,
        operation: Callable,
        operation_name: str = "operation"
    ) -> Any:
        """
        執行操作，失敗時自動重連
        
        Args:
            operation: 可調用的操作
            operation_name: 操作名稱 (用於日誌)
        
        Returns:
            操作結果
        """
        while self.reconnect_count < self.config.max_retries:
            try:
                logger.info(f"🔄 執行 {operation_name}...")
                
                # 執行操作
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = operation()
                
                self.is_connected = True
                self.backoff.reset()
                self.reconnect_count = 0
                logger.info(f"✓ {operation_name} 成功")
                return result
            
            except Exception as e:
                self.reconnect_count += 1
                logger.error(f"✗ {operation_name} 失敗 (嘗試 {self.reconnect_count}/{self.config.max_retries})")
                logger.error(f"  錯誤: {str(e)}")
                
                if self.reconnect_count >= self.config.max_retries:
                    logger.error(f"❌ 達到最大重試次數，放棄 {operation_name}")
                    self.is_connected = False
                    raise
                
                # 計算等待時間
                wait_time = self.backoff.get_wait_time()
                logger.info(f"⏳ 將在 {wait_time:.1f} 秒後重試...")
                
                # 等待後重試
                await asyncio.sleep(wait_time)
        
        raise RuntimeError(f"無法執行 {operation_name}，已達到最大重試次數")
    
    async def monitor_connection(
        self,
        health_check: Callable,
        check_interval: float = 5.0
    ) -> None:
        """
        監控連接狀態，自動重連
        
        Args:
            health_check: 健康檢查函數
            check_interval: 檢查間隔（秒）
        """
        logger.info("🔍 開始監控連接...")
        
        while True:
            try:
                # 執行健康檢查
                if asyncio.iscoroutinefunction(health_check):
                    is_healthy = await health_check()
                else:
                    is_healthy = health_check()
                
                if is_healthy:
                    self.is_connected = True
                    logger.debug("✓ 連接正常")
                else:
                    logger.warning("⚠️  連接異常，準備重連...")
                    self.is_connected = False
                    
                    # 嘗試重連
                    wait_time = self.backoff.get_wait_time()
                    logger.info(f"⏳ 將在 {wait_time:.1f} 秒後重連...")
                    await asyncio.sleep(wait_time)
                    self.reconnect_count += 1
                
                # 等待下一次檢查
                await asyncio.sleep(check_interval)
            
            except Exception as e:
                logger.error(f"監控錯誤: {e}")
                await asyncio.sleep(check_interval)
    
    def get_status(self) -> dict:
        """獲取重連狀態"""
        return {
            "is_connected": self.is_connected,
            "reconnect_count": self.reconnect_count,
            "backoff_attempt": self.backoff.attempt,
            "duration": str(self.backoff.get_duration())
        }


class SystemGuard:
    """系統守護者 - 監控系統狀態，自動重啟"""
    
    def __init__(self, system, config: Optional[ReconnectConfig] = None):
        self.system = system
        self.reconnect = AutoReconnect(config)
        self.is_running = False
        self.start_time = datetime.now()
        self.crash_count = 0
        self.max_crashes = 10
    
    async def start_with_protection(self) -> bool:
        """
        帶保護的系統啟動
        
        Returns:
            bool: 是否成功啟動
        """
        return await self.reconnect.execute_with_retry(
            lambda: self.system.start(),
            "系統啟動"
        )
    
    async def monitor_and_restart(self) -> None:
        """
        監控系統，自動重啟
        """
        logger.info("🛡️  系統守護者已激活")
        
        async def system_health_check():
            """系統健康檢查"""
            try:
                # 檢查系統狀態
                status = self.system.get_status()
                is_healthy = status.get("status") == "running"
                
                if not is_healthy:
                    self.crash_count += 1
                    logger.warning(f"⚠️  系統異常 (第 {self.crash_count} 次)")
                    
                    if self.crash_count >= self.max_crashes:
                        logger.error(f"❌ 系統多次異常，放棄自動重啟")
                        return False
                
                return is_healthy
            except Exception as e:
                logger.error(f"健康檢查錯誤: {e}")
                return False
        
        # 開始監控
        await self.reconnect.monitor_connection(
            system_health_check,
            check_interval=3.0
        )
    
    def get_status(self) -> dict:
        """獲取系統守護者狀態"""
        uptime = datetime.now() - self.start_time
        return {
            "is_running": self.is_running,
            "crash_count": self.crash_count,
            "uptime": str(uptime),
            "reconnect_status": self.reconnect.get_status()
        }
