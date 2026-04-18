#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子纠错编码系统 - 用于 Cosmic Engine
Quantum Error Correction System for Cosmic Engine

实现多种纠错码用于保护系统状态：
- 3-比特重复码
- 9-比特 Shor 码
- 表面码
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """错误类型"""
    BIT_FLIP = "bit_flip"           # 比特翻转
    PHASE_FLIP = "phase_flip"       # 相位翻转
    AMPLITUDE_DAMP = "amplitude_damp"  # 振幅阻尼
    PHASE_DAMP = "phase_damp"       # 相位阻尼
    DEPOLARIZING = "depolarizing"   # 去极化


class CodeType(Enum):
    """纠错码类型"""
    REPETITION = "repetition_3"     # 3-比特重复码
    SHOR = "shor_9"                 # 9-比特 Shor 码
    SURFACE = "surface"              # 表面码


@dataclass
class ErrorSyndrome:
    """错误综合症"""
    syndrome_bits: List[int]         # 综合症比特
    error_type: Optional[ErrorType] = None
    confidence: float = 0.0          # 诊断信心度
    estimated_error_location: Optional[int] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False


@dataclass
class QuantumState:
    """量子状态"""
    qubits: np.ndarray              # 物理量子比特
    logical_state: Optional[int] = None  # 逻辑比特 (0 或 1)
    encoding_type: CodeType = CodeType.REPETITION
    error_history: List[Dict] = field(default_factory=list)


class ErrorCorrectionCodec:
    """纠错编码解码器基类"""
    
    def __init__(self, code_type: CodeType):
        self.code_type = code_type
        self.syndrome_table: Dict[tuple, int] = {}
        self.performance_stats = {
            'corrections_attempted': 0,
            'corrections_successful': 0,
            'detection_rate': 0.0
        }
    
    def encode(self, logical_bit: int) -> np.ndarray:
        """编码逻辑比特到物理比特"""
        raise NotImplementedError
    
    def extract_syndrome(self, physical_state: np.ndarray) -> ErrorSyndrome:
        """提取错误综合症"""
        raise NotImplementedError
    
    def correct(
        self,
        physical_state: np.ndarray,
        syndrome: ErrorSyndrome
    ) -> np.ndarray:
        """纠正错误"""
        raise NotImplementedError
    
    def decode(self, physical_state: np.ndarray) -> int:
        """解码物理状态到逻辑比特"""
        raise NotImplementedError


class RepetitionCode(ErrorCorrectionCodec):
    """3-比特重复码实现"""
    
    def __init__(self, num_qubits: int = 3):
        super().__init__(CodeType.REPETITION)
        self.physical_qubits = num_qubits if num_qubits > 0 else 3
        self.num_qubits = self.physical_qubits  # 兼容性別名
        # 简单的综合症表
        self.syndrome_table = {
            (0, 0): 0,    # 无错误
            (1, 0): 1,    # 第1比特翻转
            (0, 1): 2,    # 第2比特翻转
            (1, 1): 3,    # 第3比特翻转
        }
    
    def encode(self, logical_bit: int) -> np.ndarray:
        """编码逻辑比特"""
        # 支持数组输入，提取第一个元素
        if isinstance(logical_bit, np.ndarray):
            logical_bit = int(logical_bit[0])
        else:
            logical_bit = int(logical_bit)
        if logical_bit == 0:
            return np.array([0, 0, 0])
        else:
            return np.array([1, 1, 1])
    
    def extract_syndrome(self, physical_state: np.ndarray) -> ErrorSyndrome:
        """提取综合症"""
        # 计算奇偶性
        # 转换复数为实数 (取绝对值)
        if np.iscomplexobj(physical_state):
            physical_state = np.abs(physical_state)
        
        parity_1 = int(physical_state[0] + physical_state[1] >= 1.0) % 2
        parity_2 = int(physical_state[1] + physical_state[2] >= 1.0) % 2
        
        syndrome_bits = [parity_1, parity_2]
        syndrome_tuple = tuple(syndrome_bits)
        
        # 确定错误位置
        error_location = self.syndrome_table.get(syndrome_tuple, 0)
        
        return ErrorSyndrome(
            syndrome_bits=syndrome_bits,
            error_type=ErrorType.BIT_FLIP if error_location > 0 else None,
            confidence=0.95 if error_location > 0 else 1.0,
            estimated_error_location=error_location if error_location > 0 else None
        )
    
    def detect_errors(self, physical_state: np.ndarray) -> List[int]:
        """检测错误 - 返回错误列表，兼容测试接口"""
        syndrome = self.extract_syndrome(physical_state)
        return syndrome.syndrome_bits
    
    def correct(
        self,
        physical_state: np.ndarray,
        syndrome: Optional[ErrorSyndrome] = None
    ) -> np.ndarray:
        """纠正错误"""
        
        # 如果没有提供 syndrome，则提取它
        if syndrome is None:
            syndrome = self.extract_syndrome(physical_state)
        
        self.performance_stats['corrections_attempted'] += 1
        
        corrected = physical_state.copy()
        
        if syndrome.estimated_error_location and syndrome.estimated_error_location > 0:
            # 翻转错误的比特
            error_idx = syndrome.estimated_error_location - 1
            if 0 <= error_idx < len(corrected):
                corrected[error_idx] = 1 - corrected[error_idx]
                self.performance_stats['corrections_successful'] += 1
                syndrome.recovery_successful = True
        
        syndrome.recovery_attempted = True
        return corrected
    
    def decode(self, physical_state: np.ndarray) -> int:
        """解码"""
        # 多数投票
        majority = np.sum(physical_state) >= 2
        return 1 if majority else 0


