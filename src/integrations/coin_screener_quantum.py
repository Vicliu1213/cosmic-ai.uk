#!/usr/bin/env python3
"""
量子共振突破幣種篩選系統
Quantum Resonance Breakout Coin Screener

核心功能:
- 11維度市場數據分析
- 共振突破模式檢測
- 奇點特徵識別
- 概率雲密度計算
- 高勝率幣種推薦
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
from collections import deque
from enum import Enum
import json

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# 篩選維度枚舉
# ============================================================================

class ScreeningDimension(Enum):
    """11維篩選維度"""
    PRICE_MOMENTUM = "price_momentum"           # 價格動量
    VOLUME_BREAKOUT = "volume_breakout"         # 成交量突破
    VOLATILITY_ANOMALY = "volatility_anomaly"   # 波動率異常
    RESONANCE_ALIGNMENT = "resonance_alignment" # 共振對齐
    SINGULARITY_SCORE = "singularity_score"     # 奇點分數
    PROBABILITY_CLOUD = "probability_cloud"     # 概率雲
    TECHNICAL_CONFLUENCE = "technical_confluence" # 技術匯聚
    ORDERBOOK_IMBALANCE = "orderbook_imbalance" # 訂單簿失衡
    FUNDING_RATE_SPIKE = "funding_rate_spike"   # 資金費率尖峰
    SOCIAL_SENTIMENT = "social_sentiment"       # 社群情緒
    LIQUIDITY_DEPTH = "liquidity_depth"         # 流動性深度


class BreakoutType(Enum):
    """突破類型"""
    PRICE_BREAKOUT = "price_breakout"           # 價格突破
    VOLUME_BREAKOUT = "volume_breakout"         # 成交量突破
    VOLATILITY_SPIKE = "volatility_spike"       # 波動率尖峰
    RESONANCE_BREAKOUT = "resonance_breakout"   # 共振突破
    MULTI_TIMEFRAME = "multi_timeframe"         # 多時間框架突破


# ============================================================================
# 數據結構
# ============================================================================

@dataclass
class MarketMetrics:
    """市場指標"""
    timestamp: datetime
    coin_id: str
    
    # 價格數據
    price: float
    price_1h_change: float
    price_4h_change: float
    price_24h_change: float
    price_7d_change: float
    
    # 成交量數據
    volume_24h: float
    volume_change_ratio: float  # 與平均成交量的比率
    
    # 波動率
    volatility_1h: float
    volatility_4h: float
    volatility_24h: float
    volatility_ratio: float  # 短期/長期波動率
    
    # 訂單簿
    bid_ask_spread: float
    orderbook_imbalance: float  # 買單/賣單比率
    top_10_liquidity: float
    
    # 資金費率
    funding_rate: float
    funding_rate_change: float
    
    # 技術指標
    rsi_1h: float
    rsi_4h: float
    macd_signal_1h: float
    bollinger_band_position: float  # 0-1, 0=下軌, 1=上軌


@dataclass
class ScreeningScore:
    """篩選評分"""
    coin_id: str
    timestamp: datetime
    
    # 各維度評分 (0-100)
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    
    # 綜合指標
    composite_score: float = 0.0  # 總體評分 (0-100)
    breakout_probability: float = 0.0  # 突破概率 (0-1)
    
    # 特徵檢測
    detected_breakouts: List[BreakoutType] = field(default_factory=list)
    singularity_detected: bool = False
    probability_cloud_density: float = 0.0
    resonance_strength: float = 0.0
    
    # 其他
    risk_level: str = "medium"  # low, medium, high
    confidence: float = 0.0


@dataclass
class CoinOpportunity:
    """幣種交易機會"""
    coin_id: str
    timestamp: datetime
    
    scoring: ScreeningScore
    metrics: MarketMetrics
    
    # 建議
    recommended_action: str  # "strong_buy", "buy", "hold", "sell"
    price_target: float
    stop_loss: float
    entry_price: float
    confidence: float
    
    # 詳細分析
    key_factors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    catalysts: List[str] = field(default_factory=list)


# ============================================================================
# 量子篩選引擎
# ============================================================================

class QuantumCoinScreener:
    """量子幣種篩選器"""
    
    def __init__(self, lookback_periods: Dict = None):
        """初始化篩選器"""
        self.lookback_periods = lookback_periods or {
            'short': 5,    # 5分鐘
            'medium': 1,   # 1小時
            'long': 4      # 4小時
        }
        
        self.screening_weights = self._initialize_weights()
        self.historical_data = {}
        self.opportunity_cache = {}
        
        logger.info("🚀 量子幣種篩選器已初始化")
    
    def _initialize_weights(self) -> Dict[str, float]:
        """初始化各維度權重"""
        return {
            ScreeningDimension.PRICE_MOMENTUM.value: 0.12,
            ScreeningDimension.VOLUME_BREAKOUT.value: 0.15,
            ScreeningDimension.VOLATILITY_ANOMALY.value: 0.10,
            ScreeningDimension.RESONANCE_ALIGNMENT.value: 0.14,
            ScreeningDimension.SINGULARITY_SCORE.value: 0.12,
            ScreeningDimension.PROBABILITY_CLOUD.value: 0.11,
            ScreeningDimension.TECHNICAL_CONFLUENCE.value: 0.10,
            ScreeningDimension.ORDERBOOK_IMBALANCE.value: 0.08,
            ScreeningDimension.FUNDING_RATE_SPIKE.value: 0.06,
            ScreeningDimension.SOCIAL_SENTIMENT.value: 0.06,
            ScreeningDimension.LIQUIDITY_DEPTH.value: 0.06,
        }
    
    def screen_coins(self, market_data: List[MarketMetrics], 
                    min_score: float = 70.0) -> List[CoinOpportunity]:
        """篩選幣種"""
        opportunities = []
        
        for metrics in market_data:
            try:
                # 計算篩選評分
                scoring = self._calculate_screening_score(metrics)
                
                # 如果評分滿足最低要求
                if scoring.composite_score >= min_score:
                    # 生成交易機會
                    opportunity = self._generate_opportunity(metrics, scoring)
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.error(f"篩選 {metrics.coin_id} 失敗: {e}")
                continue
        
        # 按綜合評分排序
        opportunities.sort(key=lambda x: x.scoring.composite_score, reverse=True)
        
        return opportunities
    
    def _calculate_screening_score(self, metrics: MarketMetrics) -> ScreeningScore:
        """計算篩選評分"""
        scoring = ScreeningScore(
            coin_id=metrics.coin_id,
            timestamp=metrics.timestamp
        )
        
        # 計算各維度評分
        dimensions = {
            ScreeningDimension.PRICE_MOMENTUM: self._score_price_momentum(metrics),
            ScreeningDimension.VOLUME_BREAKOUT: self._score_volume_breakout(metrics),
            ScreeningDimension.VOLATILITY_ANOMALY: self._score_volatility_anomaly(metrics),
            ScreeningDimension.RESONANCE_ALIGNMENT: self._score_resonance_alignment(metrics),
            ScreeningDimension.SINGULARITY_SCORE: self._score_singularity(metrics),
            ScreeningDimension.PROBABILITY_CLOUD: self._score_probability_cloud(metrics),
            ScreeningDimension.TECHNICAL_CONFLUENCE: self._score_technical_confluence(metrics),
            ScreeningDimension.ORDERBOOK_IMBALANCE: self._score_orderbook(metrics),
            ScreeningDimension.FUNDING_RATE_SPIKE: self._score_funding_rate(metrics),
            ScreeningDimension.SOCIAL_SENTIMENT: self._score_social_sentiment(metrics),
            ScreeningDimension.LIQUIDITY_DEPTH: self._score_liquidity(metrics),
        }
        
        # 保存各維度評分
        scoring.dimension_scores = {
            dim.value: score for dim, score in dimensions.items()
        }
        
        # 計算綜合評分 (加權平均)
        composite = sum(
            dimensions[dim] * self.screening_weights[dim.value]
            for dim in dimensions.keys()
        )
        
        scoring.composite_score = min(100.0, max(0.0, composite))
        
        # 檢測突破
        scoring.detected_breakouts = self._detect_breakouts(metrics)
        scoring.breakout_probability = self._calculate_breakout_probability(scoring)
        
        # 檢測奇點
        scoring.singularity_detected = self._detect_singularity(metrics)
        
        # 計算概率雲密度
        scoring.probability_cloud_density = self._calculate_probability_cloud(metrics)
        
        # 計算共振強度
        scoring.resonance_strength = dimensions[ScreeningDimension.RESONANCE_ALIGNMENT]
        
        # 評估風險
        scoring.risk_level = self._assess_risk_level(metrics, scoring)
        
        # 計算置信度
        scoring.confidence = self._calculate_confidence(scoring)
        
        return scoring
    
    # ========== 各維度評分函數 ==========
    
    def _score_price_momentum(self, metrics: MarketMetrics) -> float:
        """價格動量評分"""
        # 多時間框架動量檢查
        momentum_1h = metrics.price_1h_change
        momentum_4h = metrics.price_4h_change
        momentum_24h = metrics.price_24h_change
        
        # 檢測上升動量
        if momentum_1h > 0 and momentum_4h > 0 and momentum_24h > 0:
            # 全時間框架上升 (最佳)
            score = 85 + min(15, momentum_1h * 100)
        elif momentum_1h > 2 and momentum_4h > 0:
            # 短期強勁上升
            score = 75 + momentum_1h
        elif momentum_1h > 0 and momentum_4h > 0:
            # 中期上升
            score = 65 + momentum_1h * 2
        else:
            score = 40 + max(0, momentum_1h * 20)
        
        return min(100.0, max(0.0, score))
    
    def _score_volume_breakout(self, metrics: MarketMetrics) -> float:
        """成交量突破評分"""
        vol_ratio = metrics.volume_change_ratio
        
        # 成交量異常檢測
        if vol_ratio > 3.0:
            # 成交量大幅增加 (3倍以上)
            score = 90 + min(10, (vol_ratio - 3) * 5)
        elif vol_ratio > 2.0:
            # 成交量顯著增加 (2-3倍)
            score = 80
        elif vol_ratio > 1.5:
            # 成交量中等增加 (1.5-2倍)
            score = 70
        elif vol_ratio > 1.2:
            # 成交量輕微增加 (1.2-1.5倍)
            score = 60
        else:
            score = 40
        
        return min(100.0, max(0.0, score))
    
    def _score_volatility_anomaly(self, metrics: MarketMetrics) -> float:
        """波動率異常評分"""
        vol_ratio = metrics.volatility_ratio
        
        # 波動率奇點檢測 (異常波動)
        if vol_ratio > 2.0:
            # 短期波動率極高 (可能形成突破)
            score = 85
        elif vol_ratio > 1.5:
            # 波動率明顯升高
            score = 75
        elif 0.5 < vol_ratio < 1.5:
            # 正常範圍
            score = 50
        elif vol_ratio < 0.5:
            # 波動率異常低 (可能醞釀突破)
            score = 70
        else:
            score = 40
        
        return min(100.0, max(0.0, score))
    
    def _score_resonance_alignment(self, metrics: MarketMetrics) -> float:
        """共振對齐評分"""
        # 多時間框架技術指標對齐
        rsi_aligned = (metrics.rsi_1h > 50 and metrics.rsi_4h > 50) or \
                      (metrics.rsi_1h < 50 and metrics.rsi_4h < 50)
        
        # MACD信號對齐
        macd_aligned = metrics.macd_signal_1h > 0
        
        # 布林帶位置
        bb_position = metrics.bollinger_band_position
        
        score = 0
        if rsi_aligned and macd_aligned:
            score = 80 + abs(metrics.rsi_1h - 50) / 5
        elif rsi_aligned:
            score = 70
        elif macd_aligned:
            score = 60
        else:
            score = 40
        
        # 布林帶上軌加分
        if bb_position > 0.8:
            score += 15
        
        return min(100.0, max(0.0, score))
    
    def _score_singularity(self, metrics: MarketMetrics) -> float:
        """奇點評分 - 檢測臨界點特徵"""
        # 奇點定義: 多個異常同時出現
        anomaly_count = 0
        
        # 檢測各類異常
        if metrics.volatility_ratio > 1.8:
            anomaly_count += 1
        if metrics.volume_change_ratio > 2.5:
            anomaly_count += 1
        if abs(metrics.price_1h_change) > 2:
            anomaly_count += 1
        if metrics.orderbook_imbalance > 1.5 or metrics.orderbook_imbalance < 0.7:
            anomaly_count += 1
        if abs(metrics.funding_rate) > 0.005:
            anomaly_count += 1
        
        # 異常越多，奇點越強
        score = anomaly_count * 15
        
        return min(100.0, max(0.0, score))
    
    def _score_probability_cloud(self, metrics: MarketMetrics) -> float:
        """概率雲評分"""
        # 概率雲 = 多個信號在接近的價格區域聚集
        cloud_score = 0
        signal_count = 0
        
        # 檢測多個技術信號
        if metrics.rsi_1h > 70 or metrics.rsi_1h < 30:
            signal_count += 1
        if metrics.macd_signal_1h > 0:
            signal_count += 1
        if 0.3 < metrics.bollinger_band_position < 0.7:
            signal_count += 1
        if metrics.volume_change_ratio > 1.5:
            signal_count += 1
        
        cloud_score = signal_count * 20
        
        return min(100.0, max(0.0, cloud_score))
    
    def _score_technical_confluence(self, metrics: MarketMetrics) -> float:
        """技術匯聚評分"""
        confluence_count = 0
        
        # 多個技術指標同時發信號
        if metrics.rsi_1h > 70:
            confluence_count += 1
        if metrics.rsi_4h > 70:
            confluence_count += 1
        if metrics.macd_signal_1h > 0:
            confluence_count += 1
        if metrics.bollinger_band_position > 0.8:
            confluence_count += 1
        if metrics.price_1h_change > 1:
            confluence_count += 1
        
        score = confluence_count * 18
        
        return min(100.0, max(0.0, score))
    
    def _score_orderbook(self, metrics: MarketMetrics) -> float:
        """訂單簿失衡評分"""
        imbalance = metrics.orderbook_imbalance
        spread = metrics.bid_ask_spread
        
        # 失衡程度
        imbalance_score = 0
        if imbalance > 1.5:
            imbalance_score = 80  # 買單遠多於賣單
        elif imbalance > 1.3:
            imbalance_score = 70
        elif imbalance > 1.1:
            imbalance_score = 60
        elif 0.9 < imbalance < 1.1:
            imbalance_score = 40  # 相對平衡
        else:
            imbalance_score = 50 + (1 - imbalance) * 20
        
        # 價差獎勵 (低價差表示流動性好)
        spread_bonus = 0
        if spread < 0.01:
            spread_bonus = 10
        
        return min(100.0, max(0.0, imbalance_score + spread_bonus))
    
    def _score_funding_rate(self, metrics: MarketMetrics) -> float:
        """資金費率評分"""
        funding_rate = metrics.funding_rate
        funding_change = metrics.funding_rate_change
        
        score = 50
        
        # 資金費率尖峰
        if abs(funding_rate) > 0.01:
            score = 80
        elif abs(funding_rate) > 0.005:
            score = 70
        
        # 資金費率上升
        if funding_change > 0.002:
            score += 15
        
        return min(100.0, max(0.0, score))
    
    def _score_social_sentiment(self, metrics: MarketMetrics) -> float:
        """社群情緒評分 (簡化版)"""
        # 在實際應用中應連接社群數據
        # 這裡使用技術指標作為代理
        return 50.0  # 預設中性
    
    def _score_liquidity(self, metrics: MarketMetrics) -> float:
        """流動性深度評分"""
        liquidity = metrics.top_10_liquidity
        
        # 根據前10檔訂單的流動性評分
        if liquidity > 5000000:
            score = 95
        elif liquidity > 2000000:
            score = 85
        elif liquidity > 1000000:
            score = 75
        elif liquidity > 500000:
            score = 65
        else:
            score = 40
        
        return min(100.0, max(0.0, score))
    
    # ========== 特徵檢測函數 ==========
    
    def _detect_breakouts(self, metrics: MarketMetrics) -> List[BreakoutType]:
        """檢測突破"""
        breakouts = []
        
        # 價格突破
        if metrics.price_1h_change > 3:
            breakouts.append(BreakoutType.PRICE_BREAKOUT)
        
        # 成交量突破
        if metrics.volume_change_ratio > 3:
            breakouts.append(BreakoutType.VOLUME_BREAKOUT)
        
        # 波動率尖峰
        if metrics.volatility_ratio > 2.5:
            breakouts.append(BreakoutType.VOLATILITY_SPIKE)
        
        # 多時間框架對齐時的共振突破
        if (metrics.price_1h_change > 1 and metrics.price_4h_change > 1 and 
            metrics.volume_change_ratio > 2):
            breakouts.append(BreakoutType.RESONANCE_BREAKOUT)
        
        # 多時間框架突破
        if (metrics.price_1h_change > 0 and metrics.price_4h_change > 0 and 
            metrics.price_24h_change > 0):
            breakouts.append(BreakoutType.MULTI_TIMEFRAME)
        
        return breakouts
    
    def _detect_singularity(self, metrics: MarketMetrics) -> bool:
        """檢測奇點"""
        anomaly_count = 0
        
        # 計算異常數量
        if metrics.volatility_ratio > 2.0:
            anomaly_count += 1
        if metrics.volume_change_ratio > 3.0:
            anomaly_count += 1
        if abs(metrics.price_1h_change) > 2.5:
            anomaly_count += 1
        if metrics.orderbook_imbalance > 1.8 or metrics.orderbook_imbalance < 0.5:
            anomaly_count += 1
        if abs(metrics.funding_rate) > 0.01:
            anomaly_count += 1
        if metrics.bollinger_band_position > 0.95 or metrics.bollinger_band_position < 0.05:
            anomaly_count += 1
        
        # 3個或以上異常同時發生 = 奇點
        return anomaly_count >= 3
    
    def _calculate_probability_cloud(self, metrics: MarketMetrics) -> float:
        """計算概率雲密度"""
        # 概率雲 = 多個信號在相似價格區域聚集的密度
        signal_density = 0
        
        # 技術信號匯聚
        signals_present = 0
        if 30 < metrics.rsi_1h < 70:
            signals_present += 1
        if metrics.macd_signal_1h > 0:
            signals_present += 1
        if 0.2 < metrics.bollinger_band_position < 0.8:
            signals_present += 1
        if 1.2 < metrics.volume_change_ratio < 3:
            signals_present += 1
        if 1.2 < metrics.volatility_ratio < 2.5:
            signals_present += 1
        
        # 信號匯聚度
        signal_density = (signals_present / 5.0) * 100
        
        return min(100.0, max(0.0, signal_density))
    
    def _calculate_breakout_probability(self, scoring: ScreeningScore) -> float:
        """計算突破概率"""
        prob = 0.5  # 基礎概率
        
        # 檢測到的突破越多，概率越高
        prob += len(scoring.detected_breakouts) * 0.1
        
        # 奇點檢測提高概率
        if scoring.singularity_detected:
            prob += 0.15
        
        # 共振強度提高概率
        prob += (scoring.resonance_strength / 100.0) * 0.2
        
        # 概率雲密度提高概率
        prob += (scoring.probability_cloud_density / 100.0) * 0.1
        
        return min(1.0, max(0.0, prob))
    
    def _assess_risk_level(self, metrics: MarketMetrics, 
                          scoring: ScreeningScore) -> str:
        """評估風險等級"""
        risk_score = 0
        
        # 波動率高 = 風險高
        if metrics.volatility_ratio > 2:
            risk_score += 30
        elif metrics.volatility_ratio > 1.5:
            risk_score += 15
        
        # 流動性低 = 風險高
        if metrics.top_10_liquidity < 500000:
            risk_score += 25
        
        # 訂單簿失衡嚴重 = 風險高
        if metrics.orderbook_imbalance > 2 or metrics.orderbook_imbalance < 0.5:
            risk_score += 20
        
        # 價差寬 = 風險高
        if metrics.bid_ask_spread > 0.05:
            risk_score += 15
        
        if risk_score > 50:
            return "high"
        elif risk_score > 30:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, scoring: ScreeningScore) -> float:
        """計算置信度"""
        conf = 0.5
        
        # 綜合評分高 = 置信度高
        conf += (scoring.composite_score / 100.0) * 0.3
        
        # 檢測到奇點 = 置信度高
        if scoring.singularity_detected:
            conf += 0.1
        
        # 檢測到多個突破 = 置信度高
        if len(scoring.detected_breakouts) >= 2:
            conf += 0.1
        
        return min(1.0, max(0.0, conf))
    
    def _generate_opportunity(self, metrics: MarketMetrics, 
                             scoring: ScreeningScore) -> CoinOpportunity:
        """生成交易機會"""
        
        # 確定推薦行動
        if scoring.composite_score > 85 and scoring.breakout_probability > 0.8:
            action = "strong_buy"
        elif scoring.composite_score > 75 and scoring.breakout_probability > 0.7:
            action = "buy"
        else:
            action = "hold"
        
        # 計算目標價格
        price_target = metrics.price * (1 + metrics.price_1h_change / 100 * 1.5)
        
        # 計算止損
        stop_loss = metrics.price * (1 - abs(metrics.volatility_1h * 3))
        
        # 入場價格
        entry_price = metrics.price * (1 + metrics.bid_ask_spread / 2)
        
        # 關鍵因素
        key_factors = []
        if scoring.singularity_detected:
            key_factors.append("🔴 偵測到奇點特徵")
        if scoring.detected_breakouts:
            key_factors.append(f"📈 檢測到 {len(scoring.detected_breakouts)} 個突破信號")
        if scoring.resonance_strength > 75:
            key_factors.append("🎯 強共振對齐")
        if metrics.volume_change_ratio > 2.5:
            key_factors.append("📊 成交量大幅增加")
        
        # 風險因素
        risk_factors = []
        if scoring.risk_level == "high":
            risk_factors.append("⚠️ 高風險等級")
        if metrics.bid_ask_spread > 0.05:
            risk_factors.append("💔 價差較寬")
        if metrics.top_10_liquidity < 1000000:
            risk_factors.append("🚨 流動性不足")
        
        return CoinOpportunity(
            coin_id=metrics.coin_id,
            timestamp=metrics.timestamp,
            scoring=scoring,
            metrics=metrics,
            recommended_action=action,
            price_target=price_target,
            stop_loss=stop_loss,
            entry_price=entry_price,
            confidence=scoring.confidence,
            key_factors=key_factors,
            risk_factors=risk_factors,
            catalysts=[]
        )


# ============================================================================
# 主測試
# ============================================================================

def generate_sample_data() -> List[MarketMetrics]:
    """生成示例市場數據"""
    coins = ["BTC", "ETH", "BNB", "XRP", "DOGE"]
    data = []
    
    for coin in coins:
        metrics = MarketMetrics(
            timestamp=datetime.now(),
            coin_id=coin,
            price=np.random.uniform(10, 50000),
            price_1h_change=np.random.uniform(-3, 5),
            price_4h_change=np.random.uniform(-2, 3),
            price_24h_change=np.random.uniform(-5, 10),
            price_7d_change=np.random.uniform(-10, 20),
            volume_24h=np.random.uniform(1e6, 1e9),
            volume_change_ratio=np.random.uniform(0.5, 4),
            volatility_1h=np.random.uniform(0.005, 0.1),
            volatility_4h=np.random.uniform(0.01, 0.08),
            volatility_24h=np.random.uniform(0.02, 0.06),
            volatility_ratio=np.random.uniform(0.3, 3),
            bid_ask_spread=np.random.uniform(0.0005, 0.1),
            orderbook_imbalance=np.random.uniform(0.5, 2),
            top_10_liquidity=np.random.uniform(100000, 5000000),
            funding_rate=np.random.uniform(-0.01, 0.01),
            funding_rate_change=np.random.uniform(-0.005, 0.005),
            rsi_1h=np.random.uniform(20, 80),
            rsi_4h=np.random.uniform(20, 80),
            macd_signal_1h=np.random.uniform(-0.1, 0.1),
            bollinger_band_position=np.random.uniform(0, 1)
        )
        data.append(metrics)
    
    return data


if __name__ == "__main__":
    # 初始化篩選器
    screener = QuantumCoinScreener()
    
    # 生成示例數據
    market_data = generate_sample_data()
    
    # 篩選幣種
    opportunities = screener.screen_coins(market_data, min_score=70)
    
    # 顯示結果
    print("\n" + "="*80)
    print("               🎯 量子共振突破幣種篩選結果")
    print("="*80)
    
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"\n#{i} {opp.coin_id}")
        print(f"   綜合評分: {opp.scoring.composite_score:.1f}/100")
        print(f"   突破概率: {opp.scoring.breakout_probability:.1%}")
        print(f"   推薦行動: {opp.recommended_action.upper()}")
        print(f"   置信度: {opp.confidence:.1%}")
        print(f"   入場: ${opp.entry_price:.2f} | 目標: ${opp.price_target:.2f} | 止損: ${opp.stop_loss:.2f}")
        
        if opp.key_factors:
            print(f"   關鍵因素: {' | '.join(opp.key_factors)}")
        if opp.risk_factors:
            print(f"   風險因素: {' | '.join(opp.risk_factors)}")
    
    print("\n" + "="*80)
