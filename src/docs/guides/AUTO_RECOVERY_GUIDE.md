# 🔄 Cosmic AI 自動恢復系統指南

**創建日期**: 2026-03-02  
**版本**: 1.0  
**狀態**: ✅ 已激活

---

## 🎯 系統功能

自動恢復系統可以在對話中斷時自動恢復：

1. ✅ **對話狀態恢復** - 記住你在做什麼
2. ✅ **Git 分支恢復** - 恢復到上次的工作分支
3. ✅ **量子連接恢復** - 恢復模擬量子系統連接
4. ✅ **進度追蹤** - 始終知道下一步是什麼
5. ✅ **快速導航** - 快速找到所有重要文件

---

## 🚀 使用方法

### 方法 1: Python 版本 (推薦)

```bash
python3 cosmic_auto_recovery.py
```

**優點**:
- 自動檢查量子連接
- 保存量子狀態到 `.quantum_state.json`
- 更完整的恢復過程

### 方法 2: Shell 版本

```bash
bash auto_recovery.sh
```

**優點**:
- 快速啟動
- 不需要 Python 環境
- 輕量級

---

## 📊 恢復系統保存的內容

### 對話狀態 (`.recovery_state.json`)
```json
{
  "timestamp": "2026-03-02 16:51:20",
  "current_branch": "main",
  "last_commit": "a0650a7",
  "uncommitted_changes": 5,
  "status": "active",
  "quantum_connected": true
}
```

### 量子狀態 (`.quantum_state.json`)
```json
{
  "timestamp": "2026-03-02T16:51:58",
  "status": "connected",
  "qubits_initialized": 4,
  "quantum_circuits": 0,
  "simulated_quantum_systems": {
    "quantum_generator": "simulated_quantum_generator.py",
    "quantum_field_theory": "quantum_field_theory_system.py",
    "quantum_entanglement": "quantum_entanglement_verification.py",
    "quantum_genetic": "quantum_genetic_algorithm.py"
  }
}
```

### 恢復日誌 (`logs/recovery.log`)
```
[2026-03-02 16:51:20] 💾 正在保存恢復狀態...
[2026-03-02 16:51:20] ✅ 恢復狀態已保存
[2026-03-02 16:51:58] 🔄 檢測到之前的對話狀態，正在恢復...
[2026-03-02 16:51:58] 🌿 嘗試恢復分支: main
[2026-03-02 16:51:58] ✅ 恢復完成
```

---

## 🔗 量子連接詳解

### 集成的量子系統

| 系統 | 文件 | 功能 |
|------|------|------|
| 模擬量子生成器 | `simulated_quantum_generator.py` | 量子態生成和演化 |
| 量子場論系統 | `quantum_field_theory_system.py` | 量子場理論模擬 |
| 量子糾纏系統 | `quantum_entanglement_verification.py` | 量子糾纏驗證 |
| 量子遺傳演算 | `quantum_genetic_algorithm.py` | 遺傳算法優化 |

### 量子連接恢復流程

```
1. 檢查模擬量子生成器是否存在
   ↓
2. 嘗試導入量子模塊
   ↓
3. 初始化量子狀態 (4 個量子位)
   ↓
4. 保存量子狀態到 .quantum_state.json
   ↓
5. 返回連接狀態
```

---

## 💡 工作流程

### 對話開始時

```bash
# 1. 運行自動恢復
python3 cosmic_auto_recovery.py

# 2. 查看進度
cat PROGRESS_TRACKER.md

# 3. 查看計劃
cat task/ETHANALGOX_INTEGRATION_ROADMAP.md

# 4. 開始工作
```

### 工作中間

```bash
# 1. 隨時可以查看當前狀態
cat .recovery_state.json

# 2. 查看量子連接狀態
cat .quantum_state.json

# 3. 查看恢復日誌
tail -20 logs/recovery.log
```

### 對話結束時

```bash
# 自動恢復系統會自動保存所有狀態
# (每次運行 cosmic_auto_recovery.py 時執行)

# 可以手動更新進度表
cat > PROGRESS_TRACKER.md << 'EOF'
[更新進度]
EOF
```

---

## 📁 文件結構

```
/workspaces/cosmic-ai.uk/
├── cosmic_auto_recovery.py          # 自動恢復系統 (Python)
├── auto_recovery.sh                 # 自動恢復系統 (Shell)
├── .recovery_state.json             # 恢復狀態 (自動生成)
├── .quantum_state.json              # 量子狀態 (自動生成)
├── logs/
│   └── recovery.log                 # 恢復日誌 (自動生成)
├── PROGRESS_TRACKER.md              # 進度追蹤 (手動更新)
├── INDEX.md                         # 導覽索引
└── memory.md                        # 主紀錄檔
```

