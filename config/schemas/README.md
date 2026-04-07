# 配置 Schema 定义

所有配置的 JSON Schema 验证规则。

## Schema 文件

- `engine/engine_schema.json` - 引擎配置规则
- `system/system_schema.json` - 系统配置规则
- `api/api_schema.json` - API 配置规则
- `trading/trading_schema.json` - 交易配置规则

## 使用方式

```python
import jsonschema
import json

# 加载 schema 和配置
with open('schemas/engine/engine_schema.json') as f:
    schema = json.load(f)

with open('config.json') as f:
    config = json.load(f)

# 验证配置
try:
    jsonschema.validate(config, schema)
    print("配置有效")
except jsonschema.ValidationError as e:
    print(f"配置错误: {e}")
```

最后更新: 2026-04-05
