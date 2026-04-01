import asyncio
import time
from datetime import datetime
from .agents.technician import TechnicianAgent
from .agents.risk_officer import RiskOfficer
from perception.tracker import PerformanceTracker

class Position:
    """持倉數據結構"""
    def __init__(self, symbol, side, entry, sl, tp, size):
        self.symbol = symbol
        self.side = side  # "LONG" or "SHORT"
        self.entry = entry
        self.sl = sl
        self.tp = tp
        self.size = size # 幣數

class AegisStrategy:
    def __init__(self, client):
        self.client = client
        self.positions = {}  # {symbol: PositionObject}
        self.is_running = True

        # 初始化組件
        self.technician = TechnicianAgent(api_key=getattr(client, 'api_key', ''))
        self.risk_officer = RiskOfficer(base_stake=50.0)
        self.tracker = PerformanceTracker() # 👈 自動盈虧報表器

    async def position_risk_loop(self):
        """
        🕵️ 隱形風控哨兵 (工業級增強版)
        任務：每 0.5 秒掃描價格，執行隱形止損，並自動生成 50u 盈虧報表
        """
        print("🕵️ Aegis 隱形風控哨兵已啟動，監控中...")

        while self.is_running:
            try:
                # 複製一份清單避免遍歷時刪除導致報錯
                for symbol, pos in list(self.positions.items()):
                    # 1. 從 WebSocket 緩存拿取實時盤口
                    market_info = self.client.orderbook_cache.get(symbol)
                    if not market_info:
                        continue

                    # 判斷對手價 (做多看買盤 bid, 做空看賣盤 ask)
                    current_price = market_info['bid'] if pos.side == "LONG" else market_info['ask']

                    # 2. 判斷是否觸發止損或止盈
                    is_stop_loss = (pos.side == "LONG" and current_price <= pos.sl) or \
                                   (pos.side == "SHORT" and current_price >= pos.sl)

                    is_take_profit = (pos.side == "LONG" and current_price >= pos.tp) or \
                                     (pos.side == "SHORT" and current_price <= pos.tp)

                    if is_stop_loss or is_take_profit:
                        reason = "止損" if is_stop_loss else "止盈"
                        print(f"🚨 {symbol} 觸發{reason}！立即執行市價平倉...")

                        # 3. 執行市價平倉
                        await self.client.execute_smart_order(
                            symbol=symbol,
                            side="sell" if pos.side == "LONG" else "buy",
                            size=pos.size
                        )

                        # 4. 🧮 確切計算這一單的 PNL (以 50u 為基底)
                        if pos.side == "LONG":
                            pnl = (current_price - pos.entry) * pos.size
                        else:
                            pnl = (pos.entry - current_price) * pos.size

                        # 5. 📝 寫入自動盈虧報表 (Perception 層)
                        self.tracker.record_trade(
                            symbol=symbol,
                            side=pos.side,
                            entry=pos.entry,
                            exit_price=current_price,
                            size_usdt=pos.size * pos.entry, # 實際投入總額
                            result_pnl=pnl,
                            reason=reason
                        )

                        # 6. 從監控中移除
                        del self.positions[symbol]
                        print(f"✅ {symbol} 報表已更新，移除監控。")

            except Exception as e:
                print(f"⚠️ 風控循環異常: {e}")

            await asyncio.sleep(0.5) # 0.5秒高頻掃描

    async def on_tick(self, symbol, features):
        """
        主掃描邏輯：發現斜率共振後，呼叫下方的開倉邏輯
        """
        # ... 之前的掃描邏輯 ...
        pass

    async def analyze_and_execute(self, symbol, features, confidence):
        """
        🚀 開倉決策中心：50u 基準下單
        """
        current_price = self.client.orderbook_cache.get(symbol, {}).get('bid', 0)
        if current_price == 0: return

        # 1. 透過 RiskOfficer 算錢 (以 50u 為核心)
        stake_usdt, qty = self.risk_officer.calculate_execution_size(
            balance=0, # 暫不需傳入總餘額，走基準單邏輯
            entry=current_price,
            sl=current_price * 0.985, # 示例 1.5% 止損
            ai_conf=confidence,
            atr_value=0 # 視情況傳入
        )

        # 2. 執行下單
        print(f"💰 [開倉] {symbol} | 金額: {stake_usdt} USDT")
        order_res = await self.client.execute_smart_order(
            symbol=symbol,
            side="buy", # 示例
            size=qty
        )

        # 3. 納入哨兵監控
        self.positions[symbol] = Position(
            symbol=symbol,
            side="LONG",
            entry=current_price,
            sl=current_price * 0.985,
            tp=current_price * 1.045, # 示例 4.5% 止盈
            size=qty
        )
