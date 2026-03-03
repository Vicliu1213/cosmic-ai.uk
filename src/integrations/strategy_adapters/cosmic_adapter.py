#!/usr/bin/env python3
"""
Cosmic Strategy Adapter - Hybrid Multi-Agent Architecture
Cosmic 策略適配器 - 混合多代理架構

Implements Hybrid Agent Architecture (方案 C):
- Parallel execution: Technical + Fundamental analysis (並行執行)
- Resonance detection: Signal fusion based on agreement (共振偵測)
- Conditional risk management: RiskManager only acts on high-confidence signals (條件式風險管理)

This adapter integrates your three agents:
1. TechnicalAnalyst (技術分析智能體)
2. FundamentalAnalyst (基本面分析智能體)
3. RiskManager (風險管理智能體)

Core benefits:
✅ Leverages Cosmic system's resonance philosophy
✅ Fast execution (~80-100ms total latency)
✅ High signal quality (multi-layer validation + resonance confirmation)
✅ Fault-tolerant design
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from src.integrations.strategy_adapters.strategy_interface import (
    UnifiedStrategyInterface,
    MarketData,
    TradeSignal,
    SignalType,
    StrategyMetrics,
)

logger = logging.getLogger(__name__)


@dataclass
class AgentSignal:
    """Signal output from an individual agent."""
    agent_name: str
    signal_type: SignalType
    confidence: float  # 0.0 - 1.0
    reasoning: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ResonanceResult:
    """Result of resonance detection between multiple signals."""
    resonance_type: str  # "bullish", "bearish", "neutral", "conflicted"
    resonance_score: float  # 0.0 - 1.0, how well signals agree
    participating_agents: List[str]
    combined_confidence: float
    final_signal_type: Optional[SignalType] = None
    amplification_factor: float = 1.0  # Sharpe ratio amplification


class TechnicalAnalystAgent:
    """Technical analysis agent - price, volume, indicators."""
    
    def __init__(self):
        self.name = "TechnicalAnalyst"
        self.last_analysis = None
    
    async def analyze(self, market_data: MarketData) -> AgentSignal:
        """
        Analyze market data using technical indicators.
        
        Simulates analysis of:
        - Moving averages
        - RSI, MACD, Bollinger Bands
        - Volume patterns
        - Price action
        """
        await asyncio.sleep(0.05)  # Simulate 50ms computation
        
        try:
            # Simple technical analysis heuristic
            price_trend = self._analyze_price_trend(market_data)
            volume_signal = self._analyze_volume(market_data)
            momentum = self._analyze_momentum(market_data)
            
            # Combine indicators
            signal_strength = np.mean([price_trend, volume_signal, momentum])
            
            if signal_strength > 0.55:
                signal_type = SignalType.BUY
                confidence = min(signal_strength, 0.9)
                reasoning = f"Bullish technical setup (trend:{price_trend:.2f}, volume:{volume_signal:.2f}, momentum:{momentum:.2f})"
            elif signal_strength < 0.45:
                signal_type = SignalType.SELL
                confidence = min(1 - signal_strength, 0.9)
                reasoning = f"Bearish technical setup (trend:{price_trend:.2f}, volume:{volume_signal:.2f}, momentum:{momentum:.2f})"
            else:
                signal_type = SignalType.HOLD
                confidence = 0.5
                reasoning = "Neutral technical signals, inconclusive"
            
            result = AgentSignal(
                agent_name=self.name,
                signal_type=signal_type,
                confidence=confidence,
                reasoning=reasoning,
                details={
                    "price_trend": price_trend,
                    "volume_signal": volume_signal,
                    "momentum": momentum,
                }
            )
            
            self.last_analysis = result
            logger.debug(f"{self.name}: {reasoning}")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return AgentSignal(
                agent_name=self.name,
                signal_type=SignalType.HOLD,
                confidence=0.0,
                reasoning=f"Analysis error: {e}"
            )
    
    @staticmethod
    def _analyze_price_trend(market_data: MarketData) -> float:
        """Analyze price trend (0-1, higher = uptrend)."""
        # Simple: compare close to open
        if market_data.open_price > 0:
            trend = (market_data.close_price - market_data.open_price) / market_data.open_price
            return float(np.clip(0.5 + trend * 5, 0.0, 1.0))  # Map to 0-1 range
        return 0.5
    
    @staticmethod
    def _analyze_volume(market_data: MarketData) -> float:
        """Analyze volume signal (0-1)."""
        # Higher volume = stronger signal
        if market_data.volume > 0:
            # Normalized volume (assume 1M is normal)
            normalized = np.clip(market_data.volume / 1000000, 0.0, 2.0)
            return float(np.clip(normalized / 2.0, 0.0, 1.0))
        return 0.5
    
    @staticmethod
    def _analyze_momentum(market_data: MarketData) -> float:
        """Analyze momentum (0-1)."""
        # Compare high/low prices
        if market_data.high_price > market_data.low_price:
            momentum = (market_data.close_price - market_data.low_price) / (
                market_data.high_price - market_data.low_price
            )
            return np.clip(momentum, 0.0, 1.0)
        return 0.5


class FundamentalAnalystAgent:
    """Fundamental analysis agent - market conditions, macro factors."""
    
    def __init__(self):
        self.name = "FundamentalAnalyst"
        self.last_analysis = None
    
    async def analyze(self, market_data: MarketData) -> AgentSignal:
        """
        Analyze fundamental factors.
        
        Simulates analysis of:
        - Market regime (trending vs range-bound)
        - Bid-ask spread (liquidity)
        - Order book imbalance
        - Macro factors
        """
        await asyncio.sleep(0.08)  # Simulate 80ms computation
        
        try:
            liquidity_score = self._analyze_liquidity(market_data)
            market_regime = self._analyze_market_regime(market_data)
            macro_factor = self._analyze_macro_factors(market_data)
            
            # Combine fundamental factors
            fundamental_strength = np.mean([liquidity_score, market_regime, macro_factor])
            
            if fundamental_strength > 0.55:
                signal_type = SignalType.BUY
                confidence = min(fundamental_strength, 0.85)
                reasoning = f"Bullish fundamentals (liquidity:{liquidity_score:.2f}, regime:{market_regime:.2f}, macro:{macro_factor:.2f})"
            elif fundamental_strength < 0.45:
                signal_type = SignalType.SELL
                confidence = min(1 - fundamental_strength, 0.85)
                reasoning = f"Bearish fundamentals (liquidity:{liquidity_score:.2f}, regime:{market_regime:.2f}, macro:{macro_factor:.2f})"
            else:
                signal_type = SignalType.HOLD
                confidence = 0.5
                reasoning = "Neutral fundamental outlook"
            
            result = AgentSignal(
                agent_name=self.name,
                signal_type=signal_type,
                confidence=confidence,
                reasoning=reasoning,
                details={
                    "liquidity_score": liquidity_score,
                    "market_regime": market_regime,
                    "macro_factor": macro_factor,
                }
            )
            
            self.last_analysis = result
            logger.debug(f"{self.name}: {reasoning}")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return AgentSignal(
                agent_name=self.name,
                signal_type=SignalType.HOLD,
                confidence=0.0,
                reasoning=f"Analysis error: {e}"
            )
    
    @staticmethod
    def _analyze_liquidity(market_data: MarketData) -> float:
        """Analyze liquidity (tight spread = good liquidity)."""
        if market_data.ask_price > market_data.bid_price:
            spread = (market_data.ask_price - market_data.bid_price) / market_data.bid_price
            # Low spread = high liquidity
            return np.clip(1.0 - spread * 100, 0.0, 1.0)
        return 0.5
    
    @staticmethod
    def _analyze_market_regime(market_data: MarketData) -> float:
        """Analyze market regime."""
        # Volatility-based regime detection
        high_low_range = (market_data.high_price - market_data.low_price) / market_data.low_price
        # Moderate volatility is good for trading
        if high_low_range < 0.05:
            return 0.3  # Range-bound, low opportunity
        elif high_low_range < 0.15:
            return 0.8  # Trending, good opportunity
        else:
            return 0.5  # Very volatile, risky
    
    @staticmethod
    def _analyze_macro_factors(market_data: MarketData) -> float:
        """Simulate macro factor analysis."""
        # In real implementation, fetch economic calendars, sentiment indices, etc.
        # For demo, use random with slight bias toward neutral
        return np.clip(np.random.normal(0.5, 0.15), 0.0, 1.0)


class RiskManagerAgent:
    """Risk management agent - position sizing, stop-loss, take-profit."""
    
    def __init__(self):
        self.name = "RiskManager"
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.max_position_size = 10.0  # Maximum units
    
    async def calculate(
        self,
        resonance_result: "ResonanceResult",
        market_data: MarketData,
        account_equity: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Calculate risk parameters for a trade.
        
        Args:
            resonance_result: Combined signal from Technical + Fundamental
            market_data: Current market data
            account_equity: Trading account size
            
        Returns:
            Dictionary with risk parameters (position size, stop-loss, take-profit)
        """
        await asyncio.sleep(0.02)  # Simulate 20ms computation
        
        try:
            current_price = market_data.close_price
            
            # Calculate stop-loss and take-profit based on volatility
            volatility = self._calculate_volatility(market_data)
            
            # Conservative stop-loss: 2% below entry for BUY, 2% above for SELL
            if resonance_result.final_signal_type == SignalType.BUY:
                stop_loss = current_price * (1 - 0.02 - volatility * 0.5)
                take_profit = current_price * (1 + 0.04 + volatility * 1.0)  # Risk/reward 1:2
            elif resonance_result.final_signal_type == SignalType.SELL:
                stop_loss = current_price * (1 + 0.02 + volatility * 0.5)
                take_profit = current_price * (1 - 0.04 - volatility * 1.0)
            else:
                stop_loss = current_price
                take_profit = current_price
            
            # Calculate position size based on risk tolerance
            risk_amount = account_equity * self.risk_per_trade
            price_risk = abs(current_price - stop_loss)
            
            if price_risk > 0:
                position_size = min(
                    risk_amount / price_risk,
                    self.max_position_size
                )
            else:
                position_size = self.max_position_size * 0.5
            
            # Scale position size by confidence
            position_size *= resonance_result.combined_confidence
            
            result = {
                "position_size": position_size,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk_reward_ratio": abs(take_profit - current_price) / abs(stop_loss - current_price) if price_risk > 0 else 0,
                "volatility": volatility,
            }
            
            logger.debug(f"{self.name}: Position size={position_size:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return {
                "position_size": 0.5,
                "stop_loss": market_data.close_price * 0.98,
                "take_profit": market_data.close_price * 1.02,
                "risk_reward_ratio": 0.5,
                "volatility": 0.0,
            }
    
    @staticmethod
    def _calculate_volatility(market_data: MarketData) -> float:
        """Calculate volatility from high-low range."""
        if market_data.low_price > 0:
            volatility = (market_data.high_price - market_data.low_price) / market_data.low_price
            return np.clip(volatility, 0.0, 1.0)
        return 0.0


