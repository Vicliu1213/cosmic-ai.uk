import numpy as np
import pandas as pd
from sklearn.manifold import Isomap
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist, squareform
from ..base_plugin import BasePlugin
from typing import Dict, Any

class TopologicalManifold(BasePlugin):
    """
    增研版：整合 TDA Persistent Homology + 強化 Isomap 曲率計算 + 多尺度異常探測。
    超越流形投影，捕捉市場時空的拓撲不變性與「斷裂」信號，用於 BTC/Altcoin 套利觸發。
    """
    @property
    def plugin_name(self):
        return "topological_manifold_pro"

    def _compute_geodesic_curvature(self, embedding: np.ndarray) -> float:
        """強化曲率：使用 geodesic 近似 + 高斯曲率代理，提升爆發預測精度 [web:1][web:4]。"""
        # 多尺度梯度：捕捉局部/全局彎曲
        nbrs = NearestNeighbors(n_neighbors=10).fit(embedding)
        distances, indices = nbrs.kneighbors(embedding)
        geodesic_approx = np.mean(distances[:, 1:], axis=1)  # 平均 geodesic 距離作為曲率代理
        gradients = np.gradient(embedding, axis=0)
        total_curvature = np.std(gradients) + np.std(geodesic_approx)
        return total_curvature

    def _compute_topological_anomaly(self, high_dim_data: pd.DataFrame) -> Dict[str, Any]:
        """TDA 異常分數：使用距離矩陣 persistence proxy，檢測拓撲「洞」與斷裂 [web:2][web:12]。"""
        dist_matrix = squareform(pdist(high_dim_data.values, metric='euclidean'))
        # Persistence proxy: max gap in sorted distances (birth-death analog)
        sorted_dist = np.sort(dist_matrix, axis=None)
        gaps = np.diff(sorted_dist)
        persistence = np.max(gaps) / np.median(gaps) if np.median(gaps) > 0 else 0
        # Local density anomaly
        mean_dist = np.mean(dist_matrix, axis=1)
        anomaly_score = np.max(np.std(mean_dist)) * persistence
        return {"persistence": persistence, "tda_anomaly": anomaly_score}

    async def run(self, high_dim_data: pd.DataFrame) -> Dict[str, Any]:
        # 輸入驗證：假設 normalized 多維市場數據 (價、量、鏈上、情緒...)
        if high_dim_data.isnull().any().any():
            high_dim_data = high_dim_data.fillna(method='ffill').fillna(0)
        data_norm = (high_dim_data - high_dim_data.mean()) / high_dim_data.std()

        # Isomap 3D 投影：n_neighbors 自適應 [web:9]
        n_samples = len(data_norm)
        n_neighbors = min(10, max(5, int(np.sqrt(n_samples))))
        iso = Isomap(n_components=3, n_neighbors=n_neighbors, n_jobs=-1)
        projection = iso.fit_transform(data_norm)

        # 強化曲率：std(gradient) -> geodesic-aware 版本
        manifold_curvature = self._compute_geodesic_curvature(projection)

        # TDA 增強異常：拓撲洞檢測
        tda_metrics = self._compute_topological_anomaly(data_norm)

        # 綜合信號：曲率 * TDA，閾值建議 >1.5 觸發套利掃描
        composite_signal = manifold_curvature * tda_metrics["tda_anomaly"]

        return {
            "manifold_curvature": manifold_curvature,
            "tda_persistence": tda_metrics["persistence"],
            "tda_anomaly": tda_metrics["tda_anomaly"],
            "composite_signal": composite_signal,
            "projection_3d": projection,  # 可視化用
            "threshold_alert": composite_signal > 2.0  # 經驗閾值，依回測調整 [web:7]
        }
