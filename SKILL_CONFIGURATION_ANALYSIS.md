# AI Coding Agent Skill Configuration 對比分析

## 1. OpenCode Skill 配置格式

### 1.1 SKILL.md 文件結構

**位置**:
- 項目級: `.opencode/skills/<name>/SKILL.md`
- 全局級: `~/.config/opencode/skills/<name>/SKILL.md`
- Claude 兼容: `.claude/skills/<name>/SKILL.md`
- Agent 兼容: `.agents/skills/<name>/SKILL.md`

**文件格式** (Markdown + YAML Frontmatter):

```markdown
---
name: git-release
description: Create consistent releases and changelogs
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
  workflow: github
---

## What I do
- Draft release notes from merged PRs
- Propose a version bump
- Provide a copy-pasteable `gh release create` command

## When to use me
Use this when you are preparing a tagged release.
Ask clarifying questions if the target versioning scheme is unclear.
```

**Frontmatter 字段規則**:
- `name` (必需): 1-64 字符, 小寫字母數字和單個連字號分隔
  - 正則: `^[a-z0-9]+(-[a-z0-9]+)*$`
  - 必須與包含目錄名稱匹配
- `description` (必需): 1-1024 字符
- `license` (可選): MIT, Apache 2.0 等
- `compatibility` (可選): opencode, claude 等
- `metadata` (可選): 字符串對字典

### 1.2 OpenCode 配置 (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "description": "Build agent with all tools enabled",
      "prompt": "{file:./prompts/build.txt}",
      "temperature": 0.3,
      "steps": 10,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true,
        "skill": true
      },
      "permission": {
        "edit": "allow",
        "bash": {
          "*": "ask",
          "git status *": "allow"
        },
        "skill": {
          "*": "allow",
          "pr-review": "allow",
          "internal-*": "deny",
          "experimental-*": "ask"
        }
      }
    }
  },
  "permission": {
    "skill": {
      "*": "allow",
      "pr-review": "allow",
      "internal-*": "deny"
    }
  }
}
```

### 1.3 OpenCode Tools

內建工具清單:
- `bash`: 執行 shell 命令
- `edit`: 修改現有文件
- `write`: 創建/覆寫文件
- `read`: 讀取文件內容
- `grep`: 正則搜索
- `glob`: 文件模式匹配
- `skill`: 加載 SKILL.md 文件
- `todowrite/todoread`: 任務列表管理
- `webfetch/websearch`: 網絡訪問
- `question`: 詢問用戶

---

## 2. Claude / Anthropic Skill 配置格式

### 2.1 Claude Tools (Tool Use)

```python
@beta_tool
def get_weather(location: str) -> str:
    """Lookup the weather for a given city
    Args:
        location: The city and state, e.g. San Francisco, CA
    Returns:
        A dictionary containing the location, temperature, and weather condition.
    """
    return json.dumps({
        "location": location,
        "temperature": "68°F",
        "condition": "Sunny",
    })

