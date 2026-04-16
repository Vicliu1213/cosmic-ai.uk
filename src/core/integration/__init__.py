"""
integration - 核心系統模塊

此模塊包含異變全知宇宙智能體系統的 integration 相關功能。
"""

# 自動導入該目錄下的所有 .py 文件（除了 __init__.py）
import os
import importlib

__dir__ = os.path.dirname(__file__)
__modules__ = []

for filename in os.listdir(__dir__):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = filename[:-3]
        try:
            importlib.import_module(f'.{module_name}', package=__name__)
            __modules__.append(module_name)
        except ImportError as e:
            print(f"警告: 無法導入 {module_name}: {e}")

__all__ = __modules__
