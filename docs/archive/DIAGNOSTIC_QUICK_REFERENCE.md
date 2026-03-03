# Comic AI 系統快速參考

## 🟢 當前運行狀態
```bash
# 檢查守護程序狀態
python daemon_manager.py --status

# 查看實時日誌
tail -f logs/auto_evolution.log
tail -f logs/daemon_status.json
```

## 🎮 守護程序管理命令

```bash
# 啟動守護程序
python daemon_manager.py --start

# 停止守護程序
python daemon_manager.py --stop

# 重啟守護程序
python daemon_manager.py --restart

# 檢查狀態
python daemon_manager.py --status
```

## 📊 進化系統手動命令

```bash
# OpenCode 進化系統
python opencode_evolution_system.py --init      # 初始化
python opencode_evolution_system.py --record    # 記錄性能
python opencode_evolution_system.py --evolve    # 進化優化
python opencode_evolution_system.py --report    # 生成報告

# OpenCode 進化引擎
python opencode_evolution_engine.py --init      # 初始化
python opencode_evolution_engine.py --record    # 記錄性能
python opencode_evolution_engine.py --evolve    # 進化優化
python opencode_evolution_engine.py --report    # 生成報告
```

## 📁 關鍵文件位置

| 文件 | 位置 | 用途 |
|-----|------|------|
| 容錯管理器 | auto_evolution_daemon.py:57-133 | 監控和修復 |
| 進化引擎 | auto_evolution_daemon.py:136-241 | 自動進化 |
| daemon管理 | daemon_manager.py | 生命周期管理 |
| 進化算法 | quantum_genetic_algorithm.py | 量子遺傳算法 |
| 狀態報告 | logs/daemon_status.json | 實時狀態 |
| 進化日誌 | logs/auto_evolution.log | 運行日誌 |

## 🔍 監控指標

```json
{
  "容錯拓撲健康度": "100.0%",
  "進化代數": 3,
  "最佳適應度": 0.7779,
  "運行線程": 3,
  "檢查間隔": {
    "容錯監控": "30秒",
    "進化引擎": "300秒(5分鐘)",
    "狀態報告": "60秒"
  }
}
```

## ⚠️ 已知問題

1. **硬編碼數據**: 性能數據是固定值 (0.85, 0.92, 1.2)
2. **模擬拓撲**: 拓撲狀態總是健康 (100%)
3. **無真實效果**: 進化沒有實際修改系統配置
4. **無系統集成**: main_system.py 不啟動 daemon

## 💡 改進優先度

| 優先度 | 任務 | 工作量 |
|--------|------|--------|
| 🔴 高 | 實現真實性能數據收集 | 2-3小時 |
| 🔴 高 | 連接到真實系統指標 | 2-3小時 |
| 🟠 中 | 實現真實修復邏輯 | 3-4小時 |
| 🟠 中 | 系統集成 (main_system) | 2小時 |
| 🟡 低 | systemd 集成 | 1小時 |

## 🔧 立即可做的改進

### 1. 添加系統監控 (立即)
```python
# auto_evolution_daemon.py 中添加 psutil
import psutil

# 在 check_topology_health() 中使用
cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory().percent
```

### 2. 連接 main_system.py (立即)
```python
# main_system.py 的 initialize() 中添加
from daemon_manager import start_daemon
start_daemon()
```

### 3. 改進性能收集 (短期)
- 實現任務指標收集機制
- 連接到真實的系統監控
- 實現性能反饋環

### 4. 自動優化配置 (短期)
- 實現真實的配置應用機制
- 根據進化結果調整參數
- 測試和驗證優化效果

## 📈 性能基準

當前系統報告的性能指標（硬編碼）:
- 品質分數: 0.85
- 成功率: 0.92
- 平均響應時間: 1.2 秒
- 資源效率: 0.78
- 錯誤率: 0.08

**注意**: 這些是模擬數據，不反映真實系統性能。

## 🎯 下一步行動

1. 閱讀完整診斷報告
2. 識別最高優先級的改進
3. 實現真實數據收集
4. 測試修改的系統
5. 部署到生產環境
