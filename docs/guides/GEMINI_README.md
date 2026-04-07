# Google Gemini API 集成 - Comic AI

🎉 **完整的 Google Gemini AI 集成已完成！**

这个项目现在包含了完整的 Google Gemini API 集成，支持文本生成、代码审查、数据分析等多种功能。

## 🚀 快速开始（3 步）

### 1️⃣ 获取 API 密钥（免费）
访问 https://aistudio.google.com/apikey，点击 "Create API key"，复制密钥。

### 2️⃣ 设置环境变量
```bash
export GOOGLE_API_KEY='gsk_XXXXXXXXXXXXXXXXXXXXX'
```

### 3️⃣ 运行测试
```bash
python test_gemini.py
```

## 📁 项目结构

```
/root/comic_ai/
├── src/core/
│   └── google_gemini_integration.py      # 核心 Gemini 集成库
├── test_gemini.py                        # 测试脚本
├── demo_gemini_trading_analyst.py        # 交易分析演示
├── GEMINI_QUICK_REFERENCE.py             # 快速参考卡
├── GEMINI_SETUP_SUMMARY.txt              # 设置总结
├── GEMINI_README.md                      # 本文件
├── docs/
│   └── GEMINI_API_INTEGRATION_GUIDE.md   # 完整指南
└── .env                                  # 配置文件（已更新）
```

## 💻 基本用法

### 简单的文本生成
```python
from src.core.google_gemini_integration import GoogleGeminiClient

client = GoogleGeminiClient()
response = client.generate_text("用中文解释什么是 API？")
print(response)
```

### 代码审查
```python
code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item.price * item.quantity
    return total
"""

review = client.code_review(code, language="python")
print(review)
```

### 文本总结
```python
text = "长篇文本内容..."
summary = client.summarize_text(text, max_length=200)
print(summary)
```

### 聊天对话
```python
messages = [
    {"role": "user", "content": "你是一个金融分析师"},
    {"role": "user", "content": "分析一下科技股的前景"}
]
response = client.generate_with_chat(messages)
print(response)
```

## 🎯 可用功能

### GoogleGeminiClient 类

| 方法 | 功能 | 用例 |
|------|------|------|
| `generate_text()` | 生成文本响应 | 通用 AI 查询 |
| `generate_with_chat()` | 聊天对话 | 多轮对话 |
| `code_review()` | 代码审查 | 代码质量检查 |
| `summarize_text()` | 文本总结 | 文档摘要 |
| `analyze_trading_signal()` | 交易信号分析 | 交易决策 |
| `get_available_models()` | 获取可用模型 | 模型选择 |

### GeminiMCPTool 类

| 方法 | 功能 | 返回 |
|------|------|------|
| `analyze_market_sentiment()` | 分析市场情绪 | 情绪评分 |
| `generate_trading_strategy()` | 生成交易策略 | 策略建议 |

## 📚 文档

- **完整指南**: `docs/GEMINI_API_INTEGRATION_GUIDE.md`
  - 详细的集成说明
  - API 参考
  - 最佳实践
  - 常见问题

- **快速参考**: `python GEMINI_QUICK_REFERENCE.py`
  - 快速参考卡
  - 常见错误
  - 高级技巧

- **设置总结**: `cat GEMINI_SETUP_SUMMARY.txt`
  - 完成情况
  - 使用场景
  - 集成方法

## 🎓 示例脚本

### 1. 基本测试
```bash
python test_gemini.py
```
运行所有基本功能测试

### 2. 交易分析演示
```bash
python demo_gemini_trading_analyst.py
```
完整的交易分析系统演示，包括：
- 市场新闻分析
- 策略评估
- 投资组合分析
- 技术指标分析
- 风险管理建议

### 3. 快速参考
```bash
python GEMINI_QUICK_REFERENCE.py
```
显示完整的快速参考卡

## 🔧 配置

### 环境变量
编辑 `.env` 文件：
```ini
# 必需 - Google Gemini API
GOOGLE_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXX

# 可选 - Google Cloud Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 参数调整

```python
# 温度参数（0-1）
# 0.0: 确定性，适合事实查询
# 0.7: 平衡（默认）
# 1.0: 随机性，适合创意

