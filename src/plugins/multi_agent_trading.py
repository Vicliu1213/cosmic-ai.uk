#!/usr/bin/env python3
"""
Multi-Agent Trading System
多智能體交易系統

Provides a comprehensive multi-agent trading framework with portfolio management,
risk management, and signal analysis agents for autonomous trading decisions.
提供包含組合管理、風險管理和信號分析智能體的多智能體交易框架。
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent role enumeration - 智能體角色"""
    PORTFOLIO_MANAGER = "portfolio_manager"
    RISK_MANAGER = "risk_manager"
    SIGNAL_ANALYST = "signal_analyst"
    COORDINATOR = "coordinator"


class DecisionType(Enum):
    """Decision type enumeration - 決策類型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REBALANCE = "rebalance"


@dataclass
class TradingDecision:
    """Trading decision data structure - 交易決策數據結構"""
    agent_id: str
    decision_type: DecisionType
    symbol: str
    quantity: float
    price: float
    confidence: float
    timestamp: datetime
    rationale: str
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'agent_id': self.agent_id,
            'decision_type': self.decision_type.value,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'rationale': self.rationale,
            'risk_score': self.risk_score
        }


@dataclass
class PortfolioState:
    """Portfolio state data structure - 投資組合狀態"""
    positions: Dict[str, float] = field(default_factory=dict)
    cash: float = 0.0
    total_value: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'positions': self.positions,
            'cash': self.cash,
            'total_value': self.total_value,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class MarketData:
    """Market data structure - 市場數據"""
    symbol: str
    price: float
    volume: float
    bid: float
    ask: float
    timestamp: datetime
    indicators: Dict[str, float] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base agent class with decision-making capabilities.
    基礎智能體類，具有決策能力。
    
    Attributes:
        agent_id (str): Unique agent identifier
        role (AgentRole): Agent's role
        confidence_threshold (float): Minimum confidence for decisions
    """
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            role: The role of the agent
            confidence_threshold: Minimum confidence level for decisions (0.0-1.0)
        """
        self.agent_id = agent_id
        self.role = role
        self.confidence_threshold = confidence_threshold
        self.decision_history: List[TradingDecision] = []
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
    @abstractmethod
    def analyze(self, market_data: MarketData, portfolio: PortfolioState) -> Optional[TradingDecision]:
        """
        Analyze market data and make trading decision.
        分析市場數據並做出交易決策。
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            
        Returns:
            TradingDecision if confident enough, None otherwise
        """
        pass
    
    def record_decision(self, decision: TradingDecision) -> None:
        """Record a trading decision in history."""
        self.decision_history.append(decision)
        self.logger.info(f"Decision recorded: {decision.decision_type.value} {decision.quantity} {decision.symbol}")
    
    def get_decision_history(self, limit: int = 100) -> List[TradingDecision]:
        """Get recent decision history."""
        return self.decision_history[-limit:]


class PortfolioManagementAgent(BaseAgent):
    """
    Portfolio management agent that handles position sizing and allocation.
    組合管理智能體，處理頭寸大小和配置。
    
    Manages portfolio allocation across multiple assets and rebalances
    the portfolio to maintain target allocations.
    """
    
    def __init__(
        self,
        agent_id: str = "pm_agent_1",
        target_allocations: Optional[Dict[str, float]] = None,
        rebalance_threshold: float = 0.05
    ):
        """
        Initialize portfolio management agent.
        
        Args:
            agent_id: Unique agent identifier
            target_allocations: Target allocation percentages
            rebalance_threshold: Trigger rebalance if drift exceeds this
        """
        super().__init__(agent_id, AgentRole.PORTFOLIO_MANAGER)
        self.target_allocations = target_allocations or {}
        self.rebalance_threshold = rebalance_threshold
        
    def analyze(
        self,
        market_data: MarketData,
        portfolio: PortfolioState
    ) -> Optional[TradingDecision]:
        """
        Analyze portfolio allocation and determine rebalancing needs.
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            
        Returns:
            TradingDecision for rebalancing or None
        """
        try:
            if not self.target_allocations:
                return None
            
            current_allocations = self._calculate_allocations(portfolio)
            drift = self._calculate_allocation_drift(current_allocations)
            
            if drift > self.rebalance_threshold:
                decision = self._create_rebalance_decision(
                    market_data, portfolio, drift
                )
                if decision.confidence >= self.confidence_threshold:
                    self.record_decision(decision)
                    return decision
                    
        except Exception as e:
            self.logger.error(f"Error in portfolio analysis: {e}")
            
        return None
    
    def _calculate_allocations(self, portfolio: PortfolioState) -> Dict[str, float]:
        """Calculate current portfolio allocations."""
        if portfolio.total_value <= 0:
            return {}
        
        allocations = {}
        for symbol, quantity in portfolio.positions.items():
            # Estimate position value (simplified)
            position_value = quantity * 100  # Placeholder
            allocations[symbol] = position_value / portfolio.total_value
            
        return allocations
    
    def _calculate_allocation_drift(self, current: Dict[str, float]) -> float:
        """Calculate total allocation drift from targets."""
        total_drift = 0.0
        for symbol, target in self.target_allocations.items():
            current_alloc = current.get(symbol, 0.0)
            total_drift += abs(current_alloc - target)
        return total_drift
    
    def _create_rebalance_decision(
        self,
        market_data: MarketData,
        portfolio: PortfolioState,
        drift: float
    ) -> TradingDecision:
        """Create a rebalancing decision."""
        confidence = min(0.9, drift)  # Higher drift = higher confidence
        
        return TradingDecision(
            agent_id=self.agent_id,
            decision_type=DecisionType.REBALANCE,
            symbol=market_data.symbol,
            quantity=portfolio.total_value * 0.01,  # 1% rebalance
            price=market_data.price,
            confidence=confidence,
            timestamp=datetime.now(),
            rationale=f"Portfolio drift {drift:.2%} exceeds threshold {self.rebalance_threshold:.2%}",
            risk_score=drift
        )


class RiskManagementAgent(BaseAgent):
    """
    Risk management agent that monitors and controls portfolio risk.
    風險管理智能體，監控和控制投資組合風險。
    
    Enforces risk limits, stop-loss orders, and position limits.
    """
    
    def __init__(
        self,
        agent_id: str = "rm_agent_1",
        max_position_size: float = 0.1,
        max_portfolio_loss: float = 0.02,
        var_threshold: float = 0.95
    ):
        """
        Initialize risk management agent.
        
        Args:
            agent_id: Unique agent identifier
            max_position_size: Maximum position size as % of portfolio
            max_portfolio_loss: Maximum allowed portfolio loss %
            var_threshold: Value at Risk threshold (confidence level)
        """
        super().__init__(agent_id, AgentRole.RISK_MANAGER)
        self.max_position_size = max_position_size
        self.max_portfolio_loss = max_portfolio_loss
        self.var_threshold = var_threshold
        
    def analyze(
        self,
        market_data: MarketData,
        portfolio: PortfolioState
    ) -> Optional[TradingDecision]:
        """
        Analyze portfolio risk and determine risk mitigation actions.
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            
        Returns:
            TradingDecision to reduce risk or None
        """
        try:
            # Check position size limits
            position_value = portfolio.positions.get(market_data.symbol, 0) * market_data.price
            max_allowed = portfolio.total_value * self.max_position_size
            
            if position_value > max_allowed:
                decision = self._create_risk_reduction_decision(
                    market_data, portfolio, position_value, max_allowed
                )
                if decision.confidence >= self.confidence_threshold:
                    self.record_decision(decision)
                    return decision
            
            # Check portfolio loss limit
            if portfolio.unrealized_pnl < -portfolio.total_value * self.max_portfolio_loss:
                decision = self._create_emergency_exit_decision(market_data, portfolio)
                if decision.confidence >= self.confidence_threshold:
                    self.record_decision(decision)
                    return decision
                    
        except Exception as e:
            self.logger.error(f"Error in risk analysis: {e}")
            
        return None
    
    def _create_risk_reduction_decision(
        self,
        market_data: MarketData,
        portfolio: PortfolioState,
        current_size: float,
        max_allowed: float
    ) -> TradingDecision:
        """Create decision to reduce oversized position."""
        excess = current_size - max_allowed
        quantity_to_sell = excess / market_data.price if market_data.price > 0 else 0
        
        return TradingDecision(
            agent_id=self.agent_id,
            decision_type=DecisionType.SELL,
            symbol=market_data.symbol,
            quantity=quantity_to_sell,
            price=market_data.price,
            confidence=0.95,
            timestamp=datetime.now(),
            rationale=f"Position size {current_size:.2f} exceeds limit {max_allowed:.2f}",
            risk_score=0.9
        )
    
    def _create_emergency_exit_decision(
        self,
        market_data: MarketData,
        portfolio: PortfolioState
    ) -> TradingDecision:
        """Create emergency exit decision when loss limit exceeded."""
        all_positions_qty = sum(portfolio.positions.values())
        
        return TradingDecision(
            agent_id=self.agent_id,
            decision_type=DecisionType.SELL,
            symbol=market_data.symbol,
            quantity=portfolio.positions.get(market_data.symbol, 0) * 0.5,
            price=market_data.price,
            confidence=0.99,
            timestamp=datetime.now(),
            rationale=f"Emergency exit: Portfolio loss {portfolio.unrealized_pnl:.2f} exceeds limit",
            risk_score=0.99
        )


class SignalAnalysisAgent(BaseAgent):
    """
    Signal analysis agent that identifies trading opportunities.
    信號分析智能體，識別交易機會。
    
    Uses technical indicators and market data to generate trading signals.
    """
    
    def __init__(
        self,
        agent_id: str = "sa_agent_1",
        sma_short: int = 20,
        sma_long: int = 50,
        rsi_threshold: float = 0.3
    ):
        """
        Initialize signal analysis agent.
        
        Args:
            agent_id: Unique agent identifier
            sma_short: Short SMA period
            sma_long: Long SMA period
            rsi_threshold: RSI threshold for signal generation
        """
        super().__init__(agent_id, AgentRole.SIGNAL_ANALYST)
        self.sma_short = sma_short
        self.sma_long = sma_long
        self.rsi_threshold = rsi_threshold
        
    def analyze(
        self,
        market_data: MarketData,
        portfolio: PortfolioState
    ) -> Optional[TradingDecision]:
        """
        Analyze market data indicators and generate trading signals.
        
        Args:
            market_data: Current market data with indicators
            portfolio: Current portfolio state
            
        Returns:
            TradingDecision if signal detected, None otherwise
        """
        try:
            if not market_data.indicators:
                return None
            
            # Check SMA crossover
            sma_signal = self._check_sma_crossover(market_data)
            if sma_signal:
                self.record_decision(sma_signal)
                return sma_signal
            
            # Check RSI signal
            rsi_signal = self._check_rsi_signal(market_data)
            if rsi_signal:
                self.record_decision(rsi_signal)
                return rsi_signal
                
        except Exception as e:
            self.logger.error(f"Error in signal analysis: {e}")
            
        return None
    
    def _check_sma_crossover(self, market_data: MarketData) -> Optional[TradingDecision]:
        """Check for SMA crossover signals."""
        sma_short = market_data.indicators.get('sma_short', 0)
        sma_long = market_data.indicators.get('sma_long', 0)
        
        if sma_short <= 0 or sma_long <= 0:
            return None
        
        if sma_short > sma_long:  # Bullish crossover
            return TradingDecision(
                agent_id=self.agent_id,
                decision_type=DecisionType.BUY,
                symbol=market_data.symbol,
                quantity=1.0,
                price=market_data.price,
                confidence=0.75,
                timestamp=datetime.now(),
                rationale=f"SMA crossover: {sma_short:.2f} > {sma_long:.2f}",
                risk_score=0.25
            )
        elif sma_short < sma_long:  # Bearish crossover
            return TradingDecision(
                agent_id=self.agent_id,
                decision_type=DecisionType.SELL,
                symbol=market_data.symbol,
                quantity=1.0,
                price=market_data.price,
                confidence=0.70,
                timestamp=datetime.now(),
                rationale=f"SMA crossover: {sma_short:.2f} < {sma_long:.2f}",
                risk_score=0.20
            )
        
        return None
    
    def _check_rsi_signal(self, market_data: MarketData) -> Optional[TradingDecision]:
        """Check for RSI-based signals."""
        rsi = market_data.indicators.get('rsi', 0.5)
        
        if rsi < self.rsi_threshold:  # Oversold
            return TradingDecision(
                agent_id=self.agent_id,
                decision_type=DecisionType.BUY,
                symbol=market_data.symbol,
                quantity=1.0,
                price=market_data.price,
                confidence=0.65,
                timestamp=datetime.now(),
                rationale=f"RSI oversold: {rsi:.2f} < {self.rsi_threshold}",
                risk_score=0.15
            )
        elif rsi > (1.0 - self.rsi_threshold):  # Overbought
            return TradingDecision(
                agent_id=self.agent_id,
                decision_type=DecisionType.SELL,
                symbol=market_data.symbol,
                quantity=1.0,
                price=market_data.price,
                confidence=0.60,
                timestamp=datetime.now(),
                rationale=f"RSI overbought: {rsi:.2f} > {1.0 - self.rsi_threshold}",
                risk_score=0.20
            )
        
        return None


class MultiAgentCoordinator:
    """
    Coordinator for managing multiple trading agents.
    多智能體協調器，管理多個交易智能體。
    
    Aggregates decisions from multiple agents and applies voting/consensus
    mechanisms to determine final trading actions.
    """
    
    def __init__(self, coordinator_id: str = "coordinator_1"):
        """
        Initialize the multi-agent coordinator.
        
        Args:
            coordinator_id: Unique identifier for the coordinator
        """
        self.coordinator_id = coordinator_id
        self.agents: Dict[str, BaseAgent] = {}
        self.decision_log: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.{coordinator_id}")
        
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the coordinator.
        
        Args:
            agent: The agent to register
        """
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_id} (role: {agent.role.value})")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the coordinator."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    def coordinate_decisions(
        self,
        market_data: MarketData,
        portfolio: PortfolioState,
        voting_threshold: float = 0.5
    ) -> Optional[TradingDecision]:
        """
        Coordinate decisions from all registered agents.
        
        收集所有智能體的決策並應用投票機制。
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            voting_threshold: Minimum agreement percentage for decision
            
        Returns:
            Final trading decision or None
        """
        if not self.agents:
            self.logger.warning("No agents registered with coordinator")
            return None
        
        try:
            decisions = self._collect_decisions(market_data, portfolio)
            
            if not decisions:
                return None
            
            final_decision = self._apply_consensus(
                decisions, market_data, voting_threshold
            )
            
            if final_decision:
                self._log_coordination(decisions, final_decision)
                
            return final_decision
            
        except Exception as e:
            self.logger.error(f"Error in coordination: {e}")
            return None
    
    def _collect_decisions(
        self,
        market_data: MarketData,
        portfolio: PortfolioState
    ) -> List[TradingDecision]:
        """Collect decisions from all agents."""
        decisions = []
        
        for agent_id, agent in self.agents.items():
            try:
                decision = agent.analyze(market_data, portfolio)
                if decision:
                    decisions.append(decision)
            except Exception as e:
                self.logger.error(f"Error getting decision from {agent_id}: {e}")
        
        return decisions
    
    def _apply_consensus(
        self,
        decisions: List[TradingDecision],
        market_data: MarketData,
        threshold: float
    ) -> Optional[TradingDecision]:
        """Apply consensus mechanism to combine agent decisions."""
        if not decisions:
            return None
        
        # Count decisions by type
        decision_counts = {}
        for decision in decisions:
            dec_type = decision.decision_type
            if dec_type not in decision_counts:
                decision_counts[dec_type] = {
                    'count': 0,
                    'confidence_sum': 0.0,
                    'risk_sum': 0.0
                }
            
            decision_counts[dec_type]['count'] += 1
            decision_counts[dec_type]['confidence_sum'] += decision.confidence
            decision_counts[dec_type]['risk_sum'] += decision.risk_score
        
        # Find decision with highest support
        best_decision = None
        best_agreement = 0
        
        for dec_type, stats in decision_counts.items():
            agreement = stats['count'] / len(decisions)
            
            if agreement >= threshold and agreement > best_agreement:
                best_agreement = agreement
                avg_confidence = stats['confidence_sum'] / stats['count']
                avg_risk = stats['risk_sum'] / stats['count']
                
                best_decision = TradingDecision(
                    agent_id=self.coordinator_id,
                    decision_type=dec_type,
                    symbol=market_data.symbol,
                    quantity=1.0,
                    price=market_data.price,
                    confidence=avg_confidence,
                    timestamp=datetime.now(),
                    rationale=f"Consensus decision with {best_agreement:.1%} agreement",
                    risk_score=avg_risk
                )
        
        return best_decision
    
    def _log_coordination(
        self,
        decisions: List[TradingDecision],
        final_decision: TradingDecision
    ) -> None:
        """Log coordination details."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agents_reporting': len(decisions),
            'decisions': [d.to_dict() for d in decisions],
            'final_decision': final_decision.to_dict()
        }
        self.decision_log.append(log_entry)
        
        self.logger.info(
            f"Coordination complete: {len(decisions)} agents, "
            f"final decision: {final_decision.decision_type.value}"
        )
    
    def get_coordination_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent coordination history."""
        return self.decision_log[-limit:]
