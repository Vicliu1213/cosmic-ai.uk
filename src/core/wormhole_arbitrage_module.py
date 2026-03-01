#!/usr/bin/env python3
"""
Wormhole Arbitrage Module
蟲洞套利模塊

This module implements cross-exchange arbitrage detection and execution.
Detects price discrepancies across multiple exchanges for the same assets.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    """Enumeration of supported exchange types."""
    CENTRALIZED = "centralized"     # CEX (Binance, Kraken, etc.)
    DECENTRALIZED = "decentralized" # DEX (Uniswap, etc.)
    HYBRID = "hybrid"               # Hybrid platforms


class ArbitrageDimension(Enum):
    """Enumeration of arbitrage dimensions."""
    SIMPLE = "simple"               # Two exchanges, same pair
    TRIANGLE = "triangle"           # Three exchanges
    QUAD = "quad"                  # Four exchanges
    COMPLEX = "complex"            # 5+ exchanges


@dataclass
class ExchangeInfo:
    """Information about a connected exchange."""
    exchange_id: str
    exchange_name: str
    exchange_type: ExchangeType
    base_fee: float                 # Trading fee %
    withdrawal_fee: float           # Network withdrawal fee %
    deposit_fee: float              # Deposit fee %
    supported_pairs: Set[str]       # Pairs available on this exchange
    connection_latency_ms: float    # Average latency in milliseconds
    last_update: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class ExchangePrice:
    """Price snapshot from a specific exchange."""
    exchange_id: str
    pair: str
    bid: float
    ask: float
    timestamp: datetime
    volume: float
    
    @property
    def mid(self) -> float:
        """Get mid price."""
        return (self.bid + self.ask) / 2 if self.bid > 0 and self.ask > 0 else 0.0
    
    @property
    def spread_pct(self) -> float:
        """Get spread as percentage."""
        if self.mid <= 0:
            return 0.0
        return ((self.ask - self.bid) / self.mid) * 100


@dataclass
class WormholeOpportunity:
    """Cross-exchange arbitrage opportunity."""
    opportunity_id: str
    pair: str
    buy_exchange: str              # Exchange to buy from
    sell_exchange: str             # Exchange to sell to
    buy_price: float
    sell_price: float
    profit_pct: float              # Gross profit %
    net_profit_pct: float          # Net profit after fees %
    volume_available: float        # How much can be executed
    execution_time_sec: float      # Estimated execution time
    confidence: float              # Confidence level (0-1)
    created_at: datetime           # When opportunity was identified
    expires_at: datetime           # When opportunity expires
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if opportunity has expired."""
        return datetime.now() > self.expires_at or not self.is_active
    
    def time_remaining_sec(self) -> float:
        """Get seconds remaining until expiration."""
        delta = self.expires_at - datetime.now()
        return max(0.0, delta.total_seconds())


@dataclass
class WormholeExecution:
    """Execution record of a wormhole arbitrage trade."""
    execution_id: str
    opportunity: WormholeOpportunity
    buy_order_id: Optional[str] = None
    sell_order_id: Optional[str] = None
    buy_execution_price: Optional[float] = None
    sell_execution_price: Optional[float] = None
    execution_start: datetime = field(default_factory=datetime.now)
    execution_end: Optional[datetime] = None
    status: str = "PENDING"        # PENDING, BUY_FILLED, SELL_FILLED, COMPLETE, FAILED
    actual_profit_usd: Optional[float] = None
    execution_fees: float = 0.0
    withdrawal_time_sec: float = 0.0  # Time to withdraw from buy exchange
    deposit_time_sec: float = 0.0      # Time to deposit to sell exchange


