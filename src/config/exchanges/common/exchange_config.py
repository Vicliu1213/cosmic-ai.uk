# config/exchanges.py
"""
交易所API配置 - 完整端点地址
"""

class ExchangeConfig:
    """交易所配置类"""

    # Binance 币安
    BINANCE = {
        'name': 'binance',
        'rest_api': 'https://api.binance.com',
        'rest_api_testnet': 'https://testnet.binance.vision',
        'ws_stream': 'wss://stream.binance.com:9443/ws',
        'ws_stream_testnet': 'wss://testnet.binance.vision/ws',
        'futures_api': 'https://fapi.binance.com',
        'futures_ws': 'wss://fstream.binance.com/ws',
        'docs': 'https://binance-docs.github.io/apidocs/'
    }

    # OKX 欧易
    OKX = {
        'name': 'okx',
        'rest_api': 'https://www.okx.com',
        'rest_api_aws': 'https://aws.okx.com',
        'ws_public': 'wss://ws.okx.com:8443/ws/v5/public',
        'ws_private': 'wss://ws.okx.com:8443/ws/v5/private',
        'demo_trading': 'https://www.okx.com/api/v5',
        'docs': 'https://www.okx.com/docs-v5/'
    }

    # Bybit
    BYBIT = {
        'name': 'bybit',
        'rest_api': 'https://api.bybit.com',
        'rest_api_testnet': 'https://api-testnet.bybit.com',
        'ws_public': 'wss://stream.bybit.com/v5/public/spot',
        'ws_private': 'wss://stream.bybit.com/v5/private',
        'futures_ws': 'wss://stream.bybit.com/v5/public/linear',
        'docs': 'https://bybit-exchange.github.io/docs/v5/intro'
    }

    # Bitget
    BITGET = {
        'name': 'bitget',
        'rest_api': 'https://api.bitget.com',
        'rest_api_testnet': 'https://api.testnet.bitget.com',
        'ws_public': 'wss://ws.bitget.com/mix/v1/stream',
        'ws_private': 'wss://ws.bitget.com/mix/v1/stream',
        'docs': 'https://bitgetlimited.github.io/apidoc/en/mix/'
    }


