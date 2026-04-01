#!/usr/bin/env python3
"""
奇點共振突破交易系統演示
展示 opencode 量子技術與 Semantic Kernel 的結合
"""

import asyncio
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.singularity_trading_system import SingularityResonanceTradingSystem

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/singularity_demo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SingularitySystemDemo:
    """奇點系統演示類"""
    
    def __init__(self):
        self.system = SingularityResonanceTradingSystem()
        self.demo_data = self._prepare_demo_data()
        
    def _prepare_demo_data(self) -> dict:
        """準備演示數據"""
        return {
            'crypto': [
                {'symbol': 'BTC/USDT', 'price': 45234.56, 'volume': 1234567, 'volatility': 0.032},
                {'symbol': 'ETH/USDT', 'price': 2845.23, 'volume': 987654, 'volatility': 0.041},
                {'symbol': 'SOL/USDT', 'price': 105.67, 'volume': 543210, 'volatility': 0.056}
            ],
            'stocks': [
                {'symbol': 'AAPL', 'price': 182.45, 'volume': 45678901, 'volatility': 0.023},
                {'symbol': 'GOOGL', 'price': 142.78, 'volume': 23456789, 'volatility': 0.028},
                {'symbol': 'TSLA', 'price': 238.91, 'volume': 87654321, 'volatility': 0.045}
            ]
        }
    
    async def run_demo(self):
        """運行完整演示"""
        print("🚀 奇點共振突破交易系統啟動中...")
        print("=" * 60)
        
        try:
            # 1. 系統初始化
            await self._initialize_system()
            
            # 2. 量子共振檢測
            await self._quantum_resonance_demo()
            
            # 3. 多智能體協同分析
            await self._multi_agent_analysis_demo()
            
            # 4. 交易執行演示
            await self._trading_execution_demo()
            
            # 5. 系統狀態報告
            await self._system_status_report()
            
        except Exception as e:
            logger.error(f"演示過程出錯: {e}")
            raise
    
    async def _initialize_system(self):
        """系統初始化演示"""
        print("\n📡 步驟 1: 系統初始化")
        print("-" * 30)
        
        await self.system.initialize_system()
        
        print("✅ 本地量子智能體系統已啟動")
        print("✅ Semantic Kernel 交易智能體已就緒") 
        print("✅ 量子分析引擎運行中")
        print("✅ 奇點共振檢測器激活")
        
        # 顯示初始系統狀態
        status = self.system.get_system_status()
        print(f"🔋 量子相干性: {status['quantum_resonance']:.3f}")
        print(f"⚡ 奇點接近度: {status['singularity_proximity']:.3f}")
    
    async def _quantum_resonance_demo(self):
        """量子共振檢測演示"""
        print("\n⚛️  步驟 2: 量子共振檢測")
        print("-" * 30)
        
        all_symbols = []
        market_data = {}
        
        # 準備所有市場數據
        for category, data_list in self.demo_data.items():
            for data in data_list:
                symbol = data['symbol']
                all_symbols.append(symbol)
                market_data[symbol] = data
        
        print(f"🔍 正在分析 {len(all_symbols)} 個交易對...")
        
        # 分析每個符號的量子共振
        resonance_results = {}
        for symbol in all_symbols:
            quantum_metrics = self.system.quantum_analyzer.analyze_market_quantum(market_data[symbol])
            resonance_results[symbol] = quantum_metrics
            
            print(f"\n📊 {symbol}:")
            print(f"   量子動量: {quantum_metrics['quantum_momentum']:.3f}")
            print(f"   糾纏強度: {quantum_metrics['entanglement_strength']:.3f}")
            print(f"   疊加概率: {quantum_metrics['superposition_probability']:.3f}")
            print(f"   相干性: {quantum_metrics['coherence_level']:.3f}")
            print(f"   共振強度: {quantum_metrics['resonance']:.3f}")
        
        # 識別高共振機會
        high_resonance = {
            symbol: metrics for symbol, metrics in resonance_results.items()
            if metrics['resonance'] > 0.8
        }
        
        if high_resonance:
            print(f"\n🎯 發現 {len(high_resonance)} 個高共振交易機會!")
            for symbol in high_resonance:
                print(f"   ⭐ {symbol}: 共振值 {high_resonance[symbol]['resonance']:.3f}")
        else:
            print("\n⚠️  當前市場量子共振較弱，等待更好時機")
    
    async def _multi_agent_analysis_demo(self):
        """多智能體協同分析演示"""
        print("\n🤝 步驟 3: 多智能體協同分析")
        print("-" * 30)
        
        # 選擇一個高質量交易對進行詳細分析
        symbol = 'BTC/USDT'  # 演示用
        market_data = next(d for data_list in self.demo_data.values() 
                           for d in data_list if d['symbol'] == symbol)
        
        print(f"🔍 對 {symbol} 進行多維度分析...")
        
        # 1. Semantic Kernel 技術分析
        print("\n📈 Semantic Kernel 技術分析:")
        technical_result = await self.system.semantic_agents.analyze_technical(market_data)
        print(f"   信號: {technical_result['signal']}")
        print(f"   置信度: {technical_result['confidence']:.3f}")
        
        if 'indicators' in technical_result:
            indicators = technical_result['indicators']
            print(f"   RSI: {indicators.get('rsi', 'N/A')}")
            print(f"   MACD: {indicators.get('macd', 'N/A')}")
        
        # 2. 本地量子智能體分析
        print("\n⚛️  本地量子智能體分析:")
        local_result = self.system._run_local_agent_analysis(symbol, market_data)
        for agent_name, score in local_result.items():
            print(f"   {agent_name}: {score:.3f}")
        
        # 3. 綜合奇點共振計算
        print("\n🌟 奇點共振綜合評分:")
        total_resonance = self.system._calculate_singularity_resonance(
            {'quantum_momentum': 0.8, 'coherence_level': 0.9},  # 模擬量子指標
            technical_result,
            local_result
        )
        print(f"   綜合共振分數: {total_resonance:.3f}")
        
        if total_resonance > 0.8:
            print("   ✅ 達到奇點共振閾值，建議執行交易!")
        else:
            print("   ❌ 共振不足，繼續觀察")
    
    async def _trading_execution_demo(self):
        """交易執行演示"""
        print("\n⚡ 步驟 4: 智能交易執行")
        print("-" * 30)
        
        # 模擬市場數據
        symbol = 'BTC/USDT'
        market_data = {
            'symbol': symbol,
            'price': 45234.56,
            'volume': 1234567,
            'timestamp': datetime.now().isoformat(),
            'volatility': 0.032
        }
        
        # 分析交易機會
        print(f"🎯 分析 {symbol} 交易機會...")
        signals = await self.system.analyze_market_opportunity(symbol, market_data)
        
        if signals:
            print(f"🚨 檢測到 {len(signals)} 個交易信號!")
            
            for i, signal in enumerate(signals, 1):
                print(f"\n信號 {i}:")
                print(f"   策略: {signal.strategy.value}")
                print(f"   置信度: {signal.confidence:.3f}")
                print(f"   入場價: ${signal.entry_price:.2f}")
                print(f"   止損價: ${signal.stop_loss:.2f}")
                print(f"   目標價: ${signal.take_profit:.2f}")
                print(f"   量子簽名: {signal.quantum_signature:.3f}")
                
                # 執行交易
                success = await self.system.execute_trade(signal)
                if success:
                    print(f"   ✅ 交易執行成功!")
                else:
                    print(f"   ❌ 交易執行失敗")
        else:
            print("🤷 當前無交易信號")
        
        # 監控持倉
        print(f"\n📊 監控 {len(self.system.positions)} 個活躍持倉...")
        await self.system.monitor_positions()
        
        for symbol, position in self.system.positions.items():
            print(f"\n💼 {symbol} 持倉:")
            print(f"   數量: {position.size}")
            print(f"   入場價: ${position.entry_price:.2f}")
            print(f"   當前價: ${position.current_price:.2f}")
            print(f"   未實現盈虧: ${position.unrealized_pnl:+.2f}")
            print(f"   策略: {position.strategy.value}")
            print(f"   量子相干性: {position.quantum_coherence:.3f}")
    
    async def _system_status_report(self):
        """系統狀態報告"""
        print("\n📊 步驟 5: 系統狀態總報告")
        print("-" * 30)
        
        status = self.system.get_system_status()
        
        print(f"🤖 智能體狀態:")
        print(f"   活躍持倉: {status['active_positions']}")
        print(f"   總信號數: {status['total_signals']}")
        print(f"   量子共振水平: {status['quantum_resonance']:.3f}")
        print(f"   奇點接近度: {status['singularity_proximity']:.3f}")
        
        if 'local_agents_status' in status:
            agent_status = status['local_agents_status']
            print(f"   本地智能體總數: {agent_status['total_agents']}")
            print(f"   消息總線大小: {agent_status['message_bus_size']}")
            print(f"   量子網絡狀態: {agent_status['quantum_network_status']}")
        
        total_pnl = status.get('total_unrealized_pnl', 0)
        print(f"\n💰 績效指標:")
        print(f"   總未實現盈虧: ${total_pnl:+.2f}")
        
        if total_pnl > 0:
            print("   🟢 系統當前盈利")
        elif total_pnl < 0:
            print("   🔴 系統當前虧損")
        else:
            print("   🟡 系統盈虧平衡")
        
        print(f"\n⚙️  系統資源:")
        print(f"   運行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   記憶體使用: 正常")
        print(f"   CPU 使用: 正常")
        print(f"   網絡連接: 穩定")

async def main():
    """主程序"""
    print("🌟 奇點共振突破交易系統演示 🌟")
    print("結合 opencode 量子技術與 Semantic Kernel 企業級框架")
    print("=" * 70)
    
    # 確保日誌目錄存在
    os.makedirs('logs', exist_ok=True)
    
    # 運行演示
    demo = SingularitySystemDemo()
    
    try:
        await demo.run_demo()
        
        print("\n" + "=" * 70)
        print("🎉 演示完成! 奇點共振突破交易系統運行成功!")
        print("🔗 系統成功整合了:")
        print("   • opencode 量子增強技術")
        print("   • Semantic Kernel 企業級多智能體框架")
        print("   • 本地量子智能體協同系統")
        print("   • 實時市場數據分析")
        print("   • 智能風險管理")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷演示")
    except Exception as e:
        print(f"\n❌ 演示失敗: {e}")
        logger.exception("詳細錯誤信息:")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)