import aiohttp
from src.models.schema import TradeSignal

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    async def send_signal(self, signal: TradeSignal):
        text = (
            f"🤖 **Aegis Signal Detected**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔥 標的: {signal.symbol} | {signal.side}\n"
            f"🎯 進場: {signal.price_entry}\n"
            f"🚀 止盈: {signal.price_tp}\n"
            f"🛡️ 止損: {signal.price_sl}\n"
            f"💪 置信度: {signal.confidence * 100}%\n"
            f"📝 理由: {signal.justification}"
        )
        async with aiohttp.ClientSession() as session:
            await session.post(self.url, data={"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"})
