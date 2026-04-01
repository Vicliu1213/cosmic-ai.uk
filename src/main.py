import asyncio
import logging
from engine.bitget_client import BitgetClient
from strategies.aegis_bitget.main import AegisStrategy
from algorithms.engine.hyperexponential_plugin import HyperexponentialGrowthPlugin
from algorithms.engine.iceberg_order import IcebergOrder

# ---------------------------------------------------------
# 🛠️ 插件註冊中心 (對齊圖片 2 的 Registry 模式)
# ---------------------------------------------------------
registry = {
    "HyperexponentialGrowthPlugin": None,
    "IcebergOrder": None,
    "AegisStrategy": None
}

async def run_system():
    # 1. 初始化底層 Client
    # 建議從加密 config 讀取：api_key, secret, passphrase
    bitget = BitgetClient(api_key="YOUR_KEY", secret="YOUR_SECRET", passphrase="...")

    # 2. 實例化所有插件並存入 Registry
    registry["HyperexponentialGrowthPlugin"] = HyperexponentialGrowthPlugin()
    registry["IcebergOrder"] = IcebergOrder(client=bitget)
    registry["AegisStrategy"] = AegisStrategy(client=bitget)

    print("⚔️ Aegis Elite v2.0 | 所有系統插件已就緒...")

    # 3. 啟動背景併發任務 (WebSocket 監聽與隱形風控)
    # 這確保了當主循環在執行 AI 分析時，風控依然在 0.5s 頻率運行
    asyncio.create_task(bitget.subscribe_market_data(["BTCUSDT", "ETHUSDT", "SOLUSDT"]))
    asyncio.create_task(registry["AegisStrategy"].position_risk_loop())

    while True:
        try:
            # 💡 執行圖片 2 的核心邏輯：超指數增長掃描
            context = {"symbol": "BTCUSDT", "client": bitget}
            result = await registry["HyperexponentialGrowthPlugin"].run(context)

            # 如果觸發「超增長」信號，執行高階冰山單
            if result.get("signal") == "hyper_growth":
                print("🚀 [警告] 偵測到超指數增長信號！啟動冰山委託執行...")
                await registry["IcebergOrder"].run(
                    symbol="BTCUSDT",
                    side="buy",
                    total_size=0.1 # 這裡可改為透過 RiskOfficer 計算出的動態倉位
                )

            # 💡 同時執行 Aegis 的 AI 斜率研調邏輯
            # 我們讓它與 Hyper-Growth 進行交叉驗證
            await registry["AegisStrategy"].on_tick()

            # 正常循環間隔
            await asyncio.sleep(10)

        except Exception as e:
            # 💡 整合圖片 1 的錯誤自癒邏輯
            print(f"❌ Critical Error: {e}")
            print("⏳ 系統將在 60 秒後嘗試重啟恢復...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    # 對齊圖片 1 的啟動入口
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        print("\n🛑 系統安全關閉中...")
