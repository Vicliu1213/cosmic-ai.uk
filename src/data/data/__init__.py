#!/usr/bin/env python3
"""
Data Processing Utilities
數據處理工具

Provides data loading, validation, caching, and feature extraction utilities
for market data processing and technical indicator calculation.
提供市場數據處理和技術指標計算的數據加載、驗證、緩存和特徵提取工具。
"""

import os
import json
import csv
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import pickle

import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class DataPoint:
    """Market data point - 市場數據點"""
    timestamp: datetime
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume
        }

class DataLoader:
    """
    Data loader for CSV and JSON market data files.
    用於 CSV 和 JSON 市場數據文件的數據加載器。
    
    Supports loading OHLCV (Open, High, Low, Close, Volume) data
    from various file formats.
    """
    
    def __init__(self, default_encoding: str = 'utf-8'):
        """
        Initialize data loader.
        
        Args:
            default_encoding: Default file encoding
        """
        self.default_encoding = default_encoding
        self.logger = logging.getLogger(f"{__name__}.DataLoader")
        
    def load_csv(
        self,
        filepath: str,
        symbol: str,
        date_column: str = 'date',
        open_col: str = 'open',
        high_col: str = 'high',
        low_col: str = 'low',
        close_col: str = 'close',
        volume_col: str = 'volume'
    ) -> List[DataPoint]:
        """
        Load market data from CSV file.
        
        從 CSV 文件加載市場數據。
        
        Args:
            filepath: Path to CSV file
            symbol: Stock symbol
            date_column: Column name for dates
            open_col: Column name for open prices
            high_col: Column name for high prices
            low_col: Column name for low prices
            close_col: Column name for close prices
            volume_col: Column name for volumes
            
        Returns:
            List of DataPoint objects
        """
        data_points = []
        
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            
            with open(filepath, 'r', encoding=self.default_encoding) as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        data_point = DataPoint(
                            timestamp=self._parse_datetime(row[date_column]),
                            symbol=symbol,
                            open_price=float(row[open_col]),
                            high_price=float(row[high_col]),
                            low_price=float(row[low_col]),
                            close_price=float(row[close_col]),
                            volume=float(row[volume_col])
                        )
                        data_points.append(data_point)
                    except ValueError as e:
                        self.logger.warning(f"Skipping invalid row: {e}")
                        continue
            
            self.logger.info(f"Loaded {len(data_points)} data points from {filepath}")
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {e}")
            return []
    
    def load_json(
        self,
        filepath: str,
        symbol: str,
        data_key: str = 'data'
    ) -> List[DataPoint]:
        """
        Load market data from JSON file.
        
        從 JSON 文件加載市場數據。
        
        Args:
            filepath: Path to JSON file
            symbol: Stock symbol
            data_key: Key containing data array
            
        Returns:
            List of DataPoint objects
        """
        data_points = []
        
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            
            with open(filepath, 'r', encoding=self.default_encoding) as f:
                json_data = json.load(f)
            
            data_array = json_data.get(data_key, json_data)
            if not isinstance(data_array, list):
                data_array = [data_array]
            
            for item in data_array:
                try:
                    data_point = DataPoint(
                        timestamp=self._parse_datetime(item.get('timestamp', item.get('date'))),
                        symbol=symbol,
                        open_price=float(item.get('open', item.get('o', 0))),
                        high_price=float(item.get('high', item.get('h', 0))),
                        low_price=float(item.get('low', item.get('l', 0))),
                        close_price=float(item.get('close', item.get('c', 0))),
                        volume=float(item.get('volume', item.get('v', 0)))
                    )
                    data_points.append(data_point)
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Skipping invalid item: {e}")
                    continue
            
            self.logger.info(f"Loaded {len(data_points)} data points from {filepath}")
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error loading JSON file: {e}")
            return []
    
    @staticmethod
    def _parse_datetime(date_string: Any) -> datetime:
        """Parse various date string formats."""
        if isinstance(date_string, datetime):
            return date_string
        
        if isinstance(date_string, (int, float)):
            return datetime.fromtimestamp(date_string)
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_string), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Cannot parse date: {date_string}")

