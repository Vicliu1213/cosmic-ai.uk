#!/usr/bin/env python3
"""
Hummingbot Integration Layer Test
Hummingbot 集成層測試

Tests the integration layer for connecting to Hummingbot exchange connectors.
"""

import sys
import logging
from datetime import datetime

sys.path.insert(0, '/workspaces/cosmic-ai.uk')

from src.core.hummingbot_integration_layer import (
    HummingbotIntegrationLayer,
    HummingbotConnector,
    ExchangeConfig,
    HummingbotStatus,
    OrderStatus
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


def test_hummingbot_integration():
    """Test basic Hummingbot integration layer functionality"""
    
    print("=" * 80)
    print("HUMMINGBOT INTEGRATION LAYER TEST")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    # Test 1: Initialize integration layer
    print("\n[Test 1] Initialize Hummingbot Integration Layer")
    print("-" * 80)
    try:
        hb = HummingbotIntegrationLayer()
        print("✅ Initialization successful")
        passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        failed += 1
        return False
    
    # Test 2: Get system status
    print("\n[Test 2] Get System Status")
    print("-" * 80)
    try:
        status = hb.get_system_status()
        print("✅ System status retrieved")
        print(f"   Hummingbot Status: {status.get('hummingbot_status', 'N/A')}")
        print(f"   Active Orders: {status.get('active_orders', 0)}")
        print(f"   Active Trades: {status.get('active_trades', 0)}")
        print(f"   Total Trades Executed: {status.get('total_trades_executed', 0)}")
        print(f"   Total Profit: ${status.get('total_profit_usd', 0):.2f}")
        passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        failed += 1
    
    # Test 3: Get performance statistics
    print("\n[Test 3] Get Performance Statistics")
    print("-" * 80)
    try:
        stats = hb.get_performance_stats()
        print("✅ Performance stats retrieved")
        if 'total_trades' in stats:
            print(f"   Total Trades: {stats['total_trades']}")
        if 'average_profit_per_trade' in stats:
            print(f"   Avg Profit per Trade: {stats['average_profit_per_trade']}")
        if 'win_rate' in stats:
            print(f"   Win Rate: {stats['win_rate']}")
        passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        failed += 1
    
    # Test 4: Test Order Executor initialization
    print("\n[Test 4] Order Executor Status")
    print("-" * 80)
    try:
        active_orders = hb.order_executor.get_active_orders()
        print("✅ Order executor is working")
        print(f"   Active Orders: {len(active_orders)}")
        passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        failed += 1
    
    # Test 5: Test Trade Tracker initialization
    print("\n[Test 5] Trade Tracker Status")
    print("-" * 80)
    try:
        active_trades = hb.trade_tracker.get_active_trades()
        print("✅ Trade tracker is working")
        print(f"   Active Trades: {len(active_trades)}")
        passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        failed += 1
    
    # Test 6: Test Connector status
    print("\n[Test 6] Hummingbot Connector Status")
    print("-" * 80)
    try:
        connector_status = hb.connector.get_status()
        print("✅ Connector is initialized")
        print(f"   Connector Status: {connector_status}")
        print(f"   Is Ready: {hb.connector.is_ready()}")
        passed += 1
    except Exception as e:
        print(f"❌ Failed: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print(f"TEST SUMMARY: {passed} Passed, {failed} Failed")
    print("=" * 80)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED")
        return True
    else:
        print(f"❌ {failed} TESTS FAILED")
        return False


if __name__ == "__main__":
    success = test_hummingbot_integration()
    sys.exit(0 if success else 1)
