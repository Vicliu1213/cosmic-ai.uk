import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class TradeMemory:
    def __init__(self):
        self.history = [] # 格式: {"vector": [], "pnl": float}

    def add_experience(self, tech_details, pnl):
        # 將斜率轉為特徵向量
        vector = [tech_details['15m']['slope'], tech_details['1h']['slope'], tech_details['4h']['slope']]
        self.history.append({"vector": vector, "pnl": pnl})

    def match_history(self, current_tech):
        if not self.history: return 0.5
        curr_vec = [current_tech['15m']['slope'], current_tech['1h']['slope'], current_tech['4h']['slope']]
        past_vecs = [item['vector'] for item in self.history]

        # 計算餘弦相似度
        sims = cosine_similarity([curr_vec], past_vecs)[0]
        # 找出相似度 > 0.9 的平均表現
        relevant_pnl = [self.history[i]['pnl'] for i, s in enumerate(sims) if s > 0.9]

        if not relevant_pnl: return 0.5
        win_rate = len([p for p in relevant_pnl if p > 0]) / len(relevant_pnl)
        return win_rate
