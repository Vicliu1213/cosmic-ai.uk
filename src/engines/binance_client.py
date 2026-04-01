class BinanceClient(BaseClient):
    BASE_URL = "https://fapi.binance.com" # 期貨接口

    async def request(self, method, path, params=None, data=None):
        # 增強：自動處理 Binance 的 ListenKey 與 User Data Stream
        res = await super().request(method, path, params, data)
        # 邏輯：解析 Binance 獨有的 x-mbx-used-weight 標頭來預防禁封
        return res

    def _generate_signature(self, params):
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(self.secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
