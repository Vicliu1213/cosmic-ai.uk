"""金融大鰐分布式交易艦隊"""

import ray
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


@ray.remote
class CrocodileTrader:
    def __init__(self, trader_id: str, symbol: str, trading_cfg: dict, risk_cfg: dict):
        from agents.divine_financial_crocodile import CoherentTradingRunner, RiskLimits, DryRunBroker
        self.trader_id = trader_id
        self.symbol = symbol
        self.dry_run = trading_cfg.get("dry_run", True)
        limits = RiskLimits(
            max_position_fraction=risk_cfg.get("max_position_pct", 0.10),
            risk_per_trade=risk_cfg.get("risk_per_trade", 0.01),
            max_daily_drawdown=risk_cfg.get("max_daily_drawdown", 0.03),
            min_confidence=risk_cfg.get("signal_confidence_min", 0.55),
        )
        broker = DryRunBroker(initial_cash=trading_cfg.get("initial_capital", 100000) / 5)
        self.runner = CoherentTradingRunner(broker=broker, risk_limits=limits, live_trading_enabled=not self.dry_run)
        self.cycle_count = 0
        logger.info(f"  🐊 {trader_id} on {symbol}")

    def trade_cycle(self, market_data: dict = None) -> dict:
        import asyncio
        if market_data is None:
            from agents.divine_financial_crocodile import generate_synthetic_market
            market_data = generate_synthetic_market(days=1)
        result = asyncio.run(self.runner.trading_cycle(market_data, symbol=self.symbol))
        self.cycle_count += 1
        return {
            "trader_id": self.trader_id,
            "symbol": self.symbol,
            "cycle": self.cycle_count,
            "signal": result["signal"],
            "risk": result["risk"],
            "execution": result["execution"],
            "portfolio": result["portfolio"],
        }

    def get_status(self) -> dict:
        return self.runner.get_absolute_status()


class CrocodileFleet:
    def __init__(self, config: dict):
        self.config = config
        self.traders: List[Any] = []

    def deploy(self) -> List[Any]:
        symbols = self.config.get("symbols", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"])
        trading_cfg = self.config
        self.traders = []
        for i, sym in enumerate(symbols):
            t = CrocodileTrader.remote(f"CROC-{i+1}", sym, trading_cfg, self.config)
            self.traders.append(t)
        logger.info(f"🐊 Fleet deployed: {len(self.traders)} traders")
        return self.traders

    def run_cycle(self) -> List[dict]:
        refs = [t.trade_cycle.remote() for t in self.traders]
        try:
            return ray.get(refs, timeout=30)
        except Exception as e:
            logger.warning(f"Fleet cycle failed: {e}")
            return []

    def get_status(self) -> List[dict]:
        refs = [t.get_status.remote() for t in self.traders]
        try:
            return ray.get(refs, timeout=10)
        except Exception as e:
            return [{"error": str(e)}] * len(self.traders)
