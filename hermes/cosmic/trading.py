import ray

@ray.remote
class TradingEngine:
    def __init__(self, config):
        self.capital = config["initial_capital"]
        self.max_position_pct = config["max_position_pct"]

    def place_order(self, symbol, quantity, side, price):
        cost = quantity * price
        if cost > self.capital * self.max_position_pct:
            return "風險拒絕"
        self.capital -= cost
        return f"下單成功: {side} {quantity} {symbol} @ {price}"
