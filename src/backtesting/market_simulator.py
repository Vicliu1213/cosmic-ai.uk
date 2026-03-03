#!/usr/bin/env python3
"""
Market Simulator for Backtesting
回測市場模擬器 - 生成真實的OHLCV數據

模擬特性:
- 幾何布朗運動 (GBM) 生成價格路徑
- 真實的市場特徵 (波動率、跳躍、均值回歸)
- 訂單簿深度和滑點
- 交易摩擦成本 (手續費、點差)
"""

import numpy as np
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime types."""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    MEAN_REVERSION = "mean_reversion"
    VOLATILE = "volatile"
    LOW_VOLATILITY = "low_volatility"


@dataclass
class OHLCVBar:
    """OHLCV candlestick bar."""
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    bid_price: float = 0.0
    ask_price: float = 0.0
    bid_volume: float = 0.0
    ask_volume: float = 0.0


@dataclass
class MarketSnapshot:
    """Market snapshot at a point in time."""
    timestamp: datetime
    bars: Dict[str, OHLCVBar]
    regime: MarketRegime
    volatility: float
    volume_profile: Dict[str, float]
    liquidity_score: float  # 0-1, 1 = perfectly liquid


class GeometricBrownianMotion:
    """
    Geometric Brownian Motion price generator.
    
    Model: dS = μ*S*dt + σ*S*dW
    Where:
      S = price
      μ = drift (expected return)
      σ = volatility
      dW = Wiener process increment
    """
    
    def __init__(self, initial_price: float, drift: float = 0.0001, volatility: float = 0.02):
        """
        Initialize GBM.
        
        Args:
            initial_price: Starting price
            drift: Expected daily return
            volatility: Daily volatility
        """
        self.initial_price = initial_price
        self.drift = drift
        self.volatility = volatility
        self.current_price = initial_price
    
    def generate_path(self, steps: int, dt: float = 1.0) -> np.ndarray:
        """
        Generate price path using GBM.
        
        Args:
            steps: Number of steps
            dt: Time step (1.0 = 1 day)
            
        Returns:
            Array of prices
        """
        prices = np.zeros(steps + 1)
        prices[0] = self.current_price
        
        for i in range(steps):
            # Generate random shock
            dW = np.random.normal(0, np.sqrt(dt))
            
            # GBM formula
            dS = self.drift * prices[i] * dt + self.volatility * prices[i] * dW
            prices[i + 1] = prices[i] + dS
            
            # Ensure price stays positive
            prices[i + 1] = max(prices[i + 1], prices[i] * 0.5)
        
        self.current_price = prices[-1]
        return prices
    
    def reset(self, initial_price: Optional[float] = None):
        """Reset the path generator."""
        if initial_price:
            self.initial_price = initial_price
            self.current_price = initial_price
        else:
            self.current_price = self.initial_price


class MarketSimulator:
    """
    Market simulator for backtesting.
    
    生成真實的市場數據，包括:
    - OHLCV 蠟燭線
    - 市場體制變化
    - 流動性變化
    - 交易摩擦成本
    """
    
    def __init__(
        self,
        symbols: List[str],
        initial_prices: Dict[str, float],
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1h"  # "1m", "5m", "1h", "1d"
    ):
        """
        Initialize market simulator.
        
        Args:
            symbols: List of trading symbols
            initial_prices: Initial price for each symbol
            start_date: Backtesting start date
            end_date: Backtesting end date
            timeframe: Candlestick timeframe
        """
        self.symbols = symbols
        self.initial_prices = initial_prices
        self.start_date = start_date
        self.end_date = end_date
        self.timeframe = timeframe
        
        # Initialize GBM generators
        self.gbm_generators = {
            symbol: GeometricBrownianMotion(
                initial_price=initial_prices[symbol],
                drift=np.random.uniform(0.0, 0.0005),  # Random drift 0-0.05% per day
                volatility=np.random.uniform(0.01, 0.05)  # 1-5% daily volatility
            )
            for symbol in symbols
        }
        
        # Market regime tracker
        self.current_regime = MarketRegime.MEAN_REVERSION
        self.regime_change_probability = 0.05  # 5% chance per bar
        
        # Generate time index
        self.timeframe_minutes = self._parse_timeframe(timeframe)
        self.timestamps = self._generate_timestamps()
        
        logger.info(
            f"Market simulator initialized: {len(self.symbols)} symbols, "
            f"{len(self.timestamps)} bars ({timeframe})"
        )
    
    @staticmethod
    def _parse_timeframe(timeframe: str) -> int:
        """Parse timeframe string to minutes."""
        mapping = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
        return mapping.get(timeframe, 60)
    
    def _generate_timestamps(self) -> List[datetime]:
        """Generate market timestamps (excluding weekends)."""
        timestamps = []
        current = self.start_date
        
        while current <= self.end_date:
            # Skip weekends for crypto (24/7, so include weekends)
            timestamps.append(current)
            current += timedelta(minutes=self.timeframe_minutes)
        
        return timestamps
    
    def generate_bar(self, symbol: str, idx: int) -> OHLCVBar:
        """
        Generate OHLCV bar for a symbol at time index.
        
        Args:
            symbol: Trading symbol
            idx: Time index in timestamps
            
        Returns:
            OHLCV bar
        """
        timestamp = self.timestamps[idx]
        gbm = self.gbm_generators[symbol]
        
        # Generate 4 price movements within the bar (OHLC)
        price_path = gbm.generate_path(steps=4, dt=self.timeframe_minutes / 1440.0)
        
        open_price = price_path[0]
        close_price = price_path[-1]
        high_price = np.max(price_path)
        low_price = np.min(price_path)
        
        # Volume varies with volatility and regime
        volatility = (high_price - low_price) / low_price if low_price > 0 else 0
        base_volume = 1000000  # 1M base volume
        volume_multiplier = 1.0 + volatility * 10
        
        if self.current_regime in [MarketRegime.VOLATILE, MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN]:
            volume_multiplier *= 1.5
        
        volume = base_volume * volume_multiplier * np.random.uniform(0.8, 1.2)
        
        # Bid-ask spread based on volatility and regime
        mid_price = close_price
        spread_bps = 2 + volatility * 100  # 2-102 basis points
        spread = mid_price * spread_bps / 10000
        
        bid_price = mid_price - spread / 2
        ask_price = mid_price + spread / 2
        
        # Order book depth
        bid_volume = volume * np.random.uniform(0.3, 0.7)
        ask_volume = volume * np.random.uniform(0.3, 0.7)
        
        return OHLCVBar(
            timestamp=timestamp,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=volume,
            bid_price=bid_price,
            ask_price=ask_price,
            bid_volume=bid_volume,
            ask_volume=ask_volume,
        )
    
    def get_snapshot(self, idx: int) -> MarketSnapshot:
        """
        Get full market snapshot at time index.
        
        Args:
            idx: Time index
            
        Returns:
            Market snapshot with all symbols
        """
        timestamp = self.timestamps[idx]
        bars = {symbol: self.generate_bar(symbol, idx) for symbol in self.symbols}
        
        # Update market regime
        if np.random.random() < self.regime_change_probability:
            self.current_regime = random.choice([e for e in MarketRegime])
        
        # Calculate average volatility
        volatilities = [
            (bar.high_price - bar.low_price) / bar.low_price 
            for bar in bars.values() if bar.low_price > 0
        ]
        avg_volatility = float(np.mean(volatilities)) if volatilities else 0.02
        
        # Calculate liquidity score (0-1)
        avg_spread_bps = np.mean([
            (bar.ask_price - bar.bid_price) / bar.bid_price * 10000
            for bar in bars.values() if bar.bid_price > 0
        ])
        liquidity_score = float(max(0, 1.0 - avg_spread_bps / 100))
        
        return MarketSnapshot(
            timestamp=timestamp,
            bars=bars,
            regime=self.current_regime,
            volatility=avg_volatility,
            volume_profile={symbol: bars[symbol].volume for symbol in self.symbols},
            liquidity_score=liquidity_score,
        )
    
    def __iter__(self):
        """Iterate over market snapshots."""
        for idx in range(len(self.timestamps)):
            yield self.get_snapshot(idx)
    
    def __len__(self) -> int:
        """Number of bars in simulation."""
        return len(self.timestamps)


class SlippageModel:
    """Model slippage and market impact."""
    
    def __init__(
        self,
        maker_fee: float = 0.0002,  # 0.02%
        taker_fee: float = 0.0005,  # 0.05%
        slippage_multiplier: float = 1.0
    ):
        """
        Initialize slippage model.
        
        Args:
            maker_fee: Fee for limit orders
            taker_fee: Fee for market orders
            slippage_multiplier: Market impact multiplier
        """
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.slippage_multiplier = slippage_multiplier
    
    def calculate_execution_price(
        self,
        price: float,
        quantity: float,
        order_type: str = "market",  # "market" or "limit"
        bar: Optional[OHLCVBar] = None
    ) -> Tuple[float, float]:  # (execution_price, fee)
        """
        Calculate actual execution price including slippage and fees.
        
        Args:
            price: Quoted price
            quantity: Order quantity
            order_type: "market" or "limit"
            bar: Market bar for bid-ask info
            
        Returns:
            Tuple of (execution_price, total_fee)
        """
        # Determine fee
        fee = self.taker_fee if order_type == "market" else self.maker_fee
        
        # Calculate slippage based on quantity vs available liquidity
        if bar:
            available_liquidity = bar.bid_volume if price > bar.close_price else bar.ask_volume
            quantity_ratio = quantity / available_liquidity if available_liquidity > 0 else 0
            slippage = quantity_ratio * self.slippage_multiplier
        else:
            slippage = 0
        
        # Total cost per unit
        total_cost_per_unit = fee + slippage
        execution_price = price * (1 + total_cost_per_unit if price > 0 else 0)
        
        # Total fee in absolute terms
        total_fee = execution_price * quantity * (fee + slippage)
        
        return execution_price, total_fee


def test_market_simulator():
    """Test market simulator."""
    
    print("\n" + "="*80)
    print("Testing Market Simulator")
    print("="*80)
    
    # Initialize simulator
    symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
    initial_prices = {
        "BTC/USDT": 45000.0,
        "ETH/USDT": 2500.0,
        "ADA/USDT": 0.5,
    }
    
    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 1, 10, tzinfo=timezone.utc)
    
    simulator = MarketSimulator(
        symbols=symbols,
        initial_prices=initial_prices,
        start_date=start_date,
        end_date=end_date,
        timeframe="1h"
    )
    
    print(f"\nSimulation period: {start_date} to {end_date}")
    print(f"Timeframe: 1h")
    print(f"Total bars: {len(simulator)}")
    
    # Generate first 10 snapshots
    print("\nFirst 10 market snapshots:")
    for idx, snapshot in enumerate(simulator):
        if idx >= 10:
            break
        
        print(f"\n[{idx}] {snapshot.timestamp} | Regime: {snapshot.regime.value}")
        for symbol in symbols:
            bar = snapshot.bars[symbol]
            print(f"  {symbol:12s} | O:{bar.open_price:8.2f} H:{bar.high_price:8.2f} "
                  f"L:{bar.low_price:8.2f} C:{bar.close_price:8.2f} | "
                  f"Vol:{bar.volume/1e6:6.2f}M | Bid:{bar.bid_price:8.2f} Ask:{bar.ask_price:8.2f}")
        print(f"  Volatility: {snapshot.volatility:.2%} | Liquidity: {snapshot.liquidity_score:.2f}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_market_simulator()
