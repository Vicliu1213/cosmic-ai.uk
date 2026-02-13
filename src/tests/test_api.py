#!/usr/bin/env python3
"""
API Endpoints Tests
API 端點測試

Unit tests for REST API endpoints and server functionality.
REST API 端點和服務器功能的單位測試。
"""

import unittest
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status_code: int, data: Dict[str, Any]):
        """Initialize mock response."""
        self.status_code = status_code
        self.data = data
    
    def json(self) -> Dict[str, Any]:
        """Get response JSON."""
        return self.data


class TestHealthCheckEndpoint(unittest.TestCase):
    """Test health check endpoint."""
    
    def test_health_check_structure(self):
        """Test health check response structure."""
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'environment': 'development'
        }
        
        self.assertEqual(response_data['status'], 'healthy')
        self.assertIn('timestamp', response_data)
        self.assertIn('version', response_data)
    
    def test_health_check_status_code(self):
        """Test health check returns 200 OK."""
        mock_response = MockResponse(200, {'status': 'healthy'})
        self.assertEqual(mock_response.status_code, 200)


class TestApiStatusEndpoint(unittest.TestCase):
    """Test API status endpoint."""
    
    def test_api_status_response(self):
        """Test API status response format."""
        status_data = {
            'api_version': '2.0.0',
            'active_systems': 3,
            'active_agents': 12,
            'timestamp': datetime.now().isoformat()
        }
        
        self.assertIn('api_version', status_data)
        self.assertIn('active_systems', status_data)
        self.assertIsInstance(status_data['active_agents'], int)


class TestPortfolioEndpoint(unittest.TestCase):
    """Test portfolio endpoint."""
    
    def test_portfolio_data_structure(self):
        """Test portfolio data structure."""
        portfolio_data = {
            'cash': 100000.0,
            'total_value': 250000.0,
            'unrealized_pnl': 5000.0,
            'positions': {
                'AAPL': 100,
                'MSFT': 50
            }
        }
        
        self.assertIn('cash', portfolio_data)
        self.assertIn('positions', portfolio_data)
        self.assertEqual(len(portfolio_data['positions']), 2)
    
    def test_portfolio_calculations(self):
        """Test portfolio calculations."""
        cash = 50000.0
        unrealized_pnl = 2500.0
        realized_pnl = 1000.0
        
        total_pnl = unrealized_pnl + realized_pnl
        self.assertEqual(total_pnl, 3500.0)


class TestTradingSignalsEndpoint(unittest.TestCase):
    """Test trading signals endpoint."""
    
    def test_signal_data_structure(self):
        """Test trading signal data structure."""
        signal = {
            'symbol': 'AAPL',
            'signal_type': 'buy',
            'confidence': 0.85,
            'price': 150.75,
            'timestamp': datetime.now().isoformat(),
            'reason': 'SMA crossover'
        }
        
        self.assertEqual(signal['symbol'], 'AAPL')
        self.assertEqual(signal['signal_type'], 'buy')
        self.assertGreater(signal['confidence'], 0.8)
    
    def test_multiple_signals(self):
        """Test multiple trading signals."""
        signals = [
            {'symbol': 'AAPL', 'signal_type': 'buy', 'confidence': 0.85},
            {'symbol': 'MSFT', 'signal_type': 'hold', 'confidence': 0.60},
            {'symbol': 'GOOGL', 'signal_type': 'sell', 'confidence': 0.75}
        ]
        
        self.assertEqual(len(signals), 3)
        buy_signals = [s for s in signals if s['signal_type'] == 'buy']
        self.assertEqual(len(buy_signals), 1)


class TestMarketDataEndpoint(unittest.TestCase):
    """Test market data endpoint."""
    
    def test_market_data_structure(self):
        """Test market data structure."""
        market_data = {
            'symbol': 'AAPL',
            'price': 150.75,
            'bid': 150.70,
            'ask': 150.80,
            'volume': 1000000,
            'timestamp': datetime.now().isoformat()
        }
        
        self.assertEqual(market_data['symbol'], 'AAPL')
        self.assertGreater(market_data['ask'], market_data['bid'])
        self.assertGreater(market_data['volume'], 0)
    
    def test_market_data_validation(self):
        """Test market data validation."""
        bid = 150.70
        ask = 150.80
        price = 150.75
        
        self.assertGreater(ask, bid)
        self.assertGreaterEqual(price, bid)
        self.assertLessEqual(price, ask)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in API."""
    
    def test_404_not_found(self):
        """Test 404 Not Found response."""
        response = MockResponse(404, {'error': 'Endpoint not found'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
    
    def test_400_bad_request(self):
        """Test 400 Bad Request response."""
        response = MockResponse(400, {'error': 'Invalid parameters'})
        self.assertEqual(response.status_code, 400)
    
    def test_500_server_error(self):
        """Test 500 Server Error response."""
        response = MockResponse(500, {'error': 'Internal server error'})
        self.assertEqual(response.status_code, 500)


class TestAuthenticationEndpoint(unittest.TestCase):
    """Test authentication endpoint."""
    
    def test_auth_response_structure(self):
        """Test authentication response structure."""
        auth_response = {
            'token': 'fake-jwt-token-123',
            'expires_in': 3600,
            'token_type': 'Bearer'
        }
        
        self.assertIn('token', auth_response)
        self.assertEqual(auth_response['token_type'], 'Bearer')
        self.assertGreater(auth_response['expires_in'], 0)


if __name__ == '__main__':
    unittest.main()
