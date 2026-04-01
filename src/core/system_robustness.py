#!/usr/bin/env python3
"""
Comic AI 防閃退和斷線重連系統
Crash Prevention & Auto-Reconnection System

功能:
1. 防止程序意外崩潰 (Crash Prevention)
2. 自動斷線重連 (Auto-Reconnection)
3. 健康檢查 (Health Check)
4. 優雅關閉 (Graceful Shutdown)
5. 錯誤恢復 (Error Recovery)
"""

import signal
import sys
import time
import logging
import traceback
import threading
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class ConnectionState(Enum):
    """連接狀態"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ReconnectionConfig:
    """斷線重連配置"""
    max_retries: int = 5  # 最大重試次數
    initial_delay: float = 1.0  # 初始延遲 (秒)
    max_delay: float = 60.0  # 最大延遲 (秒)
    backoff_multiplier: float = 2.0  # 指數退避倍數
    timeout: float = 30.0  # 連接超時 (秒)
    health_check_interval: float = 10.0  # 健康檢查間隔


@dataclass
class ConnectionMetrics:
    """連接指標"""
    total_connections: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    total_reconnections: int = 0
    last_connection_time: Optional[datetime] = None
    last_error: Optional[str] = None
    uptime_seconds: float = 0.0
    connection_history: list = field(default_factory=list)


class RobustConnection:
    """強健連接管理器"""

    def __init__(
        self,
        name: str,
        connect_func: Callable,
        disconnect_func: Optional[Callable] = None,
        health_check_func: Optional[Callable] = None,
        config: Optional[ReconnectionConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化連接管理器
        
        Args:
            name: 連接名稱
            connect_func: 連接函數
            disconnect_func: 斷開連接函數
            health_check_func: 健康檢查函數
            config: 重連配置
            logger: 日誌記錄器
        """
        self.name = name
        self.connect_func = connect_func
        self.disconnect_func = disconnect_func or (lambda: None)
        self.health_check_func = health_check_func or (lambda: True)
        self.config = config or ReconnectionConfig()
        self.logger = logger or self._setup_logger()

        self.state = ConnectionState.DISCONNECTED
        self.metrics = ConnectionMetrics()
        self.current_retry = 0
        self._lock = threading.Lock()
        self._health_check_thread = None
        self._running = False
        self._connection_object = None

    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger(f"RobustConnection.{self.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def connect(self) -> bool:
        """嘗試連接 (使用指數退避重試)"""
        with self._lock:
            self.logger.info(f"[{self.name}] 開始連接...")
            self.state = ConnectionState.RECONNECTING

            for attempt in range(self.config.max_retries):
                try:
                    self.current_retry = attempt
                    delay = self._calculate_delay(attempt)

                    if attempt > 0:
                        self.logger.warning(
                            f"[{self.name}] 第 {attempt + 1} 次重試, 延遲 {delay:.1f}s"
                        )
                        time.sleep(delay)

                    # 執行連接
                    self._connection_object = self.connect_func()
                    self.state = ConnectionState.CONNECTED
                    self.metrics.successful_connections += 1
                    self.metrics.total_connections += 1
                    self.metrics.last_connection_time = datetime.now()
                    self.metrics.connection_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "status": "success",
                        "attempt": attempt + 1
                    })

                    self.logger.info(f"[{self.name}] ✅ 連接成功 (嘗試 #{attempt + 1})")
                    return True

                except Exception as e:
                    error_msg = str(e)
                    self.logger.error(
                        f"[{self.name}] ❌ 連接失敗 (嘗試 #{attempt + 1}): {error_msg}"
                    )
                    self.metrics.failed_connections += 1
                    self.metrics.last_error = error_msg
                    self.metrics.connection_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "attempt": attempt + 1,
                        "error": error_msg
                    })

            # 所有重試都失敗
            self.state = ConnectionState.FAILED
            self.logger.error(
                f"[{self.name}] ❌ 所有連接嘗試都失敗 (共 {self.config.max_retries} 次)"
            )
            return False

    def disconnect(self) -> None:
        """斷開連接"""
        with self._lock:
            try:
                self.disconnect_func()
                self.state = ConnectionState.DISCONNECTED
                self.logger.info(f"[{self.name}] 已斷開連接")
            except Exception as e:
                self.logger.error(f"[{self.name}] 斷開連接時出錯: {e}")

    def _calculate_delay(self, attempt: int) -> float:
        """計算指數退避延遲"""
        delay = self.config.initial_delay * (
            self.config.backoff_multiplier ** attempt
        )
        return min(delay, self.config.max_delay)

    def start_health_check(self) -> None:
        """開始定期健康檢查"""
        if self._health_check_thread and self._health_check_thread.is_alive():
            return

        self._running = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
        self.logger.info(f"[{self.name}] 🏥 健康檢查已啟動")

    def stop_health_check(self) -> None:
        """停止健康檢查"""
        self._running = False
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
        self.logger.info(f"[{self.name}] 🏥 健康檢查已停止")

    def _health_check_loop(self) -> None:
        """健康檢查循環"""
        while self._running:
            try:
                time.sleep(self.config.health_check_interval)

                if self.state == ConnectionState.CONNECTED:
                    if not self.health_check_func():
                        self.logger.warning(f"[{self.name}] ⚠️ 健康檢查失敗")
                        self._handle_health_check_failure()
                    else:
                        self.metrics.uptime_seconds += self.config.health_check_interval

            except Exception as e:
                self.logger.error(f"[{self.name}] 健康檢查異常: {e}")

    def _handle_health_check_failure(self) -> None:
        """處理健康檢查失敗"""
        self.logger.warning(f"[{self.name}] 偵測到連接異常, 嘗試重新連接...")
        self.state = ConnectionState.DISCONNECTED
        self.metrics.total_reconnections += 1
        self.connect()

    def get_status(self) -> Dict[str, Any]:
        """獲取連接狀態"""
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "metrics": {
                    "total_connections": self.metrics.total_connections,
                    "successful_connections": self.metrics.successful_connections,
                    "failed_connections": self.metrics.failed_connections,
                    "total_reconnections": self.metrics.total_reconnections,
                    "last_connection_time": self.metrics.last_connection_time.isoformat() 
                        if self.metrics.last_connection_time else None,
                    "uptime_seconds": self.metrics.uptime_seconds,
                    "last_error": self.metrics.last_error
                },
                "connection_history": self.metrics.connection_history[-10:]  # 最後10條記錄
            }


