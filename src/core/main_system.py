#!/usr/bin/env python3
"""
Comic AI 主系統入口 - 帶防閃退和斷線重連功能
Main Entry Point with Crash Prevention & Auto-Reconnection
"""

import sys
import os
import logging
from pathlib import Path

# 添加項目路徑
sys.path.insert(0, '/root/comic_ai')
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from system_robustness import (
    initialize_robustness,
    get_robustness_manager,
    ReconnectionConfig
)

try:
    from core.session_recap import SessionRecap
    RECAP_AVAILABLE = True
except ImportError:
    RECAP_AVAILABLE = False


class ComicAISystem:
    """Comic AI 主系統"""

    def __init__(self):
        """初始化系統"""
        self.logger = self._setup_logger()
        self.robustness = None
        self.is_running = False

    def _setup_logger(self) -> logging.Logger:
        """設置日誌"""
        logger = logging.getLogger("ComicAISystem")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _run_session_recap(self) -> None:
        """運行會話回顧"""
        try:
            self.logger.info("📝 運行會話回顧...")
            recap = SessionRecap()
            summary = recap.get_session_summary()
            
            if summary:
                self.logger.info("=" * 70)
                self.logger.info("📊 會話回顧摘要")
                self.logger.info("=" * 70)
                
                # 顯示 Git 分支
                self.logger.info(f"🌿 當前分支: {summary.git_branch}")
                
                # 顯示最近提交
                if summary.recent_commits:
                    self.logger.info("📜 最近提交:")
                    for commit in summary.recent_commits[:3]:
                        self.logger.info(f"  • {commit.hash[:7]} - {commit.message}")
                
                # 顯示未提交的變更
                if summary.uncommitted_changes:
                    self.logger.info(f"⚠️ 未提交的變更: {len(summary.uncommitted_changes)} 個文件")
                    for change in summary.uncommitted_changes[:5]:
                        self.logger.info(f"  • {change}")
                
                # 顯示建議
                if summary.recommendations:
                    self.logger.info("💡 建議:")
                    for rec in summary.recommendations:
                        self.logger.info(f"  • {rec}")
                
                self.logger.info("=" * 70)
            else:
                self.logger.info("ℹ️ 沒有會話記錄")
        
        except Exception as e:
            self.logger.warning(f"⚠️ 會話回顧失敗: {e}")

    def _setup_connections(self) -> None:
        """設置受管理的連接"""
        self.logger.info("🔌 設置系統連接...")

        # 示例：API連接
        def api_connect():
            """連接到API服務"""
            # 實際實現應與真實API連接
            return {"type": "api", "status": "connected"}

        def api_health_check():
            """API健康檢查"""
            # 實際實現應進行真實健康檢查
            return True

        # 註冊API連接
        self.robustness.register_connection(
            name="API Service",
            connect_func=api_connect,
            health_check_func=api_health_check,
            config=ReconnectionConfig(
                max_retries=5,
                initial_delay=2.0,
                max_delay=30.0
            )
        )

        self.logger.info("✅ 連接設置完成")

    def _setup_crash_handlers(self) -> None:
        """設置崩潰處理器"""
        self.logger.info("🔧 設置崩潰處理器...")

        def cleanup_handler(exc_type, exc_value, exc_traceback):
            """清理資源"""
            self.logger.warning("🔧 執行緊急清理...")
            try:
                for name, conn in self.robustness.connections.items():
                    conn.stop_health_check()
                    conn.disconnect()
                self.logger.info("✅ 清理完成")
            except Exception as e:
                self.logger.error(f"清理過程中出錯: {e}")

        self.robustness.register_crash_handler(cleanup_handler)
        self.logger.info("✅ 崩潰處理器設置完成")

    def initialize(self) -> bool:
        """初始化系統"""
        try:
            self.logger.info("=" * 70)
            self.logger.info("🚀 Comic AI 系統初始化中...")
            self.logger.info("=" * 70)

            # 運行自動回顧 (在啟動時)
            if RECAP_AVAILABLE:
                self._run_session_recap()

            # 初始化強健性管理器
            self.robustness = initialize_robustness()

            # 設置連接
            self._setup_connections()

            # 設置崩潰處理器
            self._setup_crash_handlers()

            # 嘗試連接所有服務
            self.logger.info("🔗 建立系統連接...")
            for name, conn in self.robustness.connections.items():
                if not conn.connect():
                    self.logger.warning(f"⚠️ {name} 連接失敗，將在後台重試")
                else:
                    self.logger.info(f"✅ {name} 已連接")

            self.is_running = True
            self.logger.info("=" * 70)
            self.logger.info("✅ Comic AI 系統已準備就緒")
            self.logger.info("=" * 70)
            return True

        except Exception as e:
            self.logger.error(f"❌ 系統初始化失敗: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self) -> None:
        """運行系統"""
        if not self.initialize():
            sys.exit(1)

        try:
            self.logger.info("🎯 系統運行中...")
            self.logger.info("按 Ctrl+C 優雅關閉...")

            # 主循環
            import time
            while self.is_running:
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("\n⚠️ 收到中斷信號")
        except Exception as e:
            self.logger.error(f"❌ 系統錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """優雅關閉"""
        self.logger.info("\n🛑 開始優雅關閉...")
        self.is_running = False

        if self.robustness:
            self.robustness.stop()

        self.logger.info("✅ 系統已關閉")

    def status(self) -> None:
        """顯示系統狀態"""
        if self.robustness:
            self.robustness.print_status_report()
        else:
            self.logger.warning("⚠️ 系統未初始化")


def main():
    """主函數"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Comic AI 主系統 - 帶防閃退和斷線重連功能"
    )
    parser.add_argument(
        '--mode',
        choices=['run', 'status'],
        default='run',
        help='運行模式'
    )

    args = parser.parse_args()

    # 創建系統實例
    system = ComicAISystem()

    if args.mode == 'run':
        system.run()
    elif args.mode == 'status':
        system.initialize()
        system.status()


if __name__ == "__main__":
    main()