class ShorCode(ErrorCorrectionCodec):
    """9-比特 Shor 码实现"""
    
    def __init__(self, num_qubits: int = 9):
        super().__init__(CodeType.SHOR)
        self.physical_qubits = num_qubits if num_qubits > 0 else 9
        self.num_qubits = self.physical_qubits  # 兼容性別名
    
    def encode(self, logical_bit: int) -> np.ndarray:
        """编码逻辑比特"""
        # 支持数组输入，提取第一个元素
        if isinstance(logical_bit, np.ndarray):
            logical_bit = int(logical_bit[0])
        else:
            logical_bit = int(logical_bit)
        if logical_bit == 0:
            # |0⟩_L = (|000⟩ + |111⟩) ⊗ (|000⟩ + |111⟩) ⊗ (|000⟩ + |111⟩)
            # 简化：3组，每组3个比特
            return np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
        else:
            # |1⟩_L = (|000⟩ - |111⟩) ⊗ (|000⟩ - |111⟩) ⊗ (|000⟩ - |111⟩)
            # 简化：3组，每组3个比特翻转
            return np.array([1, 1, 1, 1, 1, 1, 1, 1, 1])
    
    def extract_syndrome(self, physical_state: np.ndarray) -> ErrorSyndrome:
        """提取综合症"""
        # 对于每组计算奇偶性
        syndromes = []
        
        # 转换复数为实数 (取绝对值)
        if np.iscomplexobj(physical_state):
            physical_state = np.abs(physical_state)
        
        for group in range(3):
            start = group * 3
            end = start + 3
            group_bits = physical_state[start:end]
            
            # 检测比特翻转 (使用整数转换避免模运算错误)
            parity = int(np.sum(group_bits) >= 1.5) % 2  # 如果和 >= 1.5，认为是 1
            syndromes.append(parity)
        
        # 检测相位翻转
        phase_syndrome = (
            (int(physical_state[0] + physical_state[3] + physical_state[6] >= 1.5) % 2),
            (int(physical_state[1] + physical_state[4] + physical_state[7] >= 1.5) % 2)
        )
        
        return ErrorSyndrome(
            syndrome_bits=syndromes + list(phase_syndrome),
            error_type=ErrorType.BIT_FLIP if sum(syndromes) > 0 else ErrorType.PHASE_FLIP,
            confidence=0.99,
            estimated_error_location=int(np.argmax(syndromes)) if sum(syndromes) > 0 else None
        )
    
    def detect_errors(self, physical_state: np.ndarray) -> List[int]:
        """检测错误 - 返回错误列表，兼容测试接口"""
        syndrome = self.extract_syndrome(physical_state)
        return syndrome.syndrome_bits
    
    def correct(
        self,
        physical_state: np.ndarray,
        syndrome: Optional[ErrorSyndrome] = None
    ) -> np.ndarray:
        """纠正错误"""
        
        # 如果没有提供 syndrome，则提取它
        if syndrome is None:
            syndrome = self.extract_syndrome(physical_state)
        
        self.performance_stats['corrections_attempted'] += 1
        
        corrected = physical_state.copy()
        
        if syndrome.estimated_error_location is not None:
            # 根据综合症纠正
            for i in range(len(corrected)):
                if syndrome.syndrome_bits[i % 3] and i == syndrome.estimated_error_location:
                    corrected[i] = 1 - corrected[i]
                    self.performance_stats['corrections_successful'] += 1
        
        syndrome.recovery_attempted = True
        return corrected
    
    def decode(self, physical_state: np.ndarray) -> int:
        """解码"""
        # 多数投票对每组
        votes = []
        for group in range(3):
            start = group * 3
            group_sum = np.sum(physical_state[start:start+3])
            votes.append(1 if group_sum >= 2 else 0)
        
        # 最终多数投票
        final_vote = np.sum(votes) >= 2
        return 1 if final_vote else 0


