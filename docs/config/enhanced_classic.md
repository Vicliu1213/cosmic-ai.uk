# enhanced_classic 配置說明

檔案：`config/enhanced_classic.yaml`

## 欄位
- `system.name`：系統名稱
- `system.version`：版本
- `system.mode`：推薦模式
- `system.catalog_path`：模組目錄來源
- `layers.*.enabled`：是否啟用該層
- `layers.*.keywords`：映射關鍵字
- `layers.*.top_k`：推薦數量
- `ui.title`：UI 標題
- `ui.default_page`：預設頁
- `ui.theme`：主題

## 用法
```python
from src.algorithms.enhanced_classic import build_default_registry
registry = build_default_registry()
print(registry.recommend())
```

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
