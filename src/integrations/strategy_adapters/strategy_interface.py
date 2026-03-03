#!/usr/bin/env python3
"""
Unified Strategy Interface
统一策略接口 - 用于适配所有策略系统(Cosmic, Hummingbot, LLM-TradeBot)

This module defines the abstract base class that all strategy adapters must implement.
All trading strategies (Cosmic System, Hummingbot, LLM-TradeBot) must conform to this
interface for fair benchmarking and comparison.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Trading signal type enumeration."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE_POSITION = "close_position"


class StrategyStatus(Enum):
    """Strategy execution status."""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class MarketData:
    """Market data structure for unified format."""
    timestamp: datetime
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    bid_price: float = 0.0
    ask_price: float = 0.0
    bid_volume: float = 0.0
    ask_volume: float = 0.0
    extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeSignal:
    """Trade signal structure for unified format."""
    timestamp: datetime
    symbol: str
    signal_type: SignalType
    confidence: float  # 0.0 - 1.0
    quantity: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyMetrics:
    """Performance metrics structure."""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0  # percentage
    total_pnl: float = 0.0
    total_return_pct: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown_pct: float = 0.0
    annual_return_pct: float = 0.0
    avg_trade_duration: float = 0.0  # seconds
    execution_latency_ms: float = 0.0
    daily_avg_profit: float = 0.0
    extra_metrics: Dict[str, Any] = field(default_factory=dict)


class UnifiedStrategyInterface(ABC):
    """
    Abstract base class for all trading strategy adapters.
    
    统一策略适配器抽象基类 - 所有策略系统都必须实现这个接口
    以确保公平的基准测试和性能对比。
    
    Key responsibilities:
    1. Initialize strategy with configuration
    2. Process market data in real-time
    3. Generate trading signals
    4. Track performance metrics
    5. Execute trades (in backtesting context)
    6. Manage strategy state (pause, resume, stop)
    
    All implementations must be async-compatible for concurrent execution.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the strategy adapter.
        
        Args:
            name: Strategy identifier (e.g., 'cosmic_triangular', 'hummingbot_mm')
            config: Strategy-specific configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.status = StrategyStatus.INITIALIZED
        self.current_price = {}
        self.open_positions = {}
        self.trade_history = []
        self.metrics = StrategyMetrics()
        self._start_time = None
        self._initialize_callbacks = []
        self._signal_callbacks = []
        logger.info(f"Initialized strategy: {self.name}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the strategy with configuration.
        
        Should perform:
        - Load strategy parameters
        - Setup data sources
        - Validate configuration
        - Initialize internal state
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def on_market_data(self, market_data: MarketData) -> None:
        """
        Process incoming market data and update internal state.
        
        This method is called for each new market tick.
        Strategy should:
        - Update current prices
        - Update internal indicators
        - Maintain order book state
        
        Args:
            market_data: Incoming market data
        """
        pass
    
    @abstractmethod
    async def generate_signals(self) -> List[TradeSignal]:
        """
        Generate trading signals based on current market state.
        
        Should return:
        - Empty list if no signals
        - List of TradeSignal objects if signals detected
        
        Each signal includes:
        - Signal type (BUY, SELL, HOLD, CLOSE_POSITION)
        - Confidence level (0.0 - 1.0)
        - Quantity
        - Entry/exit prices
        - Risk management parameters
        
        Returns:
            List of generated trading signals
        """
        pass
    
    @abstractmethod
    async def execute_trade(self, signal: TradeSignal) -> bool:
        """
        Execute a trade based on the signal.
        
        In backtesting context, this simulates trade execution.
        Should:
        - Create/update/close position
        - Track PnL
        - Update metrics
        - Handle partial fills
        
        Args:
            signal: Trade signal to execute
            
        Returns:
            True if execution successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> StrategyMetrics:
        """
        Get current performance metrics.
        
        Returns comprehensive metrics including:
        - Trade statistics (count, win rate)
        - Return metrics (total, annual, daily)
        - Risk metrics (Sharpe, max drawdown)
        - Execution metrics (latency)
        
        Returns:
            StrategyMetrics object with current performance
        """
        pass
    
    # === Concrete Methods (Common Implementation) ===
    
    async def start(self) -> bool:
        """
        Start the strategy.
        
        Returns:
            True if started successfully
        """
        try:
            self._start_time = datetime.now(timezone.utc)
            result = await self.initialize()
            if result:
                self.status = StrategyStatus.RUNNING
                logger.info(f"Strategy {self.name} started")
                for callback in self._initialize_callbacks:
                    await self._call_async(callback, self)
            return result
        except Exception as e:
            self.status = StrategyStatus.ERROR
            logger.error(f"Error starting strategy {self.name}: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the strategy."""
        self.status = StrategyStatus.STOPPED
        logger.info(f"Strategy {self.name} stopped")
    
    async def pause(self) -> None:
        """Pause the strategy (maintain state)."""
        self.status = StrategyStatus.PAUSED
        logger.info(f"Strategy {self.name} paused")
    
    async def resume(self) -> None:
        """Resume the strategy."""
        if self.status == StrategyStatus.PAUSED:
            self.status = StrategyStatus.RUNNING
            logger.info(f"Strategy {self.name} resumed")
    
    def register_initialize_callback(self, callback: Callable) -> None:
        """Register callback to be called when strategy initializes."""
        self._initialize_callbacks.append(callback)
    
    def register_signal_callback(self, callback: Callable) -> None:
        """Register callback to be called when signals are generated."""
        self._signal_callbacks.append(callback)
    
    def record_trade(
        self,
        signal: TradeSignal,
        execution_price: float,
        execution_timestamp: datetime,
        pnl: float = 0.0
    ) -> None:
        """
        Record a trade in history.
        
        Args:
            signal: Original trade signal
            execution_price: Price at which trade was executed
            execution_timestamp: When the trade executed
            pnl: Profit/loss from the trade
        """
        trade_record = {
            "signal": signal,
            "execution_price": execution_price,
            "execution_timestamp": execution_timestamp,
            "pnl": pnl,
        }
        self.trade_history.append(trade_record)
        
        # Update metrics
        if signal.signal_type == SignalType.BUY or signal.signal_type == SignalType.SELL:
            self.metrics.total_trades += 1
            self.metrics.total_pnl += pnl
            
            if pnl > 0:
                self.metrics.winning_trades += 1
            elif pnl < 0:
                self.metrics.losing_trades += 1
            
            if self.metrics.total_trades > 0:
                self.metrics.win_rate = (
                    self.metrics.winning_trades / self.metrics.total_trades * 100
                )
    
    def update_position(self, symbol: str, quantity: float, price: float) -> None:
        """
        Update current position for a symbol.
        
        Args:
            symbol: Trading symbol
            quantity: Position quantity (positive=long, negative=short)
            price: Current price
        """
        self.open_positions[symbol] = {
            "quantity": quantity,
            "entry_price": price,
            "timestamp": datetime.now(timezone.utc),
        }
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current position for a symbol."""
        return self.open_positions.get(symbol)
    
    def close_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Close position for a symbol.
        
        Returns:
            Closed position details
        """
        return self.open_positions.pop(symbol, None)
    
    @staticmethod
    async def _call_async(callback: Callable, *args, **kwargs) -> Any:
        """
        Call a callback, handling both sync and async functions.
        
        Args:
            callback: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of callback
        """
        if asyncio.iscoroutinefunction(callback):
            return await callback(*args, **kwargs)
        else:
            return callback(*args, **kwargs)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} name={self.name} status={self.status.value}>"