class SurfaceCode(ErrorCorrectionCodec):
    """表面码实现 (简化版)"""
    
    def __init__(self, distance: int = None, num_qubits: int = None, lattice_size: int = 5):
        super().__init__(CodeType.SURFACE)
        # 支持多种参数方式
        if distance is not None:
            self.distance = distance
            self.lattice_size = distance
        elif num_qubits is not None:
            self.lattice_size = int(np.sqrt(num_qubits)) if num_qubits > 0 else 5
            self.distance = self.lattice_size
        elif lattice_size is not None and lattice_size > 0:
            self.lattice_size = lattice_size
            self.distance = lattice_size
        else:
            self.distance = 5
            self.lattice_size = 5
        
        self.physical_qubits = self.lattice_size * self.lattice_size
        self.num_qubits = self.physical_qubits  # 兼容性別名
        self.plaquette_operators = []
        self.vertex_operators = []
    
    def encode(self, logical_bit: int) -> np.ndarray:
        """编码"""
        # 支持数组输入，提取第一个元素
        if isinstance(logical_bit, np.ndarray):
            logical_bit = int(logical_bit[0])
        else:
            logical_bit = int(logical_bit)
        state = np.zeros(self.physical_qubits)
        if logical_bit == 1:
            state[:] = 1
        return state
    
    def extract_syndrome(self, physical_state: np.ndarray) -> ErrorSyndrome:
        """提取综合症"""
        # 简化的表面码综合症提取
        # 转换复数为实数 (取绝对值)
        if np.iscomplexobj(physical_state):
            physical_state = np.abs(physical_state)
        
        syndrome_bits = []
        
        for i in range(0, min(4, len(physical_state))):
            # 计算周围比特的奇偶性
            neighbors = [
                (i-1) % len(physical_state),
                (i+1) % len(physical_state)
            ]
            parity = int(sum(physical_state[n] for n in neighbors) >= 1.0) % 2
            syndrome_bits.append(parity)
        
        return ErrorSyndrome(
            syndrome_bits=syndrome_bits,
            error_type=ErrorType.BIT_FLIP if sum(syndrome_bits) > 0 else None,
            confidence=0.98
        )
    
    def detect_errors(self, physical_state: np.ndarray) -> List[int]:
        """检测错误 - 返回错误列表，兼容测试接口"""
        syndrome = self.extract_syndrome(physical_state)
        return syndrome.syndrome_bits
    
    def correct(
        self,
        physical_state: np.ndarray,
        syndrome: Optional[ErrorSyndrome] = None
    ) -> np.ndarray:
        """纠正错误"""
        
        # 如果没有提供 syndrome，则提取它
        if syndrome is None:
            syndrome = self.extract_syndrome(physical_state)
        
        self.performance_stats['corrections_attempted'] += 1
        
        corrected = physical_state.copy()
        
        # 根据综合症找到并纠正错误
        for i, bit in enumerate(syndrome.syndrome_bits):
            if bit and i < len(corrected):
                corrected[i] = 1 - corrected[i]
                self.performance_stats['corrections_successful'] += 1
        
        syndrome.recovery_attempted = True
        return corrected
    
    def decode(self, physical_state: np.ndarray) -> int:
        """解码"""
        return 1 if np.mean(physical_state) >= 0.5 else 0
    
    def get_physical_qubit_count(self) -> int:
        """获取物理比特数"""
        return self.physical_qubits
    
    def detect_topological_errors(self, state: np.ndarray) -> List[int]:
        """检测拓扑错误"""
        syndrome = self.extract_syndrome(state)
        return syndrome.syndrome_bits
    
    def extract_logical_qubit(self, state: np.ndarray) -> np.ndarray:
        """提取逻辑比特"""
        # 简化：返回两个复数表示逻辑比特的 |0⟩ 和 |1⟩ 成分
        return np.array([np.mean(state), 1.0 - np.mean(state)])


