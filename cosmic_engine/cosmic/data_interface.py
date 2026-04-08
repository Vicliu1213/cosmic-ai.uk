class DataInterface:
    def __init__(self, config):
        self.config = config
        self.type = config["type"]
        if self.type == "simulated":
            self.data = {"BTC/USD": 50000, "ETH/USD": 3000}
        elif self.type == "openbb":
            # 初始化 OpenBB 客戶端（需安裝 openbb）
            pass

    def get_price(self, symbol):
        if self.type == "simulated":
            return self.data.get(symbol, 0)
        return 0
