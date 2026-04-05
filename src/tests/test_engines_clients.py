#!/usr/bin/env python3
"""
Test suite for engines/base_client.py and the concrete exchange clients
(BinanceClient, BybitClient, OkxClient, BitgetClient).

All network/IO is mocked — no real HTTP or WebSocket connections are made.
"""

import sys
import asyncio
import hmac
import hashlib
import importlib.util
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

_SRC = Path(__file__).parent.parent
sys.path.insert(0, str(_SRC))

# ---------------------------------------------------------------------------
# Stub out optional heavy dependencies before any engine imports
# ---------------------------------------------------------------------------

_fake_aiohttp = types.ModuleType("aiohttp")
_fake_aiohttp.ClientSession = MagicMock()
sys.modules.setdefault("aiohttp", _fake_aiohttp)

_fake_ws = types.ModuleType("websockets")
_fake_ws.connect = MagicMock()
sys.modules.setdefault("websockets", _fake_ws)

# ---------------------------------------------------------------------------
# Load base_client first, then inject BaseClient into each concrete module
# ---------------------------------------------------------------------------


def _exec_module(relpath: str, name: str, extra_globals: dict = None):
    """Load a Python file as a module, optionally injecting extra globals."""
    spec = importlib.util.spec_from_file_location(name, str(_SRC / relpath))
    mod = importlib.util.module_from_spec(spec)
    if extra_globals:
        mod.__dict__.update(extra_globals)
    spec.loader.exec_module(mod)
    return mod


_base_mod = _exec_module("engines/base_client.py", "base_client")
BaseClient = _base_mod.BaseClient

# bitget_client.py uses `from engine.base_client import BaseClient` (note: "engine",
# not "engines").  We register both a package stub and the submodule entry so
# that Python's import machinery resolves `engine.base_client` to our already-loaded
# _base_mod instead of attempting a real file-system lookup.
_engine_pkg = types.ModuleType("engine")
_engine_pkg.base_client = _base_mod
sys.modules.setdefault("engine", _engine_pkg)
sys.modules["engine.base_client"] = _base_mod

# Concrete clients don't import BaseClient — inject it via extra_globals
_inject = {"BaseClient": BaseClient, "asyncio": asyncio, "hmac": hmac, "hashlib": hashlib}

_binance_mod = _exec_module("engines/binance_client.py", "binance_client", _inject)
_bybit_mod = _exec_module("engines/bybit_client.py", "bybit_client", _inject)
_okx_mod = _exec_module("engines/okx_client.py", "okx_client", _inject)
_bitget_mod = _exec_module("engines/bitget_client.py", "bitget_client", _inject)

BinanceClient = _binance_mod.BinanceClient
BybitClient = _bybit_mod.BybitClient
OkxClient = _okx_mod.OkxClient
BitgetClient = _bitget_mod.BitgetClient


# ---------------------------------------------------------------------------
# Concrete test subclasses for abstract clients
# ---------------------------------------------------------------------------

class _ConcreteBybit(BybitClient):
    def _generate_signature(self, method, path, params):
        return "stub_sig"

    def _get_headers(self, method, path, params):
        return {}


class _ConcreteOkx(OkxClient):
    def _generate_signature(self, method, path, params):
        return "stub_sig"

    def _get_headers(self, method, path, params):
        return {}


class _ConcreteBitget(BitgetClient):
    def _generate_signature(self, method, path, params):
        return "stub_sig"

    def _get_headers(self, method, path, params):
        return {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _make_mock_response(status: int = 200, json_data: dict = None):
    """Create a mock aiohttp response context manager."""
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or {"result": "ok"})
    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=resp)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx, resp


# ---------------------------------------------------------------------------
# BaseClient (via concrete subclass)
# ---------------------------------------------------------------------------


class TestBaseClientInit:

    def test_stores_api_key_secret(self):
        client = BinanceClient("key123", "secret456")
        assert client.api_key == "key123"
        assert client.secret == "secret456"

    def test_passphrase_optional(self):
        client = BinanceClient("k", "s")
        assert client.passphrase is None

    def test_passphrase_stored(self):
        client = BinanceClient("k", "s", passphrase="pass")
        assert client.passphrase == "pass"

    def test_session_starts_as_none(self):
        client = BinanceClient("k", "s")
        assert client.session is None


class TestBaseClientEnsureSession:

    def test_creates_session_when_none(self):
        client = BinanceClient("k", "s")
        mock_session = MagicMock()
        with patch("aiohttp.ClientSession", return_value=mock_session):
            _run(client._ensure_session())
        assert client.session is mock_session

    def test_does_not_recreate_open_session(self):
        client = BinanceClient("k", "s")
        existing = MagicMock()
        existing.closed = False
        client.session = existing

        with patch("aiohttp.ClientSession") as cls:
            _run(client._ensure_session())
            cls.assert_not_called()

        assert client.session is existing

    def test_recreates_closed_session(self):
        client = BinanceClient("k", "s")
        old = MagicMock()
        old.closed = True
        client.session = old
        new = MagicMock()

        with patch("aiohttp.ClientSession", return_value=new):
            _run(client._ensure_session())

        assert client.session is new


