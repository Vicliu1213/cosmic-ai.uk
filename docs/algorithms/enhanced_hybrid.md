# enhanced_hybrid

`enhanced_hybrid` 是比 `enhanced_classic` 更上層的混合推薦模組，並且與 Hest 即時驗證系統聯動。

## 功能
- 讀取 module catalog
- 以四層 rule 做混合推薦
- 輸出 manifest、recommendations
- 供 Hest 進行實時驗證

## 入口
- `src/algorithms/enhanced_hybrid/hybrid.py`
- `src/tests/enhanced_hybrid/verifier.py`

## 驗證
- Hest 必須通過
- hybrid manifest 必須存在
- dashboard 頁面必須可見

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
