"""
================================================================================
 金融大鰐聯同神性絕對超越完全體混合版神級 SDK (增研版)
================================================================================
 本檔案整合：
   - 市場狀態機 (10 種相態)
   - 森林增強分析器 (RandomForest + IsolationForest)
   - 五力奇點偵測器 (SingularityDetector)
   - 高階交易系統 (AdvancedTradingSystem)
   - Dash 即時監控儀表板
 每一區塊皆附「增研註釋」，解釋為什麼這樣設計、如何調參、數學意涵。

 作者: Singularity Quant Lab
 版本: 2026.05 完全體
"""

import numpy as np
import pandas as pd
import talib
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta
import json
from functools import lru_cache
import ccxt
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# 設定繪圖風格
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# ============================================================================
# 第一部分：市場狀態枚舉
# 增研：傳統策略只分趨勢/盤整，我們將市場分解為 10 種「相態」，
#       允許部位管理針對不同相態採用不同風險參數。
# ============================================================================

class MarketRegime(Enum):
    """市場狀態枚舉
    
    設計哲學:
    - 市場不是只有漲跌，而是存在多種「情緒溫度」。
    - SINGULARITY 是新增的非線性極端狀態，當奇點概率 > 0.7 時自動觸發，
      此時傳統技術分析失效，需降低部位或避險。
    """
    BULL_TREND = "牛市趨勢"         # ADX > 25, +DI > -DI, 價格 > SMA50
    BEAR_TREND = "熊市趨勢"         # ADX > 25, -DI > +DI, 價格 < SMA50
    RANGING = "震盪區間"            # ADX < 20, 布林帶收窄
    HIGH_VOLATILITY = "高波動性"    # ATR/價格 > 歷史80百分位
    LOW_VOLATILITY = "低波動性"     # ATR/價格 < 歷史20百分位
    BREAKOUT = "突破"               # 價格突破布林帶上軌 + 成交量放大1.5倍
    REVERSAL = "反轉"               # RSI背離 + 吞噬型態
    CRASH = "崩盤"                  # 日內跌幅 > 5% 且成交量暴增
    RALLY = "強勢上漲"              # 日內漲幅 > 5% 且成交量暴增
    SINGULARITY = "奇點區域"        # 奇點概率 > 0.7 (覆蓋其他狀態)


class SignalStrength(Enum):
    """信號強度枚舉
    
    信心區間對應強度:
        VERY_WEAK  (0.2) : 0.5~0.6
        WEAK       (0.4) : 0.6~0.7
        NEUTRAL    (0.6) : 0.7~0.8 (此「中性」指的是強度中等，非方向)
        STRONG     (0.8) : 0.8~0.9
        VERY_STRONG(1.0) : 0.9~1.0
    強度可作為後續資金管理乘數，例如 VERY_STRONG 信號允許放大 1.2 倍風險。
    """
    VERY_WEAK = 0.2
    WEAK = 0.4
    NEUTRAL = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0


# ============================================================================
# 第二部分：交易信號資料類
# 增研：使用 dataclass 保證資料完整性，to_dict 方便序列化至資料庫/API。
# ============================================================================

