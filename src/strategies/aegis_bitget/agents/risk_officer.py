class RiskOfficer:
    def __init__(self, base_stake=50.0):
        self.base_stake = base_stake

    def calculate_execution_size(self, current_balance, entry, sl, ai_conf):
        """
        實施凱利公式與 50u 基準保護
        """
        risk_dist = abs(entry - sl) / entry
        # 凱利公式簡化版 (f = p - q/b)
        win_rate = 0.4 + (ai_conf * 0.3) # AI 置信度轉化為預期勝率
        reward_risk_ratio = 2.0 # 假設盈虧比 2
        kelly_f = win_rate - (1 - win_rate) / reward_risk_ratio

        # 以 50u 為基數進行增減
        target_stake = self.base_stake * (1 + kelly_f)

        # 安全邊界：防止 AI 梭哈，也防止下單太小
        final_stake = max(20.0, min(150.0, target_stake))

        print(f"⚖️ [風控計算] 基準: 50u | 建議: {final_stake:.2f}u | 風險距離: {risk_dist*100:.2f}%")
        return round(final_stake, 2), final_stake / entry
