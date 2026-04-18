"""
示例: fractal_recursion
中文名稱: 分形遞歸

此範例展示如何使用 分形遞歸 模組。
"""

import sys
from pathlib import Path

# 添加 src 路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """主函數"""
    print(f"Running example for 分形遞歸...")
    
    try:
        # 嘗試導入核心模塊
        from fractal_recursion import core
        print(f"✓ Successfully imported core module")
    except ImportError as e:
        print(f"✗ Failed to import core module: {e}")
        return False
    
    print("Example completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
