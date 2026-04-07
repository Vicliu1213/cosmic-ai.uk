# Google Gemini API 集成指南
# Google Gemini API Integration Guide

## 📋 目录
1. [快速开始](#快速开始)
2. [API 密钥获取](#api-密钥获取)
3. [安装和配置](#安装和配置)
4. [使用示例](#使用示例)
5. [集成到 Comic AI](#集成到-comic-ai)
6. [常见问题](#常见问题)

---

## 🚀 快速开始

### 最快 3 步使用 Gemini

```bash
# 1️⃣ 获取 API 密钥 (免费)
# 访问: https://aistudio.google.com/apikey

# 2️⃣ 设置环境变量
export GOOGLE_API_KEY='your-api-key-here'

# 3️⃣ 运行测试
python /root/comic_ai/test_gemini.py
```

---

## 🔑 API 密钥获取

### 方式 1: 免费 Google AI Studio API (推荐)

最简单、最快的方式，无需信用卡。

1. **访问 Google AI Studio**
   ```
   https://aistudio.google.com/apikey
   ```

2. **点击 "Create API key"**
   - 选择 "Create API key in new Google Cloud project"
   - 或选择现有项目

3. **复制 API 密钥**
   ```
   gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

4. **设置环境变量**
   ```bash
   export GOOGLE_API_KEY='gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
   ```

**限制**:
- 免费配额: 60 请求/分钟
- 适合开发和测试

---

### 方式 2: Google Cloud Vertex AI (企业级)

适合生产环境，需要 Google Cloud 账户。

1. **创建 Google Cloud 项目**
   ```
   https://console.cloud.google.com/
   ```

2. **启用 Vertex AI API**
   - 搜索 "Vertex AI"
   - 点击 "Enable API"

3. **创建服务账户**
   ```bash
   # 命令行创建
   gcloud iam service-accounts create my-gemini-sa
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:my-gemini-sa@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

4. **生成密钥文件**
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=my-gemini-sa@PROJECT_ID.iam.gserviceaccount.com
   ```

5. **在 .env 中配置**
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   ```

---

## 🔧 安装和配置

### 1. 安装必要的包

```bash
# 已在 requirements.txt 中，或手动安装
pip install google-generativeai --break-system-packages
```

### 2. 配置环境变量

编辑 `/root/comic_ai/.env`:

```ini
# Google Gemini API
GOOGLE_API_KEY=your-api-key-here

# 或 Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 3. 验证配置

```bash
cd /root/comic_ai

# 检查环境变量
echo $GOOGLE_API_KEY

# 运行测试脚本
python test_gemini.py
```

---

## 💡 使用示例

### 示例 1: 简单文本生成

```python
from src.core.google_gemini_integration import GoogleGeminiClient

# 初始化
client = GoogleGeminiClient()

# 生成文本
response = client.generate_text(
    "用中文解释什么是 API？",
    temperature=0.7,
    max_output_tokens=256
)

print(response)
```

**输出**:
```
API（应用程序编程接口）是一组规则和工具，允许不同的软件应用程序相互通信。
就像餐厅菜单一样，API 告诉开发者可以请求什么服务。
通过 API，第三方开发者可以访问特定的功能或数据，而不需要了解其内部工作原理。
```

---

### 示例 2: 代码审查

```python
client = GoogleGeminiClient()

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

**输出**:
```
这个函数功能正确，但可以改进：

1. 使用 sum() 和生成器表达式简化：
   total = sum(item.price * item.quantity for item in items)

2. 添加类型注释：
   def calculate_total(items: List[Item]) -> float:

3. 添加文档字符串：
   """计算所有项目的总价格"""

4. 考虑处理空列表
```

---

### 示例 3: 聊天对话

```python
client = GoogleGeminiClient()

messages = [
    {"role": "user", "content": "你是一个金融分析师，请分析股票市场。"},
    {"role": "user", "content": "现在我想知道科技股的趋势。"}
]

response = client.generate_with_chat(messages)
print(response)
```

---

### 示例 4: 交易信号分析

```python
client = GoogleGeminiClient()

trading_data = {
    "symbol": "AAPL",
    "current_price": 152.50,
    "50_day_ma": 150.00,
    "200_day_ma": 145.00,
    "rsi": 65,
    "volume": 52000000,
    "previous_close": 150.25
}

analysis = client.analyze_trading_signal(trading_data)
print(analysis)
```

---

## 🔌 集成到 Comic AI

### 1. 作为 MCP 工具

在 MCP 配置中添加:

```json
{
  "tools": [
    {
      "name": "gemini-analyzer",
      "type": "google_gemini",
      "config": {
        "api_key": "${GOOGLE_API_KEY}",
        "model": "gemini-pro"
      }
    }
  ]
}
```

### 2. 在交易系统中使用

编辑 `src/core/singularity_trading_system.py`:

```python
from src.core.google_gemini_integration import GeminiMCPTool

class SingularityTradingSystem:
    def __init__(self):
        self.gemini = GeminiMCPTool()
    
    async def analyze_market(self, market_data):
        # 使用 Gemini 分析市场
        strategy = await self.gemini.generate_trading_strategy(
            market_data,
            risk_profile="medium"
        )
        return strategy
```

### 3. 在数据分析器中使用

编辑 `src/core/data_analyzer_mcp.py`:

```python
from src.core.google_gemini_integration import GoogleGeminiClient

class DataAnalyzer:
    def __init__(self):
        self.gemini = GoogleGeminiClient()
    
    def analyze_report(self, report_text):
        # 使用 Gemini 总结分析报告
        summary = self.gemini.summarize_text(report_text)
        return summary
```

---

## 📚 API 文档

### GoogleGeminiClient 类

#### 初始化
```python
client = GoogleGeminiClient(api_key="your-key")
```

#### 方法

**1. generate_text()**
```python
response = client.generate_text(
    prompt: str,
    temperature: float = 0.7,
    max_output_tokens: int = 2048
) -> str
```

**2. generate_with_chat()**
```python
response = client.generate_with_chat(
    messages: List[Dict[str, str]]
) -> str
```

**3. get_available_models()**
```python
models = client.get_available_models() -> List[Dict]
```

**4. code_review()**
```python
review = client.code_review(
    code: str,
    language: str = "python"
) -> str
```

**5. summarize_text()**
```python
summary = client.summarize_text(
    text: str,
    max_length: int = 200
) -> str
```

**6. analyze_trading_signal()**
```python
analysis = client.analyze_trading_signal(
    data: Dict[str, Any]
) -> Dict[str, Any]
```

---

## 🎯 最佳实践

### 1. API 密钥安全

❌ **不要**:
```python
api_key = "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # 硬编码
```

✅ **要**:
```python
api_key = os.getenv('GOOGLE_API_KEY')  # 环境变量
```

### 2. 错误处理

```python
try:
    response = client.generate_text(prompt)
except ValueError as e:
    print(f"❌ 初始化失败: {e}")
except Exception as e:
    print(f"❌ API 错误: {e}")
```

### 3. 优化成本

```python
# 使用较短的 max_output_tokens
response = client.generate_text(
    prompt,
    max_output_tokens=512  # 而不是默认 2048
)

# 缓存重复的请求
cache = {}
if prompt not in cache:
    cache[prompt] = client.generate_text(prompt)
```

### 4. 温度参数说明

```
temperature:
- 0.0: 确定性，适合事实查询
- 0.7: 平衡（默认）
- 1.0: 随机性，适合创意任务
```

---

## ❓ 常见问题

### Q1: 如何获取 API 密钥？

**A**: 访问 https://aistudio.google.com/apikey，点击 "Create API key"，选择或创建项目即可。

### Q2: 免费配额是多少？

**A**: 
- 免费：60 请求/分钟
- 付费：根据使用情况计费

### Q3: 如何处理超时？

**A**:
```python
try:
    response = client.generate_text(prompt)
except Exception as e:
    if "timeout" in str(e):
        # 重试逻辑
        pass
```

### Q4: 支持哪些模型？

**A**: 
- `gemini-pro`: 文本生成（推荐）
- `gemini-pro-vision`: 图像理解（如有需要）

### Q5: 如何监控 API 使用情况？

**A**: 访问 https://aistudio.google.com/app/apikeys 查看使用统计

---

## 🔗 相关资源

- **Google Gemini 文档**: https://ai.google.dev/
- **API 参考**: https://ai.google.dev/api/rest
- **定价**: https://ai.google.dev/pricing
- **状态页面**: https://status.cloud.google.com/
- **社区论坛**: https://github.com/google-gemini/cookbook

---

## 📞 获取帮助

### 出现问题？

1. **检查 API 密钥**
   ```bash
   echo $GOOGLE_API_KEY
   ```

2. **查看日志**
   ```bash
   cat ~/.local/share/opencode/logs/
   ```

3. **运行诊断**
   ```bash
   python test_gemini.py
   ```

4. **查阅文档**
   ```bash
   https://ai.google.dev/
   ```

## 实践代码示例

### 基本使用

```python
import google.generativeai as genai
import os

# 配置 API
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

# 创建模型实例
model = genai.GenerativeModel('gemini-pro')

# 生成文本
response = model.generate_content("解释量子计算的基本原理")
print(response.text)
```

### 流式响应

```python
def stream_gemini_response(prompt):
    """流式获取 Gemini 响应"""
    
    model = genai.GenerativeModel('gemini-pro')
    
    print(f"提示: {prompt}")
    print("响应:")
    
    response = model.generate_content(
        prompt,
        stream=True
    )
    
    for chunk in response:
        print(chunk.text, end='', flush=True)
    print()

# 使用示例
stream_gemini_response("写一个 Python 函数来计算斐波那契数列")
```

### 错误处理

```python
def safe_gemini_call(prompt):
    """安全的 Gemini API 调用"""
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    
    except genai.types.APIError as e:
        print(f"API 错误: {e}")
        return None
    
    except genai.types.APIConnectionError as e:
        print(f"连接错误: {e}")
        return None
    
    except Exception as e:
        print(f"未知错误: {e}")
        return None

# 使用示例
result = safe_gemini_call("你好，Gemini")
if result:
    print(f"结果: {result}")
```

## 性能优化

### 请求队列管理

```python
from queue import Queue
import threading

class GeminiAPIQueue:
    """Gemini API 请求队列"""
    
    def __init__(self, max_workers=3):
        self.queue = Queue()
        self.max_workers = max_workers
        self.workers = []
        self._start_workers()
    
    def _start_workers(self):
        """启动工作线程"""
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def _worker(self):
        """工作线程"""
        model = genai.GenerativeModel('gemini-pro')
        
        while True:
            prompt, callback = self.queue.get()
            try:
                response = model.generate_content(prompt)
                callback(response.text)
            except Exception as e:
                callback(f"Error: {e}")
            finally:
                self.queue.task_done()
    
    def submit_request(self, prompt, callback):
        """提交请求"""
        self.queue.put((prompt, callback))

# 使用示例
api_queue = GeminiAPIQueue(max_workers=3)

def handle_response(text):
    print(f"收到: {text[:100]}...")

api_queue.submit_request("什么是机器学习？", handle_response)
```

## 故障排除表

| 问题 | 症状 | 解决方案 |
|------|------|--------|
| 无效的 API 密钥 | 401 认证错误 | 检查 GOOGLE_API_KEY 环境变量 |
| API 配额超限 | 429 速率限制 | 等待或升级配额 |
| 网络连接错误 | 连接超时 | 检查网络连接 |
| 模型不可用 | 404 不是找到 | 检查模型名称是否正确 |
| 内容过滤 | 400 坏请求 | 修改提示内容 |

---

**最后更新**: 2026-03-01  
**版本**: 1.1 (含实践代码和性能优化)
**增强内容**: +基本使用示例、+流式响应、+错误处理、+队列管理、+故障排除表

