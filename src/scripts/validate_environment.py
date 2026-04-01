#!/usr/bin/env python3
"""
Environment Validation Script for Cosmic AI Trading System
宇宙交易系統環境驗證腳本

This script validates that all Phase 1-4 systems are properly installed
and can be imported without errors.

Usage:
    python scripts/validate_environment.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_header(text: str) -> None:
    """Print formatted header"""
    width = 70
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width)


def print_section(text: str) -> None:
    """Print section header"""
    print(f"\n✓ {text}...")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"  ✅ {text}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"  ❌ {text}")


def validate_phase1() -> int:
    """Validate Phase 1 Foundation Layer"""
    print_section("Testing Phase 1 (Foundation Layer) imports")
    try:
        from src.core.quantum_verification_layer import QuantumVerificationLayer
        from src.core.market_regime_detector import MarketRegimeDetector
        from src.core.theory_optimizer import DynamicTheoryOptimizer
        from src.core.phase1_integration import Phase1IntegrationEngine
        print_success("Phase 1 modules loaded successfully")
        return 4
    except ImportError as e:
        print_error(f"Phase 1 import failed: {e}")
        return 0


def validate_phase2() -> int:
    """Validate Phase 2 Resonance Breakthrough Layer"""
    print_section("Testing Phase 2 (Resonance Breakthrough Layer) imports")
    try:
        from src.core.resonance_detection_engine import ResonanceDetectionEngine
        from src.core.multi_agent_resonance_module import MultiAgentResonanceModule
        from src.core.cma_es_adaptive_evolution import AdaptiveEvolutionCoordinator
        print_success("Phase 2 modules loaded successfully")
        return 3
    except ImportError as e:
        print_error(f"Phase 2 import failed: {e}")
        return 0


def validate_phase3() -> int:
    """Validate Phase 3 Singularity Optimization Layer"""
    print_section("Testing Phase 3 (Singularity Optimization Layer) imports")
    try:
        from src.core.sharpe_target_engine import SharpeTargetEngine
        from src.core.dynamic_risk_management import DynamicRiskManagementEngine
        from src.core.singularity_detection_system import SingularityDetectionSystem
        print_success("Phase 3 modules loaded successfully")
        return 3
    except ImportError as e:
        print_error(f"Phase 3 import failed: {e}")
        return 0


def validate_phase4() -> int:
    """Validate Phase 4 Arbitrage Integration Layer"""
    print_section("Testing Phase 4 (Arbitrage Integration Layer) imports")
    try:
        from src.core.triangular_arbitrage_engine import TriangularArbitrageEngine
        from src.core.wormhole_arbitrage_module import WormholeArbitrageModule
        from src.core.hummingbot_integration_layer import HummingbotIntegrationLayer
        print_success("Phase 4 modules loaded successfully")
        return 3
    except ImportError as e:
        print_error(f"Phase 4 import failed: {e}")
        return 0


def validate_dependencies() -> bool:
    """Validate core dependencies"""
    print_section("Testing core dependencies")
    try:
        import numpy as np
        import pandas as pd
        import scipy
        import yaml
        import qiskit
        from semantic_kernel import Kernel
        import openai
        print_success("All core dependencies loaded successfully")
        return True
    except ImportError as e:
        print_error(f"Dependency import failed: {e}")
        return False


def validate_python_version() -> bool:
    """Validate Python version"""
    version = sys.version_info
    min_version = (3, 10)
    
    if version >= min_version:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} (required: 3.10+)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (required: 3.10+)")
        return False


def print_summary(phase1: int, phase2: int, phase3: int, phase4: int, deps: bool, py_version: bool) -> int:
    """Print validation summary"""
    total_modules = phase1 + phase2 + phase3 + phase4
    
    print_header("ENVIRONMENT VALIDATION SUMMARY")
    
    print(f"\n✅ Python Version: {'OK' if py_version else 'FAILED'}")
    print(f"✅ Phase 1 Modules: {phase1}/4 - Foundation Layer")
    print(f"✅ Phase 2 Modules: {phase2}/3 - Resonance Breakthrough Layer")
    print(f"✅ Phase 3 Modules: {phase3}/3 - Singularity Optimization Layer")
    print(f"✅ Phase 4 Modules: {phase4}/3 - Arbitrage Integration Layer")
    print(f"✅ Core Dependencies: {'OK' if deps else 'FAILED'}")
    
    if total_modules == 13 and deps and py_version:
        print(f"\n🎉 ALL SYSTEMS READY! ({total_modules}/13 modules + dependencies)")
        return 0
    else:
        print(f"\n⚠️  System Status: {total_modules}/13 modules loaded")
        if not py_version:
            print("   - Python version requirement not met")
        if not deps:
            print("   - Some dependencies missing")
        return 1


def main() -> int:
    """Main validation routine"""
    print_header("COSMIC AI TRADING SYSTEM - ENVIRONMENT VALIDATION")
    
    # Validate Python version
    py_version = validate_python_version()
    
    # Validate each phase
    phase1 = validate_phase1()
    phase2 = validate_phase2()
    phase3 = validate_phase3()
    phase4 = validate_phase4()
    
    # Validate dependencies
    deps = validate_dependencies()
    
    # Print summary and return status
    return print_summary(phase1, phase2, phase3, phase4, deps, py_version)


if __name__ == "__main__":
    sys.exit(main())
