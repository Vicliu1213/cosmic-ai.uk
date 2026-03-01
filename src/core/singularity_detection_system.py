#!/usr/bin/env python3
"""
Singularity Detection System - Phase 3
奇點檢測系統 - 第3階段

Detects and characterizes singularity events through:
- Multi-dimensional pattern recognition
- Wavelet analysis for transient detection
- Chaos theory metrics
- Anomaly detection algorithms
- Real-time singularity probability scoring
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import deque
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)


class SingularityType(Enum):
    """奇點類型分類"""
    NONE = "none"  # 沒有奇點
    EMERGING = "emerging"  # 萌芽: Sharpe 剛超過 2.0
    STRONG = "strong"  # 強型: Sharpe > 2.5 且穩定
    EXCEPTIONAL = "exceptional"  # 異常: Sharpe > 3.0 或特殊事件
    WANING = "waning"  # 衰退: 從強轉向中等


class SingularityPhase(Enum):
    """奇點生命週期"""
    DORMANT = "dormant"  # 無活動
    FORMATION = "formation"  # 形成中 (1-5 次交易)
    PEAK = "peak"  # 巔峰 (Sharpe 最高)
    PLATEAU = "plateau"  # 平台 (維持高 Sharpe)
    DECLINE = "decline"  # 衰退 (Sharpe 下降)


@dataclass
class SingularitySignal:
    """奇點信號"""
    singularity_type: SingularityType
    probability: float  # 0-1
    confidence: float  # 0-1
    phase: SingularityPhase
    sharpe_ratio: float
    strength_score: float  # 0-100
    duration_trades: int  # 持續交易數
    peak_sharpe: float  # 期間峰值
    characteristics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def is_active(self) -> bool:
        """檢查是否活躍奇點"""
        return (
            self.singularity_type != SingularityType.NONE and
            self.probability > 0.5 and
            self.confidence > 0.6
        )


@dataclass
class PatternCharacteristic:
    """模式特徵"""
    name: str
    value: float  # 特徵值
    weight: float  # 權重
    detected: bool  # 是否檢測到
    threshold: float  # 檢測閾值


class WaveletAnalyzer:
    """小波分析引擎 (檢測 transient 事件)"""

    def __init__(self, scales: List[int] = None):
        """
        初始化小波分析器

        Args:
            scales: 分析尺度
        """
        self.scales = scales or [2, 4, 8, 16, 32]

    def morlet_wavelet(self, scale: int, length: int) -> np.ndarray:
        """生成 Morlet 小波"""
        frequency = 5.0 / (scale * np.pi)
        time = np.arange(-length / 2, length / 2, 1)

        real = np.cos(2 * np.pi * frequency * time) * np.exp(-time ** 2 / (2 * scale ** 2))
        imag = np.sin(2 * np.pi * frequency * time) * np.exp(-time ** 2 / (2 * scale ** 2))

        return real + 1j * imag

    def continuous_wavelet_transform(
        self,
        signal: List[float],
        scale: int
    ) -> np.ndarray:
        """連續小波變換"""
        signal_array = np.array(signal)
        if len(signal_array) < scale * 2:
            return np.zeros_like(signal_array, dtype=complex)

        wavelet = self.morlet_wavelet(scale, len(signal_array))
        coefficients = np.correlate(signal_array, wavelet, mode='same')

        return coefficients

    def detect_transients(self, signal: List[float]) -> Dict[int, float]:
        """
        檢測 transient 事件

        Returns:
            {時間索引: 事件強度}
        """
        transients = {}

        for scale in self.scales:
            coefficients = self.continuous_wavelet_transform(signal, scale)
            power = np.abs(coefficients)

            # 偵測局部最大值
            for i in range(1, len(power) - 1):
                if power[i] > power[i - 1] and power[i] > power[i + 1]:
                    threshold = np.mean(power) + 2 * np.std(power)
                    if power[i] > threshold:
                        if i not in transients:
                            transients[i] = 0.0
                        transients[i] += power[i] / (len(self.scales) * np.max(power))

        return transients

    def get_transient_intensity(self, signal: List[float]) -> float:
        """計算 transient 總強度 (0-1)"""
        if len(signal) < 10:
            return 0.0

        transients = self.detect_transients(signal)
        if not transients:
            return 0.0

        return float(min(sum(transients.values()) / len(transients), 1.0))


class ChaosAnalyzer:
    """混沌理論分析引擎"""

    @staticmethod
    def calculate_lyapunov_exponent(
        time_series: List[float],
        dim: int = 2,
        delay: int = 1
    ) -> float:
        """
        計算 Lyapunov 指數

        Args:
            time_series: 時間序列
            dim: 嵌入維度
            delay: 延遲

        Returns:
            Lyapunov 指數 (正值表示混沌)
        """
        if len(time_series) < dim * delay + 100:
            return 0.0

        data = np.array(time_series)
        N = len(data)

        # 相位空間嵌入
        X = np.zeros((N - dim * delay, dim))
        for i in range(N - dim * delay):
            for j in range(dim):
                X[i, j] = data[i + j * delay]

        # 計算最近鄰域距離
        lyapunov_sum = 0.0
        count = 0

        for i in range(len(X)):
            distances = np.linalg.norm(X[i:] - X[i], axis=1)
            distances = distances[distances > 0]

            if len(distances) > 0:
                nearest_dist = np.min(distances)
                if nearest_dist > 0:
                    nearest_idx = np.argmin(distances)
                    future_dist = abs(data[i + nearest_idx + 1] - data[i + 1]) if i + 1 < N else nearest_dist

                    if future_dist > 0:
                        lyapunov_sum += np.log(future_dist / nearest_dist)
                        count += 1

        if count == 0:
            return 0.0

        lyapunov = lyapunov_sum / count
        return float(lyapunov)

    @staticmethod
    def calculate_entropy(time_series: List[float], bins: int = 20) -> float:
        """計算 Shannon 熵 (0-1 歸一化)"""
        if len(time_series) < 2:
            return 0.0

        hist, _ = np.histogram(time_series, bins=bins, density=True)
        hist = hist[hist > 0]  # 移除零值

        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        max_entropy = np.log2(len(hist))

        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        return float(min(normalized_entropy, 1.0))

    @staticmethod
    def calculate_hurst_exponent(time_series: List[float]) -> float:
        """
        計算 Hurst 指數

        0.5: 隨機行走
        > 0.5: 持續 (趨勢)
        < 0.5: 反轉
        """
        if len(time_series) < 10:
            return 0.5

        data = np.array(time_series)
        n = len(data)

        # 計算 rescaled range
        mean_data = np.mean(data)
        Y = np.cumsum(data - mean_data)

        # 分割成子序列
        hurst_values = []
        for k in range(10, n // 2):
            num_chunks = n // k
            if num_chunks == 0:
                continue

            R_k = []
            for i in range(num_chunks):
                chunk = Y[i * k:(i + 1) * k]
                R = np.max(chunk) - np.min(chunk)
                S = np.std(data[i * k:(i + 1) * k], ddof=1)
                if S > 0:
                    R_k.append(R / S)

            if R_k:
                hurst_values.append(np.mean(R_k))

        if not hurst_values:
            return 0.5

        # 擬合 H*log(N) = log(R/S)
        log_k = np.log([10 + i * 5 for i in range(len(hurst_values))])
        log_rs = np.log(hurst_values)

        if len(log_k) > 1:
            H = np.polyfit(log_k, log_rs, 1)[0]
            return float(np.clip(H, 0.0, 2.0))

        return 0.5


class AnomalyDetector:
    """異常檢測引擎"""

    def __init__(self, window_size: int = 50):
        """初始化異常檢測器"""
        self.window_size = window_size
        self.value_history: deque = deque(maxlen=window_size)

    def update(self, value: float) -> float:
        """
        更新值並返回異常分數 (0-1)

        Args:
            value: 新值

        Returns:
            異常分數
        """
        self.value_history.append(value)

        if len(self.value_history) < 10:
            return 0.0

        values = np.array(self.value_history)
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return 0.0

        # Z-score 異常檢測
        z_score = abs(value - mean) / std
        anomaly_score = min(z_score / 3.0, 1.0)  # 3-sigma 歸一化

        return float(anomaly_score)

    def detect_spike(self, sensitivity: float = 0.8) -> bool:
        """檢測峰值異常"""
        if len(self.value_history) < 2:
            return False

        values = np.array(self.value_history)
        recent = values[-1]
        previous_mean = np.mean(values[:-1])
        previous_std = np.std(values[:-1])

        if previous_std == 0:
            return False

        z_score = abs(recent - previous_mean) / previous_std
        return z_score > (1.0 - sensitivity) * 4.0


class SingularityDetectionSystem:
    """Phase 3 奇點檢測系統 - 核心系統"""

    def __init__(
        self,
        sharpe_threshold_emerging: float = 2.0,
        sharpe_threshold_strong: float = 2.5,
        sharpe_threshold_exceptional: float = 3.0,
        min_duration_trades: int = 5
    ):
        """
        初始化奇點檢測系統

        Args:
            sharpe_threshold_emerging: 萌芽閾值
            sharpe_threshold_strong: 強型閾值
            sharpe_threshold_exceptional: 異常閾值
            min_duration_trades: 最少持續交易數
        """
        self.sharpe_threshold_emerging = sharpe_threshold_emerging
        self.sharpe_threshold_strong = sharpe_threshold_strong
        self.sharpe_threshold_exceptional = sharpe_threshold_exceptional
        self.min_duration_trades = min_duration_trades

        self.wavelet_analyzer = WaveletAnalyzer()
        self.chaos_analyzer = ChaosAnalyzer()
        self.anomaly_detector = AnomalyDetector(window_size=50)

        self.sharpe_history: deque = deque(maxlen=100)
        self.volatility_history: deque = deque(maxlen=100)
        self.return_history: deque = deque(maxlen=100)

        self.current_singularity: Optional[SingularitySignal] = None
        self.past_singularities: List[SingularitySignal] = []
        self.formation_start = None

        self.logger = logging.getLogger(self.__class__.__name__)

    def process_trading_data(
        self,
        sharpe_ratio: float,
        volatility: float,
        return_value: float
    ) -> SingularitySignal:
        """
        處理交易數據並檢測奇點

        Args:
            sharpe_ratio: Sharpe 比率
            volatility: 波動率
            return_value: 收益率

        Returns:
            SingularitySignal 物件
        """
        self.sharpe_history.append(sharpe_ratio)
        self.volatility_history.append(volatility)
        self.return_history.append(return_value)

        # 檢測奇點
        signal = self._detect_singularity()

        self.logger.debug(
            f"Singularity detection: type={signal.singularity_type.value}, "
            f"prob={signal.probability:.2%}, conf={signal.confidence:.2%}"
        )

        return signal

    def _detect_singularity(self) -> SingularitySignal:
        """偵測奇點訊號"""
        if len(self.sharpe_history) < self.min_duration_trades:
            return SingularitySignal(
                singularity_type=SingularityType.NONE,
                probability=0.0,
                confidence=0.0,
                phase=SingularityPhase.DORMANT,
                sharpe_ratio=self.sharpe_history[-1] if self.sharpe_history else 0.0,
                strength_score=0.0,
                duration_trades=0,
                peak_sharpe=0.0
            )

        current_sharpe = float(self.sharpe_history[-1])
        characteristics = self._extract_characteristics()

        # 判斷奇點類型
        if current_sharpe >= self.sharpe_threshold_exceptional:
            singularity_type = SingularityType.EXCEPTIONAL
        elif current_sharpe >= self.sharpe_threshold_strong:
            singularity_type = SingularityType.STRONG
        elif current_sharpe >= self.sharpe_threshold_emerging:
            singularity_type = SingularityType.EMERGING
        else:
            # 檢查是否從高 Sharpe 衰退
            if self._is_waning():
                singularity_type = SingularityType.WANING
            else:
                singularity_type = SingularityType.NONE

        # 計算機率和信心度
        probability, confidence = self._calculate_probability_confidence(
            singularity_type,
            characteristics
        )

        # 判斷生命週期
        phase = self._determine_phase(singularity_type, characteristics)

        # 計算強度分數
        strength_score = self._calculate_strength_score(characteristics)

        # 計算持續時間
        duration_trades = self._calculate_duration()

        # 峰值 Sharpe
        peak_sharpe = float(max(self.sharpe_history)) if self.sharpe_history else 0.0

        signal = SingularitySignal(
            singularity_type=singularity_type,
            probability=probability,
            confidence=confidence,
            phase=phase,
            sharpe_ratio=current_sharpe,
            strength_score=strength_score,
            duration_trades=duration_trades,
            peak_sharpe=peak_sharpe,
            characteristics=characteristics
        )

        # 更新目前奇點
        if signal.is_active():
            if self.current_singularity is None:
                self.formation_start = datetime.now()
                self.logger.warning(f"⭐ Singularity formation detected: {singularity_type.value}")
            self.current_singularity = signal
        else:
            if self.current_singularity is not None and self.current_singularity.is_active():
                self.past_singularities.append(self.current_singularity)
                self.logger.info(f"⭐ Singularity ended: {self.current_singularity.singularity_type.value}")
            self.current_singularity = None
            self.formation_start = None

        return signal

    def _extract_characteristics(self) -> Dict[str, float]:
        """提取特徵"""
        sharpe_trend = self._calculate_trend(list(self.sharpe_history))
        volatility_stability = self._calculate_stability(list(self.volatility_history))
        anomaly_score = self.anomaly_detector.update(float(self.sharpe_history[-1]))

        # 小波分析
        transient_intensity = self.wavelet_analyzer.get_transient_intensity(
            list(self.return_history)
        )

        # 混沌指標
        if len(self.return_history) > 30:
            lyapunov = self.chaos_analyzer.calculate_lyapunov_exponent(
                list(self.return_history)
            )
            entropy = self.chaos_analyzer.calculate_entropy(
                list(self.return_history)
            )
            hurst = self.chaos_analyzer.calculate_hurst_exponent(
                list(self.return_history)
            )
        else:
            lyapunov = 0.0
            entropy = 0.5
            hurst = 0.5

        return {
            "sharpe_trend": sharpe_trend,
            "volatility_stability": volatility_stability,
            "anomaly_score": anomaly_score,
            "transient_intensity": transient_intensity,
            "lyapunov_exponent": lyapunov,
            "entropy": entropy,
            "hurst_exponent": hurst,
            "sharpe_acceleration": self._calculate_acceleration(list(self.sharpe_history))
        }

    def _calculate_trend(self, values: List[float]) -> float:
        """計算趨勢 (-1 到 1)"""
        if len(values) < 2:
            return 0.0

        values_array = np.array(values[-20:])
        if len(values_array) < 2:
            return 0.0

        x = np.arange(len(values_array))
        z = np.polyfit(x, values_array, 1)
        trend = np.clip(z[0] / (max(abs(z[0]), 0.1)), -1, 1)

        return float(trend)

    def _calculate_stability(self, values: List[float]) -> float:
        """計算穩定性 (0-1)"""
        if len(values) < 2:
            return 0.0

        values_array = np.array(values[-20:])
        cv = np.std(values_array) / (np.mean(values_array) + 1e-6)
        stability = 1.0 / (1.0 + cv)

        return float(np.clip(stability, 0.0, 1.0))

    def _calculate_acceleration(self, values: List[float]) -> float:
        """計算加速度"""
        if len(values) < 3:
            return 0.0

        values_array = np.array(values[-10:])
        if len(values_array) < 3:
            return 0.0

        first_diff = np.diff(values_array)
        second_diff = np.diff(first_diff)

        acceleration = float(np.mean(second_diff))
        return float(np.clip(acceleration, -1, 1))

    def _is_waning(self) -> bool:
        """檢查是否衰退"""
        if len(self.sharpe_history) < 5:
            return False

        recent = list(self.sharpe_history)[-5:]
        return recent[-1] < max(recent[:-1]) - 0.2

    def _calculate_probability_confidence(
        self,
        singularity_type: SingularityType,
        characteristics: Dict[str, float]
    ) -> Tuple[float, float]:
        """計算奇點機率和信心度"""
        if singularity_type == SingularityType.NONE:
            return 0.0, 0.0

        # 基礎機率
        prob_base_map = {
            SingularityType.EMERGING: 0.4,
            SingularityType.STRONG: 0.7,
            SingularityType.EXCEPTIONAL: 0.9,
            SingularityType.WANING: 0.3,
            SingularityType.NONE: 0.0
        }
        probability = prob_base_map.get(singularity_type, 0.0)

        # 特徵調整
        trend_factor = (characteristics.get("sharpe_trend", 0.0) + 1.0) / 2.0
        anomaly_factor = characteristics.get("anomaly_score", 0.0)
        transient_factor = characteristics.get("transient_intensity", 0.0)

        probability = probability * 0.5 + (trend_factor + anomaly_factor + transient_factor) / 3.0 * 0.5

        # 信心度 = 持續性
        if len(self.sharpe_history) < 5:
            confidence = 0.5
        else:
            recent_sharpe = list(self.sharpe_history)[-5:]
            consistency = 1.0 - np.std(recent_sharpe) / (np.mean(recent_sharpe) + 1e-6)
            confidence = float(np.clip(consistency, 0.0, 1.0))

        return float(np.clip(probability, 0.0, 1.0)), float(np.clip(confidence, 0.0, 1.0))

    def _determine_phase(
        self,
        singularity_type: SingularityType,
        characteristics: Dict[str, float]
    ) -> SingularityPhase:
        """判斷奇點生命週期"""
        if singularity_type == SingularityType.NONE:
            return SingularityPhase.DORMANT

        duration = self._calculate_duration()
        trend = characteristics.get("sharpe_trend", 0.0)
        acceleration = characteristics.get("sharpe_acceleration", 0.0)

        if duration < 3:
            return SingularityPhase.FORMATION
        elif acceleration > 0.05:
            return SingularityPhase.PEAK
        elif trend > -0.01:
            return SingularityPhase.PLATEAU
        else:
            return SingularityPhase.DECLINE

    def _calculate_strength_score(self, characteristics: Dict[str, float]) -> float:
        """計算強度分數 (0-100)"""
        factors = [
            characteristics.get("sharpe_trend", 0.0) + 1.0,  # 0-2
            characteristics.get("volatility_stability", 0.5) * 2,  # 0-1
            (1.0 - characteristics.get("anomaly_score", 0.0)),  # 0-1
            characteristics.get("transient_intensity", 0.0),  # 0-1
        ]

        score = (sum(factors) / len(factors)) * 50
        return float(np.clip(score, 0.0, 100.0))

    def _calculate_duration(self) -> int:
        """計算當前奇點持續時間 (交易數)"""
        if self.current_singularity is None or not self.current_singularity.is_active():
            return 0

        return self.current_singularity.duration_trades + 1

    def get_singularity_status(self) -> Dict[str, Any]:
        """取得奇點狀態"""
        if self.current_singularity is None or not self.current_singularity.is_active():
            return {
                "status": "inactive",
                "active_singularity": False,
                "past_singularities": len(self.past_singularities),
                "timestamp": datetime.now().isoformat()
            }

        return {
            "status": "active",
            "active_singularity": True,
            "type": self.current_singularity.singularity_type.value,
            "probability": self.current_singularity.probability,
            "confidence": self.current_singularity.confidence,
            "phase": self.current_singularity.phase.value,
            "strength_score": self.current_singularity.strength_score,
            "duration_trades": self.current_singularity.duration_trades,
            "peak_sharpe": self.current_singularity.peak_sharpe,
            "characteristics": self.current_singularity.characteristics,
            "past_singularities": len(self.past_singularities),
            "timestamp": self.current_singularity.timestamp.isoformat()
        }

    def reset(self) -> None:
        """重設系統"""
        self.sharpe_history.clear()
        self.volatility_history.clear()
        self.return_history.clear()
        self.anomaly_detector = AnomalyDetector(window_size=50)
        self.current_singularity = None
        self.past_singularities.clear()
        self.formation_start = None
        self.logger.info("✅ Singularity Detection System reset")
