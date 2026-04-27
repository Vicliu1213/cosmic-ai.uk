import threading
from core.log_manager import LogManager
from core.notifier import AsyncTelegramNotifier
from core.data_feeder import DataFeeder
from skills.active.orderflow_hunt.hunt_engine import OrderFlowHunt
from skills.active.arbitrage_capture.arbitrage_engine import ArbitrageCapture
from skills.active.liquidity_stealth.stealth_order import LiquidityStealth
from skills.passive.risk_shield.risk_monitor import RiskShield
from skills.passive.memory_matrix.memory_core import MemoryMatrix
from skills.passive.self_evolve.evolution_engine import SelfEvolve

class OmegaCore:
    _instance = None

    @staticmethod
    def get_instance():
        if OmegaCore._instance is None:
            OmegaCore._instance = OmegaCore()
        return OmegaCore._instance

    def __init__(self):
        self.log_manager = LogManager()
        self.notifier = AsyncTelegramNotifier(token="YOUR_TOKEN", chat_id="YOUR_ID")
        self.memory = MemoryMatrix()
        self.risk_shield = RiskShield()
        self.hunt_engine = OrderFlowHunt(self.memory)
        self.arbitrage = ArbitrageCapture()
        self.stealth = LiquidityStealth()
        self.evolve = SelfEvolve(trade_history=[])
        self.active_tasks = []
        self.passive_monitors = [self.risk_shield, self.memory]

    def calculate_trade_setup(self, entry_price, atr, adx=None):
        dynamic_mult = 2.1 if (atr/entry_price) < 0.02 else 2.5
        sl = entry_price - atr * dynamic_mult
        rr = 2.2 if adx and adx > 30 else 1.5
        tp = entry_price + (entry_price - sl) * rr
        sl_pct = (entry_price - sl)/entry_price
        lev = 0.02 / sl_pct if sl_pct>0 else 10
        return {'entry':entry_price, 'sl':sl, 'tp':tp, 'leverage':min(lev,20), 'risk_reward':rr}

    def on_tick(self, symbol, tick_data):
        # 调用主动技能
        opp = self.hunt_engine.evaluate(symbol, tick_data['buy_vol'], tick_data['sell_vol'],
                                        tick_data['price_ticks'], tick_data['spread'])
        if opp and self.risk_shield.check_order(opp['entry'], tick_data['price_ticks'][-1]):
            # 隐蔽下单
            orders = self.stealth.split_order(0.01, opp['entry'], opp['confidence'])
            self.notifier.send_opportunity(opp)
            # 实际下单逻辑...
            self.memory.commit(opp, win=None)  # 待成交后更新

    def run(self):
        feeder = DataFeeder()
        for tick in feeder.stream():
            self.on_tick(tick['symbol'], tick)