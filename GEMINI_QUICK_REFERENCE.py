#!/usr/bin/env python3
"""
Google Gemini API 快速参考卡
Google Gemini API Quick Reference Card
"""

QUICK_START = """
╔══════════════════════════════════════════════════════════════════════════╗
║              Google Gemini API - 快速参考卡                             ║
║              Quick Reference Card for Google Gemini API                 ║
╚══════════════════════════════════════════════════════════════════════════╝

📌 核心步骤
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  获取 API 密钥 (免费，无需信用卡)
    https://aistudio.google.com/apikey
    → 点击 "Create API key"
    → 复制密钥: gsk_XXXXXXXXXXXXXXXXXXXXX

2️⃣  设置环境变量
    export GOOGLE_API_KEY='gsk_XXXXXXXXXXXXXXXXXXXXX'

3️⃣  验证
    echo $GOOGLE_API_KEY  # 应该显示你的密钥

4️⃣  运行测试
    python /root/comic_ai/test_gemini.py


🚀 基本用法
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from src.core.google_gemini_integration import GoogleGeminiClient

# 初始化
client = GoogleGeminiClient()

# 生成文本
response = client.generate_text("你的问题")

# 代码审查
review = client.code_review(code_string)

# 文本总结
summary = client.summarize_text(long_text)

# 聊天对话
messages = [
    {"role": "user", "content": "消息1"},
    {"role": "user", "content": "消息2"}
]
response = client.generate_with_chat(messages)


📊 可用模型
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ gemini-pro
  - 文本生成
  - 聊天对话
  - 代码分析
  - 推荐使用

✓ gemini-pro-vision (如需图像识别)
  - 图像理解
  - 图像描述


🎯 常见用例
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 内容生成
    - 文章写作
    - 代码生成
    - 翻译
    - 总结

💡 分析和理解
    - 代码审查
    - 文档分析
    - 趋势分析
    - 风险评估

🤖 交互式应用
    - 聊天机器人
    - 问答系统
    - 辅导系统


⚙️ 参数说明
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

temperature (温度，0.0-1.0)
├─ 0.0: 确定性，适合事实查询
├─ 0.3-0.5: 平衡准确性和创意
├─ 0.7: 默认，推荐
└─ 1.0: 随机性，适合创意写作

max_output_tokens (最大输出)
├─ 256: 简短回答
├─ 512: 中等长度
├─ 1024: 详细答案
└─ 2048: 完整文档（默认）


📈 定价信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

免费配额:
├─ 输入: $0/百万令牌
├─ 输出: $0/百万令牌
└─ 限制: 60 请求/分钟

付费配额:
├─ 输入: $0.075/百万令牌
└─ 输出: $0.30/百万令牌


🔐 安全最佳实践
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ 不要
├─ 硬编码 API 密钥
├─ 将 API 密钥上传到 Git
├─ 在日志中打印密钥
└─ 分享你的密钥给任何人

✅ 要
├─ 使用环境变量存储密钥
├─ 在 .gitignore 中排除 .env
├─ 定期轮换密钥
└─ 使用 IAM 限制访问权限


❓ 常见错误
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

错误: DefaultCredentialsError
→ 解决: 设置 GOOGLE_API_KEY 环境变量

错误: 429 Too Many Requests
→ 解决: 超过速率限制，等待或升级到付费配额

错误: 401 Unauthorized
→ 解决: 检查 API 密钥是否有效

错误: ResourceExhausted
→ 解决: 超过月度配额


📚 有用的链接
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

获取密钥          https://aistudio.google.com/apikey
官方文档          https://ai.google.dev/
API 参考          https://ai.google.dev/api/rest
使用案例          https://github.com/google-gemini/cookbook
社区论坛          https://github.com/google-gemini/
状态页面          https://status.cloud.google.com/


🔥 高级技巧
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 链式提示
   ├─ 先让 Gemini 提出假设
   └─ 再让它验证假设

2. 少样本学习
   ├─ 提供几个例子
   └─ 模型会学习模式

3. 思维链
   ├─ 要求 Gemini 逐步思考
   └─ "先展示你的推理，然后给出答案"

4. 系统提示
   ├─ 定义 Gemini 的角色
   └─ 设定输出格式


💻 集成到 Comic AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 在交易系统中
from src.core.google_gemini_integration import GeminiMCPTool

gemini = GeminiMCPTool()
strategy = await gemini.generate_trading_strategy(market_data)

# 在数据分析中
from src.core.data_analyzer_mcp import DataAnalyzer

analyzer = DataAnalyzer()
summary = analyzer.analyze_with_gemini(report)


📞 需要帮助？
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 查看测试脚本
   python /root/comic_ai/test_gemini.py

2. 查看集成指南
   /root/comic_ai/docs/GEMINI_API_INTEGRATION_GUIDE.md

3. 查看示例代码
   /root/comic_ai/demo_gemini_trading_analyst.py

4. 查看 API 文档
   https://ai.google.dev/

═════════════════════════════════════════════════════════════════════════════
最后更新: 2026-02-19 | 版本: 1.0.0
═════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(QUICK_START)
