# 🆕 新人入門指南 - First Time User Guide

**適用於**: 第一次使用 Cosmic AI 的新人  
**語言**: 中文 / English  
**更新日期**: 2026-03-02

---

## 🎯 5 分鐘快速入門

### ❌ 不需要登入
Cosmic AI 系統**不需要登入帳號**，直接使用即可！

### ✅ 第一次使用 3 個步驟

```bash
# 1️⃣ 進入系統目錄
cd /workspaces/cosmic-ai.uk

# 2️⃣ 啟動自動恢復系統
python3 system/recovery/cosmic_auto_recovery.py

# 3️⃣ 查看快速開始
cat QUICK_START.md
```

**就這樣！系統已準備好！** 🚀

---

## 📚 新人必讀的 5 個文件

按照這個順序閱讀，會很快理解系統：

| 順序 | 文件 | 時間 | 內容 |
|------|------|------|------|
| 1️⃣ | `QUICK_START.md` | 3 分鐘 | 快速入門 |
| 2️⃣ | `README.md` | 5 分鐘 | 系統說明 |
| 3️⃣ | `FOLDER_STRUCTURE.md` | 10 分鐘 | 資料夾結構 |
| 4️⃣ | `system/tracking/PROGRESS_TRACKER.md` | 5 分鐘 | 當前進度 |
| 5️⃣ | `system/navigation/INDEX.md` | 10 分鐘 | 完整索引 |

**總共 33 分鐘即可完全熟悉系統！**

---

## 🚀 新人工作流程

### 第一天

```
早上:
  ✓ 閱讀 QUICK_START.md
  ✓ 運行 python3 system/recovery/cosmic_auto_recovery.py
  ✓ 查看 README.md

中午:
  ✓ 閱讀 FOLDER_STRUCTURE.md
  ✓ 了解資料夾結構

下午:
  ✓ 查看 PROGRESS_TRACKER.md 了解進度
  ✓ 查看 INDEX.md 快速查找文件
  ✓ 準備開始工作
```

### 之後每天

```
工作開始:
  1. 運行: python3 system/recovery/cosmic_auto_recovery.py
  2. 查看: cat system/tracking/PROGRESS_TRACKER.md
  3. 開始工作

工作中:
  - 需要找文件?     → cat system/navigation/INDEX.md
  - 不知道怎麼用?   → cat docs/guides/AUTO_RECOVERY_GUIDE.md
  - 需要幫助?       → cat QUICK_START.md

工作完成:
  - 更新進度: nano system/tracking/PROGRESS_TRACKER.md
  - 查看日誌: tail -20 data/logs/recovery.log
  - 提交代碼: git commit
```

---

## 🔧 系統架構 (新人版)

```
Cosmic AI 系統
│
├── 🔄 自動恢復 (不需要手動操作)
│   ├── 自動保存進度
│   ├── 自動保存 Git 分支
│   └── 自動保存量子連接
│
├── 📊 進度追蹤 (你需要更新)
│   ├── 查看當前進度
│   ├── 列出待辦項目
│   └── 記錄已完成工作
│
├── 📑 導覽系統 (快速找文件)
│   ├── 快速查找文件位置
│   ├── 了解系統結構
│   └── 獲取幫助
│
├── 📚 文檔系統 (學習和參考)
│   ├── 快速開始指南
│   ├── 詳細使用說明
│   └── 系統紀錄
│
└── 💾 數據系統 (自動管理)
    ├── 自動保存狀態
    └── 自動記錄日誌
```

---

## ❓ 新人常見問題

### Q1: 需要登入嗎？
**A**: 不需要！直接使用 `python3 system/recovery/cosmic_auto_recovery.py` 即可

### Q2: 對話中斷了怎麼辦？
**A**: 再次運行 `python3 system/recovery/cosmic_auto_recovery.py`，所有狀態會自動恢復

### Q3: 找不到某個文件？
**A**: 查看 `system/navigation/INDEX.md`，會告訴你所有文件位置

### Q4: 不知道現在進度如何？
**A**: 查看 `system/tracking/PROGRESS_TRACKER.md`，會顯示當前進度

### Q5: 需要詳細的使用說明？
**A**: 查看 `docs/guides/AUTO_RECOVERY_GUIDE.md`，有完整的詳細說明

### Q6: 系統是怎麼工作的？
**A**: 
1. 你運行自動恢復系統
2. 系統自動記錄你的進度
3. 下次對話時自動恢復狀態
4. 你只需專注於工作

### Q7: 我可以修改進度表嗎？
**A**: 可以！用 `nano system/tracking/PROGRESS_TRACKER.md` 編輯進度

### Q8: 日誌文件在哪裡？
**A**: 在 `data/logs/recovery.log`，用 `cat data/logs/recovery.log` 查看

---

## 🎓 新人學習路線

### 第 1 週 (熟悉系統)

**Day 1-2: 快速入門**
- [ ] 閱讀 QUICK_START.md
- [ ] 運行自動恢復系統
- [ ] 了解基本命令

**Day 3-4: 深入了解**
- [ ] 閱讀 README.md
- [ ] 閱讀 FOLDER_STRUCTURE.md
- [ ] 熟悉資料夾結構

**Day 5-7: 完全掌握**
- [ ] 閱讀 INDEX.md
- [ ] 閱讀 AUTO_RECOVERY_GUIDE.md
- [ ] 練習編輯進度表

