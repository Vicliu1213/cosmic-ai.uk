#!/usr/bin/env python3
"""
Hybrid Quantum-Classical Trading Engine
混合量子-經典交易引擎

Dynamic Degradation Strategy:
- With Quantum: Use full quantum hybrid algorithms
- Without Quantum: Seamlessly fallback to enhanced classical algorithms
- With Partial Quantum: Use hybrid mode with best available resources

Architecture:
  1. HybridQuantumClassicalEngine: Main engine with auto-detection
  2. QuantumModeExecutor: Executes quantum algorithms
  3. ClassicalModeExecutor: Executes enhanced classical algorithms
  4. HybridModeExecutor: Blends quantum and classical
  5. CapabilityDetector: Auto-detects available quantum capabilities
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution mode enumeration"""
    FULL_QUANTUM = "full_quantum"           # 完整量子模式
    HYBRID = "hybrid"                       # 混合模式
    CLASSICAL = "classical"                 # 純經典模式


class QuantumCapability(Enum):
    """Quantum capability levels"""
    FULL_QUANTUM_AVAILABLE = "full"         # 完整量子可用
    PARTIAL_QUANTUM_AVAILABLE = "partial"   # 部分量子可用
    QUANTUM_UNAVAILABLE = "unavailable"     # 量子不可用


@dataclass
class CapabilityReport:
    """Quantum capability detection report"""
    quantum_available: bool
    capability_level: QuantumCapability
    available_qubits: int = 0
    quantum_coherence_time_us: float = 0.0
    classical_cpu_cores: int = 1
    execution_mode: ExecutionMode = ExecutionMode.CLASSICAL
    fallback_strategy: str = "enhanced_classical"
    detection_timestamp: float = field(default_factory=time.time)
    
    def __str__(self) -> str:
        """生成能力報告字符串"""
        mode_str = "🔴 Classical Only" if not self.quantum_available else "🟢 Quantum Available"
        return (
            f"{mode_str} | "
            f"Mode: {self.execution_mode.value} | "
            f"Qubits: {self.available_qubits} | "
            f"CPU Cores: {self.classical_cpu_cores}"
        )


class AlgorithmBase(ABC):
    """Base class for all trading algorithms"""
    
    def __init__(self, name: str):
        self.name = name
        self.execution_time = 0.0
        self.performance_metrics = {}
        
    @abstractmethod
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute algorithm on market data"""
        pass
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get algorithm performance metrics"""
        return {
            'name': self.name,
            'execution_time_ms': self.execution_time * 1000,
            'metrics': self.performance_metrics
        }


