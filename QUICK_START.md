# 🚀 快速開始指南

系統激活完成於 **2026-02-20**

---

## 📋 三步快速上手

### 1️⃣ 激活虛擬環境
```bash
cd /root/comic_ai
source venv/bin/activate
```

### 2️⃣ 驗證系統狀態
```bash
# 檢查所有依賴
pytest src/tests/test_api.py -v

# 完整測試（可選）
pytest src/tests/ -v
```

### 3️⃣ 運行應用
```bash
# CLI 應用
python3 src/cli/cli.py

# 量子交易演算法
python3 quantum_grover_trading_algorithm.py

# 多智能體系統
python3 demo_singularity_system.py
```

---

## 📚 重要文檔

| 用途 | 文檔 |
|------|------|
| **系統概述** | [`README.md`](README.md) |
| **激活記錄** | [`memory.md`](memory.md) |
| **文檔索引** | [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) |
| **整理報告** | [`DOCUMENTATION_CLEANUP_SUMMARY.md`](DOCUMENTATION_CLEANUP_SUMMARY.md) |
| **項目架構** | [`SYSTEM_OVERVIEW.md`](SYSTEM_OVERVIEW.md) |

---

## ✅ 系統狀態

```
核心系統:       ✅ 激活完成
量子引擎:       ✅ Qiskit 2.3.0
分佈式計算:     ✅ Ray 2.52.1
多智能體:       ✅ Semantic Kernel 1.39.4
測試覆蓋率:     ✅ 78.9% (172/218)
文檔整理:       ✅ 完成 (43.5% 精簡)
```

---

## 🗂️ 文檔位置

- **根目錄**: 35 個活躍文檔
- **歸檔區**: `docs/archive/` (19 個分類文檔)
  - `session_reports/` - 會話記錄
  - `deployment_guides/` - 部署指南
  - `quantum_docs/` - 量子文檔
  - `trading_docs/` - 交易文檔
  - `system_config/` - 系統配置
  - `activation_history/` - 激活記錄

---

## ⚡ 常用命令

```bash
# 安裝依賴
pip install -r requirements.txt

# 代碼檢查
flake8 . --count --select=E9,F63,F7,F82

# 運行測試
pytest src/tests/ -v

# 退出虛擬環境
deactivate
```

---

## 🆘 故障排除

**問題**: 模塊導入失敗
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

**問題**: 環境變量錯誤
```bash
# 設置環境
export PYTHONPATH=/root/comic_ai:$PYTHONPATH
```

**問題**: 測試失敗
```bash
pytest -vv --tb=long src/tests/test_api.py
```

---

## 📊 系統組件

| 組件 | 版本 | 狀態 |
|------|------|------|
| Python | 3.12.3 | ✅ |
| NumPy | 1.26.4 | ✅ |
| Pandas | 3.0.1 | ✅ |
| Qiskit | 2.3.0 | ✅ |
| Ray | 2.52.1 | ✅ |
| Semantic Kernel | 1.39.4 | ✅ |

---

## 🎯 下一步

1. 查看 `DOCUMENTATION_INDEX.md` 了解完整文檔
2. 修復失敗的 46 個測試 (主要是高級功能)
3. 開始開發新功能

---

**最後更新**: 2026-02-20  
**狀態**: ✅ 就緒  
**聯繫**: 查看 `README.md` 的貢獻指南
