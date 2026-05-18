# 宇宙智能體核心引擎 v3.0

本專案實現一個基於 Ray 的分佈式智能體系統，包含 15 個核心理論基因組、量子驗證任務、共識機制與交易引擎。

## .hermes 核心堆疊

- `.hermes/SOUL.md`：最高身份與主目標
- `.hermes/omega.md`：控制律與驗證邊界
- `.hermes/personality.md`：行為模式
- `.hermes/task.md`：任務分解與遞歸編排
- `.hermes/prompt.md`：提示激活層
- `.hermes/skills.md`：技能拓撲與編排層
- `.hermes/screen.md`：觀測面板定義
- `.hermes/memory.md`：記憶保留規則
- `.hermes/learn.md`：學習與升格規則
- `.hermes/protocol.md`：跨文件耦合協議
- `.hermes/checklist.md`：驗證清單
- `.hermes/glossary.md`：術語對齊字典

## 全局共享層

- `skills/hermes/`：`.hermes` 的共享鏡像入口，可供其他 agent / 工具直接讀取
- `skills/README.md`：共享層索引

## 目錄結構

- `config/`：系統設定檔
- `cosmic/`：核心 Python 模組
- `docs/`：15 個理論的詳細技術文檔
- `main.py`：主程式入口

## 安裝與執行

1. 安裝依賴：`pip install -r requirements.txt`
2. 修改 `config/cosmic_config.yaml` 中的 API 金鑰（如需）
3. 執行：`python main.py`

## Protected Content Rule

- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
