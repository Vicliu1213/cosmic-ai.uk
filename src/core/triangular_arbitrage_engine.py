#!/usr/bin/env python3
"""
Triangular Arbitrage Engine
三角套利引擎

This module implements triangular arbitrage detection and execution on a single exchange.
Detects profitable trading cycles across three currency pairs and calculates optimal execution.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class ArbitrageOpportunityType(Enum):
    """Enumeration of arbitrage opportunity types."""
    EMERGING = "emerging"           # First detection of cycle
    CONFIRMED = "confirmed"         # Multiple confirmations
    OPTIMAL = "optimal"             # Peak profitability window
    DECLINING = "declining"         # Diminishing returns
    EXHAUSTED = "exhausted"         # No longer profitable


class ExecutionPhase(Enum):
    """Enumeration of arbitrage execution phases."""
    INITIAL = "initial"             # First leg of cycle
    INTERMEDIATE = "intermediate"   # Second leg
    FINAL = "final"                 # Third leg completing cycle
    SETTLEMENT = "settlement"       # Waiting for settlement
    COMPLETE = "complete"           # Cycle finished


@dataclass
class PriceSnapshot:
    """Market price snapshot at a point in time."""
    timestamp: datetime
    bid: float
    ask: float
    mid: float
    volume: float
    
    def spread(self) -> float:
        """Calculate bid-ask spread."""
        return (self.ask - self.bid) / self.mid if self.mid > 0 else 0.0


@dataclass
class TriangularCycle:
    """Representation of a triangular arbitrage cycle."""
    pair1: str                      # First currency pair (e.g., BTC/USD)
    pair2: str                      # Second currency pair
    pair3: str                      # Third currency pair
    cycle_path: List[str]           # Path of currencies in cycle
    profit_pct: float               # Profit percentage (%)
    entry_time: datetime            # Time cycle was identified
    expiration_time: datetime       # Expected expiration of opportunity
    confidence: float               # Confidence level (0-1)
    base_amount: float              # Amount to trade in base currency
    
    def is_expired(self) -> bool:
        """Check if cycle opportunity has expired."""
        return datetime.now() > self.expiration_time
    
    def time_remaining(self) -> float:
        """Get seconds remaining until expiration."""
        delta = self.expiration_time - datetime.now()
        return max(0.0, delta.total_seconds())


@dataclass
class ExecutionState:
    """State of a triangular arbitrage execution."""
    cycle: TriangularCycle
    phase: ExecutionPhase
    entry_price_1: float            # Entry price for first leg
    entry_price_2: float            # Entry price for second leg
    entry_price_3: float            # Entry price for third leg
    current_amount: float           # Current position amount
    execution_start: datetime       # Start of execution
    realized_profit_pct: float      # Actual profit achieved so far
    status: str                     # Human-readable status


class PriceMonitor:
    """Monitors real-time prices for triangular arbitrage detection."""
    
    def __init__(self, history_window: int = 1000):
        """
        Initialize price monitor.
        
        Args:
            history_window: Number of price snapshots to maintain per pair
        """
        self.history_window = history_window
        self.price_history: Dict[str, List[PriceSnapshot]] = {}
        self.current_prices: Dict[str, PriceSnapshot] = {}
        self.update_count: Dict[str, int] = {}
        
        logger.info(f"PriceMonitor initialized with {history_window} window size")
    
    def update_price(
        self,
        pair: str,
        bid: float,
        ask: float,
        volume: float
    ) -> None:
        """
        Update price for a trading pair.
        
        Args:
            pair: Currency pair (e.g., BTC/USD)
            bid: Current bid price
            ask: Current ask price
            volume: Trading volume
        """
        if bid <= 0 or ask <= 0 or bid > ask:
            logger.warning(f"Invalid prices for {pair}: bid={bid}, ask={ask}")
            return
        
        snapshot = PriceSnapshot(
            timestamp=datetime.now(),
            bid=bid,
            ask=ask,
            mid=(bid + ask) / 2,
            volume=volume
        )
        
        if pair not in self.price_history:
            self.price_history[pair] = []
            self.update_count[pair] = 0
        
        self.price_history[pair].append(snapshot)
        if len(self.price_history[pair]) > self.history_window:
            self.price_history[pair].pop(0)
        
        self.current_prices[pair] = snapshot
        self.update_count[pair] += 1
    
    def get_price(self, pair: str) -> Optional[PriceSnapshot]:
        """Get current price snapshot for a pair."""
        return self.current_prices.get(pair)
    
    def get_price_history(self, pair: str, lookback: int = 100) -> List[PriceSnapshot]:
        """Get historical prices for a pair."""
        if pair not in self.price_history:
            return []
        return self.price_history[pair][-lookback:]
    
    def get_average_spread(self, pair: str, lookback: int = 100) -> float:
        """Calculate average bid-ask spread for a pair."""
        history = self.get_price_history(pair, lookback)
        if not history:
            return 0.0
        spreads = [s.spread() for s in history]
        return np.mean(spreads)


class CycleDetector:
    """Detects and evaluates triangular arbitrage cycles."""
    
    def __init__(
        self,
        min_profit_threshold: float = 0.1,  # Minimum 0.1% profit
        min_confidence: float = 0.7,
        cycle_validity_seconds: float = 5.0
    ):
        """
        Initialize cycle detector.
        
        Args:
            min_profit_threshold: Minimum profit percentage to consider
            min_confidence: Minimum confidence level (0-1)
            cycle_validity_seconds: How long a cycle is considered valid
        """
        self.min_profit_threshold = min_profit_threshold
        self.min_confidence = min_confidence
        self.cycle_validity_seconds = cycle_validity_seconds
        self.detected_cycles: List[TriangularCycle] = []
        
        logger.info(
            f"CycleDetector initialized: "
            f"min_profit={min_profit_threshold}%, "
            f"min_confidence={min_confidence}"
        )
    
    def detect_cycles(
        self,
        price_monitor: PriceMonitor,
        pairs: List[str]
    ) -> List[TriangularCycle]:
        """
        Detect profitable triangular arbitrage cycles.
        
        Args:
            price_monitor: PriceMonitor instance with current prices
            pairs: List of trading pairs to analyze
            
        Returns:
            List of detected profitable cycles
        """
        cycles = []
        n = len(pairs)
        
        # Check all possible 3-pair combinations
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    cycle = self._evaluate_cycle(
                        price_monitor,
                        [pairs[i], pairs[j], pairs[k]]
                    )
                    if cycle and cycle.profit_pct > self.min_profit_threshold:
                        cycles.append(cycle)
        
        # Sort by profitability
        cycles.sort(key=lambda c: c.profit_pct, reverse=True)
        self.detected_cycles = cycles
        
        return cycles
    
    def _evaluate_cycle(
        self,
        price_monitor: PriceMonitor,
        pairs: List[str]
    ) -> Optional[TriangularCycle]:
        """
        Evaluate a specific three-pair cycle.
        
        Args:
            price_monitor: PriceMonitor instance
            pairs: List of three pairs
            
        Returns:
            TriangularCycle if profitable, None otherwise
        """
        if len(pairs) != 3:
            return None
        
        # Get prices for all three pairs
        prices = {}
        for pair in pairs:
            p = price_monitor.get_price(pair)
            if not p:
                return None
            prices[pair] = p
        
        # Calculate cycle profit (using ask to buy, bid to sell)
        # Start with 1 unit of base currency
        starting_amount = 1.0
        
        # Leg 1: Sell pair1 (get quote)
        p1 = prices[pairs[0]]
        amount_after_leg1 = starting_amount / p1.ask  # Buy at ask
        
        # Leg 2: Exchange quote for another currency
        p2 = prices[pairs[1]]
        amount_after_leg2 = amount_after_leg1 * p2.bid  # Sell at bid
        
        # Leg 3: Exchange back to original
        p3 = prices[pairs[2]]
        amount_after_leg3 = amount_after_leg2 / p3.ask  # Buy at ask
        
        # Calculate profit
        profit_amount = amount_after_leg3 - starting_amount
        profit_pct = (profit_amount / starting_amount) * 100 if starting_amount > 0 else 0
        
        if profit_pct <= 0:
            return None
        
        # Calculate confidence based on cycle spreads and volume
        avg_spread = np.mean([
            prices[pair].spread() for pair in pairs
        ])
        
        # Higher spread = lower confidence
        confidence = max(0.0, min(1.0, 1.0 - (avg_spread * 100)))
        
        if confidence < self.min_confidence:
            return None
        
        # Create cycle representation
        cycle = TriangularCycle(
            pair1=pairs[0],
            pair2=pairs[1],
            pair3=pairs[2],
            cycle_path=[pairs[0], pairs[1], pairs[2]],
            profit_pct=profit_pct,
            entry_time=datetime.now(),
            expiration_time=datetime.now() + timedelta(seconds=self.cycle_validity_seconds),
            confidence=confidence,
            base_amount=1.0
        )
        
        return cycle
    
    def get_best_cycle(self) -> Optional[TriangularCycle]:
        """Get the most profitable cycle detected."""
        if not self.detected_cycles:
            return None
        return self.detected_cycles[0]
    
    def get_active_cycles(self) -> List[TriangularCycle]:
        """Get all currently active (non-expired) cycles."""
        return [c for c in self.detected_cycles if not c.is_expired()]


class ExecutionCalculator:
    """Calculates optimal execution parameters for cycles."""
    
    def __init__(
        self,
        transaction_fee_pct: float = 0.05,  # 0.05% per trade
        slippage_pct: float = 0.02  # 0.02% expected slippage
    ):
        """
        Initialize execution calculator.
        
        Args:
            transaction_fee_pct: Transaction fee percentage
            slippage_pct: Expected slippage percentage
        """
        self.transaction_fee_pct = transaction_fee_pct
        self.slippage_pct = slippage_pct
        
        logger.info(
            f"ExecutionCalculator initialized: "
            f"fee={transaction_fee_pct}%, slippage={slippage_pct}%"
        )
    
    def calculate_net_profit(self, cycle: TriangularCycle) -> float:
        """
        Calculate net profit after fees and slippage.
        
        Args:
            cycle: TriangularCycle to evaluate
            
        Returns:
            Net profit percentage
        """
        # Three trades = 3x transaction fee
        total_fee = self.transaction_fee_pct * 3
        
        # Slippage on each leg
        total_slippage = self.slippage_pct * 3
        
        net_profit = cycle.profit_pct - total_fee - total_slippage
        return net_profit
    
    def calculate_optimal_position_size(
        self,
        cycle: TriangularCycle,
        available_capital: float,
        max_position_pct: float = 5.0
    ) -> float:
        """
        Calculate optimal position size for execution.
        
        Args:
            cycle: TriangularCycle
            available_capital: Total available capital
            max_position_pct: Maximum percentage of capital to use (%)
            
        Returns:
            Optimal position size in base currency
        """
        # Limit to max percentage of capital
        max_position = (available_capital * max_position_pct) / 100
        
        # Adjust based on confidence and profitability
        net_profit = self.calculate_net_profit(cycle)
        confidence_factor = cycle.confidence
        profitability_factor = min(1.0, net_profit / 1.0)  # Normalize to 1%
        
        position_size = max_position * confidence_factor * profitability_factor
        
        return position_size
    
    def calculate_execution_sequence(
        self,
        cycle: TriangularCycle,
        position_size: float
    ) -> List[Dict[str, Any]]:
        """
        Calculate the optimal execution sequence.
        
        Args:
            cycle: TriangularCycle
            position_size: Position size to execute
            
        Returns:
            List of execution steps with amounts and directions
        """
        steps = []
        current_amount = position_size
        
        for i, pair in enumerate(cycle.cycle_path):
            step = {
                "leg": i + 1,
                "pair": pair,
                "action": "BUY" if i == 0 else ("SELL" if i % 2 == 1 else "BUY"),
                "amount": current_amount,
                "sequence_order": i,
                "estimated_execution_ms": 50 + (i * 10)  # Timing estimates
            }
            steps.append(step)
        
        return steps


class TriangularArbitrageEngine:
    """Main engine for triangular arbitrage detection and execution."""
    
    def __init__(
        self,
        exchange_name: str = "default",
        min_profit_threshold: float = 0.1,
        history_window: int = 1000,
        transaction_fee_pct: float = 0.05
    ):
        """
        Initialize Triangular Arbitrage Engine.
        
        Args:
            exchange_name: Name of the exchange
            min_profit_threshold: Minimum profit threshold (%)
            history_window: Price history window size
            transaction_fee_pct: Transaction fee percentage
        """
        self.exchange_name = exchange_name
        self.price_monitor = PriceMonitor(history_window)
        self.cycle_detector = CycleDetector(
            min_profit_threshold=min_profit_threshold
        )
        self.execution_calculator = ExecutionCalculator(
            transaction_fee_pct=transaction_fee_pct
        )
        self.active_executions: Dict[str, ExecutionState] = {}
        self.execution_history: List[ExecutionState] = []
        
        self.cycle_count = 0
        self.successful_executions = 0
        self.total_profit = 0.0
        
        logger.info(
            f"TriangularArbitrageEngine initialized for {exchange_name}: "
            f"min_profit={min_profit_threshold}%"
        )
    
    def update_market_prices(
        self,
        prices: Dict[str, Tuple[float, float, float]]
    ) -> None:
        """
        Update market prices for multiple pairs.
        
        Args:
            prices: Dict of {pair: (bid, ask, volume)}
        """
        for pair, (bid, ask, volume) in prices.items():
            self.price_monitor.update_price(pair, bid, ask, volume)
    
    def analyze_opportunities(self, pairs: List[str]) -> List[TriangularCycle]:
        """
        Analyze and detect triangular arbitrage opportunities.
        
        Args:
            pairs: List of trading pairs to analyze
            
        Returns:
            List of detected profitable cycles
        """
        cycles = self.cycle_detector.detect_cycles(self.price_monitor, pairs)
        self.cycle_count += len(cycles)
        return cycles
    
    def prepare_execution(
        self,
        cycle: TriangularCycle,
        available_capital: float
    ) -> Dict[str, Any]:
        """
        Prepare execution plan for a cycle.
        
        Args:
            cycle: TriangularCycle to execute
            available_capital: Available capital for execution
            
        Returns:
            Execution plan with details
        """
        net_profit = self.execution_calculator.calculate_net_profit(cycle)
        
        if net_profit <= 0:
            logger.warning(f"Cycle has negative net profit: {net_profit}%")
            return {}
        
        position_size = self.execution_calculator.calculate_optimal_position_size(
            cycle,
            available_capital
        )
        
        if position_size <= 0:
            logger.warning("Position size too small for execution")
            return {}
        
        execution_steps = self.execution_calculator.calculate_execution_sequence(
            cycle,
            position_size
        )
        
        plan = {
            "cycle": cycle,
            "net_profit_pct": net_profit,
            "position_size": position_size,
            "estimated_profit_usd": (net_profit / 100) * position_size,
            "execution_steps": execution_steps,
            "confidence": cycle.confidence,
            "time_available_ms": cycle.time_remaining() * 1000
        }
        
        logger.info(
            f"Execution plan prepared: {cycle.pair1}-{cycle.pair2}-{cycle.pair3} "
            f"profit={net_profit:.3f}%, position={position_size:.4f}"
        )
        
        return plan
    
    def execute_cycle(
        self,
        cycle: TriangularCycle,
        position_size: float,
        execution_id: str = ""
    ) -> ExecutionState:
        """
        Execute a triangular arbitrage cycle.
        
        Args:
            cycle: TriangularCycle to execute
            position_size: Position size
            execution_id: Unique identifier for execution
            
        Returns:
            ExecutionState tracking the execution
        """
        state = ExecutionState(
            cycle=cycle,
            phase=ExecutionPhase.INITIAL,
            entry_price_1=0.0,
            entry_price_2=0.0,
            entry_price_3=0.0,
            current_amount=position_size,
            execution_start=datetime.now(),
            realized_profit_pct=0.0,
            status="INITIATED"
        )
        
        if not execution_id:
            execution_id = f"TRIARG_{datetime.now().timestamp()}"
        
        self.active_executions[execution_id] = state
        self.successful_executions += 1
        
        logger.info(f"Cycle execution started: {execution_id}")
        
        return state
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "exchange": self.exchange_name,
            "cycles_detected": self.cycle_count,
            "successful_executions": self.successful_executions,
            "total_profit_usd": self.total_profit,
            "active_executions": len(self.active_executions),
            "execution_history_count": len(self.execution_history),
            "timestamp": datetime.now().isoformat()
        }
