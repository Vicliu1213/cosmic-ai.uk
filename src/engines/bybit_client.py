class BybitClient(BaseClient):
    BASE_URL = "https://api.bybit.com"

    async def execute_iceberg_order(self, symbol, side, total_qty):
        """超越版特有：自動拆單（冰山委託）防止滑點"""
        chunk = total_qty / 10
        for _ in range(10):
            await self.request("POST", "/v5/order/create", {
                "category": "linear", "symbol": symbol, "side": side, "qty": str(chunk)
            })
            await asyncio.sleep(0.5) # 隨機化間隔
