import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

class AdaptiveTimer:
    """自适应定时触发器 - 根据市场状态动态调整触发频率"""

    def __init__(self, base_interval: int = 180):  # 默认3分钟
        self.base_interval = base_interval  # 秒
        self.volatility_window = []  # 存储最近N次波动率
        self.trigger_count = 0
        self.last_trigger = None
        self.market_state = "normal"

    async def run(self, callback, market_data_provider):
        """主循环，动态调整间隔"""
        while True:
            try:
                # 执行核心逻辑
                start_time = datetime.now()
                await callback()
                elapsed = (datetime.now() - start_time).total_seconds()

                # 根据市场波动率调整下次触发时间
                volatility = await self._get_market_volatility(market_data_provider)
                next_interval = self._calculate_next_interval(volatility, elapsed)

                logging.info(f"触发器执行耗时: {elapsed:.2f}s, 下次触发: {next_interval:.0f}s")
                await asyncio.sleep(max(next_interval, 10))  # 至少10秒

            except Exception as e:
                logging.error(f"触发器异常: {e}")
                await asyncio.sleep(30)  # 异常后等待30秒重试

    async def _get_market_volatility(self, provider) -> float:
        """获取当前市场波动率"""
        try:
            # 获取最近1小时K线
            klines = await provider.get_klines(symbol="BTCUSDT", interval="1m", limit=60)
            if len(klines) >= 10:
                returns = np.diff([float(k[4]) for k in klines[-10:]]) / [float(k[4]) for k in klines[-10:-1]]
                volatility = np.std(returns)
                self.volatility_window.append(volatility)
                if len(self.volatility_window) > 20:
                    self.volatility_window.pop(0)
                return volatility
        except:
            pass
        return 0.01  # 默认波动率

    def _calculate_next_interval(self, volatility: float, last_elapsed: float) -> int:
        """计算下次触发间隔"""
        # 波动率越高，触发越频繁
        volatility_factor = min(2.0, max(0.5, 1.0 / (volatility * 100 + 0.5)))

        # 根据执行时间调整
        if last_elapsed > self.base_interval * 0.8:
            # 执行耗时过长，增加间隔
            time_factor = 1.2
        else:
            time_factor = 1.0

        # 市场状态调整
        if volatility > 0.02:  # 高波动
            self.market_state = "high_volatility"
            interval = int(self.base_interval * 0.5 * volatility_factor * time_factor)
        elif volatility > 0.005:  # 中等波动
            self.market_state = "normal"
            interval = int(self.base_interval * volatility_factor * time_factor)
        else:  # 低波动
            self.market_state = "low_volatility"
            interval = int(self.base_interval * 1.5 * volatility_factor * time_factor)

        return max(interval, 30)  # 至少30秒，最多5分钟p
