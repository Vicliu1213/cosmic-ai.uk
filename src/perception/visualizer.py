import matplotlib.pyplot as plt
import pandas as pd

def draw_equity_curve(csv_path="logs/trading_report.csv"):
    df = pd.read_csv(csv_path)
    df['cumulative_pnl'] = df['pnl'].cumsum()

    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['cumulative_pnl'], marker='o', linestyle='-', color='lime')
    plt.title("Aegis-Bitget Equity Curve (Base 50u)")
    plt.xlabel("Time")
    plt.ylabel("Cumulative PNL (USDT)")
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("logs/equity_curve.png") # 自動保存為圖片
    print("🎨 資產曲線圖已更新：logs/equity_curve.png")
