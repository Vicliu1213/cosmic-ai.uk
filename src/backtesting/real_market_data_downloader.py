#!/usr/bin/env python3
"""
Real Market Data Downloader
真實市場數據下載器 - 從多個交易所下載實時K線數據

支持的交易所:
- Binance (binance)
- Kraken (kraken)
- Coinbase (coinbase)
- Bitget (bitget)
"""

import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time

try:
    import ccxt
except ImportError:
    print("安裝 ccxt: pip install ccxt")
    raise

logger = logging.getLogger(__name__)

class RealMarketDataDownloader:
    """真實市場數據下載器"""
    
    def __init__(self, cache_dir: str = "./market_data_cache"):
        """
        初始化下載器
        
        Args:
            cache_dir: 數據快取目錄
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize exchanges
        self.exchanges = {
            'binance': ccxt.binance(),
            'kraken': ccxt.kraken(),
            'coinbase': ccxt.coinbase(),
            'bitget': ccxt.bitget()
        }
        
        # Symbol mapping for different exchanges
        self.symbol_mapping = {
            'binance': {
                'BTC/USD': 'BTC/USDT',
                'ETH/USD': 'ETH/USDT',
                'BNB/USD': 'BNB/USDT'
            },
            'bitget': {
                'BTC/USD': 'BTC/USDT',
                'ETH/USD': 'ETH/USDT',
                'BNB/USD': 'BNB/USDT'
            },
            'kraken': {
                'BTC/USD': 'BTC/USD',
                'ETH/USD': 'ETH/USD',
                'BNB/USD': 'BNB/USD'  # 可能不支持，會跳過
            },
            'coinbase': {
                'BTC/USD': 'BTC-USD',
                'ETH/USD': 'ETH-USD',
                'BNB/USD': 'BNB-USD'  # 可能不支持，會跳過
            }
        }
    
    def _get_cache_path(self, exchange: str, symbol: str, timeframe: str) -> Path:
        """獲取快取文件路徑"""
        safe_symbol = symbol.replace('/', '_')
        filename = f"{exchange}_{safe_symbol}_{timeframe}.json"
        return self.cache_dir / filename
    
    def _load_from_cache(self, exchange: str, symbol: str, timeframe: str, max_age_hours: int = 24) -> Optional[List]:
        """從快取加載數據"""
        cache_path = self._get_cache_path(exchange, symbol, timeframe)
        
        if not cache_path.exists():
            return None
        
        # 檢查快取年齡
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age > max_age_hours * 3600:
            logger.info(f"快取已過期: {cache_path.name}")
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                logger.info(f"✓ 從快取加載 {len(data)} 根K線: {exchange} {symbol}")
                return data
        except Exception as e:
            logger.warning(f"快取加載失敗: {e}")
            return None
    
    def _save_to_cache(self, exchange: str, symbol: str, timeframe: str, data: List):
        """保存數據到快取"""
        cache_path = self._get_cache_path(exchange, symbol, timeframe)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
                logger.info(f"✓ 已保存到快取: {cache_path.name} ({len(data)} 根K線)")
        except Exception as e:
            logger.warning(f"快取保存失敗: {e}")
    
    def download_klines(
        self,
        exchange: str,
        symbol: str,
        timeframe: str = '1h',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        use_cache: bool = True,
        max_retries: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """
        下載K線數據
        
        Args:
            exchange: 交易所 (binance/kraken/coinbase)
            symbol: 交易對 (BTC/USD, ETH/USD等)
            timeframe: 時間框架 ('1m', '5m', '1h', '1d等)
            start_date: 開始日期
            end_date: 結束日期
            use_cache: 是否使用快取
            max_retries: 最大重試次數
        
        Returns:
            K線數據列表
        """
        
        # 檢查快取
        if use_cache:
            cached_data = self._load_from_cache(exchange, symbol, timeframe)
            if cached_data:
                return cached_data
        
        # 標準化交易對
        if exchange in self.symbol_mapping:
            actual_symbol = self.symbol_mapping[exchange].get(symbol, symbol)
        else:
            actual_symbol = symbol
        
        if exchange not in self.exchanges:
            logger.error(f"不支持的交易所: {exchange}")
            return None
        
        exch = self.exchanges[exchange]
        
        # 默認時間範圍
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        logger.info(f"下載 {exchange} {symbol} {timeframe} ({start_date.date()} 到 {end_date.date()})")
        
        all_klines = []
        current_date = start_date
        
        while current_date < end_date:
            try:
                # 獲取該時間點的K線
                since = int(current_date.timestamp() * 1000)
                
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        klines = exch.fetch_ohlcv(actual_symbol, timeframe, since=since, limit=1000)
                        
                        if not klines:
                            break
                        
                        all_klines.extend(klines)
                        
                        # 移到下一個時間點
                        last_timestamp = klines[-1][0]
                        current_date = datetime.fromtimestamp(last_timestamp / 1000, tz=timezone.utc)
                        
                        # 速率限制
                        time.sleep(0.1)
                        break
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = 2 ** retry_count
                            logger.warning(f"重試 {retry_count}/{max_retries}，等待 {wait_time}秒: {e}")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"下載失敗: {e}")
                            raise
                
                if not klines:
                    break
                    
            except Exception as e:
                logger.error(f"下載 {exchange} {symbol} 失敗: {e}")
                # 返回已獲取的數據
                if all_klines:
                    break
                return None
        
        if all_klines:
            logger.info(f"✓ 成功下載 {len(all_klines)} 根K線")
            
            # 保存到快取
            if use_cache:
                self._save_to_cache(exchange, symbol, timeframe, all_klines)
            
            return all_klines
        
        return None
    
    def download_multiple_symbols(
        self,
        exchange: str,
        symbols: List[str],
        timeframe: str = '1h',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        use_cache: bool = True
    ) -> Dict[str, Optional[List]]:
        """
        下載多個交易對的K線數據
        
        Args:
            exchange: 交易所
            symbols: 交易對列表
            timeframe: 時間框架
            start_date: 開始日期
            end_date: 結束日期
            use_cache: 是否使用快取
        
        Returns:
            {symbol: klines} 字典
        """
        
        results = {}
        
        for symbol in symbols:
            logger.info(f"\n下載 {symbol}...")
            klines = self.download_klines(
                exchange=exchange,
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                use_cache=use_cache
            )
            results[symbol] = klines
            
            # 交易所限流
            time.sleep(1)
        
        return results
    
    def get_supported_pairs(self, exchange: str) -> List[str]:
        """獲取交易所支持的交易對"""
        if exchange in self.symbol_mapping:
            return list(self.symbol_mapping[exchange].keys())
        return []


def download_backtest_data(
    exchange: str = 'binance',
    symbols: Optional[List[str]] = None,
    timeframe: str = '1h',
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, List]:
    """
    便利函數：下載回測所需的數據
    
    Args:
        exchange: 交易所 (binance/kraken/coinbase)
        symbols: 交易對列表，默認為 ['BTC/USD', 'ETH/USD', 'BNB/USD']
        timeframe: 時間框架
        start_date: 開始日期，默認去年
        end_date: 結束日期，默認今天
    
    Returns:
        {symbol: klines} 字典
    """
    
    if symbols is None:
        symbols = ['BTC/USD', 'ETH/USD', 'BNB/USD']
    
    if end_date is None:
        end_date = datetime.now(timezone.utc)
    
    if start_date is None:
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    
    logger.info("="*80)
    logger.info(f"開始下載實時K線數據")
    logger.info(f"交易所: {exchange}")
    logger.info(f"交易對: {', '.join(symbols)}")
    logger.info(f"時間框架: {timeframe}")
    logger.info(f"日期範圍: {start_date.date()} 到 {end_date.date()}")
    logger.info("="*80)
    
    downloader = RealMarketDataDownloader()
    
    results = downloader.download_multiple_symbols(
        exchange=exchange,
        symbols=symbols,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    
    return results


if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 下載數據
    data = download_backtest_data(
        exchange='binance',
        symbols=['BTC/USD', 'ETH/USD', 'BNB/USD'],
        timeframe='1h',
        start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
    )
    
    # 打印統計
    print("\n" + "="*80)
    print("下載統計")
    print("="*80)
    for symbol, klines in data.items():
        if klines:
            print(f"✓ {symbol}: {len(klines)} 根K線")
        else:
            print(f"✗ {symbol}: 下載失敗")
