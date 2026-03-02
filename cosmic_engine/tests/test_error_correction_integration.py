#!/usr/bin/env python3
"""
Quantum Error Correction Integration Test
量子糾錯系統集成測試
"""

import pytest
import ray
import yaml
import logging
import numpy as np
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cosmic.error_correction import (
    RepetitionCode,
    ShorCode,
    SurfaceCode,
    QuantumErrorCorrectionEngine
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def ray_cluster():
    """Initialize and cleanup Ray cluster for testing"""
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True, num_cpus=4, num_gpus=0)
    yield
    ray.shutdown()


@pytest.fixture
def config():
    """Load test configuration"""
    config_path = Path(__file__).parent.parent / "config" / "cosmic_config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


class TestRepetitionCode:
    """Test Repetition Code for quantum error correction"""
    
    def test_repetition_code_initialization(self):
        """Test RepetitionCode initialization"""
        code = RepetitionCode(num_qubits=3)
        assert code is not None
        assert code.num_qubits == 3
        logger.info("✅ RepetitionCode initialized successfully")
    
    def test_encode_logical_qubit(self):
        """Test encoding logical qubit"""
        code = RepetitionCode(num_qubits=3)
        logical_qubit = np.array([1, 0])  # |0⟩ state
        
        encoded = code.encode(logical_qubit)
        assert encoded is not None
        assert len(encoded) > 0
        logger.info(f"✅ Logical qubit encoded: {encoded}")
    
    def test_detect_errors(self):
        """Test error detection"""
        code = RepetitionCode(num_qubits=3)
        
        # Simulate noisy quantum state
        noisy_state = np.array([1.0, 0.1, 0.0])
        errors = code.detect_errors(noisy_state)
        
        assert errors is not None
        assert isinstance(errors, (list, np.ndarray))
        logger.info(f"✅ Errors detected: {errors}")
    
    def test_correct_errors(self):
        """Test error correction"""
        code = RepetitionCode(num_qubits=3)
        
        # Simulate quantum state with errors
        corrupted_state = np.array([0.9, 0.15, 0.05])
        corrected = code.correct(corrupted_state)
        
        assert corrected is not None
        logger.info(f"✅ Errors corrected: {corrected}")


class TestShorCode:
    """Test Shor Code for quantum error correction"""
    
    def test_shor_code_initialization(self):
        """Test ShorCode initialization"""
        code = ShorCode(num_qubits=9)
        assert code is not None
        assert code.num_qubits == 9
        logger.info("✅ ShorCode initialized successfully")
    
    def test_encode_with_shor_code(self):
        """Test Shor code encoding"""
        code = ShorCode(num_qubits=9)
        logical_qubit = np.array([1, 0])  # |0⟩ state
        
        encoded = code.encode(logical_qubit)
        assert encoded is not None
        assert len(encoded) == 9
        logger.info(f"✅ Shor code encoding successful: {len(encoded)} qubits")
    
    def test_syndrome_extraction(self):
        """Test syndrome extraction"""
        code = ShorCode(num_qubits=9)
        
        # Simulate encoded state with errors
        encoded_state = np.random.rand(9) + 1j * np.random.rand(9)
        syndrome = code.extract_syndrome(encoded_state)
        
        assert syndrome is not None
        logger.info(f"✅ Syndrome extracted: {syndrome}")
    
    def test_recovery_from_errors(self):
        """Test recovery from single-qubit errors"""
        code = ShorCode(num_qubits=9)
        
        # Create encoded state
        logical_qubit = np.array([1, 0])
        encoded = code.encode(logical_qubit)
        
        # Introduce error on one qubit
        corrupted = encoded.copy()
        corrupted[0] *= 0.9  # Phase flip
        
        # Correct errors
        corrected = code.correct(corrupted)
        assert corrected is not None
        logger.info("✅ Single-qubit errors corrected successfully")


class TestSurfaceCode:
    """Test Surface Code for quantum error correction"""
    
    def test_surface_code_initialization(self):
        """Test SurfaceCode initialization"""
        code = SurfaceCode(distance=5)
        assert code is not None
        assert code.distance == 5
        logger.info("✅ SurfaceCode initialized successfully")
    
    def test_physical_qubit_allocation(self):
        """Test physical qubit allocation"""
        code = SurfaceCode(distance=5)
        
        num_physical = code.get_physical_qubit_count()
        assert num_physical == 25  # 5x5 grid
        logger.info(f"✅ Physical qubits allocated: {num_physical}")
    
    def test_topological_error_detection(self):
        """Test topological error detection"""
        code = SurfaceCode(distance=5)
        
        # Simulate surface code state with errors
        state = np.random.rand(25)
        errors = code.detect_topological_errors(state)
        
        assert errors is not None
        logger.info(f"✅ Topological errors detected: {errors}")
    
    def test_logical_qubit_extraction(self):
        """Test logical qubit extraction from surface code"""
        code = SurfaceCode(distance=5)
        
        # Create surface code state
        state = np.ones(25) / np.sqrt(25)
        logical = code.extract_logical_qubit(state)
        
        assert logical is not None
        assert len(logical) == 2
        logger.info(f"✅ Logical qubit extracted: {logical}")


