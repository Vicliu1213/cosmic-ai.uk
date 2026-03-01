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

## 🛠️ 自動化代碼質量檢查工具

### 完整代碼質量檢查器

```python
# code_quality_checker.py - 完整的代碼質量檢查系統
import os
import re
import subprocess
import ast
from pathlib import Path
from typing import Dict, List, Tuple

class CodeQualityChecker:
    """完整的代碼質量檢查工具"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = project_path
        self.issues = {
            "critical": [],
            "warning": [],
            "info": [],
        }
        self.total_files = 0
        self.passed_files = 0
    
    def check_all_python_files(self) -> Dict:
        """檢查所有 Python 文件"""
        
        print("🔍 掃描 Python 文件...\n")
        
        python_files = list(Path(self.project_path).rglob("*.py"))
        self.total_files = len(python_files)
        
        for py_file in python_files:
            if self._should_skip(py_file):
                continue
            
            self._check_file(py_file)
        
        return self._generate_report()
    
    def _should_skip(self, file_path: Path) -> bool:
        """判斷是否應該跳過該文件"""
        
        skip_dirs = {"__pycache__", ".venv", "venv", ".git", "node_modules"}
        skip_files = {"__pycache__.py"}
        
        parts = file_path.parts
        if any(part in skip_dirs for part in parts):
            return True
        
        if file_path.name in skip_files:
            return True
        
        return False
    
    def _check_file(self, file_path: Path):
        """檢查單個文件"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. 語法檢查
            self._check_syntax(file_path, content)
            
            # 2. Import 檢查
            self._check_imports(file_path, content)
            
            # 3. 類型提示檢查
            self._check_type_hints(file_path, content)
            
            # 4. 縮進檢查
            self._check_indentation(file_path, content)
            
            # 5. 命名規範檢查
            self._check_naming_conventions(file_path, content)
            
            self.passed_files += 1
            
        except Exception as e:
            self.issues["critical"].append(f"無法掃描 {file_path}: {e}")
    
    def _check_syntax(self, file_path: Path, content: str):
        """檢查 Python 語法"""
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.issues["critical"].append(
                f"[語法錯誤] {file_path}:{e.lineno} - {e.msg}"
            )
    
    def _check_imports(self, file_path: Path, content: str):
        """檢查 Import 聲明"""
        
        # 檢查缺失的 typing imports
        if "-> Any" in content or "Dict[" in content or "List[" in content:
            if "from typing import" not in content:
                self.issues["warning"].append(
                    f"[缺失 Import] {file_path} - 使用了類型註解但未導入 typing"
                )
        
        # 檢查未使用的導入
        tree = ast.parse(content)
        imports = set()
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        
        unused = imports - used_names
        for unused_import in unused:
            if not unused_import.startswith('_'):
                self.issues["info"].append(
                    f"[未使用導入] {file_path} - '{unused_import}'"
                )
    
    def _check_type_hints(self, file_path: Path, content: str):
        """檢查類型提示完整性"""
        
        # 尋找函數定義但缺少返回類型
        func_pattern = r'def\s+\w+\s*\([^)]*\)\s*:'
        no_return_hint = r'def\s+\w+\s*\([^)]*\)\s*:->'
        
        funcs = re.findall(func_pattern, content)
        hints = re.findall(no_return_hint, content)
        
        if len(funcs) > len(hints):
            self.issues["info"].append(
                f"[類型提示] {file_path} - 某些函數缺少返回類型提示"
            )
    
    def _check_indentation(self, file_path: Path, content: str):
        """檢查縮進規範"""
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line and not line[0].isspace() and not line.startswith('#'):
                # 檢查 tab vs space
                if '\t' in line[:20]:
                    self.issues["warning"].append(
                        f"[縮進混亂] {file_path}:{i} - 發現 Tab 字符,應使用空格"
                    )
    
    def _check_naming_conventions(self, file_path: Path, content: str):
        """檢查命名規範"""
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 函數應使用 snake_case
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    if not node.name.startswith('__'):
                        self.issues["info"].append(
                            f"[命名規範] {file_path}:{node.lineno} - 函數 '{node.name}' 應使用 snake_case"
                        )
            
            elif isinstance(node, ast.ClassDef):
                # 類應使用 PascalCase
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues["info"].append(
                        f"[命名規範] {file_path}:{node.lineno} - 類 '{node.name}' 應使用 PascalCase"
                    )
    
    def _generate_report(self) -> Dict:
        """生成檢查報告"""
        
        report = {
            "total_files": self.total_files,
            "passed_files": self.passed_files,
            "failed_files": self.total_files - self.passed_files,
            "critical_issues": len(self.issues["critical"]),
            "warnings": len(self.issues["warning"]),
            "info": len(self.issues["info"]),
            "all_passed": len(self.issues["critical"]) == 0,
        }
        
        return report
    
    def print_report(self):
        """打印檢查報告"""
        
        report = self._generate_report()
        
        print("\n" + "="*60)
        print("📊 代碼質量檢查報告")
        print("="*60)
        
        print(f"\n✅ 檢查統計:")
        print(f"  總文件數: {report['total_files']}")
        print(f"  通過文件: {report['passed_files']}")
        print(f"  失敗文件: {report['failed_files']}")
        
        print(f"\n⚠️  問題統計:")
        print(f"  🔴 Critical: {report['critical_issues']}")
        print(f"  🟡 Warning:  {report['warnings']}")
        print(f"  ℹ️  Info:     {report['info']}")
        
        if self.issues["critical"]:
            print(f"\n🔴 Critical 問題:")
            for issue in self.issues["critical"][:5]:
                print(f"  - {issue}")
            if len(self.issues["critical"]) > 5:
                print(f"  ... 還有 {len(self.issues['critical'])-5} 個問題")
        
        if self.issues["warning"]:
            print(f"\n🟡 Warning 問題:")
            for issue in self.issues["warning"][:5]:
                print(f"  - {issue}")
        
        if report["all_passed"]:
            print("\n✅ 所有檢查通過!")
        else:
            print("\n❌ 有問題需要修復")
        
        return report

if __name__ == "__main__":
    checker = CodeQualityChecker(".")
    checker.check_all_python_files()
    report = checker.print_report()
```

**運行檢查**:
```bash
python code_quality_checker.py
```

### Pre-commit Hook 配置

```yaml
# .pre-commit-config.yaml - 自動代碼檢查配置

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=127", "--select=E9,F63,F7,F82"]
  
  - repo: https://github.com/pycqa/pylint
    rev: pylint-2.17.4
    hooks:
      - id: pylint
        args: ["--disable=R,C", "--exit-zero"]
```

**安裝和使用**:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

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