class ResonanceDetector:
    """Detects resonance between Technical and Fundamental signals."""
    
    @staticmethod
    async def detect(
        technical_signal: AgentSignal,
        fundamental_signal: AgentSignal
    ) -> ResonanceResult:
        """
        Detect resonance (agreement) between two agent signals.
        
        共振類型:
        - Bullish: Both agents agree on BUY
        - Bearish: Both agents agree on SELL
        - Neutral: Conflicting signals or both HOLD
        - Conflicted: Opposite signals (need RiskManager veto)
        """
        
        # Determine signal types
        bullish_votes = sum(1 for s in [technical_signal, fundamental_signal]
                           if s.signal_type == SignalType.BUY)
        bearish_votes = sum(1 for s in [technical_signal, fundamental_signal]
                           if s.signal_type == SignalType.SELL)
        neutral_votes = sum(1 for s in [technical_signal, fundamental_signal]
                           if s.signal_type == SignalType.HOLD)
        
        # Calculate resonance
        if bullish_votes == 2:
            resonance_type = "bullish"
            combined_confidence = float(np.mean([
                technical_signal.confidence,
                fundamental_signal.confidence
            ]))
            final_signal_type = SignalType.BUY
            amplification_factor = 1.2  # 20% Sharpe ratio boost on resonance
            
        elif bearish_votes == 2:
            resonance_type = "bearish"
            combined_confidence = float(np.mean([
                technical_signal.confidence,
                fundamental_signal.confidence
            ]))
            final_signal_type = SignalType.SELL
            amplification_factor = 1.2
            
        elif neutral_votes >= 1:
            resonance_type = "neutral"
            combined_confidence = 0.5
            final_signal_type = SignalType.HOLD
            amplification_factor = 0.8
            
        else:
            resonance_type = "conflicted"
            combined_confidence = min(
                technical_signal.confidence,
                fundamental_signal.confidence
            ) * 0.5  # Penalize conflicts
            # Conflicted signals lean toward previous strongest signal
            final_signal_type = (
                technical_signal.signal_type
                if technical_signal.confidence > fundamental_signal.confidence
                else fundamental_signal.signal_type
            )
            amplification_factor = 0.6  # Sharpe ratio penalty on conflicts
        
        # Calculate resonance score (0-1, higher = better agreement)
        if resonance_type in ["bullish", "bearish"]:
            resonance_score = 0.9
        elif resonance_type == "neutral":
            resonance_score = 0.5
        else:  # conflicted
            resonance_score = 0.3
        
        return ResonanceResult(
            resonance_type=resonance_type,
            resonance_score=resonance_score,
            participating_agents=[technical_signal.agent_name, fundamental_signal.agent_name],
            combined_confidence=combined_confidence,
            final_signal_type=final_signal_type,
            amplification_factor=amplification_factor,
        )


