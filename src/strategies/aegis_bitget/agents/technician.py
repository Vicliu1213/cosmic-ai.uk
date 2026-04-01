import numpy as np
from scipy.stats import linregress

class Technician:
    async def get_slope_resonance(self, symbol, klines_dict):
        """
        klines_dict: {'15m': [...], '1h': [...], '4h': [...]}
        返回: 共振置信度與物理加速度
        """
        results = {}
        for tf, data in klines_dict.items():
            y = np.array([float(k[4]) for k in data]) # 收盤價
            x = np.arange(len(y))
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            results[tf] = {"slope": slope, "r2": r_value**2}

        # 核心判斷：三週期方向一致且 R2 > 0.8
        is_resonant = (results['15m']['slope'] * results['1h']['slope'] > 0) and \
                      (results['1h']['slope'] * results['4h']['slope'] > 0) and \
                      (results['15m']['r2'] > 0.8)

        print(f"📊 [技術掃描] {symbol} | 15M R2: {results['15m']['r2']:.2f} | 共振: {is_resonant}")
        return {
            "is_resonant": is_resonant,
            "acceleration": results['15m']['slope'] / results['1h']['slope'] if results['1h']['slope'] != 0 else 0,
            "details": results
        }
