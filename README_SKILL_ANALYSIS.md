# AI Coding Agent Skill 配置分析 - 完整指南

## 項目概述

本項目對 GitHub 和開源社區中的主要 AI 編程代理系統的 Skill/Tool/Rule 配置格式進行了深度分析，並創建了一套完整的轉換工具和文檔。

**研究對象**:
1. **OpenCode** - 開源 AI 編程代理 (anomalyco/opencode)
2. **Claude/Anthropic** - Claude API 的 Tool Use 系統
3. **Cursor IDE** - AI 代碼編輯器
4. **CodeLaw** - 代碼分析和規則引擎

---

## 文檔導航

### 📖 主文檔

| 文檔 | 內容 | 適合人群 |
|------|------|---------|
| **[SKILL_ANALYSIS_SUMMARY.md](./SKILL_ANALYSIS_SUMMARY.md)** | 執行摘要、快速參考 | 決策者、項目經理 |
| **[SKILL_CONFIGURATION_ANALYSIS.md](./SKILL_CONFIGURATION_ANALYSIS.md)** | 詳細技術分析、對比表、轉換策略 | 技術人員、架構師 |
| **[SKILL_CONVERTER_USAGE_GUIDE.md](./SKILL_CONVERTER_USAGE_GUIDE.md)** | 工具使用指南、最佳實踐、FAQ | 開發者、使用者 |

### 🔧 代碼文件

| 文件 | 位置 | 說明 |
|------|------|------|
| **skill_converter.py** | `src/utils/` | 核心轉換工具和類 |
| **skill_converter_examples.py** | `examples/` | 5 個完整使用示例 |

---

## 快速開始

### 1. 閱讀順序

**第一次接觸**:
```
1. 本文件 (README_SKILL_ANALYSIS.md) 
   └─ 項目概述和導航
2. SKILL_ANALYSIS_SUMMARY.md 
   └─ 了解主要內容和對比
3. SKILL_CONVERTER_USAGE_GUIDE.md 
   └─ 學習如何使用工具
```

**技術深入**:
```
1. SKILL_CONFIGURATION_ANALYSIS.md
   └─ 詳細的技術分析
2. src/utils/skill_converter.py
   └─ 源碼實現
3. examples/skill_converter_examples.py
   └─ 實踐示例
```

### 2. 基本使用

```python
from src.utils.skill_converter import UnifiedSkill, SkillConverter
from pathlib import Path

# 定義一個 Skill
skill = UnifiedSkill(
    id="my-skill",
    name="My Skill",
    description="A useful skill",
    categories=["development"],
    capabilities=["Feature 1", "Feature 2"]
)

# 創建轉換器
converter = SkillConverter(skill)

# 生成所有格式並保存
converter.save_all(Path("./output"))
```

### 3. 查看示例

```bash
cd /root/comic_ai
python examples/skill_converter_examples.py
```

---

## 核心發現

### 平臺特徵對比

```
┌──────────────┬───────────┬────────┬────────┬─────────┐
│ 特性         │ OpenCode  │ Claude │ Cursor │ CodeLaw │
├──────────────┼───────────┼────────┼────────┼─────────┤
│ 框架完整性   │ ⭐⭐⭐⭐⭐ │ ⭐⭐⭐  │ ⭐⭐   │ ⭐⭐⭐  │
│ 靈活性       │ ⭐⭐⭐   │ ⭐⭐⭐⭐│ ⭐⭐   │ ⭐⭐⭐  │
│ 可復用性     │ ⭐⭐⭐⭐ │ ⭐⭐   │ ⭐    │ ⭐⭐   │
│ 學習曲線     │ 中等      │ 低     │ 低    │ 中等    │
│ 權限控制     │ ✓         │ ✗      │ ✗     │ ✓       │
└──────────────┴───────────┴────────┴────────┴─────────┘
```

### 轉換優先順序

1. **OpenCode → Claude** (最容易)
2. **OpenCode → CodeLaw** (中等)
3. **OpenCode → Cursor** (較難)

### 統一格式

所有平臺都可以轉換為統一的 YAML 格式進行跨平臺共享：

```yaml
schema_version: "1.0"
metadata:
  id: skill-id
  name: Skill Name
  description: Skill description
platforms:
  opencode:
    enabled: true
  claude:
    enabled: true
  cursor:
    enabled: true
  codelaw:
    enabled: true
```

---

## 目錄結構

```
comic_ai/
├── README_SKILL_ANALYSIS.md          # 本文件
├── SKILL_ANALYSIS_SUMMARY.md         # 執行摘要
├── SKILL_CONFIGURATION_ANALYSIS.md   # 詳細分析
├── SKILL_CONVERTER_USAGE_GUIDE.md    # 使用指南
│
├── src/
│   └── utils/
│       └── skill_converter.py        # 核心轉換工具
│
├── examples/
│   └── skill_converter_examples.py   # 使用示例
│
└── .opencode/
    └── skills/                       # OpenCode Skills 配置
```

