@dataclass
class PulseEvent:
    """單一脈衝事件 — 來自某幣種的真突破"""
    symbol: str              # BTCUSDT
    sector: str              # "L1" | "L2" | "DeFi" | "LST" | "Meme" | "Other"
    timestamp: float         # Unix 時間戳
    direction: str           # "LONG" | "SHORT"
    confidence: float        # 0~1
    breakout_level: float    # 突破價位


@dataclass
class PulseCluster:
    """多重脈衝的時空耦合群集"""
    events: List[PulseEvent]                        # 時間窗內的事件列表
    time_window_seconds: float = 180.0              # 時間窗口 (3 分鐘)
    sector_diversity: int = 0                       # 跨賽道數量
    total_confidence: float = 0.0                   # 平均信心
    density_score: float = 0.0                      # 耦合密度 (0~1)
    phase: str = "SCATTERED"                        # "SCATTERED" | "COALESCING" | "RESONATING"
    directional_coherence: float = 0.0              # 方向一致性 (0.5~1.0)
    dominant_direction: str = ""                    # 主方向
    sector_breakdown: Dict[str, List[str]] = field(default_factory=dict)  # 賽道分佈