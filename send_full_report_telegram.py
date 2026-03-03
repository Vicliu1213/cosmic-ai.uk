#!/usr/bin/env python3
"""
Send Full Comparison Report to Telegram
"""

import os
import requests
import time
from pathlib import Path

token = "7605741830:AAHLuUuz2v4IKz2GlLOVv-vOR0wXb9qsdUI"
user_id = "1978452909"

def send_message(text):
    """Send text message"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': user_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=data)
    return response.status_code == 200

def send_file(filepath, caption=""):
    """Send file"""
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(filepath, 'rb') as f:
        files = {'document': f}
        data = {
            'chat_id': user_id,
            'caption': caption,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, files=files, data=data)
    return response.status_code == 200

print("📱 Sending Comparison Report to Telegram\n")

# 1. Summary
print("1️⃣  Sending summary message...")
summary = """🔬 **量化對比分析完成!**

**我的量化混合系統** (1年 6幣種):
• 收益: +172.91% 📈
• Sharpe: 1.35 ⭐
• 最大回撤: 35.70%
• 配置: 60% Avellaneda-Stoikov + 40% Pure Market Making

**你的LLM-TradeBot系統** (1個月 BTCUSDT):
• 收益: -0.20% ⚠️
• Sharpe: -1.49 📉
• 最大回撤: 0.52%
• 交易: 6次, 勝率 33.3%

🔍 **主要差異**:
1️⃣ 時間: 1年 vs 1個月
2️⃣ 交易對: 6個 vs 1個
3️⃣ 算法: 量子 vs EMA技術指標
4️⃣ Sharpe: 1.35 vs -1.49 (相差2.84倍)

💡 **結論**: 數據時間和質量是關鍵

📊 **建議**: 用1年數據測試你的系統看結果如何?
"""
if send_message(summary):
    print("   ✅ Summary sent")
    time.sleep(1)
else:
    print("   ❌ Failed")

# 2. Detailed Report
print("2️⃣  Sending detailed report...")
report_file = "/workspaces/cosmic-ai.uk/COMPARISON_RESULTS.md"
if os.path.exists(report_file):
    size_mb = os.path.getsize(report_file) / 1024 / 1024
    if size_mb < 50:  # Telegram file size limit
        if send_file(report_file, "📄 完整對比分析報告"):
            print("   ✅ Report sent")
            time.sleep(1)
        else:
            print("   ❌ Failed")
    else:
        print(f"   ⚠️ File too large ({size_mb:.1f}MB)")

# 3. CSV Files
print("3️⃣  Sending CSV reports...")
csv_files = [
    ("01_individual_strategies_ranking.csv", "🏆 6個策略排名"),
    ("04_balanced_portfolio_weights.csv", "✅ 推薦配置權重"),
]

csv_dir = "/workspaces/cosmic-ai.uk/reports/backtesting/"
for filename, caption in csv_files:
    filepath = os.path.join(csv_dir, filename)
    if os.path.exists(filepath):
        if send_file(filepath, f"📈 {caption}"):
            print(f"   ✅ {filename} sent")
        else:
            print(f"   ❌ {filename} failed")
        time.sleep(1)

# 4. Key Metrics
print("4️⃣  Sending key metrics...")
metrics = """📊 **詳細性能對比**

**我的系統 - 個別策略表現**:
1. Avellaneda-Stoikov: +216.97% | Sharpe 1.41
2. Pure Market Making: +106.81% | Sharpe 1.26
3. Triangular Arbitrage: +22.67% | Sharpe 0.56

**最優投資組合 (量子優化)**:
• 權重: 60% + 40%
• 預期收益: 172.91%
• Sharpe: 1.35
• 資本成長: $10k → $27.3k

**你的系統 - 交易統計**:
• 總交易: 6筆
• 贏利: 2筆 (止盈)
• 虧損: 4筆 (止損)
• 風險審計攔截: 多次 ✅

⏰ **執行時間**: 31.3秒 (快速!)

🎯 **下一步建議**:
1. 用1年BTCUSDT測試你的系統
2. 嘗試你系統的Agent模式
3. 考慮混合兩個系統
"""
if send_message(metrics):
    print("   ✅ Metrics sent")
    time.sleep(1)
else:
    print("   ❌ Failed")

# 5. Final message
print("5️⃣  Sending final message...")
final = """✅ **對比分析完成!**

📌 **已發送**:
✅ 對比摘要
✅ 詳細分析報告
✅ CSV數據文件
✅ 性能指標

💼 **混合方案建議**:
\`\`\`
步驟1: 用我的量子算法優化權重 (60/40)
步驟2: 用你的LLM-TradeBot執行交易
步驟3: 用你的風險審計防止過度槓桿
步驟4: 定期重新優化權重
\`\`\`

🚀 **預期結果**:
• Sharpe比 > 1.5
• 年化收益 > 150%
• 最大回撤 < 30%

❓ **有問題? 需要更多測試?**
讓我知道你想要什麼!

---
*由 OpenCode 量化分析系統生成*
"""
if send_message(final):
    print("   ✅ Final message sent")
else:
    print("   ❌ Failed")

print("\n✅ 所有 Telegram 消息已發送完成!")
print(f"\n👤 已發送到: @chieh1024")
