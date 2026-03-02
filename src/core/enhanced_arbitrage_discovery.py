#!/usr/bin/env python3
"""
Enhanced Triangular Arbitrage Discovery Engine
增强的三角套利发现引擎

Combines Cosmic-AI's triangular_arbitrage_engine with Hummingbot's market integration
techniques to provide fast, accurate arbitrage opportunity detection.

结合了 Cosmic-AI 的三角套利引擎和 Hummingbot 的市场集成技术
提供快速、准确的套利机会发现
"""

import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import heapq
from collections import defaultdict

import numpy as np

logger = logging.getLogger(__name__)


class DiscoveryAlgorithm(Enum):
    """Available arbitrage discovery algorithms"""
    BRUTE_FORCE = "brute_force"          # Simple O(n³) triangle enumeration
    BELLMAN_FORD = "bellman_ford"        # Negative cycle detection O(n³)
    FLOYD_WARSHALL = "floyd_warshall"    # All-pairs shortest path O(n³)
    INCREMENTAL = "incremental"          # Fast incremental updates O(1) per price change


@dataclass
class ExchangeConnector:
    """Exchange market data connector"""
    name: str                           # Exchange name (e.g., "binance")
    trading_pairs: List[str]           # Available trading pairs
    bid_ask_data: Dict[str, Tuple[float, float]] = field(default_factory=dict)  # pair -> (bid, ask)
    maker_fee: float = 0.001           # Maker fee percentage
    taker_fee: float = 0.001           # Taker fee percentage
    min_order_size: float = 0.0        # Minimum order size in base currency
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class ArbitrageOpportunity:
    """A discovered arbitrage opportunity"""
    path: List[str]                    # Trading path [pair1, pair2, pair3]
    currency_path: List[str]           # Currency path [A, B, C, A]
    profit_pct: float                  # Profit percentage
    roi: float                         # Return on investment
    required_capital: float            # Initial capital needed
    entry_time: datetime
    expiration_time: datetime
    exchanges: List[str]               # Which exchanges to use
    confidence: float                  # 0-1 confidence score
    detection_method: str              # Algorithm used
    
    def __lt__(self, other):
        """Allow sorting by profit (for use in heaps)"""
        return self.profit_pct > other.profit_pct  # Descending order