@dataclass
class TradingSignal:
    """交易信號資料類
    
    每個欄位都包含該信號的完整生命週期資訊，從生成到出場。
    """
    symbol: str
    timeframe: str
    signal_type: str  # BUY or SELL
    strength: SignalStrength
    confidence: float  # 0-1
    indicators: Dict[str, Any]  # 完整技術分析，供覆盤與除錯
    price: float
    timestamp: pd.Timestamp
    target_prices: Dict[str, float]  # target1, target2
    stop_loss: float
    risk_reward_ratio: float
    recommended_position: float  # 建議倉位比例 (0~1)
    market_regime: MarketRegime
    singularity_probability: float  # 來自奇點偵測器
    forest_confidence: float  # 來自森林模型
    time_to_expiry: Optional[timedelta] = None  # 若為選擇權信號
    expected_move: Optional[float] = None        # 預期波動幅度

    def to_dict(self):
        """轉換為字典，方便 JSON 輸出"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'signal_type': self.signal_type,
            'strength': self.strength.value,
            'confidence': self.confidence,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'target_prices': self.target_prices,
            'stop_loss': self.stop_loss,
            'risk_reward_ratio': self.risk_reward_ratio,
            'recommended_position': self.recommended_position,
            'market_regime': self.market_regime.value,
            'singularity_probability': self.singularity_probability,
            'forest_confidence': self.forest_confidence,
            'time_to_expiry': self.time_to_expiry.total_seconds() if self.time_to_expiry else None,
            'expected_move': self.expected_move
        }


# ============================================================================
# 第三部分：森林增強分析器 (ForestEnhancedAnalyzer)
# 增研：雙森林架構 — 隨機森林預測方向，孤立森林檢測異常，
#       兩者結合提供「方向信心」與「市場異常度」。
# ============================================================================

class ForestEnhancedAnalyzer:
    """森林增強分析器
    
    核心思維：
    - RandomForest：學習特徵→未來N期漲跌，提供 predict_proba 的信心值。
    - IsolationForest：計算每個樣本的異常分數，用 sigmoid 轉換為「奇點輔助概率」。
      當市場出現前所未見的特徵組合時，異常分數會顯著下降（越負越異常）。
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            oob_score=True,           # 使用 OOB 作為泛化能力參考
            class_weight='balanced'   # 處理不平衡標籤
        )
        # contamination=0.1 表示預期 10% 的樣本為異常，可根據市場調整
        self.anomaly_detector = IsolationForest(
            n_estimators=n_estimators,
            random_state=random_state,
            contamination=0.1
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        特徵工程：
        - 價格動量、波動率、振幅
        - RSI(14)、MACD差值
        - SMA20/50 比率 (均線排列)
        - 成交量比率、OBV 及其均線比 (量價配合)
        - ATR 及 ATR/價格 (波動歸一化)
        全部特徵經過 StandardScaler 標準化，確保森林不受尺度影響。
        """
        features = pd.DataFrame()

        # 價格特徵
        features['returns'] = data['close'].pct_change()
        features['volatility'] = data['close'].rolling(20).std() / data['close'].rolling(20).mean()
        features['high_low_ratio'] = data['high'] / data['low']

        # 技術指標特徵
        features['rsi'] = talib.RSI(data['close'], timeperiod=14)
        macd, macd_signal, _ = talib.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        features['macd_diff'] = macd - macd_signal

        # 移動平均特徵
        features['sma_20'] = talib.SMA(data['close'], timeperiod=20)
        features['sma_50'] = talib.SMA(data['close'], timeperiod=50)
        features['sma_ratio'] = features['sma_20'] / features['sma_50'] - 1

        # 成交量特徵
        features['volume_ma_ratio'] = data['volume'] / talib.SMA(data['volume'], timeperiod=20)
        features['obv'] = talib.OBV(data['close'], data['volume'])
        features['obv_ma_ratio'] = features['obv'] / talib.SMA(features['obv'], timeperiod=20)

        # 波動性特徵
        features['atr'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
        features['atr_ratio'] = features['atr'] / data['close']

        features = features.dropna()
        return features

    def prepare_labels(self, data: pd.DataFrame, forward_periods: int = 5) -> pd.Series:
        """
        標籤：未來 5 根 K 線的漲跌 (分類，非迴歸)
        使用二元分類可避免迴歸雜訊，且實務上只要方向正確就能獲利。
        """
        future_returns = data['close'].pct_change(forward_periods).shift(-forward_periods)
        labels = (future_returns > 0).astype(int)
        labels = labels[~labels.isna()]
        return labels

    def train(self, data: pd.DataFrame):
        """訓練雙森林模型"""
        features = self.prepare_features(data)
        labels = self.prepare_labels(data)

        # 對齊時間索引
        aligned_index = features.index.intersection(labels.index)
        features = features.loc[aligned_index]
        labels = labels.loc[aligned_index]

        # 標準化
        scaled_features = self.scaler.fit_transform(features)

        # 訓練分類器
        self.classifier.fit(scaled_features, labels)

        # 訓練異常檢測器
        self.anomaly_detector.fit(scaled_features)

        self.is_trained = True
        self.feature_importances_ = pd.Series(
            self.classifier.feature_importances_,
            index=features.columns
        ).sort_values(ascending=False)

        return self

    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        預測輸出：
        - direction: 1 (看漲) 或 -1 (看跌)
        - confidence: 方向的最大機率
        - singularity_prob: 來自異常分數的輔助奇點概率 (sigmoid 轉換)
        - feature_importances: 特徵重要性 (供儀表板展示)

        sigmoid 轉換公式：
            singularity_prob = 1 / (1 + exp(-anomaly_score * 10))
        其中 anomaly_score 為 score_samples 輸出 (越小越異常)。
        乘以 10 是經驗尺度因子，使分數在 -0.5~0 之間時概率約 0.01~0.5。
        """
        if not self.is_trained:
            raise ValueError("模型尚未訓練")

        features = self.prepare_features(data)
        if features.empty:
            return {"direction": 0, "confidence": 0, "singularity_prob": 0}

        latest_features = features.iloc[-1:].copy()
        scaled = self.scaler.transform(latest_features)

        # 方向預測
        direction_proba = self.classifier.predict_proba(scaled)[0]
        predicted_class = self.classifier.predict(scaled)[0]
        confidence = max(direction_proba)

        # 異常分數 → 奇點輔助概率
        anomaly_score = self.anomaly_detector.score_samples(scaled)[0]
        singularity_prob = 1 / (1 + np.exp(-anomaly_score * 10))  # 調整斜率

        return {
            "direction": 1 if predicted_class == 1 else -1,
            "confidence": confidence,
            "singularity_prob": singularity_prob,
            "feature_importances": self.feature_importances_
        }


# ============================================================================
# 第四部分：奇點偵測器 (SingularityDetector)
# 增研：五力模型，捕捉市場從「連續體」過渡到「奇點」的微觀信號。
#       權重設定依據特徵對極端事件的解釋力，可透過回測優化。
# ============================================================================

class SingularityDetector:
    """奇點概率檢測器
    
    五力模型：
        1. 價格加速度 (0.30) - 回報的二階差分，反映趨勢的急遽變化
        2. 波動率突破 (0.25) - ATR/價格的 Z-Score，捕捉波動驟增
        3. 成交量異常 (0.20) - 成交量 Z-Score，爆量通常是變盤前兆
        4. 情緒極端   (0.15) - RSI 與威廉指標的極端化程度
        5. 流動性衝擊 (0.10) - 高低價差的異常擴大，反映流動性枯竭

    各分量經 sigmoid 或直接歸一化至 0~1，加權後再經 sigmoid 壓縮，
    確保輸出為合理概率值。

    調校建議：
        - 若奇點信號太頻繁，提高閾值 (0.7→0.8) 或降低權重。
        - 加密貨幣市場應增加資金費率、清算量等維度。
    """

    def __init__(self):
        self.history = []
        self.singularity_threshold = 0.7

    def detect_singularity(self, market_data: pd.DataFrame,
                          technical_indicators: Dict[str, Any]) -> float:
        """計算最終奇點概率 (0~1)"""
        price_acceleration = self._calculate_price_acceleration(market_data)
        volatility_breakout = self._detect_volatility_breakout(market_data)
        volume_anomaly = self._detect_volume_anomaly(market_data)
        sentiment_extreme = self._detect_sentiment_extreme(technical_indicators)
        liquidity_shock = self._detect_liquidity_shock(market_data)

        # 加權合成 (可根據市場調整)
        singularity_score = (
            price_acceleration * 0.30 +
            volatility_breakout * 0.25 +
            volume_anomaly * 0.20 +
            sentiment_extreme * 0.15 +
            liquidity_shock * 0.10
        )

        # sigmoid 轉換，中心偏移 0.5 使中性分數對應 0.5 概率
        singularity_prob = 1 / (1 + np.exp(-10 * (singularity_score - 0.5)))

        # 紀錄歷史 (供儀表板繪製)
        self.history.append({
            'timestamp': pd.Timestamp.now(),
            'score': singularity_score,
            'probability': singularity_prob,
            'components': {
                'price_acceleration': price_acceleration,
                'volatility_breakout': volatility_breakout,
                'volume_anomaly': volume_anomaly,
                'sentiment_extreme': sentiment_extreme,
                'liquidity_shock': liquidity_shock
            }
        })

        return singularity_prob

    def _calculate_price_acceleration(self, data: pd.DataFrame) -> float:
        """價格加速度：回報的差分取絕對值，標準化後 sigmoid"""
        returns = data['close'].pct_change()
        acceleration = returns.diff().abs()
        if acceleration.std() > 0:
            normalized = (acceleration - acceleration.mean()) / acceleration.std()
        else:
            normalized = acceleration * 0
        return 1 / (1 + np.exp(-normalized.iloc[-1]))

    def _detect_volatility_breakout(self, data: pd.DataFrame) -> float:
        """波動率突破：ATR/價格比率的 Z-Score"""
        atr = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
        vol_ratio = atr / data['close']
        if len(vol_ratio) > 20:
            vol_mean = vol_ratio.rolling(20).mean()
            vol_std = vol_ratio.rolling(20).std()
            if vol_std.iloc[-1] > 0:
                z = (vol_ratio.iloc[-1] - vol_mean.iloc[-1]) / vol_std.iloc[-1]
                return 1 / (1 + np.exp(-z))
        return 0.5

    def _detect_volume_anomaly(self, data: pd.DataFrame) -> float:
        """成交量異常：成交量 Z-Score"""
        volume = data['volume']
        if len(volume) > 20:
            vol_mean = volume.rolling(20).mean()
            vol_std = volume.rolling(20).std()
            if vol_std.iloc[-1] > 0:
                z = (volume.iloc[-1] - vol_mean.iloc[-1]) / vol_std.iloc[-1]
                return 1 / (1 + np.exp(-z))
        return 0.5

    def _detect_sentiment_extreme(self, indicators: Dict[str, Any]) -> float:
        """情緒極端：RSI 和 Williams %R 的極端程度平均"""
        rsi = indicators.get('rsi', 50)
        willr = indicators.get('willr', -50)
        rsi_extreme = abs(rsi - 50) / 50
        willr_extreme = abs(willr + 50) / 50
        return (rsi_extreme + willr_extreme) / 2

    def _detect_liquidity_shock(self, data: pd.DataFrame) -> float:
        """流動性衝擊：高低價差比率偏離均值的程度"""
        spread = data['high'] - data['low']
        spread_ratio = spread / data['close']
        if len(spread_ratio) > 20:
            spread_mean = spread_ratio.rolling(20).mean()
            spread_std = spread_ratio.rolling(20).std()
            if spread_std.iloc[-1] > 0:
                z = (spread_ratio.iloc[-1] - spread_mean.iloc[-1]) / spread_std.iloc[-1]
                return 1 / (1 + np.exp(-z))
        return 0.5


# ============================================================================
# 第五部分：多時間框架分析器與風險管理器 (簡化實現)
# 增研：這兩個類在原碼中依賴但未完全給出，此處提供最小可行版本，
#       使用者可自行擴展為真實邏輯。
# ============================================================================

class MultiTimeframeAnalyzer:
    """
    多時間框架分析器 (模擬版)
    實戰中應分別計算 1h/4h/1d/1w 的趨勢、動量、波動、成交量指標，
    並合成一個綜合分數 composite_score (-1~1)。
    """
    def analyze_multiple_timeframes(self, ohlc_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        返回格式需包含:
        - market_regime: MarketRegime
        - composite_score: float
        - timeframe_analysis: dict of timeframes
        """
        # 簡易模擬：直接使用 1h 數據計算一些指標
        df = ohlc_data.get('1h', pd.DataFrame())
        if df.empty:
            return {'market_regime': MarketRegime.RANGING, 'composite_score': 0.0,
                    'timeframe_analysis': {'1h': {'price': 0.0, 'volatility': {'volatility': 0.0, 'atr': 0.0},
                                                  'trend': {'strength': 0.0}, 'momentum': {'rsi': 50, 'willr': -50}}}}

        close = df['close']
        rsi = talib.RSI(close, timeperiod=14).iloc[-1]
        willr = talib.WILLR(df['high'], df['low'], close, timeperiod=14).iloc[-1]
        atr = talib.ATR(df['high'], df['low'], close, timeperiod=14).iloc[-1]
        sma20 = talib.SMA(close, timeperiod=20).iloc[-1]
        sma50 = talib.SMA(close, timeperiod=50).iloc[-1]

        price = close.iloc[-1]
        volatility = close.pct_change().std()

        # 簡單的趨勢判斷
        if sma20 > sma50:
            trend_strength = min(1.0, (sma20/sma50 - 1) * 10)
            regime = MarketRegime.BULL_TREND
            composite = 0.6
        else:
            trend_strength = max(-1.0, (sma20/sma50 - 1) * 10)
            regime = MarketRegime.BEAR_TREND
            composite = -0.6

        return {
            'market_regime': regime,
            'composite_score': composite,
            'timeframe_analysis': {
                '1h': {
                    'price': price,
                    'volatility': {'volatility': volatility, 'atr': atr},
                    'trend': {'strength': trend_strength},
                    'momentum': {'rsi': rsi, 'willr': willr}
                }
            }
        }


class AdvancedRiskManager:
    """
    進階風險管理器 (模擬版)
    提供動態止損與倉位計算。
    實戰中可整合最大回撤控制、凱利公式、VaR 等。
    """
    def __init__(self, capital: float):
        self.capital = capital

    def calculate_dynamic_stop_loss(self, price: float, volatility: float,
                                    trend_strength: float, atr: float) -> float:
        """
        止損 = 入場價 - (ATR * 2 + volatility * price * 0.5)
        趨勢強度可微調，強趨勢可放寬止損。
        """
        buffer = atr * 2 + volatility * price * 0.5
        return price - buffer

    def calculate_position_size(self, price: float, stop_loss: float,
                                confidence: float, volatility: float) -> float:
        """
        建議倉位比例 (0~1)
        基礎風險資金 = 資本 * 0.02 (2% rule)
        合約張數 = 基礎風險資金 / (入場價 - 止損)
        再乘以 confidence 調整。
        """
        risk_per_trade = self.capital * 0.02
        risk_per_unit = abs(price - stop_loss)
        if risk_per_unit == 0:
            return 0.0
        size = risk_per_trade / risk_per_unit
        max_size = self.capital / price  # 不超過全倉
        return min(size / max_size, 1.0) * confidence


# ============================================================================
# 第六部分：高階交易系統 (AdvancedTradingSystem)
# 增研：整合所有組件，包含森林訓練、市場分析、信號生成。
# ============================================================================

class AdvancedTradingSystem:
    """高級交易系統
    
    生命週期:
    1. 初始化 -> train_forest_model(歷史數據) -> analyze_market(實時數據)
    2. 每次呼叫 analyze_market 返回完整分析結果與信號列表。
    """

    def __init__(self, initial_capital: float = 10000):
        self.capital = initial_capital
        self.analyzer = MultiTimeframeAnalyzer()
        self.forest_analyzer = ForestEnhancedAnalyzer()
        self.singularity_detector = SingularityDetector()
        self.risk_manager = AdvancedRiskManager(initial_capital)
        self.portfolio = {}
        self.trade_history = []
        self.signals = []
        self.is_forest_trained = False

    def train_forest_model(self, historical_data: pd.DataFrame):
        """訓練森林模型，完成後啟用森林分析"""
        print("訓練森林模型中...")
        self.forest_analyzer.train(historical_data)
        self.is_forest_trained = True
        print("森林模型訓練完成")
        print("特徵重要性:")
        print(self.forest_analyzer.feature_importances_)

    def analyze_market(self, ohlc_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        """市場分析主入口"""
        # 技術分析
        technical_analysis = self.analyzer.analyze_multiple_timeframes(ohlc_data)

        # 森林增強分析 (若已訓練)
        forest_analysis = {}
        if self.is_forest_trained:
            forest_result = self.forest_analyzer.predict(ohlc_data.get('1h'))
            forest_analysis = {
                'direction': forest_result['direction'],
                'confidence': forest_result['confidence'],
                'singularity_prob': forest_result['singularity_prob'],
                'feature_importances': forest_result['feature_importances'].to_dict()
            }

        # 奇點檢測 (基於 1h 數據)
        singularity_prob = self.singularity_detector.detect_singularity(
            ohlc_data.get('1h'),
            technical_analysis['timeframe_analysis']['1h']['momentum']
        )

        # 生成信號
        signals = self.generate_signals(
            technical_analysis,
            forest_analysis,
            singularity_prob,
            symbol
        )

        return {
            'technical_analysis': technical_analysis,
            'forest_analysis': forest_analysis,
            'singularity_probability': singularity_prob,
            'signals': signals,
            'timestamp': pd.Timestamp.now()
        }

    def generate_signals(self, technical_analysis: Dict[str, Any],
                        forest_analysis: Dict[str, Any],
                        singularity_prob: float,
                        symbol: str) -> List[TradingSignal]:
        """生成交易信號"""
        signals = []
        latest_price = technical_analysis['timeframe_analysis']['1h']['price']
        market_regime = technical_analysis['market_regime']

        # 奇點覆蓋市場狀態
        if singularity_prob > self.singularity_detector.singularity_threshold:
            market_regime = MarketRegime.SINGULARITY

        # 計算綜合信心
        tech_score = technical_analysis['composite_score']
        forest_conf = forest_analysis.get('confidence', 0.5) if forest_analysis else 0.5
        # 將 tech_score (約 -1~1) 映射到 0~1
        tech_confidence = (tech_score + 1) / 2
        combined_confidence = tech_confidence * 0.6 + forest_conf * 0.4 if forest_analysis else tech_confidence

        # 買入信號邏輯
        if combined_confidence > 0.6 and market_regime in [MarketRegime.BULL_TREND, MarketRegime.RALLY, MarketRegime.BREAKOUT]:
            signal = self._create_signal(
                symbol, latest_price, technical_analysis, forest_analysis,
                singularity_prob, market_regime, "BUY", combined_confidence
            )
            signals.append(signal)

        # 賣出信號邏輯 (使用負信心表示看跌強度)
        if combined_confidence < 0.4 and market_regime in [MarketRegime.BEAR_TREND, MarketRegime.CRASH, MarketRegime.REVERSAL]:
            sell_confidence = 1 - combined_confidence  # 轉為看跌信心
            signal = self._create_signal(
                symbol, latest_price, technical_analysis, forest_analysis,
                singularity_prob, market_regime, "SELL", sell_confidence
            )
            signals.append(signal)

        return signals

    def _create_signal(self, symbol: str, price: float,
                      technical_analysis: Dict[str, Any],
                      forest_analysis: Dict[str, Any],
                      singularity_prob: float,
                      market_regime: MarketRegime,
                      signal_type: str,
                      confidence: float) -> TradingSignal:
        """建立具體信號物件"""
        tf_1h = technical_analysis['timeframe_analysis']['1h']
        vol = tf_1h['volatility']['volatility']
        atr = tf_1h['volatility']['atr']
        trend_str = tf_1h['trend']['strength']

        stop_loss = self.risk_manager.calculate_dynamic_stop_loss(price, vol, trend_str, atr)
        risk = abs(price - stop_loss)
        reward = risk * 3  # 預設 1:3
        risk_reward = reward / risk

        position_size = self.risk_manager.calculate_position_size(price, stop_loss, confidence, vol)

        # 奇點衰減
        if singularity_prob > 0.7:
            position_size *= (1 - singularity_prob)

        # 訊號強度
        if confidence > 0.9:
            strength = SignalStrength.VERY_STRONG
        elif confidence > 0.8:
            strength = SignalStrength.STRONG
        elif confidence > 0.7:
            strength = SignalStrength.NEUTRAL
        elif confidence > 0.6:
            strength = SignalStrength.WEAK
        else:
            strength = SignalStrength.VERY_WEAK

        return TradingSignal(
            symbol=symbol,
            timeframe='multiple',
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            indicators=technical_analysis,
            price=price,
            timestamp=pd.Timestamp.now(),
            target_prices={'target1': price + reward, 'target2': price + reward * 1.5},
            stop_loss=stop_loss,
            risk_reward_ratio=risk_reward,
            recommended_position=position_size,
            market_regime=market_regime,
            singularity_probability=singularity_prob,
            forest_confidence=forest_analysis.get('confidence', 0) if forest_analysis else 0
        )


# ============================================================================
# 第七部分：Dash 儀表板
# 增研：視覺化駕駛艙，即時呈現所有分析結果。
# ============================================================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 為了讓儀表板能存取交易系統，我們將其儲存在 Flask app.config 中
app.server.config['TRADING_SYSTEM'] = None


EXCHANGE_FACTORIES = {
    'bitget': ccxt.bitget,
    'okx': ccxt.okx,
    'binance': ccxt.binance,
    'bybit': ccxt.bybit,
}

ALL_EXCHANGES = tuple(EXCHANGE_FACTORIES.keys())
ALL_MARKET_TYPES = ('spot', 'swap', 'future')


@lru_cache(maxsize=16)
def get_exchange(exchange_name: str, market_type: str):
    """Build and cache a ccxt exchange client."""
    exchange_name = exchange_name.lower()
    if exchange_name not in EXCHANGE_FACTORIES:
        raise ValueError(f"Unsupported exchange: {exchange_name}")

    exchange = EXCHANGE_FACTORIES[exchange_name]({
        'enableRateLimit': True,
        'options': {'defaultType': market_type}
    })
    exchange.load_markets()
    return exchange


@lru_cache(maxsize=64)
def get_market_symbols(exchange_name: str, market_type: str) -> Tuple[str, ...]:
    """Return all listed symbols for an exchange market type."""
    exchange = get_exchange(exchange_name, market_type)
    symbols = sorted({
        market['symbol']
        for market in exchange.markets.values()
        if market.get('type') == market_type
    })
    return tuple(symbols)


def build_symbol_options(exchange_name: str, market_type: str) -> List[Dict[str, str]]:
    """Build dropdown options from every listed symbol."""
    exchange_names = ALL_EXCHANGES if exchange_name == 'all' else (exchange_name,)
    market_types = ALL_MARKET_TYPES if market_type == 'all' else (market_type,)

    options: List[Dict[str, str]] = []
    seen = set()
    for ex_name in exchange_names:
        for mk_type in market_types:
            for symbol in get_market_symbols(ex_name, mk_type):
                value = f"{ex_name}|{mk_type}|{symbol}"
                if value in seen:
                    continue
                seen.add(value)
                options.append({
                    'label': f"{symbol} [{ex_name} {mk_type}]",
                    'value': value,
                })
    return options


def get_default_symbol(exchange_name: str, market_type: str) -> Optional[str]:
    """Return the first available symbol for startup defaults."""
    symbols = get_market_symbols(exchange_name, market_type)
    return f"{exchange_name}|{market_type}|{symbols[0]}" if symbols else None


def parse_market_selection(selection: Optional[str], fallback_exchange: str = 'bitget', fallback_market_type: str = 'spot') -> Tuple[str, str, str]:
    """Parse an encoded selector value into exchange, market type, and symbol."""
    if not selection:
        symbol = get_default_symbol(fallback_exchange, fallback_market_type) or f"{fallback_exchange}|{fallback_market_type}|BTC/USDT"
        parts = symbol.split('|', 2)
        return parts[0], parts[1], parts[2]

    parts = selection.split('|', 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid market selection: {selection}")
    return parts[0], parts[1], parts[2]


def normalize_market_symbol(symbol: str) -> str:
    """Normalize a user-entered symbol into a ccxt-friendly market string."""
    symbol = symbol.strip().upper().replace('-', '/').replace('_', '/')
    if '/' in symbol:
        return symbol

    suffixes = ['USDT', 'USDC', 'USD', 'BTC', 'ETH', 'EUR', 'JPY']
    for suffix in suffixes:
        if symbol.endswith(suffix) and len(symbol) > len(suffix):
            return f"{symbol[:-len(suffix)]}/{suffix}"
    return symbol


def resolve_market_symbol(exchange, symbol: str, market_type: str) -> str:
    """Resolve a free-form symbol to an exchange market symbol."""
    normalized = normalize_market_symbol(symbol)
    markets = exchange.markets

    if normalized in markets and markets[normalized].get('type') == market_type:
        return normalized

    candidates = []
    if '/' in normalized:
        base, quote = normalized.split('/', 1)
        quote = quote.split(':', 1)[0]
        for market in markets.values():
            if market.get('type') != market_type:
                continue
            if market.get('base') == base and market.get('quote') == quote:
                candidates.append(market['symbol'])
        if candidates:
            return candidates[0]
    else:
        for market in markets.values():
            if market.get('type') != market_type:
                continue
            market_id = str(market.get('id', '')).upper()
            compact = f"{market.get('base', '')}{market.get('quote', '')}".upper()
            if normalized == market_id or normalized == compact:
                candidates.append(market['symbol'])
        if candidates:
            return candidates[0]

    raise ValueError(f"{exchange.id} does not list {symbol} on {market_type}")


def fetch_market_ohlcv(exchange_name: str, market_type: str, symbol: str, timeframe: str, limit: int = 300) -> pd.DataFrame:
    """Fetch real OHLCV data from a supported exchange via ccxt."""
    exchange = get_exchange(exchange_name, market_type)
    market_symbol = resolve_market_symbol(exchange, symbol, market_type)

    ohlcv = exchange.fetch_ohlcv(market_symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('timestamp')
    return df


def fetch_any_market_ohlcv(selection: Optional[str], timeframe: str, limit: int = 300) -> pd.DataFrame:
    """Fetch OHLCV from the exact exchange/market encoded in the selection."""
    exchange_name, market_type, symbol = parse_market_selection(selection)
    return fetch_market_ohlcv(exchange_name, market_type, symbol, timeframe, limit=limit)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("森林增強與奇點概率交易系統", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='symbol-selector',
                options=[],
                value=None,
                searchable=True,
                clearable=False,
                className='mb-3'
            )
        ], width=6),
        dbc.Col([
            dcc.Dropdown(
                id='timeframe-selector',
                options=[
                    {'label': '1小時', 'value': '1h'},
                    {'label': '4小時', 'value': '4h'},
                    {'label': '日線', 'value': '1d'},
                    {'label': '周線', 'value': '1w'}
                ],
                value='1h',
                className='mb-3'
            )
        ], width=4),
        dbc.Col([
            dcc.Dropdown(
                id='exchange-selector',
                options=[
                    {'label': 'All Exchanges', 'value': 'all'},
                    {'label': 'Bitget', 'value': 'bitget'},
                    {'label': 'OKX', 'value': 'okx'},
                    {'label': 'Binance', 'value': 'binance'},
                    {'label': 'Bybit', 'value': 'bybit'},
                ],
                value='all',
                className='mb-3'
            )
        ], width=4),
        dbc.Col([
            dcc.Dropdown(
                id='market-type-selector',
                options=[
                    {'label': 'All Market Types', 'value': 'all'},
                    {'label': 'Spot', 'value': 'spot'},
                    {'label': 'Swap / Perp', 'value': 'swap'},
                    {'label': 'Future', 'value': 'future'},
                ],
                value='all',
                className='mb-3'
            )
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("市場狀態"),
                dbc.CardBody([
                    html.H4(id='market-regime', className="card-title"),
                    html.P(id='market-regime-desc', className="card-text")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("奇點概率"),
                dbc.CardBody([
                    html.H4(id='singularity-prob', className="card-title"),
                    dcc.Graph(id='singularity-gauge', config={'displayModeBar': False})
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("森林算法置信度"),
                dbc.CardBody([
                    html.H4(id='forest-confidence', className="card-title"),
                    dcc.Graph(id='forest-gauge', config={'displayModeBar': False})
                ])
            ])
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("交易信號"),
                dbc.CardBody([
                    html.H4(id='trade-signal', className="card-title"),
                    html.P(id='signal-details', className="card-text"),
                    dbc.Button("執行交易", id='execute-trade', color="success", className="mt-2")
                ])
            ])
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("價格圖表與技術指標"),
                dbc.CardBody([dcc.Graph(id='price-chart')])
            ])
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("特徵重要性"),
                dbc.CardBody([dcc.Graph(id='feature-importance')])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("奇點概率歷史"),
                dbc.CardBody([dcc.Graph(id='singularity-history')])
            ])
        ], width=6)
    ]),
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)
], fluid=True)


def create_price_chart(market_data: pd.DataFrame, symbol: str, timeframe: str):
    """Create price chart from real OHLCV data."""
    market_data = market_data.tail(100)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=market_data.index,
        open=market_data['open'],
        high=market_data['high'],
        low=market_data['low'],
        close=market_data['close'],
        name='價格'
    ))
    sma20 = talib.SMA(market_data['close'], timeperiod=20)
    fig.add_trace(go.Scatter(x=market_data.index, y=sma20, name='SMA 20', line=dict(color='orange')))
    fig.update_layout(title=f"{symbol} {timeframe} 價格圖表", template="plotly_white", height=400)
    return fig


def create_feature_importance():
    """Feature importance chart from the trained forest model."""
    trading_system = app.server.config.get('TRADING_SYSTEM')
    if trading_system and trading_system.is_forest_trained:
        feature_importances = trading_system.forest_analyzer.feature_importances_
        fig = go.Figure(go.Bar(x=feature_importances.values, y=feature_importances.index, orientation='h'))
    else:
        fig = go.Figure(go.Bar(x=[1], y=['No model'], orientation='h'))
    fig.update_layout(title="森林算法特徵重要性", template="plotly_white", height=400)
    return fig


def create_singularity_history():
    """Plot singularity history from the live detector state."""
    trading_system = app.server.config.get('TRADING_SYSTEM')
    history = trading_system.singularity_detector.history if trading_system else []
    if history:
        dates = [item['timestamp'] for item in history[-50:]]
        prob = [item['probability'] for item in history[-50:]]
    else:
        dates = [pd.Timestamp.now()]
        prob = [0.0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prob, mode='lines+markers', name='奇點概率'))
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="奇點閾值")
    fig.update_layout(title="奇點概率歷史", template="plotly_white", height=400)
    return fig


def create_gauge_chart(value, title, min_val, max_val):
    """創建儀表板圖表"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, 0.3], 'color': "lightgray"},
                {'range': [0.3, 0.7], 'color': "gray"},
                {'range': [0.7, max_val], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.7
            }
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
    return fig


@app.callback(
    [Output('market-regime', 'children'),
     Output('market-regime-desc', 'children'),
     Output('singularity-prob', 'children'),
     Output('forest-confidence', 'children'),
     Output('trade-signal', 'children'),
     Output('signal-details', 'children'),
     Output('price-chart', 'figure'),
     Output('feature-importance', 'figure'),
     Output('singularity-history', 'figure'),
     Output('singularity-gauge', 'figure'),
     Output('forest-gauge', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('symbol-selector', 'value'),
     Input('timeframe-selector', 'value'),
     Input('exchange-selector', 'value'),
     Input('market-type-selector', 'value')]
)
def update_dashboard(n, symbol, timeframe, exchange_name, market_type):
    """
    儀表板主要回調函數。
    在生產環境中，此處應從 app.server.config 取得已訓練的 trading_system，
    並使用真實資料調用 analyze_market。以下使用模擬資料展示。
    """
    trading_system = app.server.config.get('TRADING_SYSTEM')
    try:
        resolved_exchange, resolved_market_type, resolved_symbol = parse_market_selection(symbol, exchange_name, market_type)
        market_df = fetch_market_ohlcv(resolved_exchange, resolved_market_type, resolved_symbol, timeframe, limit=300)
        ohlc_data = {timeframe: market_df, '1h': market_df}
        if trading_system is not None:
            analysis = trading_system.analyze_market(ohlc_data, symbol)
            market_regime = analysis['technical_analysis']['market_regime'].value
            regime_desc = f"{resolved_exchange} {resolved_market_type} {resolved_symbol} 的真實市場資料"
            singularity_prob = float(analysis['singularity_probability'])
            forest_confidence = float(analysis['forest_analysis'].get('confidence', 0.0)) if analysis['forest_analysis'] else 0.0
            signals = analysis['signals']
            trade_signal = signals[0].signal_type if signals else "觀望"
            if signals:
                s = signals[0]
                signal_details = f"建議倉位: {s.recommended_position:.2%}, 風險回報比: {s.risk_reward_ratio:.2f}, 止損: {s.stop_loss:.4f}"
            else:
                signal_details = "目前沒有符合條件的信號"
        else:
            market_regime = "未初始化"
            regime_desc = "交易系統尚未啟動"
            singularity_prob = 0.0
            forest_confidence = 0.0
            trade_signal = "無"
            signal_details = "TRADING_SYSTEM 未載入"
    except Exception as exc:
        market_regime = "資料錯誤"
        regime_desc = str(exc)
        singularity_prob = 0.0
        forest_confidence = 0.0
        trade_signal = "無"
        signal_details = str(exc)
        market_df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

    price_fig = create_price_chart(market_df, resolved_symbol, timeframe) if not market_df.empty else go.Figure()
    feature_fig = create_feature_importance()
    singularity_fig = create_singularity_history()
    singularity_gauge = create_gauge_chart(singularity_prob, "奇點概率", 0, 1)
    forest_gauge = create_gauge_chart(forest_confidence, "森林置信度", 0, 1)

    return (market_regime, regime_desc, f"{singularity_prob:.2%}",
            f"{forest_confidence:.2%}", trade_signal, signal_details,
            price_fig, feature_fig, singularity_fig, singularity_gauge, forest_gauge)


@app.callback(
    [Output('symbol-selector', 'options'),
     Output('symbol-selector', 'value')],
    [Input('exchange-selector', 'value'),
     Input('market-type-selector', 'value')]
)
def update_symbol_list(exchange_name, market_type):
    options = build_symbol_options(exchange_name, market_type)
    value = options[0]['value'] if options else None
    return options, value


# ============================================================================
# 第八部分：啟動腳本 (作為主程式時執行)
# ============================================================================
if __name__ == '__main__':
    # 建立交易系統實例
    trading_system = AdvancedTradingSystem(initial_capital=10000)
    # 下載真實歷史資料並訓練
    default_exchange = 'bitget'
    default_market_type = 'spot'
    app.server.config['DEFAULT_EXCHANGE'] = default_exchange
    app.server.config['DEFAULT_MARKET_TYPE'] = default_market_type
    default_symbol = get_default_symbol(default_exchange, default_market_type)
    default_selection = default_symbol or f"{default_exchange}|{default_market_type}|BTC/USDT"
    df = fetch_any_market_ohlcv(default_selection, '1h', limit=500)
    trading_system.train_forest_model(df)

    # 將系統存放到 Flask app.config 供儀表板回調使用
    app.server.config['TRADING_SYSTEM'] = trading_system

    # 啟動儀表板
    app.run(debug=True, port=8050)
