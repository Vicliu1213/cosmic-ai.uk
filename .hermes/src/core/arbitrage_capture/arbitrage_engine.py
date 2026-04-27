from core.omega_core import OmegaSkill

class ArbitrageCapture(OmegaSkill):
    def __init__(self, fee_rate=0.001, min_spread=0.002):
        self.fee_rate = fee_rate
        self.min_spread = min_spread

    def check_spread(self, price_spot, price_future):
        spread = abs(price_future - price_spot) / price_spot
        if spread > self.fee_rate + self.min_spread:
            if price_future > price_spot:
                return {'action': 'buy_spot_sell_future', 'spread': spread}
            else:
                return {'action': 'sell_spot_buy_future', 'spread': spread}
        return None