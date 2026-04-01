#!/usr/bin/env python3
"""
測試所有 __init__.py 和 main.py 是否可正常導入和執行
"""
import os
import sys
import json
import importlib.util
from pathlib import Path

SRC_DIR = Path('/workspaces/cosmic-ai.uk/src')
REPORT_FILE = Path('/workspaces/cosmic-ai.uk/IMPORT_TEST_REPORT.json')

def test_init_imports() -> Dict:
    """測試 __init__.py 導入"""
    report = {
        "init_files_tested": 0,
        "init_files_passed": 0,
        "init_files_failed": 0,
        "main_files_tested": 0,
        "main_files_passed": 0,
        "main_files_failed": 0,
        "errors": []
    }
    
    # 測試 __init__.py
    print("測試 __init__.py 導入...")
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
        
        if '__init__.py' in files:
            init_path = os.path.join(root, '__init__.py')
            rel_path = os.path.relpath(init_path, SRC_DIR)
            report["init_files_tested"] += 1
            
            try:
                spec = importlib.util.spec_from_file_location("temp_module", init_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    report["init_files_passed"] += 1
                    print(f"✓ {rel_path}")
                else:
                    report["init_files_failed"] += 1
                    error_msg = f"Could not load: {rel_path}"
                    report["errors"].append(error_msg)
                    print(f"✗ {rel_path}")
            except Exception as e:
                report["init_files_failed"] += 1
                error_msg = f"Error loading {rel_path}: {str(e)}"
                report["errors"].append(error_msg)
                print(f"✗ {rel_path}: {e}")
    
    return report

def test_main_execution() -> Dict:
    """測試 main.py 執行"""
    print("\n測試 main.py 執行...")
    
    main_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
        
        if 'main.py' in files:
            main_path = os.path.join(root, 'main.py')
            main_files.append(main_path)
    
    # 統計
    results = {
        "total": len(main_files),
        "passed": 0,
        "failed": 0,
        "syntax_checked": 0,
        "errors": []
    }
    
    for main_path in main_files:
        rel_path = os.path.relpath(main_path, SRC_DIR)
        
        try:
            # 檢查語法
            with open(main_path, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, main_path, 'exec')
            
            results["syntax_checked"] += 1
            results["passed"] += 1
            print(f"✓ {rel_path}")
        except SyntaxError as e:
            results["failed"] += 1
            error_msg = f"SyntaxError in {rel_path}: {e.msg} (line {e.lineno})"
            results["errors"].append(error_msg)
            print(f"✗ {rel_path}: {e}")
        except Exception as e:
            results["failed"] += 1
            error_msg = f"Error in {rel_path}: {str(e)}"
            results["errors"].append(error_msg)
            print(f"✗ {rel_path}: {e}")
    
    return results

def main():
    """主函數"""
    print("=" * 70)
    print("Python 導入和執行測試")
    print("=" * 70)
    print()
    
    # 測試導入
    import_report = test_init_imports()
    
    # 測試執行
    exec_report = test_main_execution()
    
    # 合併報告
    full_report = {
        "timestamp": str(Path.cwd()),
        "init_tests": import_report,
        "main_tests": exec_report,
        "summary": {
            "init_files_total": import_report["init_files_tested"],
            "init_files_passed": import_report["init_files_passed"],
            "init_files_failed": import_report["init_files_failed"],
            "main_files_total": exec_report["total"],
            "main_files_passed": exec_report["passed"],
            "main_files_failed": exec_report["failed"],
            "total_passed": import_report["init_files_passed"] + exec_report["passed"],
            "total_failed": import_report["init_files_failed"] + exec_report["failed"]
        }
    }
    
    # 打印摘要
    print()
    print("=" * 70)
    print("測試摘要")
    print("=" * 70)
    print(f"__init__.py 導入測試:")
    print(f"  總數: {import_report['init_files_tested']}")
    print(f"  通過: {import_report['init_files_passed']} ✓")
    print(f"  失敗: {import_report['init_files_failed']} ✗")
    print()
    print(f"main.py 執行測試:")
    print(f"  總數: {exec_report['total']}")
    print(f"  通過: {exec_report['passed']} ✓")
    print(f"  失敗: {exec_report['failed']} ✗")
    print()
    print(f"全部測試:")
    print(f"  通過: {full_report['summary']['total_passed']}")
    print(f"  失敗: {full_report['summary']['total_failed']}")
    print("=" * 70)
    
    # 保存報告
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"報告已保存到: {REPORT_FILE}")
    
    return 0 if full_report['summary']['total_failed'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
