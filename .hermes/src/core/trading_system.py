"""
================================================================================
 金融大鰐聯同神性絕對超越完全體混合版神級 SDK (真實數據即時版)
================================================================================
 依賴：pip install numpy pandas TA-Lib scikit-learn plotly dash dash-bootstrap-components ccxt
 啟動：python trading_system.py
 瀏覽器：http://127.0.0.1:8050
================================================================================
"""

import numpy as np
import pandas as pd
import talib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import warnings
from datetime import timedelta
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import ccxt
from pathlib import Path
import gzip

warnings.filterwarnings('ignore')

# ======================== 市場狀態 & 信號強度 ========================
class MarketRegime(Enum):
    BULL_TREND = "牛市趨勢"
    BEAR_TREND = "熊市趨勢"
    RANGING = "震盪區間"
    HIGH_VOLATILITY = "高波動性"
    LOW_VOLATILITY = "低波動性"
    BREAKOUT = "突破"
    REVERSAL = "反轉"
    CRASH = "崩盤"
    RALLY = "強勢上漲"
    SINGULARITY = "奇點區域"

class SignalStrength(Enum):
    VERY_WEAK = 0.2
    WEAK = 0.4
    NEUTRAL = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0

# ======================== 交易信號資料類 ========================
@dataclass
class TradingSignal:
    symbol: str
    timeframe: str
    signal_type: str
    strength: SignalStrength
    confidence: float
    indicators: Dict[str, Any]
    price: float
    timestamp: pd.Timestamp
    target_prices: Dict[str, float]
    stop_loss: float
    risk_reward_ratio: float
    recommended_position: float
    market_regime: MarketRegime
    singularity_probability: float
    forest_confidence: float
    order_notional_usdt: float = 50.0
    attack_dimension: float = 0.5
    order_quantity: Optional[float] = None
    time_to_expiry: Optional[timedelta] = None
    expected_move: Optional[float] = None

    def to_dict(self):
        return {
            'symbol': self.symbol, 'timeframe': self.timeframe,
            'signal_type': self.signal_type, 'strength': self.strength.value,
            'confidence': self.confidence, 'price': self.price,
            'timestamp': self.timestamp.isoformat(), 'target_prices': self.target_prices,
            'stop_loss': self.stop_loss, 'risk_reward_ratio': self.risk_reward_ratio,
            'recommended_position': self.recommended_position,
            'market_regime': self.market_regime.value,
            'singularity_probability': self.singularity_probability,
            'forest_confidence': self.forest_confidence,
            'order_notional_usdt': self.order_notional_usdt,
            'attack_dimension': self.attack_dimension,
            'order_quantity': self.order_quantity,
            'time_to_expiry': self.time_to_expiry.total_seconds() if self.time_to_expiry else None,
            'expected_move': self.expected_move
        }