class ExchangeConnector:
    """Manages connections to multiple exchanges."""
    
    def __init__(self):
        """Initialize exchange connector."""
        self.exchanges: Dict[str, ExchangeInfo] = {}
        self.prices: Dict[str, Dict[str, ExchangePrice]] = {}  # {exchange_id: {pair: price}}
        self.price_history: Dict[str, List[ExchangePrice]] = {}
        self.connection_status: Dict[str, bool] = {}
        
        logger.info("ExchangeConnector initialized")
    
    def register_exchange(self, info: ExchangeInfo) -> None:
        """
        Register a new exchange.
        
        Args:
            info: ExchangeInfo describing the exchange
        """
        self.exchanges[info.exchange_id] = info
        self.prices[info.exchange_id] = {}
        self.connection_status[info.exchange_id] = True
        
        logger.info(f"Exchange registered: {info.exchange_name} ({info.exchange_id})")
    
    def update_price(self, exchange_id: str, price: ExchangePrice) -> None:
        """
        Update price for a pair from an exchange.
        
        Args:
            exchange_id: Exchange identifier
            price: ExchangePrice data
        """
        if exchange_id not in self.exchanges:
            logger.warning(f"Unknown exchange: {exchange_id}")
            return
        
        self.prices[exchange_id][price.pair] = price
        
        # Maintain price history
        key = f"{exchange_id}_{price.pair}"
        if key not in self.price_history:
            self.price_history[key] = []
        
        self.price_history[key].append(price)
        
        # Keep only recent history
        if len(self.price_history[key]) > 1000:
            self.price_history[key].pop(0)
    
    def get_price(self, exchange_id: str, pair: str) -> Optional[ExchangePrice]:
        """Get current price for a pair from an exchange."""
        if exchange_id not in self.prices:
            return None
        return self.prices[exchange_id].get(pair)
    
    def get_all_prices_for_pair(self, pair: str) -> Dict[str, ExchangePrice]:
        """Get current prices for a pair from all exchanges."""
        result = {}
        for exchange_id, pairs_dict in self.prices.items():
            if pair in pairs_dict:
                result[exchange_id] = pairs_dict[pair]
        return result
    
    def get_active_exchanges(self) -> List[ExchangeInfo]:
        """Get list of active exchanges."""
        return [ex for ex in self.exchanges.values() if ex.is_active]
    
    def set_exchange_status(self, exchange_id: str, is_active: bool) -> None:
        """Update exchange active status."""
        if exchange_id in self.exchanges:
            self.exchanges[exchange_id].is_active = is_active
            self.connection_status[exchange_id] = is_active


