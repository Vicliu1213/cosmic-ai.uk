#!/usr/bin/env python3
"""
Hierarchical Dashboard with Arbitrage Data Test
分層儀表板與套利數據測試

Tests the hierarchical dashboard integration with arbitrage discovery.
"""

import sys
import logging
from datetime import datetime, timedelta

sys.path.insert(0, '/workspaces/cosmic-ai.uk')

from src.core.enhanced_arbitrage_discovery import (
    EnhancedTriangularArbitrageDiscovery,
    ExchangeConnector,
    DiscoveryAlgorithm
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)


def test_dashboard_with_arbitrage():
    """Test hierarchical dashboard with arbitrage data"""
    
    print("=" * 80)
    print("HIERARCHICAL DASHBOARD WITH ARBITRAGE DATA TEST")
    print("=" * 80)
    
    # Setup test exchanges
    print("\n[Step 1] Setting up test exchanges")
    print("-" * 80)
    
    engine = EnhancedTriangularArbitrageDiscovery(
        algorithm=DiscoveryAlgorithm.BRUTE_FORCE,
        min_profit_threshold=0.0001
    )
    
    # Binance
    binance = ExchangeConnector(
        name="binance",
        trading_pairs=["BTC/USDT", "ETH/BTC", "ETH/USDT", "BNB/USDT"],
        maker_fee=0.001,
        taker_fee=0.001
    )
    binance.bid_ask_data = {
        "BTC/USDT": (42000.0, 42010.0),
        "ETH/BTC": (0.0548, 0.0549),
        "ETH/USDT": (2300.0, 2310.0),
        "BNB/USDT": (310.0, 315.0)
    }
    engine.add_exchange_connector(binance)
    
    # Kraken
    kraken = ExchangeConnector(
        name="kraken",
        trading_pairs=["BTC/USDT", "ETH/BTC", "ETH/USDT"],
        maker_fee=0.0026,
        taker_fee=0.0026
    )
    kraken.bid_ask_data = {
        "BTC/USDT": (41950.0, 42050.0),
        "ETH/BTC": (0.0547, 0.0551),
        "ETH/USDT": (2310.0, 2320.0)
    }
    engine.add_exchange_connector(kraken)
    
    # Coinbase (with cross-exchange spreads)
    coinbase = ExchangeConnector(
        name="coinbase",
        trading_pairs=["BTC/USDT", "ETH/BTC", "ETH/USDT"],
        maker_fee=0.004,
        taker_fee=0.006
    )
    coinbase.bid_ask_data = {
        "BTC/USDT": (42500.0, 42510.0),
        "ETH/BTC": (0.0545, 0.0546),
        "ETH/USDT": (2350.0, 2360.0)
    }
    engine.add_exchange_connector(coinbase)
    
    print("✅ Setup 3 exchanges (Binance, Kraken, Coinbase)")
    print(f"   Total pairs: {sum(len(c.trading_pairs) for c in engine.connectors.values())}")
    
    # Discover opportunities
    print("\n[Step 2] Discovering arbitrage opportunities")
    print("-" * 80)
    
    opportunities = engine.discover_opportunities()
    
    print(f"✅ Found {len(opportunities)} opportunities")
    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n   Opportunity {i}:")
        print(f"   Path: {' -> '.join(opp.currency_path)}")
        print(f"   Profit: {opp.profit_pct:.4f}%")
        print(f"   Exchanges: {', '.join(opp.exchanges)}")
        print(f"   Confidence: {opp.confidence:.1%}")
    
    if len(opportunities) > 5:
        print(f"\n   ... and {len(opportunities) - 5} more opportunities")
    
    # Prepare dashboard data
    print("\n[Step 3] Preparing dashboard data")
    print("-" * 80)
    
    dashboard_data = {
        "title": "Cosmic AI - Arbitrage Detection Dashboard",
        "timestamp": datetime.now().isoformat(),
        "system_stats": {
            "exchanges": len(engine.connectors),
            "total_pairs": sum(len(c.trading_pairs) for c in engine.connectors.values()),
            "scan_count": engine.scan_count,
            "opportunities_found": len(opportunities)
        },
        "performance": {
            "avg_discovery_time_ms": sum(engine.discovery_times) / len(engine.discovery_times) * 1000 if engine.discovery_times else 0,
            "algorithm": engine.algorithm.value,
            "profit_threshold": engine.min_profit_threshold * 100
        },
        "top_opportunities": [
            {
                "path": " → ".join(opp.currency_path),
                "profit_pct": opp.profit_pct,
                "roi": opp.roi * 100,
                "exchanges": ", ".join(opp.exchanges),
                "confidence": opp.confidence,
                "expiration": opp.expiration_time.isoformat()
            }
            for opp in opportunities[:10]
        ]
    }
    
    print("✅ Dashboard data prepared")
    print(f"   Top 10 opportunities formatted")
    
    # Verify data integrity
    print("\n[Step 4] Verifying data integrity")
    print("-" * 80)
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: All opportunities have positive or negative profit
    checks_total += 1
    if all(isinstance(opp['profit_pct'], (int, float)) for opp in dashboard_data['top_opportunities']):
        print("✅ All opportunities have numeric profit values")
        checks_passed += 1
    else:
        print("❌ Some opportunities have invalid profit values")
    
    # Check 2: All exchanges are registered
    checks_total += 1
    if dashboard_data['system_stats']['exchanges'] == 3:
        print("✅ All 3 exchanges registered")
        checks_passed += 1
    else:
        print(f"❌ Expected 3 exchanges, got {dashboard_data['system_stats']['exchanges']}")
    
    # Check 3: Opportunities are sorted
    checks_total += 1
    profits = [opp['profit_pct'] for opp in dashboard_data['top_opportunities']]
    if profits == sorted(profits, reverse=True):
        print("✅ Opportunities sorted by profitability (descending)")
        checks_passed += 1
    else:
        print("❌ Opportunities not properly sorted")
    
    # Check 4: Performance metrics valid
    checks_total += 1
    if dashboard_data['performance']['avg_discovery_time_ms'] >= 0:
        print(f"✅ Performance metrics valid (avg: {dashboard_data['performance']['avg_discovery_time_ms']:.2f}ms)")
        checks_passed += 1
    else:
        print("❌ Performance metrics invalid")
    
    # Summary
    print("\n" + "=" * 80)
    print(f"VERIFICATION SUMMARY: {checks_passed}/{checks_total} checks passed")
    print("=" * 80)
    
    # Display final dashboard data
    print("\n[Final] Dashboard Data Summary")
    print("-" * 80)
    print(f"Title: {dashboard_data['title']}")
    print(f"Timestamp: {dashboard_data['timestamp']}")
    print(f"Exchanges: {dashboard_data['system_stats']['exchanges']}")
    print(f"Trading Pairs: {dashboard_data['system_stats']['total_pairs']}")
    print(f"Opportunities Found: {dashboard_data['system_stats']['opportunities_found']}")
    print(f"Average Discovery Time: {dashboard_data['performance']['avg_discovery_time_ms']:.2f}ms")
    print(f"Algorithm: {dashboard_data['performance']['algorithm'].upper()}")
    
    return checks_passed == checks_total


if __name__ == "__main__":
    success = test_dashboard_with_arbitrage()
    sys.exit(0 if success else 1)
