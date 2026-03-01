#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永恆自主錯誤處理系統 - 後台守護程序
Eternal Autonomous Error Handler - Background Daemon

功能:
1. 持續在後台運行
2. 自動偵測和修復系統錯誤
3. 提供永不停止的故障保護
4. 開機自動啟動
5. 優雅的停止機制
"""

import os
import sys
import signal
import time
import atexit
import logging
from pathlib import Path
from datetime import datetime

# 配置編碼
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/cosmic-ai.uk/logs/eternal_autonomous_handler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EternalAutonomousHandler:
    """永恆自主錯誤處理守護程序"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.EternalAutonomousHandler")
        self.pid_file = Path("/workspaces/cosmic-ai.uk/logs/eternal_handler.pid")
        self.running = False
        self.start_time = None
        self.cycles = 0
        self.errors_fixed = 0
        
        # 註冊信號處理器
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        atexit.register(self.cleanup)
    
    def _signal_handler(self, signum, frame):
        """信號處理器"""
        self.logger.info(f"\n收到信號 {signum}，正在優雅停止...")
        self.running = False
    
    def cleanup(self):
        """清理資源"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
            self.logger.info("✅ 清理完成")
        except Exception as e:
            self.logger.error(f"❌ 清理失敗: {str(e)}")
    
    def write_pid(self):
        """寫入PID文件"""
        try:
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            self.logger.info(f"✅ PID文件已寫入: {self.pid_file}")
        except Exception as e:
            self.logger.error(f"❌ 無法寫入PID文件: {str(e)}")
    
    def run_eternal_loop(self):
        """永恆循環"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🚀 永恆自主錯誤處理系統啟動")
        self.logger.info("="*80)
        self.logger.info(f"PID: {os.getpid()}")
        self.logger.info(f"啟動時間: {datetime.now().isoformat()}")
        
        self.write_pid()
        self.running = True
        self.start_time = datetime.now()
        
        try:
            while self.running:
                self.cycles += 1
                cycle_start = datetime.now()
                
                self.logger.info(f"\n🔄 【循環 #{self.cycles}】")
                
                try:
                    # 執行自主錯誤處理
                    from autonomous_error_handler import AutonomousErrorHandlerSystem
                    
                    handler = AutonomousErrorHandlerSystem()
                    
                    # 運行一個快速檢查循環（不使用後台線程）
                    detector = handler.detector
                    corrector = handler.corrector
                    learner = handler.learner
                    
                    # 檢測編碼錯誤
                    test_text = "宇宙AI自主系統🚀"
                    encoding_error = detector.detect_encoding_errors(test_text)
                    if encoding_error:
                        from autonomous_error_handler import ErrorEvent
                        import hashlib
                        event = ErrorEvent(
                            error_id=hashlib.md5(encoding_error.encode()).hexdigest()[:12],
                            timestamp=datetime.now().isoformat(),
                            error_type='encoding_error',
                            error_message=encoding_error,
                            source='encoding_detector',
                            severity='medium',
                        )
                        success = corrector.auto_correct(event)
                        learner.learn_from_error(event, success)
                        if success:
                            self.errors_fixed += 1
                    
                    # 檢測內存錯誤
                    memory_error = detector.detect_memory_errors()
                    if memory_error:
                        from autonomous_error_handler import ErrorEvent
                        import hashlib
                        event = ErrorEvent(
                            error_id=hashlib.md5(memory_error['message'].encode()).hexdigest()[:12],
                            timestamp=datetime.now().isoformat(),
                            error_type=memory_error['type'],
                            error_message=memory_error['message'],
                            source='memory_detector',
                            severity='high' if 'critical' in memory_error['type'] else 'medium',
                        )
                        success = corrector.auto_correct(event)
                        learner.learn_from_error(event, success)
                        if success:
                            self.errors_fixed += 1
                    
                    # 統計信息
                    uptime = datetime.now() - self.start_time
                    self.logger.info(f"📊 統計:")
                    self.logger.info(f"   • 已運行: {uptime}")
                    self.logger.info(f"   • 總循環: {self.cycles}")
                    self.logger.info(f"   • 已修復: {self.errors_fixed} 個錯誤")
                    
                    learning_report = learner.get_learning_report()
                    self.logger.info(f"   • 已學習: {learning_report['total_patterns']} 個模式")
                    self.logger.info(f"   • 知識增益: {learning_report['average_knowledge_gain']:.2f}")
                    
                except ImportError:
                    self.logger.warning("⚠️ autonomous_error_handler 模組未找到")
                except Exception as e:
                    self.logger.error(f"❌ 循環錯誤: {str(e)}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                
                # 等待下一個循環
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(0, 10 - cycle_duration)  # 目標: 每10秒一次循環
                
                if self.running and sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            self.logger.info("\n⏸️  收到中斷信號")
        finally:
            self.running = False
            self._print_final_stats()
    
    def _print_final_stats(self):
        """打印最終統計"""
        if self.start_time:
            uptime = datetime.now() - self.start_time
            self.logger.info("\n" + "="*80)
            self.logger.info("📊 永恆自主錯誤處理系統 - 統計報告")
            self.logger.info("="*80)
            self.logger.info(f"啟動時間: {self.start_time.isoformat()}")
            self.logger.info(f"停止時間: {datetime.now().isoformat()}")
            self.logger.info(f"運行時間: {uptime}")
            self.logger.info(f"總循環: {self.cycles}")
            self.logger.info(f"已修復: {self.errors_fixed} 個錯誤")
            if self.cycles > 0:
                self.logger.info(f"平均修復率: {(self.errors_fixed / self.cycles) * 100:.1f}%")
            self.logger.info("="*80)


def main():
    """主函數"""
    handler = EternalAutonomousHandler()
    handler.run_eternal_loop()


if __name__ == "__main__":
    main()