class OpportunityScan:
    """Scans for wormhole arbitrage opportunities."""
    
    def __init__(
        self,
        min_profit_threshold: float = 0.2,  # Minimum 0.2% profit
        min_confidence: float = 0.65,
        opportunity_validity_sec: float = 10.0,
        max_dimension: ArbitrageDimension = ArbitrageDimension.TRIANGLE
    ):
        """
        Initialize opportunity scanner.
        
        Args:
            min_profit_threshold: Minimum profit threshold (%)
            min_confidence: Minimum confidence level (0-1)
            opportunity_validity_sec: How long opportunity is valid
            max_dimension: Maximum dimension to scan
        """
        self.min_profit_threshold = min_profit_threshold
        self.min_confidence = min_confidence
        self.opportunity_validity_sec = opportunity_validity_sec
        self.max_dimension = max_dimension
        
        self.opportunities: List[WormholeOpportunity] = []
        self.opportunity_count = 0
        
        logger.info(
            f"OpportunityScan initialized: "
            f"min_profit={min_profit_threshold}%, min_confidence={min_confidence}"
        )
    
    def scan_pair(
        self,
        pair: str,
        exchange_connector: ExchangeConnector,
        dimension: ArbitrageDimension = ArbitrageDimension.SIMPLE
    ) -> List[WormholeOpportunity]:
        """
        Scan for arbitrage opportunities for a specific pair.
        
        Args:
            pair: Trading pair to scan
            exchange_connector: ExchangeConnector with current prices
            dimension: Which dimension to scan
            
        Returns:
            List of identified opportunities
        """
        opportunities = []
        
        # Get prices from all exchanges
        prices = exchange_connector.get_all_prices_for_pair(pair)
        
        if len(prices) < 2:
            return opportunities
        
        # Simple 2-exchange arbitrage
        exchange_ids = list(prices.keys())
        
        for i, buy_ex in enumerate(exchange_ids):
            for sell_ex in exchange_ids[i+1:]:
                opp = self._evaluate_simple_arbitrage(
                    pair,
                    buy_ex,
                    sell_ex,
                    prices[buy_ex],
                    prices[sell_ex],
                    exchange_connector
                )
                if opp:
                    opportunities.append(opp)
        
        self.opportunities.extend(opportunities)
        self.opportunity_count += len(opportunities)
        
        return opportunities
    
    def _evaluate_simple_arbitrage(
        self,
        pair: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_price: ExchangePrice,
        sell_price: ExchangePrice,
        connector: ExchangeConnector
    ) -> Optional[WormholeOpportunity]:
        """
        Evaluate a simple 2-exchange arbitrage opportunity.
        
        Args:
            pair: Trading pair
            buy_exchange: Exchange to buy from
            sell_exchange: Exchange to sell to
            buy_price: Price at buy exchange
            sell_price: Price at sell exchange
            connector: ExchangeConnector for fee info
            
        Returns:
            WormholeOpportunity if profitable, None otherwise
        """
        # Get exchange info
        buy_ex_info = connector.exchanges.get(buy_exchange)
        sell_ex_info = connector.exchanges.get(sell_exchange)
        
        if not buy_ex_info or not sell_ex_info:
            return None
        
        # Calculate gross profit (buy at ask, sell at bid)
        gross_profit_pct = ((sell_price.bid - buy_price.ask) / buy_price.ask) * 100
        
        if gross_profit_pct <= 0:
            return None
        
        # Calculate net profit after all fees
        # Buy fee + sell fee + withdrawal fee (from buy exchange) + deposit fee (to sell exchange)
        total_fees = (
            buy_ex_info.base_fee +
            sell_ex_info.base_fee +
            buy_ex_info.withdrawal_fee +
            sell_ex_info.deposit_fee
        )
        
        net_profit_pct = gross_profit_pct - total_fees
        
        if net_profit_pct <= self.min_profit_threshold:
            return None
        
        # Calculate confidence based on spreads and volume
        spread_factor = (buy_price.spread_pct + sell_price.spread_pct) / 2
        volume_factor = min(1.0, buy_price.volume / 10.0)  # Normalize volume
        
        confidence = max(0.0, min(1.0, 0.8 * (1.0 - spread_factor / 5.0) * volume_factor))
        
        if confidence < self.min_confidence:
            return None
        
        # Create opportunity
        opportunity = WormholeOpportunity(
            opportunity_id=f"WHOP_{datetime.now().timestamp()}",
            pair=pair,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            buy_price=buy_price.ask,
            sell_price=sell_price.bid,
            profit_pct=gross_profit_pct,
            net_profit_pct=net_profit_pct,
            volume_available=min(buy_price.volume, sell_price.volume),
            execution_time_sec=buy_ex_info.connection_latency_ms / 1000.0 +
                               sell_ex_info.connection_latency_ms / 1000.0 + 1.0,
            confidence=confidence,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.opportunity_validity_sec)
        )
        
        return opportunity
    
    def get_best_opportunities(self, limit: int = 10) -> List[WormholeOpportunity]:
        """
        Get the best opportunities by profit.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            Sorted list of best opportunities
        """
        active_opps = [o for o in self.opportunities if not o.is_expired()]
        active_opps.sort(key=lambda o: o.net_profit_pct, reverse=True)
        return active_opps[:limit]