### 第 2 週 (開始工作)

- [ ] 開始執行分配的任務
- [ ] 每天更新進度表
- [ ] 遇到問題查看相關文檔
- [ ] 習慣系統工作流程

### 第 3 週及以後

- [ ] 獨立完成工作
- [ ] 幫助其他新人
- [ ] 對系統提出改進建議

---

## 🛠️ 新人常用命令

### 系統啟動
```bash
# 啟動自動恢復系統
python3 system/recovery/cosmic_auto_recovery.py
```

### 查看信息
```bash
# 查看快速開始
cat QUICK_START.md

# 查看進度
cat system/tracking/PROGRESS_TRACKER.md

# 查找文件
cat system/navigation/INDEX.md

# 查看系統紀錄
cat memory.md
```

### 編輯和更新
```bash
# 編輯進度表
nano system/tracking/PROGRESS_TRACKER.md

# 查看日誌
tail -20 data/logs/recovery.log

# 查看系統狀態
cat data/state/.recovery_state.json
```

### Git 操作
```bash
# 查看狀態
git status

# 提交變更
git add .
git commit -m "feat: [描述你的工作]"

# 查看日誌
git log --oneline -10
```

---

## 💡 新人貼心提示

### ✅ 應該做的事

1. **定期更新進度表**
   - 完成一個任務後立即更新
   - 讓其他人知道你的進度

2. **查看日誌和狀態**
   - 了解系統是否正常運行
   - 調試問題時查看日誌

3. **保存你的工作**
   - 經常 commit 到 Git
   - 定期備份重要文件

4. **使用導覽系統**
   - 找不到文件時查看索引
   - 需要幫助時查看指南

5. **保持學習**
   - 閱讀系統文檔
   - 理解系統架構

### ❌ 不應該做的事

1. **不要手動修改狀態文件**
   - `data/state/` 中的文件由系統自動管理
   - 修改可能會破壞系統

2. **不要刪除關鍵目錄**
   - `system/` 目錄包含關鍵系統文件
   - `data/` 目錄包含重要數據

3. **不要忽視日誌中的錯誤**
   - 日誌中的錯誤可能表示系統問題
   - 及時報告和解決

4. **不要跳過入門指南**
   - 快速入門可以節省你的時間
   - 理解系統會讓工作更高效

5. **不要害怕提問**
   - 查看文檔中的常見問題
   - 向同事詢問

---

## 🎯 新人目標

### 第一天目標
- [ ] 成功啟動系統
- [ ] 理解基本概念
- [ ] 知道如何查看進度

### 第一週目標
- [ ] 完全理解系統結構
- [ ] 可以獨立編輯進度表
- [ ] 知道如何查找文件

### 第一個月目標
- [ ] 獨立完成分配的工作
- [ ] 熟練使用所有命令
- [ ] 能幫助其他新人

---

## 📞 新人需要幫助時

### 查找幫助的步驟

```
1️⃣ 查看 QUICK_START.md
   ↓
2️⃣ 查看 docs/guides/AUTO_RECOVERY_GUIDE.md
   ↓
3️⃣ 查看 system/navigation/INDEX.md
   ↓
4️⃣ 查看相關的詳細文檔
   ↓
5️⃣ 如果還是不懂，請向同事詢問
```

### 快速答案表

| 問題 | 查看這個文件 |
|------|------------|
| 如何開始？ | QUICK_START.md |
| 系統怎麼用？ | README.md |
| 資料夾在哪？ | FOLDER_STRUCTURE.md |
| 文件在哪？ | system/navigation/INDEX.md |
| 怎麼操作？ | docs/guides/AUTO_RECOVERY_GUIDE.md |
| 當前進度？ | system/tracking/PROGRESS_TRACKER.md |
| 系統紀錄？ | memory.md |
| 遇到錯誤？ | data/logs/recovery.log |

---

## 🎓 學習資源

### 推薦閱讀順序

1. **QUICK_START.md** ← 從這裡開始
2. **README.md**
3. **FOLDER_STRUCTURE.md**
4. **system/tracking/PROGRESS_TRACKER.md**
5. **system/navigation/INDEX.md**
6. **docs/guides/AUTO_RECOVERY_GUIDE.md**

### 隨時參考

- `QUICK_START.md` - 快速查詢
- `system/navigation/INDEX.md` - 文件位置
- `memory.md` - 系統歷史

---

## ✨ 新人成功秘訣

1. **別急著深入代碼**
   - 先理解系統架構
   - 再看具體代碼

2. **保持筆記**
   - 記錄重要命令
   - 記錄常見問題

3. **經常更新進度**
   - 幫助自己追蹤進度
   - 幫助團隊了解狀況

4. **充分利用自動恢復系統**
   - 它會幫你記錄一切
   - 不用擔心丟失進度

5. **主動提問**
   - 同事都願意幫忙
   - 快速學習最好的方式

---

## 🚀 準備好了嗎？

### 現在就開始吧！

```bash
# Step 1: 進入目錄
cd /workspaces/cosmic-ai.uk

# Step 2: 查看快速開始
cat QUICK_START.md

# Step 3: 啟動系統
python3 system/recovery/cosmic_auto_recovery.py

# Step 4: 開始工作！
```

---

**歡迎加入 Cosmic AI！** 🎉

如有任何問題，查看相關文檔或向同事詢問。祝你工作順利！

**最後更新**: 2026-03-02  
**版本**: 1.0
