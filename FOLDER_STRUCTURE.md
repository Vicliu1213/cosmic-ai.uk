# 📂 Cosmic AI 資料夾結構指南

**版本**: 1.0  
**更新日期**: 2026-03-02

---

## 🗂️ 頂級目錄結構

```
/workspaces/cosmic-ai.uk/
├── 📋 README.md                          # 主系統指南
├── 📋 memory.md                          # 系統激活紀錄
├── 🎯 task/                              # 任務和計劃
│
├── 🔧 system/                            # ⭐ 系統管理 (重要)
│   ├── recovery/                         # 自動恢復系統
│   ├── tracking/                         # 進度追蹤
│   └── navigation/                       # 導覽系統
│
├── 📚 docs/                              # ⭐ 文檔 (重要)
│   ├── guides/                           # 使用指南
│   ├── system/                           # 系統文檔
│   ├── reference/                        # 參考文檔
│   └── archive/                          # 存檔文檔
│
├── 💾 data/                              # ⭐ 數據 (重要)
│   ├── state/                            # 狀態文件
│   └── logs/                             # 日誌文件
│
├── 🔌 integration/                       # 集成系統
│   └── ethanalgox/                       # EthanAlgoX 整合
│
└── 📦 [其他核心代碼目錄]
    ├── src/
    ├── config/
    ├── engine/
    └── ...
```

---

## 📖 各資料夾詳細說明

### 🔧 `system/` - 系統管理 (優先度: ⭐⭐⭐)

主要用於管理 Cosmic AI 的核心系統功能。

#### `system/recovery/` - 自動恢復系統

**位置**: `/workspaces/cosmic-ai.uk/system/recovery/`

**包含文件**:
```
cosmic_auto_recovery.py          # Python 自動恢復系統 (推薦)
auto_recovery.sh                 # Shell 自動恢復系統
```

**用途**:
- 對話狀態自動保存和恢復
- Git 分支自動恢復
- 量子連接自動恢復

**使用方式**:
```bash
# 推薦方式
python3 system/recovery/cosmic_auto_recovery.py

# 或使用 Shell
bash system/recovery/auto_recovery.sh
```

#### `system/tracking/` - 進度追蹤

**位置**: `/workspaces/cosmic-ai.uk/system/tracking/`

**包含文件**:
```
PROGRESS_TRACKER.md              # 進度追蹤表
```

**用途**:
- 追蹤當前工作進度
- 記錄已完成的任務
- 列出下一步行動

**何時查看**:
- 開始新工作時
- 完成一個 Task 後
- 不確定下一步做什麼時

**使用方式**:
```bash
cat system/tracking/PROGRESS_TRACKER.md
nano system/tracking/PROGRESS_TRACKER.md  # 編輯進度
```

#### `system/navigation/` - 導覽系統

**位置**: `/workspaces/cosmic-ai.uk/system/navigation/`

**包含文件**:
```
INDEX.md                         # 完整導覽索引
```

**用途**:
- 快速找到所有重要文件
- 了解系統架構
- 查看文件位置

**何時查看**:
- 找不到某個文件時
- 想了解系統結構時
- 需要快速查找時

**使用方式**:
```bash
cat system/navigation/INDEX.md
```

---

### 📚 `docs/` - 文檔系統 (優先度: ⭐⭐⭐)

主要用於存放所有文檔和指南。

#### `docs/guides/` - 使用指南

**位置**: `/workspaces/cosmic-ai.uk/docs/guides/`

**包含文件**:
```
AUTO_RECOVERY_GUIDE.md           # 自動恢復系統詳細指南
RECOVERY_SYSTEM_SETUP.txt        # 設置說明
```

**用途**:
- 詳細的使用步驟
- 故障排除方法
- 配置說明

**何時查看**:
- 不知道怎麼使用系統時
- 遇到問題時
- 需要詳細說明時

**使用方式**:
```bash
cat docs/guides/AUTO_RECOVERY_GUIDE.md
```

#### `docs/system/` - 系統文檔

**位置**: `/workspaces/cosmic-ai.uk/docs/system/`

**用途**:
- 系統設計文檔
- 架構說明
- 技術細節

#### `docs/reference/` - 參考文檔

**位置**: `/workspaces/cosmic-ai.uk/docs/reference/`

**用途**:
- API 參考
- 快速查找表
- 技術參考

#### `docs/archive/` - 存檔

**位置**: `/workspaces/cosmic-ai.uk/docs/archive/`

**用途**:
- 舊版本文檔
- 歷史記錄
- 參考檔案

---

### 💾 `data/` - 數據系統 (優先度: ⭐⭐⭐)

主要用於存放所有自動生成的狀態和日誌。

#### `data/state/` - 狀態文件

**位置**: `/workspaces/cosmic-ai.uk/data/state/`

**包含文件** (自動生成):
```
.recovery_state.json             # 恢復狀態
.quantum_state.json              # 量子狀態
```

**用途**:
- 保存對話狀態
- 記錄量子系統狀態
- 追蹤系統狀態

**何時查看**:
- 檢查系統狀態時
- 調試問題時
- 了解上次對話狀態時

**使用方式**:
```bash
# 查看恢復狀態
cat data/state/.recovery_state.json

# 查看量子狀態
cat data/state/.quantum_state.json
```

#### `data/logs/` - 日誌文件

**位置**: `/workspaces/cosmic-ai.uk/data/logs/`