# ======================== 森林增強分析器 ========================
class ForestEnhancedAnalyzer:
    def __init__(self, n_estimators=100, random_state=42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators, random_state=random_state,
            oob_score=True, class_weight='balanced'
        )
        self.anomaly_detector = IsolationForest(
            n_estimators=n_estimators, random_state=random_state,
            contamination=0.1
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame()
        features['returns'] = data['close'].pct_change()
        features['volatility'] = data['close'].rolling(20).std() / data['close'].rolling(20).mean()
        features['high_low_ratio'] = data['high'] / data['low']
        features['rsi'] = talib.RSI(data['close'], timeperiod=14)
        macd, macd_signal, _ = talib.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        features['macd_diff'] = macd - macd_signal
        features['sma_20'] = talib.SMA(data['close'], timeperiod=20)
        features['sma_50'] = talib.SMA(data['close'], timeperiod=50)
        features['sma_ratio'] = features['sma_20'] / features['sma_50'] - 1
        features['volume_ma_ratio'] = data['volume'] / talib.SMA(data['volume'], timeperiod=20)
        features['obv'] = talib.OBV(data['close'], data['volume'])
        features['obv_ma_ratio'] = features['obv'] / talib.SMA(features['obv'], timeperiod=20)
        features['atr'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
        features['atr_ratio'] = features['atr'] / data['close']
        return features.dropna()

    def prepare_labels(self, data: pd.DataFrame, forward_periods=5) -> pd.Series:
        future_returns = data['close'].pct_change(forward_periods).shift(-forward_periods)
        labels = (future_returns > 0).astype(int)
        return labels.dropna()

    def train(self, data: pd.DataFrame):
        features = self.prepare_features(data)
        labels = self.prepare_labels(data)
        aligned_idx = features.index.intersection(labels.index)
        features = features.loc[aligned_idx]
        labels = labels.loc[aligned_idx]
        scaled = self.scaler.fit_transform(features)
        self.classifier.fit(scaled, labels)
        self.anomaly_detector.fit(scaled)
        self.is_trained = True
        self.feature_importances_ = pd.Series(
            self.classifier.feature_importances_, index=features.columns
        ).sort_values(ascending=False)

    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        if not self.is_trained:
            raise ValueError("模型尚未訓練")
        features = self.prepare_features(data)
        if features.empty:
            return {"direction": 0, "confidence": 0, "singularity_prob": 0}
        latest = features.iloc[-1:].copy()
        scaled = self.scaler.transform(latest)
        proba = self.classifier.predict_proba(scaled)[0]
        pred_class = self.classifier.predict(scaled)[0]
        confidence = max(proba)
        anomaly_score = self.anomaly_detector.score_samples(scaled)[0]
        singularity_prob = 1 / (1 + np.exp(-anomaly_score * 10))
        return {
            "direction": 1 if pred_class == 1 else -1,
            "confidence": confidence,
            "singularity_prob": singularity_prob,
            "feature_importances": self.feature_importances_
        }

# ======================== 奇點偵測器 ========================
class SingularityDetector:
    def __init__(self):
        self.history = []
        self.singularity_threshold = 0.7

    def detect_singularity(self, market_data: pd.DataFrame,
                          indicators: Dict[str, Any]) -> float:
        pa = self._price_acceleration(market_data)
        vb = self._volatility_breakout(market_data)
        va = self._volume_anomaly(market_data)
        se = self._sentiment_extreme(indicators)
        ls = self._liquidity_shock(market_data)
        score = pa*0.30 + vb*0.25 + va*0.20 + se*0.15 + ls*0.10
        prob = 1 / (1 + np.exp(-10*(score-0.5)))
        self.history.append({
            'timestamp': pd.Timestamp.now(), 'score': score,
            'probability': prob,
            'components': {'pa': pa, 'vb': vb, 'va': va, 'se': se, 'ls': ls}
        })
        return prob

    def _price_acceleration(self, data):
        ret = data['close'].pct_change()
        acc = ret.diff().abs()
        if acc.std() > 0:
            norm = (acc - acc.mean())/acc.std()
        else:
            norm = acc*0
        return 1/(1+np.exp(-norm.iloc[-1]))

    def _volatility_breakout(self, data):
        atr = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
        ratio = atr / data['close']
        if len(ratio)>20:
            mean = ratio.rolling(20).mean()
            std = ratio.rolling(20).std()
            if std.iloc[-1]>0:
                z = (ratio.iloc[-1]-mean.iloc[-1])/std.iloc[-1]
                return 1/(1+np.exp(-z))
        return 0.5

    def _volume_anomaly(self, data):
        vol = data['volume']
        if len(vol)>20:
            mean = vol.rolling(20).mean()
            std = vol.rolling(20).std()
            if std.iloc[-1]>0:
                z = (vol.iloc[-1]-mean.iloc[-1])/std.iloc[-1]
                return 1/(1+np.exp(-z))
        return 0.5

    def _sentiment_extreme(self, indicators):
        rsi = indicators.get('rsi', 50)
        willr = indicators.get('willr', -50)
        return (abs(rsi-50)/50 + abs(willr+50)/50)/2

    def _liquidity_shock(self, data):
        spread = data['high'] - data['low']
        ratio = spread / data['close']
        if len(ratio)>20:
            mean = ratio.rolling(20).mean()
            std = ratio.rolling(20).std()
            if std.iloc[-1]>0:
                z = (ratio.iloc[-1]-mean.iloc[-1])/std.iloc[-1]
                return 1/(1+np.exp(-z))
        return 0.5

# ======================== 多時間框架分析器 ========================
class MultiTimeframeAnalyzer:
    def analyze_multiple_timeframes(self, ohlc_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        df = ohlc_data.get('1h')
        if df is None or df.empty:
            return {'market_regime': MarketRegime.RANGING, 'composite_score': 0.0,
                    'timeframe_analysis': {'1h': {'price': 0.0,
                        'volatility': {'volatility': 0.0, 'atr': 0.0},
                        'trend': {'strength': 0.0},
                        'momentum': {'rsi': 50, 'willr': -50}}}}
        close = df['close']
        rsi = talib.RSI(close, timeperiod=14).iloc[-1]
        willr = talib.WILLR(df['high'], df['low'], close, timeperiod=14).iloc[-1]
        atr = talib.ATR(df['high'], df['low'], close, timeperiod=14).iloc[-1]
        sma20 = talib.SMA(close, timeperiod=20).iloc[-1]
        sma50 = talib.SMA(close, timeperiod=50).iloc[-1]
        price = close.iloc[-1]
        volatility = close.pct_change().std()
        if sma20 > sma50:
            trend_strength = min(1.0, (sma20/sma50-1)*10)
            regime = MarketRegime.BULL_TREND
            composite = 0.6
        else:
            trend_strength = max(-1.0, (sma20/sma50-1)*10)
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

# ======================== 風險管理器 ========================
class AdvancedRiskManager:
    def __init__(self, capital: float):
        self.capital = capital

    def calculate_dynamic_stop_loss(self, price, volatility, trend_strength, atr):
        buffer = atr*2 + volatility*price*0.5
        return price - buffer

    def calculate_position_size(self, price, stop_loss, confidence, volatility):
        risk_per_trade = self.capital * 0.02
        risk_per_unit = abs(price - stop_loss)
        if risk_per_unit == 0:
            return 0.0
        size = risk_per_trade / risk_per_unit
        max_size = self.capital / price
        return min(size/max_size, 1.0) * confidence

# ======================== 高階交易系統 ========================
class AdvancedTradingSystem:
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.default_order_notional_usdt = 50.0
        self.analyzer = MultiTimeframeAnalyzer()
        self.forest_analyzer = ForestEnhancedAnalyzer()
        self.singularity_detector = SingularityDetector()
        self.risk_manager = AdvancedRiskManager(initial_capital)
        self.is_forest_trained = False

    def train_forest_model(self, historical_data: pd.DataFrame):
        print("訓練森林模型中...")
        self.forest_analyzer.train(historical_data)
        self.is_forest_trained = True
        print("訓練完成，特徵重要性：")
        print(self.forest_analyzer.feature_importances_)

    def analyze_market(self, ohlc_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        tech = self.analyzer.analyze_multiple_timeframes(ohlc_data)
        forest_info = {}
        if self.is_forest_trained:
            forest_result = self.forest_analyzer.predict(ohlc_data.get('1h'))
            forest_info = {
                'direction': forest_result['direction'],
                'confidence': forest_result['confidence'],
                'singularity_prob': forest_result['singularity_prob'],
                'feature_importances': forest_result['feature_importances'].to_dict()
            }
        singularity_prob = self.singularity_detector.detect_singularity(
            ohlc_data['1h'],
            tech['timeframe_analysis']['1h']['momentum']
        )
        signals = self._generate_signals(tech, forest_info, singularity_prob, symbol)
        return {
            'technical_analysis': tech,
            'forest_analysis': forest_info,
            'singularity_probability': singularity_prob,
            'signals': signals,
            'timestamp': pd.Timestamp.now()
        }

    def _generate_signals(self, tech, forest_info, singularity_prob, symbol):
        signals = []
        price = tech['timeframe_analysis']['1h']['price']
        regime = tech['market_regime']
        if singularity_prob > self.singularity_detector.singularity_threshold:
            regime = MarketRegime.SINGULARITY

        tech_score = tech['composite_score']
        forest_conf = forest_info.get('confidence', 0.5) if forest_info else 0.5
        tech_confidence = (tech_score + 1)/2
        combined = tech_confidence*0.6 + forest_conf*0.4 if forest_info else tech_confidence

        if combined > 0.6 and regime in [MarketRegime.BULL_TREND, MarketRegime.RALLY, MarketRegime.BREAKOUT]:
            signals.append(self._create_signal(symbol, price, tech, forest_info, singularity_prob, regime, "BUY", combined))
        elif combined < 0.4 and regime in [MarketRegime.BEAR_TREND, MarketRegime.CRASH, MarketRegime.REVERSAL]:
            sell_conf = 1 - combined
            signals.append(self._create_signal(symbol, price, tech, forest_info, singularity_prob, regime, "SELL", sell_conf))
        return signals

    def _calculate_attack_dimension(self, confidence, singularity_prob, regime):
        attack = confidence * (1 - singularity_prob)
        if regime in [MarketRegime.BREAKOUT, MarketRegime.RALLY, MarketRegime.BULL_TREND]:
            attack += 0.15
        elif regime in [MarketRegime.CRASH, MarketRegime.BEAR_TREND, MarketRegime.REVERSAL]:
            attack -= 0.05
        return max(0.1, min(1.0, attack))

    def _create_signal(self, symbol, price, tech, forest_info, singularity_prob, regime, stype, confidence):
        tf = tech['timeframe_analysis']['1h']
        vol = tf['volatility']['volatility']
        atr = tf['volatility']['atr']
        trend_str = tf['trend']['strength']
        sl = self.risk_manager.calculate_dynamic_stop_loss(price, vol, trend_str, atr)
        risk = abs(price - sl)
        reward = risk * 3
        pos = self.risk_manager.calculate_position_size(price, sl, confidence, vol)
        attack_dimension = self._calculate_attack_dimension(confidence, singularity_prob, regime)
        order_notional_usdt = self.default_order_notional_usdt
        order_quantity = order_notional_usdt / price if price > 0 else None
        if singularity_prob > 0.7:
            pos *= (1 - singularity_prob)
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
            symbol=symbol, timeframe='multiple', signal_type=stype,
            strength=strength, confidence=confidence, indicators=tech,
            price=price, timestamp=pd.Timestamp.now(),
            target_prices={'target1': price+reward, 'target2': price+reward*1.5},
            stop_loss=sl, risk_reward_ratio=reward/risk,
            recommended_position=pos, market_regime=regime,
            singularity_probability=singularity_prob,
            forest_confidence=forest_info.get('confidence',0) if forest_info else 0,
            order_notional_usdt=order_notional_usdt,
            attack_dimension=attack_dimension,
            order_quantity=order_quantity
        )

# ======================== 交易所數據接口 ========================
exchange = ccxt.binance({
    'enableRateLimit': True,
})

SCAN_SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
    'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'TRX/USDT',
    'LINK/USDT', 'MATIC/USDT', 'LTC/USDT', 'BCH/USDT', 'ATOM/USDT',
    'ETC/USDT', 'UNI/USDT', 'NEAR/USDT', 'APT/USDT', 'ARB/USDT'
]

OFFLINE_TRAIN_LIMITS = {
    '1h': 2000,
    '4h': 1000,
    '1d': 365,
}

def get_market_symbols(limit=30):
    try:
        markets = exchange.load_markets()
        symbols = [s for s, info in markets.items() if s.endswith('/USDT') and info.get('active', True)]
        preferred = [s for s in SCAN_SYMBOLS if s in symbols]
        extras = [s for s in symbols if s not in preferred]
        return (preferred + extras)[:limit]
    except Exception as e:
        print(f"讀取交易對失敗: {e}")
        return SCAN_SYMBOLS[:limit]

def download_offline_training_pack(timeframes=None, per_symbol_limit=None, symbol_limit=20):
    timeframes = timeframes or ['1h', '4h', '1d']
    per_symbol_limit = per_symbol_limit or OFFLINE_TRAIN_LIMITS
    pack = []
    for symbol in get_market_symbols(limit=symbol_limit):
        for timeframe in timeframes:
            limit = per_symbol_limit.get(timeframe, 500)
            df = fetch_ohlcv(symbol, timeframe, limit)
            if df.empty:
                continue
            enriched = df.reset_index().copy()
            enriched.insert(0, 'symbol', symbol)
            enriched.insert(1, 'timeframe', timeframe)
            pack.append(enriched)
    if not pack:
        return pd.DataFrame()
    return pd.concat(pack, ignore_index=True)

def export_compressed_csv(df: pd.DataFrame, output_path: Path):
    if df.empty:
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    with gzip.open(output_path, 'wb') as f:
        f.write(csv_bytes)
    return True

def fetch_ohlcv(symbol='BTC/USDT', timeframe='1h', limit=2000):
    """從 Binance 拉取 OHLCV 數據並轉為 DataFrame"""
    try:
        raw = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"數據抓取失敗: {e}")
        # 若失敗則回傳空 DataFrame 避免中斷
        return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

# ======================== Dash 儀表板 ========================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 全域配置
TRADING_SYSTEM = None
FETCH_CONFIG = {
    'symbol': 'BTC/USDT',
    'timeframe': '1h',
    'live_limit': 120   # 儀表板顯示近120根K線
}

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("森林增強與奇點概率交易系統 (BTC/USDT 即時)", className="text-center mb-4"))),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='symbol-selector', options=[
            {'label': s, 'value': s} for s in SCAN_SYMBOLS
        ], value='BTC/USDT'), width=6),
        dbc.Col(dcc.Dropdown(id='timeframe-selector', options=[
            {'label': '1小時', 'value': '1h'},
            {'label': '4小時', 'value': '4h'},
            {'label': '日線', 'value': '1d'}
        ], value='1h'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("市場狀態"), dbc.CardBody(html.H4(id='market-regime'))]), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("奇點概率"), dbc.CardBody(html.H4(id='singularity-prob'))]), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("森林置信度"), dbc.CardBody(html.H4(id='forest-confidence'))]), width=4)
    ]),
    dbc.Row(dbc.Col(dbc.Card([dbc.CardHeader("交易信號"), dbc.CardBody([html.H4(id='trade-signal'), html.P(id='signal-details')])]))),
    dbc.Row(dbc.Col(dbc.Card([dbc.CardHeader("價格圖表"), dbc.CardBody(dcc.Graph(id='price-chart'))]))),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("特徵重要性"), dbc.CardBody(dcc.Graph(id='feature-importance'))]), width=6),
        dbc.Col(dbc.Card([dbc.CardHeader("奇點概率歷史"), dbc.CardBody(dcc.Graph(id='singularity-history'))]), width=6)
    ]),
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # 每分鐘更新
], fluid=True)

