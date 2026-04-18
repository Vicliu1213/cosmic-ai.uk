# enhanced_classic

這是 `src/algorithms/` 下的增強型經典算法索引套件。

目標：
- 從現有 `module_catalog.json` 讀取模組
- 依能源 / 壓縮 / 精度 / 計算四層做自動映射
- 提供更好的推薦、查詢與索引輸出

使用：
```python
from src.algorithms.enhanced_classic import build_default_registry

registry = build_default_registry()
print(registry.recommend())
```