---

## 關鍵特性

### SkillConverter 工具

✅ 支持所有主流平臺轉換
✅ 自動驗證和錯誤檢測
✅ 批量轉換能力
✅ 統一中間格式
✅ 完整的文檔和示例

### 支持的轉換

| 源 | → | 目標 | 難度 |
|----|----|------|------|
| OpenCode | → | Claude | 易 |
| OpenCode | → | Cursor | 中 |
| OpenCode | → | CodeLaw | 易 |
| Claude | → | OpenCode | 難 |
| Any | → | Unified YAML | 易 |

---

## 實用案例

### 用例 1: 新 Skill 開發

```python
# 1. 定義 Skill
skill = UnifiedSkill(
    id="database-migration",
    name="Database Migration",
    description="Help with database migrations",
    version="1.0.0",
    categories=["database", "devops"],
    capabilities=["Generate scripts", "Validate changes"]
)

# 2. 轉換到所有平臺
converter = SkillConverter(skill)
converter.save_all(Path("./skills_output"))

# 3. 複製到各平臺配置目錄
#    .opencode/skills/database-migration/SKILL.md
#    Claude tool definitions
#    Cursor config
#    CodeLaw rules
```

### 用例 2: Skill 遷移

```python
# 解析現有 OpenCode Skill
skill = parse_opencode_skill(".opencode/skills/old-skill/SKILL.md")

# 轉換到其他平臺
converter = SkillConverter(skill)
claude_tool = converter.to_claude_tool()
cursor_config = converter.to_cursor_rules()
```

### 用例 3: 批量同步

```python
# 掃描所有 Skills 並轉換
for skill_dir in Path(".opencode/skills").glob("*/"):
    skill_md = skill_dir / "SKILL.md"
    try:
        skill = parse_opencode_skill(str(skill_md))
        converter = SkillConverter(skill)
        converter.save_all(Path(f"./converted/{skill_dir.name}"))
    except Exception as e:
        print(f"Error: {e}")
```

---

## 最佳實踐

### ✅ DO (推薦)

- 使用統一 YAML 格式管理 Skills
- 定期驗證 Skills 配置
- 在 Git 中跟蹤版本
- 使用語義化版本號
- 記錄 Skill 更改日誌

### ❌ DON'T (不推薦)

- 手動編輯轉換後的文件
- 混合使用不同平臺的配置
- 忽視命名規範
- 沒有文檔的 Skills
- 未驗證就部署

---

## 技術棧

**核心依賴**:
- Python 3.9+
- PyYAML (配置解析)
- dataclasses (數據結構)
- pathlib (文件操作)
- regex (驗證)

**測試平臺**:
- OpenCode 1.x
- Claude 3.x
- Cursor latest
- CodeLaw latest

---

## 改進建議

### 短期 (1-2 周)

- [ ] 工具完整測試
- [ ] 文檔校對
- [ ] CI/CD 集成
- [ ] 遷移指南

### 中期 (1-3 個月)

- [ ] Skill 倉庫建設
- [ ] Web UI 工具
- [ ] 最佳實踐模板
- [ ] 社區反饋

### 長期 (3-6 個月)

- [ ] 標準化格式
- [ ] 跨組織共享
- [ ] 自動化完善
- [ ] 生態發展

---

## 常見問題

**Q: 能轉換 Claude → OpenCode 嗎?**
A: 理論上可能，但困難較大，因為 Claude 的 Tool 信息不夠完整。

**Q: 如何添加新平臺支持?**
A: 在 SkillConverter 中添加新的 `to_<platform>()` 方法。

**Q: 轉換是否會失去信息?**
A: 统一格式會保留所有關鍵信息，但平臺特定的配置可能不同。

**Q: 如何驗證轉換結果?**
A: 查看生成的文件，並在目標平臺測試。

---

## 貢獻

歡迎提交 Issue 和 PR！

## 許可證

MIT License - 詳見 LICENSE 文件

---

## 聯繫和反饋

- 📝 提交 Issue: GitHub Issues
- 🤝 貢獻代碼: Pull Requests
- 💬 討論: GitHub Discussions

---

## 相關資源

- [OpenCode 官方](https://opencode.ai)
- [Claude API](https://docs.anthropic.com)
- [Cursor 官方](https://cursor.com)
- [本地分析文檔](./SKILL_CONFIGURATION_ANALYSIS.md)

---

**最後更新**: 2026-02-15
**版本**: 1.0.0
**狀態**: ✅ 完成

---

### 快速導航

🚀 [快速開始](#快速開始)
📖 [文檔導航](#文檔導航)
💡 [核心發現](#核心發現)
🔧 [實用案例](#實用案例)
❓ [常見問題](#常見問題)
