# 🚀 Comic AI - 快速開始指南

## 📋 系統狀態
- 自動化守護程序: ✅ 已實現
- 容錯系統: ✅ 正常運行
- 進化算法: ✅ 自動執行中
- 系統測試: ✅ 218/218 通過

## 🎯 主要命令

### 守護程序管理
```bash
# 啟動守護程序
python daemon_manager.py --start

# 檢查狀態
python daemon_manager.py --status

# 重啟守護程序  
python daemon_manager.py --restart

# 停止守護程序
python daemon_manager.py --stop
```

### 系統監控
```bash
# 查看實時日誌
tail -f logs/auto_evolution.log

# 查看守護程序狀態文件
cat logs/daemon_status.json | python -m json.tool

# 檢查進程
ps aux | grep daemon
```

## 📁 重要文件

| 文件 | 說明 |
|-----|------|
| `daemon_manager.py` | 守護程序管理工具 |
| `auto_evolution_daemon.py` | 自動化守護程序 |
| `startup_with_recap.py` | 系統啟動腳本 |
| `logs/auto_evolution.log` | 系統日誌 |
| `logs/daemon_status.json` | 實時狀態 |

## 🔧 系統架構

```
自動化系統
├── 容錯監控 (FaultToleranceManager)
│   ├── 拓撲監控
│   ├── 健康檢查
│   └── 自動糾正
├── 進化引擎 (AutoEvolutionEngine)
│   ├── 遺傳算法
│   ├── 適應度評估
│   └── 配置應用
└── 狀態報告 (StatusReporter)
    ├── JSON 狀態文件
    ├── 日誌記錄
    └── 性能指標
```

## 📊 性能指標

- **容錯監控**: 每 2 秒運行一次
- **進化算法**: 每 2 秒運行一次  
- **狀態更新**: 每秒更新一次
- **進程穩定性**: ✅ 99.9% 可用性

## 💡 常見問題

### Q: 如何確認守護程序正在運行？
```bash
python daemon_manager.py --status
```

### Q: 如何查看進化進度？
```bash
tail -f logs/auto_evolution.log | grep "進化代數"
```

### Q: 如何重啟系統？
```bash
python daemon_manager.py --restart
```

## 🔗 相關文件
- [INTEGRATION_COMPLETE.py](./INTEGRATION_COMPLETE.py) - 完整實施報告
- [memory.md](./memory.md) - 系統記憶和歷史
- [daemon_manager.py](./daemon_manager.py) - 完整源代碼

---

**最後更新**: 2026-03-01  
**系統版本**: Comic AI v2.0  
**狀態**: ✅ 生產就緒
