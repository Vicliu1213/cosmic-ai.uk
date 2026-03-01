#!/usr/bin/env python3
"""
Exchange Connector Module
交易所連接器模組

Provides unified API connectivity for multiple crypto exchanges:
- Binance (Testnet/Live)
- Kraken
- Coinbase

This module handles:
1. Exchange connection initialization
2. API authentication
3. Connection health checking
4. Rate limiting
5. Error handling and recovery
6. Account balance retrieval
7. Trading capability verification
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import os
import json

import requests
import hashlib
import hmac
import base64
from urllib.parse import urlencode

# ============================================================================
# Constants & Enums
# ============================================================================

class ExchangeType(Enum):
    """Supported cryptocurrency exchanges."""
    BINANCE = "binance"
    KRAKEN = "kraken"
    COINBASE = "coinbase"


class ConnectionStatus(Enum):
    """Connection status indicators."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TESTING = "testing"
    RATE_LIMITED = "rate_limited"


class TradingMode(Enum):
    """Trading mode options."""
    TESTNET = "testnet"
    SANDBOX = "sandbox"
    PAPER = "paper"
    LIVE = "live"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ExchangeConfig:
    """Configuration for exchange connection."""
    exchange_type: ExchangeType
    api_key: str
    api_secret: str
    mode: TradingMode = TradingMode.TESTNET
    rate_limit_per_minute: int = 1200
    timeout_seconds: int = 30
    base_url: Optional[str] = None
    passphrase: Optional[str] = None  # Kraken/Coinbase specific
    testnet: bool = True
    sandbox: bool = True


@dataclass
class AccountBalance:
    """Account balance information."""
    exchange: ExchangeType
    timestamp: datetime
    total_balance: float
    available_balance: float
    locked_balance: float
    balances: Dict[str, Dict[str, float]] = field(default_factory=dict)  # {symbol: {available, locked}}


@dataclass
class ConnectionResult:
    """Result of connection attempt."""
    success: bool
    status: ConnectionStatus
    exchange: ExchangeType
    timestamp: datetime
    message: str
    error_details: Optional[str] = None
    response_time_ms: Optional[float] = None
    balance: Optional[AccountBalance] = None


@dataclass
class RateLimitInfo:
    """Rate limiting information."""
    exchange: ExchangeType
    limit_per_minute: int
    requests_made: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)
    is_limited: bool = False


# ============================================================================
# Base Exchange Connector
# ============================================================================

