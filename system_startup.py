#!/usr/bin/env python3
"""
System Startup Configuration
系統啟動配置 - 確保 Ray 並行處理總是打開的
"""

import os
import sys
from pathlib import Path

# 設置環境變數以啟用 Ray
os.environ['RAY_ENABLED'] = '1'
os.environ['RAY_AUTO_INIT'] = '1'

# 導入 Ray 自動初始化模組
try:
    from ray_auto_init import RayAutoInit
    
    # 自動初始化 Ray
    if RayAutoInit.init(auto_start=True):
        print("✅ Ray 並行處理已自動啟用")
    else:
        print("⚠️  Ray 初始化失敗，繼續運行...")
except ImportError:
    print("⚠️  Ray 模組未找到，跳過自動初始化")
except Exception as e:
    print(f"⚠️  Ray 啟動異常: {e}")


def startup_checks():
    """執行系統啟動檢查"""
    import ray
    
    checks = {
        'Ray 狀態': ray.is_initialized(),
        '文件系統': Path('/workspaces/cosmic-ai.uk').exists(),
        'Python 版本': sys.version_info >= (3, 10),
    }
    
    print("\n📋 系統啟動檢查:")
    all_passed = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    return all_passed


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Cosmic AI 系統啟動")
    print("="*60)
    
    if startup_checks():
        print("\n✅ 系統已就緒")
    else:
        print("\n⚠️  系統檢查發現問題")
    
    print("="*60 + "\n")
