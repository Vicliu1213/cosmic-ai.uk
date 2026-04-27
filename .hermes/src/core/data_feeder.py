import random
import time

class DataFeeder:
    def stream(self):
        while True:
            yield {
                'symbol': 'BTC/USDT',
                'buy_vol': random.uniform(10, 100),
                'sell_vol': random.uniform(10, 100),
                'price_ticks': [50000 + i*0.5 for i in range(5)],
                'spread': 1.0
            }
            time.sleep(0.001)   # 1ms tick