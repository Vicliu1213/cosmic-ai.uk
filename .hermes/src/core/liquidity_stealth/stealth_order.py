import random
import numpy as np

class LiquidityStealth:
    def split_order(self, total_qty, price, imbalance, max_parts=20):
        if imbalance > 0.7:
            num_parts = random.randint(10, max_parts)
        else:
            num_parts = random.randint(3, 8)
        sizes = np.random.dirichlet(np.ones(num_parts)) * total_qty
        sizes = [round(s, 2) for s in sizes]
        # 随机时间间隔（毫秒）
        delays = [random.uniform(0.5, 2.0) for _ in range(num_parts)]
        return [{'qty': q, 'price': price, 'delay_ms': d} for q, d in zip(sizes, delays)]