class TransferCostEstimator:
    """Estimates transfer costs and times between exchanges."""
    
    def __init__(self):
        """Initialize transfer cost estimator."""
        # Network transfer time estimates (in seconds)
        self.network_delays: Dict[Tuple[str, str], float] = {}
        
        # Confirmation time estimates by blockchain
        self.confirmation_times = {
            "ethereum": 12.0,    # ~12 seconds
            "bitcoin": 600.0,    # ~10 minutes
            "bsc": 3.0,          # ~3 seconds
            "polygon": 2.0,      # ~2 seconds
            "optimism": 2.0,
            "arbitrum": 1.0
        }
        
        logger.info("TransferCostEstimator initialized")
    
    def estimate_transfer_time(
        self,
        from_exchange: str,
        to_exchange: str,
        blockchain: str = "ethereum"
    ) -> float:
        """
        Estimate total transfer time between exchanges.
        
        Args:
            from_exchange: Source exchange
            to_exchange: Destination exchange
            blockchain: Blockchain network
            
        Returns:
            Estimated time in seconds
        """
        key = (from_exchange, to_exchange)
        
        if key in self.network_delays:
            network_time = self.network_delays[key]
        else:
            # Default estimate
            network_time = 5.0
        
        confirmation_time = self.confirmation_times.get(blockchain, 30.0)
        
        # Add processing time
        processing_time = 2.0
        
        total = network_time + confirmation_time + processing_time
        
        return total
    
    def estimate_transfer_cost_pct(self, blockchain: str = "ethereum") -> float:
        """
        Estimate transfer cost as percentage.
        
        Args:
            blockchain: Blockchain network
            
        Returns:
            Estimated cost as percentage
        """
        # Typical gas costs as percentage of transaction
        gas_costs = {
            "ethereum": 0.15,    # ~0.15%
            "bitcoin": 0.20,     # ~0.20%
            "bsc": 0.01,         # ~0.01%
            "polygon": 0.001,    # ~0.001%
            "optimism": 0.01,
            "arbitrum": 0.01
        }
        
        return gas_costs.get(blockchain, 0.10)


