#!/usr/bin/env python3
"""
Google Gemini API 快速入门脚本
Quick Start Guide for Google Gemini API
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.google_gemini_integration import GoogleGeminiClient


def test_gemini_basic():
    """测试 Gemini 基本功能"""
    
    print("🚀 Google Gemini API 快速测试\n")
    print("=" * 70)
    
    # 获取 API 密钥
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ 缺少 GOOGLE_API_KEY 环境变量\n")
        print("📌 快速设置步骤:\n")
        print("1️⃣  获取免费 API 密钥:")
        print("   访问: https://aistudio.google.com/apikey\n")
        print("2️⃣  设置环境变量:")
        print("   export GOOGLE_API_KEY='your-api-key-here'\n")
        print("3️⃣  验证设置:")
        print("   echo $GOOGLE_API_KEY\n")
        print("4️⃣  运行此脚本:")
        print("   python test_gemini.py\n")
        return
    
    try:
        # 初始化客户端
        print("⏳ 初始化 Gemini 客户端...")
        client = GoogleGeminiClient(api_key)
        print("✅ 客户端初始化成功\n")
        
        # 测试 1: 获取可用模型
        print("=" * 70)
        print("测试 1: 获取可用模型")
        print("=" * 70)
        
        models = client.get_available_models()
        if models:
            print(f"✅ 找到 {len(models)} 个可用模型:\n")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model['display_name']}")
                print(f"     ID: {model['name']}")
                print(f"     输入令牌: {model['input_token_limit']:,}")
                print(f"     输出令牌: {model['output_token_limit']:,}\n")
        else:
            print("⚠️  未找到可用模型\n")
        
        # 测试 2: 简单文本生成
        print("=" * 70)
        print("测试 2: 简单文本生成")
        print("=" * 70)
        
        prompt = "用一句话用中文解释什么是 API。"
        print(f"📝 提示: {prompt}\n")
        
        response = client.generate_text(prompt, max_output_tokens=256)
        print(f"🤖 回复: {response}\n")
        
        # 测试 3: 代码分析
        print("=" * 70)
        print("测试 3: 代码分析")
        print("=" * 70)
        
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(result)
        """
        
        print("📝 代码:")
        print(code)
        
        review = client.code_review(code, "python")
        print(f"🔍 分析:\n{review}\n")
        
        # 测试 4: 文本总结
        print("=" * 70)
        print("测试 4: 文本总结")
        print("=" * 70)
        
        text = """
        区块链技术是一种分布式数据库技术，具有去中心化、不可篡改和透明性等特点。
        它最初是作为比特币的底层技术被提出的，但现在已经被应用到更广泛的领域。
        从供应链管理到智能合约，区块链正在改变多个行业的运作方式。
        """
        
        print("📄 原文:")
        print(text)
        
        summary = client.summarize_text(text, max_length=100)
        print(f"\n📋 摘要:\n{summary}\n")
        
        print("=" * 70)
        print("✅ 所有测试完成！\n")
        
        print("📚 下一步:")
        print("  - 查看 Google Gemini 文档: https://ai.google.dev/")
        print("  - 探索更多功能: src/core/google_gemini_integration.py")
        print("  - 集成到你的项目中\n")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_gemini_basic()
