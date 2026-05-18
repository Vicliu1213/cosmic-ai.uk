@dataclass
class BreakoutSignal:
    """真突破驗證的完整結果"""
    symbol: str                            # BTCUSDT
    direction: str                         # "LONG" | "SHORT"
    breakout_level: float                  # 突破的關鍵價位
    current_price: float                   # 當前價格
    confidence: float                      # 信心分數 (0~1)
    confirmations: Dict[str, bool] = field(default_factory=lambda: {
        "volume_surge": False,             # 量能擴張 ≥1.5x
        "oi_expansion": False,             # OI 擴張 ≥2%
        "funding_healthy": False,          # 費率未極端 (<0.15%)
        "book_aligned": False,             # 訂單簿壓力同向
        "liq_stacked": False,              # 清算堆疊支持
    })
    entry_zone: Tuple[float, float] = (0, 0)  # 進場價格區間
    stop_loss: float = 0.0                    # 止損價
    valid: bool = False                       # 最終有效性
    timestamp: float = 0.0                    # 觸發時間