# 使用 tool runner
runner = client.beta.messages.tool_runner(
    max_tokens=1024,
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
    messages=[
        {"role": "user", "content": "What is the weather in SF?"},
    ],
)
```

### 2.2 Claude Skills (API 層次)

Claude 沒有正式的 "SKILL" 框架，但使用 **Tool Use** 機制:

```json
{
  "tools": [
    {
      "name": "weather_lookup",
      "description": "Get weather information for a location",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City and state"
          }
        },
        "required": ["location"]
      }
    }
  ]
}
```

### 2.3 Claude Messages Tool Use

```json
{
  "type": "tool_use",
  "id": "toolu_1234567890",
  "name": "weather_lookup",
  "input": {
    "location": "San Francisco, CA"
  }
}
```

---

## 3. Cursor IDE Skill/Plugin 配置

### 3.1 Cursor 配置結構

Cursor 主要使用 VSCode 兼容的配置:

```json
{
  "cursor.commands": [
    {
      "id": "extension.myCommand",
      "title": "My Custom Command",
      "category": "My Extension"
    }
  ],
  "cursor.keybindings": [
    {
      "key": "ctrl+shift+p",
      "command": "extension.myCommand",
      "when": "editorTextFocus"
    }
  ]
}
```

### 3.2 Cursor AI Features (無正式 Skill 框架)

Cursor 整合 Claude 作為後端，但沒有自定義 Skill 機制。
支援通過:
- `.cursorrules` 文件: 自定義行為
- System prompts: 自定義指令
- Custom commands: 自定義命令

**.cursorrules 範例**:
```
You are an expert Python developer.
When writing code:
- Use type hints
- Follow PEP 8
- Add docstrings
- Use descriptive variable names
```

---

## 4. CodeLaw Skill 配置

### 4.1 CodeLaw 架構 (推斷自 GitHub 倉庫)

CodeLaw (anilyaris/codelaw) 作為代碼分析工具，使用配置結構:

```json
{
  "rules": [
    {
      "name": "naming-convention",
      "level": "error",
      "pattern": "^[a-z_][a-z0-9_]*$",
      "applies_to": ["functions", "variables"]
    },
    {
      "name": "max-line-length",
      "level": "warning",
      "value": 127,
      "applies_to": ["code"]
    }
  ],
  "exclusions": ["node_modules", "dist", "build"]
}
```

### 4.2 CodeLaw 規則格式

```yaml
rules:
  - id: rule-001
    name: "Type Safety"
    description: "Enforce type annotations"
    pattern: "def\\s+\\w+\\([^)]*\\)\\s*:"
    severity: "warning"
    fixer: "auto"
    
  - id: rule-002
    name: "Documentation"
    description: "Require docstrings"
    pattern: "^def\\s+\\w+.*:$"
    severity: "error"
    requires: "docstring"
```

---

## 5. 配置結構對比表

| 特徵 | OpenCode | Claude/Anthropic | Cursor | CodeLaw |
|------|----------|------------------|--------|---------|
| **框架類型** | SKILL.md + JSON | Python Decorator + JSON | .cursorrules | YAML/JSON Rules |
| **定義方式** | Markdown Frontmatter | Python 函數 + Schema | 文本格式 | YAML 規則定義 |
| **權限管理** | 支持 (allow/deny/ask) | 無權限系統 | VSCode 集成 | 規則級別 |
| **模式匹配** | 文件名驗證 | 不適用 | 不適用 | 正則模式 |
| **工具發現** | 自動發現 | 手動配置 | 無 | 規則掃描 |
| **可復用性** | 高 (全局/項目) | 中等 | 低 | 中等 |
| **配置位置** | 多層級 | 代碼內嵌 | 文件或設置 | 配置文件 |
| **文檔格式** | Markdown | Docstring | 純文本 | YAML/JSON |

---

## 6. 關鍵可轉換字段

### 6.1 OpenCode → Claude Tool Use

```
SKILL.md Frontmatter → Tool Definition

name → tool.name
description → tool.description
metadata.audience → tool.category
metadata.workflow → tool.tags
```

**轉換例**:
```
OpenCode SKILL.md:
- name: git-release
- description: Create consistent releases

↓ 轉換為

Claude Tool:
{
  "name": "git_release",
  "description": "Create consistent releases and changelogs",
  "input_schema": { ... }
}
```

### 6.2 OpenCode → CodeLaw Rules

```
Skill Metadata → CodeLaw Rule

name → rule.id
description → rule.name
compatibility → rule.applies_to
```

### 6.3 OpenCode → Cursor Rules

```
Skill Content → .cursorrules

Skill body → Command documentation
metadata → Command categories
name → Command ID
```

---

## 7. 建議的轉換策略

### 7.1 OpenCode → Claude

**步驟**:
1. 解析 SKILL.md Frontmatter (YAML)
2. 從 Markdown 內容提取功能描述
3. 映射到 Claude Tool Schema
4. 創建 Python 函數包裝器

**例**:
```python
# 從 SKILL.md 轉換
skill_name = "git-release"
skill_desc = "Create consistent releases and changelogs"

# 生成 Claude Tool
@beta_tool
def git_release(version: str, branch: str = "main") -> str:
    """Create consistent releases and changelogs
    
    Args:
        version: Version number for the release
        branch: Target branch (default: main)
    """
    # 從原始 SKILL.md 提取的實現邏輯
    pass