# ---------- 圖表輔助函數 ----------
def make_price_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='價格'
    ))
    sma = talib.SMA(df['close'], timeperiod=20)
    fig.add_trace(go.Scatter(x=df.index, y=sma, name='SMA20', line=dict(color='orange')))
    fig.update_layout(template='plotly_white', height=300)
    return fig

# ---------- 回調 ----------
@app.callback(
    [Output('market-regime','children'), Output('singularity-prob','children'),
     Output('forest-confidence','children'), Output('trade-signal','children'),
     Output('signal-details','children'), Output('price-chart','figure'),
     Output('feature-importance','figure'), Output('singularity-history','figure')],
    [Input('interval-component','n_intervals'), Input('symbol-selector','value'),
     Input('timeframe-selector','value')]
)
def update_dashboard(n, symbol, timeframe):
    if TRADING_SYSTEM is None:
        return "未訓練","0%","0%","無信號","請先訓練系統",{},{},{}

    # 從交易所拉取最新數據
    df = fetch_ohlcv(symbol, timeframe, FETCH_CONFIG['live_limit'])
    if df.empty:
        return "數據錯誤","0%","0%","錯誤","無法取得交易所數據",{},{},{}

    ohlc_data = {'1h': df}  # 系統內部使用 '1h' 作為主要分析週期

    # 分析市場
    result = TRADING_SYSTEM.analyze_market(ohlc_data, symbol)

    regime = result['technical_analysis']['market_regime'].value
    sing_prob = result['singularity_probability']
    forest_conf = result['forest_analysis'].get('confidence', 0) if result['forest_analysis'] else 0
    signals = result['signals']

    if signals:
        sig = signals[0]
        trade_signal = f"{sig.signal_type} ({sig.strength.name})"
        details = (
            f"信心:{sig.confidence:.2%} | 倉位:{sig.recommended_position:.2%} | "
            f"下單:{sig.order_notional_usdt:.0f}USDT | 數量:{sig.order_quantity:.6f} | "
            f"攻擊:{sig.attack_dimension:.2f} | 止損:{sig.stop_loss:.2f}"
        )
    else:
        trade_signal = "無信號"
        details = "等待條件符合"

    # 圖表
    price_fig = make_price_chart(df)

    # 特徵重要性
    feat_imp = result['forest_analysis'].get('feature_importances', {})
    if feat_imp:
        imp_df = pd.DataFrame({'feature': list(feat_imp.keys()), 'importance': list(feat_imp.values())})
        imp_df = imp_df.sort_values('importance')
        feat_fig = go.Figure(go.Bar(x=imp_df['importance'], y=imp_df['feature'], orientation='h'))
    else:
        feat_fig = go.Figure()
    feat_fig.update_layout(title="特徵重要性", template='plotly_white', height=300)

    # 奇點歷史
    hist = TRADING_SYSTEM.singularity_detector.history
    if hist:
        hist_df = pd.DataFrame(hist)
        sing_fig = go.Figure()
        sing_fig.add_trace(go.Scatter(x=hist_df['timestamp'], y=hist_df['probability'], mode='lines+markers'))
        sing_fig.add_hline(y=0.7, line_dash='dash', line_color='red')
    else:
        sing_fig = go.Figure()
    sing_fig.update_layout(title="奇點概率歷史", template='plotly_white', height=300)

    return (regime, f"{sing_prob:.2%}", f"{forest_conf:.2%}",
            trade_signal, details, price_fig, feat_fig, sing_fig)

