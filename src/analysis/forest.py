"""
随机森林分类器，用于预测市场方向。
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from .indicators import rsi, macd, atr, sma, obv


class ForestAnalyzer:
    def __init__(self, n_estimators=100, random_state=42):
        self.clf = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state, oob_score=True)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_importances_ = None

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """从OHLCV数据中提取特征"""
        features = pd.DataFrame(index=df.index)

        # 价格特征
        features['returns'] = df['close'].pct_change()
        features['volatility'] = df['close'].rolling(20).std() / df['close'].rolling(20).mean()

        # 技术指标
        features['rsi'] = rsi(df['close'], 14)
        macd_line, macd_signal, _ = macd(df['close'])
        features['macd_diff'] = macd_line - macd_signal

        # 移动平均线比率
        sma20 = sma(df['close'], 20)
        sma50 = sma(df['close'], 50)
        features['sma_ratio'] = sma20 / sma50 - 1

        # 成交量特征
        features['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        obv_val = obv(df['close'], df['volume'])
        features['obv_ratio'] = obv_val / obv_val.rolling(20).mean()

        # 波动率特征
        features['atr_ratio'] = atr(df['high'], df['low'], df['close']) / df['close']

        # 高/低比例
        features['hl_ratio'] = df['high'] / df['low']

        # 删除NaN
        features = features.dropna()
        return features

    def prepare_labels(self, df: pd.DataFrame, forward_periods: int = 5) -> pd.Series:
        """生成标签：未来 forward_periods 根K线的收益率符号"""
        future_returns = df['close'].pct_change(forward_periods).shift(-forward_periods)
        labels = (future_returns > 0).astype(int)
        labels = labels.dropna()
        return labels

    def train(self, df: pd.DataFrame):
        """训练模型"""
        features = self.prepare_features(df)
        labels = self.prepare_labels(df)
        # 对齐索引
        common_idx = features.index.intersection(labels.index)
        features = features.loc[common_idx]
        labels = labels.loc[common_idx]

        # 标准化
        scaled_features = self.scaler.fit_transform(features)
        self.clf.fit(scaled_features, labels)
        self.is_trained = True
        self.feature_importances_ = pd.Series(self.clf.feature_importances_, index=features.columns).sort_values(ascending=False)
        return self

    def predict(self, df: pd.DataFrame) -> dict:
        """预测最新数据点的方向和置信度"""
        if not self.is_trained:
            raise ValueError("模型未训练")
        features = self.prepare_features(df)
        if features.empty:
            return {"direction": 0, "confidence": 0, "singularity_prob": 0}

        latest = features.iloc[-1:].copy()
        scaled = self.scaler.transform(latest)
        proba = self.clf.predict_proba(scaled)[0]
        pred_class = self.clf.predict(scaled)[0]
        confidence = max(proba)
        direction = 1 if pred_class == 1 else -1

        # 简化的奇点概率（基于预测置信度的异常程度）
        # 这里只是示例，真实奇点检测在 singularity.py 中实现
        anomaly_score = abs(confidence - 0.5) * 2
        singularity_prob = 1 / (1 + np.exp(-anomaly_score * 10))

        return {
            "direction": direction,
            "confidence": confidence,
            "singularity_prob": singularity_prob,
            "feature_importances": self.feature_importances_.to_dict()
        }
