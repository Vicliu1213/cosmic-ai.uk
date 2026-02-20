# Skill 配置分析 - 執行摘要

## 研究成果總結

本研究對比分析了四個主要 AI 編程代理系統的 Skill/Tool/Rule 配置格式，並創建了統一轉換工具。

### 主要文檔

| 文檔 | 說明 | 位置 |
|------|------|------|
| **SKILL_CONFIGURATION_ANALYSIS.md** | 詳細對比分析 | 本目錄 |
| **SKILL_CONVERTER_USAGE_GUIDE.md** | 使用指南和最佳實踐 | 本目錄 |
| **skill_converter.py** | 自動轉換工具代碼 | `src/utils/` |
| **skill_converter_examples.py** | 使用示例 | `examples/` |

---

## 四大平臺對比

### 1. OpenCode
- **特點**: 完整框架，多層級配置
- **格式**: Markdown + YAML Frontmatter
- **位置**: `.opencode/skills/<id>/SKILL.md`
- **權限**: 支持 (allow/deny/ask)
- **優勢**: 自動發現，可復用性高，權限控制靈活

### 2. Claude/Anthropic
- **特點**: 基礎工具系統，代碼驅動
- **格式**: Python Decorator + JSON Schema
- **位置**: 代碼內嵌或配置文件
- **權限**: 無正式權限系統
- **優勢**: 靈活性高，與 API 深度集成

### 3. Cursor IDE
- **特點**: IDE 集成，VSCode 兼容
- **格式**: JSON/YAML 配置或 .cursorrules
- **位置**: 項目或全局配置
- **權限**: VSCode 權限系統
- **優勢**: IDE 原生支持，開箱即用

### 4. CodeLaw
- **特點**: 代碼分析規則引擎
- **格式**: YAML/JSON 規則定義
- **位置**: 配置文件或代碼注釋
- **權限**: 規則級別 (error/warning/info)
- **優勢**: 代碼質量檢查，自動化分析

---

## 統一轉換框架

### 架構

```
UnifiedSkill (中間格式)
    ↓
SkillConverter
    ├─→ OpenCode SKILL.md
    ├─→ Claude Tool Definition
    ├─→ Cursor Configuration
    ├─→ CodeLaw Rules
    └─→ Unified YAML (共享格式)
```

### 支持的轉換

| 源平臺 | 目標平臺 | 難度 | 映射清晰度 |
|--------|---------|------|----------|
| OpenCode | Claude | 易 | 清晰 |
| OpenCode | Cursor | 中 | 中等 |
| OpenCode | CodeLaw | 易 | 清晰 |
| Claude | OpenCode | 難 | 不清晰 |
| Any | Unified YAML | 易 | 標準化 |

---

## 關鍵可轉換字段

### Skill 元數據映射

```
OpenCode Frontmatter
├─ name → Claude tool_name (snake_case)
├─ description → 所有平臺共享
├─ metadata.categories → Tags/Categories
├─ metadata.audience → Cursor category
├─ metadata.workflow → CodeLaw tags
└─ capabilities → CodeLaw rules

Claude Tool
├─ name → OpenCode id (kebab-case)
├─ description → 所有平臺共享
├─ input_schema → Platform-specific
└─ tags → Categories

Cursor Commands
├─ id → 自動從 OpenCode id 生成
├─ title → 來自 name 或 description
├─ category → 來自 metadata.audience
└─ keybinding → 可定制

CodeLaw Rules
├─ id → 來自 OpenCode id
├─ name → 來自 capabilities
├─ severity → 根據 categories 推斷
└─ tags → 來自 categories
```

---

## 轉換流程

### 推薦步驟

1. **定義統一 Skill**
   ```python
   skill = UnifiedSkill(
       id="my-skill",
       name="My Skill",
       description="...",
       categories=[...],
       capabilities=[...]
   )
   ```

2. **創建轉換器**
   ```python
   converter = SkillConverter(skill)
   ```

3. **生成各平臺格式**
   ```python
   converter.save_all(Path("./output"))
   ```

4. **驗證輸出**
   - 檢查每個平臺的配置文件
   - 測試權限和訪問控制
   - 驗證規則和能力映射

5. **部署和整合**
   - 複製文件到適當位置
   - 更新配置和權限
   - 運行測試和驗證

---

## 實現指南

### 基本使用

```python
from src.utils.skill_converter import UnifiedSkill, SkillConverter

# 1. 創建 Skill
skill = UnifiedSkill(
    id="database-migration",
    name="Database Migration Helper",
    description="Assist with database schema migrations",
    version="1.2.0",
    categories=["database", "devops"],
    capabilities=[
        "Generate migration scripts",
        "Validate schema changes",
        "Rollback support"
    ]
)

# 2. 轉換
converter = SkillConverter(skill)

# 3. 使用
print(converter.to_opencode_skill())  # OpenCode SKILL.md
print(converter.to_claude_tool())     # Claude tool
print(converter.to_cursor_rules())    # Cursor config
print(converter.to_codelaw_rules())   # CodeLaw rules

# 4. 保存
converter.save_all(Path("./skills_output"))
```

### 解析現有 Skill

```python
from src.utils.skill_converter import parse_opencode_skill

skill = parse_opencode_skill(".opencode/skills/my-skill/SKILL.md")
converter = SkillConverter(skill)
# 現在可以轉換到其他格式
```

### 批量轉換

