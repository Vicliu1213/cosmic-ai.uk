# layers

`src/layers/` 目前提供四層能源精度壓縮框架：

- `config.py`：配置資料類
- `core.py`：核心資料類與預設四層模板
- `pipeline.py`：執行、收集與輸出結果

## 快速使用

```python
from src.layers import build_default_pipeline
result = build_default_pipeline().run()
print(result["final"])
```

## 相關文件

- `docs/layers/四層能源精度壓縮設計.md`

## Protected Content Rule

- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
