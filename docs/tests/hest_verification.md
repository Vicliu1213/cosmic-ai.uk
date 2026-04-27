# Hest 驗證系統

這是一套即時系統驗證層，會在執行時檢查：
- `src/layers/`
- `src/algorithms/enhanced_classic/`
- `hermes/dashboard/module_catalog.json`
- Dashboard UI
- Sharpe growth trend (risk-adjusted uplift)
- Growth stack state (nonlinear stacking)
- Strategy win rate vs backtest quality

## 核心能力
- 即時驗證
- 多檢查點健康報告
- 支援 watch 模式
- 可接入自定義狀態來源

## 使用
```python
from src.tests.hest import build_default_hest_verifier
verifier = build_default_hest_verifier()
report = verifier.verify()
print(report.as_dict())
```

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