```python
from pathlib import Path

for skill_dir in Path(".opencode/skills").glob("*/"):
    skill_md = skill_dir / "SKILL.md"
    try:
        skill = parse_opencode_skill(str(skill_md))
        converter = SkillConverter(skill)
        converter.save_all(Path(f"./converted/{skill_dir.name}"))
    except Exception as e:
        print(f"Error converting {skill_dir.name}: {e}")
```

---

## 最佳實踐

### 1. 命名規範

- **ID**: 小寫、連字號、1-64 字符 (必須)
- **描述**: 1-1024 字符、清晰明確
- **版本**: 使用語義化版本 (MAJOR.MINOR.PATCH)

### 2. 組織結構

```
project/
├── .opencode/
│   └── skills/
│       ├── skill-1/
│       │   └── SKILL.md
│       └── skill-2/
│           └── SKILL.md
├── src/utils/
│   └── skill_converter.py
└── docs/
    ├── SKILL_CONFIGURATION_ANALYSIS.md
    ├── SKILL_CONVERTER_USAGE_GUIDE.md
    └── SKILL_ANALYSIS_SUMMARY.md (本文件)
```

### 3. 分類標籤

推薦標籤:
- **功能**: testing, documentation, security, devops
- **技術**: database, api, frontend, backend
- **流程**: ci-cd, deployment, monitoring

### 4. 能力描述

- 明確列出功能
- 每個能力一行
- 每個能力轉換為一條 CodeLaw 規則

### 5. 文檔維護

- 保留版本歷史
- 在 SKILL.md 中記錄更改
- 使用 Git tags 標記版本

---

## 工程化考慮

### 版本控制

```yaml
# unified-skill.yaml
metadata:
  version: 1.2.0
  last_updated: 2026-02-15
  changelog:
    - version: 1.2.0
      date: 2026-02-15
      changes:
        - Added performance profiling capability
    - version: 1.1.0
      date: 2026-02-10
      changes:
        - Initial release
```

### CI/CD 集成

```yaml
# .github/workflows/validate-skills.yml
- name: Validate Skills
  run: |
    pip install pyyaml
    python scripts/validate_skills.py

- name: Generate Skill Artifacts
  run: |
    python scripts/generate_skill_artifacts.py
```

### 權限管理

```json
// opencode.json
{
  "permission": {
    "skill": {
      "*": "allow",
      "internal-*": "deny",
      "experimental-*": "ask"
    }
  }
}
```

---

## 轉換工具特性

### SkillConverter 類

**主要方法**:
- `to_opencode_skill()` → OpenCode SKILL.md
- `to_claude_tool()` → Claude Tool JSON
- `to_cursor_rules()` → Cursor Configuration
- `to_codelaw_rules()` → CodeLaw YAML Rules
- `to_unified_yaml()` → 統一 YAML 格式
- `save_all(output_dir)` → 保存所有格式

**驗證**:
- 名稱驗證 (正則表達式)
- 描述長度檢查
- 元數據一致性檢查

---

## 使用場景

### 場景 1: 新 Skill 開發

1. 在 UnifiedSkill 中定義 Skill
2. 使用 SkillConverter 生成所有格式
3. 複製到各平臺配置目錄
4. 提交到版本控制

### 場景 2: Skill 遷移

1. 從現有平臺解析 Skill
2. 轉換為 UnifiedSkill 格式
3. 轉換到目標平臺格式
4. 驗證和測試

### 場景 3: Skill 同步

1. 定期解析所有 Skills
2. 更新統一 YAML 格式
3. 檢測不一致和衝突
4. 自動同步和修復

---

## 後續工作建議

### 短期 (1-2 周)

- [ ] 完成轉換工具測試
- [ ] 文檔審查和改進
- [ ] 集成到 CI/CD 流程
- [ ] 創建遷移指南

### 中期 (1-3 個月)

- [ ] 建立 Skill 倉庫
- [ ] 開發 Web UI 管理工具
- [ ] 創建最佳實踐模板
- [ ] 社區反饋和改進

### 長期 (3-6 個月)

- [ ] 標準化 Skill 格式
- [ ] 跨組織 Skill 共享
- [ ] 自動化工具鏈完善
- [ ] 生態系統建設

---

## 文件清單

生成的文件和代碼:

1. **SKILL_CONFIGURATION_ANALYSIS.md** (本目錄)
   - 詳細的技術分析和對比
   - 配置格式說明
   - 轉換策略

2. **SKILL_CONVERTER_USAGE_GUIDE.md** (本目錄)
   - 工具使用指南
   - 最佳實踐
   - FAQ 和常見問題

3. **src/utils/skill_converter.py**
   - SkillConverter 類實現
   - UnifiedSkill 數據類
   - 轉換邏輯和驗證

4. **examples/skill_converter_examples.py**
   - 5 個完整使用示例
   - 批量轉換演示
   - 映射參考

5. **SKILL_ANALYSIS_SUMMARY.md** (本文件)
   - 執行摘要
   - 快速參考
   - 後續工作建議

---

## 相關資源

- [OpenCode 官方文檔](https://opencode.ai/docs/skills/)
- [Claude API 文檔](https://docs.anthropic.com/claude/docs/tool-use)
- [Cursor 文檔](https://cursor.com/docs)
- [本地分析文檔](./SKILL_CONFIGURATION_ANALYSIS.md)

---

## 許可證

MIT License

---

**最後更新**: 2026-02-15
**版本**: 1.0.0
**作者**: OpenCode 分析團隊