```

### 7.2 OpenCode → CodeLaw

**步驟**:
1. 提取 Skill 的 metadata.audience (audience/workflow)
2. 轉換為 CodeLaw 規則級別 (error/warning/info)
3. 生成模式匹配規則
4. 配置排除項

**例**:
```yaml
# 從 OpenCode Skill 轉換
rules:
  - id: opencode-git-release
    name: "git-release skill"
    description: "Create consistent releases and changelogs"
    applies_to: [build]
    severity: "warning"
    tags: ["github", "release"]
```

### 7.3 OpenCode → Cursor

**步驟**:
1. 從 Skill name 生成 Command ID
2. 使用 description 作為 Command title
3. 在 .cursorrules 中定義行為
4. 映射到 VSCode 命令機制

**例**:
```json
{
  "cursor.commands": [
    {
      "id": "opencode.gitRelease",
      "title": "Create consistent releases and changelogs",
      "category": "Git"
    }
  ]
}
```

---

## 8. 實現建議

### 8.1 通用 Skill 定義格式

創建一個中間格式，支持所有系統:

```yaml
# unified-skill.yaml
schema_version: "1.0"

metadata:
  id: git-release
  name: "Git Release"
  description: "Create consistent releases and changelogs"
  version: "1.0.0"
  license: "MIT"
  categories: ["devops", "github"]
  
platforms:
  opencode:
    path: ".opencode/skills/git-release/SKILL.md"
    compatibility: "opencode"
  
  claude:
    function_name: "git_release"
    input_schema:
      version:
        type: "string"
        required: true
      branch:
        type: "string"
        default: "main"
  
  cursor:
    command_id: "opencode.gitRelease"
    keybinding: "ctrl+shift+r"
  
  codelaw:
    rule_id: "git-release-rule"
    severity: "warning"

capabilities:
  - draft_release_notes
  - propose_version_bump
  - generate_gh_commands

documentation:
  usage: |
    Use this skill when preparing a tagged release.
    Ask clarifying questions about the versioning scheme.
```

### 8.2 轉換工具流程

```
unified-skill.yaml
  ↓
Parser
  ├─→ SKILL.md Generator
  ├─→ Claude Tool Generator
  ├─→ CodeLaw Rule Generator
  └─→ Cursor Rule Generator
```

### 8.3 自動轉換代碼框架

```python
class SkillConverter:
    def __init__(self, skill_config: dict):
        self.config = skill_config
    
    def to_opencode_skill(self) -> str:
        """生成 SKILL.md"""
        pass
    
    def to_claude_tool(self) -> dict:
        """生成 Claude Tool 定義"""
        pass
    
    def to_cursor_rules(self) -> dict:
        """生成 Cursor 規則"""
        pass
    
    def to_codelaw_rules(self) -> list:
        """生成 CodeLaw 規則"""
        pass
```

---

## 9. 關鍵差異總結

| 方面 | OpenCode | Claude | Cursor | CodeLaw |
|------|----------|--------|--------|---------|
| **完整性** | 完整框架 | 基礎工具系統 | 集成 VSCode | 規則引擎 |
| **靈活性** | 中等 | 高 | 低 | 中等 |
| **學習曲線** | 中等 | 低 | 低 | 中等 |
| **可擴展性** | 高 | 高 | 低 | 中等 |
| **文檔方式** | Markdown | Python 代碼 | 配置文件 | YAML |
| **運行環境** | 獨立 CLI | API | IDE 插件 | 代碼分析工具 |

---

## 10. 實踐建議

### 10.1 推薦的轉換優先順序

1. **OpenCode → Claude**: 最容易，功能映射清晰
2. **OpenCode → CodeLaw**: 中等難度，規則轉換直接
3. **OpenCode → Cursor**: 較難，需要調整心態

### 10.2 共享 Skill 的最佳實踐

- 使用統一的中間格式 (unified-skill.yaml)
- 建立自動轉換管道
- 維護轉換映射表
- 提供版本管理機制
- 編寫跨平臺文檔

### 10.3 可復用組件結構

```
/shared/
  ├── skills/
  │   ├── unified-skill.schema.json
  │   ├── converters/
  │   │   ├── opencode.py
  │   │   ├── claude.py
  │   │   ├── cursor.py
  │   │   └── codelaw.py
  │   └── templates/
  │       ├── skill.md.template
  │       ├── tool.json.template
  │       └── rule.yaml.template
```