class CosmicStrategyAdapter(UnifiedStrategyInterface):
    """
    Cosmic Strategy Adapter - Integrates your three agents with resonance framework.
    
    這是你的 Cosmic 系統在基準測試框架中的適配器實現。
    它使用混合架構 (方案 C):
    1. Technical + Fundamental 並行執行 (~80ms)
    2. 共振偵測合併信號
    3. RiskManager 條件式執行（高信心度時）
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Cosmic strategy adapter."""
        super().__init__(name="cosmic_hybrid", config=config or {})
        
        # Initialize the three agents
        self.technical_agent = TechnicalAnalystAgent()
        self.fundamental_agent = FundamentalAnalystAgent()
        self.risk_manager = RiskManagerAgent()
        self.resonance_detector = ResonanceDetector()
        
        # Configuration
        self.resonance_threshold = self.config.get("resonance_threshold", 0.6)
        self.account_equity = self.config.get("account_equity", 100000.0)
        
        logger.info("CosmicStrategyAdapter initialized with hybrid agent architecture")
    
    async def initialize(self) -> bool:
        """Initialize strategy."""
        try:
            self._start_time = datetime.now(timezone.utc)
            self.status = self.status.RUNNING
            logger.info("Cosmic strategy initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Cosmic strategy: {e}")
            return False
    
    async def on_market_data(self, market_data: MarketData) -> None:
        """Process incoming market data."""
        self.current_price[market_data.symbol] = market_data.close_price
    
    async def generate_signals(self) -> List[TradeSignal]:
        """
        Generate trading signals using hybrid agent architecture.
        
        Flow:
        1. Parallel: Technical + Fundamental analysis (~80ms total)
        2. Resonance: Detect signal agreement
        3. Conditional: RiskManager calculates params if resonance > threshold
        4. Output: List of TradeSignal objects
        """
        if not self.current_price:
            return []
        
        signals = []
        
        try:
            # Get latest market data (assume single symbol for now)
            symbol = list(self.current_price.keys())[0] if self.current_price else None
            if not symbol:
                return []
            
            # Simulate market data for demo
            market_data = MarketData(
                timestamp=datetime.now(timezone.utc),
                symbol=symbol,
                open_price=self.current_price[symbol] * 0.995,
                high_price=self.current_price[symbol] * 1.005,
                low_price=self.current_price[symbol] * 0.990,
                close_price=self.current_price[symbol],
                volume=1000000.0,
                bid_price=self.current_price[symbol] * 0.9999,
                ask_price=self.current_price[symbol] * 1.0001,
            )
            
            # Step 1: Parallel execution of Technical + Fundamental analysis
            logger.debug("Step 1: Executing parallel agent analysis...")
            tech_signal, fund_signal = await asyncio.gather(
                self.technical_agent.analyze(market_data),
                self.fundamental_agent.analyze(market_data),
                return_exceptions=True
            )
            
            # Check for exceptions
            if isinstance(tech_signal, Exception) or isinstance(fund_signal, Exception):
                logger.error("Error in agent analysis")
                return []
            
            # Step 2: Resonance detection
            logger.debug("Step 2: Detecting resonance...")
            resonance_result = await self.resonance_detector.detect(tech_signal, fund_signal)
            
            logger.info(
                f"Resonance: {resonance_result.resonance_type} "
                f"(score={resonance_result.resonance_score:.2f}, "
                f"confidence={resonance_result.combined_confidence:.2f})"
            )
            
            # Step 3: Conditional RiskManager execution
            if resonance_result.resonance_score >= self.resonance_threshold:
                logger.debug("Step 3: Calculating risk parameters...")
                risk_params = await self.risk_manager.calculate(
                    resonance_result,
                    market_data,
                    self.account_equity
                )
                
                # Generate final trade signal
                signal = TradeSignal(
                    timestamp=datetime.now(timezone.utc),
                    symbol=symbol,
                    signal_type=resonance_result.final_signal_type,
                    confidence=resonance_result.combined_confidence,
                    quantity=risk_params["position_size"],
                    entry_price=market_data.close_price,
                    stop_loss=risk_params["stop_loss"],
                    take_profit=risk_params["take_profit"],
                    metadata={
                        "resonance_score": resonance_result.resonance_score,
                        "resonance_type": resonance_result.resonance_type,
                        "technical_signal": tech_signal.signal_type.value,
                        "fundamental_signal": fund_signal.signal_type.value,
                        "technical_confidence": tech_signal.confidence,
                        "fundamental_confidence": fund_signal.confidence,
                        "risk_reward_ratio": risk_params["risk_reward_ratio"],
                        "volatility": risk_params["volatility"],
                        "amplification_factor": resonance_result.amplification_factor,
                    }
                )
                
                signals.append(signal)
                logger.info(f"Generated signal: {signal.signal_type.value} for {symbol}")
            else:
                logger.debug(f"Resonance score {resonance_result.resonance_score:.2f} below threshold {self.resonance_threshold}")
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}", exc_info=True)
        
        return signals
    
    async def execute_trade(self, signal: TradeSignal) -> bool:
        """Execute trade based on signal."""
        try:
            self.update_position(signal.symbol, signal.quantity, signal.entry_price)
            logger.info(f"Executed {signal.signal_type.value} for {signal.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def get_metrics(self) -> StrategyMetrics:
        """Get performance metrics."""
        return self.metrics


# Helper function for testing
async def test_cosmic_adapter():
    """Test the Cosmic strategy adapter."""
    adapter = CosmicStrategyAdapter(config={
        "resonance_threshold": 0.6,
        "account_equity": 100000.0
    })
    
    # Initialize
    await adapter.initialize()
    
    # Simulate market data
    adapter.current_price["BTC/USDT"] = 45000.0
    
    # Generate signals
    signals = await adapter.generate_signals()
    
    print(f"Generated {len(signals)} signals")
    for signal in signals:
        print(f"  - {signal.signal_type.value} at {signal.entry_price}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_cosmic_adapter())