# 多交易所统一客户端
class UnifiedExchangeClient:
    """统一交易所客户端 - 支持所有主流交易所"""

    def __init__(self, exchange_name: str, api_key: str, api_secret: str,
                 passphrase: str = None, testnet: bool = False):
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.testnet = testnet

        # 获取配置
        self.config = self._get_config()
        self.base_url = self._get_base_url()

        # 初始化会话
        self.session = None
        self.ws = None

    def _get_config(self) -> Dict:
        """获取交易所配置"""
        configs = {
            'binance': ExchangeConfig.BINANCE,
            'okx': ExchangeConfig.OKX,
            'bybit': ExchangeConfig.BYBIT,
            'bitget': ExchangeConfig.BITGET
        }
        return configs.get(self.exchange_name, {})

    def _get_base_url(self) -> str:
        """获取API基础URL"""
        if self.testnet:
            testnet_keys = {
                'binance': 'rest_api_testnet',
                'bybit': 'rest_api_testnet',
                'bitget': 'rest_api_testnet',
                'okx': 'demo_trading'
            }
            key = testnet_keys.get(self.exchange_name, 'rest_api')
            return self.config.get(key, self.config.get('rest_api'))
        return self.config.get('rest_api')

    async def create_session(self):
        """创建HTTP会话"""
        import aiohttp
        self.session = aiohttp.ClientSession()

    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()

    def _generate_signature(self, timestamp: str, method: str,
                           request_path: str, body: str = '') -> str:
        """生成签名 - 各交易所签名算法不同"""
        import hmac
        import hashlib

        if self.exchange_name == 'binance':
            # Binance签名算法
            query_string = f"{timestamp}{method}{request_path}{body}"
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

        elif self.exchange_name == 'okx':
            # OKX签名算法
            sign_str = f"{timestamp}{method}{request_path}{body}"
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                sign_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

        elif self.exchange_name == 'bybit':
            # Bybit签名算法
            param_str = f"{timestamp}{self.api_key}{self.recv_window}{body}"
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                param_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

        elif self.exchange_name == 'bitget':
            # Bitget签名算法
            sign_str = f"{timestamp}{method}{request_path}{body}"
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                sign_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

        else:
            signature = ''

        return signature

    async def _request(self, method: str, endpoint: str, params: Dict = None,
                      data: Dict = None, signed: bool = True) -> Dict:
        """发送HTTP请求"""
        import time

        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time() * 1000))

        headers = {
            'Content-Type': 'application/json',
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': timestamp,
        }

        # 添加各交易所特定头部
        if self.exchange_name == 'binance':
            headers['X-MBX-APIKEY'] = self.api_key

        elif self.exchange_name == 'okx':
            headers['OK-ACCESS-KEY'] = self.api_key
            headers['OK-ACCESS-TIMESTAMP'] = timestamp
            headers['OK-ACCESS-PASSPHRASE'] = self.passphrase

        elif self.exchange_name == 'bybit':
            headers['X-BAPI-RECV-WINDOW'] = '5000'
            headers['X-BAPI-API-KEY'] = self.api_key
            headers['X-BAPI-TIMESTAMP'] = timestamp

        elif self.exchange_name == 'bitget':
            headers['ACCESS-KEY'] = self.api_key
            headers['ACCESS-TIMESTAMP'] = timestamp
            headers['ACCESS-PASSPHRASE'] = self.passphrase

        if signed:
            body = json.dumps(data) if data else ''
            signature = self._generate_signature(timestamp, method, endpoint, body)

            if self.exchange_name == 'binance':
                headers['X-MBX-APIKEY'] = self.api_key
                if method == 'GET':
                    url += f"?{urllib.parse.urlencode(params)}&signature={signature}"
                else:
                    url += f"?signature={signature}"

            elif self.exchange_name == 'okx':
                headers['OK-ACCESS-SIGN'] = signature

            elif self.exchange_name == 'bybit':
                headers['X-BAPI-SIGN'] = signature

            elif self.exchange_name == 'bitget':
                headers['ACCESS-SIGN'] = signature

        async with self.session.request(method, url, headers=headers,
                                       params=params, json=data) as response:
            return await response.json()

    # ==================== 公开API ====================

    async def get_klines(self, symbol: str, interval: str = '1m',
                         limit: int = 100) -> List:
        """获取K线数据"""
        endpoint = '/api/v3/klines' if self.exchange_name == 'binance' else '/api/v5/market/candles'

        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }

        result = await self._request('GET', endpoint, params=params, signed=False)
        return result.get('data', result) if isinstance(result, dict) else result

    async def get_orderbook(self, symbol: str, limit: int = 10) -> Dict:
        """获取订单簿"""
        endpoints = {
            'binance': '/api/v3/depth',
            'okx': '/api/v5/market/books',
            'bybit': '/v5/market/orderbook',
            'bitget': '/api/v2/spot/market/orderbook'
        }

        endpoint = endpoints.get(self.exchange_name, '/api/v3/depth')
        params = {'symbol': symbol, 'limit': limit}

        result = await self._request('GET', endpoint, params=params, signed=False)
        return result

    async def get_ticker(self, symbol: str) -> Dict:
        """获取24小时行情"""
        endpoints = {
            'binance': '/api/v3/ticker/24hr',
            'okx': '/api/v5/market/ticker',
            'bybit': '/v5/market/tickers',
            'bitget': '/api/v2/spot/market/ticker'
        }

        endpoint = endpoints.get(self.exchange_name)
        params = {'symbol': symbol}

        result = await self._request('GET', endpoint, params=params, signed=False)

        if self.exchange_name == 'binance':
            return {'bid': float(result.get('bidPrice', 0)),
                   'ask': float(result.get('askPrice', 0))}
        elif self.exchange_name == 'okx':
            data = result.get('data', [{}])[0]
            return {'bid': float(data.get('bidPx', 0)),
                   'ask': float(data.get('askPx', 0))}
        elif self.exchange_name == 'bybit':
            data = result.get('result', {}).get('list', [{}])[0]
            return {'bid': float(data.get('bid1Price', 0)),
                   'ask': float(data.get('ask1Price', 0))}
        else:
            data = result.get('data', {})
            return {'bid': float(data.get('buy', 0)),
                   'ask': float(data.get('sell', 0))}

    async def get_funding_rate(self, symbol: str) -> float:
        """获取资金费率（永续合约）"""
        endpoints = {
            'binance': '/fapi/v1/fundingInfo',
            'okx': '/api/v5/public/funding-rate',
            'bybit': '/v5/market/tickers',
            'bitget': '/api/v2/mix/market/funding-time'
        }

        endpoint = endpoints.get(self.exchange_name)
        params = {'symbol': symbol}

        result = await self._request('GET', endpoint, params=params, signed=False)

        if self.exchange_name == 'binance':
            for item in result:
                if item.get('symbol') == symbol:
                    return float(item.get('lastFundingRate', 0))
        elif self.exchange_name == 'okx':
            data = result.get('data', [{}])[0]
            return float(data.get('fundingRate', 0))
        elif self.exchange_name == 'bybit':
            data = result.get('result', {}).get('list', [{}])[0]
            return float(data.get('fundingRate', 0))

        return 0.0

    # ==================== 私有API ====================

    async def get_account(self) -> Dict:
        """获取账户信息"""
        endpoints = {
            'binance': '/api/v3/account',
            'okx': '/api/v5/account/info',
            'bybit': '/v5/account/info',
            'bitget': '/api/v2/spot/account/info'
        }

        endpoint = endpoints.get(self.exchange_name)
        result = await self._request('GET', endpoint, signed=True)

        if self.exchange_name == 'binance':
            return result
        elif self.exchange_name == 'okx':
            return result.get('data', [{}])[0]
        elif self.exchange_name == 'bybit':
            return result.get('result', {})
        else:
            return result.get('data', {})

    async def get_balance(self) -> Dict:
        """获取余额"""
        endpoints = {
            'binance': '/api/v3/account',
            'okx': '/api/v5/account/balance',
            'bybit': '/v5/account/wallet-balance',
            'bitget': '/api/v2/spot/account/assets'
        }

        endpoint = endpoints.get(self.exchange_name)
        result = await self._request('GET', endpoint, signed=True)

        if self.exchange_name == 'binance':
            balances = result.get('balances', [])
            usdt_balance = next((b for b in balances if b['asset'] == 'USDT'), {})
            return {'total': float(usdt_balance.get('free', 0)) + float(usdt_balance.get('locked', 0)),
                   'free': float(usdt_balance.get('free', 0)),
                   'used': float(usdt_balance.get('locked', 0))}
        elif self.exchange_name == 'okx':
            data = result.get('data', [{}])[0]
            details = data.get('details', [])
            usdt_detail = next((d for d in details if d['ccy'] == 'USDT'), {})
            return {'total': float(usdt_detail.get('eq', 0)),
                   'free': float(usdt_detail.get('availEq', 0)),
                   'used': float(usdt_detail.get('frozenBal', 0))}
        elif self.exchange_name == 'bybit':
            result_data = result.get('result', {})
            list_data = result_data.get('list', [{}])[0]
            coins = list_data.get('coin', [])
            usdt_coin = next((c for c in coins if c['coin'] == 'USDT'), {})
            return {'total': float(usdt_coin.get('walletBalance', 0)),
                   'free': float(usdt_coin.get('availableToWithdraw', 0)),
                   'used': float(usdt_coin.get('locked', 0))}
        else:
            data = result.get('data', {})
            usdt_data = data.get('USDT', {})
            return {'total': float(usdt_data.get('available', 0)) + float(usdt_data.get('frozen', 0)),
                   'free': float(usdt_data.get('available', 0)),
                   'used': float(usdt_data.get('frozen', 0))}

    async def get_positions(self, symbol: str = None) -> List[Dict]:
        """获取持仓"""
        endpoints = {
            'binance': '/fapi/v2/positionRisk',
            'okx': '/api/v5/account/positions',
            'bybit': '/v5/position/list',
            'bitget': '/api/v2/mix/position/allPosition'
        }

        endpoint = endpoints.get(self.exchange_name)
        params = {'symbol': symbol} if symbol else {}

        result = await self._request('GET', endpoint, params=params, signed=True)

        positions = []

        if self.exchange_name == 'binance':
            for pos in result:
                if float(pos.get('positionAmt', 0)) != 0:
                    positions.append({
                        'symbol': pos.get('symbol'),
                        'amount': abs(float(pos.get('positionAmt', 0))),
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'current_price': float(pos.get('markPrice', 0)),
                        'unrealized_pnl': float(pos.get('unRealizedProfit', 0)),
                        'side': 'long' if float(pos.get('positionAmt', 0)) > 0 else 'short'
                    })
        elif self.exchange_name == 'okx':
            data = result.get('data', [])
            for pos in data:
                if float(pos.get('pos', 0)) != 0:
                    positions.append({
                        'symbol': pos.get('instId'),
                        'amount': abs(float(pos.get('pos', 0))),
                        'entry_price': float(pos.get('avgPx', 0)),
                        'current_price': float(pos.get('markPx', 0)),
                        'unrealized_pnl': float(pos.get('upl', 0)),
                        'side': 'long' if float(pos.get('pos', 0)) > 0 else 'short'
                    })
        elif self.exchange_name == 'bybit':
            result_data = result.get('result', {})
            list_data = result_data.get('list', [])
            for pos in list_data:
                if float(pos.get('size', 0)) != 0:
                    positions.append({
                        'symbol': pos.get('symbol'),
                        'amount': abs(float(pos.get('size', 0))),
                        'entry_price': float(pos.get('avgPrice', 0)),
                        'current_price': float(pos.get('markPrice', 0)),
                        'unrealized_pnl': float(pos.get('unrealisedPnl', 0)),
                        'side': 'long' if float(pos.get('side', 0)) == 1 else 'short'
                    })
        else:
            data = result.get('data', [])
            for pos in data:
                if float(pos.get('size', 0)) != 0:
                    positions.append({
                        'symbol': pos.get('symbol'),
                        'amount': abs(float(pos.get('size', 0))),
                        'entry_price': float(pos.get('averageOpenPrice', 0)),
                        'current_price': float(pos.get('markPrice', 0)),
                        'unrealized_pnl': float(pos.get('unrealizedPL', 0)),
                        'side': pos.get('holdSide', 'long')
                    })

        return positions

    async def create_market_order(self, symbol: str, side: str,
                                  amount: float) -> Dict:
        """市价单"""
        endpoints = {
            'binance': '/api/v3/order',
            'okx': '/api/v5/trade/order',
            'bybit': '/v5/order/create',
            'bitget': '/api/v2/spot/trade/orders'
        }

        endpoint = endpoints.get(self.exchange_name)

        data = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': amount
        }

        if self.exchange_name == 'okx':
            data = {
                'instId': symbol,
                'tdMode': 'cash',
                'side': side,
                'ordType': 'market',
                'sz': str(amount)
            }
        elif self.exchange_name == 'bybit':
            data = {
                'symbol': symbol,
                'side': side.upper(),
                'orderType': 'Market',
                'qty': str(amount),
                'timeInForce': 'GTC'
            }
        elif self.exchange_name == 'bitget':
            data = {
                'symbol': symbol,
                'side': side.upper(),
                'orderType': 'market',
                'size': str(amount),
                'force': 'normal'
            }

        result = await self._request('POST', endpoint, data=data, signed=True)

        return {'order_id': result.get('orderId', result.get('ordId', '')),
                'status': result.get('status', 'submitted')}

    async def create_limit_order(self, symbol: str, side: str,
                                 amount: float, price: float) -> Dict:
        """限价单"""
        endpoints = {
            'binance': '/api/v3/order',
            'okx': '/api/v5/trade/order',
            'bybit': '/v5/order/create',
            'bitget': '/api/v2/spot/trade/orders'
        }

        endpoint = endpoints.get(self.exchange_name)

        data = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'LIMIT',
            'quantity': amount,
            'price': price,
            'timeInForce': 'GTC'
        }

        if self.exchange_name == 'okx':
            data = {
                'instId': symbol,
                'tdMode': 'cash',
                'side': side,
                'ordType': 'limit',
                'sz': str(amount),
                'px': str(price)
            }
        elif self.exchange_name == 'bybit':
            data = {
                'symbol': symbol,
                'side': side.upper(),
                'orderType': 'Limit',
                'qty': str(amount),
                'price': str(price),
                'timeInForce': 'GTC'
            }
        elif self.exchange_name == 'bitget':
            data = {
                'symbol': symbol,
                'side': side.upper(),
                'orderType': 'limit',
                'size': str(amount),
                'price': str(price),
                'force': 'normal'
            }

        result = await self._request('POST', endpoint, data=data, signed=True)

        return {'order_id': result.get('orderId', result.get('ordId', '')),
                'status': result.get('status', 'submitted')}

    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """取消订单"""
        endpoints = {
            'binance': '/api/v3/order',
            'okx': '/api/v5/trade/cancel-order',
            'bybit': '/v5/order/cancel',
            'bitget': '/api/v2/spot/trade/cancel-order'
        }

        endpoint = endpoints.get(self.exchange_name)

        params = {'symbol': symbol, 'orderId': order_id}
        data = None

        if self.exchange_name == 'okx':
            data = {'instId': symbol, 'ordId': order_id}
            params = None
        elif self.exchange_name == 'bybit':
            data = {'symbol': symbol, 'orderId': order_id}
            params = None
        elif self.exchange_name == 'bitget':
            data = {'symbol': symbol, 'orderId': order_id}
            params = None

        result = await self._request('DELETE', endpoint, params=params,
                                     data=data, signed=True)
        return result

    async def get_order_status(self, order_id: str) -> Dict:
        """获取订单状态"""
        endpoints = {
            'binance': '/api/v3/order',
            'okx': '/api/v5/trade/order',
            'bybit': '/v5/order/history',
            'bitget': '/api/v2/spot/trade/orderInfo'
        }

        endpoint = endpoints.get(self.exchange_name)
        params = {'orderId': order_id}

        if self.exchange_name == 'okx':
            params = {'ordId': order_id}
        elif self.exchange_name == 'bybit':
            params = {'orderId': order_id}
        elif self.exchange_name == 'bitget':
            params = {'orderId': order_id}

        result = await self._request('GET', endpoint, params=params, signed=True)
        return result

    # ==================== WebSocket连接 ====================

    async def connect_websocket(self, channels: List[str]):
        """连接WebSocket"""
        import websockets

        ws_urls = {
            'binance': ExchangeConfig.BINANCE['ws_stream'],
            'okx': ExchangeConfig.OKX['ws_public'],
            'bybit': ExchangeConfig.BYBIT['ws_public'],
            'bitget': ExchangeConfig.BITGET['ws_public']
        }

        ws_url = ws_urls.get(self.exchange_name)

        async with websockets.connect(ws_url) as websocket:
            # 订阅频道
            subscribe_msg = self._build_subscribe_msg(channels)
            await websocket.send(json.dumps(subscribe_msg))

            while True:
                message = await websocket.recv()
                yield json.loads(message)

    def _build_subscribe_msg(self, channels: List[str]) -> Dict:
        """构建订阅消息"""
        if self.exchange_name == 'binance':
            return {
                'method': 'SUBSCRIBE',
                'params': channels,
                'id': 1
            }
        elif self.exchange_name == 'okx':
            return {
                'op': 'subscribe',
                'args': [{'channel': ch} for ch in channels]
            }
        elif self.exchange_name == 'bybit':
            return {
                'op': 'subscribe',
                'args': channels
            }
        elif self.exchange_name == 'bitget':
            return {
                'op': 'subscribe',
                'args': channels
            }
        return {}


