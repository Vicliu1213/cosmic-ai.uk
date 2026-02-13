#!/usr/bin/env python3
"""
數據整合層 (Data Integration Layer)
Comic AI Trading System - Market Data Integration

Supports multiple data sources: CSV files, OHLCV data, WebSocket streams,
and real-time market feeds.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import csv
from pathlib import Path

logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """Data format enumeration."""
    OHLCV = "ohlcv"
    CSV = "csv"
    JSON = "json"
    WEBSOCKET = "websocket"


@dataclass
class OHLCV:
    """OHLCV (Open, High, Low, Close, Volume) data."""
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], symbol: str = ""):
        """Create OHLCV from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else data['timestamp'],
            symbol=data.get('symbol', symbol),
            open=float(data['open']),
            high=float(data['high']),
            low=float(data['low']),
            close=float(data['close']),
            volume=float(data['volume']),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
        }


class DataLoader:
    """Load market data from various sources."""
    
    @staticmethod
    def load_csv(filepath: str, symbol: str = "") -> List[OHLCV]:
        """
        Load OHLCV data from CSV file.
        
        Expected CSV columns: timestamp, open, high, low, close, volume
        
        Args:
            filepath: Path to CSV file
            symbol: Trading symbol
            
        Returns:
            List of OHLCV objects
        """
        data = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        ohlcv = OHLCV.from_dict(row, symbol)
                        data.append(ohlcv)
                    except Exception as e:
                        logger.warning(f"Failed to parse row: {e}")
            
            logger.info(f"Loaded {len(data)} records from {filepath}")
            return data
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {filepath}")
            return []
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return []
    
    @staticmethod
    def load_json(filepath: str, symbol: str = "") -> List[OHLCV]:
        """
        Load OHLCV data from JSON file.
        
        Expected JSON format:
        [
            {"timestamp": "...", "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...},
            ...
        ]
        
        Args:
            filepath: Path to JSON file
            symbol: Trading symbol
            
        Returns:
            List of OHLCV objects
        """
        data = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                records = json.load(f)
                
                # Handle dict of symbols
                if isinstance(records, dict):
                    for sym, records_list in records.items():
                        for record in records_list:
                            try:
                                ohlcv = OHLCV.from_dict(record, sym)
                                data.append(ohlcv)
                            except Exception as e:
                                logger.warning(f"Failed to parse record: {e}")
                # Handle list of records
                elif isinstance(records, list):
                    for record in records:
                        try:
                            ohlcv = OHLCV.from_dict(record, symbol)
                            data.append(ohlcv)
                        except Exception as e:
                            logger.warning(f"Failed to parse record: {e}")
            
            logger.info(f"Loaded {len(data)} records from {filepath}")
            return data
            
        except FileNotFoundError:
            logger.error(f"JSON file not found: {filepath}")
            return []
        except Exception as e:
            logger.error(f"Failed to load JSON: {e}")
            return []
    
    @staticmethod
    def generate_mock_data(symbol: str, num_records: int = 1000) -> List[OHLCV]:
        """
        Generate mock OHLCV data for testing.
        
        Args:
            symbol: Trading symbol
            num_records: Number of records to generate
            
        Returns:
            List of OHLCV objects
        """
        import random
        from datetime import timedelta
        
        data = []
        current_price = 100.0
        base_time = datetime.now() - timedelta(days=num_records)
        
        for i in range(num_records):
            timestamp = base_time + timedelta(hours=i)
            
            # Generate realistic price movement
            change = random.uniform(-2, 2)
            open_price = current_price
            close_price = current_price + change
            high_price = max(open_price, close_price) + random.uniform(0, 1)
            low_price = min(open_price, close_price) - random.uniform(0, 1)
            volume = random.uniform(1000000, 10000000)
            
            ohlcv = OHLCV(
                timestamp=timestamp,
                symbol=symbol,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
            )
            
            data.append(ohlcv)
            current_price = close_price
        
        logger.info(f"Generated {len(data)} mock records for {symbol}")
        return data


