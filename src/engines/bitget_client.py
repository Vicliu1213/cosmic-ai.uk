import hmac
import hashlib
import json
import asyncio
import websockets
from engine.base_client import BaseClient

class BitgetClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws_url = "wss://ws.bitget.com/v2/ws/public"
        self.orderbook_cache = {} # 存放實時盤口：{symbol: {"bid": x, "ask": y}}

    async def subscribe_market_data(self, symbols: list):
        """🚀 強度提升：啟動 WebSocket 監聽，實現零延遲盤口感知"""
        async with websockets.connect(self.ws_url) as ws:
            sub_msg = {
                "op": "subscribe",
                "args": [{"instType": "mc", "channel": "ticker", "instId": s} for s in symbols]
            }
            await ws.send(json.dumps(sub_msg))
            while True:
                data = json.loads(await ws.recv())
                if "data" in data:
                    ticker = data["data"][0]
                    self.orderbook_cache[ticker["instId"]] = {
                        "bid": float(ticker["bestBidPrice"]),
                        "ask": float(ticker["bestAskPrice"]),
                        "ts": ticker["ts"]
                    }

    async def get_market_slope_data(self, symbol: str):
        """核心增強：在獲取 K 線的同時，注入實時盤口深度"""
        kline_data = await super().get_market_slope_data(symbol)
        # 注入當前秒的盤口價差，判斷流動性是否足以支撐 AI 建議的倉位
        kline_data['realtime'] = self.orderbook_cache.get(symbol, {"bid": 0, "ask": 0})
        return kline_data