class WormholeArbitrageModule:
    """Main module for cross-exchange (wormhole) arbitrage."""
    
    def __init__(self, module_name: str = "wormhole_default"):
        """
        Initialize Wormhole Arbitrage Module.
        
        Args:
            module_name: Name of this module instance
        """
        self.module_name = module_name
        self.exchange_connector = ExchangeConnector()
        self.opportunity_scanner = OpportunityScan()
        self.transfer_cost_estimator = TransferCostEstimator()
        
        self.active_executions: Dict[str, WormholeExecution] = {}
        self.execution_history: List[WormholeExecution] = []
        
        self.total_opportunities_found = 0
        self.successful_executions = 0
        self.total_profit_usd = 0.0
        
        logger.info(f"WormholeArbitrageModule initialized: {module_name}")
    
    def register_exchange(
        self,
        exchange_id: str,
        exchange_name: str,
        exchange_type: ExchangeType,
        base_fee: float,
        withdrawal_fee: float,
        deposit_fee: float,
        supported_pairs: List[str],
        connection_latency_ms: float = 50.0
    ) -> None:
        """
        Register a new exchange connector.
        
        Args:
            exchange_id: Unique identifier for exchange
            exchange_name: Display name
            exchange_type: Type of exchange
            base_fee: Trading fee percentage
            withdrawal_fee: Withdrawal fee percentage
            deposit_fee: Deposit fee percentage
            supported_pairs: List of supported pairs
            connection_latency_ms: Connection latency
        """
        info = ExchangeInfo(
            exchange_id=exchange_id,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
            base_fee=base_fee,
            withdrawal_fee=withdrawal_fee,
            deposit_fee=deposit_fee,
            supported_pairs=set(supported_pairs),
            connection_latency_ms=connection_latency_ms
        )
        
        self.exchange_connector.register_exchange(info)
    
    def update_price(
        self,
        exchange_id: str,
        pair: str,
        bid: float,
        ask: float,
        volume: float
    ) -> None:
        """
        Update price for a pair from an exchange.
        
        Args:
            exchange_id: Exchange identifier
            pair: Trading pair
            bid: Current bid price
            ask: Current ask price
            volume: Trading volume
        """
        price = ExchangePrice(
            exchange_id=exchange_id,
            pair=pair,
            bid=bid,
            ask=ask,
            timestamp=datetime.now(),
            volume=volume
        )
        
        self.exchange_connector.update_price(exchange_id, price)
    
    def scan_opportunities(self, pairs: List[str]) -> List[WormholeOpportunity]:
        """
        Scan for wormhole arbitrage opportunities across all registered exchanges.
        
        Args:
            pairs: List of trading pairs to scan
            
        Returns:
            List of identified opportunities
        """
        all_opportunities = []
        
        for pair in pairs:
            opportunities = self.opportunity_scanner.scan_pair(
                pair,
                self.exchange_connector
            )
            all_opportunities.extend(opportunities)
        
        self.total_opportunities_found += len(all_opportunities)
        
        return all_opportunities
    
    def get_best_opportunities(self, limit: int = 10) -> List[WormholeOpportunity]:
        """Get the best opportunities ranked by net profit."""
        return self.opportunity_scanner.get_best_opportunities(limit)
    
    def prepare_execution(
        self,
        opportunity: WormholeOpportunity,
        execution_amount: float
    ) -> Dict[str, Any]:
        """
        Prepare execution plan for an opportunity.
        
        Args:
            opportunity: WormholeOpportunity to execute
            execution_amount: Amount to execute
            
        Returns:
            Execution plan with details
        """
        if opportunity.is_expired():
            logger.warning(f"Opportunity expired: {opportunity.opportunity_id}")
            return {}
        
        # Estimate transfer times
        transfer_time = self.transfer_cost_estimator.estimate_transfer_time(
            opportunity.buy_exchange,
            opportunity.sell_exchange
        )
        
        transfer_cost = self.transfer_cost_estimator.estimate_transfer_cost_pct()
        
        # Adjust net profit for transfer costs
        net_profit_adjusted = opportunity.net_profit_pct - transfer_cost
        
        if net_profit_adjusted <= 0:
            logger.warning("Opportunity no longer profitable after transfer costs")
            return {}
        
        plan = {
            "opportunity_id": opportunity.opportunity_id,
            "pair": opportunity.pair,
            "buy_exchange": opportunity.buy_exchange,
            "sell_exchange": opportunity.sell_exchange,
            "buy_price": opportunity.buy_price,
            "sell_price": opportunity.sell_price,
            "gross_profit_pct": opportunity.profit_pct,
            "net_profit_pct": opportunity.net_profit_pct,
            "execution_amount": execution_amount,
            "estimated_profit_usd": (net_profit_adjusted / 100) * execution_amount,
            "transfer_time_sec": transfer_time,
            "transfer_cost_pct": transfer_cost,
            "confidence": opportunity.confidence,
            "time_window_sec": opportunity.time_remaining_sec(),
            "feasible": opportunity.time_remaining_sec() > transfer_time
        }
        
        logger.info(
            f"Execution plan prepared: {opportunity.pair} "
            f"{opportunity.buy_exchange}→{opportunity.sell_exchange} "
            f"profit={net_profit_adjusted:.3f}%"
        )
        
        return plan
    
    def execute_opportunity(
        self,
        opportunity: WormholeOpportunity,
        execution_amount: float,
        execution_id: str = ""
    ) -> WormholeExecution:
        """
        Execute a wormhole arbitrage opportunity.
        
        Args:
            opportunity: WormholeOpportunity to execute
            execution_amount: Amount to execute
            execution_id: Unique identifier
            
        Returns:
            WormholeExecution tracking the execution
        """
        if not execution_id:
            execution_id = f"WHEX_{datetime.now().timestamp()}"
        
        execution = WormholeExecution(
            execution_id=execution_id,
            opportunity=opportunity,
            status="PENDING"
        )
        
        # Estimate transfer times
        execution.withdrawal_time_sec = self.transfer_cost_estimator.estimate_transfer_time(
            opportunity.buy_exchange,
            opportunity.sell_exchange
        ) / 2
        
        execution.deposit_time_sec = self.transfer_cost_estimator.estimate_transfer_time(
            opportunity.buy_exchange,
            opportunity.sell_exchange
        ) / 2
        
        self.active_executions[execution_id] = execution
        self.successful_executions += 1
        
        logger.info(f"Wormhole execution started: {execution_id}")
        
        return execution
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "module_name": self.module_name,
            "registered_exchanges": len(self.exchange_connector.exchanges),
            "active_exchanges": len(self.exchange_connector.get_active_exchanges()),
            "opportunities_found": self.total_opportunities_found,
            "successful_executions": self.successful_executions,
            "total_profit_usd": self.total_profit_usd,
            "active_executions": len(self.active_executions),
            "execution_history_count": len(self.execution_history),
            "timestamp": datetime.now().isoformat()
        }