---

## ⚙️ 配置和自定義

### 修改恢復狀態文件位置

編輯 `cosmic_auto_recovery.py` 中的:

```python
self.recovery_state_file = self.cosmic_dir / ".my_recovery_state.json"
```

### 修改量子狀態文件位置

編輯 `cosmic_auto_recovery.py` 中的:

```python
self.quantum_state_file = self.cosmic_dir / ".my_quantum_state.json"
```

### 增加更多量子系統

在 `_restore_quantum_connection()` 中添加:

```python
from my_quantum_system import MyQuantumClass

# 初始化你的量子系統
quantum_state["my_system"] = MyQuantumClass()
```

---

## 🐛 故障排除

### 問題 1: 恢復失敗

**症狀**: 運行 `cosmic_auto_recovery.py` 後說"未初始化"

**解決方案**:
```bash
# 手動初始化
python3 cosmic_auto_recovery.py
```

### 問題 2: 量子連接失敗

**症狀**: 量子狀態顯示 "未連接"

**解決方案**:
```bash
# 檢查文件是否存在
ls simulated_quantum_generator.py

# 如果不存在，檢查路徑
find /workspaces -name "*quantum*generator*" -type f
```

### 問題 3: 日誌文件不更新

**症狀**: `logs/recovery.log` 時間戳沒變

**解決方案**:
```bash
# 檢查文件權限
ls -la logs/recovery.log

# 重建日誌目錄
mkdir -p logs
chmod 777 logs
```

---

## 📞 快速命令參考

```bash
# 運行自動恢復
python3 cosmic_auto_recovery.py

# 查看恢復狀態
cat .recovery_state.json | python3 -m json.tool

# 查看量子狀態
cat .quantum_state.json | python3 -m json.tool

# 查看恢復日誌
cat logs/recovery.log

# 查看最近 20 行日誌
tail -20 logs/recovery.log

# 搜索日誌
grep "error\|Error" logs/recovery.log

# 清空日誌 (謹慎!)
> logs/recovery.log

# 查看進度
cat PROGRESS_TRACKER.md

# 更新進度
nano PROGRESS_TRACKER.md
```

---

## ✨ 特色功能

### 1. 自動 Git 恢復
- 記住上次使用的分支
- 對話中斷後自動恢復分支
- 保存未提交的變更數量

### 2. 量子連接追蹤
- 記錄量子系統初始化狀態
- 跟蹤量子位元數量
- 保存量子系統列表

### 3. 進度同步
- 與 `PROGRESS_TRACKER.md` 同步
- 自動更新最後修改時間
- 支持手動和自動更新

### 4. 多層日誌
- 恢復日誌 (`logs/recovery.log`)
- JSON 狀態文件 (`.recovery_state.json`, `.quantum_state.json`)
- 即時控制台輸出

---

## 🎯 最佳實踐

1. ✅ **定期運行** - 每個 Session 開始時運行一次
2. ✅ **檢查狀態** - 完成一個任務後檢查 `.recovery_state.json`
3. ✅ **更新進度** - 重要工作完成後手動更新 `PROGRESS_TRACKER.md`
4. ✅ **查看日誌** - 遇到問題時查看 `logs/recovery.log`
5. ✅ **保持備份** - 定期 commit 到 Git

---

## 📊 統計和監控

### 恢復系統狀態

```bash
# 查看恢復系統詳細狀態
python3 -c "
import json
with open('.recovery_state.json') as f:
    state = json.load(f)
print(f'分支: {state[\"current_branch\"]}')
print(f'最後提交: {state[\"last_commit\"]}')
print(f'未提交變更: {state[\"uncommitted_changes\"]}')
print(f'量子連接: {state[\"quantum_connected\"]}')
"
```

---

## 🚀 下一步

1. **加入 CI/CD** - 自動在 GitHub Actions 中運行
2. **增加通知** - 對話中斷時發送通知
3. **備份到雲端** - 保存狀態到雲存儲
4. **多用戶支持** - 支持多個用戶的並行恢復
5. **量子優化** - 集成更多量子算法

---

**最後更新**: 2026-03-02  
**維護者**: Cosmic AI  
**狀態**: ✅ 穩定運行
