#!/usr/bin/env python3
"""
Multi-Agent Trading System - LogManager Integration Examples
多智能體交易系統 - LogManager 整合示例

This file provides detailed examples of how to integrate the LogManager
logging system with the multi-agent trading system.
這個文件提供了如何將 LogManager 日誌系統與多智能體交易系統整合的詳細示例。

Key Integration Points:
1. Agent initialization with logging
2. Decision tracking and logging
3. Event logging for trading operations
4. Error handling and logging
5. Performance metrics logging
6. Portfolio state changes logging
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.core.logging_integration import LogManager, LogConfig
from src.plugins.multi_agent_trading import (
    BaseAgent, PortfolioManagementAgent, RiskManagementAgent,
    SignalAnalysisAgent, MultiAgentCoordinator,
    TradingDecision, PortfolioState, MarketData, DecisionType, AgentRole
)


# ============================================================================
# EXAMPLE 1: Initialize LogManager for Multi-Agent Trading System
# ============================================================================

def setup_trading_logging() -> LogManager:
    """
    Setup LogManager for the multi-agent trading system.
    為多智能體交易系統設置 LogManager。
    
    This should be called once at system startup to initialize all logging.
    這應該在系統啟動時調用一次以初始化所有日誌。
    
    Returns:
        LogManager: Configured logger instance for trading
    """
    # Create configuration for trading system
    config = LogConfig(
        log_dir="logs",
        log_level=logging.INFO,
        max_bytes=10485760,  # 10 MB
        backup_count=5,
        format_type="detailed"  # Detailed format for trading events
    )
    
    # Initialize LogManager
    log_manager = LogManager(config)
    
    # Create dedicated loggers for different trading components
    log_manager.create_logger(
        name="trading.agents",
        level=logging.INFO,
        filename="logs/trading_agents.log"
    )
    log_manager.create_logger(
        name="trading.decisions",
        level=logging.INFO,
        filename="logs/trading_decisions.log"
    )
    log_manager.create_logger(
        name="trading.portfolio",
        level=logging.INFO,
        filename="logs/trading_portfolio.log"
    )
    log_manager.create_logger(
        name="trading.risk",
        level=logging.WARNING,
        filename="logs/trading_risk.log"
    )
    
    return log_manager


# ============================================================================
# EXAMPLE 2: Enhanced Agent with LogManager Integration
# ============================================================================

class LoggingBaseAgent(BaseAgent):
    """
    Extended BaseAgent with integrated LogManager.
    具有集成 LogManager 的擴展 BaseAgent。
    
    This shows how to enhance the BaseAgent class to use the centralized
    logging system.
    這展示了如何增強 BaseAgent 類以使用集中式日誌系統。
    """
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        log_manager: LogManager,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize agent with LogManager.
        
        Args:
            agent_id: Unique agent identifier
            role: Agent role
            log_manager: LogManager instance for centralized logging
            confidence_threshold: Minimum confidence for decisions
        """
        super().__init__(agent_id, role, confidence_threshold)
        self.log_manager = log_manager
        self.trading_logger = log_manager.get_logger("trading.agents")
        self.decision_logger = log_manager.get_logger("trading.decisions")
        
        # Log agent initialization
        self.trading_logger.info(
            f"[AGENT_INIT] Agent initialized: {agent_id} | "
            f"Role: {role.value} | "
            f"Confidence threshold: {confidence_threshold}"
        )
    
    def record_decision(self, decision: TradingDecision) -> None:
        """
        Record decision with enhanced logging.
        
        Args:
            decision: The trading decision to record
        """
        super().record_decision(decision)
        
        # Enhanced logging with decision details
        self.decision_logger.info(
            f"[DECISION_RECORDED] Agent: {decision.agent_id} | "
            f"Type: {decision.decision_type.value} | "
            f"Symbol: {decision.symbol} | "
            f"Quantity: {decision.quantity:.2f} | "
            f"Confidence: {decision.confidence:.2%} | "
            f"Risk: {decision.risk_score:.2%} | "
            f"Rationale: {decision.rationale}"
        )
    
    def log_analysis_started(self, symbol: str) -> None:
        """Log when agent starts analyzing."""
        self.trading_logger.debug(
            f"[ANALYSIS_START] Agent {self.agent_id} analyzing {symbol}"
        )
    
    def log_analysis_completed(self, symbol: str, decision: Optional[TradingDecision]) -> None:
        """Log when agent completes analysis."""
        if decision:
            self.trading_logger.info(
                f"[ANALYSIS_COMPLETE] Agent {self.agent_id} | "
                f"Symbol: {symbol} | Decision: {decision.decision_type.value}"
            )
        else:
            self.trading_logger.debug(
                f"[ANALYSIS_COMPLETE] Agent {self.agent_id} | "
                f"Symbol: {symbol} | No decision"
            )
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log analysis errors with context."""
        self.trading_logger.error(
            f"[AGENT_ERROR] Agent {self.agent_id} | "
            f"Context: {context} | "
            f"Error: {str(error)}",
            exc_info=True
        )


# ============================================================================
# EXAMPLE 3: Enhanced Signal Analysis Agent with Detailed Logging
# ============================================================================

class LoggingSignalAnalysisAgent(LoggingBaseAgent):
    """
    SignalAnalysisAgent with comprehensive event logging.
    具有全面事件日誌的信號分析智能體。
    
    Shows how to integrate logging throughout the analysis process.
    """
    
    def __init__(
        self,
        agent_id: str,
        log_manager: LogManager,
        sma_short: int = 20,
        sma_long: int = 50,
        rsi_threshold: float = 0.3
    ):
        """Initialize with logging."""
        super().__init__(agent_id, AgentRole.SIGNAL_ANALYST, log_manager)
        self.sma_short = sma_short
        self.sma_long = sma_long
        self.rsi_threshold = rsi_threshold
    
    def analyze(self, market_data: MarketData, portfolio: PortfolioState) -> Optional[TradingDecision]:
        """
        Analyze with event logging.
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            
        Returns:
            Trading decision or None
        """
        self.log_analysis_started(market_data.symbol)
        
        try:
            if not market_data.indicators:
                self.trading_logger.debug(
                    f"[NO_INDICATORS] {market_data.symbol}: No indicators available"
                )
                return None
            
            # Check SMA crossover with detailed logging
            sma_signal = self._check_sma_crossover_with_logging(market_data)
            if sma_signal:
                self.record_decision(sma_signal)
                self.log_analysis_completed(market_data.symbol, sma_signal)
                return sma_signal
            
            # Check RSI signal with detailed logging
            rsi_signal = self._check_rsi_signal_with_logging(market_data)
            if rsi_signal:
                self.record_decision(rsi_signal)
                self.log_analysis_completed(market_data.symbol, rsi_signal)
                return rsi_signal
            
            self.log_analysis_completed(market_data.symbol, None)
            
        except Exception as e:
            self.log_error(e, f"Signal analysis for {market_data.symbol}")
        
        return None
    
    def _check_sma_crossover_with_logging(self, market_data: MarketData) -> Optional[TradingDecision]:
        """Check SMA with detailed logging."""
        sma_short = market_data.indicators.get('sma_short', 0)
        sma_long = market_data.indicators.get('sma_long', 0)
        
        self.trading_logger.debug(
            f"[SMA_CHECK] {market_data.symbol} | "
            f"Short: {sma_short:.2f} | Long: {sma_long:.2f}"
        )
        
        if sma_short <= 0 or sma_long <= 0:
            self.trading_logger.debug(
                f"[SMA_INVALID] {market_data.symbol}: Invalid SMA values"
            )
            return None
        
        if sma_short > sma_long:  # Bullish
            decision = TradingDecision(
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
            self.trading_logger.info(
                f"[SMA_SIGNAL_BUY] {market_data.symbol}: Bullish crossover detected"
            )
            return decision
        
        elif sma_short < sma_long:  # Bearish
            decision = TradingDecision(
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
            self.trading_logger.info(
                f"[SMA_SIGNAL_SELL] {market_data.symbol}: Bearish crossover detected"
            )
            return decision
        
        return None
    
    def _check_rsi_signal_with_logging(self, market_data: MarketData) -> Optional[TradingDecision]:
        """Check RSI with detailed logging."""
        rsi = market_data.indicators.get('rsi', 0.5)
        
        self.trading_logger.debug(
            f"[RSI_CHECK] {market_data.symbol} | RSI: {rsi:.2f}"
        )
        
        if rsi < self.rsi_threshold:  # Oversold
            decision = TradingDecision(
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
            self.trading_logger.info(
                f"[RSI_SIGNAL_BUY] {market_data.symbol}: Oversold condition (RSI: {rsi:.2f})"
            )
            return decision
        
        elif rsi > (1.0 - self.rsi_threshold):  # Overbought
            decision = TradingDecision(
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
            self.trading_logger.info(
                f"[RSI_SIGNAL_SELL] {market_data.symbol}: Overbought condition (RSI: {rsi:.2f})"
            )
            return decision
        
        return None


# ============================================================================
# EXAMPLE 4: Enhanced Risk Management Agent with Logging
# ============================================================================

class LoggingRiskManagementAgent(LoggingBaseAgent):
    """
    RiskManagementAgent with comprehensive risk event logging.
    具有全面風險事件日誌的風險管理智能體。
    """
    
    def __init__(
        self,
        agent_id: str,
        log_manager: LogManager,
        max_position_size: float = 0.1,
        max_portfolio_loss: float = 0.02,
        var_threshold: float = 0.95
    ):
        """Initialize with logging."""
        super().__init__(agent_id, AgentRole.RISK_MANAGER, log_manager)
        self.max_position_size = max_position_size
        self.max_portfolio_loss = max_portfolio_loss
        self.var_threshold = var_threshold
        self.risk_logger = log_manager.get_logger("trading.risk")
    
    def analyze(self, market_data: MarketData, portfolio: PortfolioState) -> Optional[TradingDecision]:
        """Analyze with risk logging."""
        self.log_analysis_started(market_data.symbol)
        
        try:
            # Check position size limits
            position_value = portfolio.positions.get(market_data.symbol, 0) * market_data.price
            max_allowed = portfolio.total_value * self.max_position_size
            
            self.trading_logger.debug(
                f"[RISK_CHECK] {market_data.symbol} | "
                f"Position: ${position_value:.2f} | Max allowed: ${max_allowed:.2f}"
            )
            
            if position_value > max_allowed:
                decision = self._create_risk_reduction_decision_with_logging(
                    market_data, portfolio, position_value, max_allowed
                )
                if decision.confidence >= self.confidence_threshold:
                    self.record_decision(decision)
                    return decision
            
            # Check portfolio loss limit
            if portfolio.unrealized_pnl < -portfolio.total_value * self.max_portfolio_loss:
                decision = self._create_emergency_exit_decision_with_logging(
                    market_data, portfolio
                )
                if decision.confidence >= self.confidence_threshold:
                    self.record_decision(decision)
                    return decision
            
            self.log_analysis_completed(market_data.symbol, None)
            
        except Exception as e:
            self.log_error(e, f"Risk analysis for {market_data.symbol}")
        
        return None
    
    def _create_risk_reduction_decision_with_logging(
        self,
        market_data: MarketData,
        portfolio: PortfolioState,
        current_size: float,
        max_allowed: float
    ) -> TradingDecision:
        """Create risk reduction decision with logging."""
        excess = current_size - max_allowed
        quantity_to_sell = excess / market_data.price if market_data.price > 0 else 0
        
        self.risk_logger.warning(
            f"[RISK_LIMIT_EXCEEDED] {market_data.symbol} | "
            f"Current position: ${current_size:.2f} | "
            f"Max allowed: ${max_allowed:.2f} | "
            f"Excess: ${excess:.2f} | "
            f"Selling: {quantity_to_sell:.2f} units"
        )
        
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
    
    def _create_emergency_exit_decision_with_logging(
        self,
        market_data: MarketData,
        portfolio: PortfolioState
    ) -> TradingDecision:
        """Create emergency exit decision with critical logging."""
        loss_percent = (portfolio.unrealized_pnl / portfolio.total_value) * 100
        
        self.risk_logger.critical(
            f"[EMERGENCY_EXIT] Portfolio loss limit exceeded | "
            f"Loss: ${portfolio.unrealized_pnl:.2f} ({loss_percent:.2f}%) | "
            f"Limit: {self.max_portfolio_loss:.2%} | "
            f"Initiating emergency exit for {market_data.symbol}"
        )
        
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


# ============================================================================
# EXAMPLE 5: Enhanced Coordinator with Logging
# ============================================================================

class LoggingMultiAgentCoordinator(MultiAgentCoordinator):
    """
    MultiAgentCoordinator with comprehensive coordination logging.
    具有全面協調日誌的多智能體協調器。
    """
    
    def __init__(self, coordinator_id: str = "coordinator_1", log_manager: Optional[LogManager] = None):
        """Initialize with logging."""
        super().__init__(coordinator_id)
        self.log_manager = log_manager
        if log_manager:
            self.coordination_logger = log_manager.get_logger("trading.decisions")
        else:
            self.coordination_logger = logging.getLogger(f"{__name__}.{coordinator_id}")
    
    def coordinate_decisions(
        self,
        market_data: MarketData,
        portfolio: PortfolioState,
        voting_threshold: float = 0.5
    ) -> Optional[TradingDecision]:
        """Coordinate with detailed logging."""
        self.coordination_logger.info(
            f"[COORDINATION_START] Symbol: {market_data.symbol} | "
            f"Agents: {len(self.agents)} | "
            f"Portfolio value: ${portfolio.total_value:.2f}"
        )
        
        try:
            decisions = self._collect_decisions(market_data, portfolio)
            
            if not decisions:
                self.coordination_logger.debug(
                    f"[NO_DECISIONS] Symbol: {market_data.symbol}: No agent decisions"
                )
                return None
            
            self.coordination_logger.debug(
                f"[DECISIONS_COLLECTED] {len(decisions)} decision(s) from agents"
            )
            
            final_decision = self._apply_consensus(decisions, market_data, voting_threshold)
            
            if final_decision:
                self._log_coordination_with_details(decisions, final_decision)
            
            return final_decision
            
        except Exception as e:
            self.coordination_logger.error(
                f"[COORDINATION_ERROR] Symbol: {market_data.symbol} | Error: {str(e)}",
                exc_info=True
            )
            return None
    
    def _log_coordination_with_details(
        self,
        decisions: List[TradingDecision],
        final_decision: TradingDecision
    ) -> None:
        """Log coordination with detailed analysis."""
        # Count decisions by type
        decision_types = {}
        for decision in decisions:
            dec_type = decision.decision_type.value
            if dec_type not in decision_types:
                decision_types[dec_type] = 0
            decision_types[dec_type] += 1
        
        decision_summary = " | ".join(
            [f"{dec_type}: {count}" for dec_type, count in decision_types.items()]
        )
        
        self.coordination_logger.info(
            f"[COORDINATION_COMPLETE] Symbol: {final_decision.symbol} | "
            f"Final decision: {final_decision.decision_type.value} | "
            f"Confidence: {final_decision.confidence:.2%} | "
            f"Agent votes: {decision_summary} | "
            f"Risk score: {final_decision.risk_score:.2%}"
        )
        
        # Log individual agent decisions
        for decision in decisions:
            self.coordination_logger.debug(
                f"[AGENT_DECISION] {decision.agent_id}: "
                f"{decision.decision_type.value} | "
                f"Confidence: {decision.confidence:.2%} | "
                f"Rationale: {decision.rationale}"
            )


# ============================================================================
# EXAMPLE 6: Portfolio State Tracking with Logging
# ============================================================================

class PortfolioStateTracker:
    """
    Utility class to track and log portfolio state changes.
    用於跟蹤和記錄投資組合狀態變化的實用程序類。
    """
    
    def __init__(self, log_manager: LogManager):
        """Initialize tracker."""
        self.log_manager = log_manager
        self.portfolio_logger = log_manager.get_logger("trading.portfolio")
        self.previous_state: Optional[PortfolioState] = None
    
    def track_state_change(self, new_state: PortfolioState, trigger: str = "") -> None:
        """
        Track portfolio state changes with logging.
        
        Args:
            new_state: New portfolio state
            trigger: What triggered the change (e.g., "decision_execution")
        """
        if self.previous_state is None:
            # First state
            self.portfolio_logger.info(
                f"[PORTFOLIO_INIT] Total value: ${new_state.total_value:.2f} | "
                f"Cash: ${new_state.cash:.2f} | "
                f"Positions: {len(new_state.positions)}"
            )
        else:
            # Track changes
            value_change = new_state.total_value - self.previous_state.total_value
            pnl_change = new_state.unrealized_pnl - self.previous_state.unrealized_pnl
            
            self.portfolio_logger.info(
                f"[PORTFOLIO_UPDATE] Trigger: {trigger} | "
                f"Value: ${new_state.total_value:.2f} (change: ${value_change:+.2f}) | "
                f"P&L: ${new_state.unrealized_pnl:.2f} (change: ${pnl_change:+.2f}) | "
                f"Cash: ${new_state.cash:.2f}"
            )
            
            # Log significant changes
            if abs(value_change) > new_state.total_value * 0.05:  # 5% threshold
                self.portfolio_logger.warning(
                    f"[SIGNIFICANT_CHANGE] Value changed by {value_change/self.previous_state.total_value:+.2%}"
                )
        
        self.previous_state = new_state


# ============================================================================
# EXAMPLE 7: Complete Integration Usage
# ============================================================================

def example_complete_integration():
    """
    Complete example showing how to integrate logging throughout
    the multi-agent trading system.
    完整的示例展示如何在多智能體交易系統中整合日誌記錄。
    """
    # Step 1: Initialize LogManager
    log_manager = setup_trading_logging()
    trading_logger = log_manager.get_logger("trading.agents")
    
    trading_logger.info("=" * 80)
    trading_logger.info("Starting Multi-Agent Trading System with Logging Integration")
    trading_logger.info("=" * 80)
    
    # Step 2: Create agents with logging
    signal_agent = LoggingSignalAnalysisAgent(
        agent_id="signal_analyst_1",
        log_manager=log_manager,
        sma_short=20,
        sma_long=50
    )
    
    risk_agent = LoggingRiskManagementAgent(
        agent_id="risk_manager_1",
        log_manager=log_manager,
        max_position_size=0.1
    )
    
    # Step 3: Create coordinator with logging
    coordinator = LoggingMultiAgentCoordinator(
        coordinator_id="coordinator_1",
        log_manager=log_manager
    )
    
    coordinator.register_agent(signal_agent)
    coordinator.register_agent(risk_agent)
    
    trading_logger.info(f"Registered {len(coordinator.agents)} agents with coordinator")
    
    # Step 4: Create portfolio tracker
    portfolio_tracker = PortfolioStateTracker(log_manager)
    
    # Step 5: Simulate trading
    portfolio = PortfolioState(
        positions={"AAPL": 100, "GOOG": 50},
        cash=50000.0,
        total_value=100000.0,
        unrealized_pnl=5000.0
    )
    portfolio_tracker.track_state_change(portfolio, "initialization")
    
    # Step 6: Analyze market data
    market_data = MarketData(
        symbol="AAPL",
        price=150.0,
        volume=1000000.0,
        bid=149.95,
        ask=150.05,
        timestamp=datetime.now(),
        indicators={
            'sma_short': 151.0,
            'sma_long': 148.0,
            'rsi': 0.65
        }
    )
    
    trading_logger.info(f"Analyzing {market_data.symbol} at ${market_data.price}")
    
    # Step 7: Get coordinated decision
    final_decision = coordinator.coordinate_decisions(market_data, portfolio)
    
    if final_decision:
        trading_logger.info(
            f"Final decision: {final_decision.decision_type.value} "
            f"{final_decision.quantity} units of {final_decision.symbol}"
        )
    
    trading_logger.info("=" * 80)
    trading_logger.info("Trading cycle complete")
    trading_logger.info("=" * 80)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_trading_statistics(log_manager: LogManager) -> Dict[str, Any]:
    """
    Get trading statistics from logs.
    從日誌獲取交易統計數據。
    
    Args:
        log_manager: LogManager instance
        
    Returns:
        Dictionary with trading statistics
    """
    decision_logger = log_manager.get_logger("trading.decisions")
    
    return {
        'timestamp': datetime.now().isoformat(),
        'log_files': log_manager.get_log_files(),
        'current_level': decision_logger.level
    }


def create_trading_summary(log_manager: LogManager) -> str:
    """
    Create a summary of trading activity from logs.
    從日誌創建交易活動摘要。
    
    Args:
        log_manager: LogManager instance
        
    Returns:
        Summary string
    """
    summary = f"""
Multi-Agent Trading System - Logging Integration Summary
========================================================

Logging System Initialized:
- Log directory: {log_manager.log_dir}
- Log level: {log_manager.config.log_level}
- Max file size: {log_manager.config.max_bytes} bytes
- Backup files: {log_manager.config.backup_count}

Trading Loggers Created:
1. trading.agents - Agent initialization and analysis events
2. trading.decisions - Trading decisions and signals
3. trading.portfolio - Portfolio state changes
4. trading.risk - Risk warnings and alerts

Key Logging Points:
- Agent initialization and configuration
- Market analysis and signal detection
- Trading decisions with confidence and rationale
- Risk assessments and limit violations
- Portfolio state changes and P&L tracking
- Coordination and consensus building
- Errors and exceptions

Access Logs:
- View logs: python logging_dashboard.py
- View specific log: tail -f logs/trading_decisions.log
- Search logs: grep "[ERROR]" logs/*.log
"""
    return summary


if __name__ == "__main__":
    # Run example integration
    example_complete_integration()
    
    # Print summary
    log_manager = setup_trading_logging()
    print(create_trading_summary(log_manager))
