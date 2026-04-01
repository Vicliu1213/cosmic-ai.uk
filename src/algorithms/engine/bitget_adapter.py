#!/usr/bin/env python3
"""
Bitget 交易所適配器 - 完整實現
支援 REST API、WebSocket 流、訂單管理、帳戶查詢
"""

import asyncio
import hmac
import hashlib
import time
import json
import base64
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import aiohttp
import websockets

from ..base_engine import BaseEngine, EngineSignal

logger = logging.getLogger(__name__)


class BitgetAdapter(BaseEngine):
    """
    Bitget 交易所適配器 - 完整實現

    功能：
    1. REST API 完整封裝
    2. WebSocket 實時數據流
    3. 訂單管理（創建、取消、查詢）
    4. 帳戶管理（餘額、持倉）
    5. 市場數據（訂單簿、K線、Ticker）
    """

    def __init__(self, engine_id: str, output_queue: asyncio.Queue, config: Dict):
        super().__init__(engine_id, output_queue)
        self.config = config

        # API 憑證
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.passphrase = config.get('passphrase')
        self.testnet = config.get('testnet', True)

        # 限流配置
        self.rate_limit = config.get('rate_limit', 10)
        self.timeout = config.get('timeout', 30)

        # WebSocket 配置
        self.websocket_enabled = config.get('websocket', True)
        self.ws_url = config.get('websocket_url', "wss://ws.bitget.com/v2/ws/public")
        self.ws_private_url = "wss://ws.bitget.com/v2/ws/private"

        # 交易配置
        self.instruments = config.get('instruments', ['BTCUSDT', 'ETHUSDT'])
        self.order_types = config.get('order_types', ['market', 'limit', 'post_only'])
        self.price_precision = config.get('price_precision', 2)
        self.quantity_precision = config.get('quantity_precision', 6)
        self.max_order_size = config.get('max_order_size', 10)
        self.min_order_size = config.get('min_order_size', 0.001)

        # API 端點
        if self.testnet:
            self.base_url = "https://api.bitget.com"
        else:
            self.base_url = "https://api.bitget.com"

        # 狀態存儲
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws_connection = None
        self._ws_private = None
        self._running = True
        self._rate_limiter = asyncio.Semaphore(self.rate_limit)

        # 緩存
        self.order_book_cache: Dict[str, Dict] = {}
        self.ticker_cache: Dict[str, Dict] = {}
        self.balance_cache: Dict[str, Dict] = {}
        self.position_cache: Dict[str, Dict] = {}
        self.open_orders_cache: Dict[str, List[Dict]] = {}

        # 訂單跟蹤
        self.order_tracker: Dict[str, Dict] = {}

        # 啟動 WebSocket
        if self.websocket_enabled:
            asyncio.create_task(self._websocket_loop())

        logger.info(f"Bitget 適配器初始化完成")
        logger.info(f"  測試網: {self.testnet}")
        logger.info(f"  監控品種: {self.instruments}")
        logger.info(f"  WebSocket: {self.websocket_enabled}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """獲取 HTTP 會話"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _generate_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """生成簽名"""
        message = timestamp + method + request_path + body
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _get_headers(self, method: str, path: str, body: str = '') -> Dict:
        """獲取請求頭"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, path, body)

        return {
            'Content-Type': 'application/json',
            'ACCESS-KEY': self.api_key or '',
            'ACCESS-SIGN': signature,
            'ACCESS-TIMESTAMP': timestamp,
            'ACCESS-PASSPHRASE': self.passphrase or '',
            'locale': 'en-US'
        }

    async def _request(self, method: str, path: str, params: Dict = None, data: Dict = None) -> Dict:
        """發送 API 請求"""
        async with self._rate_limiter:
            session = await self._get_session()
            url = f"{self.base_url}{path}"
            body = json.dumps(data) if data else ''
            headers = self._get_headers(method, path, body) if self.api_key else {}

            try:
                async with session.request(
                    method, url, params=params, json=data, headers=headers, timeout=self.timeout
                ) as resp:
                    result = await resp.json()

                    if resp.status != 200 or result.get('code') != '00000':
                        logger.error(f"Bitget API 錯誤: {result}")
                        return {'code': result.get('code', -1), 'msg': result.get('msg', 'Unknown error')}

                    return result

            except asyncio.TimeoutError:
                logger.error(f"Bitget 請求超時: {url}")
                return {'code': -1, 'msg': 'timeout'}
            except Exception as e:
                logger.error(f"Bitget 請求失敗: {e}")
                return {'code': -1, 'msg': str(e)}

    # ==================== 市場數據 API ====================

    async def fetch_order_book(self, symbol: str, limit: int = 10) -> Dict:
        """獲取訂單簿"""
        path = "/api/v2/spot/market/orderbook"
        params = {'symbol': symbol, 'limit': limit}
        result = await self._request('GET', path, params=params)

        if result.get('code') == '00000':
            data = result.get('data', {})
            return {
                'bids': [[float(b[0]), float(b[1])] for b in data.get('bids', [])],
                'asks': [[float(a[0]), float(a[1])] for a in data.get('asks', [])],
                'timestamp': int(time.time() * 1000)
            }
        return {'bids': [], 'asks': [], 'timestamp': 0}

    async def fetch_ticker(self, symbol: str) -> Dict:
        """獲取最新價格"""
        path = "/api/v2/spot/market/ticker"
        params = {'symbol': symbol}
        result = await self._request('GET', path, params=params)

        if result.get('code') == '00000':
            data = result.get('data', {})
            return {
                'symbol': symbol,
                'last': float(data.get('last', 0)),
                'bid': float(data.get('bid', 0)),
                'ask': float(data.get('ask', 0)),
                'high': float(data.get('high24h', 0)),
                'low': float(data.get('low24h', 0)),
                'volume': float(data.get('baseVolume', 0)),
                'quoteVolume': float(data.get('quoteVolume', 0)),
                'timestamp': int(data.get('ts', 0))
            }
        return {}

    async def fetch_klines(self, symbol: str, interval: str = '1m', limit: int = 100) -> List[Dict]:
        """獲取K線"""
        # 時間間隔映射
        interval_map = {
            '1m': '1min', '5m': '5min', '15m': '15min',
            '30m': '30min', '1h': '1h', '4h': '4h', '1d': '1d'
        }
        granularity = interval_map.get(interval, '1min')

        path = "/api/v2/spot/market/candles"
        params = {'symbol': symbol, 'granularity': granularity, 'limit': limit}
        result = await self._request('GET', path, params=params)

        if result.get('code') == '00000':
            candles = result.get('data', [])
            return [
                {
                    'timestamp': int(c[0]),
                    'open': float(c[1]),
                    'high': float(c[2]),
                    'low': float(c[3]),
                    'close': float(c[4]),
                    'volume': float(c[5])
                }
                for c in candles
            ]
        return []

    # ==================== 帳戶 API ====================

    async def fetch_balance(self) -> Dict:
        """獲取帳戶餘額"""
        path = "/api/v2/spot/account/assets"
        result = await self._request('GET', path)

        if result.get('code') == '00000':
            balances = {}
            for asset in result.get('data', []):
                symbol = asset.get('coin')
                free = float(asset.get('available', 0))
                frozen = float(asset.get('frozen', 0))
                balances[symbol] = {
                    'free': free,
                    'used': frozen,
                    'total': free + frozen
                }
            self.balance_cache = balances
            return balances
        return {}

    async def fetch_positions(self, symbol: str = None) -> Dict:
        """獲取持倉"""
        path = "/api/v2/mix/position/all-position"
        params = {'symbol': symbol} if symbol else {}
        result = await self._request('GET', path, params=params)

        if result.get('code') == '00000':
            positions = {}
            for pos in result.get('data', []):
                sym = pos.get('symbol')
                positions[sym] = {
                    'symbol': sym,
                    'size': float(pos.get('total', 0)),
                    'avg_price': float(pos.get('avgPrice', 0)),
                    'unrealized_pnl': float(pos.get('upl', 0))
                }
            self.position_cache = positions
            return positions
        return {}

    # ==================== 訂單 API ====================

    async def create_order(self, symbol: str, side: str, order_type: str,
                           quantity: float, price: Optional[float] = None,
                           client_order_id: str = None) -> Dict:
        """創建訂單"""
        # 檢查數量限制
        quantity = round(quantity, self.quantity_precision)
        if quantity < self.min_order_size:
            return {'success': False, 'error': f'數量小於最小值 {self.min_order_size}'}
        if quantity > self.max_order_size:
            return {'success': False, 'error': f'數量大於最大值 {self.max_order_size}'}

        # 轉換訂單類型
        order_type_map = {
            'market': 'market',
            'limit': 'limit',
            'post_only': 'post_only'
        }
        order_type = order_type_map.get(order_type, 'limit')

        path = "/api/v2/spot/trade/place-order"
        data = {
            'symbol': symbol,
            'side': side.upper(),
            'orderType': order_type.upper(),
            'size': str(quantity),
            'clientOid': client_order_id or str(uuid.uuid4())
        }

        if price and order_type != 'market':
            data['price'] = str(round(price, self.price_precision))

        result = await self._request('POST', path, data=data)

        if result.get('code') == '00000':
            order_data = result.get('data', {})
            order_id = order_data.get('orderId')

            # 跟蹤訂單
            self.order_tracker[order_id] = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'status': 'pending',
                'timestamp': datetime.now()
            }

            return {
                'success': True,
                'order_id': order_id,
                'client_order_id': client_order_id,
                'symbol': symbol,
                'side': side,
                'price': price,
                'quantity': quantity,
                'status': order_data.get('status', 'new')
            }
        else:
            return {
                'success': False,
                'error': result.get('msg', 'Unknown error'),
                'code': result.get('code')
            }

    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """取消訂單"""
        path = "/api/v2/spot/trade/cancel-order"
        data = {'symbol': symbol, 'orderId': order_id}
        result = await self._request('POST', path, data=data)

        if result.get('code') == '00000':
            if order_id in self.order_tracker:
                self.order_tracker[order_id]['status'] = 'cancelled'
            return True
        return False

    async def fetch_open_orders(self, symbol: str) -> List[Dict]:
        """獲取未完成訂單"""
        path = "/api/v2/spot/trade/open-orders"
        params = {'symbol': symbol}
        result = await self._request('GET', path, params=params)

        if result.get('code') == '00000':
            orders = result.get('data', [])
            self.open_orders_cache[symbol] = orders
            return orders
        return []

    async def fetch_order_status(self, symbol: str, order_id: str) -> Dict:
        """獲取訂單狀態"""
        path = "/api/v2/spot/trade/order-detail"
        params = {'symbol': symbol, 'orderId': order_id}
        result = await self._request('GET', path, params=params)

        if result.get('code') == '00000':
            data = result.get('data', {})
            status = data.get('state')

            # 更新追蹤器
            if order_id in self.order_tracker:
                self.order_tracker[order_id]['status'] = status
                self.order_tracker[order_id]['filled'] = float(data.get('filledSize', 0))

            return {
                'order_id': data.get('orderId'),
                'symbol': data.get('symbol'),
                'side': data.get('side'),
                'price': float(data.get('price', 0)),
                'quantity': float(data.get('size', 0)),
                'filled': float(data.get('filledSize', 0)),
                'status': status,
                'timestamp': int(data.get('cTime', 0))
            }
        return {}

    # ==================== WebSocket 實時數據 ====================

    async def _websocket_loop(self):
        """WebSocket 連接循環"""
        while self._running:
            try:
                # 公共頻道連接
                async with websockets.connect(self.ws_url) as ws:
                    self._ws_connection = ws

                    # 訂閱公共頻道
                    subscribe_msg = {
                        "op": "subscribe",
                        "args": []
                    }

                    # 訂閱 ticker
                    for inst in self.instruments:
                        subscribe_msg["args"].append({
                            "channel": "ticker",
                            "instId": inst
                        })

                    # 訂閱訂單簿
                    for inst in self.instruments:
                        subscribe_msg["args"].append({
                            "channel": "books5",
                            "instId": inst
                        })

                    await ws.send(json.dumps(subscribe_msg))
                    logger.info(f"Bitget WebSocket 訂閱成功: {self.instruments}")

                    # 接收消息
                    async for message in ws:
                        data = json.loads(message)
                        await self._handle_websocket_message(data)

            except websockets.exceptions.ConnectionClosed:
                logger.warning("Bitget WebSocket 連接關閉，重連中...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Bitget WebSocket 錯誤: {e}")
                await asyncio.sleep(5)

    async def _handle_websocket_message(self, data: Dict):
        """處理 WebSocket 消息"""
        try:
            # 訂閱確認
            if 'event' in data:
                if data['event'] == 'subscribe':
                    logger.debug(f"訂閱成功: {data.get('arg', {})}")
                return

            # 數據推送
            arg = data.get('arg', {})
            channel = arg.get('channel')
            inst = arg.get('instId')
            data_list = data.get('data', [])

            if not data_list:
                return

            for item in data_list:
                if channel == 'ticker':
                    self._handle_ticker(inst, item)
                elif channel == 'books5':
                    self._handle_order_book(inst, item)

        except Exception as e:
            logger.error(f"處理 WebSocket 消息失敗: {e}")

    def _handle_ticker(self, symbol: str, data: Dict):
        """處理 Ticker 數據"""
        ticker = {
            'last': float(data.get('last', 0)),
            'bid': float(data.get('bid', 0)),
            'ask': float(data.get('ask', 0)),
            'high': float(data.get('high24h', 0)),
            'low': float(data.get('low24h', 0)),
            'volume': float(data.get('baseVolume', 0)),
            'timestamp': int(data.get('ts', 0))
        }

        self.ticker_cache[symbol] = ticker

        # 生成引擎信號
        asyncio.create_task(self._emit_signal(symbol, ticker))

    def _handle_order_book(self, symbol: str, data: Dict):
        """處理訂單簿數據"""
        bids = [[float(b[0]), float(b[1])] for b in data.get('bids', [])]
        asks = [[float(a[0]), float(a[1])] for a in data.get('asks', [])]

        self.order_book_cache[symbol] = {
            'bids': bids,
            'asks': asks,
            'timestamp': int(data.get('ts', 0))
        }

    async def _emit_signal(self, symbol: str, ticker: Dict):
        """發送引擎信號"""
        signal = EngineSignal(
            engine_id=self.engine_id,
            direction=1 if ticker['bid'] > 0 else 0,
            strength=min(1.0, ticker['volume'] / 1000000),
            confidence=0.7,
            meta={
                'symbol': symbol,
                'ticker': ticker,
                'exchange': 'bitget'
            }
        )
        await self.output_queue.put(signal)

    # ==================== 輔助方法 ====================

    async def run(self, features: Dict) -> None:
        """引擎運行入口"""
        # 更新特徵中的 Bitget 數據
        features['bitget_ticker'] = self.ticker_cache
        features['bitget_orderbook'] = self.order_book_cache
        features['bitget_balance'] = self.balance_cache

        # 生成狀態信號
        signal = EngineSignal(
            engine_id=self.engine_id,
            direction=1 if self.balance_cache else 0,
            strength=0.5,
            confidence=0.8 if self._ws_connection else 0.3,
            meta={
                'connected': self._ws_connection is not None,
                'instruments': self.instruments,
                'has_balance': bool(self.balance_cache)
            }
        )
        await self.output_queue.put(signal)

    async def shutdown(self):
        """關閉適配器"""
        self._running = False

        if self._ws_connection:
            await self._ws_connection.close()

        if self._session and not self._session.closed:
            await self._session.close()

        logger.info("Bitget 適配器已關閉")

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            'connected': self._ws_connection is not None,
            'instruments': self.instruments,
            'ticker_count': len(self.ticker_cache),
            'balance_assets': list(self.balance_cache.keys()),
            'open_orders': {sym: len(orders) for sym, orders in self.open_orders_cache.items()},
            'tracked_orders': len(self.order_tracker)
        }
