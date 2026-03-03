#!/usr/bin/env python3
"""
市場數據生成器 - 為回測生成真實感的 OHLCV 數據
Market Data Generator - Generate realistic OHLCV data for backtesting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import os
from pathlib import Path


class MarketDataGenerator:
    """生成模擬市場數據"""
    
    def __init__(self, seed: int = 42):
        """初始化數據生成器"""
        np.random.seed(seed)
        self.seed = seed
    
    def generate_price_series(
        self, 
        initial_price: float,
        days: int = 365,
        intervals_per_day: int = 24,  # 小時級別
        drift: float = 0.0005,  # 日均漂移
        volatility: float = 0.02,  # 日均波動率
        regime_changes: Optional[List[Dict]] = None
    ) -> np.ndarray:
        """
        使用幾何布朗運動生成價格序列
        
        Args:
            initial_price: 初始價格
            days: 交易天數
            intervals_per_day: 每天的時間段數
            drift: 日平均漂移
            volatility: 日平均波動率
            regime_changes: 制度變化配置 (可選)
        
        Returns:
            價格序列
        """
        total_periods = days * intervals_per_day
        dt = 1 / intervals_per_day  # 時間步長
        
        # 初始化價格數組
        prices = np.zeros(total_periods + 1)
        prices[0] = initial_price
        
        # 應用制度變化
        if regime_changes:
            regimes = self._create_regime_schedule(total_periods, regime_changes)
        else:
            regimes = np.ones(total_periods)
        
        # 生成對數收益
        for t in range(1, total_periods + 1):
            regime_vol = volatility * regimes[t - 1]
            shock = np.random.normal(drift * dt, regime_vol * np.sqrt(dt))
            prices[t] = prices[t - 1] * np.exp(shock)
        
        return prices[1:]  # 去掉初始值
    
    def _create_regime_schedule(
        self, 
        total_periods: int, 
        regime_changes: List[Dict]
    ) -> np.ndarray:
        """創建制度變化時間表"""
        regimes = np.ones(total_periods)
        
        for change in regime_changes:
            start = int(change.get('start_pct', 0) * total_periods)
            end = int(change.get('end_pct', 1) * total_periods)
            vol_multiplier = change.get('volatility_multiplier', 1.0)
            regimes[start:end] *= vol_multiplier
        
        return regimes
    
    def generate_ohlcv_data(
        self,
        symbol: str,
        initial_price: float,
        days: int = 365,
        start_date: datetime = None,
        intervals_per_day: int = 24,  # 小時數據
        drift: float = 0.0005,
        volatility: float = 0.02,
        regime_changes: Optional[List[Dict]] = None
    ) -> pd.DataFrame:
        """
        生成完整的 OHLCV 數據
        
        Args:
            symbol: 交易對符號
            initial_price: 初始價格
            days: 交易天數
            start_date: 開始日期
            intervals_per_day: 每天的區間數
            drift: 日漂移
            volatility: 日波動率
            regime_changes: 制度變化
        
        Returns:
            OHLCV DataFrame
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=days)
        
        # 生成基礎價格序列
        prices = self.generate_price_series(
            initial_price, days, intervals_per_day, drift, volatility, regime_changes
        )
        
        # 為每個價格生成 OHLCV
        ohlcv_data = []
        period_duration = timedelta(hours=24 // intervals_per_day)
        
        for i, price in enumerate(prices):
            current_time = start_date + i * period_duration
            
            # 生成開高低收
            open_price = price * np.random.uniform(0.99, 1.01)
            high = max(open_price, price) * np.random.uniform(1.0, 1.015)
            low = min(open_price, price) * np.random.uniform(0.985, 1.0)
            close = price
            
            # 生成交易量 (與波動率相關)
            volume = np.random.uniform(10000, 50000) * (1 + abs(np.random.normal(0, 0.3)))
            
            ohlcv_data.append({
                'timestamp': current_time,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': round(volume, 2)
            })
        
        df = pd.DataFrame(ohlcv_data)
        df['symbol'] = symbol
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def generate_multiple_symbols(
        self,
        symbols_config: Dict[str, Dict],
        days: int = 365,
        start_date: datetime = None
    ) -> Dict[str, pd.DataFrame]:
        """
        生成多個交易對的數據
        
        Args:
            symbols_config: 交易對配置字典
            days: 交易天數
            start_date: 開始日期
        
        Returns:
            交易對名稱 -> DataFrame 的字典
        """
        data = {}
        
        for symbol, config in symbols_config.items():
            print(f"生成 {symbol} 數據...")
            df = self.generate_ohlcv_data(
                symbol=symbol,
                initial_price=config.get('initial_price', 50000),
                days=days,
                start_date=start_date,
                drift=config.get('drift', 0.0005),
                volatility=config.get('volatility', 0.02),
                regime_changes=config.get('regime_changes')
            )
            data[symbol] = df
        
        return data
    
    def save_to_csv(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: str = './data/market_data'
    ) -> None:
        """保存數據到 CSV 文件"""
        os.makedirs(output_dir, exist_ok=True)
        
        for symbol, df in data.items():
            filename = os.path.join(output_dir, f"{symbol.replace('/', '_')}.csv")
            df.to_csv(filename)
            print(f"✅ 已保存: {filename}")


def generate_default_market_data(
    output_dir: str = './data/market_data'
) -> Dict[str, pd.DataFrame]:
    """生成默認市場數據集"""
    
    generator = MarketDataGenerator(seed=42)
    
    # 配置多個交易對
    symbols_config = {
        'BTC/USDT': {
            'initial_price': 45000,
            'drift': 0.0008,
            'volatility': 0.025,
            'regime_changes': [
                {'start_pct': 0.3, 'end_pct': 0.6, 'volatility_multiplier': 1.5},  # 高波動期
                {'start_pct': 0.7, 'end_pct': 0.9, 'volatility_multiplier': 0.8},  # 低波動期
            ]
        },
        'ETH/USDT': {
            'initial_price': 2500,
            'drift': 0.0010,
            'volatility': 0.030,
            'regime_changes': [
                {'start_pct': 0.25, 'end_pct': 0.55, 'volatility_multiplier': 1.3},
            ]
        },
        'BNB/USDT': {
            'initial_price': 600,
            'drift': 0.0006,
            'volatility': 0.022,
        },
        'ADA/USDT': {
            'initial_price': 1.0,
            'drift': 0.0004,
            'volatility': 0.028,
        },
        'SOL/USDT': {
            'initial_price': 150,
            'drift': 0.0012,
            'volatility': 0.035,
        },
        'XRP/USDT': {
            'initial_price': 2.5,
            'drift': 0.0003,
            'volatility': 0.020,
        }
    }
    
    # 生成數據
    data = generator.generate_multiple_symbols(
        symbols_config=symbols_config,
        days=365,
        start_date=datetime.now() - timedelta(days=365)
    )
    
    # 保存到 CSV
    generator.save_to_csv(data, output_dir)
    
    return data


if __name__ == '__main__':
    print("🚀 正在生成市場數據...")
    data = generate_default_market_data()
    print(f"\n✅ 生成完成！共 {len(data)} 個交易對")
    
    # 打印樣本
    for symbol, df in data.items():
        print(f"\n{symbol} 樣本:")
        print(df.head())
