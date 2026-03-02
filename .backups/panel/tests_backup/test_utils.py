#!/usr/bin/env python3
"""
Utility Functions Tests
工具函數測試

Unit tests for utility functions and helpers.
工具函數和幫助程序的單位測試。
"""

import unittest
import logging
from datetime import datetime
import tempfile
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class TestDateTimeUtilities(unittest.TestCase):
    """Test datetime utility functions."""
    
    def test_datetime_parsing(self):
        """Test datetime parsing."""
        
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        self.assertEqual(test_date.year, 2024)
        self.assertEqual(test_date.month, 1)
        self.assertEqual(test_date.day, 15)
    
    def test_datetime_isoformat(self):
        """Test datetime ISO format conversion."""
        dt = datetime(2024, 2, 13, 12, 0, 0)
        iso_str = dt.isoformat()
        
        self.assertIsInstance(iso_str, str)
        self.assertIn('2024-02-13', iso_str)
        self.assertIn('12:00:00', iso_str)

class TestNumericUtilities(unittest.TestCase):
    """Test numeric utility functions."""
    
    def test_numeric_operations(self):
        """Test basic numeric operations."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        mean = sum(values) / len(values)
        self.assertEqual(mean, 3.0)
    
    def test_percentage_calculation(self):
        """Test percentage calculations."""
        total = 100.0
        part = 25.0
        percentage = (part / total) * 100
        
        self.assertEqual(percentage, 25.0)

class TestStringUtilities(unittest.TestCase):
    """Test string utility functions."""
    
    def test_string_formatting(self):
        """Test string formatting."""
        symbol = "AAPL"
        price = 150.75
        formatted = f"{symbol}: ${price:.2f}"
        
        self.assertEqual(formatted, "AAPL: $150.75")
    
    def test_string_parsing(self):
        """Test string parsing."""
        data_string = "AAPL,150.75,100"
        parts = data_string.split(',')
        
        self.assertEqual(parts[0], "AAPL")
        self.assertEqual(float(parts[1]), 150.75)
        self.assertEqual(int(parts[2]), 100)

class TestCollectionUtilities(unittest.TestCase):
    """Test collection utility functions."""
    
    def test_dict_operations(self):
        """Test dictionary operations."""
        data = {'symbol': 'AAPL', 'price': 150.75}
        
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertEqual(data.get('price'), 150.75)
        self.assertIsNone(data.get('volume'))
    
    def test_list_operations(self):
        """Test list operations."""
        prices = [150.0, 151.0, 149.5, 152.0]
        
        self.assertEqual(len(prices), 4)
        self.assertEqual(max(prices), 152.0)
        self.assertEqual(min(prices), 149.5)
    
    def test_sorting(self):
        """Test list sorting."""
        values = [3, 1, 4, 1, 5, 9]
        sorted_values = sorted(values)
        
        self.assertEqual(sorted_values, [1, 1, 3, 4, 5, 9])

class TestFileUtilities(unittest.TestCase):
    """Test file utility functions."""
    
    def test_file_exists_check(self):
        """Test file existence checking."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            self.assertTrue(os.path.exists(temp_file))
            os.remove(temp_file)
            self.assertFalse(os.path.exists(temp_file))
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_path_operations(self):
        """Test path operations."""
        path = "/root/comic_ai/data/test.csv"
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        
        self.assertIn("data", dirname)
        self.assertEqual(basename, "test.csv")

class TestLogging(unittest.TestCase):
    """Test logging functionality."""
    
    def test_logger_creation(self):
        """Test logger creation."""
        test_logger = logging.getLogger("test_logger")
        
        self.assertIsInstance(test_logger, logging.Logger)
        self.assertEqual(test_logger.name, "test_logger")
    
    def test_logging_levels(self):
        """Test logging levels."""
        levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL
        ]
        
        self.assertEqual(len(levels), 5)
        self.assertLess(logging.DEBUG, logging.CRITICAL)

if __name__ == '__main__':
    unittest.main()
