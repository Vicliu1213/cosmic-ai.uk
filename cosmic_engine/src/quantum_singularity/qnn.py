"""量子神經網絡 (Quantum Neural Network)"""
import numpy as np
import logging

logger = logging.getLogger(__name__)


class QuantumNeuralNet:
    """量子神經網絡"""
    
    def __init__(self, input_dim: int = 4, hidden_dim: int = 8):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.weights = np.random.randn(input_dim, hidden_dim) * 0.1
        
    def initialize(self):
        logger.info(f"QuantumNeuralNet initialized")
    
    def forward(self, data: np.ndarray) -> np.ndarray:
        """前向傳播"""
        if len(data) == 0:
            return np.zeros(self.hidden_dim)
        
        # 簡單的矩陣乘法
        if len(data.shape) == 1:
            if data.shape[0] >= self.input_dim:
                return np.dot(data[:self.input_dim], self.weights)
            else:
                padded = np.zeros(self.input_dim)
                padded[:len(data)] = data
                return np.dot(padded, self.weights)
        return np.zeros(self.hidden_dim)