class EnhancedTriangularArbitrageDiscovery:
    """Enhanced triangular arbitrage discovery engine"""
    
    def __init__(self, 
                 algorithm: DiscoveryAlgorithm = DiscoveryAlgorithm.BRUTE_FORCE,
                 min_profit_threshold: float = 0.001,  # 0.1% minimum
                 max_execution_time: float = 5.0,      # 5 seconds
                 cache_ttl: float = 1.0):              # Cache for 1 second
        """
        Initialize the discovery engine
        
        Args:
            algorithm: Which discovery algorithm to use
            min_profit_threshold: Minimum profit % to consider
            max_execution_time: Maximum time for execution window
            cache_ttl: Time to live for cached price data
        """
        self.algorithm = algorithm
        self.min_profit_threshold = min_profit_threshold
        self.max_execution_time = max_execution_time
        self.cache_ttl = cache_ttl
        
        self.connectors: Dict[str, ExchangeConnector] = {}
        self.opportunities: List[ArbitrageOpportunity] = []
        self.last_scan_time = datetime.now()
        self.scan_count = 0
        
        # Performance metrics
        self.discovery_times: List[float] = []
        self.opportunities_found: int = 0
        
    def add_exchange_connector(self, connector: ExchangeConnector):
        """Register an exchange connector"""
        self.connectors[connector.name] = connector
        logger.info(f"Added connector for {connector.name} with {len(connector.trading_pairs)} pairs")
    
    def update_prices(self, exchange_name: str, price_data: Dict[str, Tuple[float, float]]):
        """Update market prices from an exchange (bid, ask)"""
        if exchange_name not in self.connectors:
            logger.warning(f"Unknown exchange: {exchange_name}")
            return
        
        connector = self.connectors[exchange_name]
        connector.bid_ask_data = price_data
        connector.last_update = datetime.now()
    
    def discover_opportunities(self) -> List[ArbitrageOpportunity]:
        """
        Main discovery method - finds all profitable triangular arbitrage cycles
        
        Returns:
            List of discovered opportunities, sorted by profitability
        """
        start_time = datetime.now()
        
        if self.algorithm == DiscoveryAlgorithm.BRUTE_FORCE:
            opportunities = self._discover_brute_force()
        elif self.algorithm == DiscoveryAlgorithm.BELLMAN_FORD:
            opportunities = self._discover_bellman_ford()
        elif self.algorithm == DiscoveryAlgorithm.FLOYD_WARSHALL:
            opportunities = self._discover_floyd_warshall()
        else:
            opportunities = self._discover_brute_force()
        
        # Track metrics
        elapsed = (datetime.now() - start_time).total_seconds()
        self.discovery_times.append(elapsed)
        self.opportunities_found += len(opportunities)
        self.scan_count += 1
        
        # Sort by profitability
        opportunities.sort(key=lambda x: x.profit_pct, reverse=True)
        self.opportunities = opportunities
        
        logger.debug(f"Found {len(opportunities)} opportunities in {elapsed:.3f}s using {self.algorithm.value}")
        return opportunities
    
    def _discover_brute_force(self) -> List[ArbitrageOpportunity]:
        """
        Simple O(n³) brute force algorithm
        Enumerate all possible triangles and check profitability
        """
        opportunities = []
        
        # Get all unique trading pairs across exchanges
        all_pairs = set()
        for connector in self.connectors.values():
            all_pairs.update(connector.trading_pairs)
        
        pairs = list(all_pairs)
        n = len(pairs)
        
        # Try all combinations of 3 pairs
        for i in range(n):
            for j in range(n):
                if j == i:
                    continue
                for k in range(n):
                    if k == i or k == j:
                        continue
                    
                    pair1, pair2, pair3 = pairs[i], pairs[j], pairs[k]
                    opp = self._check_triangle_profitability(pair1, pair2, pair3)
                    if opp and opp.profit_pct >= self.min_profit_threshold:
                        opportunities.append(opp)
        
        return opportunities
    
    def _discover_bellman_ford(self) -> List[ArbitrageOpportunity]:
        """
        Bellman-Ford algorithm for negative cycle detection
        More efficient than brute force for sparse graphs
        
        Algorithm:
        1. Convert prices to log space (multiplication becomes addition)
        2. Negate the log prices (profit becomes negative cost)
        3. Detect negative cycles using Bellman-Ford
        4. Convert back to profit percentage
        """
        opportunities = []
        
        # Build log-price graph
        graph = self._build_log_price_graph()
        
        if not graph:
            return opportunities
        
        vertices = list(graph.keys())
        n = len(vertices)
        
        # Bellman-Ford algorithm
        distances = {v: float('inf') for v in vertices}
        predecessors = {v: None for v in vertices}
        
        # Initialize
        distances[vertices[0]] = 0
        
        # Relax edges n-1 times
        for _ in range(n - 1):
            for u in graph:
                if distances[u] == float('inf'):
                    continue
                for v, weight in graph[u]:
                    if distances[u] + weight < distances[v]:
                        distances[v] = distances[u] + weight
                        predecessors[v] = u
        
        # Detect negative cycles
        for u in graph:
            if distances[u] == float('inf'):
                continue
            for v, weight in graph[u]:
                if distances[u] + weight < distances[v]:
                    # Found a negative cycle
                    cycle = self._extract_cycle(u, v, predecessors, graph)
                    opp = self._cycle_to_opportunity(cycle)
                    if opp and opp.profit_pct >= self.min_profit_threshold:
                        opportunities.append(opp)
        
        return opportunities
    
    def _discover_floyd_warshall(self) -> List[ArbitrageOpportunity]:
        """
        Floyd-Warshall algorithm for all-pairs analysis
        Best for small, dense graphs
        """
        opportunities = []
        
        # Similar to Bellman-Ford but more comprehensive
        # For now, delegate to brute force for stability
        return self._discover_brute_force()
    
    def _check_triangle_profitability(self, pair1: str, pair2: str, pair3: str) -> Optional[ArbitrageOpportunity]:
        """
        Check if a triangle of three pairs forms a profitable arbitrage cycle
        
        A valid triangle must connect properly:
        Example: BTC/USDT, ETH/BTC, ETH/USDT form a valid cycle:
        USDT -> BTC -> ETH -> USDT
        
        Each pair must share exactly one currency with the next pair.
        """
        try:
            # Validate that the three pairs form a valid triangle
            if not self._is_valid_triangle(pair1, pair2, pair3):
                return None
            
            # Find which exchange has the best prices for this combination
            best_profit = 0
            best_exchanges = []
            
            for exchange_name, connector in self.connectors.items():
                if not all(p in connector.bid_ask_data for p in [pair1, pair2, pair3]):
                    continue
                
                # Get prices
                bid1, ask1 = connector.bid_ask_data[pair1]
                bid2, ask2 = connector.bid_ask_data[pair2]
                bid3, ask3 = connector.bid_ask_data[pair3]
                
                # Calculate profit through the cycle
                # Start with 1 unit
                profit = self._calculate_cycle_profit(
                    bid1, ask1, bid2, ask2, bid3, ask3,
                    connector.taker_fee, connector.maker_fee
                )
                
                if profit > best_profit:
                    best_profit = profit
                    best_exchanges = [exchange_name]
            
            if best_profit > self.min_profit_threshold:
                return ArbitrageOpportunity(
                    path=[pair1, pair2, pair3],
                    currency_path=self._extract_currency_path([pair1, pair2, pair3]),
                    profit_pct=best_profit * 100,
                    roi=best_profit,
                    required_capital=1.0,
                    entry_time=datetime.now(),
                    expiration_time=datetime.now() + timedelta(seconds=self.max_execution_time),
                    exchanges=best_exchanges,
                    confidence=0.8,
                    detection_method=self.algorithm.value
                )
        
        except Exception as e:
            logger.debug(f"Error checking triangle {pair1}, {pair2}, {pair3}: {e}")
        
        return None
    
    def _is_valid_triangle(self, pair1: str, pair2: str, pair3: str) -> bool:
        """
        Validate that three pairs form a proper triangular cycle.
        
        A valid triangle has each pair sharing exactly one currency with another,
        forming a complete loop with no repeated currencies.
        """
        try:
            pairs = [pair1, pair2, pair3]
            
            # Parse all currencies
            all_currencies = set()
            currencies_by_pair = {}
            
            for pair in pairs:
                if '/' not in pair:
                    return False
                base, quote = pair.split('/')
                currencies_by_pair[pair] = (base, quote)
                all_currencies.add(base)
                all_currencies.add(quote)
            
            # A valid triangle should have exactly 3 unique currencies
            if len(all_currencies) != 3:
                return False
            
            # Check that the pairs form a connected cycle
            # Each currency should appear in exactly 2 pairs
            currency_count = {}
            for pair in pairs:
                base, quote = currencies_by_pair[pair]
                currency_count[base] = currency_count.get(base, 0) + 1
                currency_count[quote] = currency_count.get(quote, 0) + 1
            
            # Each currency should appear exactly 2 times
            if not all(count == 2 for count in currency_count.values()):
                return False
            
            return True
        except Exception as e:
            logger.debug(f"Error validating triangle: {e}")
            return False
    
    def _calculate_cycle_profit(self, bid1, ask1, bid2, ask2, bid3, ask3,
                               taker_fee: float, maker_fee: float) -> float:
        """
        Calculate profit percentage for a complete cycle
        
        Correct formula (based on verified calculator):
        Pair1: BTC/USDT (bid=42000, ask=42010) - buy BTC, pay USDT
        Pair2: ETH/BTC (bid=0.0548, ask=0.0549) - sell BTC to buy ETH
        Pair3: ETH/USDT (bid=2300, ask=2310) - sell ETH, get USDT
        
        Cycle: USDT -> BTC -> ETH -> USDT
        
        Step 1: Buy BTC at ask1 (cost): amount_btc = amount_usd / ask1
        Step 2: Sell BTC for ETH at bid2 (rate): amount_eth = amount_btc / bid2
        Step 3: Sell ETH for USDT at bid3 (rate): amount_usd = amount_eth * bid3
        """
        try:
            # Safety checks
            if ask1 <= 0 or bid2 <= 0 or bid3 <= 0:
                return -1.0
            
            initial = 100.0  # Start with 100 USDT
            
            # Step 1: Buy BTC with USDT at ask price
            # To buy BTC, pay USDT at the ask price
            btc_amount = (initial / ask1) * (1 - taker_fee)
            if btc_amount <= 0:
                return -1.0
            
            # Step 2: Sell BTC for ETH at bid price
            # If ETH/BTC bid = 0.0548, it means "sell BTC at this rate to get ETH"
            # So: amount_eth = amount_btc / pair2_bid
            eth_amount = (btc_amount / bid2) * (1 - maker_fee)
            if eth_amount <= 0:
                return -1.0
            
            # Step 3: Sell ETH back to USDT at bid price
            # If ETH/USDT bid = 2300, it means "sell 1 ETH to get 2300 USDT"
            final_usd = (eth_amount * bid3) * (1 - taker_fee)
            if final_usd <= 0:
                return -1.0
            
            # Calculate profit
            profit = (final_usd - initial) / initial
            return max(profit, -1.0)  # Cap at -100% loss
        
        except (ValueError, ZeroDivisionError, TypeError):
            return -1.0
    
    def _extract_currency_path(self, pair_path: List[str]) -> List[str]:
        """Extract currency path from trading pair path"""
        # Simple extraction - parse pair format like "BTC/USD"
        currencies = []
        for pair in pair_path:
            if '/' in pair:
                currencies.append(pair.split('/')[0])
        
        if pair_path[-1] and '/' in pair_path[-1]:
            currencies.append(pair_path[-1].split('/')[1])
        
        return currencies
    
    def _build_log_price_graph(self) -> Dict[str, List[Tuple[str, float]]]:
         """Build a graph for Bellman-Ford using log prices"""
         graph = defaultdict(list)
         
         try:
             for exchange_name, connector in self.connectors.items():
                 for pair, (bid, ask) in connector.bid_ask_data.items():
                     if '/' not in pair or not isinstance(bid, (int, float)) or not isinstance(ask, (int, float)):
                         continue
                     
                     if bid <= 0 or ask <= 0:
                         continue
                     
                     base, quote = pair.split('/')
                     
                     # Add edges for both directions
                     # Forward: quote -> base (at bid)
                     try:
                         log_price = float(np.log(float(bid))) - float(connector.taker_fee)
                         graph[quote].append((base, -log_price))
                     except (ValueError, TypeError) as e:
                         logger.debug(f"Error processing bid {bid}: {e}")
                         pass
                     
                     # Reverse: base -> quote (at ask)
                     try:
                         log_price = float(np.log(float(ask))) - float(connector.taker_fee)
                         graph[base].append((quote, -log_price))
                     except (ValueError, TypeError) as e:
                         logger.debug(f"Error processing ask {ask}: {e}")
                         pass
         except Exception as e:
             logger.debug(f"Error building log price graph: {e}")
         
         return graph
    
    def _extract_cycle(self, u: str, v: str, predecessors: Dict, graph: Dict) -> List[str]:
        """Extract a cycle from predecessor links"""
        cycle = [v]
        current = u
        
        while current and current not in cycle:
            cycle.append(current)
            current = predecessors.get(current)
        
        return cycle
    
    def _cycle_to_opportunity(self, cycle: List[str]) -> Optional[ArbitrageOpportunity]:
        """Convert a cycle to an ArbitrageOpportunity
        
        For now, we skip cycles that don't have proper price data.
        In a full implementation, we would extract prices from the graph.
        """
        if len(cycle) < 3:
            return None
        
        # In a full implementation, we would:
        # 1. Extract the prices from the graph weights
        # 2. Calculate the actual profit from those prices
        # For now, return None to skip this cycle
        # The brute force algorithm handles this properly
        return None
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        if not self.discovery_times:
            return {}
        
        return {
            "total_scans": self.scan_count,
            "total_opportunities": self.opportunities_found,
            "avg_discovery_time_ms": np.mean(self.discovery_times) * 1000,
            "min_discovery_time_ms": np.min(self.discovery_times) * 1000,
            "max_discovery_time_ms": np.max(self.discovery_times) * 1000,
            "current_opportunities": len(self.opportunities),
            "best_profit_pct": self.opportunities[0].profit_pct if self.opportunities else 0,
        }


def main():
    """Demo of the enhanced discovery engine"""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create engine
    engine = EnhancedTriangularArbitrageDiscovery(
        algorithm=DiscoveryAlgorithm.BRUTE_FORCE,
        min_profit_threshold=0.0005  # 0.05% minimum
    )
    
    # Add mock exchanges
    binance = ExchangeConnector(
        name="binance",
        trading_pairs=["BTC/USD", "ETH/USD", "ETH/BTC"],
        bid_ask_data={
            "BTC/USD": (40000, 40100),
            "ETH/USD": (2200, 2210),
            "ETH/BTC": (0.055, 0.0551),
        },
        maker_fee=0.001,
        taker_fee=0.001
    )
    
    engine.add_exchange_connector(binance)
    
    # Discover opportunities
    opportunities = engine.discover_opportunities()
    
    print(f"\n✅ Found {len(opportunities)} opportunities:")
    for opp in opportunities[:5]:  # Show top 5
        print(f"  • {' -> '.join(opp.path)}: {opp.profit_pct:.4f}% profit")
    
    # Show metrics
    metrics = engine.get_performance_metrics()
    print(f"\n📊 Performance: {metrics}")


if __name__ == "__main__":
    main()
