#!/usr/bin/env python3
"""
修復空的 __init__.py 文件
"""
import os
import json
from pathlib import Path

# 讀取驗證報告
REPORT_FILE = Path('/workspaces/cosmic-ai.uk/INIT_MAIN_VALIDATION_REPORT.json')

with open(REPORT_FILE, 'r', encoding='utf-8') as f:
    report = json.load(f)

# 提取空文件列表
empty_files = []
for path, info in report['init_files'].items():
    if info['size'].get('is_empty', False):
        empty_files.append(os.path.join('/workspaces/cosmic-ai.uk/src', path))

print(f"找到 {len(empty_files)} 個空的 __init__.py 文件")
print("正在修復...")
print()

# 模板內容
init_template = '''"""
Package initialization module.
"""

__version__ = "1.0.0"
__all__ = []
'''

fixed_count = 0
for file_path in empty_files:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(init_template)
        fixed_count += 1
        print(f"✓ {os.path.relpath(file_path, '/workspaces/cosmic-ai.uk/src')}")
    except Exception as e:
        print(f"✗ {os.path.relpath(file_path, '/workspaces/cosmic-ai.uk/src')}: {e}")

print()
print(f"已修復 {fixed_count}/{len(empty_files)} 個文件")
