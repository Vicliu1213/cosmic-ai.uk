"""時空計算網格 (Spacetime Grid)"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SpacetimeGrid:
    """時空計算網格"""
    
    def __init__(self, dimension: int = 4):
        self.dimension = dimension
        self.grid_resolution = 64
        self.metric_tensor = self._initialize_metric()
        self.topology_order = 0.5
        
    def _initialize_metric(self) -> np.ndarray:
        """初始化 Minkowski 度規"""
        metric = np.zeros((self.dimension, self.dimension))
        metric[0, 0] = 1.0
        for i in range(1, self.dimension):
            metric[i, i] = -1.0
        return metric
    
    def initialize(self):
        logger.info(f"SpacetimeGrid initialized")
    
    def transform(self, data: np.ndarray) -> np.ndarray:
        """在時空網格上變換數據"""
        if data.shape[0] >= self.dimension:
            transformed = np.dot(self.metric_tensor, data[:self.dimension])
            if len(data) > self.dimension:
                transformed = np.concatenate([transformed, data[self.dimension:]])
        else:
            padded = np.zeros(self.dimension)
            padded[:len(data)] = data
            transformed = np.dot(self.metric_tensor, padded)
        return transformed
    
    def get_order(self) -> float:
        return self.topology_order
