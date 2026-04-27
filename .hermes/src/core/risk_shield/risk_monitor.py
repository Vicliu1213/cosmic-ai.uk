from core.omega_core import OmegaSkill

class RiskShield(OmegaSkill):
    def __init__(self, max_slippage=0.005, max_positions=3, max_daily_loss=0.05):
        self.max_slippage = max_slippage
        self.max_positions = max_positions
        self.max_daily_loss = max_daily_loss
        self.daily_loss = 0.0
        self.active_positions = 0

    def check_order(self, entry_price, current_price):
        slip = abs(current_price - entry_price) / entry_price
        return slip <= self.max_slippage

    def can_open(self):
        return self.active_positions < self.max_positions and abs(self.daily_loss) < self.max_daily_loss

    def detect_competitor(self, symbol, price_level):
        # 模拟：如果同一价位有多个挂单，返回True
        # 实际需接入交易所订单簿深度
        return False