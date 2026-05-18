@dataclass
class AssetCandidate:
    """篩選後的單一幣種完整快照"""
    symbol: str                           # BTCUSDT
    price: float                          # 67250.0
    volume_24h: float                     # 24h 成交量 (USD)
    open_interest: float                  # 未平倉合約 (USD)
    atr_15m: float                        # 15 分鐘 ATR (百分比)
    funding_rate: float                   # 資金費率 (-0.001 ~ 0.001)
    orderbook_imbalance: float            # 訂單簿失衡比 (>1 買壓, <1 賣壓)
    spot_premium: float                   # 永續溢價 (%)
    liq_walls: Dict[str, float]           # {"short_liq": 67480, "long_liq": 66900}
    score: float = 0.0                    # 綜合評分 (0~4)
    optimal_leverage: int = 1             # 蒙地卡羅最優槓桿 (1~20)
    expected_terminal: float = 1.0        # 期望終值倍數
    prob_ruin: float = 0.0                # 爆倉機率 (0~1)
    monitored_levels: List[float] = []    # 3 個監控關鍵價位
    last_updated: float = 0.0             # 最後更新時間戳