class CrashPreventionManager:
    """防閃退管理器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """初始化防閃退管理器"""
        self.logger = logger or self._setup_logger()
        self.crash_count = 0
        self.last_crash_time = None
        self._original_excepthook = sys.excepthook
        self._crash_handlers = []

    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger("CrashPreventionManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def register_crash_handler(self, handler: Callable) -> None:
        """註冊崩潰處理器"""
        self._crash_handlers.append(handler)
        self.logger.info("✅ 已註冊崩潰處理器")

    def start(self) -> None:
        """啟動防閃退保護"""
        # 設置全局異常處理
        sys.excepthook = self._global_exception_handler

        # 設置信號處理 (SIGTERM, SIGINT)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.logger.info("🛡️ 防閃退保護已啟動")

    def stop(self) -> None:
        """停止防閃退保護"""
        sys.excepthook = self._original_excepthook
        self.logger.info("🛡️ 防閃退保護已停止")

    def _global_exception_handler(self, exc_type, exc_value, exc_traceback) -> None:
        """全局異常處理"""
        self.crash_count += 1
        self.last_crash_time = datetime.now()

        error_msg = ''.join(traceback.format_exception(
            exc_type, exc_value, exc_traceback
        ))

        self.logger.error(f"💥 捕獲到未處理的異常 (#{self.crash_count}):")
        self.logger.error(error_msg)

        # 執行已註冊的崩潰處理器
        for handler in self._crash_handlers:
            try:
                handler(exc_type, exc_value, exc_traceback)
            except Exception as e:
                self.logger.error(f"崩潰處理器執行失敗: {e}")

        # 允許程序繼續運行（防止崩潰退出）
        self.logger.warning("⚠️ 程序將繼續運行")

    def _signal_handler(self, signum, frame) -> None:
        """信號處理"""
        sig_name = signal.Signals(signum).name
        self.logger.warning(f"⚠️ 收到信號: {sig_name}")

        # 執行優雅關閉
        for handler in self._crash_handlers:
            try:
                handler(None, None, None)
            except Exception as e:
                self.logger.error(f"信號處理器執行失敗: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """獲取防閃退統計"""
        return {
            "crash_count": self.crash_count,
            "last_crash_time": self.last_crash_time.isoformat() if self.last_crash_time else None,
            "status": "active" if sys.excepthook == self._global_exception_handler else "inactive"
        }


class SystemRobustness:
    """系統強健性管理器"""

    def __init__(self):
        """初始化系統強健性管理器"""
        self.logger = self._setup_logger()
        self.crash_manager = CrashPreventionManager(self.logger)
        self.connections: Dict[str, RobustConnection] = {}
        self._start_time = datetime.now()

    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger("SystemRobustness")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def register_connection(
        self,
        name: str,
        connect_func: Callable,
        disconnect_func: Optional[Callable] = None,
        health_check_func: Optional[Callable] = None,
        config: Optional[ReconnectionConfig] = None
    ) -> RobustConnection:
        """註冊受管理的連接"""
        connection = RobustConnection(
            name=name,
            connect_func=connect_func,
            disconnect_func=disconnect_func,
            health_check_func=health_check_func,
            config=config,
            logger=self.logger
        )
        self.connections[name] = connection
        self.logger.info(f"✅ 已註冊連接: {name}")
        return connection

    def register_crash_handler(self, handler: Callable) -> None:
        """註冊崩潰處理器"""
        self.crash_manager.register_crash_handler(handler)

    def start(self) -> None:
        """啟動系統強健性保護"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 Comic AI 防閃退和斷線重連系統啟動")
        self.logger.info("=" * 60)

        # 啟動防閃退
        self.crash_manager.start()

        # 啟動所有連接的健康檢查
        for connection in self.connections.values():
            connection.start_health_check()

        self.logger.info("✅ 系統強健性保護已啟動")

    def stop(self) -> None:
        """停止系統強健性保護"""
        self.logger.info("🛑 停止系統強健性保護...")

        # 停止所有健康檢查
        for connection in self.connections.values():
            connection.stop_health_check()

        # 停止防閃退
        self.crash_manager.stop()

        self.logger.info("✅ 系統強健性保護已停止")

    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        uptime = datetime.now() - self._start_time

        return {
            "uptime": str(uptime),
            "crash_stats": self.crash_manager.get_stats(),
            "connections": {
                name: conn.get_status()
                for name, conn in self.connections.items()
            }
        }

    def print_status_report(self) -> None:
        """打印狀態報告"""
        status = self.get_system_status()

        print("\n" + "=" * 60)
        print("📊 系統強健性狀態報告")
        print("=" * 60)
        print(f"系統運行時間: {status['uptime']}")
        print(f"崩潰次數: {status['crash_stats']['crash_count']}")

        if status['connections']:
            print("\n📡 連接狀態:")
            for name, conn_status in status['connections'].items():
                state = conn_status['state']
                metrics = conn_status['metrics']
                print(f"\n  {name}:")
                print(f"    狀態: {state}")
                print(f"    成功連接: {metrics['successful_connections']}")
                print(f"    失敗連接: {metrics['failed_connections']}")
                print(f"    重連次數: {metrics['total_reconnections']}")
                print(f"    運行時間: {metrics['uptime_seconds']:.1f}s")
                if metrics['last_error']:
                    print(f"    最後錯誤: {metrics['last_error']}")

        print("\n" + "=" * 60)


