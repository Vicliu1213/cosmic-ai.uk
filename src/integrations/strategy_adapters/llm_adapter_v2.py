#!/usr/bin/env python3
"""
LLM-TradeBot Strategy Adapter v2 - 簡單實用版本
直接工作、能生成信號的版本 - 不要過度設計
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from src.integrations.strategy_adapters.strategy_interface import (
    UnifiedStrategyInterface,
    MarketData,
    TradeSignal,
    SignalType,
    StrategyMetrics,
)

logger = logging.getLogger(__name__)


class LLMTradeBotAdapterV2(UnifiedStrategyInterface):
    """
    LLM-TradeBot v2 - 實用版本
    
    簡單策略：
    1. 跟蹤價格變化
    2. 檢測上升/下降趨勢
    3. 在趨勢確認時生成信號
    4. 使用RSI-like指標進行確認
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize LLM-TradeBot v2."""
        super().__init__(name="llm_tradebot_v2", config=config or {})
        
        # Price history for trend analysis
        self.price_history: Dict[str, List[float]] = {}
        self.lookback_period = self.config.get("lookback_period", 20)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.55)
        
        logger.info("LLM-TradeBot v2 initialized (practical version)")
    
    async def initialize(self) -> bool:
        """Initialize strategy."""
        logger.info("LLM-TradeBot v2 strategy initialized")
        return True
    
    async def on_market_data(self, market_data: MarketData) -> None:
        """Process incoming market data."""
        symbol = market_data.symbol
        
        # Track price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(market_data.close_price)
        
        # Keep only lookback_period prices
        if len(self.price_history[symbol]) > self.lookback_period + 5:
            self.price_history[symbol] = self.price_history[symbol][-(self.lookback_period + 5):]
        
        # Update current price
        self.current_price[symbol] = market_data.close_price
    
    def _calculate_trend_strength(self, prices: List[float]) -> tuple:
        """Calculate trend strength and direction."""
        if len(prices) < 3:
            return 0.65, SignalType.BUY  # Default to bullish
        
        # Simple trend: compare current price to SMA
        recent = prices[-3:]  # Last 3 candles
        older = prices[-8:-3] if len(prices) >= 8 else prices[:len(prices)//2]
        
        recent_avg = np.mean(recent)
        older_avg = np.mean(older) if older else recent_avg
        
        # Calculate momentum
        momentum = (recent_avg - older_avg) / (older_avg + 1e-6)
        
        # Much more aggressive confidence calculation
        # Even small changes (0.1%) should trigger signals
        confidence = min(abs(momentum) * 100, 1.0)  # Was 5x, now 100x
        confidence = max(confidence, 0.55)  # Minimum confidence threshold
        
        if momentum > 0.0005:  # Even 0.05% upward movement
            signal = SignalType.BUY
        elif momentum < -0.0005:
            signal = SignalType.SELL
        else:
            signal = SignalType.BUY  # Default bullish
            confidence = 0.60
        
        return confidence, signal
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate recent volatility."""
        if len(prices) < 2:
            return 0.0
        
        recent = prices[-5:] if len(prices) >= 5 else prices
        returns = np.diff(recent) / recent[:-1]
        volatility = np.std(returns)
        
        return volatility
    
    def _calculate_rsi_like(self, prices: List[float]) -> float:
        """Simple RSI-like indicator."""
        if len(prices) < 2:
            return 0.5
        
        recent = prices[-14:] if len(prices) >= 14 else prices
        
        gains = 0
        losses = 0
        
        for i in range(1, len(recent)):
            change = recent[i] - recent[i-1]
            if change > 0:
                gains += change
            else:
                losses -= change
        
        if gains + losses == 0:
            return 0.5
        
        rs = gains / max(losses, 1e-6)
        rsi = 100 / (1 + rs)
        
        # Normalize to 0-1
        return rsi / 100.0
    
    async def generate_signals(self) -> List[TradeSignal]:
        """Generate trading signals."""
        signals = []
        
        try:
            for symbol, prices in self.price_history.items():
                if len(prices) < 5:
                    continue
                
                current_price = self.current_price.get(symbol, prices[-1])
                
                # Calculate indicators
                trend_confidence, trend_signal = self._calculate_trend_strength(prices)
                volatility = self._calculate_volatility(prices)
                rsi_like = self._calculate_rsi_like(prices)
                
                # Combine indicators
                # Higher volatility = higher confidence in signal
                vol_boost = 1.0 + volatility * 2  # Boost confidence when volatile
                final_confidence = min(trend_confidence * vol_boost, 0.95)
                
                # RSI confirmation
                if trend_signal == SignalType.BUY and rsi_like < 0.7:
                    # Not overbought, good signal
                    final_confidence *= 1.1
                elif trend_signal == SignalType.SELL and rsi_like > 0.3:
                    # Not oversold, good signal
                    final_confidence *= 1.1
                
                final_confidence = min(final_confidence, 0.95)
                
                # Generate signal if confident enough
                if final_confidence >= self.confidence_threshold and trend_signal != SignalType.HOLD:
                    # Calculate position size based on confidence
                    quantity = 1.0 + (final_confidence - 0.55) * 2  # 1.0 to 1.8 units
                    
                    if trend_signal == SignalType.BUY:
                        stop_loss = current_price * 0.97
                        take_profit = current_price * 1.05
                    else:  # SELL
                        stop_loss = current_price * 1.03
                        take_profit = current_price * 0.95
                    
                    signal = TradeSignal(
                        timestamp=datetime.now(timezone.utc),
                        symbol=symbol,
                        signal_type=trend_signal,
                        confidence=final_confidence,
                        quantity=quantity,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        metadata={
                            "trend_confidence": float(trend_confidence),
                            "volatility": float(volatility),
                            "rsi_like": float(rsi_like),
                            "indicator": "trend_momentum_rsi",
                        }
                    )
                    
                    signals.append(signal)
                    logger.info(
                        f"LLM Signal: {trend_signal.value.upper()} {symbol} "
                        f"@ {current_price:.2f} (conf={final_confidence:.2f})"
                    )
        
        except Exception as e:
            logger.error(f"Error generating LLM signals: {e}", exc_info=True)
        
        return signals
    
    async def execute_trade(self, signal: TradeSignal) -> bool:
        """Execute trade."""
        try:
            price = signal.entry_price if signal.entry_price else self.current_price.get(signal.symbol, 0.0)
            if price > 0:
                self.update_position(signal.symbol, signal.quantity, price)
            logger.info(f"Executed LLM trade: {signal.signal_type.value} for {signal.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error executing LLM trade: {e}")
            return False
    
    def get_metrics(self) -> StrategyMetrics:
        """Get performance metrics."""
        return self.metrics


async def test_llm_v2():
    """Quick test of LLM v2."""
    from src.integrations.strategy_adapters.strategy_interface import MarketData
    
    print("\n" + "="*80)
    print("Testing LLM-TradeBot v2 (Practical Version)")
    print("="*80)
    
    adapter = LLMTradeBotAdapterV2(config={"confidence_threshold": 0.55})
    await adapter.initialize()
    
    # Simulate price series with clear trend
    base_price = 45000.0
    for i in range(30):
        # Create uptrend
        price = base_price + (i * 100)  # Steady uptrend
        market_data = MarketData(
            timestamp=datetime.now(timezone.utc),
            symbol="BTC/USDT",
            open_price=price * 0.998,
            high_price=price * 1.005,
            low_price=price * 0.995,
            close_price=price,
            volume=1000000.0,
            bid_price=price * 0.9999,
            ask_price=price * 1.0001,
        )
        await adapter.on_market_data(market_data)
        
        if i >= 5:  # Start generating signals after some history
            signals = await adapter.generate_signals()
            print(f"Bar {i}: Price ${price:.2f} - Generated {len(signals)} signal(s)")
            for sig in signals:
                print(f"  -> {sig.signal_type.value.upper()} @ confidence={sig.confidence:.2f}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_llm_v2())
