#!/usr/bin/env python3
"""
完整系統檢查和驗證腳本
檢查所有功能完整性
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def check_file_integrity():
    """檢查文件完整性"""
    print("\n📁 檢查文件完整性...")
    
    required_files = {
        'src/__init__.py': 'Main init',
        'src/main.py': 'Main entry',
        'src/data/__init__.py': 'Data init',
        'src/data/main.py': 'Data main',
        'src/analysis/__init__.py': 'Analysis init',
        'src/analysis/main.py': 'Analysis main',
        'src/utils/__init__.py': 'Utils init',
        'src/utils/main.py': 'Utils main',
        'src/quantum/__init__.py': 'Quantum init',
        'src/quantum/main.py': 'Quantum main',
        'src/optimizer/__init__.py': 'Optimizer init',
        'src/optimizer/main.py': 'Optimizer main',
        'src/agents/__init__.py': 'Agents init',
        'src/agents/main.py': 'Agents main',
        'src/execution/__init__.py': 'Execution init',
        'src/execution/main.py': 'Execution main',
        'src/risk/__init__.py': 'Risk init',
        'src/risk/main.py': 'Risk main',
        'src/core/__init__.py': 'Core init',
        'src/core/main.py': 'Core main',
        'src/strategies/__init__.py': 'Strategies init',
        'src/strategies/main.py': 'Strategies main',
    }
    
    missing_files = []
    for file_path, description in required_files.items():
        if not Path(file_path).exists():
            missing_files.append(f"{file_path} ({description})")
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n  ❌ 缺失文件:")
        for f in missing_files:
            print(f"    - {f}")
        return False
    
    return True


def check_structure():
    """檢查目錄結構"""
    print("\n🏗️  檢查目錄結構...")
    
    required_dirs = [
        'src', 'src/data', 'src/analysis', 'src/utils', 'src/quantum',
        'src/optimizer', 'src/agents', 'src/execution', 'src/risk',
        'src/core', 'src/strategies', 'tests'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    if missing_dirs:
        print(f"\n  ❌ 缺失目錄:")
        for d in missing_dirs:
            print(f"    - {d}")
        return False
    
    return True


def check_nested_inits():
    """檢查嵌套的 __init__.py"""
    print("\n🔗 檢查嵌套 __init__.py...")
    
    nested_inits = {
        'src/agents/core/__init__.py': 'Agents core',
        'src/agents/engine/__init__.py': 'Agents engine',
        'src/agents/engine/examples/__init__.py': 'Agents engine examples',
        'src/agents/engine/scripts/__init__.py': 'Agents engine scripts',
        'src/data/data/agents/__init__.py': 'Data agents',
        'src/utils/logging/__init__.py': 'Utils logging',
        'src/utils/notifications/__init__.py': 'Utils notifications',
        'src/lib/math/__init__.py': 'Lib math',
        'src/internal/pkg/__init__.py': 'Internal pkg',
        'src/system/dashboard/__init__.py': 'System dashboard',
        'src/system/recovery/__init__.py': 'System recovery',
        'src/tests/tests/__init__.py': 'Tests tests',
        'src/test_files/economic/__init__.py': 'Test files economic',
        'src/algorithms/engine/__init__.py': 'Algorithms engine',
    }
    
    missing_nested = []
    for file_path, description in nested_inits.items():
        if not Path(file_path).exists():
            missing_nested.append(f"{file_path} ({description})")
        else:
            print(f"  ✅ {file_path}")
    
    if missing_nested:
        print(f"\n  ❌ 缺失嵌套 __init__.py:")
        for f in missing_nested:
            print(f"    - {f}")
        return False
    
    return True


def check_documentation():
    """檢查文檔完整性"""
    print("\n📚 檢查文檔完整性...")
    
    doc_files = {
        'README.md': 'Project README',
        'STRUCTURE_AUDIT_REPORT.md': 'Structure audit',
        'requirements.txt': 'Dependencies',
    }
    
    missing_docs = []
    for file_path, description in doc_files.items():
        if not Path(file_path).exists():
            missing_docs.append(f"{file_path} ({description})")
        else:
            print(f"  ✅ {file_path}")
    
    if missing_docs:
        print(f"\n  ⚠️  缺失文檔:")
        for d in missing_docs:
            print(f"    - {d}")
    
    return len(missing_docs) == 0


def check_git_status():
    """檢查 Git 狀態"""
    print("\n🔀 檢查 Git 狀態...")
    
    git_dir = Path('.git')
    if git_dir.exists():
        print(f"  ✅ Git 倉庫已初始化")
        return True
    else:
        print(f"  ❌ Git 倉庫未初始化")
        return False


def generate_final_report():
    """生成最終報告"""
    print("\n" + "=" * 70)
    print("🎯 COSMIC AI - 系統完整性檢查")
    print("=" * 70)
    
    checks = {
        '文件完整性': check_file_integrity(),
        '目錄結構': check_structure(),
        '嵌套初始化': check_nested_inits(),
        '文檔完整性': check_documentation(),
        'Git 狀態': check_git_status(),
    }
    
    print("\n" + "=" * 70)
    print("📊 檢查結果摘要")
    print("=" * 70)
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n總體結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n✅ 系統完整性驗證通過!")
    else:
        print(f"\n⚠️  部分檢查失敗 ({total - passed} 項)")
    
    print("=" * 70 + "\n")
    
    return {
        'timestamp': datetime.now().isoformat(),
        'passed': passed,
        'total': total,
        'status': '✅ 全部通過' if passed == total else '⚠️ 部分失敗',
        'checks': checks
    }


if __name__ == "__main__":
    report = generate_final_report()
    
    # 保存報告
    with open('SYSTEM_INTEGRITY_CHECK.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    sys.exit(0 if report['passed'] == report['total'] else 1)
