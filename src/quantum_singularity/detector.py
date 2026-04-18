"""奇點檢測器 (Singularity Detector)"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SingularityDetector:
    """奇點檢測器"""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.strength = 0.0
        
    def detect(self, data: np.ndarray) -> tuple:
        """檢測奇點"""
        if len(data) == 0:
            return False, 0.0
        
        # 計算數據的範數作為強度
        self.strength = float(np.linalg.norm(data) / (np.sqrt(len(data)) + 1e-8))
        self.strength = min(1.0, self.strength)
        
        detected = self.strength > self.threshold
        return detected, self.strength
    
    def get_strength(self) -> float:
        """獲取奇點強度"""
        return self.strength
