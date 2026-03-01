#!/usr/bin/env python3
"""
Trading Components Tests
交易組件測試

Unit tests for trading system components and multi-agent trading.
交易系統組件和多智能體交易的單位測試。
"""

import unittest
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.plugins.multi_agent_trading import (
    BaseAgent, PortfolioManagementAgent, RiskManagementAgent,
    SignalAnalysisAgent, MultiAgentCoordinator, TradingDecision,
    DecisionType, AgentRole, PortfolioState, MarketData
)

class TestTradingDecision(unittest.TestCase):
    """Test trading decision data structure."""
    
    def test_decision_creation(self):
        """Test creating a trading decision."""
        decision = TradingDecision(
            agent_id='test_agent',
            decision_type=DecisionType.BUY,
            symbol='AAPL',
            quantity=10.0,
            price=150.75,
            confidence=0.85,
            timestamp=datetime.now(),
            rationale='Test buy signal',
            risk_score=0.2
        )
        
        self.assertEqual(decision.decision_type, DecisionType.BUY)
        self.assertEqual(decision.symbol, 'AAPL')
        self.assertGreater(decision.confidence, 0.8)
    
    def test_decision_serialization(self):
        """Test decision serialization to dict."""
        decision = TradingDecision(
            agent_id='test_agent',
            decision_type=DecisionType.SELL,
            symbol='MSFT',
            quantity=5.0,
            price=300.00,
            confidence=0.75,
            timestamp=datetime.now(),
            rationale='Risk management',
            risk_score=0.3
        )
        
        decision_dict = decision.to_dict()
        
        self.assertEqual(decision_dict['symbol'], 'MSFT')
        self.assertEqual(decision_dict['decision_type'], 'sell')
        self.assertIn('timestamp', decision_dict)

class TestPortfolioState(unittest.TestCase):
    """Test portfolio state tracking."""
    
    def test_portfolio_creation(self):
        """Test creating portfolio state."""
        portfolio = PortfolioState(
            positions={'AAPL': 100, 'MSFT': 50},
            cash=50000.0,
            total_value=250000.0,
            unrealized_pnl=5000.0,
            realized_pnl=1000.0
        )
        
        self.assertEqual(len(portfolio.positions), 2)
        self.assertEqual(portfolio.cash, 50000.0)
        self.assertGreater(portfolio.total_value, 0)
    
    def test_portfolio_serialization(self):
        """Test portfolio state serialization."""
        portfolio = PortfolioState(
            positions={'AAPL': 100},
            cash=100000.0,
            total_value=200000.0
        )
        
        portfolio_dict = portfolio.to_dict()
        
        self.assertIn('positions', portfolio_dict)
        self.assertIn('cash', portfolio_dict)
        self.assertIn('timestamp', portfolio_dict)

class TestMarketData(unittest.TestCase):
    """Test market data structure."""
    
    def test_market_data_creation(self):
        """Test creating market data."""
        market_data = MarketData(
            symbol='AAPL',
            price=150.75,
            volume=1000000,
            bid=150.70,
            ask=150.80,
            timestamp=datetime.now(),
            indicators={'sma_short': 150.5, 'rsi': 0.65}
        )
        
        self.assertEqual(market_data.symbol, 'AAPL')
        self.assertGreater(market_data.ask, market_data.bid)
        self.assertIn('sma_short', market_data.indicators)

class TestPortfolioManagementAgent(unittest.TestCase):
    """Test portfolio management agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = PortfolioManagementAgent(
            agent_id='pm_test',
            target_allocations={'AAPL': 0.5, 'MSFT': 0.3, 'GOOGL': 0.2},
            rebalance_threshold=0.05
        )
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_id, 'pm_test')
        self.assertEqual(self.agent.role, AgentRole.PORTFOLIO_MANAGER)
        self.assertGreater(self.agent.confidence_threshold, 0)
    
    def test_agent_can_analyze(self):
        """Test agent analysis capability."""
        portfolio = PortfolioState(
            positions={'AAPL': 100, 'MSFT': 50},
            cash=50000.0,
            total_value=250000.0
        )
        
        market_data = MarketData(
            symbol='AAPL',
            price=150.0,
            volume=1000000,
            bid=149.9,
            ask=150.1,
            timestamp=datetime.now()
        )
        
        # Should not raise exception
        decision = self.agent.analyze(market_data, portfolio)
        # Decision may be None or a TradingDecision

class TestRiskManagementAgent(unittest.TestCase):
    """Test risk management agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = RiskManagementAgent(
            agent_id='rm_test',
            max_position_size=0.1,
            max_portfolio_loss=0.02
        )
    
    def test_risk_agent_initialization(self):
        """Test risk agent initialization."""
        self.assertEqual(self.agent.agent_id, 'rm_test')
        self.assertEqual(self.agent.role, AgentRole.RISK_MANAGER)
    
    def test_position_size_validation(self):
        """Test position size validation."""
        portfolio = PortfolioState(
            positions={'AAPL': 1000},
            cash=50000.0,
            total_value=250000.0
        )
        
        market_data = MarketData(
            symbol='AAPL',
            price=150.0,
            volume=1000000,
            bid=149.9,
            ask=150.1,
            timestamp=datetime.now()
        )
        
        # Should analyze without error
        decision = self.agent.analyze(market_data, portfolio)

