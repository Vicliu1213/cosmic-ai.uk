#!/usr/bin/env python3
"""
Exchange API Integration Tests
交易所 API 整合測試

Tests for trading API connectors:
- Binance API order submission and management
- Kraken API order submission and management
- Coinbase API order submission and management
- Market data retrieval
- Order lifecycle (place, check status, cancel)
"""

import unittest
import asyncio
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.phase5.exchange_connector import (
    ExchangeType, TradingMode, ExchangeConfig, ExchangeConnectorFactory,
    BinanceConnector, KrakenConnector, CoinbaseConnector,
    ConnectionStatus, ConnectionResult, AccountBalance
)


class TestBinanceConnector(unittest.TestCase):
    """Test Binance exchange connector."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ExchangeConfig(
            exchange_type=ExchangeType.BINANCE,
            api_key="test_key",
            api_secret="test_secret",
            mode=TradingMode.TESTNET,
            testnet=True
        )
        self.connector = BinanceConnector(self.config)

    def test_connector_initialization(self):
        """Test connector initialization."""
        self.assertIsNotNone(self.connector)
        self.assertEqual(self.connector.config.exchange_type, ExchangeType.BINANCE)
        self.assertEqual(self.connector.config.mode, TradingMode.TESTNET)

    def test_get_base_url_testnet(self):
        """Test testnet URL generation."""
        url = self.connector._get_base_url()
        self.assertEqual(url, "https://testnet.binance.vision/api")

    def test_get_base_url_live(self):
        """Test live URL generation."""
        live_config = ExchangeConfig(
            exchange_type=ExchangeType.BINANCE,
            api_key="test_key",
            api_secret="test_secret",
            testnet=False,
            sandbox=False
        )
        live_connector = BinanceConnector(live_config)
        url = live_connector._get_base_url()
        self.assertEqual(url, "https://api.binance.com/api")

    def test_signature_generation(self):
        """Test HMAC signature generation."""
        params = {"key1": "value1", "key2": "value2"}
        signature = self.connector._get_signature(params)
        self.assertIsNotNone(signature)
        self.assertTrue(len(signature) > 0)
        # Signature should be hexadecimal
        self.assertTrue(all(c in '0123456789abcdef' for c in signature))

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_get_ticker(self, mock_session_class):
        """Test ticker retrieval."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "symbol": "BTCUSDT",
            "price": "50000.00"
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.get_ticker("BTCUSDT")
        self.assertIsNotNone(result)
        if result:
            self.assertIn("symbol", result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_get_order_book(self, mock_session_class):
        """Test order book retrieval."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "bids": [["50000", "1.0"]],
            "asks": [["50001", "1.0"]]
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.get_order_book("BTCUSDT")
        self.assertIsNotNone(result)
        if result:
            self.assertIn("bids", result)
            self.assertIn("asks", result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_place_limit_order(self, mock_session_class):
        """Test limit order placement."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "orderId": "12345",
            "symbol": "BTCUSDT",
            "status": "NEW"
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.place_limit_order(
            "BTCUSDT", "BUY", 0.1, 50000.0
        )
        self.assertIsNotNone(result)
        if result:
            self.assertIn("orderId", result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_place_market_order(self, mock_session_class):
        """Test market order placement."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "orderId": "12346",
            "symbol": "BTCUSDT",
            "status": "FILLED"
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.place_market_order("BTCUSDT", "SELL", 0.1)
        self.assertIsNotNone(result)
        if result:
            self.assertIn("orderId", result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_cancel_order(self, mock_session_class):
        """Test order cancellation."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "orderId": "12345",
            "status": "CANCELED"
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.delete.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.cancel_order("BTCUSDT", order_id="12345")
        self.assertIsNotNone(result)
        if result:
            self.assertIn("status", result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_get_order_status(self, mock_session_class):
        """Test order status retrieval."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "orderId": "12345",
            "status": "PARTIALLY_FILLED",
            "executedQty": "0.05"
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.get_order_status("BTCUSDT", order_id="12345")
        self.assertIsNotNone(result)
        if result:
            self.assertIn("status", result)


class TestKrakenConnector(unittest.TestCase):
    """Test Kraken exchange connector."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ExchangeConfig(
            exchange_type=ExchangeType.KRAKEN,
            api_key="test_key",
            api_secret="test_secret",
            mode=TradingMode.LIVE
        )
        self.connector = KrakenConnector(self.config)

    def test_connector_initialization(self):
        """Test connector initialization."""
        self.assertIsNotNone(self.connector)
        self.assertEqual(self.connector.config.exchange_type, ExchangeType.KRAKEN)

    def test_get_base_url(self):
        """Test base URL."""
        url = self.connector._get_base_url()
        self.assertEqual(url, "https://api.kraken.com")

    def test_kraken_signature_generation(self):
        """Test Kraken signature generation."""
        import base64
        # Kraken expects base64-encoded secret
        secret = base64.b64encode(b"test_secret").decode()
        config = ExchangeConfig(
            exchange_type=ExchangeType.KRAKEN,
            api_key="test_key",
            api_secret=secret
        )
        connector = KrakenConnector(config)
        
        urlpath = "/0/private/Balance"
        data = {"nonce": "1234567890"}
        nonce = "1234567890"

        signature = connector._get_kraken_signature(urlpath, data, nonce)
        self.assertIsNotNone(signature)
        self.assertTrue(len(signature) > 0)
        # Kraken signatures are base64 encoded
        try:
            base64.b64decode(signature)
            # If we get here, it's valid base64
        except Exception:
            self.fail("Kraken signature is not valid base64")

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_place_limit_order(self, mock_session_class):
        """Test Kraken limit order placement."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": [],
            "result": {
                "descr": {
                    "order": "buy 1 XXBTZUSD @ limit 50000.0"
                },
                "txid": ["OQCLNL-XXXXX-XXXXX"]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.place_limit_order(
            "XXBTZUSD", "buy", 1.0, 50000.0
        )
        self.assertIsNotNone(result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_place_market_order(self, mock_session_class):
        """Test Kraken market order placement."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": [],
            "result": {
                "descr": {
                    "order": "sell 1 XXBTZUSD @ market"
                },
                "txid": ["OQCLNL-XXXXX-XXXXX"]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.place_market_order(
            "XXBTZUSD", "sell", 1.0
        )
        self.assertIsNotNone(result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_cancel_order(self, mock_session_class):
        """Test Kraken order cancellation."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": [],
            "result": {
                "count": 1
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.cancel_order("OQCLNL-XXXXX-XXXXX")
        self.assertIsNotNone(result)


class TestCoinbaseConnector(unittest.TestCase):
    """Test Coinbase exchange connector."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ExchangeConfig(
            exchange_type=ExchangeType.COINBASE,
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_passphrase",
            mode=TradingMode.LIVE,
            sandbox=True
        )
        self.connector = CoinbaseConnector(self.config)

    def test_connector_initialization(self):
        """Test connector initialization."""
        self.assertIsNotNone(self.connector)
        self.assertEqual(self.connector.config.exchange_type, ExchangeType.COINBASE)

    def test_get_base_url_sandbox(self):
        """Test sandbox URL."""
        url = self.connector._get_base_url()
        self.assertEqual(url, "https://api-sandbox.coinbase.com")

    def test_get_base_url_live(self):
        """Test live URL."""
        live_config = ExchangeConfig(
            exchange_type=ExchangeType.COINBASE,
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_passphrase",
            sandbox=False
        )
        live_connector = CoinbaseConnector(live_config)
        url = live_connector._get_base_url()
        self.assertEqual(url, "https://api.coinbase.com")

    def test_coinbase_signature_generation(self):
        """Test Coinbase signature generation."""
        timestamp, signature, key_id = self.connector._get_coinbase_signature(
            "GET", "/api/v3/brokerage/accounts"
        )
        self.assertIsNotNone(timestamp)
        self.assertIsNotNone(signature)
        self.assertEqual(key_id, "test_key")
        # Timestamp should be numeric
        self.assertTrue(timestamp.isdigit())

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_place_limit_order(self, mock_session_class):
        """Test Coinbase limit order placement."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "failure_reason": "success",
            "order_id": "00000000-0000-0000-0000-000000000000",
            "client_order_id": "order-123",
            "product_id": "BTC-USD",
            "side": "BUY",
            "order_type": "LIMIT"
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.place_limit_order(
            "BTC-USD", "BUY", 0.1, 50000.0
        )
        self.assertIsNotNone(result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_place_market_order(self, mock_session_class):
        """Test Coinbase market order placement."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "failure_reason": "success",
            "order_id": "00000000-0000-0000-0000-000000000000",
            "product_id": "BTC-USD",
            "side": "SELL",
            "order_type": "MARKET"
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.place_market_order("BTC-USD", "SELL", 0.1)
        self.assertIsNotNone(result)

    @patch('src.phase5.exchange_connector.requests.Session')
    async def test_cancel_order(self, mock_session_class):
        """Test Coinbase order cancellation."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "success": True,
                    "cancel_reason": "user_requested",
                    "order_id": "00000000-0000-0000-0000-000000000000"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.post.return_value = mock_response
        self.connector.session = mock_session

        result = await self.connector.cancel_order("00000000-0000-0000-0000-000000000000")
        self.assertIsNotNone(result)


class TestExchangeConnectorFactory(unittest.TestCase):
    """Test exchange connector factory."""

    def test_binance_creation(self):
        """Test Binance connector creation."""
        config = ExchangeConfig(
            exchange_type=ExchangeType.BINANCE,
            api_key="test_key",
            api_secret="test_secret"
        )
        connector = ExchangeConnectorFactory.create(config)
        self.assertIsInstance(connector, BinanceConnector)

    def test_kraken_creation(self):
        """Test Kraken connector creation."""
        config = ExchangeConfig(
            exchange_type=ExchangeType.KRAKEN,
            api_key="test_key",
            api_secret="test_secret"
        )
        connector = ExchangeConnectorFactory.create(config)
        self.assertIsInstance(connector, KrakenConnector)

    def test_coinbase_creation(self):
        """Test Coinbase connector creation."""
        config = ExchangeConfig(
            exchange_type=ExchangeType.COINBASE,
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_passphrase"
        )
        connector = ExchangeConnectorFactory.create(config)
        self.assertIsInstance(connector, CoinbaseConnector)

    def test_unsupported_exchange(self):
        """Test unsupported exchange raises error."""
        from enum import Enum
        
        class FakeExchange(Enum):
            UNSUPPORTED = "unsupported"
        
        config = Mock()
        config.exchange_type = "unsupported"
        
        # This should fail because unsupported is not an ExchangeType
        with self.assertRaises((ValueError, AttributeError)):
            ExchangeConnectorFactory.create(config)


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality."""

    async def async_test_rate_limit_check(self):
        """Test rate limit checking."""
        config = ExchangeConfig(
            exchange_type=ExchangeType.BINANCE,
            api_key="test_key",
            api_secret="test_secret",
            rate_limit_per_minute=2
        )
        connector = BinanceConnector(config)

        # Initial check should pass
        result1 = await connector.check_rate_limit()
        self.assertTrue(result1)

        # Second check should pass
        result2 = await connector.check_rate_limit()
        self.assertTrue(result2)

        # Third check should fail (limit is 2)
        result3 = await connector.check_rate_limit()
        self.assertFalse(result3)

    def test_rate_limiting(self):
        """Test rate limiting with async wrapper."""
        asyncio.run(self.async_test_rate_limit_check())


class TestOrderDataStructures(unittest.TestCase):
    """Test order-related data structures."""

    def test_exchange_config(self):
        """Test ExchangeConfig data class."""
        config = ExchangeConfig(
            exchange_type=ExchangeType.BINANCE,
            api_key="key123",
            api_secret="secret456"
        )
        self.assertEqual(config.exchange_type, ExchangeType.BINANCE)
        self.assertEqual(config.api_key, "key123")
        self.assertEqual(config.mode, TradingMode.TESTNET)

    def test_connection_result(self):
        """Test ConnectionResult data class."""
        result = ConnectionResult(
            success=True,
            status=ConnectionStatus.CONNECTED,
            exchange=ExchangeType.BINANCE,
            timestamp=datetime.utcnow(),
            message="Connected successfully"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.status, ConnectionStatus.CONNECTED)

    def test_account_balance(self):
        """Test AccountBalance data class."""
        balance = AccountBalance(
            exchange=ExchangeType.BINANCE,
            timestamp=datetime.utcnow(),
            total_balance=1000.0,
            available_balance=800.0,
            locked_balance=200.0,
            balances={"BTC": {"available": 0.5, "locked": 0.0}}
        )
        self.assertEqual(balance.total_balance, 1000.0)
        self.assertIn("BTC", balance.balances)


if __name__ == "__main__":
    unittest.main()