class DataBuffer:
    """Buffer for market data with caching."""
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize data buffer.
        
        Args:
            max_size: Maximum number of records to keep
        """
        self.max_size = max_size
        self.buffer: Dict[str, List[OHLCV]] = {}
        self.callbacks: List[Callable[[OHLCV], None]] = []
    
    def add_data(self, ohlcv: OHLCV) -> None:
        """Add OHLCV data to buffer."""
        symbol = ohlcv.symbol
        
        if symbol not in self.buffer:
            self.buffer[symbol] = []
        
        self.buffer[symbol].append(ohlcv)
        
        # Keep buffer size in check
        if len(self.buffer[symbol]) > self.max_size:
            self.buffer[symbol] = self.buffer[symbol][-self.max_size:]
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(ohlcv)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    def add_bulk(self, ohlcvs: List[OHLCV]) -> None:
        """Add multiple OHLCV records."""
        for ohlcv in ohlcvs:
            self.add_data(ohlcv)
    
    def get_latest(self, symbol: str) -> Optional[OHLCV]:
        """Get latest data for symbol."""
        if symbol in self.buffer and self.buffer[symbol]:
            return self.buffer[symbol][-1]
        return None
    
    def get_range(self, symbol: str, num_records: int = 100) -> List[OHLCV]:
        """Get latest N records for symbol."""
        if symbol not in self.buffer:
            return []
        return self.buffer[symbol][-num_records:]
    
    def get_all(self, symbol: str) -> List[OHLCV]:
        """Get all records for symbol."""
        return self.buffer.get(symbol, [])
    
    def register_callback(self, callback: Callable[[OHLCV], None]) -> None:
        """Register callback for new data."""
        self.callbacks.append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        total_records = sum(len(records) for records in self.buffer.values())
        return {
            'symbols': len(self.buffer),
            'total_records': total_records,
            'max_size': self.max_size,
            'usage': f"{(total_records / (self.max_size * len(self.buffer) + 1)) * 100:.1f}%" if self.buffer else "0%",
        }


class DataAnalyzer:
    """Analyze market data."""
    
    @staticmethod
    def calculate_sma(ohlcvs: List[OHLCV], period: int = 20) -> List[Tuple[datetime, float]]:
        """
        Calculate Simple Moving Average.
        
        Args:
            ohlcvs: List of OHLCV data
            period: SMA period
            
        Returns:
            List of (timestamp, sma) tuples
        """
        result = []
        
        for i in range(len(ohlcvs)):
            if i < period - 1:
                continue
            
            window = ohlcvs[i - period + 1:i + 1]
            sma = sum(o.close for o in window) / period
            result.append((ohlcvs[i].timestamp, sma))
        
        return result
    
    @staticmethod
    def calculate_ema(ohlcvs: List[OHLCV], period: int = 20) -> List[Tuple[datetime, float]]:
        """
        Calculate Exponential Moving Average.
        
        Args:
            ohlcvs: List of OHLCV data
            period: EMA period
            
        Returns:
            List of (timestamp, ema) tuples
        """
        result = []
        multiplier = 2 / (period + 1)
        
        # Calculate initial SMA
        if len(ohlcvs) < period:
            return result
        
        ema = sum(o.close for o in ohlcvs[:period]) / period
        result.append((ohlcvs[period - 1].timestamp, ema))
        
        # Calculate EMA
        for i in range(period, len(ohlcvs)):
            ema = ohlcvs[i].close * multiplier + ema * (1 - multiplier)
            result.append((ohlcvs[i].timestamp, ema))
        
        return result
    
    @staticmethod
    def calculate_rsi(ohlcvs: List[OHLCV], period: int = 14) -> List[Tuple[datetime, float]]:
        """
        Calculate Relative Strength Index.
        
        Args:
            ohlcvs: List of OHLCV data
            period: RSI period
            
        Returns:
            List of (timestamp, rsi) tuples
        """
        result = []
        
        if len(ohlcvs) < period + 1:
            return result
        
        gains = []
        losses = []
        
        for i in range(1, len(ohlcvs)):
            change = ohlcvs[i].close - ohlcvs[i - 1].close
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Calculate RSI
        for i in range(period - 1, len(gains)):
            avg_gain = sum(gains[i - period + 1:i + 1]) / period
            avg_loss = sum(losses[i - period + 1:i + 1]) / period
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
            
            result.append((ohlcvs[i + 1].timestamp, rsi))
        
        return result
    
    @staticmethod
    def calculate_volatility(ohlcvs: List[OHLCV], period: int = 20) -> List[Tuple[datetime, float]]:
        """
        Calculate volatility (standard deviation).
        
        Args:
            ohlcvs: List of OHLCV data
            period: Volatility period
            
        Returns:
            List of (timestamp, volatility) tuples
        """
        import math
        result = []
        
        for i in range(len(ohlcvs)):
            if i < period - 1:
                continue
            
            window = ohlcvs[i - period + 1:i + 1]
            returns = []
            
            for j in range(1, len(window)):
                ret = (window[j].close - window[j - 1].close) / window[j - 1].close
                returns.append(ret)
            
            if returns:
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                volatility = math.sqrt(variance)
                result.append((ohlcvs[i].timestamp, volatility))
        
        return result
    
    @staticmethod
    def get_price_stats(ohlcvs: List[OHLCV]) -> Dict[str, float]:
        """Get price statistics."""
        if not ohlcvs:
            return {}
        
        closes = [o.close for o in ohlcvs]
        
        return {
            'min': min(closes),
            'max': max(closes),
            'avg': sum(closes) / len(closes),
            'latest': closes[-1],
            'change': closes[-1] - closes[0],
            'change_percent': ((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] != 0 else 0,
        }


class DataManager:
    """Overall data management."""
    
    def __init__(self):
        """Initialize data manager."""
        self.buffer = DataBuffer()
        self.analyzer = DataAnalyzer()
        self.loader = DataLoader()
    
    async def load_and_buffer_data(self, 
                                   filepath: str, 
                                   format: DataFormat = DataFormat.CSV,
                                   symbol: str = "") -> bool:
        """Load data from file and buffer it."""
        try:
            data = []
            
            if format == DataFormat.CSV:
                data = self.loader.load_csv(filepath, symbol)
            elif format == DataFormat.JSON:
                data = self.loader.load_json(filepath, symbol)
            
            self.buffer.add_bulk(data)
            logger.info(f"Buffered {len(data)} records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load and buffer data: {e}")
            return False
    
    async def load_mock_data(self, symbol: str, num_records: int = 1000) -> bool:
        """Load mock data for testing."""
        try:
            data = self.loader.generate_mock_data(symbol, num_records)
            self.buffer.add_bulk(data)
            logger.info(f"Loaded mock data: {symbol} ({num_records} records)")
            return True
        except Exception as e:
            logger.error(f"Failed to load mock data: {e}")
            return False
    
    def get_analysis(self, symbol: str, analysis_type: str = "all") -> Dict[str, Any]:
        """Get analysis for symbol."""
        data = self.buffer.get_all(symbol)
        if not data:
            return {}
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
        }
        
        if analysis_type in ["all", "price"]:
            result['price_stats'] = self.analyzer.get_price_stats(data)
        
        if analysis_type in ["all", "sma"]:
            result['sma_20'] = self.analyzer.calculate_sma(data, 20)[-10:]
        
        if analysis_type in ["all", "ema"]:
            result['ema_20'] = self.analyzer.calculate_ema(data, 20)[-10:]
        
        if analysis_type in ["all", "rsi"]:
            result['rsi_14'] = self.analyzer.calculate_rsi(data, 14)[-10:]
        
        if analysis_type in ["all", "volatility"]:
            result['volatility'] = self.analyzer.calculate_volatility(data, 20)[-10:]
        
        return result
    
    def get_buffer_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        return self.buffer.get_stats()


async def main():
    """Test data integration layer."""
    logger.info("=" * 70)
    logger.info("Comic AI - Data Integration Layer Test")
    logger.info("=" * 70)
    
    # Create data manager
    manager = DataManager()
    
    # Load mock data
    logger.info("\n📊 Loading mock data...")
    await manager.load_mock_data("BTC/USD", 1000)
    await manager.load_mock_data("ETH/USD", 1000)
    
    # Get buffer stats
    logger.info("\n📈 Buffer statistics:")
    stats = manager.get_buffer_stats()
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    # Get analysis
    logger.info("\n🔍 Analysis for BTC/USD:")
    analysis = manager.get_analysis("BTC/USD")
    logger.info(f"  Price stats: {analysis.get('price_stats')}")
    logger.info(f"  SMA (last 3): {analysis.get('sma_20')[-3:] if analysis.get('sma_20') else 'N/A'}")
    logger.info(f"  RSI (last 3): {analysis.get('rsi_14')[-3:] if analysis.get('rsi_14') else 'N/A'}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Test completed")
    logger.info("=" * 70)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