class TestSignalAnalysisAgent(unittest.TestCase):
    """Test signal analysis agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = SignalAnalysisAgent(
            agent_id='sa_test',
            sma_short=20,
            sma_long=50,
            rsi_threshold=0.3
        )
    
    def test_signal_agent_initialization(self):
        """Test signal agent initialization."""
        self.assertEqual(self.agent.agent_id, 'sa_test')
        self.assertEqual(self.agent.role, AgentRole.SIGNAL_ANALYST)
    
    def test_sma_signal_detection(self):
        """Test SMA signal detection."""
        portfolio = PortfolioState(total_value=100000.0)
        
        market_data = MarketData(
            symbol='AAPL',
            price=150.75,
            volume=1000000,
            bid=150.70,
            ask=150.80,
            timestamp=datetime.now(),
            indicators={'sma_short': 151.0, 'sma_long': 148.0}
        )
        
        decision = self.agent.analyze(market_data, portfolio)
        
        if decision:
            self.assertIsNotNone(decision.rationale)
    
    def test_rsi_signal_detection(self):
        """Test RSI signal detection."""
        portfolio = PortfolioState(total_value=100000.0)
        
        # Test oversold signal
        market_data = MarketData(
            symbol='AAPL',
            price=150.75,
            volume=1000000,
            bid=150.70,
            ask=150.80,
            timestamp=datetime.now(),
            indicators={'rsi': 0.25}
        )
        
        decision = self.agent.analyze(market_data, portfolio)

class TestMultiAgentCoordinator(unittest.TestCase):
    """Test multi-agent coordinator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.coordinator = MultiAgentCoordinator(coordinator_id='coord_test')
        
        # Register agents
        self.pm_agent = PortfolioManagementAgent(agent_id='pm_1')
        self.rm_agent = RiskManagementAgent(agent_id='rm_1')
        self.sa_agent = SignalAnalysisAgent(agent_id='sa_1')
        
        self.coordinator.register_agent(self.pm_agent)
        self.coordinator.register_agent(self.rm_agent)
        self.coordinator.register_agent(self.sa_agent)
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        self.assertEqual(self.coordinator.coordinator_id, 'coord_test')
        self.assertEqual(len(self.coordinator.agents), 3)
    
    def test_agent_registration(self):
        """Test agent registration."""
        new_agent = SignalAnalysisAgent(agent_id='sa_2')
        self.coordinator.register_agent(new_agent)
        
        self.assertEqual(len(self.coordinator.agents), 4)
        self.assertIn('sa_2', self.coordinator.agents)
    
    def test_agent_unregistration(self):
        """Test agent unregistration."""
        self.coordinator.unregister_agent('sa_1')
        
        self.assertEqual(len(self.coordinator.agents), 2)
        self.assertNotIn('sa_1', self.coordinator.agents)
    
    def test_coordination(self):
        """Test decision coordination."""
        portfolio = PortfolioState(total_value=250000.0)
        
        market_data = MarketData(
            symbol='AAPL',
            price=150.75,
            volume=1000000,
            bid=150.70,
            ask=150.80,
            timestamp=datetime.now(),
            indicators={'sma_short': 151.0, 'sma_long': 148.0, 'rsi': 0.65}
        )
        
        final_decision = self.coordinator.coordinate_decisions(
            market_data=market_data,
            portfolio=portfolio,
            voting_threshold=0.5
        )
        
        # Decision may be None or a TradingDecision

class TestDecisionHistory(unittest.TestCase):
    """Test decision history tracking."""
    
    def test_decision_recording(self):
        """Test recording decisions in history."""
        agent = PortfolioManagementAgent(agent_id='test_pm')
        
        self.assertEqual(len(agent.get_decision_history()), 0)
        
        decision = TradingDecision(
            agent_id='test_pm',
            decision_type=DecisionType.BUY,
            symbol='AAPL',
            quantity=10.0,
            price=150.75,
            confidence=0.85,
            timestamp=datetime.now(),
            rationale='Test'
        )
        
        agent.record_decision(decision)
        
        self.assertEqual(len(agent.get_decision_history()), 1)
    
    def test_decision_history_limit(self):
        """Test decision history limit."""
        agent = PortfolioManagementAgent(agent_id='test_pm')
        
        # Record 150 decisions
        for i in range(150):
            decision = TradingDecision(
                agent_id='test_pm',
                decision_type=DecisionType.BUY,
                symbol='AAPL',
                quantity=1.0,
                price=150.0,
                confidence=0.8,
                timestamp=datetime.now(),
                rationale=f'Test {i}'
            )
            agent.record_decision(decision)
        
        # Get last 100
        history = agent.get_decision_history(limit=100)
        self.assertEqual(len(history), 100)

if __name__ == '__main__':
    unittest.main()
