@dataclass
class ExecutionResult:
    """一次完整執行週期的輸出載具"""
    candidates: List[AssetCandidate]           # 篩選出的候選幣種 (3~5)
    confirmed_breakouts: List[BreakoutSignal]  # 確認的真突破信號
    pulse_cluster: Optional[PulseCluster] = None  # 多重脈衝耦合結果
    synergy_state: SynergyState = field(default_factory=SynergyState)
    total_tokens_used: int = 0                 # 本次總 Token 消耗
    execution_time_ms: float = 0.0             # 執行耗時 (毫秒)
    mode_final: str = "VOID"                   # 最終模式 ("VOID" | "PREDATOR")
    actionable_count: int = 0                  # 可執行的信號數
    timestamp: float = field(default_factory=time.time)