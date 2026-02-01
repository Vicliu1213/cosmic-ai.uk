import ccxt
import pandas as pd
import pandas_ta as ta
import time
import requests

# ==========================================
# 1. 核心配置區 (請填入您的資訊)
# ==========================================
CONFIG = {
    'apiKey': bg_d3e17f5d767f897aef49d30d550be095',
    'secret': '8f7710e884526286425401073890ed7d143e23e139f0189b9ca10a22796fe0b5',
    'password': '1213Vicliu',
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
}

TELEGRAM_TOKEN = '您的_TG_TOKEN'
TELEGRAM_CHAT_ID = '您的_CHAT_ID'

# 交易參數
SYMBOL_COUNT = 40          # 監控成交量前 40 名
INITIAL_CASH = 50          # 每單起步 50 USDT
REINVEST_RATIO = 0.2       # 20% 利潤用於複投增長
LEVERAGE = 5               # 建議 5 倍槓桿，確保全共振容錯

# SuperATR 策略參數
SHORT_PERIOD, LONG_PERIOD, MOM_PERIOD = 3, 7, 7
TREND_THRESHOLD = 1.618

# 初始化交易所
exchange = ccxt.bitget(CONFIG)

# ==========================================
# 2. 工具函式區
# ==========================================
def send_tg_msg(msg):
    """發送 Telegram 通知"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': msg}
        requests.post(url, data=payload)
    except Exception as e:
        print(f"TG 發送失敗: {e}")

def get_top_40_symbols():
    """修正後的獲取成交量前 40 幣種函式"""
    try:
        tickers = exchange.fetch_tickers()
        # 篩選 Bitget 的 USDT 永續合約 (結尾為 USDT)
        usdt_pairs = [s for s in tickers if s.endswith('USDT')]
        # 按 24h 成交量排序
        sorted_pairs = sorted(usdt_pairs, key=lambda x: tickers[x]['quoteVolume'], reverse=True)
        return sorted_pairs[:SYMBOL_COUNT]
    except Exception as e:
        print(f"獲取幣種失敗: {e}")
        return []

def calculate_super_atr_logic(symbol):
    """SuperATR 奇點判定與 7 步參數計算"""
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])

        # 1. 計算 Adaptive ATR
        df['tr'] = ta.true_range(df['high'], df['low'], df['close'])
        df['mom'] = df['close'].diff(MOM_PERIOD)
        df['stdev'] = df['close'].rolling(MOM_PERIOD).std()
        df['mom_factor'] = (df['mom'] / df['stdev']).abs().fillna(0)

        s_atr = ta.sma(df['tr'], length=SHORT_PERIOD)
        l_atr = ta.sma(df['tr'], length=LONG_PERIOD)
        df['adaptive_atr'] = (s_atr * df['mom_factor'] + l_atr) / (1 + df['mom_factor'])

        # 2. 計算 Trend Strength
        df['trend_strength'] = ta.sma(df['mom'] / df['adaptive_atr'], length=MOM_PERIOD)
        df['sma_s'] = ta.sma(df['close'], length=SHORT_PERIOD)
        df['sma_l'] = ta.sma(df['close'], length=LONG_PERIOD)

        last = df.iloc[-1]

        # 3. 判定全共振信號 (多頭)
        is_long = (last['sma_s'] > last['sma_l']) and (last['trend_strength'] > TREND_THRESHOLD) and (last['close'] > last['sma_s'])

        return is_long, last['close'], last['adaptive_atr']
    except:
        return False, 0, 0

def get_compounding_qty(price):
    """計算複投後的開倉數量"""
    balance = exchange.fetch_balance()
    total_equity = float(balance['total']['USDT'])
    # 複投邏輯：利潤越高，每單投入越多
    trade_value = INITIAL_CASH + (max(0, total_equity - 100) * REINVEST_RATIO)
    return (trade_value / price), trade_value

# ==========================================
# 3. 執行與 7 步止盈區
# ==========================================
def execute_7_step_strategy(symbol, entry_price, atr_val, qty):
    """執行 4步 ATR + 3步 固定百分比止盈"""
    side_exit = 'sell'
    # ATR 4步止盈倍數
    atr_mults = [2.618, 5.0, 10.0, 13.82]
    # 固定 3步止盈百分比
    fixed_pcts = [0.03, 0.08, 0.17]

    step_qty = qty * 0.14 # 平分 7 份

    # 1. 設定初始止損 (2倍 ATR)
    sl_price = entry_price - (2 * atr_val)
    exchange.create_order(symbol, 'trigger', side_exit, qty, None, {'stopPrice': sl_price, 'reduceOnly': True})

    # 2. 掛出 7 步止盈單
    for m in atr_mults:
        tp_p = entry_price + (m * atr_val)
        exchange.create_order(symbol, 'limit', side_exit, step_qty, tp_p, {'reduceOnly': True})

    for p in fixed_pcts:
        tp_p = entry_price * (1 + p)
        exchange.create_order(symbol, 'limit', side_exit, step_qty, tp_p, {'reduceOnly': True})

# ==========================================
# 4. 主引擎循環
# ==========================================
def run_sentinel():
    send_tg_msg("🔥 宇宙智能體：Bitget 全共振 50U 複投系統啟動！")

    while True:
        try:
            symbols = get_top_40_symbols()
            for s in symbols:
                is_singularity, price, atr = calculate_super_atr_logic(s)

                if is_singularity:
                    # 檢查是否已有持倉，避免重複開倉
                    pos = exchange.fetch_position(s)
                    if float(pos[0]['size']) == 0:
                        qty, val = get_compounding_qty(price)
                        # 市價買入
                        exchange.create_market_buy_order(s, qty)
                        # 佈署 7 步止盈
                        noexecute_7_step_strategy(s, price, atr, qty)
                        send_tg_msg(f"✅ 奇點達成: {s}\n開倉價值: {val:.2f} USDT\n7步止盈已佈署。")

            time.sleep(120) # 每 2 分鐘掃描一次前 40 大幣種
        except Exception as e:
            print(f"運行異常: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_sentinel()