class DataValidator:
    """
    Data validator for quality checks.
    數據驗證器進行品質檢查。
    
    Validates data integrity, completeness, and consistency.
    """
    
    def __init__(self):
        """Initialize data validator."""
        self.logger = logging.getLogger(f"{__name__}.DataValidator")
        self.validation_report: Dict[str, Any] = {}
        
    def validate(self, data_points: List[DataPoint]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a list of data points.
        
        驗證數據點列表。
        
        Args:
            data_points: List of DataPoint objects
            
        Returns:
            Tuple of (is_valid, report_dict)
        """
        report = {
            'total_points': len(data_points),
            'valid_points': 0,
            'issues': [],
            'statistics': {}
        }
        
        if not data_points:
            report['issues'].append('No data points provided')
            return False, report
        
        valid_points = []
        
        for i, point in enumerate(data_points):
            try:
                if self._validate_point(point):
                    valid_points.append(point)
            except Exception as e:
                report['issues'].append(f"Point {i}: {str(e)}")
        
        report['valid_points'] = len(valid_points)
        
        # Check for temporal consistency
        if valid_points:
            temporal_issues = self._check_temporal_order(valid_points)
            if temporal_issues:
                report['issues'].extend(temporal_issues)
        
        # Calculate statistics
        if valid_points:
            report['statistics'] = self._calculate_statistics(valid_points)
        
        is_valid = len(report['issues']) == 0
        self.logger.info(f"Validation complete: {len(valid_points)}/{len(data_points)} valid")
        
        return is_valid, report
    
    @staticmethod
    def _validate_point(point: DataPoint) -> bool:
        """Validate individual data point."""
        if not point.symbol:
            raise ValueError("Symbol is required")
        
        if point.open_price < 0 or point.high_price < 0 or \
           point.low_price < 0 or point.close_price < 0:
            raise ValueError("Prices cannot be negative")
        
        if point.high_price < point.low_price:
            raise ValueError("High price is lower than low price")
        
        if not (point.low_price <= point.close_price <= point.high_price):
            raise ValueError("Close price not within high-low range")
        
        if point.volume < 0:
            raise ValueError("Volume cannot be negative")
        
        return True
    
    @staticmethod
    def _check_temporal_order(points: List[DataPoint]) -> List[str]:
        """Check if data points are in chronological order."""
        issues = []
        
        for i in range(1, len(points)):
            if points[i].timestamp < points[i-1].timestamp:
                issues.append(f"Temporal disorder at position {i}")
                break
        
        return issues
    
    @staticmethod
    def _calculate_statistics(points: List[DataPoint]) -> Dict[str, Any]:
        """Calculate data statistics."""
        closes = [p.close_price for p in points]
        volumes = [p.volume for p in points]
        
        return {
            'price_range': (min(closes), max(closes)),
            'avg_price': np.mean(closes),
            'std_price': np.std(closes),
            'total_volume': sum(volumes),
            'avg_volume': np.mean(volumes),
            'data_span': (points[0].timestamp, points[-1].timestamp)
        }

class DataCache:
    """
    Cache for historical data to avoid repeated file I/O.
    歷史數據緩存以避免重複的文件 I/O。
    
    Stores data in memory and optionally persists to disk.
    """
    
    def __init__(
        self,
        cache_dir: str = '.cache',
        ttl_hours: int = 24,
        max_cache_size: int = 1000
    ):
        """
        Initialize data cache.
        
        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time to live for cached data
            max_cache_size: Maximum number of cache entries
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.max_cache_size = max_cache_size
        self.memory_cache: Dict[str, Tuple[List[DataPoint], datetime]] = {}
        self.logger = logging.getLogger(f"{__name__}.DataCache")
        
    def get(self, key: str) -> Optional[List[DataPoint]]:
        """
        Get data from cache.
        
        從緩存獲取數據。
        
        Args:
            key: Cache key
            
        Returns:
            Cached DataPoint list or None if expired/not found
        """
        # Check memory cache
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if datetime.now() - timestamp < self.ttl:
                self.logger.debug(f"Cache hit (memory): {key}")
                return data
            else:
                del self.memory_cache[key]
        
        # Check disk cache
        cached_data = self._load_from_disk(key)
        if cached_data:
            self.logger.debug(f"Cache hit (disk): {key}")
            self.memory_cache[key] = (cached_data, datetime.now())
            return cached_data
        
        return None
    
    def put(self, key: str, data: List[DataPoint], persist: bool = True) -> None:
        """
        Put data in cache.
        
        將數據放入緩存。
        
        Args:
            key: Cache key
            data: DataPoint list
            persist: Whether to persist to disk
        """
        # Check cache size
        if len(self.memory_cache) >= self.max_cache_size:
            oldest_key = min(self.memory_cache.keys(),
                           key=lambda k: self.memory_cache[k][1])
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = (data, datetime.now())
        
        if persist:
            self._save_to_disk(key, data)
        
        self.logger.debug(f"Data cached: {key}")
    
    def clear(self) -> None:
        """Clear all caches."""
        self.memory_cache.clear()
        self.logger.info("Cache cleared")
    
    def _load_from_disk(self, key: str) -> Optional[List[DataPoint]]:
        """Load data from disk cache."""
        cache_file = self.cache_dir / f"{self._hash_key(key)}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                self.logger.error(f"Error loading from disk cache: {e}")
        
        return None
    
    def _save_to_disk(self, key: str, data: List[DataPoint]) -> None:
        """Save data to disk cache."""
        cache_file = self.cache_dir / f"{self._hash_key(key)}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error saving to disk cache: {e}")
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Generate hash for cache key."""
        return hashlib.md5(key.encode()).hexdigest()

class FeatureExtractor:
    """
    Feature extractor for technical indicators.
    技術指標的特徵提取器。
    
    Calculates various technical indicators like SMA, RSI, MACD, etc.
    """
    
    def __init__(self):
        """Initialize feature extractor."""
        self.logger = logging.getLogger(f"{__name__}.FeatureExtractor")
        
    def extract_features(
        self,
        data_points: List[DataPoint],
        indicators: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract technical indicators from data points.
        
        從數據點提取技術指標。
        
        Args:
            data_points: List of DataPoint objects
            indicators: List of indicator names to calculate
            
        Returns:
            List of dictionaries with extracted features
        """
        if not indicators:
            indicators = ['sma_short', 'sma_long', 'rsi', 'macd']
        
        features = []
        closes = np.array([p.close_price for p in data_points])
        
        for i, point in enumerate(data_points):
            feature_dict = {'timestamp': point.timestamp.isoformat()}
            
            if 'sma_short' in indicators and i >= 19:
                feature_dict['sma_short'] = float(np.mean(closes[i-19:i+1]))
            
            if 'sma_long' in indicators and i >= 49:
                feature_dict['sma_long'] = float(np.mean(closes[i-49:i+1]))
            
            if 'rsi' in indicators and i >= 13:
                feature_dict['rsi'] = self._calculate_rsi(closes[:i+1])
            
            if 'macd' in indicators and i >= 25:
                macd, signal = self._calculate_macd(closes[:i+1])
                feature_dict['macd'] = macd
                feature_dict['macd_signal'] = signal
            
            if 'volatility' in indicators and i >= 20:
                feature_dict['volatility'] = float(np.std(closes[i-19:i+1]))
            
            features.append(feature_dict)
        
        self.logger.info(f"Extracted {len(features)} feature sets")
        return features
    
    @staticmethod
    def _calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index (RSI)."""
        if len(prices) < period + 1:
            return 0.5
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 1.0 if avg_gain > 0 else 0.5
        
        rs = avg_gain / avg_loss
        rsi = 1.0 - (1.0 / (1.0 + rs))
        
        return float(np.clip(rsi, 0, 1))
    
    @staticmethod
    def _calculate_macd(
        prices: np.ndarray,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[float, float]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if len(prices) < slow:
            return 0.0, 0.0
        
        ema_fast = FeatureExtractor._calculate_ema(prices, fast)
        ema_slow = FeatureExtractor._calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        
        macd_values = []
        for i in range(len(prices) - slow):
            fast_ema = FeatureExtractor._calculate_ema(prices[:i+slow], fast)
            slow_ema = FeatureExtractor._calculate_ema(prices[:i+slow], slow)
            macd_values.append(fast_ema - slow_ema)
        
        if len(macd_values) >= signal:
            signal_line = np.mean(macd_values[-signal:])
        else:
            signal_line = 0.0
        
        return float(macd_line), float(signal_line)
    
    @staticmethod
    def _calculate_ema(prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average (EMA)."""
        if len(prices) == 0:
            return 0.0
        
        multiplier = 2.0 / (period + 1)
        ema = float(np.mean(prices[:period]))
        
        for price in prices[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return float(ema)

# Module exports
__all__ = [
    'DataPoint',
    'DataLoader',
    'DataValidator',
    'DataCache',
    'FeatureExtractor'
]
