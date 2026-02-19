# VSCode 完整配置總結 | Complete VSCode Configuration Guide

> 完整的 VSCode settings.json、keybindings.json、tasks.json 配置指南，包含所有必要的 JSON 設定

## 📋 目錄 | Table of Contents

1. [settings.json - VSCode 核心設定](#settingsjson)
2. [keybindings.json - 快捷鍵綁定](#keybindingsjson)
3. [tasks.json - 任務定義](#tasksjson)
4. [launch.json - 除錯配置](#launchjson)
5. [extensions.json - 推薦擴充](#extensionsjson)
6. [快速參考表](#快速參考表)

---

## settings.json

### 📁 檔案位置 | File Location
```
/root/comic_ai/.vscode/settings.json
~/.config/Code/User/settings.json (Linux/macOS)
C:\Users\YourUsername\AppData\Roaming\Code\User\settings.json (Windows)
```

### 🎨 主要分類 | Main Categories

#### 1. 主題與外觀 | Theme & Appearance (行 1-17)
```json
{
  "workbench.colorTheme": "Tokyo Night Storm",
  "workbench.iconTheme": "material-icon-theme",
  "workbench.productIconTheme": "fluent-icons",
  "window.titleBarStyle": "custom",
  "window.title": "${dirty}${activeEditorShort}${separator}${rootName}",
  "window.zoomLevel": 0,
  "window.autoDetectColorScheme": true,
  "window.restoreWindows": "all",
  "window.commandCenter": true,
  "activityBar.visible": true,
  "activityBar.location": "side",
  "activityBar.size": "default",
  "sideBar.location": "left",
  "workbench.sideBar.location": "left",
  "workbench.statusBar.visible": true,
  "workbench.statusBar.feedback.visible": false
}
```

#### 2. 編輯器基本設定 | Editor Basics (行 18-43)
```json
{
  "editor.fontFamily": "'JetBrains Mono', 'Cascadia Code', Consolas, 'Microsoft YaHei', monospace",
  "editor.fontSize": 14,
  "editor.fontLigatures": true,
  "editor.lineHeight": 1.6,
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.formatOnType": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "always",
    "source.organizeImports": "always",
    "source.fixAll.eslint": "always",
    "source.fixAll.ruff": "always"
  }
}
```

#### 3. 自動補完設定 | Auto-Completion (行 44-60)
```json
{
  "editor.quickSuggestions": {
    "other": "inline",
    "comments": "inline",
    "strings": "inline"
  },
  "editor.quickSuggestionsDelay": 10,
  "editor.suggest.snippetsPreventQuickSuggestions": false,
  "editor.suggest.showStatusBar": true,
  "editor.suggest.localityBonus": true,
  "editor.suggestSelection": "first"
}
```

#### 4. 括號與導引線 | Brackets & Guides (行 61-77)
```json
{
  "editor.autoClosingBrackets": "always",
  "editor.autoClosingQuotes": "always",
  "editor.autoClosingDelete": "always",
  "editor.autoSurround": "languageDefined",
  "editor.linkedEditing": true,
  "editor.guides.bracketPairs": true,
  "editor.guides.bracketPairsHorizontal": "active",
  "editor.guides.highlightActiveBracketPair": true,
  "editor.bracketPairColorization.enabled": true
}
```

#### 5. 光標與滾動 | Cursor & Scrolling (行 78-95)
```json
{
  "editor.smoothScrolling": true,
  "editor.cursorSmoothCaretAnimation": "on",
  "editor.cursorBlinking": "smooth",
  "editor.cursorStyle": "line",
  "editor.cursorWidth": 2,
  "editor.mouseWheelZoom": true,
  "editor.scrollBeyondLastLine": false,
  "editor.stickyScroll.enabled": true,
  "editor.minimap.enabled": true,
  "editor.minimap.renderCharacters": false
}
```

#### 6. Python 語言設定 | Python Settings (行 181-225)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.inlayHints.variableTypes": true,
  "python.analysis.inlayHints.functionReturnTypes": true,
  "python.analysis.extraPaths": [
    "${workspaceFolder}/src",
    "${workspaceFolder}/lib",
    "${workspaceFolder}/trading_engine"
  ],
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  }
}
```

#### 7. 終端設定 | Terminal Settings (行 226-251)
```json
{
  "terminal.integrated.fontFamily": "monospace",
  "terminal.integrated.fontSize": 13,
  "terminal.integrated.lineHeight": 1.2,
  "terminal.integrated.copyOnSelection": true,
  "terminal.integrated.cursorStyle": "line",
  "terminal.integrated.defaultLocation": "editor",
  "terminal.integrated.env.linux": {
    "PYTHONPATH": "${workspaceFolder}",
    "RAY_memory": "2000000000"
  }
}
```

#### 8. 檔案排除與關聯 | File Exclude & Association (行 142-178)
```json
{
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.coverage": true,
    "**/htmlcov": true
  },
  "files.associations": {
    "*.py": "python",
    "*.ipynb": "python",
    "requirements*.txt": "python",
    "*.yaml": "yaml",
    "*.json": "json"
  }
}
```

#### 9. 色彩客製化 | Color Customization (行 303-323)
```json
{
  "workbench.colorCustomizations": {
    "editor.background": "#1a1b26",
    "editor.foreground": "#c0caf5",
    "editor.lineHighlightBackground": "#2d2d3a",
    "sideBar.background": "#181825",
    "statusBar.background": "#1e1e2e",
    "activityBar.background": "#181825",
    "activityBar.activeBorder": "#89dceb"
  }
}
```

#### 10. 擴充設定 | Extension Settings (行 325-355)
```json
{
  "github.copilot.enable": {
    "*": true,
    "plaintext": true,
    "markdown": true
  },
  "cSpell.enabled": true,
  "cSpell.language": "en,zh-CN",
  "errorLens.enabled": true,
  "indent-rainbow.colors": [...]
}
```

---

## keybindings.json

### 📁 檔案位置 | File Location
```
/root/comic_ai/.vscode/keybindings.json
~/.config/Code/User/keybindings.json (Linux/macOS)
C:\Users\YourUsername\AppData\Roaming\Code\User\keybindings.json (Windows)
```

### 🎯 快捷鍵分類 | Keybindings Categories

#### 1. 活動欄導航 | Activity Bar Navigation
```json
{
  "key": "ctrl+shift+e",
  "command": "workbench.view.explorer",
  "description": "Explorer | 檔案總管"
},
{
  "key": "ctrl+shift+f",
  "command": "workbench.view.search",
  "description": "Search | 搜尋"
},
{
  "key": "ctrl+shift+g",
  "command": "workbench.view.scm",
  "description": "Git | 版本控制"
},
{
  "key": "ctrl+shift+d",
  "command": "workbench.view.debug",
  "description": "Dashboard | 儀表板"
},
{
  "key": "ctrl+shift+x",
  "command": "workbench.view.extensions",
  "description": "Extensions | 擴充套件"
}
```

#### 2. 工作流程快捷鍵 | Workflow Shortcuts (Alt+Shift+數字)
```json
{
  "key": "shift+alt+1",
  "command": "extension.opencomcode.runLiveServer",
  "description": "Open Dashboard | 開啟儀表板"
},
{
  "key": "shift+alt+2",
  "command": "workbench.action.openTerminal",
  "description": "Terminal | 終端"
},
{
  "key": "shift+alt+4",
  "command": "workbench.view.run",
  "description": "Run & Debug | 執行與除錯"
},
{
  "key": "shift+alt+6",
  "command": "workbench.action.tasks.test",
  "description": "Test | 測試"
}
```

#### 3. 編輯器編輯快捷鍵 | Editor Editing
```json
{
  "key": "ctrl+/",
  "command": "editor.action.commentLine",
  "description": "Toggle Comment | 切換註解"
},
{
  "key": "ctrl+h",
  "command": "editor.action.startFindReplaceAction",
  "description": "Find and Replace | 尋找和取代"
},
{
  "key": "alt+up",
  "command": "editor.action.moveLinesUpAction",
  "description": "Move Line Up | 向上移動行"
},
{
  "key": "alt+down",
  "command": "editor.action.moveLinesDownAction",
  "description": "Move Line Down | 向下移動行"
}
```

#### 4. 除錯快捷鍵 | Debug Shortcuts
```json
{
  "key": "f5",
  "command": "workbench.action.debug.start",
  "description": "Start Debugging | 開始除錯"
},
{
  "key": "shift+f5",
  "command": "workbench.action.debug.stop",
  "description": "Stop Debugging | 停止除錯"
},
{
  "key": "f9",
  "command": "editor.debug.action.toggleBreakpoint",
  "description": "Toggle Breakpoint | 切換中斷點"
},
{
  "key": "f10",
  "command": "workbench.action.debug.stepOver",
  "description": "Step Over | 逐步執行"
},
{
  "key": "f11",
  "command": "workbench.action.debug.stepInto",
  "description": "Step Into | 逐步進入"
}
```

---

## tasks.json

### 📁 檔案位置 | File Location
```
/root/comic_ai/.vscode/tasks.json
```

### 🚀 任務分類 | Task Categories

#### 1. 儀表板與插件 | Dashboard & Plugins
```json
{
  "label": "Dashboard | 儀表板",
  "type": "shell",
  "command": "python",
  "args": ["${workspaceFolder}/logging_dashboard.py"],
  "presentation": {"reveal": "always", "panel": "shared", "group": "Dashboard"},
  "isBackground": true
},
{
  "label": "Upload Plugin | 上傳插件",
  "type": "shell",
  "command": "bash",
  "args": ["${workspaceFolder}/launch_upload.sh"],
  "presentation": {"reveal": "always", "group": "Plugins"}
},
{
  "label": "Persistent System | 持久系統",
  "type": "shell",
  "command": "bash",
  "args": ["${workspaceFolder}/start_persistent_system.sh"],
  "presentation": {"reveal": "always", "group": "System"},
  "isBackground": true
}
```

#### 2. Python 開發任務 | Python Development
```json
{
  "label": "Python: Run Current File | 執行當前檔案",
  "type": "shell",
  "command": "${workspaceFolder}/venv/bin/python",
  "args": ["${file}"],
  "presentation": {"reveal": "always", "group": "Python"},
  "problemMatcher": ["$python"]
},
{
  "label": "Python: Install Requirements | 安裝依賴",
  "type": "shell",
  "command": "${workspaceFolder}/venv/bin/pip",
  "args": ["install", "-r", "${workspaceFolder}/requirements.txt"],
  "presentation": {"reveal": "always", "group": "Python"}
}
```

#### 3. 測試任務 | Testing Tasks
```json
{
  "label": "pytest: Run All Tests | 執行所有測試",
  "type": "shell",
  "command": "${workspaceFolder}/venv/bin/pytest",
  "args": ["-v", "--tb=short", "--cov=.", "--cov-report=html"],
  "presentation": {"reveal": "always", "group": "Testing"}
},
{
  "label": "pytest: Run Current Test File | 執行目前測試檔案",
  "type": "shell",
  "command": "${workspaceFolder}/venv/bin/pytest",
  "args": ["${file}", "-v", "--tb=short"],
  "presentation": {"reveal": "always", "group": "Testing"}
}
```

#### 4. Git 任務 | Git Tasks
```json
{
  "label": "Git: Status | 版本控制狀態",
  "type": "shell",
  "command": "git",
  "args": ["status"],
  "presentation": {"reveal": "always", "group": "Git"}
},
{
  "label": "Git: Commit & Push | 提交並推送",
  "type": "shell",
  "command": "bash",
  "args": ["-c", "git add . && git commit -m 'Update' && git push origin main"],
  "presentation": {"reveal": "always", "group": "Git"}
}
```

#### 5. 系統監控任務 | System Monitoring
```json
{
  "label": "System: Health Check | 系統健康檢查",
  "type": "shell",
  "command": "bash",
  "args": ["${workspaceFolder}/scripts/health-check.sh"],
  "presentation": {"reveal": "always", "group": "System"}
},
{
  "label": "System: Metrics | 系統指標",
  "type": "shell",
  "command": "bash",
  "args": ["-c", "watch -n 1 '${workspaceFolder}/scripts/metrics.sh'"],
  "presentation": {"reveal": "always", "group": "System"},
  "isBackground": true
}
```

---

## launch.json

### 📁 檔案位置 | File Location
```
/root/comic_ai/.vscode/launch.json
```

### 🐍 Python 除錯配置 | Python Debug Configuration

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File | 當前檔案",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true,
      "args": []
    },
    {
      "name": "Python: Module | Python 模組",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"],
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Attach | 附加到進程",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "localhost",
      "pathMapping": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "."
        }
      ]
    },
    {
      "name": "Chrome | Chrome 瀏覽器",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:8080",
      "webRoot": "${workspaceFolder}"
    }
  ]
}
```

---

## extensions.json

### 📁 檔案位置 | File Location
```
/root/comic_ai/.vscode/extensions.json
```

### 📦 推薦擴充 | Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "charliermarsh.ruff",
    "ms-vscode.makefile-tools",
    "eamodio.gitlens",
    "github.copilot",
    "github.copilot-chat",
    "ms-vscode.remote-explorer",
    "ms-vscode-remote.remote-ssh",
    "ms-vscode-remote.remote-containers",
    "ms-vscode-remote.remote-wsl",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-yaml",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "ritwickdey.liveserver",
    "ms-mssql.mssql",
    "ms-kubernetes-tools.vscode-kubernetes-tools",
    "gruntfuggly.todo-tree",
    "wayou.vscode-todo-highlight",
    "drcika.apc-extension",
    "dracula-theme.theme-dracula",
    "pkief.material-icon-theme",
    "PMinden.filesize",
    "wayou.color-highlight",
    "LittleFoxTeam.vscode-python-test-adapter",
    "Zignd.html-css-class-completion",
    "formulahendry.code-runner",
    "yzhang.markdown-all-in-one",
    "ms-python.pylint",
    "ms-python.isort",
    "ms-python.black-formatter"
  ]
}
```

---

## 快速參考表

### 🎯 核心快捷鍵 | Essential Shortcuts

| 快捷鍵 | 功能 | 用途 |
|--------|------|------|
| `Ctrl+Shift+P` | 命令面板 | 搜尋所有命令 |
| `Ctrl+,` | 開啟設定 | 全域設定 |
| `Ctrl+K Ctrl+S` | 快捷鍵管理 | 修改快捷鍵 |
| `Shift+Alt+1` | 儀表板 | 開啟監控 |
| `Shift+Alt+6` | 測試 | 執行測試 |
| `F5` | 除錯 | 開始偵錯 |

### 📊 配置檔案大小 | Configuration File Sizes

| 檔案 | 行數 | 大小 | 分類 |
|------|------|------|------|
| settings.json | 356 行 | ~12KB | 核心設定 |
| keybindings.json | 88 行 | ~4KB | 快捷鍵 |
| tasks.json | 328 行 | ~10KB | 工作定義 |
| launch.json | ~50 行 | ~2KB | 除錯配置 |
| extensions.json | ~30 行 | ~1.5KB | 推薦擴充 |
| **總計** | **~850 行** | **~30KB** | **完整配置** |

### ✅ 設定驗證清單 | Verification Checklist

```bash
# 1. 驗證所有 JSON 檔案語法
cd /root/comic_ai/.vscode
python -m json.tool settings.json > /dev/null && echo "✓ settings.json OK"
python -m json.tool keybindings.json > /dev/null && echo "✓ keybindings.json OK"
python -m json.tool tasks.json > /dev/null && echo "✓ tasks.json OK"

# 2. 檢查檔案是否存在
ls -la /root/comic_ai/.vscode/*.json

# 3. VSCode 中驗證
# Ctrl+Shift+P → Developer: Show Extension Data
# 應該看到所有設定已正確載入
```

### 🚀 快速開始 | Quick Start

```bash
# 1. 開啟 VSCode
cd /root/comic_ai
code .

# 2. 按下快捷鍵打開儀表板
Shift+Alt+1

# 3. 開啟終端
Shift+Alt+2

# 4. 執行測試
Shift+Alt+6

# 5. 開啟命令面板並搜尋任務
Ctrl+Shift+P → Tasks: Run Task
```

---

**最後更新 | Last Updated**: 2026-02-19  
**版本 | Version**: 2.0  
**總配置行數 | Total Config Lines**: ~850 lines  
**支持語言 | Languages**: 繁體中文 | Traditional Chinese | English
