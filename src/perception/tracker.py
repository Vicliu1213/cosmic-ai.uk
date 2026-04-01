import time
import pandas as pd
from datetime import datetime

class PerformanceTracker:
    def __init__(self, report_path="logs/trading_report.csv"):
        self.report_path = report_path
        self.trades = []
        self.base_stake = 50.0

    def record_trade(self, symbol, side, entry, exit_price, size_usdt, result_pnl, reason):
        """
        當 position_risk_loop 平倉時呼叫此函數
        """
        trade_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "side": side,
            "entry": entry,
            "exit": exit_price,
            "size": size_usdt,
            "pnl": round(result_pnl, 4),
            "pnl_pct": round((result_pnl / size_usdt) * 100, 2),
            "reason": reason # 隱形止損 / 自動止盈
        }
        self.trades.append(trade_data)
        self._save_to_csv(trade_data)
        self.generate_summary()

    def _save_to_csv(self, data):
        df = pd.DataFrame([data])
        # 如果檔案不存在則建立並寫入標題，否則追加
        df.to_csv(self.report_path, mode='a', index=False, header=not pd.io.common.file_exists(self.report_path))

    def generate_summary(self):
        """
        在終端機輸出「確切效果」的可視化報表
        """
        if not self.trades: return

        df = pd.DataFrame(self.trades)
        total_pnl = df['pnl'].sum()
        win_rate = (df['pnl'] > 0).sum() / len(df) * 100

        print("\n" + "="*45)
        print(f"📊  AEGIS 實時戰報 | {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 45)
        print(f"💰 累計總盈虧: {total_pnl:.2f} USDT")
        print(f"📈 勝率: {win_rate:.1f}% | 總交易次數: {len(df)}")
        print(f"⚖️ 平均每單盈虧: {(total_pnl/len(df)):.2f} USDT")
        print(f"🔥 最近一筆: {df.iloc[-1]['symbol']} ({df.iloc[-1]['pnl_pct']}%) - {df.iloc[-1]['reason']}")
        print("="*45 + "\n")