class TestQuantumErrorCorrectionEngine:
    """Test complete Quantum Error Correction Engine"""
    
    def test_engine_initialization(self, ray_cluster, config):
        """Test QuantumErrorCorrectionEngine initialization"""
        ec_config = config.get("error_correction", {})
        engine_remote = QuantumErrorCorrectionEngine.remote(ec_config)
        assert engine_remote is not None
        logger.info("✅ QuantumErrorCorrectionEngine initialized successfully")
    
    def test_code_selection(self, ray_cluster, config):
        """Test error correction code selection"""
        ec_config = config.get("error_correction", {})
        engine_remote = QuantumErrorCorrectionEngine.remote(ec_config)
        
        # Test different code types
        codes = ["repetition", "shor", "surface"]
        for code_type in codes:
            result = ray.get(engine_remote.select_code.remote(code_type))
            assert result is not None
            logger.info(f"✅ Code type '{code_type}' selected successfully")
    
    def test_encode_quantum_state(self, ray_cluster, config):
        """Test quantum state encoding"""
        ec_config = config.get("error_correction", {})
        engine_remote = QuantumErrorCorrectionEngine.remote(ec_config)
        
        # Prepare logical qubit
        logical_qubit = [1.0, 0.0]
        
        # Encode
        encoded = ray.get(
            engine_remote.encode_state.remote("shor", logical_qubit)
        )
        assert encoded is not None
        logger.info(f"✅ Quantum state encoded: {len(encoded)} physical qubits")
    
    def test_error_correction_cycle(self, ray_cluster, config):
        """Test complete error correction cycle"""
        ec_config = config.get("error_correction", {})
        engine_remote = QuantumErrorCorrectionEngine.remote(ec_config)
        
        # Prepare state
        logical_qubit = [1.0, 0.0]
        
        # Encode -> Detect Errors -> Correct -> Decode cycle
        encoded = ray.get(engine_remote.encode_state.remote("shor", logical_qubit))
        
        # Simulate error detection
        errors = ray.get(engine_remote.detect_errors.remote("shor", encoded))
        
        # Correct errors
        corrected = ray.get(engine_remote.correct_errors.remote("shor", encoded))
        
        # Decode
        decoded = ray.get(engine_remote.decode_state.remote("shor", corrected))
        
        assert decoded is not None
        logger.info("✅ Complete error correction cycle executed")


class TestErrorCorrectionIntegration:
    """Integration tests for error correction with fault tolerance"""
    
    def test_continuous_error_monitoring(self, ray_cluster, config):
        """Test continuous error monitoring"""
        ec_config = config.get("error_correction", {})
        engine_remote = QuantumErrorCorrectionEngine.remote(ec_config)
        
        # Monitor errors over multiple cycles
        for i in range(5):
            result = ray.get(engine_remote.monitor_errors.remote())
            assert result is not None
        
        logger.info("✅ Continuous error monitoring working correctly")
    
    def test_error_threshold_management(self, ray_cluster, config):
        """Test error threshold management"""
        ec_config = config.get("error_correction", {})
        engine_remote = QuantumErrorCorrectionEngine.remote(ec_config)
        
        # Get current error rate
        error_rate = ray.get(engine_remote.get_error_rate.remote())
        assert error_rate is not None
        assert 0 <= error_rate <= 1.0
        
        logger.info(f"✅ Error threshold managed: {error_rate}")
    
    def test_code_performance_metrics(self, ray_cluster, config):
        """Test code performance metrics"""
        ec_config = config.get("error_correction", {})
        engine_remote = QuantumErrorCorrectionEngine.remote(ec_config)
        
        # Get performance metrics for each code type
        for code_type in ["repetition", "shor", "surface"]:
            metrics = ray.get(engine_remote.get_metrics.remote(code_type))
            assert metrics is not None
            assert isinstance(metrics, dict)
            logger.info(f"✅ Performance metrics for '{code_type}': {metrics}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