response = client.generate_text(
    prompt="你的问题",
    temperature=0.7,
    max_output_tokens=2048
)
```

## 📊 API 配额

### 免费配额
- **速率**: 60 请求/分钟
- **成本**: 完全免费
- **功能**: 所有功能支持

### 付费配额
- **输入**: $0.075/百万令牌
- **输出**: $0.30/百万令牌
- **无速率限制**

## 🔐 安全最佳实践

✅ **正确做法**
- 使用环境变量存储 API 密钥
- 在 `.gitignore` 中排除 `.env`
- 定期轮换密钥
- 使用 IAM 限制访问权限

❌ **不要做的事**
- 硬编码 API 密钥
- 将密钥上传到 Git
- 在日志中打印密钥
- 分享密钥给他人

## 🆘 故障排除

### 问题 1: DefaultCredentialsError
```bash
# 检查环境变量
echo $GOOGLE_API_KEY

# 设置环境变量
export GOOGLE_API_KEY='your-key'
```

### 问题 2: 429 Too Many Requests
超过速率限制，可以：
- 添加请求延迟
- 升级到付费配额
- 实现重试逻辑

### 问题 3: 模型列表为空
- 检查 API 密钥是否有效
- 运行 `python test_gemini.py` 进行诊断

### 问题 4: 导入错误
```bash
pip install --upgrade google-generativeai
```

## 🔗 相关资源

- **官方文档**: https://ai.google.dev/
- **API 参考**: https://ai.google.dev/api/rest
- **社区论坛**: https://github.com/google-gemini/
- **定价信息**: https://ai.google.dev/pricing
- **状态页面**: https://status.cloud.google.com/

## 🎯 使用场景

### 交易系统
```python
# 生成交易策略
gemini = GeminiMCPTool()
strategy = await gemini.generate_trading_strategy(market_data)

# 分析市场情绪
sentiment = await gemini.analyze_market_sentiment(news_list)
```

### 数据分析
```python
# 总结长篇文章
summary = client.summarize_text(article_text)

# 生成数据分析报告
analysis = client.generate_text(f"分析以下数据：{data}")
```

### 代码开发
```python
# 代码审查
review = client.code_review(code_snippet)

# 优化建议
optimization = client.generate_text(f"优化以下代码的性能：{code}")
```

## 📈 性能建议

### 优化成本
```python
# 使用较短的 max_output_tokens
response = client.generate_text(
    prompt,
    max_output_tokens=512  # 而不是默认 2048
)
```

### 缓存结果
```python
cache = {}
if prompt not in cache:
    cache[prompt] = client.generate_text(prompt)
result = cache[prompt]
```

### 批量请求
```python
# 分批处理多个请求
results = []
for prompt in prompts:
    response = client.generate_text(prompt)
    results.append(response)
```

## ✨ 功能亮点

✓ **完整的 Python 集成库**  
✓ **支持多种 Gemini 模型**  
✓ **文本生成、代码审查、数据分析等**  
✓ **MCP 工具集成支持**  
✓ **详细的文档和示例**  
✓ **企业级安全实践**  
✓ **易于扩展和定制**  

## 📞 获取帮助

1. **查看快速参考**
   ```bash
   python GEMINI_QUICK_REFERENCE.py
   ```

2. **查看完整指南**
   ```bash
   cat docs/GEMINI_API_INTEGRATION_GUIDE.md
   ```

3. **运行测试**
   ```bash
   python test_gemini.py
   ```

4. **查阅官方文档**
   ```
   https://ai.google.dev/
   ```

## 🚀 下一步

1. ✅ 获取 API 密钥：https://aistudio.google.com/apikey
2. ✅ 设置环境变量：`export GOOGLE_API_KEY='your-key'`
3. ✅ 运行测试：`python test_gemini.py`
4. ✅ 查看示例：`python demo_gemini_trading_analyst.py`
5. ✅ 集成到你的项目
6. ✅ 构建应用

## 📝 许可证

本集成遵循 Comic AI 项目的许可证条款。

## 👨‍💻 贡献

欢迎贡献改进和新功能！

---

**最后更新**: 2026-02-19  
**版本**: 1.0.0  
**状态**: ✅ 完成并可用

**祝你使用 Google Gemini API 愉快！** 🎉

