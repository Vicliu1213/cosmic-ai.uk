# 互動式儀表版使用指南
# Interactive Dashboard User Guide

## 📊 概述

互動式儀表版是一個密交互式系統監控工具，提供即時的系統狀態、進度追蹤和記憶管理功能。

## 🚀 快速開始

### 方式 1: 直接運行 (Direct Run)
```bash
cd /workspaces/cosmic-ai.uk
python3 system/dashboard/interactive_dashboard.py
```

### 方式 2: 使用啟動腳本 (Using Launcher)
```bash
cd /workspaces/cosmic-ai.uk
bash system/dashboard/launch_dashboard.sh
```

## 🎯 功能菜單

### [1] 📊 概覽 (Overview)
顯示系統的完整概覽信息：
- **進度追蹤 (A 層)**: 當前進度狀態和文件大小
- **系統記憶 (B 層)**: 記憶文件大小、行數等信息
- **恢復系統狀態**: 上次恢復時間、恢復次數等
- **量子系統狀態**: 活躍系統數量、量子噪聲等
- **系統信息**: 更新時間、工作目錄等

### [2] 📈 進度詳細 (Progress Detail)
顯示進度追蹤文件 (PROGRESS_TRACKER.md) 的前 50 行內容。

### [3] 💾 記憶詳細 (Memory Detail)
顯示系統記憶文件 (memory.md) 的前 50 行內容。

### [4] 🔧 系統狀態 (System Status)
顯示系統文件夾結構和關鍵文件信息：
- 文件夾存在性檢查
- 關鍵文件大小統計
- 文件計數等

### [5] 🔄 重新整理 (Refresh)
刷新菜單視圖，重新加載最新數據。

### [0] 退出 (Exit)
優雅退出儀表版。

## 🎨 界面特性

### 視覺指示符
- ✅ 綠色: 成功/正常狀態
- ❌ 紅色: 失敗/錯誤
- ⚠️  黃色: 警告/未知狀態
- 🔄 藍色: 系統/操作符號

### 交互設計
- 簡潔清晰的菜單結構
- 中英文雙語支持
- 易於導航
- 快速響應

## 📝 配置信息

### 系統路徑
```
工作目錄: /workspaces/cosmic-ai.uk

系統文件夾: system/
├── tracking/          # 進度追蹤
├── recovery/          # 恢復系統
└── navigation/        # 導覽系統

數據文件夾: data/
├── state/            # 狀態文件
└── logs/             # 日誌文件
```

### 關鍵文件
| 文件 | 位置 | 功能 |
|------|------|------|
| PROGRESS_TRACKER.md | system/tracking/ | A 層進度追蹤 |
| memory.md | / | B 層系統記憶 |
| INDEX.md | system/navigation/ | C 層導覽索引 |
| recovery_state.json | data/state/ | 恢復狀態 |
| quantum_state.json | data/state/ | 量子狀態 |

## 💡 使用技巧

### 快速查看概覽
直接按 [1] 快速查看系統整體狀態。

### 監控進度
按 [2] 查看最新的進度信息。

### 檢查系統健康
按 [4] 確認所有關鍵文件都存在。

### 自動刷新
按 [5] 重新加載所有數據，獲取最新狀態。

## 🔧 故障排除

### 問題: "進度追蹤未找到"
解決方案:
```bash
# 檢查文件是否存在
ls -la system/tracking/PROGRESS_TRACKER.md

# 如果不存在，運行恢復系統
python3 system/recovery/cosmic_auto_recovery.py
```

### 問題: "系統記憶未找到"
解決方案:
```bash
# 檢查文件
ls -la memory.md

# 檢查文件大小
du -h memory.md
```

### 問題: 量子系統顯示 "未知"
解決方案:
```bash
# 檢查量子狀態文件
cat data/state/.quantum_state.json

# 重新初始化
python3 system/recovery/cosmic_auto_recovery.py
```

## 📊 性能指標

### 響應時間
- 菜單加載: < 100ms
- 概覽加載: < 500ms
- 詳細信息: < 1s

### 資源使用
- 內存: ~ 10-20 MB
- CPU: < 1%（在菜單等待時）
- 刷新間隔: 1 秒

## 🔄 與其他系統的集成

### 自動恢復系統
儀表版自動讀取恢復系統的狀態文件。

### 進度追蹤系統
實時顯示 A 層進度追蹤的最新內容。

### 系統記憶
訪問 B 層系統記憶的完整歷史。

### 量子系統
監控量子狀態和活躍系統計數。

## 📋 操作流程示例

### 場景 1: 每日系統檢查
```
1. 啟動儀表版
2. 按 [1] 查看概覽
3. 按 [4] 檢查系統狀態
4. 按 [0] 退出
```

### 場景 2: 進度監控
```
1. 啟動儀表版
2. 按 [2] 查看進度詳細
3. 按 [5] 刷新
4. 重複 2-3 步驟監控
```

### 場景 3: 故障排查
```
1. 啟動儀表版
2. 按 [1] 查看概覽找出問題
3. 按 [4] 詳細檢查系統狀態
4. 按 [3] 查看記憶歷史了解背景
```

## 🎓 學習路徑

### 初級用戶
1. 了解菜單結構
2. 練習 [1] 概覽視圖
3. 探索 [4] 系統狀態

### 中級用戶
1. 掌握所有菜單選項
2. 理解各個系統組件
3. 能夠快速定位問題

### 高級用戶
1. 修改源代碼以添加自定義視圖
2. 集成到自動化流程
3. 開發自己的監控機制

## 📞 支持和反饋

遇到問題或有改進建議？

- 📧 提交 Issue
- 💬 討論和反饋
- 📚 查看完整文檔

## 📄 相關文檔

- [系統導覽索引](../../system/navigation/INDEX.md)
- [進度追蹤](../../system/tracking/PROGRESS_TRACKER.md)
- [系統記憶](../../memory.md)
- [自動恢復指南](./AUTO_RECOVERY_GUIDE.md)
- [新人入門指南](../../FIRST_TIME_USER_GUIDE.md)

---

**版本**: 1.0.0  
**最後更新**: 2026-03-02  
**作者**: Cosmic AI 團隊