# ---------------------------------------------------------------------------
# BinanceClient
# ---------------------------------------------------------------------------


class TestBinanceClient:

    def test_base_url(self):
        assert BinanceClient.BASE_URL == "https://fapi.binance.com"

    def test_generate_signature_is_hmac_sha256(self):
        client = BinanceClient("key", "secret")
        params = {"symbol": "BTCUSDT", "side": "BUY"}
        sig = client._generate_signature(params)
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        expected = hmac.new(
            "secret".encode(), query_string.encode(), hashlib.sha256
        ).hexdigest()
        assert sig == expected

    def test_generate_signature_different_params_different_sig(self):
        client = BinanceClient("key", "mysecret")
        sig1 = client._generate_signature({"a": "1"})
        sig2 = client._generate_signature({"a": "2"})
        assert sig1 != sig2

    def test_signature_returns_hex_string(self):
        client = BinanceClient("key", "s")
        sig = client._generate_signature({"k": "v"})
        assert isinstance(sig, str)
        assert all(c in "0123456789abcdef" for c in sig)


# ---------------------------------------------------------------------------
# BybitClient
# ---------------------------------------------------------------------------


class TestBybitClient:

    def test_base_url(self):
        assert BybitClient.BASE_URL == "https://api.bybit.com"

    def test_has_execute_iceberg_order(self):
        assert hasattr(BybitClient, "execute_iceberg_order")

    def test_execute_iceberg_calls_request_ten_times(self):
        client = _ConcreteBybit("k", "s")
        client.request = AsyncMock(return_value={"result": "ok"})

        _run(client.execute_iceberg_order("BTCUSDT", "Buy", 1.0))

        assert client.request.call_count == 10

    def test_execute_iceberg_splits_quantity_evenly(self):
        client = _ConcreteBybit("k", "s")
        calls = []

        async def fake_request(method, path, data):
            calls.append(data)

        client.request = fake_request

        with patch("asyncio.sleep", new_callable=AsyncMock):
            _run(client.execute_iceberg_order("BTCUSDT", "Buy", 1.0))

        chunks = [float(c["qty"]) for c in calls]
        assert all(abs(q - 0.1) < 1e-9 for q in chunks)

    def test_execute_iceberg_uses_correct_symbol_and_side(self):
        client = _ConcreteBybit("k", "s")
        calls = []

        async def fake_request(method, path, data):
            calls.append(data)

        client.request = fake_request

        with patch("asyncio.sleep", new_callable=AsyncMock):
            _run(client.execute_iceberg_order("ETHUSDT", "Sell", 0.5))

        assert all(c["symbol"] == "ETHUSDT" for c in calls)
        assert all(c["side"] == "Sell" for c in calls)


# ---------------------------------------------------------------------------
# OkxClient
# ---------------------------------------------------------------------------


class TestOkxClient:

    def test_base_url(self):
        assert OkxClient.BASE_URL == "https://www.okx.com"

    def test_has_get_liquidation_map(self):
        assert hasattr(OkxClient, "get_liquidation_map")

    def test_get_liquidation_map_calls_request(self):
        client = _ConcreteOkx("k", "s")
        client.request = AsyncMock(return_value={"data": []})

        result = _run(client.get_liquidation_map("BTC-USDT"))

        client.request.assert_called_once_with(
            "GET", "/api/v5/public/liquidation-orders", {"instId": "BTC-USDT"}
        )
        assert result == {"data": []}


# ---------------------------------------------------------------------------
# BitgetClient
# ---------------------------------------------------------------------------


class TestBitgetClient:

    def test_ws_url_set(self):
        client = _ConcreteBitget("k", "s")
        assert client.ws_url == "wss://ws.bitget.com/v2/ws/public"

    def test_orderbook_cache_starts_empty(self):
        client = _ConcreteBitget("k", "s")
        assert client.orderbook_cache == {}

    def test_get_market_slope_data_injects_realtime(self):
        client = _ConcreteBitget("k", "s")
        client.orderbook_cache["BTCUSDT"] = {"bid": 49900.0, "ask": 50100.0}

        async def fake_super_call(self_or_symbol, symbol=None):
            return {"candles": []}

        _base_mod.BaseClient.get_market_slope_data = fake_super_call
        try:
            result = _run(client.get_market_slope_data("BTCUSDT"))
        finally:
            del _base_mod.BaseClient.get_market_slope_data

        assert "realtime" in result
        assert result["realtime"]["bid"] == 49900.0
        assert result["realtime"]["ask"] == 50100.0

    def test_get_market_slope_data_defaults_when_symbol_not_cached(self):
        client = _ConcreteBitget("k", "s")

        async def fake_super_call(self_or_symbol, symbol=None):
            return {"candles": []}

        _base_mod.BaseClient.get_market_slope_data = fake_super_call
        try:
            result = _run(client.get_market_slope_data("ETHUSDT"))
        finally:
            del _base_mod.BaseClient.get_market_slope_data

        assert result["realtime"] == {"bid": 0, "ask": 0}
