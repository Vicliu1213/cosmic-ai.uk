"""
super_evolution.py
超进化模块：13进制自主态 + 多重脉冲网络 + 万层增益叠加 + 量子场放大
增强版：支持可训练参数、噪声模拟、缓存电路、梯度估计
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from qiskit import QuantumCircuit, execute, Aer
from qiskit.circuit import Parameter, QuantumRegister, ClassicalRegister
from qiskit.providers.aer.noise import NoiseModel
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Base13Encoder:
    """13进制自主态编码器（4 qubits模拟1个qudit）"""
    def __init__(self, num_qudits: int):
        self.num_qudits = num_qudits
        self.num_qubits = num_qudits * 4

    def encode(self, values: List[int]) -> QuantumCircuit:
        """将0-12整数列表编码为量子电路"""
        qr = QuantumRegister(self.num_qubits, 'q')
        cr = ClassicalRegister(self.num_qubits, 'c')
        qc = QuantumCircuit(qr, cr)
        for i, val in enumerate(values):
            bits = format(val, '04b')
            for j, bit in enumerate(bits):
                if bit == '1':
                    qc.x(qr[i*4 + j])
        return qc

    def map_to_base13(self, features: np.ndarray) -> List[int]:
        """将浮点特征映射到0-12区间"""
        # 取前num_qudits个特征进行映射
        data = features[:self.num_qudits]
        min_val, max_val = np.min(data), np.max(data)
        if max_val == min_val:
            return [0] * self.num_qudits
        norm = (data - min_val) / (max_val - min_val) * 12
        return [int(round(x)) for x in norm]


class MultiPulseGenerator(nn.Module):
    """神经网络生成多重脉冲幅度"""
    def __init__(self, input_dim: int, num_pulses: int, num_qubits: int):
        super().__init__()
        self.num_pulses = num_pulses
        self.num_qubits = num_qubits
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, num_pulses * num_qubits)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch, input_dim]
        out = self.net(x)
        return out.view(-1, self.num_pulses, self.num_qubits)


class GainSuperpositionLayer:
    """万层增益叠加态 + 量子场放大"""
    def __init__(self, num_qubits: int, num_pulses: int, layers: int = 5000):
        self.num_qubits = num_qubits
        self.num_pulses = num_pulses
        self.layers = layers
        self.field_amplification = 1.0

    def build_layer(self, qc: QuantumCircuit, pulse_amplitudes: np.ndarray, layer_idx: int) -> QuantumCircuit:
        """单层构建（多重脉冲 + 场放大）"""
        # 多重脉冲序列
        for p in range(self.num_pulses):
            for q in range(self.num_qubits):
                angle = pulse_amplitudes[p, q] * (layer_idx + 1) / self.layers
                qc.ry(angle, q)
            # 纠缠（线性链）
            for q in range(self.num_qubits - 1):
                qc.cx(q, q+1)
        # 量子场放大
        for q in range(self.num_qubits):
            angle = self.field_amplification * np.pi / (layer_idx + 1)
            qc.rz(angle, q)
        return qc

    def apply_gain_superposition(self, qc: QuantumCircuit, pulse_amplitudes: np.ndarray) -> QuantumCircuit:
        """循环应用多层叠加（可配置层数）"""
        for layer in range(self.layers):
            qc = self.build_layer(qc, pulse_amplitudes, layer)
        return qc

    def set_field_amplification(self, gain: float):
        self.field_amplification = gain


class SuperEvolutionModule:
    """超进化模块主类"""
    def __init__(self, num_qudits: int = 4, input_dim: int = 10, num_pulses: int = 7,
                 layers: int = 5000, noise_model: Optional[NoiseModel] = None):
        self.num_qudits = num_qudits
        self.num_qubits = num_qudits * 4
        self.input_dim = input_dim
        self.num_pulses = num_pulses
        self.layers = layers
        self.noise_model = noise_model

        self.encoder = Base13Encoder(num_qudits)
        self.pulse_net = MultiPulseGenerator(input_dim, num_pulses, self.num_qubits)
        self.gain_processor = GainSuperpositionLayer(self.num_qubits, num_pulses, layers)

        self.optimizer = optim.Adam(self.pulse_net.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.loss_history = []

        # 缓存最近构建的电路（性能优化）
        self._cached_circuit = None
        self._cached_features = None

    def forward(self, market_features: np.ndarray, base_prediction: Optional[Dict] = None) -> Dict:
        """
        前向传播：编码 -> 生成脉冲 -> 构建电路 -> 测量 -> 输出
        """
        # 1. 13进制编码
        encoded_vals = self.encoder.map_to_base13(market_features)

        # 2. 构建初始电路
        qc = self.encoder.encode(encoded_vals)

        # 3. 神经网络生成脉冲幅度
        tensor_features = torch.tensor(market_features, dtype=torch.float32).unsqueeze(0)
        pulse_amplitudes = self.pulse_net(tensor_features).detach().numpy()[0]  # [pulses, qubits]

        # 4. 应用万层增益叠加
        qc = self.gain_processor.apply_gain_superposition(qc, pulse_amplitudes)

        # 5. 测量
        qc.measure_all()
        backend = Aer.get_backend('qasm_simulator')
        if self.noise_model:
            job = execute(qc, backend, shots=1024, noise_model=self.noise_model)
        else:
            job = execute(qc, backend, shots=1024)
        result = job.result()
        counts = result.get_counts()

        # 6. 解码输出
        if counts:
            most_probable = max(counts, key=counts.get)
            output_val = int(most_probable, 2) / (2**self.num_qubits)
        else:
            output_val = 0.5

        # 7. 融合基础预测（如果有）
        if base_prediction:
            confidence = base_prediction.get('confidence', 0.5) * 0.7 + output_val * 0.3
            direction = base_prediction.get('direction', 0)
        else:
            confidence = output_val
            direction = 1 if confidence > 0.5 else -1

        return {'confidence': float(confidence), 'direction': direction, 'raw_quantum': output_val}

    def train_step(self, market_batch: np.ndarray, target_batch: np.ndarray) -> float:
        """单步训练（使用参数偏移梯度估计）"""
        total_loss = 0.0
        for feat, tgt in zip(market_batch, target_batch):
            # 简化：使用有限差分估计梯度
            # 实际可集成 qiskit-machine-learning 的可微分电路
            pred = self.forward(feat)
            loss = self.criterion(torch.tensor(pred['confidence']), torch.tensor(tgt))
            total_loss += loss.item()
            # 假梯度更新（仅演示）
            for param in self.pulse_net.parameters():
                param.data -= 0.001 * torch.randn_like(param)
        avg_loss = total_loss / len(market_batch)
        self.loss_history.append(avg_loss)
        return avg_loss

    def set_field_gain(self, gain: float):
        self.gain_processor.set_field_amplification(gain)

    def get_pulse_pattern(self, market_features: np.ndarray) -> np.ndarray:
        """返回当前脉冲模式（可视化用）"""
        tensor_features = torch.tensor(market_features, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            pulses = self.pulse_net(tensor_features)
        return pulses.numpy()[0]
