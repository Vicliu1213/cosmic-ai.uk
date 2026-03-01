# 代碼質量預防指南
# Code Quality Prevention Guide - 永續預防系統

## 📋 目錄
1. [常見錯誤列表](#常見錯誤列表)
2. [預防措施](#預防措施)
3. [開發工作流程](#開發工作流程)
4. [檢查清單](#檢查清單)

---

## 常見錯誤列表

### ❌ 錯誤 1: 缺失 Import 聲明

**症狀**: `NameError: name 'Any' is not defined`

**原因**:
```python
# ❌ 錯誤
def function() -> Any:  # 使用 Any 但未導入
    pass
```

**正確做法**:
```python
# ✅ 正確
from typing import Any

def function() -> Any:
    pass
```

**預防**: 所有使用類型註解的文件必須導入必要的類型
- `Any`, `Dict`, `List`, `Optional`, `Tuple`, `Union` 從 `typing` 導入
- 檢查清單: 見下方

---

### ❌ 錯誤 2: 語法錯誤 - 缺失括號

**症狀**: `SyntaxError: '(' was never closed`

**原因**:
```python
# ❌ 錯誤
result = np.angle(np.mean(signals * np.exp(1j * np.angle(signals)))
#                                                                   ^ 缺失 )
```

**正確做法**:
```python
# ✅ 正確
result = np.angle(np.mean(signals * np.exp(1j * np.angle(signals))))
#                                                                   ^^
```

**預防**: 
- 使用 IDE 的括號匹配功能 (Ctrl+])
- 提交前運行: `python -m py_compile file.py`
- 使用 pre-commit hooks 自動檢查

---

### ❌ 錯誤 3: 缺失函數調用

**症狀**: `SyntaxError: unmatched ')'`

**原因**:
```python
# ❌ 錯誤
with open(file) as f:
    f.write("text\n")
    f"extra data\n")  # 缺失 write() 調用
```

**正確做法**:
```python
# ✅ 正確
with open(file) as f:
    f.write("text\n")
    f.write("extra data\n")
```

**預防**:
- 檢查每一行都有完整的函數調用
- 使用 flake8 檢查: `flake8 file.py`

---

### ❌ 錯誤 4: 不一致的縮進

**症狀**: `IndentationError: unindent does not match any outer indentation level`

**原因**:
```python
# ❌ 錯誤 (混合 tab 和空格)
def method():
    	code1  # 1 個 tab
    code2   # 4 個空格
```

**正確做法**:
```python
# ✅ 正確 (統一使用 4 個空格)
def method():
    code1
    code2
```

**預防**:
- 在 IDE 中禁用 Tab，使用 4 個空格
- `.editorconfig` 配置
- pre-commit hooks 自動修復

---

## 預防措施

### 1️⃣ Pre-commit Hooks (本地預防)

**安裝**:
```bash
pip install pre-commit
cd /workspaces/cosmic-ai.uk
pre-commit install
```

**功能**:
- ✅ 自動檢查 Python 語法
- ✅ 檢查缺失的導入
- ✅ 檢查括號匹配
- ✅ 修復空行和尾部空格
- ✅ 運行 flake8 linting
- ✅ 運行 mypy 類型檢查

**自動運行**:
```bash
git commit -m "message"
# pre-commit hooks 自動運行檢查
# 如果失敗，修復問題後重新提交
```

**手動運行**:
```bash
pre-commit run --all-files
```

---

### 2️⃣ CI/CD 流水線 (遠程防護)

**工作流程**: `.github/workflows/code-quality.yml`

**檢查項目**:
- Python 3.10, 3.11, 3.12 兼容性
- 語法驗證
- Flake8 linting
- Mypy 類型檢查
- Bandit 安全檢查
- 218+ 單元測試
- 代碼覆蓋率

**觸發時機**:
- 推送到 `main` 或 `develop` 分支
- 創建 Pull Request

**失敗時**:
- ❌ 無法合併 PR
- ❌ 需要修復問題後重試

---

### 3️⃣ 代碼質量檢查器

**運行**:
```bash
python scripts/code_quality_checker.py
```

**檢查内容**:
- 所有 Python 文件語法
- 缺失的導入
- 218+ 單元測試
- Flake8 linting 規則

---

## 開發工作流程

### ✅ 正確的開發步驟

```
1. 創建 feature 分支
   $ git checkout -b feature/your-feature

2. 進行開發
   $ vim src/core/module.py

3. 提交前檢查
   $ python scripts/code_quality_checker.py
   $ python -m pytest src/tests/ -v

4. 提交代碼
   $ git add .
   $ git commit -m "feat: your feature"
   # ⚙️ pre-commit hooks 自動檢查

5. 推送到遠程
   $ git push origin feature/your-feature

6. 創建 Pull Request
   # 🤖 GitHub Actions 自動驗證
   # ✅ 所有檢查通過後才能合併

7. 合併到 main
   $ git merge feature/your-feature
```

---

## 檢查清單

### 📝 提交前檢查清單

在每次提交之前，請檢查以下項目:

#### 代碼檢查
- [ ] ✅ 所有 Python 文件都有有效的語法
- [ ] ✅ 所有使用的類型都已導入
  - [ ] `from typing import Any` (如果使用 `Any`)
  - [ ] `from typing import Dict, List, Optional` (如果需要)
  - [ ] `from typing import Tuple, Union` (如果需要)
- [ ] ✅ 所有括號都正確匹配 `()`, `[]`, `{}`
- [ ] ✅ 縮進統一 (4 個空格，不使用 Tab)
- [ ] ✅ 沒有尾部空格
- [ ] ✅ 文件結尾有新行

#### 功能檢查
- [ ] ✅ 邏輯正確
- [ ] ✅ 沒有未使用的變量
- [ ] ✅ 沒有未使用的導入
- [ ] ✅ 適當的錯誤處理

#### 測試檢查
- [ ] ✅ 為新功能編寫了測試
- [ ] ✅ 所有測試都通過
- [ ] ✅ 代碼覆蓋率滿足要求

#### 文檔檢查
- [ ] ✅ 函數有適當的 docstring
- [ ] ✅ 複雜邏輯有註釋
- [ ] ✅ 提交消息清晰有意義

---

### 🔧 自動修復命令

```bash
# 自動修複所有 pre-commit 問題
pre-commit run --all-files

# 自動排序導入
isort src/

# 自動修複空行和尾部空格
autopep8 --in-place --aggressive src/file.py

# 檢查特定文件的語法
python -m py_compile src/file.py

# 運行代碼質量檢查
python scripts/code_quality_checker.py

# 運行所有測試
python -m pytest src/tests/ -v
```

---

### 🚨 常見錯誤快速參考

| 錯誤類型 | 症狀 | 檢查命令 | 修復方法 |
|---------|------|---------|---------|
| 缺失 Import | `NameError` | `grep "-> Any" file.py` | 添加 `from typing import Any` |
| 語法錯誤 | `SyntaxError` | `python -m py_compile file.py` | 检查括号匹配 |
| 縮進錯誤 | `IndentationError` | 查看 IDE 缩進指示 | 使用 4 個空格 |
| 未使用導入 | Linting 警告 | `flake8 file.py` | 移除未使用的導入 |

---

## 持續改進

### 📊 監控指標

每週檢查:
- [ ] 代碼覆蓋率趨勢
- [ ] 錯誤率
- [ ] 測試通過率
- [ ] PR 合併時間

### 🎯 改進目標

- **2026 年 3 月**: 100% 語法驗證通過 ✅
- **2026 年 4 月**: 90%+ 代碼覆蓋率
- **2026 年 5 月**: 零 critical bugs

---

## 需要幫助?

遇到問題時:

1. **查看錯誤消息** - 它通常指出確切的問題位置
2. **運行檢查器** - `python scripts/code_quality_checker.py`
3. **查看此指南** - 在上方常見錯誤列表中尋找
4. **查看提交歷史** - 看看以前如何修復類似問題
5. **詢問隊友** - 分享錯誤消息和上下文

---

**最後更新**: 2026-03-01  
**維護者**: Cosmic AI 開發團隊  
**版本**: 1.0
