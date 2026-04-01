#!/usr/bin/env python3
"""
Binance 交易所適配器 - 完整實現
支援 REST API、WebSocket 流、訂單管理、帳戶查詢
"""

import asyncio
import hmac
import hashlib
import time
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import websockets

from ..base_engine import BaseEngine, EngineSignal

logger = logging.getLogger(__name__)


class BinanceAdapter(BaseEngine):
    """
    Binance 交易所適配器 - 完整實現

    支援功能：
    - REST API 完整封裝
    - WebSocket 實時數據流
    - 訂單管理（限價單、市價單、止損單）
    - 帳戶管理（餘額、成交記錄）
    - 市場數據（訂單簿、K線、深度圖）
    """

    def __init__(self, engine_id: str, output_queue: asyncio.Queue, config: Dict):
        super().__init__(engine_id, output_queue)
        self.config = config

        # API 憑證
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.testnet = config.get('testnet', True)

        # 限流配置
        self.rate_limit = config.get('rate_limit', 20)
        self.timeout = config.get('timeout', 30)

        # WebSocket 配置
        self.websocket_enabled = config.get('websocket', True)
        if self.testnet:
            self.base_url = "https://testnet.binance.vision"
            self.ws_url = "wss://testnet.binance.vision/ws"
        else:
            self.base_url = "https://api.binance.com"
            self.ws_url = "wss://stream.binance.com:9443/ws"

        # 交易配置
        self.instruments = config.get('instruments', ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT'])
        self.order_types = config.get('order_types', ['MARKET', 'LIMIT', 'STOP_LOSS_LIMIT'])
        self.price_precision = config.get('price_precision', 2)
        self.quantity_precision = config.get('quantity_precision', 6)
        self.max_order_size = config.get('max_order_size', 10)
        self.min_order_size = config.get('min_order_size', 0.001)

        # 狀態存儲
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws_connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self._running = True
        self._rate_limiter = asyncio.Semaphore(self.rate_limit)

        # 緩存
        self.order_book_cache: Dict[str, Dict] = {}
        self.ticker_cache: Dict[str, Dict] = {}
        self.balance_cache: Dict[str, Dict] = {}
        self.exchange_info_cache: Dict = {}
        self.open_orders_cache: Dict[str, List[Dict]] = {}

        # 訂單跟蹤
        self.order_tracker: Dict[str, Dict] = {}

        # 啟動 WebSocket
        if self.websocket_enabled:
            asyncio.create_task(self._websocket_loop())

        logger.info(f"Binance 適配器初始化完成")
        logger.info(f"  測試網: {self.testnet}")
        logger.info(f"  監控品種: {self.instruments}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """獲取 HTTP 會話"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _generate_signature(self, params: Dict) -> str:
        """生成簽名"""
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def _request(self, method: str, path: str, params: Dict = None, signed: bool = False) -> Dict:
        """發送 API 請求"""
        async with self._rate_limiter:
            session = await self._get_session()
            url = f"{self.base_url}{path}"

            headers = {'X-MBX-APIKEY': self.api_key} if self.api_key else {}

            if signed and self.api_secret:
                params = params or {}
                params['timestamp'] = int(time.time() * 1000)
                params['signature'] = self._generate_signature(params)

            try:
                async with session.request(method, url, params=params, headers=headers, timeout=self.timeout) as resp:
                    result = await resp.json()

                    if resp.status != 200:
                        logger.error(f"Binance API 錯誤: {result}")
                        return {'code': resp.status, 'msg': str(result)}

                    return result

            except asyncio.TimeoutError:
                logger.error(f"Binance 請求超時: {url}")
                return {'code': -1, 'msg': 'timeout'}
            except Exception as e:
                logger.error(f"Binance 請求失敗: {e}")
                return {'code': -1, 'msg': str(e)}

    # ==================== 市場數據 API ====================

    async def fetch_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """獲取訂單簿"""
        path = "/api/v3/depth"
        params = {'symbol': symbol, 'limit': limit}
        result = await self._request('GET', path, params=params)

        if 'code' not in result:
            return {
                'bids': [[float(b[0]), float(b[1])] for b in result.get('bids', [])],
                'asks': [[float(a[0]), float(a[1])] for a in result.get('asks', [])],
                'timestamp': result.get('lastUpdateId', 0)
            }
        return {'bids': [], 'asks': [], 'timestamp': 0}

    async def fetch_ticker(self, symbol: str) -> Dict:
        """獲取最新價格"""
        path = "/api/v3/ticker/24hr"
        params = {'symbol': symbol}
        result = await self._request('GET', path, params=params)

        if 'code' not in result:
            return {
                'symbol': symbol,
                'last': float(result.get('lastPrice', 0)),
                'bid': float(result.get('bidPrice', 0)),
                'ask': float(result.get('askPrice', 0)),
                'high': float(result.get('highPrice', 0)),
                'low': float(result.get('lowPrice', 0)),
                'volume': float(result.get('volume', 0)),
                'quoteVolume': float(result.get('quoteVolume', 0)),
                'open': float(result.get('openPrice', 0)),
                'change': float(result.get('priceChange', 0)),
                'changePercent': float(result.get('priceChangePercent', 0)),
                'timestamp': result.get('closeTime', 0)
            }
        return {}

    async def fetch_klines(self, symbol: str, interval: str = '1m', limit: int = 100) -> List[Dict]:
        """獲取K線"""
        path = "/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        result = await self._request('GET', path, params=params)

        if 'code' not in result:
            return [
                {
                    'timestamp': int(k[0]),
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5]),
                    'close_time': int(k[6]),
                    'quote_volume': float(k[7]),
                    'trades': int(k[8])
                }
                for k in result
            ]
        return []

    async def fetch_exchange_info(self) -> Dict:
        """獲取交易所信息"""
        if self.exchange_info_cache:
            return self.exchange_info_cache

        path = "/api/v3/exchangeInfo"
        result = await self._request('GET', path)

        if 'code' not in result:
            self.exchange_info_cache = result
            return result
        return {}

    # ==================== 帳戶 API ====================

    async def fetch_balance(self) -> Dict:
        """獲取帳戶餘額"""
        path = "/api/v3/account"
        params = {}
        result = await self._request('GET', path, params=params, signed=True)

        if 'code' not in result:
            balances = {}
            for asset in result.get('balances', []):
                symbol = asset.get('asset')
                free = float(asset.get('free', 0))
                locked = float(asset.get('locked', 0))
                balances[symbol] = {
                    'free': free,
                    'used': locked,
                    'total': free + locked
                }
            self.balance_cache = balances
            return balances
        return {}

    # ==================== 訂單 API ====================

    async def create_order(self, symbol: str, side: str, order_type: str,
                           quantity: float, price: Optional[float] = None,
                           stop_price: Optional[float] = None,
                           client_order_id: str = None) -> Dict:
        """創建訂單"""
        # 檢查數量限制
        quantity = round(quantity, self.quantity_precision)
        if quantity < self.min_order_size:
            return {'success': False, 'error': f'數量小於最小值 {self.min_order_size}'}
        if quantity > self.max_order_size:
            return {'success': False, 'error': f'數量大於最大值 {self.max_order_size}'}

        path = "/api/v3/order"
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity,
            'timestamp': int(time.time() * 1000)
        }

        if client_order_id:
            params['newClientOrderId'] = client_order_id
        else:
            params['newClientOrderId'] = str(uuid.uuid4())

        if order_type.upper() in ['LIMIT', 'STOP_LOSS_LIMIT']:
            if not price:
                return {'success': False, 'error': '限價單需要價格'}
            params['price'] = round(price, self.price_precision)
            params['timeInForce'] = 'GTC'

        if order_type.upper() == 'STOP_LOSS_LIMIT' and stop_price:
            params['stopPrice'] = round(stop_price, self.price_precision)

        result = await self._request('POST', path, params=params, signed=True)

        if 'code' not in result:
            order_id = result.get('orderId')
            self.order_tracker[order_id] = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'status': result.get('status', 'NEW'),
                'timestamp': datetime.now()
            }

            return {
                'success': True,
                'order_id': order_id,
                'client_order_id': result.get('clientOrderId'),
                'symbol': symbol,
                'side': side,
                'price': price,
                'quantity': quantity,
                'status': result.get('status'),
                'transact_time': result.get('transactTime', 0)
            }
        else:
            return {
                'success': False,
                'error': result.get('msg', 'Unknown error'),
                'code': result.get('code')
            }

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """取消訂單"""
        path = "/api/v3/order"
        params = {'symbol': symbol, 'orderId': order_id}
        result = await self._request('DELETE', path, params=params, signed=True)

        if 'code' not in result:
            if order_id in self.order_tracker:
                self.order_tracker[order_id]['status'] = 'CANCELED'
            return True
        return False

    async def fetch_open_orders(self, symbol: str) -> List[Dict]:
        """獲取未完成訂單"""
        path = "/api/v3/openOrders"
        params = {'symbol': symbol}
        result = await self._request('GET', path, params=params, signed=True)

        if 'code' not in result:
            self.open_orders_cache[symbol] = result
            return result
        return []

    async def fetch_order_status(self, symbol: str, order_id: str) -> Dict:
        """獲取訂單狀態"""
        path = "/api/v3/order"
        params = {'symbol': symbol, 'orderId': order_id}
        result = await self._request('GET', path, params=params, signed=True)

        if 'code' not in result:
            if order_id in self.order_tracker:
                self.order_tracker[order_id]['status'] = result.get('status')
                self.order_tracker[order_id]['executed_qty'] = float(result.get('executedQty', 0))

            return {
                'order_id': result.get('orderId'),
                'symbol': result.get('symbol'),
                'side': result.get('side'),
                'price': float(result.get('price', 0)),
                'quantity': float(result.get('origQty', 0)),
                'executed': float(result.get('executedQty', 0)),
                'status': result.get('status'),
                'type': result.get('type'),
                'timestamp': result.get('time', 0)
            }
        return {}

    # ==================== WebSocket 實時數據 ====================

    async def _websocket_loop(self):
        """WebSocket 連接循環"""
        while self._running:
            try:
                # 為每個品種創建獨立連接
                for symbol in self.instruments:
                    stream_name = f"{symbol.lower()}@depth5@100ms"
                    ws_url = f"{self.ws_url}/{stream_name}"

                    async with websockets.connect(ws_url) as ws:
                        self._ws_connections[symbol] = ws
                        logger.info(f"Binance WebSocket 連接成功: {symbol}")

                        async for message in ws:
                            data = json.loads(message)
                            await self._handle_websocket_message(symbol, data)

            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Binance WebSocket 連接關閉，重連中...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Binance WebSocket 錯誤: {e}")
                await asyncio.sleep(5)

    async def _handle_websocket_message(self, symbol: str, data: Dict):
        """處理 WebSocket 消息"""
        try:
            if 'bids' in data and 'asks' in data:
                # 訂單簿數據
                self.order_book_cache[symbol] = {
                    'bids': [[float(b[0]), float(b[1])] for b in data.get('bids', [])],
                    'asks': [[float(a[0]), float(a[1])] for a in data.get('asks', [])],
                    'timestamp': data.get('E', 0)
                }

                # 生成信號
                signal = EngineSignal(
                    engine_id=self.engine_id,
                    direction=1 if self.order_book_cache[symbol]['bids'] else 0,
                    strength=0.5,
                    confidence=0.8,
                    meta={
                        'symbol': symbol,
                        'exchange': 'binance',
                        'best_bid': self.order_book_cache[symbol]['bids'][0][0] if self.order_book_cache[symbol]['bids'] else 0,
                        'best_ask': self.order_book_cache[symbol]['asks'][0][0] if self.order_book_cache[symbol]['asks'] else 0
                    }
                )
                await self.output_queue.put(signal)

        except Exception as e:
            logger.error(f"處理 WebSocket 消息失敗: {e}")

    # ==================== 輔助方法 ====================

    async def run(self, features: Dict) -> None:
        """引擎運行入口"""
        features['binance_ticker'] = self.ticker_cache
        features['binance_orderbook'] = self.order_book_cache
        features['binance_balance'] = self.balance_cache

        signal = EngineSignal(
            engine_id=self.engine_id,
            direction=1 if self.balance_cache else 0,
            strength=0.5,
            confidence=0.8 if self._ws_connections else 0.3,
            meta={
                'connected': bool(self._ws_connections),
                'instruments': self.instruments,
                'has_balance': bool(self.balance_cache)
            }
        )
        await self.output_queue.put(signal)

    async def shutdown(self):
        """關閉適配器"""
        self._running = False

        for ws in self._ws_connections.values():
            await ws.close()

        if self._session and not self._session.closed:
            await self._session.close()

        logger.info("Binance 適配器已關閉")

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            'connected': bool(self._ws_connections),
            'instruments': self.instruments,
            'ticker_count': len(self.ticker_cache),
            'balance_assets': list(self.balance_cache.keys()),
            'open_orders': {sym: len(orders) for sym, orders in self.open_orders_cache.items()},
            'tracked_orders': len(self.order_tracker)
        }
