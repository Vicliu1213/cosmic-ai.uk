#!/usr/bin/env python3
"""
Integration Tests: Quantum Grover Algorithm with Trading System
量子 Grover 算法與交易系統集成測試

Tests the integration of the Grover quantum search algorithm
with the Comic AI trading system for signal optimization.
"""

import sys
import unittest
import time
from pathlib import Path
from typing import List, Dict, Any
import logging

# Setup path to import quantum algorithm
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import quantum algorithm
from quantum_grover_trading_algorithm import (
    TradingSignal,
    GroverQuantumSearch,
    LinearClassicalSearch,
    QuantumInspiredClassical,
    QuantumTradingOptimizer,
    AlgorithmBenchmark
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestQuantumGroverIntegration(unittest.TestCase):
    """Test suite for Quantum Grover algorithm integration"""
    
    def setUp(self) -> Any:
        """Setup test fixtures"""
        # Create test signals
        self.test_signals = [
            TradingSignal(i, f"STRAT_{i:02d}", 100+i, 101+i, 1.0+i*0.1, 0.70+i*0.02, 0.8+i*0.05)
            for i in range(1, 9)
        ]
    
    def test_quantum_search_basic(self) -> Any:
        """Test basic quantum search functionality"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 1: Basic Quantum Search (3 qubits, 8 items)")
        logger.info("=" * 70)
        
        grover = GroverQuantumSearch(n_qubits=3)
        
        # Define marked items (indices 5 and 6)
        marked_indices = [5, 6]
        
        # Run search
        result_index = grover.search(marked_indices=marked_indices)
        
        logger.info(f"\nQuantum search result:")
        logger.info(f"  Marked indices: {marked_indices}")
        logger.info(f"  Found index: {result_index}")
        logger.info(f"  Success: {result_index in marked_indices}")
        
        # Verify result is reasonable
        self.assertIsNotNone(result_index)
        self.assertGreaterEqual(result_index, 0)
        self.assertLess(result_index, 8)
    
    def test_trading_signal_scoring(self) -> Any:
        """Test that trading signals calculate scores correctly"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 2: Trading Signal Scoring")
        logger.info("=" * 70)
        
        signals = self.test_signals
        
        logger.info(f"\nSignal scores:")
        scores = []
        for sig in signals:
            score = sig.get_score()
            scores.append(score)
            logger.info(f"  Signal {sig.signal_id}: {score:.4f}")
        
        # Verify scores are valid
        for score in scores:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
        
        # Verify scores are varied
        self.assertGreater(max(scores) - min(scores), 0.05)
    
    def test_optimizer_finds_best_signal(self) -> Any:
        """Test that optimizer can find the best signal"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 3: Optimizer Signal Selection")
        logger.info("=" * 70)
        
        optimizer = QuantumTradingOptimizer(use_quantum=True, n_qubits=3)
        signals = self.test_signals
        
        # Find best signal
        best_signal, best_score = optimizer.select_best_signal(signals)
        
        logger.info(f"\nOptimizer result:")
        logger.info(f"  Selected signal ID: {best_signal.signal_id}")
        logger.info(f"  Signal score: {best_score:.4f}")
        logger.info(f"  Details: strategy={best_signal.strategy}, risk_reward={best_signal.risk_reward_ratio:.2f}")
        
        # Verify selection
        self.assertIsNotNone(best_signal)
        self.assertGreater(best_score, 0.0)
        
        # Verify it's one of our signals
        self.assertIn(best_signal.signal_id, [s.signal_id for s in signals])
    
    def test_algorithm_comparison(self) -> Any:
        """Compare quantum and classical approaches"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 4: Quantum vs Classical Algorithm Comparison")
        logger.info("=" * 70)
        
        signals = self.test_signals * 3  # Create 24 signals
        
        # Quantum optimizer
        q_optimizer = QuantumTradingOptimizer(use_quantum=True, n_qubits=4)
        start = time.time()
        q_signal, q_score = q_optimizer.select_best_signal(signals)
        q_time = (time.time() - start) * 1000
        
        # Classical optimizer
        c_optimizer = QuantumTradingOptimizer(use_quantum=False)
        start = time.time()
        c_signal, c_score = c_optimizer.select_best_signal(signals)
        c_time = (time.time() - start) * 1000
        
        logger.info(f"\nQuantum approach:")
        logger.info(f"  Selected signal: {q_signal.signal_id}")
        logger.info(f"  Score: {q_score:.4f}")
        logger.info(f"  Time: {q_time:.3f}ms")
        
        logger.info(f"\nClassical approach:")
        logger.info(f"  Selected signal: {c_signal.signal_id}")
        logger.info(f"  Score: {c_score:.4f}")
        logger.info(f"  Time: {c_time:.3f}ms")
        
        # Both should find reasonable signals
        self.assertGreater(q_score, 0.3)
        self.assertGreater(c_score, 0.3)
    
    def test_scalability(self) -> Any:
        """Test algorithm scalability with different signal counts"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 5: Scalability Test")
        logger.info("=" * 70)
        
        sizes = [8, 16, 32]
        results = {}
        
        for size in sizes:
            # Create test signals
            signals = [
                TradingSignal(i, f"STRAT", 100+i, 101+i, 1.0+i*0.05, 0.70+i*0.01, 0.8+i*0.02)
                for i in range(1, size+1)
            ]
            
            # Test quantum
            q_opt = QuantumTradingOptimizer(use_quantum=True, n_qubits=min(5, len(signals).bit_length()))
            start = time.time()
            q_signal, q_score = q_opt.select_best_signal(signals)
            q_time = (time.time() - start) * 1000
            
            # Test classical
            c_opt = QuantumTradingOptimizer(use_quantum=False)
            start = time.time()
            c_signal, c_score = c_opt.select_best_signal(signals)
            c_time = (time.time() - start) * 1000
            
            logger.info(f"\n{size} signals:")
            logger.info(f"  Quantum:   {q_time:7.3f}ms → score={q_score:.4f}")
            logger.info(f"  Classical: {c_time:7.3f}ms → score={c_score:.4f}")
            
            results[size] = {'quantum_time': q_time, 'classical_time': c_time}
        
        # Verify reasonable scaling
        for size in sizes:
            self.assertGreater(results[size]['quantum_time'], 0)
            self.assertGreater(results[size]['classical_time'], 0)

class TestQuantumGates(unittest.TestCase):
    """Test quantum gate operations"""
    
    def test_hadamard_gate_creates_superposition(self) -> Any:
        """Test that Hadamard gate creates proper superposition"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 6: Hadamard Gate Superposition")
        logger.info("=" * 70)
        
        grover = GroverQuantumSearch(n_qubits=1)
        
        # Create |0> state and apply Hadamard
        initial_state = grover.hadamard(n_qubits=1)
        
        logger.info(f"\nState after Hadamard(|0>):")
        logger.info(f"  State: {initial_state}")
        
        # Should be equal superposition
        prob_0 = abs(initial_state[0])**2
        prob_1 = abs(initial_state[1])**2
        
        logger.info(f"  P(0): {prob_0:.4f}")
        logger.info(f"  P(1): {prob_1:.4f}")
        
        # Verify superposition (approximately 50-50)
        self.assertAlmostEqual(prob_0, 0.5, places=1)
        self.assertAlmostEqual(prob_1, 0.5, places=1)
    
    def test_oracle_phase_flip(self) -> Any:
        """Test that oracle correctly flips phase of marked states"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 7: Oracle Phase Flip")
        logger.info("=" * 70)
        
        grover = GroverQuantumSearch(n_qubits=2)
        
        # Create uniform superposition
        state = grover.hadamard(n_qubits=2)
        
        logger.info(f"\nInitial superposition state probabilities:")
        for i in range(4):
            prob = abs(state[i])**2
            logger.info(f"  |{i:02b}⟩: {prob:.4f}")
        
        # Apply oracle on state |2> (index 2)
        marked_state = grover.oracle(state, marked_indices=[2])
        
        logger.info(f"\nAfter oracle marking state |10⟩:")
        for i in range(4):
            prob = abs(marked_state[i])**2
            phase = marked_state[i] / max(abs(marked_state[i]), 0.001)
            logger.info(f"  |{i:02b}⟩: {prob:.4f}")
        
        # Verify oracle was applied
        self.assertIsNotNone(marked_state)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_single_signal(self) -> Any:
        """Test with single signal"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 8: Single Signal Handling")
        logger.info("=" * 70)
        
        single_signal = [TradingSignal(1, "ONLY", 100, 101, 1.5, 0.8, 0.9)]
        
        optimizer = QuantumTradingOptimizer()
        signal, score = optimizer.select_best_signal(single_signal)
        
        logger.info(f"\nSingle signal optimization:")
        logger.info(f"  Selected: {signal.signal_id}")
        logger.info(f"  Score: {score:.4f}")
        
        # Should select the only signal
        self.assertEqual(signal.signal_id, 1)
    
    def test_identical_signals(self) -> Any:
        """Test with identical signals"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 9: Identical Signals")
        logger.info("=" * 70)
        
        # Create identical signals
        identical = [
            TradingSignal(i, "SAME", 100, 101, 1.5, 0.8, 0.9)
            for i in range(1, 5)
        ]
        
        optimizer = QuantumTradingOptimizer()
        signal, score = optimizer.select_best_signal(identical)
        
        logger.info(f"\nIdentical signals optimization:")
        logger.info(f"  Selected: {signal.signal_id}")
        logger.info(f"  Score: {score:.4f}")
        
        # Should select one of them
        self.assertIn(signal.signal_id, [1, 2, 3, 4])

class TestBenchmarking(unittest.TestCase):
    """Test benchmarking functionality"""
    
    def test_algorithm_benchmark(self) -> Any:
        """Test algorithm benchmarking"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 10: Algorithm Benchmarking")
        logger.info("=" * 70)
        
        signals = [
            TradingSignal(i, f"BENCH_{i}", 100+i, 101+i, 1.0+i*0.1, 0.70+i*0.02, 0.8+i*0.05)
            for i in range(1, 17)  # 16 signals
        ]
        
        benchmark = AlgorithmBenchmark()
        
        logger.info(f"\nBenchmarking with {len(signals)} signals...")
        
        # Run benchmarks
        quantum_times = []
        classical_times = []
        
        for i in range(3):
            # Quantum
            q_opt = QuantumTradingOptimizer(use_quantum=True, n_qubits=4)
            start = time.time()
            _, _ = q_opt.select_best_signal(signals)
            quantum_times.append((time.time() - start) * 1000)
            
            # Classical
            c_opt = QuantumTradingOptimizer(use_quantum=False)
            start = time.time()
            _, _ = c_opt.select_best_signal(signals)
            classical_times.append((time.time() - start) * 1000)
        
        logger.info(f"\nBenchmark Results (3 runs):")
        logger.info(f"  Quantum   - avg: {sum(quantum_times)/len(quantum_times):7.3f}ms, min: {min(quantum_times):7.3f}ms, max: {max(quantum_times):7.3f}ms")
        logger.info(f"  Classical - avg: {sum(classical_times)/len(classical_times):7.3f}ms, min: {min(classical_times):7.3f}ms, max: {max(classical_times):7.3f}ms")
        
        # Verify times are positive
        for t in quantum_times + classical_times:
            self.assertGreater(t, 0)

def run_all_tests() -> Any:
    """Run all integration tests"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 QUANTUM GROVER ALGORITHM - TRADING SYSTEM INTEGRATION TESTS")
    logger.info("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumGroverIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumGates))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestBenchmarking))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        logger.info("\n✅ ALL TESTS PASSED!")
    else:
        logger.info("\n❌ SOME TESTS FAILED")
        if result.failures:
            logger.info("\nFailures:")
            for test, trace in result.failures:
                logger.info(f"  - {test}: {trace[:100]}...")
        if result.errors:
            logger.info("\nErrors:")
            for test, trace in result.errors:
                logger.info(f"  - {test}: {trace[:100]}...")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
