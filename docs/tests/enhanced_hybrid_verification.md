# Enhanced Hybrid 驗證系統

驗證項目：
- Hest 驗證結果
- enhanced_hybrid manifest
- dashboard 入口
- module catalog 交叉推薦

## 執行
```python
from src.tests.enhanced_hybrid import build_default_enhanced_hybrid_verifier
verifier = build_default_enhanced_hybrid_verifier()
print(verifier.verify().as_dict())
```

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
