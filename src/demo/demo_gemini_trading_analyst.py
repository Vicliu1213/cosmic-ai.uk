#!/usr/bin/env python3
"""
Google Gemini 在交易系统中的实际应用
Real-world application of Google Gemini in trading system
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.core.google_gemini_integration import GoogleGeminiClient


class TradingAnalystWithGemini:
    """使用 Gemini 的交易分析师"""
    
    def __init__(self):
        """初始化分析师"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "❌ 未找到 GOOGLE_API_KEY 环境变量\n"
                "请先设置: export GOOGLE_API_KEY='your-key'"
            )
        
        self.gemini = GoogleGeminiClient(api_key)
        print("✅ 交易分析师已初始化\n")
    
    def analyze_market_news(self, news_list: List[str]) -> Dict[str, Any]:
        """分析市场新闻"""
        news_text = "\n".join([f"- {news}" for news in news_list])
        
        prompt = f"""
        作为专业的金融分析师，请分析以下市场新闻，并提供交易建议：
        
        {news_text}
        
        请提供：
        1. 市场情绪分析（看涨/看跌/中立）
        2. 对股票的影响（正面/负面/中立）
        3. 建议的交易操作（买入/卖出/持仓）
        4. 风险等级（低/中/高）
        5. 置信度（0-100%）
        """
        
        analysis = self.gemini.generate_text(prompt)
        
        return {
            'market_news': news_list,
            'analysis': analysis,
            'type': 'market_analysis'
        }
    
    def evaluate_trading_strategy(self, strategy_description: str) -> Dict[str, Any]:
        """评估交易策略"""
        prompt = f"""
        请评估以下交易策略，并给出建议：
        
        {strategy_description}
        
        请分析：
        1. 策略的优势
        2. 潜在风险
        3. 改进建议
        4. 适用的市场条件
        5. 整体评分（1-10）
        """
        
        evaluation = self.gemini.generate_text(prompt)
        
        return {
            'strategy': strategy_description,
            'evaluation': evaluation,
            'type': 'strategy_evaluation'
        }
    
    def generate_portfolio_report(self, portfolio: Dict[str, Any]) -> str:
        """生成投资组合报告"""
        portfolio_text = "\n".join([
            f"- {symbol}: {data['quantity']} 股，"
            f"成本 {data['cost_price']:.2f}，"
            f"当前价 {data['current_price']:.2f}，"
            f"收益 {((data['current_price']/data['cost_price']-1)*100):.2f}%"
            for symbol, data in portfolio.items()
        ])
        
        prompt = f"""
        请基于以下投资组合数据生成一份专业的投资组合报告：
        
        {portfolio_text}
        
        报告应包含：
        1. 投资组合概览
        2. 收益分析
        3. 风险评估
        4. 配置建议
        5. 下一步行动
        
        用中文专业金融语言撰写。
        """
        
        report = self.gemini.generate_text(prompt)
        return report
    
    def analyze_technical_indicators(self, indicators: Dict[str, float]) -> str:
        """分析技术指标"""
        indicators_text = "\n".join([
            f"- {name}: {value}"
            for name, value in indicators.items()
        ])
        
        prompt = f"""
        作为技术分析师，请分析以下技术指标：
        
        {indicators_text}
        
        请提供：
        1. 各指标的意义
        2. 指标组合的信号
        3. 建议的交易行动
        4. 预期的价格走向
        5. 观察的关键水平
        """
        
        analysis = self.gemini.generate_text(prompt)
        return analysis
    
    def risk_management_advice(self, position_data: Dict[str, Any]) -> str:
        """风险管理建议"""
        prompt = f"""
        请根据以下头寸信息提供风险管理建议：
        
        头寸大小: {position_data.get('position_size', 'N/A')}
        股票代码: {position_data.get('symbol', 'N/A')}
        入场价: {position_data.get('entry_price', 'N/A')}
        当前价: {position_data.get('current_price', 'N/A')}
        账户规模: {position_data.get('account_size', 'N/A')}
        风险承受度: {position_data.get('risk_tolerance', 'N/A')}
        
        请提供：
        1. 适当的止损位置
        2. 适当的获利目标
        3. 头寸规模评估
        4. 风险回报比
        5. 风险管理最佳实践
        """
        
        advice = self.gemini.generate_text(prompt)
        return advice


def demo_analysis():
    """演示分析功能"""
    
    print("🎯 Google Gemini 交易分析系统演示\n")
    print("=" * 70)
    
    try:
        analyst = TradingAnalystWithGemini()
        
        # 演示 1: 市场新闻分析
        print("\n📰 演示 1: 市场新闻分析")
        print("-" * 70)
        
        market_news = [
            "美联储宣布维持利率不变，市场反应积极",
            "科技股因 AI 芯片需求上升而上涨",
            "能源股因油价下跌而承压"
        ]
        
        news_analysis = analyst.analyze_market_news(market_news)
        print("📊 分析结果:")
        print(news_analysis['analysis'])
        
        # 演示 2: 策略评估
        print("\n" + "=" * 70)
        print("🎲 演示 2: 交易策略评估")
        print("-" * 70)
        
        strategy = """
        均值回归策略：
        - 当价格跌破 20 天均线 2% 时买入
        - 当价格回到 20 天均线时卖出
        - 仓位大小：账户的 5%
        - 止损：买入价的下方 3%
        """
        
        strategy_eval = analyst.evaluate_trading_strategy(strategy)
        print("📋 策略评估:")
        print(strategy_eval['evaluation'])
        
        # 演示 3: 投资组合报告
        print("\n" + "=" * 70)
        print("💼 演示 3: 投资组合分析")
        print("-" * 70)
        
        portfolio = {
            "AAPL": {
                "quantity": 100,
                "cost_price": 150.00,
                "current_price": 152.50
            },
            "MSFT": {
                "quantity": 50,
                "cost_price": 300.00,
                "current_price": 298.50
            },
            "GOOGL": {
                "quantity": 75,
                "cost_price": 140.00,
                "current_price": 142.30
            }
        }
        
        portfolio_report = analyst.generate_portfolio_report(portfolio)
        print("📊 投资组合报告:")
        print(portfolio_report)
        
        # 演示 4: 技术指标分析
        print("\n" + "=" * 70)
        print("📈 演示 4: 技术指标分析")
        print("-" * 70)
        
        indicators = {
            "RSI (14)": 65,
            "MACD": 0.45,
            "移动平均线 (50)": 150.00,
            "移动平均线 (200)": 145.00,
            "布林带": "处于中轨上方",
            "成交量": "高于平均"
        }
        
        tech_analysis = analyst.analyze_technical_indicators(indicators)
        print("🔍 技术分析:")
        print(tech_analysis)
        
        # 演示 5: 风险管理建议
        print("\n" + "=" * 70)
        print("⚠️ 演示 5: 风险管理建议")
        print("-" * 70)
        
        position = {
            "symbol": "AAPL",
            "position_size": 10000,
            "entry_price": 150.00,
            "current_price": 152.50,
            "account_size": 100000,
            "risk_tolerance": "中等"
        }
        
        risk_advice = analyst.risk_management_advice(position)
        print("🛡️ 建议:")
        print(risk_advice)
        
        print("\n" + "=" * 70)
        print("✅ 演示完成！")
        print("\n💡 下一步:")
        print("  - 集成到你的交易系统")
        print("  - 自定义分析模板")
        print("  - 建立自动化工作流")
        
    except ValueError as e:
        print(f"❌ 初始化失败: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_analysis()