# 全局實例
_system_robustness = None


def get_robustness_manager() -> SystemRobustness:
    """獲取全局系統強健性管理器實例"""
    global _system_robustness
    if _system_robustness is None:
        _system_robustness = SystemRobustness()
    return _system_robustness


def initialize_robustness() -> SystemRobustness:
    """初始化系統強健性保護"""
    robustness = get_robustness_manager()
    robustness.start()
    return robustness


# 示例使用
if __name__ == "__main__":
    print("Comic AI 防閃退和斷線重連系統")
    print("=" * 60)

    # 初始化系統
    robustness = initialize_robustness()

    # 模擬連接
    def mock_connect():
        """模擬連接"""
        import random
        if random.random() > 0.3:
            return {"status": "connected"}
        raise ConnectionError("模擬連接失敗")

    def mock_health_check():
        """模擬健康檢查"""
        import random
        return random.random() > 0.1

    # 註冊連接
    conn1 = robustness.register_connection(
        name="API Server",
        connect_func=mock_connect,
        health_check_func=mock_health_check
    )

    # 註冊崩潰處理器
    def cleanup_handler(exc_type, exc_value, exc_traceback):
        print("\n🔧 執行清理程序...")
        for name, conn in robustness.connections.items():
            conn.disconnect()

    robustness.register_crash_handler(cleanup_handler)

    # 測試連接
    try:
        if conn1.connect():
            print("\n✅ 連接成功，系統運行中...")
            time.sleep(5)
            robustness.print_status_report()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷")
    finally:
        robustness.stop()
