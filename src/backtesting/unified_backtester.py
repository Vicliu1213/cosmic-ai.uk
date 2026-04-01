#!/usr/bin/env python3
"""
Unified Backtester for Strategy Performance Evaluation
統一回測引擎 - 整合所有策略系統的回測框架

This module orchestrates the complete backtesting workflow:
1. Initialize strategy adapter
2. Loop through market snapshots
3. Generate signals and execute trades
4. Track positions and P&L
5. Calculate performance metrics
"""

import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np

from src.integrations.strategy_adapters.strategy_interface import (
    UnifiedStrategyInterface, MarketData, TradeSignal, SignalType, StrategyMetrics
)
from src.backtesting.market_simulator import MarketSnapshot, OHLCVBar
from src.backtesting.metrics_calculator import MetricsCalculator, TradeRecord, PortfolioSnapshot

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Open position tracking."""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    position_type: str  # "long" or "short"
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_price: float = 0.0
    unrealized_pnl: float = 0.0


@dataclass
class BacktestConfig:
    """Backtesting configuration."""
    initial_capital: float = 100000.0
    maker_fee: float = 0.001  # 0.1% maker fee
    taker_fee: float = 0.002  # 0.2% taker fee
    max_position_size: float = 0.5  # Max 50% of capital per trade
    slippage_bps: float = 2.0  # 2 basis points slippage
    use_stop_loss: bool = True
    use_take_profit: bool = True


class UnifiedBacktester:
    """
    Complete backtesting engine for strategy evaluation.
    
    統一回測引擎 - 支持所有策略系統(Cosmic, Hummingbot, LLM-TradeBot)
    """
    
    def __init__(
        self,
        strategy: UnifiedStrategyInterface,
        config: Optional[BacktestConfig] = None,
        metrics_calculator: Optional[MetricsCalculator] = None
    ):
        """
        Initialize backtester.
        
        Args:
            strategy: Strategy adapter implementing UnifiedStrategyInterface
            config: Backtesting configuration
            metrics_calculator: Metrics calculator instance (creates if None)
        """
        self.strategy = strategy
        self.config = config or BacktestConfig()
        self.metrics_calculator = metrics_calculator or MetricsCalculator(
            initial_capital=self.config.initial_capital
        )
        
        # Portfolio state
        self.cash = self.config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.portfolio_value = self.config.initial_capital
        self.closed_pnl = 0.0
        
        # Tracking
        self.market_snapshots_processed = 0
        self.signals_generated = 0
        self.trades_executed = 0
        self.current_timestamp = None
    
    async def run_backtest(self, market_snapshots: List[MarketSnapshot]) -> StrategyMetrics:
        """
        Run complete backtest on market data.
        
        Args:
            market_snapshots: List of market snapshots from simulator
            
        Returns:
            StrategyMetrics with complete performance analysis
        """
        logger.info(f"Starting backtest with {len(market_snapshots)} market snapshots")
        logger.info(f"Initial capital: ${self.config.initial_capital:,.2f}")
        
        # Initialize strategy
        await self.strategy.initialize()
        
        try:
            # Process each market snapshot
            for i, snapshot in enumerate(market_snapshots):
                self.current_timestamp = snapshot.timestamp
                
                # Log progress every 50 snapshots
                if (i + 1) % 50 == 0:
                    logger.info(f"Processing snapshot {i+1}/{len(market_snapshots)} "
                               f"at {snapshot.timestamp}")
                
                # Update positions with current prices
                self._update_position_prices(snapshot)
                
                # Process each symbol in snapshot
                for symbol, bar in snapshot.bars.items():
                    # Create market data object
                    market_data = MarketData(
                        timestamp=snapshot.timestamp,
                        symbol=symbol,
                        open_price=bar.open_price,
                        high_price=bar.high_price,
                        low_price=bar.low_price,
                        close_price=bar.close_price,
                        volume=bar.volume,
                        bid_price=bar.bid_price,
                        ask_price=bar.ask_price,
                        bid_volume=bar.bid_volume,
                        ask_volume=bar.ask_volume,
                        extra_fields={'liquidity_score': snapshot.liquidity_score}
                    )
                    
                    # Feed market data to strategy
                    await self.strategy.on_market_data(market_data)
                    
                    # Check for stop-loss/take-profit triggers
                    self._check_exit_conditions(symbol, bar, snapshot.timestamp)
                
                # Generate signals
                signals = await self.strategy.generate_signals()
                self.signals_generated += len(signals)
                
                # Execute signals
                for signal in signals:
                    self._execute_signal(signal, snapshot)
                
                # Record portfolio snapshot
                self._record_portfolio_snapshot(snapshot.timestamp)
                
                self.market_snapshots_processed += 1
        
        finally:
            # Close all positions at end of backtest
            self._close_all_positions(market_snapshots[-1].timestamp)
            
            # Generate final metrics
            logger.info(f"Backtest complete: {self.trades_executed} trades executed, "
                       f"{len(self.metrics_calculator.trades)} closed trades")
            logger.info(f"Final portfolio value: ${self.portfolio_value:,.2f}")
        
        # Return metrics
        metrics = self.metrics_calculator.generate_metrics()
        return metrics
    
    def _update_position_prices(self, snapshot: MarketSnapshot) -> None:
        """Update current prices for all open positions."""
        for symbol, position in self.positions.items():
            if symbol in snapshot.bars:
                bar = snapshot.bars[symbol]
                position.current_price = bar.close_price
                position.unrealized_pnl = self._calculate_position_pnl(position)
    
    def _calculate_position_pnl(self, position: Position) -> float:
        """Calculate unrealized P&L for a position."""
        if position.position_type == "long":
            pnl = (position.current_price - position.entry_price) * position.quantity
        else:  # short
            pnl = (position.entry_price - position.current_price) * position.quantity
        return pnl
    
    def _check_exit_conditions(
        self,
        symbol: str,
        bar: OHLCVBar,
        timestamp: datetime
    ) -> None:
        """Check if stop-loss or take-profit conditions are met."""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Check stop-loss
        if self.config.use_stop_loss and position.stop_loss:
            if position.position_type == "long" and bar.low_price <= position.stop_loss:
                logger.info(f"Stop-loss triggered for {symbol} at ${position.stop_loss:.2f}")
                self._close_position(symbol, position.stop_loss, timestamp, reason="stop_loss")
                return
            elif position.position_type == "short" and bar.high_price >= position.stop_loss:
                logger.info(f"Stop-loss triggered for {symbol} at ${position.stop_loss:.2f}")
                self._close_position(symbol, position.stop_loss, timestamp, reason="stop_loss")
                return
        
        # Check take-profit
        if self.config.use_take_profit and position.take_profit:
            if position.position_type == "long" and bar.high_price >= position.take_profit:
                logger.info(f"Take-profit triggered for {symbol} at ${position.take_profit:.2f}")
                self._close_position(symbol, position.take_profit, timestamp, reason="take_profit")
                return
            elif position.position_type == "short" and bar.low_price <= position.take_profit:
                logger.info(f"Take-profit triggered for {symbol} at ${position.take_profit:.2f}")
                self._close_position(symbol, position.take_profit, timestamp, reason="take_profit")
                return
    
    def _execute_signal(self, signal: TradeSignal, snapshot: MarketSnapshot) -> None:
        """Execute a trading signal."""
        if signal.symbol not in snapshot.bars:
            logger.warning(f"Symbol {signal.symbol} not found in market snapshot")
            return
        
        bar = snapshot.bars[signal.symbol]
        
        # Check if we have sufficient capital
        position_cost = signal.entry_price * signal.quantity if signal.entry_price is not None else bar.close_price * signal.quantity
        
        if position_cost > self.cash:
            logger.warning(f"Insufficient capital for {signal.symbol}: "
                          f"need ${position_cost:,.2f}, have ${self.cash:,.2f}")
            return
        
        if signal.signal_type == SignalType.BUY:
            self._open_long_position(signal, bar, snapshot.timestamp)
        elif signal.signal_type == SignalType.SELL:
            self._open_short_position(signal, bar, snapshot.timestamp)
        elif signal.signal_type == SignalType.CLOSE_POSITION:
            self._close_position(signal.symbol, bar.close_price, snapshot.timestamp)
    
    def _open_long_position(
        self,
        signal: TradeSignal,
        bar: OHLCVBar,
        timestamp: datetime
    ) -> None:
        """Open a long position."""
        if signal.symbol in self.positions:
            logger.warning(f"Position already exists for {signal.symbol}, skipping")
            return
        
        # Use signal entry price if provided, else use bar close
        entry_price = signal.entry_price or bar.close_price
        quantity = signal.quantity
        
        # Calculate fees
        fees = entry_price * quantity * self.config.taker_fee
        slippage = entry_price * quantity * (self.config.slippage_bps / 10000)
        
        # Deduct from cash
        total_cost = entry_price * quantity + fees + slippage
        self.cash -= total_cost
        
        # Create position
        position = Position(
            symbol=signal.symbol,
            quantity=quantity,
            entry_price=entry_price,
            entry_time=timestamp,
            position_type="long",
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            current_price=entry_price
        )
        
        self.positions[signal.symbol] = position
        self.trades_executed += 1
        
        logger.info(f"BUY {quantity} {signal.symbol} @ ${entry_price:.2f}, "
                   f"fees: ${fees:.2f}, slippage: ${slippage:.2f}")
    
    def _open_short_position(
        self,
        signal: TradeSignal,
        bar: OHLCVBar,
        timestamp: datetime
    ) -> None:
        """Open a short position."""
        if signal.symbol in self.positions:
            logger.warning(f"Position already exists for {signal.symbol}, skipping")
            return
        
        # Use signal entry price if provided, else use bar close
        entry_price = signal.entry_price or bar.close_price
        quantity = signal.quantity
        
        # Calculate fees
        fees = entry_price * quantity * self.config.taker_fee
        slippage = entry_price * quantity * (self.config.slippage_bps / 10000)
        
        # Add to cash (shorting)
        proceeds = entry_price * quantity - fees - slippage
        self.cash += proceeds
        
        # Create position
        position = Position(
            symbol=signal.symbol,
            quantity=quantity,
            entry_price=entry_price,
            entry_time=timestamp,
            position_type="short",
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            current_price=entry_price
        )
        
        self.positions[signal.symbol] = position
        self.trades_executed += 1
        
        logger.info(f"SELL {quantity} {signal.symbol} @ ${entry_price:.2f}, "
                   f"fees: ${fees:.2f}, slippage: ${slippage:.2f}")
    
    def _close_position(
        self,
        symbol: str,
        exit_price: float,
        timestamp: datetime,
        reason: str = "signal"
    ) -> None:
        """Close an open position."""
        if symbol not in self.positions:
            logger.warning(f"No position to close for {symbol}")
            return
        
        position = self.positions[symbol]
        
        # Calculate P&L
        if position.position_type == "long":
            pnl = (exit_price - position.entry_price) * position.quantity
        else:  # short
            pnl = (position.entry_price - exit_price) * position.quantity
        
        # Calculate fees
        fees = exit_price * position.quantity * self.config.maker_fee
        slippage = exit_price * position.quantity * (self.config.slippage_bps / 10000)
        
        # Adjust cash
        if position.position_type == "long":
            self.cash += exit_price * position.quantity - fees - slippage
        else:  # short
            self.cash -= exit_price * position.quantity + fees + slippage
        
        # Record trade
        self.metrics_calculator.add_trade(
            entry_time=position.entry_time,
            entry_price=position.entry_price,
            exit_time=timestamp,
            exit_price=exit_price,
            quantity=position.quantity,
            position_type=position.position_type,
            fees=fees,
            slippage=slippage
        )
        
        self.closed_pnl += pnl
        
        logger.info(f"CLOSE {position.position_type.upper()} {symbol}: "
                   f"entry ${position.entry_price:.2f}, exit ${exit_price:.2f}, "
                   f"PnL: ${pnl:.2f} ({reason})")
        
        del self.positions[symbol]
    
    def _close_all_positions(self, timestamp: datetime) -> None:
        """Close all remaining open positions."""
        symbols_to_close = list(self.positions.keys())
        for symbol in symbols_to_close:
            # Use last known price
            position = self.positions[symbol]
            self._close_position(symbol, position.current_price, timestamp, reason="backtest_end")
    
    def _record_portfolio_snapshot(self, timestamp: datetime) -> None:
        """Record portfolio state at current time."""
        # Calculate total position value
        positions_value = sum(
            pos.current_price * pos.quantity
            for pos in self.positions.values()
        )
        
        # Calculate total P&L
        open_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        
        # Total portfolio value
        total_value = self.cash + positions_value + open_pnl
        self.portfolio_value = total_value
        
        # Record snapshot
        self.metrics_calculator.add_portfolio_snapshot(
            timestamp=timestamp,
            total_value=total_value,
            cash=self.cash,
            positions_value=positions_value,
            open_pnl=open_pnl,
            closed_pnl=self.closed_pnl
        )
    
    def get_backtest_summary(self) -> Dict[str, Any]:
        """Get backtest summary."""
        return {
            'market_snapshots_processed': self.market_snapshots_processed,
            'signals_generated': self.signals_generated,
            'trades_executed': self.trades_executed,
            'final_cash': self.cash,
            'final_portfolio_value': self.portfolio_value,
            'open_positions': len(self.positions),
            'closed_pnl': self.closed_pnl
        }
