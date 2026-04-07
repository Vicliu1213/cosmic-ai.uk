#!/usr/bin/env python3
"""
Unit Tests for Resonance Detection Engine

Tests all components: Detector, Analyzer, Amplifier, and main Engine
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from typing import List

from src.core.resonance_detection_engine import (
    ResonanceDetectionEngine,
    ResonanceDetector,
    ResonanceAnalyzer,
    ResonanceAmplifier,
    AgentTheorySignal,
    ResonanceType,
    ResonanceDirection
)


class TestResonanceDetector:
    """Test ResonanceDetector class."""
    
    def test_init(self):
        """Test detector initialization."""
        detector = ResonanceDetector(window_size=30, num_harmonics=7)
        assert detector.window_size == 30
        assert detector.num_harmonics == 7
    
    def test_correlation_matrix_single_signal(self):
        """Test correlation matrix with single signal."""
        detector = ResonanceDetector()
        
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.5,
                confidence=0.9,
                timestamp=datetime.now()
            )
        ]
        
        corr, agents = detector.compute_correlation_matrix(signals)
        assert corr.shape == (1, 1)
        assert corr[0, 0] == 1.0
        assert agents == ["agent_1"]
    
    def test_correlation_matrix_multiple_signals(self):
        """Test correlation matrix with multiple aligned signals."""
        detector = ResonanceDetector()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.8,
                confidence=0.9,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_2",
                theory_name="mean_reversion",
                signal_strength=0.75,
                confidence=0.85,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_3",
                theory_name="quantum",
                signal_strength=0.82,
                confidence=0.88,
                timestamp=now
            )
        ]
        
        corr, agents = detector.compute_correlation_matrix(signals)
        assert corr.shape == (3, 3)
        assert np.allclose(np.diag(corr), 1.0)  # Diagonal should be 1.0
        assert len(agents) == 3
    
    def test_detect_resonance_type_perfect(self):
        """Test perfect resonance detection."""
        detector = ResonanceDetector()
        
        # Nearly perfect correlation
        corr = np.array([
            [1.0, 0.98, 0.97],
            [0.98, 1.0, 0.96],
            [0.97, 0.96, 1.0]
        ])
        
        resonance_type = detector.detect_resonance_type(corr)
        assert resonance_type == ResonanceType.PERFECT
    
    def test_detect_resonance_type_strong(self):
        """Test strong resonance detection."""
        detector = ResonanceDetector()
        
        corr = np.array([
            [1.0, 0.80, 0.75],
            [0.80, 1.0, 0.78],
            [0.75, 0.78, 1.0]
        ])
        
        resonance_type = detector.detect_resonance_type(corr)
        assert resonance_type == ResonanceType.STRONG
    
    def test_detect_resonance_type_moderate(self):
        """Test moderate resonance detection."""
        detector = ResonanceDetector()
        
        corr = np.array([
            [1.0, 0.60, 0.55],
            [0.60, 1.0, 0.58],
            [0.55, 0.58, 1.0]
        ])
        
        resonance_type = detector.detect_resonance_type(corr)
        assert resonance_type == ResonanceType.MODERATE
    
    def test_detect_resonance_type_divergent(self):
        """Test divergent resonance detection."""
        detector = ResonanceDetector()
        
        corr = np.array([
            [1.0, 0.05, -0.1],
            [0.05, 1.0, 0.02],
            [-0.1, 0.02, 1.0]
        ])
        
        resonance_type = detector.detect_resonance_type(corr)
        assert resonance_type == ResonanceType.DIVERGENT
    
    def test_fft_signature(self):
        """Test FFT signature computation."""
        detector = ResonanceDetector(num_harmonics=5)
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id=f"agent_{i}",
                theory_name="momentum",
                signal_strength=0.5 + 0.1 * i,
                confidence=0.9,
                timestamp=now
            )
            for i in range(5)
        ]
        
        harmonic_sig = detector.compute_fft_signature(signals)
        assert len(harmonic_sig) == 5
        assert all(0.0 <= h <= 1.0 for h in harmonic_sig)
    
    def test_fft_signature_empty(self):
        """Test FFT signature with no signals."""
        detector = ResonanceDetector(num_harmonics=5)
        
        harmonic_sig = detector.compute_fft_signature([])
        assert len(harmonic_sig) == 5
        assert all(h == 0.0 for h in harmonic_sig)


class TestResonanceAnalyzer:
    """Test ResonanceAnalyzer class."""
    
    def test_init(self):
        """Test analyzer initialization."""
        analyzer = ResonanceAnalyzer(history_size=200)
        assert analyzer.detector is not None
        assert len(analyzer.resonance_history) == 0
    
    def test_analyze_resonance_bullish(self):
        """Test resonance analysis with bullish signals."""
        analyzer = ResonanceAnalyzer()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.85,
                confidence=0.92,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_2",
                theory_name="mean_reversion",
                signal_strength=0.80,
                confidence=0.88,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_3",
                theory_name="quantum",
                signal_strength=0.82,
                confidence=0.90,
                timestamp=now
            )
        ]
        
        resonance, alignment = analyzer.analyze_resonance(signals)
        
        assert resonance.resonance_direction == ResonanceDirection.BULLISH
        assert alignment > 0.5
        assert resonance.alignment_score >= 0.0
        assert resonance.alignment_score <= 1.0
        assert len(resonance.participating_agents) == 3
    
    def test_analyze_resonance_bearish(self):
        """Test resonance analysis with bearish signals."""
        analyzer = ResonanceAnalyzer()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=-0.85,
                confidence=0.92,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_2",
                theory_name="mean_reversion",
                signal_strength=-0.80,
                confidence=0.88,
                timestamp=now
            )
        ]
        
        resonance, _ = analyzer.analyze_resonance(signals)
        assert resonance.resonance_direction == ResonanceDirection.BEARISH
    
    def test_analyze_resonance_neutral(self):
        """Test resonance analysis with mixed signals."""
        analyzer = ResonanceAnalyzer()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.05,
                confidence=0.92,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_2",
                theory_name="mean_reversion",
                signal_strength=-0.08,
                confidence=0.88,
                timestamp=now
            )
        ]
        
        resonance, _ = analyzer.analyze_resonance(signals)
        assert resonance.resonance_direction == ResonanceDirection.NEUTRAL
    
    def test_resonance_history_tracking(self):
        """Test that resonance is tracked in history."""
        analyzer = ResonanceAnalyzer(history_size=10)
        
        now = datetime.now()
        for i in range(5):
            signals = [
                AgentTheorySignal(
                    agent_id=f"agent_{j}",
                    theory_name="momentum",
                    signal_strength=0.8 + 0.05 * j,
                    confidence=0.9,
                    timestamp=now + timedelta(seconds=i)
                )
                for j in range(3)
            ]
            
            analyzer.analyze_resonance(signals)
        
        assert len(analyzer.resonance_history) == 5
    
    def test_get_resonance_strength_metrics(self):
        """Test getting resonance strength metrics."""
        analyzer = ResonanceAnalyzer()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.85,
                confidence=0.92,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_2",
                theory_name="mean_reversion",
                signal_strength=0.80,
                confidence=0.88,
                timestamp=now
            )
        ]
        
        analyzer.analyze_resonance(signals)
        
        metrics = analyzer.get_resonance_strength_metrics()
        assert "avg_alignment" in metrics
        assert "max_alignment" in metrics
        assert "total_resonances" in metrics
        assert metrics["total_resonances"] == 1
    
    def test_update_theory_performance(self):
        """Test theory performance tracking."""
        analyzer = ResonanceAnalyzer()
        
        analyzer.update_theory_performance("momentum", True, 0.05)
        analyzer.update_theory_performance("momentum", True, 0.04)
        analyzer.update_theory_performance("momentum", False, -0.02)
        
        assert "momentum" in analyzer.theory_performance
        assert analyzer.theory_performance["momentum"] > 0.5


class TestResonanceAmplifier:
    """Test ResonanceAmplifier class."""
    
    def test_init(self):
        """Test amplifier initialization."""
        amplifier = ResonanceAmplifier(base_amplification=1.5)
        assert amplifier.base_amplification == 1.5
    
    def test_amplify_decision_bullish(self):
        """Test decision amplification with bullish resonance."""
        amplifier = ResonanceAmplifier()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.85,
                confidence=0.92,
                timestamp=now
            )
        ]
        
        analyzer = ResonanceAnalyzer()
        resonance, _ = analyzer.analyze_resonance(signals)
        
        original_decision = {
            "position_size": 1.0,
            "leverage": 1.5,
            "confidence": 0.8
        }
        
        amplified = amplifier.amplify_decision(original_decision, resonance)
        
        assert amplified["position_size"] >= original_decision["position_size"]
        assert "resonance_signal" in amplified
    
    def test_compute_confidence_boost(self):
        """Test confidence boost computation."""
        amplifier = ResonanceAmplifier()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.85,
                confidence=0.92,
                timestamp=now
            )
        ]
        
        analyzer = ResonanceAnalyzer()
        resonance, _ = analyzer.analyze_resonance(signals)
        
        boosted_conf = amplifier.compute_confidence_boost(0.7, resonance)
        assert boosted_conf > 0.7
        assert boosted_conf <= 0.99


class TestResonanceDetectionEngine:
    """Test main ResonanceDetectionEngine class."""
    
    def test_init(self):
        """Test engine initialization."""
        engine = ResonanceDetectionEngine()
        assert engine.detector is not None
        assert engine.analyzer is not None
        assert engine.amplifier is not None
        assert engine.resonance_trigger_count == 0
    
    def test_detect_and_amplify_resonance(self):
        """Test complete resonance detection and amplification."""
        engine = ResonanceDetectionEngine()
        
        now = datetime.now()
        signals = [
            AgentTheorySignal(
                agent_id="agent_1",
                theory_name="momentum",
                signal_strength=0.85,
                confidence=0.92,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_2",
                theory_name="mean_reversion",
                signal_strength=0.80,
                confidence=0.88,
                timestamp=now
            ),
            AgentTheorySignal(
                agent_id="agent_3",
                theory_name="quantum",
                signal_strength=0.82,
                confidence=0.90,
                timestamp=now
            )
        ]
        
        base_decision = {
            "action": "buy",
            "position_size": 1.0,
            "confidence": 0.8,
            "leverage": 1.5
        }
        
        resonance, amplified, conf_boost = engine.detect_and_amplify_resonance(
            signals,
            base_decision
        )
        
        assert resonance is not None
        assert amplified is not None
        assert conf_boost >= 0.0
        assert conf_boost <= 1.0
        assert resonance.resonance_type != ResonanceType.DIVERGENT
        assert engine.resonance_trigger_count == 1
    
    def test_get_engine_metrics(self):
        """Test engine metrics generation."""
        engine = ResonanceDetectionEngine()
        
        metrics = engine.get_engine_metrics()
        assert "resonance_detector" in metrics
        assert "resonance_analyzer" in metrics
        assert "amplifier" in metrics
        assert "engine_stats" in metrics
    
    def test_checkpoint_save_load(self, tmp_path):
        """Test engine checkpoint save and load."""
        engine = ResonanceDetectionEngine()
        
        # Simulate some activity
        engine.resonance_trigger_count = 5
        engine.analyzer.theory_performance["momentum"] = 0.75
        
        checkpoint_file = tmp_path / "engine_checkpoint.json"
        engine.save_checkpoint(str(checkpoint_file))
        
        # Create new engine and load checkpoint
        new_engine = ResonanceDetectionEngine()
        new_engine.load_checkpoint(str(checkpoint_file))
        
        assert new_engine.resonance_trigger_count == 5
        assert new_engine.analyzer.theory_performance["momentum"] == 0.75


class TestIntegration:
    """Integration tests for complete resonance workflow."""
    
    def test_multiple_resonance_cycles(self):
        """Test multiple cycles of resonance detection."""
        engine = ResonanceDetectionEngine()
        
        now = datetime.now()
        
        # Simulate 3 trading cycles
        for cycle in range(3):
            signals = [
                AgentTheorySignal(
                    agent_id=f"agent_{j}",
                    theory_name=["momentum", "mean_reversion", "quantum"][j],
                    signal_strength=0.7 + 0.05 * cycle + np.random.randn() * 0.05,
                    confidence=0.85 + 0.05 * cycle,
                    timestamp=now + timedelta(seconds=cycle * 60)
                )
                for j in range(3)
            ]
            
            decision = {
                "action": "buy",
                "position_size": 1.0,
                "confidence": 0.75,
                "leverage": 1.5
            }
            
            resonance, amplified, conf_boost = engine.detect_and_amplify_resonance(
                signals,
                decision
            )
            
            assert resonance is not None
            assert amplified is not None
        
        # Verify engine state
        metrics = engine.get_engine_metrics()
        assert metrics["engine_stats"]["total_analyses"] == 3
    
    def test_resonance_types_progression(self):
        """Test different resonance types in progression."""
        engine = ResonanceDetectionEngine()
        
        now = datetime.now()
        resonance_types_detected = []
        
        # Generate signals with varying alignment
        # Use divergent signals (opposite signs) for divergent resonance
        signal_pairs = [
            (0.95, 0.92),      # Perfect - both positive and close
            (0.80, 0.78),      # Strong - both positive and close
            (0.60, 0.55),      # Moderate - both positive, some distance
            (-0.80, 0.75),     # Weak - opposite signs (one positive, one negative)
            (-0.95, 0.92)      # Divergent - opposite signs, strong disagreement
        ]
        
        for sig1, sig2 in signal_pairs:
            # Create signals with specific alignment
            signals = [
                AgentTheorySignal(
                    agent_id="agent_1",
                    theory_name="momentum",
                    signal_strength=sig1,
                    confidence=0.9,
                    timestamp=now
                ),
                AgentTheorySignal(
                    agent_id="agent_2",
                    theory_name="mean_reversion",
                    signal_strength=sig2,
                    confidence=0.85,
                    timestamp=now
                )
            ]
            
            resonance, _, _ = engine.detect_and_amplify_resonance(
                signals,
                {"position_size": 1.0}
            )
            
            resonance_types_detected.append(resonance.resonance_type)
        
        # Verify we got good variety in resonance types
        # At least one should be perfect/strong (first) and one should be divergent (last)
        assert resonance_types_detected[0] in [ResonanceType.PERFECT, ResonanceType.STRONG]
        assert resonance_types_detected[-1] in [ResonanceType.WEAK, ResonanceType.DIVERGENT]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