# ======================== 啟動 ========================
if __name__ == '__main__':
    print("正在從 Binance 下載歷史數據以訓練森林模型...")
    offline_dir = Path('.hermes/output/offline_training')
    offline_dir.mkdir(parents=True, exist_ok=True)

    offline_pack = download_offline_training_pack(timeframes=['1h', '4h', '1d'], symbol_limit=20)
    if not offline_pack.empty:
        offline_csv = offline_dir / 'training_pack.csv'
        offline_gz = offline_dir / 'training_pack.csv.gz'
        offline_pack.to_csv(offline_csv, index=False)
        export_compressed_csv(offline_pack, offline_gz)
        print(f"已輸出離線訓練包: {offline_csv}")
        print(f"已輸出壓縮訓練包: {offline_gz}")

    # 訓練用 2000 根 1 小時 K 線
    train_df = fetch_ohlcv('BTC/USDT', '1h', 2000)
    if train_df.empty:
        print("無法獲取訓練數據，請檢查網路連線")
        exit()

    TRADING_SYSTEM = AdvancedTradingSystem(initial_capital=10000)
    TRADING_SYSTEM.train_forest_model(train_df)

    scan_rows = []
    for symbol in get_market_symbols(limit=50):
        live_df = fetch_ohlcv(symbol, '1h', FETCH_CONFIG['live_limit'])
        if live_df.empty:
            continue
        result = TRADING_SYSTEM.analyze_market({'1h': live_df}, symbol)
        signal = result['signals'][0] if result['signals'] else None
        scan_rows.append({
            'symbol': symbol,
            'market_regime': result['technical_analysis']['market_regime'].value,
            'singularity_probability': result['singularity_probability'],
            'forest_confidence': result['forest_analysis'].get('confidence', 0),
            'signal_type': signal.signal_type if signal else '',
            'signal_confidence': signal.confidence if signal else 0,
            'order_notional_usdt': signal.order_notional_usdt if signal else 50.0,
            'attack_dimension': signal.attack_dimension if signal else 0,
            'order_quantity': signal.order_quantity if signal else None,
        })

    output_dir = Path('.hermes/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    scan_df = pd.DataFrame(scan_rows)
    scan_csv = output_dir / 'trading_scan.csv'
    if not scan_df.empty:
        scan_df.to_csv(scan_csv, index=False)
        print(f"已輸出掃描 CSV: {scan_csv}")
    else:
        print("掃描未產生可輸出資料")

    print("啟動儀表板，請打開 http://127.0.0.1:8050")
    app.run(debug=True, port=8050)
import dash_bootstrap_components as dbc
import ccxt

warnings.filterwarnings('ignore')

# ======================== 市場狀態 & 信號強度 ========================
class MarketRegime(Enum):
    BULL_TREND = "牛市趨勢"
    BEAR_TREND = "熊市趨勢"
    RANGING = "震盪區間"
    HIGH_VOLATILITY = "高波動性"
    LOW_VOLATILITY = "低波動性"
    BREAKOUT = "突破"
    REVERSAL = "反轉"
    CRASH = "崩盤"
    RALLY = "強勢上漲"
    SINGULARITY = "奇點區域"

class SignalStrength(Enum):
    VERY_WEAK = 0.2
    WEAK = 0.4
    NEUTRAL = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0

# ======================== 交易信號資料類 ========================
@dataclass
class TradingSignal:
    symbol: str
    timeframe: str
    signal_type: str
    strength: SignalStrength
    confidence: float
    indicators: Dict[str, Any]
    price: float
    timestamp: pd.Timestamp
    target_prices: Dict[str, float]
    stop_loss: float
    risk_reward_ratio: float
    recommended_position: float
    market_regime: MarketRegime
    singularity_probability: float
    forest_confidence: float
    time_to_expiry: Optional[timedelta] = None
    expected_move: Optional[float] = None

    def to_dict(self):
        return {
            'symbol': self.symbol, 'timeframe': self.timeframe,
            'signal_type': self.signal_type, 'strength': self.strength.value,
            'confidence': self.confidence, 'price': self.price,
            'timestamp': self.timestamp.isoformat(), 'target_prices': self.target_prices,
            'stop_loss': self.stop_loss, 'risk_reward_ratio': self.risk_reward_ratio,
            'recommended_position': self.recommended_position,
            'market_regime': self.market_regime.value,
            'singularity_probability': self.singularity_probability,
            'forest_confidence': self.forest_confidence,
            'time_to_expiry': self.time_to_expiry.total_seconds() if self.time_to_expiry else None,
            'expected_move': self.expected_move
        }

# ======================== 森林增強分析器 ========================
class ForestEnhancedAnalyzer:
    def __init__(self, n_estimators=100, random_state=42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators, random_state=random_state,
            oob_score=True, class_weight='balanced'
        )
        self.anomaly_detector = IsolationForest(
            n_estimators=n_estimators, random_state=random_state,
            contamination=0.1
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame()
        features['returns'] = data['close'].pct_change()
        features['volatility'] = data['close'].rolling(20).std() / data['close'].rolling(20).mean()
        features['high_low_ratio'] = data['high'] / data['low']
        features['rsi'] = talib.RSI(data['close'], timeperiod=14)
        macd, macd_signal, _ = talib.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        features['macd_diff'] = macd - macd_signal
        features['sma_20'] = talib.SMA(data['close'], timeperiod=20)
        features['sma_50'] = talib.SMA(data['close'], timeperiod=50)
        features['sma_ratio'] = features['sma_20'] / features['sma_50'] - 1
        features['volume_ma_ratio'] = data['volume'] / talib.SMA(data['volume'], timeperiod=20)
        features['obv'] = talib.OBV(data['close'], data['volume'])
        features['obv_ma_ratio'] = features['obv'] / talib.SMA(features['obv'], timeperiod=20)
        features['atr'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
        features['atr_ratio'] = features['atr'] / data['close']
        return features.dropna()

    def prepare_labels(self, data: pd.DataFrame, forward_periods=5) -> pd.Series:
        future_returns = data['close'].pct_change(forward_periods).shift(-forward_periods)
        labels = (future_returns > 0).astype(int)
        return labels.dropna()

    def train(self, data: pd.DataFrame):
        features = self.prepare_features(data)
        labels = self.prepare_labels(data)
        aligned_idx = features.index.intersection(labels.index)
        features = features.loc[aligned_idx]
        labels = labels.loc[aligned_idx]
        scaled = self.scaler.fit_transform(features)
        self.classifier.fit(scaled, labels)
        self.anomaly_detector.fit(scaled)
        self.is_trained = True
        self.feature_importances_ = pd.Series(
            self.classifier.feature_importances_, index=features.columns
        ).sort_values(ascending=False)

    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        if not self.is_trained:
            raise ValueError("模型尚未訓練")
        features = self.prepare_features(data)
        if features.empty:
            return {"direction": 0, "confidence": 0, "singularity_prob": 0}
        latest = features.iloc[-1:].copy()
        scaled = self.scaler.transform(latest)
        proba = self.classifier.predict_proba(scaled)[0]
        pred_class = self.classifier.predict(scaled)[0]
        confidence = max(proba)
        anomaly_score = self.anomaly_detector.score_samples(scaled)[0]
        singularity_prob = 1 / (1 + np.exp(-anomaly_score * 10))
        return {
            "direction": 1 if pred_class == 1 else -1,
            "confidence": confidence,
            "singularity_prob": singularity_prob,
            "feature_importances": self.feature_importances_
        }

# ======================== 奇點偵測器 ========================
class SingularityDetector:
    def __init__(self):
        self.history = []
        self.singularity_threshold = 0.7

    def detect_singularity(self, market_data: pd.DataFrame,
                          indicators: Dict[str, Any]) -> float:
        pa = self._price_acceleration(market_data)
        vb = self._volatility_breakout(market_data)
        va = self._volume_anomaly(market_data)
        se = self._sentiment_extreme(indicators)
        ls = self._liquidity_shock(market_data)
        score = pa*0.30 + vb*0.25 + va*0.20 + se*0.15 + ls*0.10
        prob = 1 / (1 + np.exp(-10*(score-0.5)))
        self.history.append({
            'timestamp': pd.Timestamp.now(), 'score': score,
            'probability': prob,
            'components': {'pa': pa, 'vb': vb, 'va': va, 'se': se, 'ls': ls}
        })
        return prob

    def _price_acceleration(self, data):
        ret = data['close'].pct_change()
        acc = ret.diff().abs()
        if acc.std() > 0:
            norm = (acc - acc.mean())/acc.std()
        else:
            norm = acc*0
        return 1/(1+np.exp(-norm.iloc[-1]))

    def _volatility_breakout(self, data):
        atr = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
        ratio = atr / data['close']
        if len(ratio)>20:
            mean = ratio.rolling(20).mean()
            std = ratio.rolling(20).std()
            if std.iloc[-1]>0:
                z = (ratio.iloc[-1]-mean.iloc[-1])/std.iloc[-1]
                return 1/(1+np.exp(-z))
        return 0.5

    def _volume_anomaly(self, data):
        vol = data['volume']
        if len(vol)>20:
            mean = vol.rolling(20).mean()
            std = vol.rolling(20).std()
            if std.iloc[-1]>0:
                z = (vol.iloc[-1]-mean.iloc[-1])/std.iloc[-1]
                return 1/(1+np.exp(-z))
        return 0.5

    def _sentiment_extreme(self, indicators):
        rsi = indicators.get('rsi', 50)
        willr = indicators.get('willr', -50)
        return (abs(rsi-50)/50 + abs(willr+50)/50)/2

    def _liquidity_shock(self, data):
        spread = data['high'] - data['low']
        ratio = spread / data['close']
        if len(ratio)>20:
            mean = ratio.rolling(20).mean()
            std = ratio.rolling(20).std()
            if std.iloc[-1]>0:
                z = (ratio.iloc[-1]-mean.iloc[-1])/std.iloc[-1]
                return 1/(1+np.exp(-z))
        return 0.5

# ======================== 多時間框架分析器 ========================
class MultiTimeframeAnalyzer:
    def analyze_multiple_timeframes(self, ohlc_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        df = ohlc_data.get('1h')
        if df is None or df.empty:
            return {'market_regime': MarketRegime.RANGING, 'composite_score': 0.0,
                    'timeframe_analysis': {'1h': {'price': 0.0,
                        'volatility': {'volatility': 0.0, 'atr': 0.0},
                        'trend': {'strength': 0.0},
                        'momentum': {'rsi': 50, 'willr': -50}}}}
        close = df['close']
        rsi = talib.RSI(close, timeperiod=14).iloc[-1]
        willr = talib.WILLR(df['high'], df['low'], close, timeperiod=14).iloc[-1]
        atr = talib.ATR(df['high'], df['low'], close, timeperiod=14).iloc[-1]
        sma20 = talib.SMA(close, timeperiod=20).iloc[-1]
        sma50 = talib.SMA(close, timeperiod=50).iloc[-1]
        price = close.iloc[-1]
        volatility = close.pct_change().std()
        if sma20 > sma50:
            trend_strength = min(1.0, (sma20/sma50-1)*10)
            regime = MarketRegime.BULL_TREND
            composite = 0.6
        else:
            trend_strength = max(-1.0, (sma20/sma50-1)*10)
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

# ======================== 風險管理器 ========================
class AdvancedRiskManager:
    def __init__(self, capital: float):
        self.capital = capital

    def calculate_dynamic_stop_loss(self, price, volatility, trend_strength, atr):
        buffer = atr*2 + volatility*price*0.5
        return price - buffer

    def calculate_position_size(self, price, stop_loss, confidence, volatility):
        risk_per_trade = self.capital * 0.02
        risk_per_unit = abs(price - stop_loss)
        if risk_per_unit == 0:
            return 0.0
        size = risk_per_trade / risk_per_unit
        max_size = self.capital / price
        return min(size/max_size, 1.0) * confidence

# ======================== 高階交易系統 ========================
class AdvancedTradingSystem:
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.analyzer = MultiTimeframeAnalyzer()
        self.forest_analyzer = ForestEnhancedAnalyzer()
        self.singularity_detector = SingularityDetector()
        self.risk_manager = AdvancedRiskManager(initial_capital)
        self.is_forest_trained = False

    def train_forest_model(self, historical_data: pd.DataFrame):
        print("訓練森林模型中...")
        self.forest_analyzer.train(historical_data)
        self.is_forest_trained = True
        print("訓練完成，特徵重要性：")
        print(self.forest_analyzer.feature_importances_)

    def analyze_market(self, ohlc_data: Dict[str, pd.DataFrame], symbol: str) -> Dict[str, Any]:
        tech = self.analyzer.analyze_multiple_timeframes(ohlc_data)
        forest_info = {}
        if self.is_forest_trained:
            forest_result = self.forest_analyzer.predict(ohlc_data.get('1h'))
            forest_info = {
                'direction': forest_result['direction'],
                'confidence': forest_result['confidence'],
                'singularity_prob': forest_result['singularity_prob'],
                'feature_importances': forest_result['feature_importances'].to_dict()
            }
        singularity_prob = self.singularity_detector.detect_singularity(
            ohlc_data['1h'],
            tech['timeframe_analysis']['1h']['momentum']
        )
        signals = self._generate_signals(tech, forest_info, singularity_prob, symbol)
        return {
            'technical_analysis': tech,
            'forest_analysis': forest_info,
            'singularity_probability': singularity_prob,
            'signals': signals,
            'timestamp': pd.Timestamp.now()
        }

    def _generate_signals(self, tech, forest_info, singularity_prob, symbol):
        signals = []
        price = tech['timeframe_analysis']['1h']['price']
        regime = tech['market_regime']
        if singularity_prob > self.singularity_detector.singularity_threshold:
            regime = MarketRegime.SINGULARITY

        tech_score = tech['composite_score']
        forest_conf = forest_info.get('confidence', 0.5) if forest_info else 0.5
        tech_confidence = (tech_score + 1)/2
        combined = tech_confidence*0.6 + forest_conf*0.4 if forest_info else tech_confidence

        if combined > 0.6 and regime in [MarketRegime.BULL_TREND, MarketRegime.RALLY, MarketRegime.BREAKOUT]:
            signals.append(self._create_signal(symbol, price, tech, forest_info, singularity_prob, regime, "BUY", combined))
        elif combined < 0.4 and regime in [MarketRegime.BEAR_TREND, MarketRegime.CRASH, MarketRegime.REVERSAL]:
            sell_conf = 1 - combined
            signals.append(self._create_signal(symbol, price, tech, forest_info, singularity_prob, regime, "SELL", sell_conf))
        return signals

    def _create_signal(self, symbol, price, tech, forest_info, singularity_prob, regime, stype, confidence):
        tf = tech['timeframe_analysis']['1h']
        vol = tf['volatility']['volatility']
        atr = tf['volatility']['atr']
        trend_str = tf['trend']['strength']
        sl = self.risk_manager.calculate_dynamic_stop_loss(price, vol, trend_str, atr)
        risk = abs(price - sl)
        reward = risk * 3
        pos = self.risk_manager.calculate_position_size(price, sl, confidence, vol)
        if singularity_prob > 0.7:
            pos *= (1 - singularity_prob)
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
            symbol=symbol, timeframe='multiple', signal_type=stype,
            strength=strength, confidence=confidence, indicators=tech,
            price=price, timestamp=pd.Timestamp.now(),
            target_prices={'target1': price+reward, 'target2': price+reward*1.5},
            stop_loss=sl, risk_reward_ratio=reward/risk,
            recommended_position=pos, market_regime=regime,
            singularity_probability=singularity_prob,
            forest_confidence=forest_info.get('confidence',0) if forest_info else 0
        )

# ======================== 交易所數據接口 ========================
exchange = ccxt.binance({
    'enableRateLimit': True,
})

def fetch_ohlcv(symbol='BTC/USDT', timeframe='1h', limit=2000):
    """從 Binance 拉取 OHLCV 數據並轉為 DataFrame"""
    try:
        raw = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"數據抓取失敗: {e}")
        # 若失敗則回傳空 DataFrame 避免中斷
        return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

# ======================== Dash 儀表板 ========================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 全域配置
TRADING_SYSTEM = None
FETCH_CONFIG = {
    'symbol': 'BTC/USDT',
    'timeframe': '1h',
    'live_limit': 120   # 儀表板顯示近120根K線
}

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("森林增強與奇點概率交易系統 (BTC/USDT 即時)", className="text-center mb-4"))),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='symbol-selector', options=[
            {'label': 'BTC/USDT', 'value': 'BTC/USDT'},
            {'label': 'ETH/USDT', 'value': 'ETH/USDT'},
            {'label': 'BNB/USDT', 'value': 'BNB/USDT'}
        ], value='BTC/USDT'), width=6),
        dbc.Col(dcc.Dropdown(id='timeframe-selector', options=[
            {'label': '1小時', 'value': '1h'},
            {'label': '4小時', 'value': '4h'},
            {'label': '日線', 'value': '1d'}
        ], value='1h'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("市場狀態"), dbc.CardBody(html.H4(id='market-regime'))]), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("奇點概率"), dbc.CardBody(html.H4(id='singularity-prob'))]), width=4),
        dbc.Col(dbc.Card([dbc.CardHeader("森林置信度"), dbc.CardBody(html.H4(id='forest-confidence'))]), width=4)
    ]),
    dbc.Row(dbc.Col(dbc.Card([dbc.CardHeader("交易信號"), dbc.CardBody([html.H4(id='trade-signal'), html.P(id='signal-details')])]))),
    dbc.Row(dbc.Col(dbc.Card([dbc.CardHeader("價格圖表"), dbc.CardBody(dcc.Graph(id='price-chart'))]))),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("特徵重要性"), dbc.CardBody(dcc.Graph(id='feature-importance'))]), width=6),
        dbc.Col(dbc.Card([dbc.CardHeader("奇點概率歷史"), dbc.CardBody(dcc.Graph(id='singularity-history'))]), width=6)
    ]),
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # 每分鐘更新
], fluid=True)