class QuantumModeExecutor(AlgorithmBase):
    """Quantum algorithm executor"""
    
    def __init__(self):
        super().__init__("QuantumModeExecutor")
        self.quantum_engine = None
        self.use_real_quantum = False
        
    def initialize_quantum(self, quantum_engine) -> bool:
        """Initialize quantum engine"""
        try:
            self.quantum_engine = quantum_engine
            self.use_real_quantum = True
            logger.info("✅ Quantum engine initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize quantum engine: {e}")
            self.use_real_quantum = False
            return False
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quantum algorithms"""
        start_time = time.time()
        
        if not self.use_real_quantum:
            logger.warning("⚠️ Quantum engine not available, cannot execute quantum mode")
            return {'status': 'error', 'message': 'Quantum engine unavailable'}
        
        try:
            # 執行量子算法
            results = {
                'mode': 'quantum',
                'symbol': market_data.get('symbol'),
                'signals': self._generate_quantum_signals(market_data),
                'confidence': self._calculate_quantum_confidence(market_data),
            }
            
            self.execution_time = time.time() - start_time
            logger.debug(f"Quantum execution completed in {self.execution_time:.4f}s")
            return results
            
        except Exception as e:
            logger.error(f"❌ Quantum execution failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_quantum_signals(self, market_data: Dict[str, Any]) -> List[float]:
        """Generate signals using quantum algorithms"""
        if self.quantum_engine is None:
            return []
        
        # 這裡調用實際的量子引擎
        try:
            signals = self.quantum_engine.generate_signals(market_data)
            return signals
        except Exception as e:
            logger.warning(f"Quantum signal generation failed: {e}")
            return []
    
    def _calculate_quantum_confidence(self, market_data: Dict[str, Any]) -> float:
        """Calculate confidence from quantum results"""
        if self.quantum_engine is None:
            return 0.0
        
        try:
            confidence = self.quantum_engine.calculate_confidence(market_data)
            return float(confidence)
        except:
            return 0.0


class ClassicalModeExecutor(AlgorithmBase):
    """Enhanced classical algorithm executor"""
    
    def __init__(self):
        super().__init__("ClassicalModeExecutor")
        self.classical_engine = None
        # Auto-initialize for standalone operation
        self.initialize_classical(None)
    
    def initialize_classical(self, classical_engine) -> bool:
        """Initialize enhanced classical engine"""
        try:
            self.classical_engine = classical_engine
            if classical_engine is not None:
                logger.info("✅ Enhanced classical engine initialized")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize classical engine: {e}")
            return False
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced classical algorithms"""
        start_time = time.time()
        
        try:
            # 執行增強經典算法
            results = {
                'mode': 'classical',
                'symbol': market_data.get('symbol'),
                'signals': self._generate_classical_signals(market_data),
                'confidence': self._calculate_classical_confidence(market_data),
                'ensemble_voting': self._ensemble_voting(market_data),
            }
            
            self.execution_time = time.time() - start_time
            logger.info(f"✅ Classical execution completed in {self.execution_time:.4f}s")
            return results
            
        except Exception as e:
            logger.error(f"❌ Classical execution failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_classical_signals(self, market_data: Dict[str, Any]) -> List[float]:
        """Generate signals using enhanced classical algorithms"""
        try:
            # 運行多個經典算法
            signals = []
            
            # 技術分析信號
            technical_signal = self._technical_analysis_signal(market_data)
            signals.append(technical_signal)
            
            # 統計套利信號
            statistical_signal = self._statistical_arbitrage_signal(market_data)
            signals.append(statistical_signal)
            
            # 機器學習信號
            ml_signal = self._machine_learning_signal(market_data)
            signals.append(ml_signal)
            
            # 集成信號
            ensemble_signal = np.mean(signals) if signals else 0.0
            
            return signals
            
        except Exception as e:
            logger.warning(f"Classical signal generation failed: {e}")
            return []
    
    def _technical_analysis_signal(self, market_data: Dict[str, Any]) -> float:
        """Technical analysis based signal"""
        try:
            close = np.array(market_data.get('close_prices', []))
            if len(close) < 20:
                return 0.0
            
            # RSI
            rsi = self._calculate_rsi(close)
            
            # MACD
            macd_value = self._calculate_macd(close)
            
            # 組合信號
            signal = (rsi / 100.0 - 0.5) * 0.5 + np.tanh(macd_value) * 0.5
            return float(np.clip(signal, -1, 1))
            
        except Exception as e:
            logger.debug(f"Technical analysis error: {e}")
            return 0.0
    
    def _statistical_arbitrage_signal(self, market_data: Dict[str, Any]) -> float:
        """Statistical arbitrage signal"""
        try:
            returns = np.diff(np.log(np.array(market_data.get('close_prices', []))))
            if len(returns) < 10:
                return 0.0
            
            # 計算自相關性
            autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
            
            # 均值回歸信號
            signal = -np.tanh(autocorr * 2.0)
            return float(np.clip(signal, -1, 1))
            
        except Exception as e:
            logger.debug(f"Statistical arbitrage error: {e}")
            return 0.0
    
    def _machine_learning_signal(self, market_data: Dict[str, Any]) -> float:
        """Machine learning based signal"""
        try:
            close = np.array(market_data.get('close_prices', []))
            if len(close) < 30:
                return 0.0
            
            # 簡單的趨勢檢測
            trend = np.polyfit(np.arange(len(close)), close, 1)[0]
            signal = np.tanh(trend / np.std(close)) if np.std(close) > 0 else 0.0
            
            return float(np.clip(signal, -1, 1))
            
        except Exception as e:
            logger.debug(f"ML signal error: {e}")
            return 0.0
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        return float(np.clip(rsi, 0, 100))
    
    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> float:
        """Calculate MACD"""
        if len(prices) < slow:
            return 0.0
        
        ema_fast = self._ema(prices, fast)[-1]
        ema_slow = self._ema(prices, slow)[-1]
        
        macd = ema_fast - ema_slow
        return float(macd)
    
    def _ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate EMA"""
        multiplier = 2.0 / (period + 1)
        ema = np.zeros(len(prices))
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = prices[i] * multiplier + ema[i-1] * (1 - multiplier)
        
        return ema
    
    def _calculate_classical_confidence(self, market_data: Dict[str, Any]) -> float:
        """Calculate confidence for classical algorithms"""
        try:
            close = np.array(market_data.get('close_prices', []))
            if len(close) < 20:
                return 0.5
            
            # 基於波動率的置信度
            returns = np.diff(np.log(close))
            volatility = np.std(returns)
            
            # 低波動 = 更高的置信度
            confidence = 1.0 / (1.0 + volatility)
            
            return float(np.clip(confidence, 0.0, 1.0))
            
        except Exception as e:
            logger.debug(f"Confidence calculation error: {e}")
            return 0.5
    
    def _ensemble_voting(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensemble voting results"""
        signals = self._generate_classical_signals(market_data)
        
        if not signals:
            return {'votes': [], 'consensus': 0.0, 'disagreement': 0.0}
        
        votes = [1 if s > 0 else -1 for s in signals]
        consensus = np.mean(votes)
        
        # 計算分歧度
        disagreement = 1.0 - np.abs(consensus)
        
        return {
            'votes': votes,
            'consensus': float(consensus),
            'disagreement': float(disagreement),
            'ensemble_signal': float(np.mean(signals))
        }


class HybridModeExecutor(AlgorithmBase):
    """Hybrid quantum-classical executor"""
    
    def __init__(self):
        super().__init__("HybridModeExecutor")
        self.quantum_executor = None
        self.classical_executor = None
        self.quantum_weight = 0.6
        self.classical_weight = 0.4
    
    def initialize(self, quantum_executor, classical_executor):
        """Initialize both executors"""
        self.quantum_executor = quantum_executor
        self.classical_executor = classical_executor
        logger.info("✅ Hybrid mode initialized with both executors")
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hybrid algorithm (quantum + classical)"""
        start_time = time.time()
        
        try:
            # 並行執行量子和經典算法
            quantum_result = self.quantum_executor.execute(market_data) if self.quantum_executor else {}
            classical_result = self.classical_executor.execute(market_data) if self.classical_executor else {}
            
            # 融合結果
            merged_result = self._merge_results(quantum_result, classical_result, market_data)
            
            self.execution_time = time.time() - start_time
            logger.info(f"✅ Hybrid execution completed in {self.execution_time:.4f}s")
            
            return merged_result
            
        except Exception as e:
            logger.error(f"❌ Hybrid execution failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _merge_results(self, quantum_result: Dict, classical_result: Dict, 
                      market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge quantum and classical results"""
        
        quantum_signals = quantum_result.get('signals', [])
        quantum_confidence = quantum_result.get('confidence', 0.0)
        
        classical_signals = classical_result.get('signals', [])
        classical_confidence = classical_result.get('confidence', 0.5)
        
        # 加權融合信號
        if quantum_signals and classical_signals:
            quantum_signal = np.mean(quantum_signals)
            classical_signal = np.mean(classical_signals)
            
            merged_signal = (quantum_signal * quantum_confidence * self.quantum_weight +
                           classical_signal * classical_confidence * self.classical_weight)
            
            confidence = (quantum_confidence * self.quantum_weight +
                        classical_confidence * self.classical_weight)
        elif quantum_signals:
            merged_signal = np.mean(quantum_signals)
            confidence = quantum_confidence
        else:
            merged_signal = np.mean(classical_signals) if classical_signals else 0.0
            confidence = classical_confidence
        
        return {
            'mode': 'hybrid',
            'symbol': market_data.get('symbol'),
            'quantum_signal': np.mean(quantum_signals) if quantum_signals else 0.0,
            'classical_signal': np.mean(classical_signals) if classical_signals else 0.0,
            'merged_signal': float(merged_signal),
            'quantum_confidence': float(quantum_confidence),
            'classical_confidence': float(classical_confidence),
            'hybrid_confidence': float(confidence),
            'quantum_weight': self.quantum_weight,
            'classical_weight': self.classical_weight,
        }


class CapabilityDetector:
    """Auto-detect quantum and classical capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_capabilities(self) -> CapabilityReport:
        """Detect available quantum and classical capabilities"""
        
        # 檢測量子可用性
        quantum_available = self._check_quantum_availability()
        capability_level = self._determine_capability_level(quantum_available)
        
        # 獲取可用資源
        available_qubits = self._get_available_qubits() if quantum_available else 0
        coherence_time = self._get_quantum_coherence_time() if quantum_available else 0.0
        cpu_cores = self._get_cpu_cores()
        
        # 決定執行模式
        execution_mode = self._choose_execution_mode(capability_level)
        
        report = CapabilityReport(
            quantum_available=quantum_available,
            capability_level=capability_level,
            available_qubits=available_qubits,
            quantum_coherence_time_us=coherence_time,
            classical_cpu_cores=cpu_cores,
            execution_mode=execution_mode,
            fallback_strategy="enhanced_classical" if not quantum_available else "hybrid"
        )
        
        self.logger.info(f"Capability Detection: {report}")
        return report
    
    def _check_quantum_availability(self) -> bool:
        """Check if quantum hardware/simulator is available"""
        try:
            # 嘗試導入量子框架
            try:
                import qiskit
                self.logger.info("✅ Qiskit available")
                return True
            except ImportError:
                pass
            
            try:
                import cirq
                self.logger.info("✅ Cirq available")
                return True
            except ImportError:
                pass
            
            try:
                import pennylane
                self.logger.info("✅ PennyLane available")
                return True
            except ImportError:
                pass
            
            # 沒有找到量子框架
            self.logger.warning("⚠️ No quantum framework available, using classical fallback")
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Quantum detection failed: {e}")
            return False
    
    def _determine_capability_level(self, quantum_available: bool) -> QuantumCapability:
        """Determine quantum capability level"""
        if not quantum_available:
            return QuantumCapability.QUANTUM_UNAVAILABLE
        
        # 檢查是否有真實量子硬件或足夠的模擬器
        try:
            import qiskit
            from qiskit_ibm_runtime import QiskitRuntimeService
            service = QiskitRuntimeService()
            if service is not None:
                return QuantumCapability.FULL_QUANTUM_AVAILABLE
        except:
            pass
        
        return QuantumCapability.PARTIAL_QUANTUM_AVAILABLE
    
    def _get_available_qubits(self) -> int:
        """Get number of available qubits"""
        try:
            import qiskit
            return 10  # 默認值
        except:
            return 0
    
    def _get_quantum_coherence_time(self) -> float:
        """Get quantum coherence time in microseconds"""
        try:
            import qiskit
            return 100.0  # 默認值
        except:
            return 0.0
    
    def _get_cpu_cores(self) -> int:
        """Get number of CPU cores"""
        import os
        return os.cpu_count() or 1
    
    def _choose_execution_mode(self, capability_level: QuantumCapability) -> ExecutionMode:
        """Choose best execution mode based on capabilities"""
        if capability_level == QuantumCapability.FULL_QUANTUM_AVAILABLE:
            return ExecutionMode.FULL_QUANTUM
        elif capability_level == QuantumCapability.PARTIAL_QUANTUM_AVAILABLE:
            return ExecutionMode.HYBRID
        else:
            return ExecutionMode.CLASSICAL


class HybridQuantumClassicalEngine:
    """
    Main Hybrid Quantum-Classical Trading Engine
    主混合量子-經典交易引擎
    
    自動檢測並利用可用的量子資源，無量子時無縫退到增強經典算法
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.capability_detector = CapabilityDetector()
        self.capability_report = None
        self.execution_mode = ExecutionMode.CLASSICAL
        
        self.quantum_executor = QuantumModeExecutor()
        self.classical_executor = ClassicalModeExecutor()
        self.hybrid_executor = HybridModeExecutor()
        
        self.initialized = False
        self.execution_history = []
    
    def initialize(self, quantum_engine=None, classical_engine=None) -> bool:
        """Initialize the hybrid engine"""
        try:
            # 檢測可用能力
            self.capability_report = self.capability_detector.detect_capabilities()
            self.execution_mode = self.capability_report.execution_mode
            
            # 初始化量子執行器
            if quantum_engine is not None:
                self.quantum_executor.initialize_quantum(quantum_engine)
            
            # 初始化經典執行器（總是初始化，即使 classical_engine=None）
            self.classical_executor.initialize_classical(classical_engine)
            
            # 初始化混合執行器
            self.hybrid_executor.initialize(self.quantum_executor, self.classical_executor)
            
            self.initialized = True
            self.logger.info(
                f"✅ Hybrid Engine initialized in {self.execution_mode.value} mode"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Hybrid Engine initialization failed: {e}")
            return False
    
    def execute(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trading algorithm with automatic mode selection
        
        自動選擇最佳執行模式：
        - 量子可用 + 經典可用 -> 混合模式 (最佳性能)
        - 僅量子可用 -> 量子模式
        - 僅經典可用 -> 經典模式 (優雅降級)
        - 都不可用 -> 錯誤返回
        """
        
        if not self.initialized:
            return {'status': 'error', 'message': 'Engine not initialized'}
        
        try:
            # 根據當前模式選擇執行器
            if self.execution_mode == ExecutionMode.FULL_QUANTUM:
                result = self.quantum_executor.execute(market_data)
            elif self.execution_mode == ExecutionMode.HYBRID:
                result = self.hybrid_executor.execute(market_data)
            else:  # CLASSICAL
                result = self.classical_executor.execute(market_data)
            
            # 記錄執行歷史
            self.execution_history.append({
                'mode': self.execution_mode.value,
                'timestamp': time.time(),
                'result': result
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Execution failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            'initialized': self.initialized,
            'execution_mode': self.execution_mode.value,
            'capability_report': {
                'quantum_available': self.capability_report.quantum_available if self.capability_report else False,
                'capability_level': self.capability_report.capability_level.value if self.capability_report else 'unknown',
                'available_qubits': self.capability_report.available_qubits if self.capability_report else 0,
                'cpu_cores': self.capability_report.classical_cpu_cores if self.capability_report else 0,
            },
            'executors': {
                'quantum': self.quantum_executor.get_performance_metrics(),
                'classical': self.classical_executor.get_performance_metrics(),
                'hybrid': self.hybrid_executor.get_performance_metrics(),
            },
            'execution_count': len(self.execution_history),
        }
    
    def switch_mode(self, target_mode: ExecutionMode) -> bool:
        """Manually switch execution mode"""
        try:
            self.execution_mode = target_mode
            self.logger.info(f"✅ Switched to {target_mode.value} mode")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to switch mode: {e}")
            return False
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history"""
        return self.execution_history[-limit:]


# 全局實例
_hybrid_engine: Optional[HybridQuantumClassicalEngine] = None


def get_hybrid_engine() -> HybridQuantumClassicalEngine:
    """Get or create the global hybrid engine"""
    global _hybrid_engine
    if _hybrid_engine is None:
        _hybrid_engine = HybridQuantumClassicalEngine()
    return _hybrid_engine


if __name__ == "__main__":
    # 測試混合引擎
    logging.basicConfig(level=logging.INFO)
    
    engine = get_hybrid_engine()
    
    # 初始化
    engine.initialize()
    
    # 模擬市場數據
    market_data = {
        'symbol': 'BTCUSDT',
        'close_prices': np.random.randn(100).cumsum() + 40000,
        'volume': np.random.rand(100) * 1000,
    }
    
    # 執行
    result = engine.execute(market_data)
    print("\n" + "="*60)
    print("HYBRID QUANTUM-CLASSICAL ENGINE TEST RESULT")
    print("="*60)
    print(f"Mode: {result.get('mode', 'unknown')}")
    
    # 獲取信號值
    if result.get('mode') == 'classical':
        signals = result.get('signals', [])
        signal_value = signals[0] if signals else 0.0
    else:
        signal_value = result.get('merged_signal', 0.0)
    
    print(f"Signal: {signal_value:.4f}")
    
    # 獲取置信度
    if result.get('mode') == 'classical':
        confidence = result.get('confidence', 0.0)
    else:
        confidence = result.get('hybrid_confidence', result.get('confidence', 0.0))
    
    print(f"Confidence: {confidence:.2%}")
    
    # 顯示狀態
    print("\n" + "-"*60)
    print("ENGINE STATUS")
    print("-"*60)
    status = engine.get_status()
    print(f"Execution Mode: {status['execution_mode']}")
    print(f"Quantum Available: {status['capability_report']['quantum_available']}")
    print(f"Available Qubits: {status['capability_report']['available_qubits']}")
    print(f"CPU Cores: {status['capability_report']['cpu_cores']}")
    print(f"Execution Count: {status['execution_count']}")
    print("="*60 + "\n")
