#!/usr/bin/env python3
"""
驗證所有 __init__.py 和 main.py 文件的完整性和可執行性
"""
import os
import sys
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple

# 配置
SRC_DIR = Path('/workspaces/cosmic-ai.uk/src')
REPORT_FILE = Path('/workspaces/cosmic-ai.uk/INIT_MAIN_VALIDATION_REPORT.json')

def check_python_syntax(file_path: str) -> Tuple[bool, str]:
    """檢查 Python 文件語法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            if not code.strip():
                return False, "File is empty"
            ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} (line {e.lineno})"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_file_size(file_path: str) -> Dict:
    """檢查文件大小"""
    try:
        size = os.path.getsize(file_path)
        return {
            "bytes": size,
            "is_empty": size == 0,
            "status": "empty" if size == 0 else "ok"
        }
    except Exception as e:
        return {"error": str(e)}

def find_all_init_and_main_files() -> Tuple[List[str], List[str]]:
    """找到所有 __init__.py 和 main.py 文件"""
    init_files = []
    main_files = []
    
    for root, dirs, files in os.walk(SRC_DIR):
        # 跳過特定目錄
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
        
        for file in files:
            if file == '__init__.py':
                init_files.append(os.path.join(root, file))
            elif file == 'main.py':
                main_files.append(os.path.join(root, file))
    
    return sorted(init_files), sorted(main_files)

def validate_files() -> Dict:
    """驗證所有文件"""
    init_files, main_files = find_all_init_and_main_files()
    
    report = {
        "timestamp": str(Path.cwd()),
        "summary": {
            "total_init_files": len(init_files),
            "total_main_files": len(main_files),
            "init_files_ok": 0,
            "init_files_error": 0,
            "main_files_ok": 0,
            "main_files_error": 0,
            "empty_files": 0
        },
        "init_files": {},
        "main_files": {},
        "errors": []
    }
    
    # 驗證 __init__.py 文件
    for file_path in init_files:
        rel_path = os.path.relpath(file_path, SRC_DIR)
        file_info = {
            "path": rel_path,
            "absolute_path": file_path,
            "size": check_file_size(file_path)
        }
        
        # 檢查語法
        syntax_ok, syntax_msg = check_python_syntax(file_path)
        file_info["syntax"] = {
            "valid": syntax_ok,
            "message": syntax_msg
        }
        
        # 統計
        if file_info["size"].get("is_empty"):
            report["summary"]["empty_files"] += 1
            report["summary"]["init_files_error"] += 1
            report["errors"].append(f"Empty __init__.py: {rel_path}")
        elif syntax_ok:
            report["summary"]["init_files_ok"] += 1
        else:
            report["summary"]["init_files_error"] += 1
            report["errors"].append(f"Invalid syntax in {rel_path}: {syntax_msg}")
        
        report["init_files"][rel_path] = file_info
    
    # 驗證 main.py 文件
    for file_path in main_files:
        rel_path = os.path.relpath(file_path, SRC_DIR)
        file_info = {
            "path": rel_path,
            "absolute_path": file_path,
            "size": check_file_size(file_path)
        }
        
        # 檢查語法
        syntax_ok, syntax_msg = check_python_syntax(file_path)
        file_info["syntax"] = {
            "valid": syntax_ok,
            "message": syntax_msg
        }
        
        # 統計
        if file_info["size"].get("is_empty"):
            report["summary"]["empty_files"] += 1
            report["summary"]["main_files_error"] += 1
            report["errors"].append(f"Empty main.py: {rel_path}")
        elif syntax_ok:
            report["summary"]["main_files_ok"] += 1
        else:
            report["summary"]["main_files_error"] += 1
            report["errors"].append(f"Invalid syntax in {rel_path}: {syntax_msg}")
        
        report["main_files"][rel_path] = file_info
    
    return report

def main():
    """主函數"""
    print("正在驗證所有 __init__.py 和 main.py 文件...")
    print(f"搜索目錄: {SRC_DIR}")
    print()
    
    report = validate_files()
    
    # 打印摘要
    print("=" * 70)
    print("驗證摘要")
    print("=" * 70)
    print(f"  __init__.py 文件總數: {report['summary']['total_init_files']}")
    print(f"    ✓ 有效: {report['summary']['init_files_ok']}")
    print(f"    ✗ 錯誤: {report['summary']['init_files_error']}")
    print()
    print(f"  main.py 文件總數: {report['summary']['total_main_files']}")
    print(f"    ✓ 有效: {report['summary']['main_files_ok']}")
    print(f"    ✗ 錯誤: {report['summary']['main_files_error']}")
    print()
    print(f"  空文件數: {report['summary']['empty_files']}")
    print("=" * 70)
    
    # 打印錯誤
    if report["errors"]:
        print()
        print("❌ 發現的問題:")
        print("=" * 70)
        for i, error in enumerate(report["errors"], 1):
            print(f"{i}. {error}")
        print("=" * 70)
    else:
        print()
        print("✅ 所有文件都通過了驗證！")
        print()
    
    # 保存報告
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"詳細報告已保存到: {REPORT_FILE}")
    
    # 返回退出碼
    return 0 if not report["errors"] else 1

if __name__ == "__main__":
    sys.exit(main())
