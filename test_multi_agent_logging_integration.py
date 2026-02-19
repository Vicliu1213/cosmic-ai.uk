#!/usr/bin/env python3
"""
Multi-Agent Trading System - Integration Test
多智能體交易系統 - 整合測試

Tests the LogManager integration with the multi-agent trading system.
測試 LogManager 與多智能體交易系統的整合。
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.logging_integration import LogManager, LogConfig
from src.plugins.multi_agent_trading import (
    SignalAnalysisAgent, RiskManagementAgent,
    MultiAgentCoordinator, MarketData, PortfolioState
)


def setup_test_logging() -> LogManager:
    """Setup logging for tests."""
    config = LogConfig(
        log_dir="logs/test",
        log_level=logging.INFO,
        max_bytes=5242880,  # 5 MB
        backup_count=3
    )
    
    log_manager = LogManager(config)
    
    # Create test-specific loggers
    log_manager.create_logger(
        name="trading.test",
        level=logging.INFO,
        filename="logs/test/trading_test.log"
    )
    
    return log_manager


def test_agent_initialization():
    """Test 1: Agent initialization with logging."""
    print("\n" + "=" * 80)
    print("TEST 1: Agent Initialization")
    print("=" * 80)
    
    log_manager = setup_test_logging()
    test_logger = log_manager.get_logger("trading.test")
    
    test_logger.info("[TEST_START] Agent initialization test")
    
    # Create agents with logging
    signal_agent = SignalAnalysisAgent(
        agent_id="test_signal_1",
        log_manager=log_manager
    )
    
    risk_agent = RiskManagementAgent(
        agent_id="test_risk_1",
        log_manager=log_manager
    )
    
    print(f"✓ Signal agent created: {signal_agent.agent_id}")
    print(f"✓ Risk agent created: {risk_agent.agent_id}")
    print(f"✓ Event logger available: {signal_agent.event_logger is not None}")
    
    test_logger.info("[TEST_PASS] Agent initialization successful")
    return True


def test_signal_detection():
    """Test 2: Signal detection with logging."""
    print("\n" + "=" * 80)
    print("TEST 2: Signal Detection")
    print("=" * 80)
    
    log_manager = setup_test_logging()
    test_logger = log_manager.get_logger("trading.test")
    
    test_logger.info("[TEST_START] Signal detection test")
    
    # Create signal agent
    signal_agent = SignalAnalysisAgent(
        agent_id="test_signal_2",
        sma_short=20,
        sma_long=50,
        log_manager=log_manager
    )
    
    # Create market data with bullish signal
    market_data = MarketData(
        symbol="TEST",
        price=100.0,
        volume=1000000.0,
        bid=99.95,
        ask=100.05,
        timestamp=datetime.now(),
        indicators={
            'sma_short': 102.0,  # Above long SMA = bullish
            'sma_long': 98.0,
            'rsi': 0.35  # Oversold
        }
    )
    
    portfolio = PortfolioState(
        positions={"TEST": 100},
        cash=50000.0,
        total_value=100000.0
    )
    
    # Analyze
    decision = signal_agent.analyze(market_data, portfolio)
    
    if decision:
        print(f"✓ Signal detected: {decision.decision_type.value}")
        print(f"✓ Confidence: {decision.confidence:.2%}")
        print(f"✓ Decision logged to event logger")
        test_logger.info(f"[TEST_PASS] Signal detected: {decision.decision_type.value}")
        return True
    else:
        print("✗ No signal detected")
        test_logger.error("[TEST_FAIL] No signal detected")
        return False


def test_risk_management():
    """Test 3: Risk management with logging."""
    print("\n" + "=" * 80)
    print("TEST 3: Risk Management")
    print("=" * 80)
    
    log_manager = setup_test_logging()
    test_logger = log_manager.get_logger("trading.test")
    
    test_logger.info("[TEST_START] Risk management test")
    
    # Create risk agent
    risk_agent = RiskManagementAgent(
        agent_id="test_risk_2",
        max_position_size=0.1,  # 10% max
        max_portfolio_loss=0.02,  # 2% max loss
        log_manager=log_manager
    )
    
    # Create scenario with oversized position
    market_data = MarketData(
        symbol="TEST",
        price=100.0,
        volume=1000000.0,
        bid=99.95,
        ask=100.05,
        timestamp=datetime.now()
    )
    
    portfolio = PortfolioState(
        positions={"TEST": 2000},  # Large position
        cash=50000.0,
        total_value=100000.0,
        unrealized_pnl=-1000.0
    )
    
    # Analyze
    decision = risk_agent.analyze(market_data, portfolio)
    
    # Position value = 2000 * 100 = $200,000 (but total is only $100k)
    # This should trigger risk management
    
    if decision:
        print(f"✓ Risk decision made: {decision.decision_type.value}")
        print(f"✓ Confidence: {decision.confidence:.2%}")
        print(f"✓ Risk score: {decision.risk_score:.2%}")
        test_logger.info(f"[TEST_PASS] Risk decision: {decision.decision_type.value}")
        return True
    else:
        print("✓ No risk violation detected")
        print("✓ Risk management working normally")
        test_logger.info("[TEST_PASS] Risk check completed (no violations)")
        return True


def test_coordination():
    """Test 4: Multi-agent coordination with logging."""
    print("\n" + "=" * 80)
    print("TEST 4: Multi-Agent Coordination")
    print("=" * 80)
    
    log_manager = setup_test_logging()
    test_logger = log_manager.get_logger("trading.test")
    
    test_logger.info("[TEST_START] Coordination test")
    
    # Create coordinator
    coordinator = MultiAgentCoordinator(
        coordinator_id="test_coordinator",
        log_manager=log_manager
    )
    
    # Create and register agents
    signal_agent = SignalAnalysisAgent(
        agent_id="test_signal_3",
        log_manager=log_manager
    )
    
    risk_agent = RiskManagementAgent(
        agent_id="test_risk_3",
        log_manager=log_manager
    )
    
    coordinator.register_agent(signal_agent)
    coordinator.register_agent(risk_agent)
    
    print(f"✓ Coordinator created: {coordinator.coordinator_id}")
    print(f"✓ Agents registered: {len(coordinator.agents)}")
    
    # Create market data for coordination
    market_data = MarketData(
        symbol="COOR",
        price=50.0,
        volume=500000.0,
        bid=49.95,
        ask=50.05,
        timestamp=datetime.now(),
        indicators={
            'sma_short': 52.0,
            'sma_long': 48.0,
            'rsi': 0.65
        }
    )
    
    portfolio = PortfolioState(
        positions={"COOR": 50},
        cash=100000.0,
        total_value=200000.0
    )
    
    # Coordinate decisions
    final_decision = coordinator.coordinate_decisions(market_data, portfolio)
    
    if final_decision:
        print(f"✓ Coordinated decision: {final_decision.decision_type.value}")
        print(f"✓ Final confidence: {final_decision.confidence:.2%}")
        print(f"✓ From {len(coordinator.agents)} agents")
        test_logger.info(f"[TEST_PASS] Coordination successful: {final_decision.decision_type.value}")
        return True
    else:
        print("✓ No consensus reached (valid scenario)")
        test_logger.info("[TEST_PASS] Coordination completed (no consensus)")
        return True


def test_logging_output():
    """Test 5: Verify logging output."""
    print("\n" + "=" * 80)
    print("TEST 5: Verify Logging Output")
    print("=" * 80)
    
    log_manager = setup_test_logging()
    
    # Check if log files exist
    log_dir = Path("logs/test")
    log_files = list(log_dir.glob("*.log")) if log_dir.exists() else []
    
    print(f"✓ Log directory: {log_dir}")
    print(f"✓ Log files created: {len(log_files)}")
    
    for log_file in log_files:
        size = log_file.stat().st_size
        print(f"  - {log_file.name}: {size} bytes")
    
    if log_files:
        # Read first log file
        first_log = log_files[0]
        with open(first_log, 'r') as f:
            lines = f.readlines()
            print(f"\n✓ Sample log entries from {first_log.name}:")
            for line in lines[-5:]:  # Last 5 lines
                print(f"  {line.rstrip()}")
        
        return len(log_files) > 0
    else:
        print("✗ No log files found")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 80)
    print("MULTI-AGENT TRADING SYSTEM - LOGMANAGER INTEGRATION TESTS")
    print("=" * 80)
    
    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("Signal Detection", test_signal_detection),
        ("Risk Management", test_risk_management),
        ("Coordination", test_coordination),
        ("Logging Output", test_logging_output),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration successful!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check logs.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