**包含文件** (自動生成):
```
recovery.log                     # 恢復系統日誌
```

**用途**:
- 記錄系統操作
- 追蹤错誤
- 調試問題

**何時查看**:
- 遇到錯誤時
- 需要調試時
- 查看系統操作日誌時

**使用方式**:
```bash
# 查看日誌
cat data/logs/recovery.log

# 查看最後 20 行
tail -20 data/logs/recovery.log

# 實時監看日誌
tail -f data/logs/recovery.log
```

---

### 🔌 `integration/` - 集成系統

主要用於第三方系統集成。

#### `integration/ethanalgox/` - EthanAlgoX 集成

**位置**: `/workspaces/cosmic-ai.uk/integration/ethanalgox/`

**用途**:
- EthanAlgoX 集成代碼
- MarketBot 適配層
- LLM-TradeBot 路由層

---

## 🚀 快速文件查找

### 我要啟動系統
```bash
python3 system/recovery/cosmic_auto_recovery.py
```

### 我要查看進度
```bash
cat system/tracking/PROGRESS_TRACKER.md
```

### 我要找某個文件
```bash
cat system/navigation/INDEX.md
```

### 我要查看使用指南
```bash
cat docs/guides/AUTO_RECOVERY_GUIDE.md
```

### 我要看系統狀態
```bash
cat data/state/.recovery_state.json
cat data/state/.quantum_state.json
```

### 我要看日誌
```bash
cat data/logs/recovery.log
```

### 我要編輯進度
```bash
nano system/tracking/PROGRESS_TRACKER.md
```

---

## 📊 文件分類速查表

| 類型 | 位置 | 用途 |
|------|------|------|
| 快速開始 | README.md | 系統指南 |
| 啟動系統 | system/recovery/cosmic_auto_recovery.py | 自動恢復 |
| 查看進度 | system/tracking/PROGRESS_TRACKER.md | 進度追蹤 |
| 查找文件 | system/navigation/INDEX.md | 導覽索引 |
| 使用指南 | docs/guides/AUTO_RECOVERY_GUIDE.md | 詳細說明 |
| 系統紀錄 | memory.md | 激活紀錄 |
| 狀態文件 | data/state/ | 自動保存 |
| 日誌文件 | data/logs/ | 運行日誌 |
| 整合代碼 | integration/ethanalgox/ | 第三方集成 |

---

## 💡 最佳實踐

### ✅ 要這樣做:
1. 保持 `system/` 目錄整潔
2. 定期查看 `system/tracking/PROGRESS_TRACKER.md`
3. 查看 `data/logs/recovery.log` 調試問題
4. 不要手動修改 `data/state/` 中的文件

### ❌ 不要這樣做:
1. 移動或刪除 `system/` 目錄中的文件
2. 直接編輯 `data/state/` 中的 JSON 文件
3. 刪除 `data/logs/` 中的日誌文件
4. 在根目錄放置新的系統文件

---

## 🔄 結構維護

### 定期清理
```bash
# 檢查舊日誌 (超過 30 天)
find data/logs/ -mtime +30 -type f

# 清理舊日誌
rm data/logs/*.log.old
```

### 備份重要文件
```bash
# 備份進度表
cp system/tracking/PROGRESS_TRACKER.md system/tracking/PROGRESS_TRACKER.md.bak

# 備份狀態
cp data/state/.recovery_state.json data/state/.recovery_state.json.bak
```

---

## 📝 新建文件時的位置指南

如果要新增文件，應該放在哪裡？

| 文件類型 | 應放位置 |
|---------|--------|
| 新的指南 | docs/guides/ |
| 新的系統工具 | system/ (新建子目錄) |
| 新的日誌 | data/logs/ |
| 新的狀態文件 | data/state/ |
| 新的集成代碼 | integration/[系統名]/ |
| 新的文檔 | docs/system/ |

---

## ✨ 完整資料夾樹狀圖

```
/workspaces/cosmic-ai.uk/
│
├── 📋 README.md                          ← 開始這裡
├── 📋 memory.md                          ← 系統紀錄
├── 📋 task/ETHANALGOX_INTEGRATION_ROADMAP.md
│
├── 🔧 system/                            ← 核心系統
│   ├── recovery/
│   │   ├── cosmic_auto_recovery.py       ← 啟動這個
│   │   └── auto_recovery.sh
│   ├── tracking/
│   │   └── PROGRESS_TRACKER.md           ← 查看進度
│   └── navigation/
│       └── INDEX.md                      ← 快速查找
│
├── 📚 docs/                              ← 文檔
│   ├── guides/
│   │   ├── AUTO_RECOVERY_GUIDE.md        ← 詳細指南
│   │   └── RECOVERY_SYSTEM_SETUP.txt
│   ├── system/
│   ├── reference/
│   └── archive/
│
├── 💾 data/                              ← 自動生成
│   ├── state/
│   │   ├── .recovery_state.json          ← 恢復狀態
│   │   └── .quantum_state.json           ← 量子狀態
│   └── logs/
│       └── recovery.log                  ← 運行日誌
│
└── 🔌 integration/                       ← 集成系統
    └── ethanalgox/
        ├── marketbot_connector.py
        └── llm_tradebot_router.py
```

---

**最後更新**: 2026-03-02  
**維護者**: Cosmic AI  
**版本**: 1.0
