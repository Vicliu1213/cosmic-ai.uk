#!/usr/bin/env python3
"""
Google Gemini AI 集成模块
Google Gemini AI Integration Module
"""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import google.generativeai as genai

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleGeminiClient:
    """Google Gemini AI 客户端"""
    
    def __init__(self, api_key: Optional[str] = None) -> Any:
        """
        初始化 Gemini 客户端
        
        Args:
            api_key: Google Gemini API 密钥
                    如果为 None，将尝试从环境变量读取
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "❌ Google API 密钥未提供。\n"
                "请设置 GOOGLE_API_KEY 环境变量或传递 api_key 参数。\n"
                "获取免费密钥: https://aistudio.google.com/apikey"
            )
        
        # 配置 API
        genai.configure(api_key=self.api_key)
        
        # 初始化模型
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        
        logger.info("✅ Google Gemini 客户端已初始化")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用的 Gemini 模型列表"""
        try:
            models = genai.list_models()
            available = []
            
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available.append({
                        'name': model.name,
                        'display_name': model.display_name,
                        'input_token_limit': model.input_token_limit,
                        'output_token_limit': model.output_token_limit
                    })
            
            return available
        except Exception as e:
            logger.error(f"❌ 获取模型列表失败: {e}")
            return []
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 2048
    ) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 用户提示
            temperature: 温度参数 (0.0-1.0)
            max_output_tokens: 最大输出令牌数
        
        Returns:
            生成的文本
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )
            )
            
            return response.text
        except Exception as e:
            logger.error(f"❌ 文本生成失败: {e}")
            return f"错误: {str(e)}"
    
    def generate_with_chat(self, messages: List[Dict[str, str]]) -> str:
        """
        使用聊天接口生成响应
        
        Args:
            messages: 消息列表，每条消息包含 'role' 和 'content'
                     role: 'user' 或 'assistant'
                     content: 消息内容
        
        Returns:
            生成的响应
        """
        try:
            # 创建聊天会话
            chat = self.model.start_chat()
            
            # 发送所有历史消息
            for message in messages[:-1]:
                chat.send_message(message['content'])
            
            # 发送最后一条消息并获取响应
            response = chat.send_message(messages[-1]['content'])
            
            return response.text
        except Exception as e:
            logger.error(f"❌ 聊天生成失败: {e}")
            return f"错误: {str(e)}"
    
    def analyze_trading_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析交易信号
        
        Args:
            data: 包含交易数据的字典
        
        Returns:
            分析结果
        """
        prompt = f"""
        请分析以下交易数据并提供建议：
        
        {self._format_trading_data(data)}
        
        请返回 JSON 格式的分析结果，包含：
        - signal: 交易信号 (BUY/SELL/HOLD)
        - confidence: 信心度 (0-100)
        - reasoning: 分析原因
        - risk_level: 风险等级 (LOW/MEDIUM/HIGH)
        """
        
        try:
            response = self.generate_text(prompt)
            # 解析响应...
            return {
                'analysis': response,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 交易分析失败: {e}")
            return {'error': str(e)}
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        总结文本
        
        Args:
            text: 要总结的文本
            max_length: 摘要最大长度
        
        Returns:
            总结后的文本
        """
        prompt = f"""
        请用中文总结以下文本，不超过 {max_length} 个字：
        
        {text}
        """
        
        return self.generate_text(prompt, max_output_tokens=max_length)
    
    def code_review(self, code: str, language: str = "python") -> str:
        """
        代码审查
        
        Args:
            code: 要审查的代码
            language: 编程语言
        
        Returns:
            审查意见
        """
        prompt = f"""
        请审查以下 {language} 代码并提供改进建议：
        
        ```{language}
        {code}
        ```
        
        请指出：
        1. 可能的 bug
        2. 性能问题
        3. 代码风格改进
        4. 最佳实践建议
        """
        
        return self.generate_text(prompt)
    
    def _format_trading_data(self, data: Dict[str, Any]) -> str:
        """格式化交易数据"""
        lines = []
        for key, value in data.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