# ---------- 圖表輔助函數 ----------
def make_price_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='價格'
    ))
    sma = talib.SMA(df['close'], timeperiod=20)
    fig.add_trace(go.Scatter(x=df.index, y=sma, name='SMA20', line=dict(color='orange')))
    fig.update_layout(template='plotly_white', height=300)
    return fig

# ---------- 回調 ----------
@app.callback(
    [Output('market-regime','children'), Output('singularity-prob','children'),
     Output('forest-confidence','children'), Output('trade-signal','children'),
     Output('signal-details','children'), Output('price-chart','figure'),
     Output('feature-importance','figure'), Output('singularity-history','figure')],
    [Input('interval-component','n_intervals'), Input('symbol-selector','value'),
     Input('timeframe-selector','value')]
)
def update_dashboard(n, symbol, timeframe):
    if TRADING_SYSTEM is None:
        return "未訓練","0%","0%","無信號","請先訓練系統",{},{},{}

    # 從交易所拉取最新數據
    df = fetch_ohlcv(symbol, timeframe, FETCH_CONFIG['live_limit'])
    if df.empty:
        return "數據錯誤","0%","0%","錯誤","無法取得交易所數據",{},{},{}

    ohlc_data = {'1h': df}  # 系統內部使用 '1h' 作為主要分析週期

    # 分析市場
    result = TRADING_SYSTEM.analyze_market(ohlc_data, symbol)

    regime = result['technical_analysis']['market_regime'].value
    sing_prob = result['singularity_probability']
    forest_conf = result['forest_analysis'].get('confidence', 0) if result['forest_analysis'] else 0
    signals = result['signals']

    if signals:
        sig = signals[0]
        trade_signal = f"{sig.signal_type} ({sig.strength.name})"
        details = f"信心:{sig.confidence:.2%} | 倉位:{sig.recommended_position:.2%} | 止損:{sig.stop_loss:.2f}"
    else:
        trade_signal = "無信號"
        details = "等待條件符合"

    # 圖表
    price_fig = make_price_chart(df)

    # 特徵重要性
    feat_imp = result['forest_analysis'].get('feature_importances', {})
    if feat_imp:
        imp_df = pd.DataFrame({'feature': list(feat_imp.keys()), 'importance': list(feat_imp.values())})
        imp_df = imp_df.sort_values('importance')
        feat_fig = go.Figure(go.Bar(x=imp_df['importance'], y=imp_df['feature'], orientation='h'))
    else:
        feat_fig = go.Figure()
    feat_fig.update_layout(title="特徵重要性", template='plotly_white', height=300)

    # 奇點歷史
    hist = TRADING_SYSTEM.singularity_detector.history
    if hist:
        hist_df = pd.DataFrame(hist)
        sing_fig = go.Figure()
        sing_fig.add_trace(go.Scatter(x=hist_df['timestamp'], y=hist_df['probability'], mode='lines+markers'))
        sing_fig.add_hline(y=0.7, line_dash='dash', line_color='red')
    else:
        sing_fig = go.Figure()
    sing_fig.update_layout(title="奇點概率歷史", template='plotly_white', height=300)

    return (regime, f"{sing_prob:.2%}", f"{forest_conf:.2%}",
            trade_signal, details, price_fig, feat_fig, sing_fig)

# ======================== 啟動 ========================
if __name__ == '__main__':
    print("正在從 Binance 下載歷史數據以訓練森林模型...")
    # 訓練用 2000 根 1 小時 K 線
    train_df = fetch_ohlcv('BTC/USDT', '1h', 2000)
    if train_df.empty:
        print("無法獲取訓練數據，請檢查網路連線")
        exit()

    TRADING_SYSTEM = AdvancedTradingSystem(initial_capital=10000)
    TRADING_SYSTEM.train_forest_model(train_df)

    print("啟動儀表板，請打開 http://127.0.0.1:8050")
    app.run_server(debug=True, port=8050)
