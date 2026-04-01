import aiohttp

class Researcher:
    def __init__(self):
        self.fg_api = "https://api.alternative.me/fng/" # Fear & Greed Index

    async def get_market_sentiment(self):
        """
        獲取情緒指標：當 F&G > 80 (極度貪婪) 或 < 20 (極度恐懼) 時發出警告
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.fg_api) as resp:
                    data = await resp.json()
                    value = int(data['data'][0]['value'])
                    classification = data['data'][0]['value_classification']

                    # 邏輯：情緒過熱時，強制降低 AI 置信度
                    sentiment_score = 1.0
                    if value > 80: sentiment_score = 0.7  # 貪婪風險
                    if value < 20: sentiment_score = 0.8  # 恐慌風險

                    return {
                        "fng_value": value,
                        "classification": classification,
                        "sentiment_modifier": sentiment_score,
                        "market_regime": "TRENDING" if 40 <= value <= 60 else "VOLATILE"
                    }
        except:
            return {"sentiment_modifier": 1.0, "market_regime": "UNKNOWN"}