class GeminiMCPTool:
    """Gemini MCP 工具集成"""
    
    def __init__(self, api_key: Optional[str] = None) -> Any:
        """初始化 Gemini MCP 工具"""
        self.client = GoogleGeminiClient(api_key)
    
    async def analyze_market_sentiment(self, news: List[str]) -> Dict[str, Any]:
        """分析市场情绪"""
        combined_news = "\n".join(news)
        
        prompt = f"""
        请分析以下新闻的市场情绪，并返回 JSON 格式结果：
        
        {combined_news}
        
        返回格式：
        {{
            "sentiment": "positive/negative/neutral",
            "confidence": 0.0-1.0,
            "key_factors": ["因素1", "因素2"],
            "market_impact": "HIGH/MEDIUM/LOW"
        }}
        """
        
        response = self.client.generate_text(prompt)
        
        return {
            'analysis': response,
            'timestamp': datetime.now().isoformat()
        }
    
    async def generate_trading_strategy(self, 
                                       market_data: Dict[str, Any],
                                       risk_profile: str = "medium") -> Dict[str, Any]:
        """生成交易策略"""
        prompt = f"""
        基于以下市场数据和风险偏好，生成交易策略：
        
        市场数据：{market_data}
        风险偏好：{risk_profile}
        
        请返回详细的交易策略，包括：
        1. 策略名称
        2. 入场信号
        3. 止损点
        4. 获利目标
        5. 风险回报比
        """
        
        strategy = self.client.generate_text(prompt)
        
        return {
            'strategy': strategy,
            'risk_profile': risk_profile,
            'created_at': datetime.now().isoformat()
        }

def main() -> Any:
    """主函数 - 演示用法"""
    import sys
    
    # 从环境变量或命令行参数获取 API 密钥
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("❌ 需要 Google API 密钥")
        print("使用方式:")
        print("  1. 设置环境变量: export GOOGLE_API_KEY='your-key'")
        print("  2. 或传递参数: python script.py 'your-key'")
        print("\n获取免费 API 密钥: https://aistudio.google.com/apikey")
        return
    
    # 初始化客户端
    try:
        client = GoogleGeminiClient(api_key)
        print("✅ Gemini 客户端已初始化\n")
        
        # 获取可用模型
        models = client.get_available_models()
        print("📋 可用的 Gemini 模型:")
        print("-" * 60)
        for model in models:
            print(f"\n✓ {model['name']}")
            print(f"  显示名称: {model['display_name']}")
            print(f"  输入令牌上限: {model['input_token_limit']:,}")
            print(f"  输出令牌上限: {model['output_token_limit']:,}")
        
        # 示例：生成文本
        print("\n" + "=" * 60)
        print("📝 文本生成示例:")
        print("=" * 60)
        
        prompt = "用中文解释什么是量子计算，用 3 句话。"
        response = client.generate_text(prompt)
        print(f"提示: {prompt}")
        print(f"响应:\n{response}\n")
        
        # 示例：代码审查
        print("=" * 60)
        print("🔍 代码审查示例:")
        print("=" * 60)
        
        code = """
def calculate_profit(buy_price, sell_price, quantity) -> Any:
    profit = (sell_price - buy_price) * quantity
    return profit
        """
        
        review = client.code_review(code)
        print(f"代码:\n{code}")
        print(f"审查:\n{review}\n")
        
        # 示例：文本总结
        print("=" * 60)
        print("📄 文本总结示例:")
        print("=" * 60)
        
        text = """
        量子计算是一种利用量子力学现象来进行计算的新型计算方式。
        与传统计算机不同，量子计算机使用量子比特（qubits）而不是传统的二进制比特。
        这使得量子计算机能够同时处理多个状态，从而在特定问题上提供指数级的性能提升。
        """
        
        summary = client.summarize_text(text)
        print(f"原文:\n{text}")
        print(f"摘要:\n{summary}\n")
        
    except ValueError as e:
        print(f"❌ 初始化失败: {e}")
    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