class BaseExchangeConnector(ABC):
    """Abstract base class for exchange connectors."""

    def __init__(self, config: ExchangeConfig):
        """Initialize exchange connector.
        
        Args:
            config: Exchange configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"ExchangeConnector.{config.exchange_type.value}")
        self.session: Optional[requests.Session] = None
        self.rate_limit = RateLimitInfo(
            exchange=config.exchange_type,
            limit_per_minute=config.rate_limit_per_minute
        )
        self.last_connection_time: Optional[datetime] = None
        self.last_error: Optional[str] = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_async()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.disconnect()

    def connect(self) -> bool:
        """Connect to exchange.
        
        Returns:
            True if connection successful
        """
        try:
            self.session = requests.Session()
            self._setup_session()
            self.logger.info(f"Connected to {self.config.exchange_type.value}")
            self.last_connection_time = datetime.utcnow()
            return True
        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Connection failed: {e}")
            return False

    async def connect_async(self) -> bool:
        """Async connection to exchange."""
        return await asyncio.to_thread(self.connect)

    def disconnect(self) -> None:
        """Disconnect from exchange."""
        if self.session:
            self.session.close()
            self.session = None
            self.logger.info(f"Disconnected from {self.config.exchange_type.value}")

    @abstractmethod
    def _setup_session(self) -> None:
        """Setup session headers and authentication."""
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        """Get base URL for exchange API."""
        pass

    @abstractmethod
    async def test_connection(self) -> ConnectionResult:
        """Test connection to exchange."""
        pass

    @abstractmethod
    async def get_balance(self) -> Optional[AccountBalance]:
        """Get account balance."""
        pass

    async def check_rate_limit(self) -> bool:
        """Check if rate limited.
        
        Returns:
            True if can make request, False if rate limited
        """
        now = datetime.utcnow()
        elapsed = (now - self.rate_limit.last_reset).total_seconds()

        if elapsed >= 60:
            self.rate_limit.requests_made = 0
            self.rate_limit.last_reset = now
            self.rate_limit.is_limited = False
            return True

        if self.rate_limit.requests_made >= self.rate_limit.limit_per_minute:
            self.rate_limit.is_limited = True
            wait_time = 60 - elapsed
            self.logger.warning(
                f"Rate limited on {self.config.exchange_type.value}. "
                f"Wait {wait_time:.1f}s"
            )
            return False

        self.rate_limit.requests_made += 1
        return True

    async def wait_for_rate_limit(self) -> None:
        """Wait until rate limit is available."""
        while not await self.check_rate_limit():
            await asyncio.sleep(1)


# ============================================================================
# Binance Exchange Connector
# ============================================================================

class BinanceConnector(BaseExchangeConnector):
    """Connector for Binance exchange (Testnet & Live)."""

    def _get_base_url(self) -> str:
        """Get Binance API base URL."""
        if self.config.testnet or self.config.sandbox:
            return "https://testnet.binance.vision/api"
        return "https://api.binance.com/api"

    def _setup_session(self) -> None:
        """Setup Binance session."""
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "CosmicAI-Trading-System/1.0"
        })

    def _get_signature(self, params: Dict[str, Any]) -> str:
        """Generate Binance API signature.
        
        Args:
            params: Request parameters
            
        Returns:
            HMAC SHA256 signature
        """
        query_string = urlencode(params)
        return hmac.new(
            self.config.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

    async def test_connection(self) -> ConnectionResult:
        """Test connection to Binance.
        
        Returns:
            ConnectionResult with test status
        """
        start_time = datetime.utcnow()
        try:
            await self.wait_for_rate_limit()

            response = self.session.get(
                f"{self._get_base_url()}/v3/ping",
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()

            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Get balance to verify authentication
            balance = await self.get_balance()

            return ConnectionResult(
                success=True,
                status=ConnectionStatus.CONNECTED,
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                message="Successfully connected to Binance",
                response_time_ms=response_time_ms,
                balance=balance
            )

        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Binance connection test failed: {e}")
            return ConnectionResult(
                success=False,
                status=ConnectionStatus.ERROR,
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                message=f"Connection test failed: {str(e)}",
                error_details=str(e)
            )

    async def get_balance(self) -> Optional[AccountBalance]:
        """Get account balance from Binance.
        
        Returns:
            AccountBalance or None if failed
        """
        try:
            await self.wait_for_rate_limit()

            timestamp = int(datetime.utcnow().timestamp() * 1000)
            params = {
                "timestamp": timestamp,
                "recvWindow": 5000
            }
            params["signature"] = self._get_signature(params)

            response = self.session.get(
                f"{self._get_base_url()}/v3/account",
                params=params,
                headers={"X-MBX-APIKEY": self.config.api_key},
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()

            total_balance = float(data.get("totalAssetOfBtc", 0))
            balances = {}
            available_balance = 0.0
            locked_balance = 0.0

            for balance in data.get("balances", []):
                symbol = balance["asset"]
                free = float(balance["free"])
                locked = float(balance["locked"])
                balances[symbol] = {"available": free, "locked": locked}
                available_balance += free
                locked_balance += locked

            return AccountBalance(
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                total_balance=total_balance,
                available_balance=available_balance,
                locked_balance=locked_balance,
                balances=balances
            )

        except Exception as e:
            self.logger.error(f"Failed to get Binance balance: {e}")
            return None


# ============================================================================
# Kraken Exchange Connector
# ============================================================================

class KrakenConnector(BaseExchangeConnector):
    """Connector for Kraken exchange."""

    def _get_base_url(self) -> str:
        """Get Kraken API base URL."""
        return "https://api.kraken.com"

    def _setup_session(self) -> None:
        """Setup Kraken session."""
        self.session.headers.update({
            "User-Agent": "CosmicAI-Trading-System/1.0"
        })

    def _get_kraken_signature(self, urlpath: str, data: Dict, nonce: str) -> str:
        """Generate Kraken API signature.
        
        Args:
            urlpath: API endpoint path
            data: Request data
            nonce: Nonce value
            
        Returns:
            Base64 encoded signature
        """
        postdata = urlencode(data)
        encoded = (str(nonce) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        signature = hmac.new(
            base64.b64decode(self.config.api_secret),
            message,
            hashlib.sha512
        )
        return base64.b64encode(signature.digest()).decode()

    async def test_connection(self) -> ConnectionResult:
        """Test connection to Kraken.
        
        Returns:
            ConnectionResult with test status
        """
        start_time = datetime.utcnow()
        try:
            await self.wait_for_rate_limit()

            response = self.session.get(
                f"{self._get_base_url()}/0/public/SystemStatus",
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()

            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Get balance to verify authentication
            balance = await self.get_balance()

            return ConnectionResult(
                success=True,
                status=ConnectionStatus.CONNECTED,
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                message="Successfully connected to Kraken",
                response_time_ms=response_time_ms,
                balance=balance
            )

        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Kraken connection test failed: {e}")
            return ConnectionResult(
                success=False,
                status=ConnectionStatus.ERROR,
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                message=f"Connection test failed: {str(e)}",
                error_details=str(e)
            )

    async def get_balance(self) -> Optional[AccountBalance]:
        """Get account balance from Kraken.
        
        Returns:
            AccountBalance or None if failed
        """
        try:
            await self.wait_for_rate_limit()

            nonce = str(int(datetime.utcnow().timestamp() * 1000))
            data = {"nonce": nonce}
            
            urlpath = "/0/private/Balance"
            signature = self._get_kraken_signature(urlpath, data, nonce)

            headers = {
                "API-Sign": signature,
                "API-Key": self.config.api_key
            }

            response = self.session.post(
                f"{self._get_base_url()}{urlpath}",
                headers=headers,
                data=data,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            result = response.json()

            if result.get("error"):
                self.logger.error(f"Kraken API error: {result['error']}")
                return None

            balances = result.get("result", {})
            total_balance = sum(float(v) for v in balances.values())
            available_balance = total_balance

            balance_dict = {k: {"available": float(v), "locked": 0.0}
                          for k, v in balances.items()}

            return AccountBalance(
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                total_balance=total_balance,
                available_balance=available_balance,
                locked_balance=0.0,
                balances=balance_dict
            )

        except Exception as e:
            self.logger.error(f"Failed to get Kraken balance: {e}")
            return None


# ============================================================================
# Coinbase Exchange Connector
# ============================================================================

class CoinbaseConnector(BaseExchangeConnector):
    """Connector for Coinbase Prime/Advanced Trade API."""

    def _get_base_url(self) -> str:
        """Get Coinbase API base URL."""
        if self.config.sandbox:
            return "https://api-sandbox.coinbase.com"
        return "https://api.coinbase.com"

    def _setup_session(self) -> None:
        """Setup Coinbase session."""
        self.session.headers.update({
            "User-Agent": "CosmicAI-Trading-System/1.0"
        })

    def _get_coinbase_signature(self, method: str, path: str, body: str = "") -> Tuple[str, str, str]:
        """Generate Coinbase API signature.
        
        Args:
            method: HTTP method
            path: API endpoint path
            body: Request body
            
        Returns:
            Tuple of (timestamp, signature, key_id)
        """
        import time
        timestamp = str(int(time.time()))
        message = timestamp + method + path + body
        
        signature = hmac.new(
            self.config.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.b64encode(signature).decode()
        return timestamp, signature_b64, self.config.api_key

    async def test_connection(self) -> ConnectionResult:
        """Test connection to Coinbase.
        
        Returns:
            ConnectionResult with test status
        """
        start_time = datetime.utcnow()
        try:
            await self.wait_for_rate_limit()

            response = self.session.get(
                f"{self._get_base_url()}/api/v3/brokerage/accounts",
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()

            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            return ConnectionResult(
                success=True,
                status=ConnectionStatus.CONNECTED,
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                message="Successfully connected to Coinbase",
                response_time_ms=response_time_ms
            )

        except Exception as e:
            self.last_error = str(e)
            self.logger.error(f"Coinbase connection test failed: {e}")
            return ConnectionResult(
                success=False,
                status=ConnectionStatus.ERROR,
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                message=f"Connection test failed: {str(e)}",
                error_details=str(e)
            )

    async def get_balance(self) -> Optional[AccountBalance]:
        """Get account balance from Coinbase.
        
        Returns:
            AccountBalance or None if failed
        """
        try:
            await self.wait_for_rate_limit()

            path = "/api/v3/brokerage/accounts"
            timestamp, signature, key_id = self._get_coinbase_signature("GET", path)

            headers = {
                "CB-ACCESS-KEY": self.config.api_key,
                "CB-ACCESS-SIGN": signature,
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-PASSPHRASE": self.config.passphrase or ""
            }

            response = self.session.get(
                f"{self._get_base_url()}{path}",
                headers=headers,
                timeout=self.config.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()

            total_balance = 0.0
            balances = {}
            available_balance = 0.0

            for account in data.get("accounts", []):
                symbol = account["currency"]
                balance_val = float(account["available_balance"]["value"])
                balances[symbol] = {"available": balance_val, "locked": 0.0}
                available_balance += balance_val
                total_balance += balance_val

            return AccountBalance(
                exchange=self.config.exchange_type,
                timestamp=datetime.utcnow(),
                total_balance=total_balance,
                available_balance=available_balance,
                locked_balance=0.0,
                balances=balances
            )

        except Exception as e:
            self.logger.error(f"Failed to get Coinbase balance: {e}")
            return None


# ============================================================================
# Exchange Connector Factory
# ============================================================================

class ExchangeConnectorFactory:
    """Factory for creating exchange connectors."""

    _connectors: Dict[ExchangeType, type] = {
        ExchangeType.BINANCE: BinanceConnector,
        ExchangeType.KRAKEN: KrakenConnector,
        ExchangeType.COINBASE: CoinbaseConnector,
    }

    @classmethod
    def create(cls, config: ExchangeConfig) -> BaseExchangeConnector:
        """Create exchange connector.
        
        Args:
            config: Exchange configuration
            
        Returns:
            Exchange connector instance
            
        Raises:
            ValueError: If exchange type not supported
        """
        connector_class = cls._connectors.get(config.exchange_type)
        if not connector_class:
            raise ValueError(f"Unsupported exchange: {config.exchange_type}")
        return connector_class(config)

    @classmethod
    def register(cls, exchange_type: ExchangeType, connector_class: type) -> None:
        """Register custom exchange connector.
        
        Args:
            exchange_type: Exchange type
            connector_class: Connector class
        """
        cls._connectors[exchange_type] = connector_class


# ============================================================================
# Multi-Exchange Manager
# ============================================================================

class MultiExchangeManager:
    """Manages connections to multiple exchanges."""

    def __init__(self):
        """Initialize multi-exchange manager."""
        self.logger = logging.getLogger("MultiExchangeManager")
        self.connectors: Dict[ExchangeType, BaseExchangeConnector] = {}
        self.connection_results: Dict[ExchangeType, ConnectionResult] = {}

    def add_exchange(self, config: ExchangeConfig) -> None:
        """Add exchange configuration.
        
        Args:
            config: Exchange configuration
        """
        connector = ExchangeConnectorFactory.create(config)
        self.connectors[config.exchange_type] = connector
        self.logger.info(f"Registered {config.exchange_type.value} connector")

    async def connect_all(self) -> Dict[ExchangeType, bool]:
        """Connect to all configured exchanges.
        
        Returns:
            Dict mapping exchange types to connection success status
        """
        results = {}
        tasks = []

        for exchange_type, connector in self.connectors.items():
            task = self._connect_and_test(exchange_type, connector)
            tasks.append(task)

        connection_results = await asyncio.gather(*tasks)
        for exchange_type, result in zip(self.connectors.keys(), connection_results):
            results[exchange_type] = result.success
            self.connection_results[exchange_type] = result

        return results

    async def _connect_and_test(
        self,
        exchange_type: ExchangeType,
        connector: BaseExchangeConnector
    ) -> ConnectionResult:
        """Connect and test single exchange.
        
        Args:
            exchange_type: Exchange type
            connector: Exchange connector
            
        Returns:
            Connection result
        """
        try:
            if not connector.connect():
                return ConnectionResult(
                    success=False,
                    status=ConnectionStatus.ERROR,
                    exchange=exchange_type,
                    timestamp=datetime.utcnow(),
                    message="Failed to establish connection"
                )

            result = await connector.test_connection()
            return result

        except Exception as e:
            self.logger.error(f"Error connecting to {exchange_type.value}: {e}")
            return ConnectionResult(
                success=False,
                status=ConnectionStatus.ERROR,
                exchange=exchange_type,
                timestamp=datetime.utcnow(),
                message=str(e),
                error_details=str(e)
            )

    async def get_all_balances(self) -> Dict[ExchangeType, Optional[AccountBalance]]:
        """Get balances from all connected exchanges.
        
        Returns:
            Dict mapping exchange types to balances
        """
        results = {}
        tasks = []

        for exchange_type, connector in self.connectors.items():
            task = connector.get_balance()
            tasks.append((exchange_type, task))

        for exchange_type, task in tasks:
            results[exchange_type] = await task

        return results

    def disconnect_all(self) -> None:
        """Disconnect from all exchanges."""
        for connector in self.connectors.values():
            connector.disconnect()
        self.logger.info("Disconnected from all exchanges")

    def get_connection_status(self) -> Dict[ExchangeType, str]:
        """Get connection status for all exchanges.
        
        Returns:
            Dict mapping exchange types to status
        """
        return {
            exchange_type: result.status.value
            for exchange_type, result in self.connection_results.items()
        }


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging() -> None:
    """Setup logging for exchange connector."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


if __name__ == "__main__":
    setup_logging()
    print("Exchange Connector Module - Import this module to use")
