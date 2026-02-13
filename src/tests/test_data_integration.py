#!/usr/bin/env python3
"""
Data Integration Module Tests
數據整合模組測試
"""

import unittest
import asyncio
from datetime import datetime, timedelta
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from opencode.data_integration import (
    DataFormat, OHLCV, DataLoader, DataBuffer,
    DataAnalyzer, DataManager
)


class TestDataFormat(unittest.TestCase):
    """Test data format enumeration."""
    
    def test_ohlcv_format(self):
        """Test OHLCV format."""
        self.assertEqual(DataFormat.OHLCV.value, "ohlcv")
    
    def test_csv_format(self):
        """Test CSV format."""
        self.assertEqual(DataFormat.CSV.value, "csv")


class TestOHLCV(unittest.TestCase):
    """Test OHLCV data structure."""
    
    def test_ohlcv_creation(self):
        """Test creating OHLCV data."""
        ohlcv = OHLCV(
            timestamp=datetime.now(),
            symbol="BTC/USD",
            open=50000.0,
            high=50500.0,
            low=49500.0,
            close=50100.0,
            volume=1000.0
        )
        
        self.assertEqual(ohlcv.open, 50000.0)
        self.assertEqual(ohlcv.close, 50100.0)
    
    def test_ohlcv_to_dict(self):
        """Test OHLCV conversion to dict."""
        ohlcv = OHLCV(
            timestamp=datetime.now(),
            symbol="BTC/USD",
            open=50000.0,
            high=50500.0,
            low=49500.0,
            close=50100.0,
            volume=1000.0
        )
        
        data_dict = ohlcv.to_dict()
        self.assertIn('open', data_dict)
        self.assertIn('close', data_dict)


class TestDataLoader(unittest.TestCase):
    """Test data loading functionality."""
    
    def test_generate_mock_data(self):
        """Test generating mock OHLCV data."""
        data = DataLoader.generate_mock_data("BTC/USD", num_records=50)
        self.assertEqual(len(data), 50)
        self.assertEqual(data[0].symbol, "BTC/USD")


class TestDataBuffer(unittest.TestCase):
    """Test data buffer functionality."""
    
    def test_buffer_initialization(self):
        """Test buffer initialization."""
        buffer = DataBuffer(max_size=100)
        self.assertEqual(buffer.max_size, 100)
    
    def test_add_data_to_buffer(self):
        """Test adding data to buffer."""
        buffer = DataBuffer(max_size=100)
        ohlcv = OHLCV(
            timestamp=datetime.now(),
            symbol="BTC/USD",
            open=50000.0,
            high=50500.0,
            low=49500.0,
            close=50100.0,
            volume=1000.0
        )
        
        buffer.add_data(ohlcv)
        self.assertEqual(len(buffer.buffer.get("BTC/USD", [])), 1)


class TestDataAnalyzer(unittest.TestCase):
    """Test data analysis functionality."""
    
    def setUp(self):
        """Set up analyzer with test data."""
        self.analyzer = DataAnalyzer()
        self.test_data = DataLoader.generate_mock_data("BTC/USD", num_records=100)
    
    def test_calculate_sma(self):
        """Test simple moving average calculation."""
        sma_results = self.analyzer.calculate_sma(self.test_data, period=5)
        self.assertGreater(len(sma_results), 0)
    
    def test_calculate_ema(self):
        """Test exponential moving average calculation."""
        ema_results = self.analyzer.calculate_ema(self.test_data, period=5)
        self.assertGreater(len(ema_results), 0)
    
    def test_calculate_rsi(self):
        """Test RSI calculation."""
        rsi_results = self.analyzer.calculate_rsi(self.test_data, period=14)
        self.assertGreater(len(rsi_results), 0)
    
    def test_get_price_stats(self):
        """Test price statistics."""
        stats = self.analyzer.get_price_stats(self.test_data)
        self.assertIn('min', stats)
        self.assertIn('max', stats)


class TestDataManager(unittest.TestCase):
    """Test data manager functionality."""
    
    def setUp(self):
        """Set up data manager."""
        self.manager = DataManager()
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager.buffer)
        self.assertIsNotNone(self.manager.analyzer)
    
    def test_load_mock_data(self):
        """Test loading mock data."""
        async def load():
            await self.manager.load_mock_data("BTC/USD")
            self.assertIn("BTC/USD", self.manager.buffer.buffer)
        
        asyncio.run(load())


if __name__ == '__main__':
    unittest.main()
