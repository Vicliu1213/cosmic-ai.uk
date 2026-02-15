# 跨平臺 Skill 轉換指南

## 概述

本文檔詳細說明如何使用 `SkillConverter` 工具在 OpenCode、Claude、Cursor 和 CodeLaw 之間轉換 Skill 配置。

## 目錄

1. [快速開始](#快速開始)
2. [轉換工具](#轉換工具)
3. [平臺對比](#平臺對比)
4. [轉換示例](#轉換示例)
5. [最佳實踐](#最佳實踐)
6. [常見問題](#常見問題)

---

## 快速開始

### 安裝依賴

```bash
pip install pyyaml
```

### 基本用法

```python
from src.utils.skill_converter import UnifiedSkill, SkillConverter

# 1. 定義統一的 Skill
skill = UnifiedSkill(
    id="my-skill",
    name="My Skill",
    description="A useful skill for development",
    categories=["development"],
    capabilities=["Feature 1", "Feature 2"]
)

# 2. 創建轉換器
converter = SkillConverter(skill)

# 3. 生成各平臺格式
opencode_md = converter.to_opencode_skill()
claude_tool = converter.to_claude_tool()
cursor_rules = converter.to_cursor_rules()
codelaw_rules = converter.to_codelaw_rules()

# 4. 保存所有格式
converter.save_all(Path("./output"))
```

---

## 轉換工具

### SkillConverter 類

#### 初始化

```python
converter = SkillConverter(unified_skill: UnifiedSkill)
```

#### 方法

| 方法 | 返回值 | 說明 |
|------|--------|------|
| `to_opencode_skill()` | `str` | 生成 OpenCode SKILL.md 內容 |
| `to_claude_tool()` | `Dict` | 生成 Claude Tool 定義 |
| `to_cursor_rules()` | `Dict` | 生成 Cursor 配置規則 |
| `to_codelaw_rules()` | `List[Dict]` | 生成 CodeLaw 規則 |
| `to_unified_yaml()` | `str` | 生成統一 YAML 格式 |
| `save_all(output_dir)` | `None` | 保存所有格式到目錄 |

### UnifiedSkill 類

統一的 Skill 定義格式：

```python
@dataclass
class UnifiedSkill:
    id: str                          # 必需：技能 ID (kebab-case)
    name: str                        # 必需：技能名稱
    description: str                 # 必需：技能描述 (1-1024 字符)
    version: str = "1.0.0"           # 版本號
    license: str = "MIT"             # 許可證
    categories: List[str] = None     # 分類標籤
    capabilities: List[str] = None   # 能力列表
    metadata: Dict[str, Any] = None  # 額外元數據
```

---

## 平臺對比

### 配置位置

| 平臺 | 項目級 | 全局級 |
|------|--------|--------|
| **OpenCode** | `.opencode/skills/<id>/SKILL.md` | `~/.config/opencode/skills/<id>/SKILL.md` |
| **Claude** | 代碼內嵌 | `~/.claude/tools/<id>.py` |
| **Cursor** | `.cursorrules` | `~/.config/cursor/rules.json` |
| **CodeLaw** | `.codelaw/rules.yaml` | `~/.codelaw/rules.yaml` |

### 格式對比

| 特性 | OpenCode | Claude | Cursor | CodeLaw |
|------|----------|--------|--------|---------|
| 格式 | Markdown + YAML | Python | JSON/Text | YAML |
| 權限管理 | ✓ | ✗ | ✗ | ✓ |
| 自動發現 | ✓ | ✗ | ✗ | ✓ |
| 層級配置 | ✓ | ✗ | ✓ | ✓ |
| 可復用性 | 高 | 中 | 低 | 中 |

---

## 轉換示例

### 示例 1: 簡單 Skill 轉換

```python
from src.utils.skill_converter import UnifiedSkill, SkillConverter

skill = UnifiedSkill(
    id="git-release",
    name="Git Release",
    description="Create consistent releases and changelogs",
    categories=["devops", "github"],
    capabilities=[
        "Draft release notes",
        "Version bump proposal",
        "Generate gh commands"
    ]
)

converter = SkillConverter(skill)

# 保存到文件
from pathlib import Path
converter.save_all(Path("./skills_output"))
```

**輸出結構**:
```
skills_output/
├── git-release-unified.yaml
├── opencode/
│   └── git-release/
│       └── SKILL.md
├── claude/
│   └── git-release.json
├── cursor/
│   └── git-release.json
└── codelaw/
    └── git-release.yaml
```

### 示例 2: 批量轉換

```python
from pathlib import Path
from src.utils.skill_converter import UnifiedSkill, SkillConverter

skills_config = [
    {
        "id": "code-review",
        "name": "Code Review",
        "description": "Automated code review",
        "categories": ["quality"],
    },
    {
        "id": "docs-gen",
        "name": "Docs Generator",
        "description": "Auto API documentation",
        "categories": ["documentation"],
    }
]

for config in skills_config:
    skill = UnifiedSkill(**config)
    converter = SkillConverter(skill)
    converter.save_all(Path(f"./output/{config['id']}"))
```

### 示例 3: 解析現有 Skill

```python
from src.utils.skill_converter import parse_opencode_skill, SkillConverter

# 解析現有 SKILL.md
skill = parse_opencode_skill(".opencode/skills/my-skill/SKILL.md")

# 轉換到其他格式
converter = SkillConverter(skill)
claude_tool = converter.to_claude_tool()
cursor_config = converter.to_cursor_rules()
```

---

## 最佳實踐

### 1. 命名規範

**Skill ID 規則** (必須遵守):
- 小寫字母、數字、單個連字號
- 1-64 字符
- 正則: `^[a-z0-9]+(-[a-z0-9]+)*$`

**示例**:
- ✓ `code-review` 
- ✓ `api-testing-v2`
- ✗ `CodeReview` (大寫不允許)
- ✗ `code--review` (連續連字號不允許)

### 2. 描述編寫

**要求**:
- 1-1024 字符
- 清晰、簡潔的英文
- 易於被 LLM 理解

**範例**:
```
好: "Validate and execute database schema migrations with rollback support"
差: "database tool"
```

### 3. 分類標籤

**推薦標籤**:
- 功能: `testing`, `documentation`, `security`, `devops`
- 技術: `database`, `api`, `frontend`, `backend`
- 流程: `ci-cd`, `deployment`, `monitoring`

**用法**:
```python
categories=["devops", "database"]  # 最多 5 個標籤
```

### 4. 能力描述

**明確列出 Skill 提供的功能**:

```python
capabilities=[
    "Generate comprehensive test suites",
    "Validate API schemas",
    "Performance profiling",
    "Error handling verification"
]
```

每個能力會轉換為 CodeLaw 規則。

### 5. 版本管理

**使用語義化版本**:
```
MAJOR.MINOR.PATCH
例: 1.2.3
```

### 6. 文件組織

**建議的項目結構**:
```
project/
├── .opencode/
│   ├── skills/
│   │   ├── skill-1/
│   │   │   └── SKILL.md
│   │   └── skill-2/
│   │       └── SKILL.md
│   └── opencode.json
├── src/
│   └── utils/
│       └── skill_converter.py
└── examples/
    └── skill_converter_examples.py
```

---

## 常見問題

### Q1: 如何更新現有 Skill？

```python
# 1. 解析現有 Skill
skill = parse_opencode_skill("path/to/SKILL.md")

# 2. 修改屬性
skill.description = "Updated description"
skill.version = "1.1.0"

# 3. 重新轉換
converter = SkillConverter(skill)
converter.save_all(Path("./output"))
```

### Q2: Cursor 中如何使用轉換後的配置？

```json
// .vscode/settings.json 或 settings.json
{
  "cursor.commands": [
    {
      "id": "opencode.mySkill",
      "title": "My Skill",
      "category": "General",
      "description": "..."
    }
  ]
}
```

### Q3: 能否只轉換某個平臺的格式？

```python
converter = SkillConverter(skill)

# 只轉換 Claude 工具
claude_tool = converter.to_claude_tool()

# 只生成 OpenCode SKILL.md
opencode_content = converter.to_opencode_skill()
```

### Q4: 如何驗證 Skill 配置？

```python
try:
    skill = UnifiedSkill(id="invalid-ID", ...)
    converter = SkillConverter(skill)
except ValueError as e:
    print(f"驗證錯誤: {e}")
```

### Q5: 如何在 OpenCode 中註冊自定義 Skill？

1. 創建 SKILL.md 文件
2. 放在 `.opencode/skills/<id>/` 目錄
3. 運行 `opencode` 時自動發現
4. 通過 `skill` 工具加載

### Q6: CodeLaw 規則何時執行？

CodeLaw 規則在以下情況執行:
- 代碼提交前 (pre-commit hook)
- CI/CD 管道中
- IDE 實時檢查
- 代碼審查流程

---

## 高級使用

### 自定義轉換邏輯

```python
class CustomSkillConverter(SkillConverter):
    def to_my_platform(self) -> Dict:
        """自定義平臺轉換"""
        return {
            "custom_field": f"skill-{self.skill.id}",
            "description": self.skill.description
        }
```

### 批量驗證

```python
def validate_skills(skills_dir: Path) -> List[str]:
    """驗證目錄中的所有 Skills"""
    errors = []
    for skill_dir in skills_dir.glob("*/"):
        try:
            skill_md = skill_dir / "SKILL.md"
            parse_opencode_skill(str(skill_md))
        except Exception as e:
            errors.append(f"{skill_dir.name}: {e}")
    return errors
```

---

## 工具鏈集成

### Git Hook 集成

```bash
#!/bin/bash
# .git/hooks/pre-commit

python -c "
from src.utils.skill_converter import parse_opencode_skill
from pathlib import Path

for skill_md in Path('.opencode/skills').glob('*/SKILL.md'):
    parse_opencode_skill(str(skill_md))
" || exit 1
```

### CI/CD 集成

```yaml
# .github/workflows/validate-skills.yml
name: Validate Skills
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Skills
        run: |
          pip install pyyaml
          python scripts/validate_skills.py
```

---

## 參考資源

- [OpenCode Skills 文檔](https://opencode.ai/docs/skills/)
- [Claude Tools 文檔](https://docs.anthropic.com/claude/docs/tool-use)
- [Cursor 配置](https://cursor.sh/docs)
- [本分析文檔](./SKILL_CONFIGURATION_ANALYSIS.md)

---

## 貢獻

如有改進建議或問題，請提交 Issue 或 PR。

## 許可證

MIT License - 詳見 LICENSE 文件