# 多交易所管理器
class MultiExchangeManager:
    """多交易所管理器"""

    def __init__(self, config: Dict):
        self.exchanges = {}
        self.config = config

    def add_exchange(self, exchange_name: str, api_key: str,
                     api_secret: str, passphrase: str = None,
                     testnet: bool = False):
        """添加交易所"""
        client = UnifiedExchangeClient(
            exchange_name=exchange_name,
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            testnet=testnet
        )
        self.exchanges[exchange_name] = client

    async def init_all(self):
        """初始化所有交易所连接"""
        for client in self.exchanges.values():
            await client.create_session()

    async def close_all(self):
        """关闭所有连接"""
        for client in self.exchanges.values():
            await client.close()

    def get_client(self, exchange_name: str) -> UnifiedExchangeClient:
        """获取交易所客户端"""
        return self.exchanges.get(exchange_name)

    async def get_all_tickers(self, symbol: str) -> Dict[str, Dict]:
        """获取所有交易所的行情"""
        results = {}
        for name, client in self.exchanges.items():
            try:
                ticker = await client.get_ticker(symbol)
                results[name] = ticker
            except Exception as e:
                logging.error(f"获取{name}行情失败: {e}")
        return results

    async def get_all_orderbooks(self, symbol: str) -> Dict[str, Dict]:
        """获取所有交易所的订单簿"""
        results = {}
        for name, client in self.exchanges.items():
            try:
                orderbook = await client.get_orderbook(symbol)
                results[name] = orderbook
            except Exception as e:
                logging.error(f"获取{name}订单簿失败: {e}")
        return results