class QuantumErrorCorrectionEngine:
    """量子纠错引擎"""
    
    def __init__(self, code_type: CodeType = CodeType.REPETITION):
        if code_type == CodeType.REPETITION:
            self.codec = RepetitionCode()
        elif code_type == CodeType.SHOR:
            self.codec = ShorCode()
        elif code_type == CodeType.SURFACE:
            self.codec = SurfaceCode()
        else:
            self.codec = RepetitionCode()
        
        self.encoded_states: Dict[str, QuantumState] = {}
        self.correction_history = []
    
    def encode_state(self, state_id: str, logical_bit: int) -> QuantumState:
        """编码量子态"""
        physical_qubits = self.codec.encode(logical_bit)
        
        quantum_state = QuantumState(
            qubits=physical_qubits,
            logical_state=logical_bit,
            encoding_type=self.codec.code_type
        )
        
        self.encoded_states[state_id] = quantum_state
        logger.info(f"✅ 编码状态 - ID: {state_id}, 逻辑位: {logical_bit}")
        
        return quantum_state
    
    def detect_and_correct(self, state_id: str) -> Tuple[bool, int]:
        """检测并纠正错误"""
        
        if state_id not in self.encoded_states:
            logger.error(f"状态不存在: {state_id}")
            return False, -1
        
        quantum_state = self.encoded_states[state_id]
        
        # 步骤1: 提取综合症
        syndrome = self.codec.extract_syndrome(quantum_state.qubits)
        
        # 步骤2: 纠正错误
        corrected_qubits = self.codec.correct(quantum_state.qubits, syndrome)
        
        # 步骤3: 解码
        decoded_bit = self.codec.decode(corrected_qubits)
        
        # 更新状态
        quantum_state.qubits = corrected_qubits
        quantum_state.error_history.append({
            'timestamp': datetime.now().isoformat(),
            'syndrome': syndrome.syndrome_bits,
            'corrected': syndrome.recovery_successful,
            'decoded_bit': decoded_bit
        })
        
        # 记录
        self.correction_history.append({
            'state_id': state_id,
            'syndrome': syndrome.syndrome_bits,
            'success': syndrome.recovery_successful,
            'decoded_bit': decoded_bit,
            'timestamp': datetime.now().isoformat()
        })
        
        if syndrome.recovery_successful:
            logger.info(f"✅ 纠错成功 - ID: {state_id}")
        
        return syndrome.recovery_successful, decoded_bit
    
    def get_correction_stats(self) -> Dict[str, Any]:
        """获取纠错统计"""
        total = self.codec.performance_stats['corrections_attempted']
        successful = self.codec.performance_stats['corrections_successful']
        
        return {
            'code_type': self.codec.code_type.value,
            'total_corrections': total,
            'successful_corrections': successful,
            'success_rate': successful / total if total > 0 else 0,
            'recent_corrections': self.correction_history[-10:]
        }


# 导出主类
__all__ = [
    'QuantumErrorCorrectionEngine',
    'RepetitionCode',
    'ShorCode',
    'SurfaceCode',
    'QuantumState',
    'ErrorSyndrome',
    'ErrorType',
    'CodeType'
]
