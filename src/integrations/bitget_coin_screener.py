#!/usr/bin/env python3
"""
BITGET實時幣種篩選系統
Real-time Coin Screener with BITGET API
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)


class BitgetCoinScreener:
    """BITGET實時幣種篩選系統"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        """初始化BITGET篩選器"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.bitget.com/v2"
        
        # 交易對列表
        self.trading_pairs = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT",
            "ADAUSDT", "SOLUSDT", "POLKAUSDT", "LINKUSDT", "UNIUSDT"
        ]
        
        # 數據緩存
        self.market_data_cache = {}
        self.price_history = {pair: deque(maxlen=100) for pair in self.trading_pairs}
        
        # 導入篩選器
        from src.integrations.coin_screener_quantum import QuantumCoinScreener, MarketMetrics
        self.screener = QuantumCoinScreener()
        self.MarketMetrics = MarketMetrics
        
        logger.info("✅ BITGET實時篩選器已初始化")
    
    async def fetch_market_data(self, symbol: str) -> Optional[Dict]:
        """獲取BITGET市場數據"""
        try:
            async with aiohttp.ClientSession() as session:
                # 獲取最新價格和成交量
                url = f"{self.base_url}/spot/market/tickers?symbol={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("code") == "00000":
                            return data.get("data", [{}])[0]
            return None
        except Exception as e:
            logger.error(f"獲取 {symbol} 數據失敗: {e}")
            return None
    
    async def fetch_kline_data(self, symbol: str, period: str = "1h") -> List[Dict]:
        """獲取K線數據"""
        try:
            period_map = {
                "1m": "1",
                "5m": "5",
                "15m": "15",
                "1h": "1H",
                "4h": "4H",
                "1d": "1D"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/spot/market/candles"
                params = {
                    "symbol": symbol,
                    "granularity": period_map.get(period, "1H"),
                    "limit": 100
                }
                
                async with session.get(url, params=params, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("code") == "00000":
                            return data.get("data", [])
            return []
        except Exception as e:
            logger.error(f"獲取 {symbol} K線數據失敗: {e}")
            return []
    
    async def fetch_orderbook(self, symbol: str) -> Optional[Dict]:
        """獲取訂單簿數據"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/spot/market/orderbook"
                params = {"symbol": symbol, "limit": 10}
                
                async with session.get(url, params=params, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("code") == "00000":
                            return data.get("data", {})
            return None
        except Exception as e:
            logger.error(f"獲取 {symbol} 訂單簿失敗: {e}")
            return None
    
    def _calculate_metrics(self, symbol: str, market_data: Dict, 
                          klines: List[Dict], orderbook: Dict) -> Optional[Dict]:
        """計算市場指標"""
        try:
            if not market_data or not klines:
                return None
            
            # 提取市場數據
            current_price = float(market_data.get("lastPr", 0))
            volume_24h = float(market_data.get("baseVolume24h", 0))
            
            # 計算價格變化
            klines_sorted = sorted(klines, key=lambda x: x[0], reverse=True)
            
            def get_price_change(hours: int) -> float:
                """計算指定小時的價格變化百分比"""
                for i, kline in enumerate(klines_sorted):
                    if i == hours:
                        open_price = float(kline[1])
                        close_price = float(kline[4])
                        change = ((current_price - open_price) / open_price) * 100
                        return change
                return 0.0
            
            price_1h_change = get_price_change(1) if len(klines_sorted) > 1 else 0
            price_4h_change = get_price_change(4) if len(klines_sorted) > 4 else 0
            price_24h_change = get_price_change(24) if len(klines_sorted) > 24 else 0
            price_7d_change = get_price_change(168) if len(klines_sorted) > 168 else 0
            
            # 計算成交量變化
            recent_volumes = [float(k[7]) for k in klines_sorted[:24]]
            avg_volume = np.mean(recent_volumes) if recent_volumes else 1
            volume_change_ratio = volume_24h / avg_volume if avg_volume > 0 else 1
            
            # 計算波動率
            closes = [float(k[4]) for k in klines_sorted[:24]]
            returns = np.diff(np.log(closes)) if len(closes) > 1 else [0]
            
            volatility_1h = np.std(returns[-1:]) if len(returns) >= 1 else 0.001
            volatility_4h = np.std(returns[-4:]) if len(returns) >= 4 else 0.01
            volatility_24h = np.std(returns[-24:]) if len(returns) >= 24 else 0.02
            
            volatility_ratio = volatility_1h / volatility_24h if volatility_24h > 0 else 1
            
            # 訂單簿分析
            bid_ask_spread = 0.0
            orderbook_imbalance = 1.0
            top_10_liquidity = 0.0
            
            if orderbook:
                bids = orderbook.get("bids", [])
                asks = orderbook.get("asks", [])
                
                if bids and asks:
                    best_bid = float(bids[0][0]) if bids else 0
                    best_ask = float(asks[0][0]) if asks else 0
                    
                    if best_ask > 0:
                        bid_ask_spread = (best_ask - best_bid) / best_ask
                    
                    total_bid = sum(float(b[1]) for b in bids[:10])
                    total_ask = sum(float(a[1]) for a in asks[:10])
                    
                    orderbook_imbalance = total_bid / total_ask if total_ask > 0 else 1
                    top_10_liquidity = (total_bid + total_ask) * current_price
            
            # RSI計算 (簡化版)
            def calculate_rsi(prices: List[float], period: int = 14) -> float:
                if len(prices) < period:
                    return 50.0
                
                gains = []
                losses = []
                
                for i in range(len(prices) - period, len(prices)):
                    change = prices[i] - prices[i-1]
                    if change > 0:
                        gains.append(change)
                    else:
                        losses.append(abs(change))
                
                avg_gain = np.mean(gains) if gains else 0
                avg_loss = np.mean(losses) if losses else 0
                
                if avg_loss == 0:
                    return 100.0 if avg_gain > 0 else 50.0
                
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                return rsi
            
            rsi_1h = calculate_rsi(closes[-14:]) if len(closes) >= 14 else 50
            rsi_4h = calculate_rsi(closes[-56:]) if len(closes) >= 56 else 50
            
            # MACD信號 (簡化版)
            macd_signal_1h = 1.0 if price_1h_change > 0 else -1.0
            
            # 布林帶位置
            if len(closes) >= 20:
                bb_ma = np.mean(closes[-20:])
                bb_std = np.std(closes[-20:])
                bb_position = (closes[-1] - (bb_ma - 2*bb_std)) / (4*bb_std) if bb_std > 0 else 0.5
                bb_position = np.clip(bb_position, 0, 1)
            else:
                bb_position = 0.5
            
            # 資金費率 (BITGET期貨才有，現貨暫設為0)
            funding_rate = 0.0
            funding_rate_change = 0.0
            
            return {
                'current_price': current_price,
                'price_1h_change': price_1h_change,
                'price_4h_change': price_4h_change,
                'price_24h_change': price_24h_change,
                'price_7d_change': price_7d_change,
                'volume_24h': volume_24h,
                'volume_change_ratio': volume_change_ratio,
                'volatility_1h': volatility_1h,
                'volatility_4h': volatility_4h,
                'volatility_24h': volatility_24h,
                'volatility_ratio': volatility_ratio,
                'bid_ask_spread': bid_ask_spread,
                'orderbook_imbalance': orderbook_imbalance,
                'top_10_liquidity': top_10_liquidity,
                'rsi_1h': rsi_1h,
                'rsi_4h': rsi_4h,
                'macd_signal_1h': macd_signal_1h,
                'bb_position': bb_position,
                'funding_rate': funding_rate,
                'funding_rate_change': funding_rate_change,
            }
        
        except Exception as e:
            logger.error(f"計算 {symbol} 指標失敗: {e}")
            return None
    
    async def screen_all_coins(self) -> List[Dict]:
        """篩選所有幣種"""
        logger.info("🔍 開始篩選幣種...")
        
        opportunities = []
        
        # 並行獲取所有幣種數據
        tasks = [self._screen_single_coin(pair) for pair in self.trading_pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"篩選失敗: {result}")
                continue
            if result:
                opportunities.append(result)
        
        # 按評分排序
        opportunities.sort(key=lambda x: x['scoring']['composite_score'], reverse=True)
        
        return opportunities
    
    async def _screen_single_coin(self, symbol: str) -> Optional[Dict]:
        """篩選單個幣種"""
        try:
            # 並行獲取數據
            market_data, klines, orderbook = await asyncio.gather(
                self.fetch_market_data(symbol),
                self.fetch_kline_data(symbol, "1h"),
                self.fetch_orderbook(symbol),
                return_exceptions=True
            )
            
            # 處理異常
            if isinstance(market_data, Exception):
                market_data = None
            if isinstance(klines, Exception):
                klines = None
            if isinstance(orderbook, Exception):
                orderbook = None
            
            # 計算指標
            metrics_dict = self._calculate_metrics(symbol, market_data, klines, orderbook)
            
            if not metrics_dict:
                return None
            
            # 創建MarketMetrics對象
            metrics = self.MarketMetrics(
                timestamp=datetime.now(),
                coin_id=symbol.replace("USDT", ""),
                price=metrics_dict['current_price'],
                price_1h_change=metrics_dict['price_1h_change'],
                price_4h_change=metrics_dict['price_4h_change'],
                price_24h_change=metrics_dict['price_24h_change'],
                price_7d_change=metrics_dict['price_7d_change'],
                volume_24h=metrics_dict['volume_24h'],
                volume_change_ratio=metrics_dict['volume_change_ratio'],
                volatility_1h=metrics_dict['volatility_1h'],
                volatility_4h=metrics_dict['volatility_4h'],
                volatility_24h=metrics_dict['volatility_24h'],
                volatility_ratio=metrics_dict['volatility_ratio'],
                bid_ask_spread=metrics_dict['bid_ask_spread'],
                orderbook_imbalance=metrics_dict['orderbook_imbalance'],
                top_10_liquidity=metrics_dict['top_10_liquidity'],
                funding_rate=metrics_dict['funding_rate'],
                funding_rate_change=metrics_dict['funding_rate_change'],
                rsi_1h=metrics_dict['rsi_1h'],
                rsi_4h=metrics_dict['rsi_4h'],
                macd_signal_1h=metrics_dict['macd_signal_1h'],
                bollinger_band_position=metrics_dict['bb_position']
            )
            
            # 篩選評分
            screening = self.screener._calculate_screening_score(metrics)
            
            return {
                'coin': symbol.replace("USDT", ""),
                'timestamp': datetime.now().isoformat(),
                'price': metrics_dict['current_price'],
                'scoring': {
                    'composite_score': screening.composite_score,
                    'breakout_probability': screening.breakout_probability,
                    'confidence': screening.confidence,
                    'risk_level': screening.risk_level,
                    'dimension_scores': screening.dimension_scores,
                },
                'signals': {
                    'detected_breakouts': [b.value for b in screening.detected_breakouts],
                    'singularity_detected': screening.singularity_detected,
                    'probability_cloud_density': screening.probability_cloud_density,
                    'resonance_strength': screening.resonance_strength,
                },
                'metrics': {
                    'price_1h_change': metrics_dict['price_1h_change'],
                    'price_4h_change': metrics_dict['price_4h_change'],
                    'volume_change_ratio': metrics_dict['volume_change_ratio'],
                    'volatility_ratio': metrics_dict['volatility_ratio'],
                    'rsi_1h': metrics_dict['rsi_1h'],
                    'rsi_4h': metrics_dict['rsi_4h'],
                    'orderbook_imbalance': metrics_dict['orderbook_imbalance'],
                }
            }
        
        except Exception as e:
            logger.error(f"篩選 {symbol} 失敗: {e}")
            return None
    
    async def generate_daily_report(self, output_file: str = "coin_screening_report.json") -> str:
        """生成日報告"""
        logger.info("📊 生成篩選報告...")
        
        opportunities = await self.screen_all_coins()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_coins_screened': len(self.trading_pairs),
            'coins_with_signals': len([o for o in opportunities if o['scoring']['composite_score'] > 70]),
            'top_opportunities': opportunities[:5],
            'all_results': opportunities,
        }
        
        # 保存報告
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ 報告已保存到 {output_file}")
        
        return output_file
    
    def print_summary(self, opportunities: List[Dict]):
        """打印篩選摘要"""
        print("\n" + "="*100)
        print("               🎯 BITGET實時幣種篩選結果")
        print("="*100)
        
        for i, opp in enumerate(opportunities[:10], 1):
            scoring = opp['scoring']
            signals = opp['signals']
            metrics = opp['metrics']
            
            # 標記高分幣種
            if scoring['composite_score'] > 85:
                marker = "🔥"
            elif scoring['composite_score'] > 75:
                marker = "⭐"
            else:
                marker = "✓"
            
            print(f"\n{marker} #{i} {opp['coin']} - ${opp['price']:.2f}")
            print(f"   綜合評分: {scoring['composite_score']:.1f}/100 | "
                  f"突破概率: {scoring['breakout_probability']:.1%} | "
                  f"置信度: {scoring['confidence']:.1%}")
            
            print(f"   風險等級: {scoring['risk_level'].upper()}")
            
            # 價格變化
            print(f"   價格變化: 1H={metrics['price_1h_change']:+.2f}% | "
                  f"4H={metrics['price_4h_change']:+.2f}% | "
                  f"成交量比: {metrics['volume_change_ratio']:.1f}x")
            
            # 信號
            if signals['detected_breakouts']:
                print(f"   🚀 檢測到突破: {', '.join(signals['detected_breakouts'])}")
            
            if signals['singularity_detected']:
                print(f"   🔴 檢測到奇點特徵！")
            
            if signals['probability_cloud_density'] > 70:
                print(f"   ☁️ 概率雲密度: {signals['probability_cloud_density']:.0f}% (信號匯聚強)")
            
            if signals['resonance_strength'] > 75:
                print(f"   🎯 共振對齐強度: {signals['resonance_strength']:.0f}%")
        
        print("\n" + "="*100)


# ============================================================================
# 主程序
# ============================================================================

async def main():
    """主程序"""
    screener = BitgetCoinScreener()
    
    # 篩選幣種
    opportunities = await screener.screen_all_coins()
    
    # 打印摘要
    screener.print_summary(opportunities)
    
    # 生成報告
    await screener.generate_daily_report("reports/coin_screening_report.json")


if __name__ == "__main__":
    asyncio.run(main())
