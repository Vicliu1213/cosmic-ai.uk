import os
import time
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException

class DataInterface:
    def __init__(self, config):
        """
        初始化數據接口
        config: 從YAML載入的配置字典
        """
        self.config = config
        self.type = config.get("type", "binance")  # 預設使用binance

        # 初始化Binance客戶端（不需要API金鑰也能獲取公開市場數據）
        # 但如果要避免速率限制，建議還是申請免費的API金鑰
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")

        try:
            self.client = Client(api_key, api_secret)
            # 測試連線
            self.client.get_server_time()
            print("✅ Binance API 連線成功")
        except Exception as e:
            print(f"⚠️ Binance API 連線失敗，使用模擬模式: {e}")
            self.client = None
            self.type = "simulated"

        # 緩存設置
        self.cache = {}          # 價格緩存
        self.cache_time = {}     # 緩存時間戳
        self.klines_cache = {}    # K線數據緩存

        # 模擬數據（當API失敗時使用）
        self.simulated_data = {
            "BTC/USDT": 50000,
            "ETH/USDT": 3000,
            "BNB/USDT": 400,
            "SOL/USDT": 100
        }

    def _format_symbol(self, symbol):
        """
        將交易對格式轉換為Binance格式
        例如: BTC/USD -> BTCUSDT, ETH/USD -> ETHUSDT
        """
        # 移除斜線並確保是USDT交易對
        base = symbol.split('/')[0].upper()
        # 常見的穩定幣映射
        stable_map = {
            "USD": "USDT",
            "USDT": "USDT",
            "USDC": "USDC",
            "BUSD": "BUSD"
        }
        quote = symbol.split('/')[1].upper() if '/' in symbol else "USDT"
        quote = stable_map.get(quote, quote)

        return f"{base}{quote}"

    def get_price(self, symbol):
        """
        獲取單一交易對的即時價格
        """
        # 檢查緩存（10秒有效期）
        now = time.time()
        if symbol in self.cache and now - self.cache_time.get(symbol, 0) < 10:
            return self.cache[symbol]

        if self.type == "simulated" or self.client is None:
            # 使用模擬數據
            price = self.simulated_data.get(symbol, 50000)
        else:
            try:
                binance_symbol = self._format_symbol(symbol)
                ticker = self.client.get_symbol_ticker(symbol=binance_symbol)
                price = float(ticker['price'])
            except BinanceAPIException as e:
                print(f"Binance API錯誤: {e}")
                price = self.simulated_data.get(symbol, 50000)
            except Exception as e:
                print(f"獲取價格失敗: {e}")
                price = self.simulated_data.get(symbol, 50000)

        # 更新緩存
        self.cache[symbol] = price
        self.cache_time[symbol] = now
        return price

    def get_historical_klines(self, symbol, interval='1h', start_str=None, end_str=None, limit=500):
        """
        獲取歷史K線數據，用於回測

        參數:
            symbol: 交易對 (如 "BTC/USD")
            interval: K線間隔，可選: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
            start_str: 開始時間，格式: "1 Dec, 2020" 或 "2020-12-01"
            end_str: 結束時間，格式同上
            limit: 每次請求的最大數量 (預設500，最大1000)

        返回:
            pandas DataFrame，包含 open, high, low, close, volume 等欄位
        """
        if self.type == "simulated" or self.client is None:
            print("⚠️ 使用模擬K線數據（僅供測試）")
            return self._generate_simulated_klines(symbol, interval, limit)

        try:
            binance_symbol = self._format_symbol(symbol)

            # 轉換間隔格式
            interval_map = {
                '1m': Client.KLINE_INTERVAL_1MINUTE,
                '3m': Client.KLINE_INTERVAL_3MINUTE,
                '5m': Client.KLINE_INTERVAL_5MINUTE,
                '15m': Client.KLINE_INTERVAL_15MINUTE,
                '30m': Client.KLINE_INTERVAL_30MINUTE,
                '1h': Client.KLINE_INTERVAL_1HOUR,
                '2h': Client.KLINE_INTERVAL_2HOUR,
                '4h': Client.KLINE_INTERVAL_4HOUR,
                '6h': Client.KLINE_INTERVAL_6HOUR,
                '8h': Client.KLINE_INTERVAL_8HOUR,
                '12h': Client.KLINE_INTERVAL_12HOUR,
                '1d': Client.KLINE_INTERVAL_1DAY,
                '3d': Client.KLINE_INTERVAL_3DAY,
                '1w': Client.KLINE_INTERVAL_1WEEK,
                '1M': Client.KLINE_INTERVAL_1MONTH
            }
            binance_interval = interval_map.get(interval, Client.KLINE_INTERVAL_1HOUR)

            # 獲取歷史K線
            klines = self.client.get_historical_klines(
                binance_symbol,
                binance_interval,
                start_str,
                end_str,
                limit=limit
            )

            # 轉換為DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])

            # 只保留需要的欄位並轉換類型
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])

            # 轉換時間戳
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            print(f"✅ 下載 {len(df)} 條 {symbol} {interval} K線數據")
            return df

        except Exception as e:
            print(f"獲取歷史K線失敗: {e}")
            return self._generate_simulated_klines(symbol, interval, limit)

    def _generate_simulated_klines(self, symbol, interval='1h', limit=500):
        """
        生成模擬的K線數據（用於測試）
        """
        import numpy as np

        # 生成隨機價格序列
        base_price = self.simulated_data.get(symbol, 50000)
        dates = pd.date_range(end=datetime.now(), periods=limit, freq=interval.replace('m', 'T').replace('h', 'H').replace('d', 'D'))

        # 隨機遊走
        returns = np.random.randn(limit) * 0.02
        prices = base_price * np.exp(np.cumsum(returns))

        df = pd.DataFrame(index=dates)
        df['open'] = prices
        df['high'] = prices * (1 + abs(np.random.randn(limit) * 0.01))
        df['low'] = prices * (1 - abs(np.random.randn(limit) * 0.01))
        df['close'] = prices * (1 + np.random.randn(limit) * 0.005)
        df['volume'] = np.random.randint(100, 10000, limit)

        return df

    def download_backtest_data(self, symbol, interval='1h', days=30, save_to=None):
        """
        下載回測數據並可選儲存為CSV

        參數:
            symbol: 交易對
            interval: K線間隔
            days: 下載最近幾天的數據
            save_to: 如果提供，儲存到指定路徑

        返回:
            pandas DataFrame
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_str = start_date.strftime("%d %b, %Y")
        end_str = end_date.strftime("%d %b, %Y")

        print(f"📥 下載 {symbol} 從 {start_str} 到 {end_str} 的 {interval} 數據...")

        df = self.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_str,
            end_str=end_str
        )

        if save_to and df is not None:
            df.to_csv(save_to)
            print(f"💾 數據已儲存至: {save_to}")

        return df

    def get_multiple_prices(self, symbols):
        """
        批量獲取多個交易對的價格
        """
        prices = {}
        for symbol in symbols:
            prices[symbol] = self.get_price(symbol)
        return prices


# 使用範例（測試用）
if __name__ == "__main__":
    # 簡單測試
    config = {"type": "binance"}
    di = DataInterface(config)

    # 測試即時價格
    btc_price = di.get_price("BTC/USD")
    print(f"BTC/USD 即時價格: {btc_price}")

    # 測試歷史數據下載
    df = di.download_backtest_data("BTC/USD", interval="1h", days=7, save_to="btc_7d.csv")
    if df is not None:
        print(df.head())
