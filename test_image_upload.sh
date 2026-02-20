#!/bin/bash

# 測試圖片上傳功能的快速腳本

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🖼️  圖片上傳功能測試                                    ║"
echo "║        2026-02-20                                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 進入工作目錄
cd /root/comic_ai || exit 1

# 激活虛擬環境
echo "📌 激活虛擬環境..."
source venv/bin/activate
echo "✅ 虛擬環境激活完成"
echo ""

# 檢查文件處理器是否可用
echo "📌 檢查文件處理器..."
python3 -c "from intelligent_file_processor import IntelligentFileProcessor; print('✅ 文件處理器可用')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 文件處理器加載失敗"
    exit 1
fi
echo ""

# 創建測試圖片目錄
TEST_DIR="/tmp/comic_ai_test_images"
mkdir -p "$TEST_DIR"
echo "📌 測試目錄: $TEST_DIR"
echo ""

# 建立測試圖片 (1x1 PNG)
echo "📌 建立測試圖片..."
python3 << 'PYTHON_EOF'
from PIL import Image
import os

test_dir = "/tmp/comic_ai_test_images"
os.makedirs(test_dir, exist_ok=True)

# 建立簡單的 PNG 測試圖片
img = Image.new('RGB', (100, 100), color='red')
img.save(f'{test_dir}/test_image.png')

# 建立另一個 JPG 圖片
img2 = Image.new('RGB', (100, 100), color='blue')
img2.save(f'{test_dir}/test_image.jpg')

print(f"✅ 測試圖片已建立:")
print(f"   - {test_dir}/test_image.png")
print(f"   - {test_dir}/test_image.jpg")
PYTHON_EOF
echo ""

# 測試單個圖片上傳
echo "📌 測試單個圖片上傳..."
echo "命令: python3 intelligent_file_processor_cli.py upload $TEST_DIR/test_image.png"
echo ""
python3 intelligent_file_processor_cli.py upload "$TEST_DIR/test_image.png" --json 2>/dev/null | head -20
echo ""

# 測試批量處理
echo "📌 測試批量處理..."
echo "命令: python3 intelligent_file_processor_cli.py batch $TEST_DIR"
echo ""
python3 intelligent_file_processor_cli.py batch "$TEST_DIR" 2>/dev/null | head -20
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                     ✅ 測試完成                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 查看完整幫助:"
echo "   python3 intelligent_file_processor_cli.py help"
echo ""
echo "📍 使用實例:"
echo "   python3 intelligent_file_processor_cli.py upload image.jpg --report"
echo "   python3 intelligent_file_processor_cli.py batch ./images/ --strategy hybrid"
