"""
超指數遞歸協同增長增研版
偵測價格是否存在超指數增長前兆，使用遞歸自迴歸 + 協同指標
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import logging

from ..base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class HyperexponentialGrowthPlugin(BasePlugin):
    metadata = {
        "name": "hyperexponential_growth",
        "version": "1.0.0",
        "description": "基於遞歸協同的超指數增長偵測",
        "author": "quant",
        "dependencies": [],
        "required_config": ["window", "threshold", "recursive_depth"]
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.window = self.config.get("window", 100)          # 分析視窗
        self.threshold = self.config.get("threshold", 0.8)    # 超指數機率閾值
        self.recursive_depth = self.config.get("recursive_depth", 3)  # 遞歸階數

    def _log_returns(self, prices: np.ndarray) -> np.ndarray:
        """對數收益率"""
        return np.diff(np.log(prices))

    def _recursive_autoregression(self, series: np.ndarray, order: int) -> float:
        """
        遞歸自迴歸：使用遞迴方式擬合增長率對自身的依賴
        返回擬合優度 R^2
        """
        if len(series) < order + 2:
            return 0.0
        # 構造延遲矩陣
        X = np.column_stack([series[i: -order + i] for i in range(1, order+1)])
        y = series[order:]
        # 簡單線性回歸
        try:
            coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
            y_pred = X @ coeffs
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / (ss_tot + 1e-8))
            return r2
        except:
            return 0.0

    def _cointegration_score(self, prices: np.ndarray, volumes: Optional[np.ndarray] = None) -> float:
        """
        協同指標：基於價格與成交量的協整關係（簡化版）
        如果價格與成交量同步上升且協整係數顯著，則可能支持超指數增長
        """
        if volumes is None or len(prices) != len(volumes):
            return 0.5
        # 標準化
        p_norm = (prices - prices.mean()) / prices.std()
        v_norm = (volumes - volumes.mean()) / volumes.std()
        # 簡單相關係數（或可使用 Engle-Granger 檢定）
        corr = np.corrcoef(p_norm, v_norm)[0, 1]
        # 轉換為 0-1 分數
        return max(0.0, min(1.0, (corr + 1) / 2))

    def _hyperexponential_score(self, returns: np.ndarray) -> float:
        """
        超指數得分：檢驗增長率是否加速
        方法：計算回報率的回報率（二階差分）是否顯著為正
        """
        if len(returns) < 5:
            return 0.0
        # 回報率的變化率
        acceleration = np.diff(returns)
        # 檢驗加速率的均值是否大於0（t檢驗）
        t_stat, p_value = stats.ttest_1samp(acceleration, 0)
        # 如果顯著為正且均值 > 0，則得分高
        score = 0.0
        if np.mean(acceleration) > 0 and p_value < 0.05:
            score = min(1.0, np.mean(acceleration) / (np.std(acceleration) + 1e-8))
        return score

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        輸入 context 應包含:
            - prices: 價格序列 (list or np.array)
            - volumes: 成交量序列 (可選)
        """
        prices = context.get("prices")
        if prices is None:
            raise ValueError("context 中缺少 'prices'")
        volumes = context.get("volumes")

        # 轉為 numpy 陣列
        if isinstance(prices, list):
            prices = np.array(prices)
        if volumes is not None and isinstance(volumes, list):
            volumes = np.array(volumes)

        # 取最近 window 個點
        prices = prices[-self.window:]
        if volumes is not None:
            volumes = volumes[-self.window:]

        # 計算回報率
        returns = self._log_returns(prices)

        # 1. 遞歸自迴歸分數
        rec_score = self._recursive_autoregression(returns, self.recursive_depth)

        # 2. 超指數加速分數
        hyper_score = self._hyperexponential_score(returns)

        # 3. 協同指標（如果提供成交量）
        coint_score = self._cointegration_score(prices, volumes) if volumes is not None else 0.5

        # 綜合得分（可自定義加權）
        composite_score = 0.4 * rec_score + 0.4 * hyper_score + 0.2 * coint_score

        # 生成信號
        signal = "hyper_growth" if composite_score > self.threshold else "normal"
        # 若信號為 hyper_growth，可附加強度
        if signal == "hyper_growth":
            strength = "weak" if composite_score < 0.9 else "strong"

        result = {
            "recursive_r2": rec_score,
            "hyperexponential_score": hyper_score,
            "cointegration_score": coint_score,
            "composite_score": composite_score,
            "signal": signal,
            "strength": strength if signal == "hyper_growth" else None
        }
        logger.info(f"超指數增長偵測: {result}")
        return result
