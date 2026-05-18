@dataclass
class SynergyState:
    """超指數 Token 壓縮的演化記憶"""
    prior_latent_vector: Optional[np.ndarray] = None  # 前次輸出的隱含語義向量 (128 維)
    failure_patterns: Dict[str, List[Dict]] = field(default_factory=dict)
    # failure_patterns 結構:
    # {
    #   "market_scan": [
    #       {"hash": "abc123", "fix": "Validate OI data before scanning", "cost": 3500}
    #   ]
    # }
    cache_hit_count: int = 0               # 語義緩存命中次數
    token_saved_total: int = 0             # 節省 Token 累計
    compression_ratios: List[float] = field(default_factory=list)  # 壓縮率歷史
    model_usage: Dict[str, int] = field(default_factory=lambda: {
        "HAIKU": 0, "SONNET": 0, "OPUS": 0, "CACHE": 0
    })
    avg_complexity: float = 0.5            # 平均任務複雜度