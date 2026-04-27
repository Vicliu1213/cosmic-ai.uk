import json
import time
from collections import defaultdict

class MemoryMatrix:
    def __init__(self):
        self.l1 = {}      # 当前持仓/订单
        self.l2 = []      # 短期记忆 (maxlen=1000)
        self.l3 = {}      # 长期记忆 {pattern_hash: {'action':..., 'confidence':..., 'last_seen':...}}

    def recall(self, vector, top_k=5):
        # 简化的余弦相似度召回
        candidates = []
        for ph, item in self.l3.items():
            # 实际计算相似度
            candidates.append((item['confidence'] * (0.99 ** (time.time()-item['last_seen'])), item))
        candidates.sort(reverse=True)
        return [c[1] for c in candidates[:top_k]]

    def commit(self, pattern, outcome, win):
        if win:
            conf = min(1.0, pattern.get('confidence', 0.5) + 0.05)
            self.l3[pattern['hash']] = {'action': pattern['action'], 'confidence': conf, 'last_seen': time.time()}
        else:
            # 亏损模式，降低置信度，若低于0.3则删除
            pass

    def forget(self):
        now = time.time()
        self.l3 = {k:v for k,v in self.l3.items() if now - v['last_seen'] < 7*86400}