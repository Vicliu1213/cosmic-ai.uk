class OkxClient(BaseClient):
    BASE_URL = "https://www.okx.com"

    def _get_headers(self, method, path, payload):
        ts = datetime.utcnow().isoformat()[:-3] + 'Z'
        # OKX 簽名需要帶上完整的 ISO 時間戳
        # 實作略... (與 Bitget 類似但格式不同)
        pass

    async def get_liquidation_map(self, symbol):
        """OKX 特有：獲取爆倉地圖數據，供 Researcher Agent 參考"""
        return await self.request("GET", "/api/v5/public/liquidation-orders", {"instId": symbol})
