# ⚡ Cosmic AI 快速開始指南

**最後更新**: 2026-03-02  
**版本**: 1.0

---

## 🚀 5 秒內開始

```bash
# 啟動自動恢復系統
python3 system/recovery/cosmic_auto_recovery.py
```

就這樣！所有狀態會自動恢復。

---

## 📋 重要文件位置

打開這些文件了解更多：

| 文件 | 位置 | 用途 |
|------|------|------|
| 📊 進度 | `system/tracking/PROGRESS_TRACKER.md` | 查看進度 |
| 📑 導覽 | `system/navigation/INDEX.md` | 快速查找 |
| 📖 指南 | `docs/guides/AUTO_RECOVERY_GUIDE.md` | 詳細說明 |
| 📂 結構 | `FOLDER_STRUCTURE.md` | 資料夾說明 |
| 📋 紀錄 | `memory.md` | 激活紀錄 |

---

## 🎯 常見任務

### 查看進度
```bash
cat system/tracking/PROGRESS_TRACKER.md
```

### 編輯進度
```bash
nano system/tracking/PROGRESS_TRACKER.md
```

### 查找文件
```bash
cat system/navigation/INDEX.md
```

### 查看日誌
```bash
tail -20 data/logs/recovery.log
```

### 查看系統狀態
```bash
cat data/state/.recovery_state.json
cat data/state/.quantum_state.json
```

---

## 🔧 系統架構

```
Cosmic AI
├── system/                          # 核心系統
│   ├── recovery/                    # 自動恢復 ⭐
│   ├── tracking/                    # 進度追蹤 ⭐
│   └── navigation/                  # 導覽系統 ⭐
├── docs/                            # 文檔
├── data/                            # 數據和日誌
└── integration/                     # 第三方集成
```

---

## 💡 下一步

1. **運行自動恢復**: `python3 system/recovery/cosmic_auto_recovery.py`
2. **查看進度**: `cat system/tracking/PROGRESS_TRACKER.md`
3. **閱讀指南**: `cat docs/guides/AUTO_RECOVERY_GUIDE.md`
4. **了解結構**: `cat FOLDER_STRUCTURE.md`

---

## 📞 需要幫助？

- 找不到文件？ → `cat system/navigation/INDEX.md`
- 不知道怎麼用？ → `cat docs/guides/AUTO_RECOVERY_GUIDE.md`
- 想看詳細紀錄？ → `cat memory.md`
- 遇到問題？ → `tail -20 data/logs/recovery.log`

---

**準備好了？開始吧！** 🚀
