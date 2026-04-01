"""
Quantum Field Theory System - Advanced quantum computing framework
Implements quantum field theory algorithms for trading and optimization

Key Components:
- QFTEngine: Main quantum field theory computation engine
- hybrid_algorithms: Classical-quantum hybrid implementations
- quantum_state_management: State initialization and manipulation
"""

import logging

logger = logging.getLogger(__name__)

# Lazy loading pattern for quantum components
_qft_engine = None
_hybrid_algorithms = None


def get_qft_engine():
    """Get or initialize the QFT engine lazily"""
    global _qft_engine
    if _qft_engine is None:
        try:
            from .qft_engine import QFTEngine
            _qft_engine = QFTEngine()
            logger.info("QFT Engine initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import QFTEngine: {e}")
    return _qft_engine


def get_hybrid_algorithms():
    """Get or initialize hybrid algorithms lazily"""
    global _hybrid_algorithms
    if _hybrid_algorithms is None:
        try:
            from .hybrid_algorithms import HybridAlgorithmSuite
            _hybrid_algorithms = HybridAlgorithmSuite()
            logger.info("Hybrid Algorithm Suite initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import HybridAlgorithmSuite: {e}")
    return _hybrid_algorithms


# Export public API
__all__ = [
    'get_qft_engine',
    'get_hybrid_algorithms',
    'QFTEngine',  # Will be imported on first access
    'HybridAlgorithmSuite',
]

# Metadata for registry
__version__ = "2.0.0"
__author__ = "Cosmic AI"
__description__ = "Quantum Field Theory System for Advanced Computing"
