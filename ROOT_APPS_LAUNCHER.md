# 🚀 根目錄應用啟動指南

**更新日期**: 2026-02-20  
**狀態**: ✅ 所有應用已激活

---

## 📱 可用應用列表

### 1️⃣ CLI 主應用
**文件**: `src/cli/cli.py`

簡單的命令行界面，用於基本操作。

```bash
# 激活虛擬環境
source venv/bin/activate

# 運行 CLI
python3 src/cli/cli.py
```

**功能**:
- 系統狀態查看
- 基本配置管理
- 簡單操作

---

### 2️⃣ 文件處理 CLI - 圖片上傳 ⭐
**文件**: `intelligent_file_processor_cli.py`

支持上傳和分析圖片、文檔、代碼等多種文件類型。

```bash
source venv/bin/activate

# 上傳單個圖片並生成報告
python3 intelligent_file_processor_cli.py upload photo.jpg --report

# 上傳並輸出 JSON 格式
python3 intelligent_file_processor_cli.py upload image.png --json

# 批量處理目錄
python3 intelligent_file_processor_cli.py batch ./images/

# 查看幫助
python3 intelligent_file_processor_cli.py help
```

**支持的文件類型**:
```
🖼️  圖片: JPG, PNG, GIF, BMP, WEBP, SVG
📝 文字: TXT, MD, LOG, CSV, JSON, YAML, XML
💻 代碼: PY, JS, TS, JAVA, CPP, GO, RS
📦 壓縮: ZIP, TAR, GZ, BZ2, RAR, 7Z
📄 文檔: PDF, DOCX, XLSX, PPTX
```

**處理策略**:
- `hybrid`: 混合模式 (推薦) ⭐
- `advanced`: 前沿技術優先
- `classic`: 經典算法

---

### 3️⃣ 日誌儀表板
**文件**: `logging_dashboard.py`

Web 儀表板用於監控和查看日誌。

```bash
source venv/bin/activate

# 啟動儀表板 (默認 http://localhost:5000)
python3 logging_dashboard.py

# 指定端口
python3 logging_dashboard.py --port 8080

# 後臺運行
nohup python3 logging_dashboard.py > logs/dashboard.log 2>&1 &
```

**功能**:
- 實時日誌查看
- 性能監控
- 系統狀態

**訪問**: http://localhost:5000

---

### 4️⃣ 混合雲儀表板
**文件**: `hybrid_cloud_dashboard.py`

多雲環境管理儀表板。

```bash
source venv/bin/activate

# 啟動儀表板
python3 hybrid_cloud_dashboard.py

# 自定義配置
python3 hybrid_cloud_dashboard.py --config config/cloud_config.yaml
```

**功能**:
- 多雲資源管理
- 分佈式監控
- 成本分析

---

### 5️⃣ 任務面板
**文件**: `task_panel_optimized.py`

優化的任務管理和監控面板。

```bash
source venv/bin/activate

# 啟動任務面板
python3 task_panel_optimized.py

# 啟用實時更新
python3 task_panel_optimized.py --realtime
```

**功能**:
- 任務管理
- 進度監控
- 性能追蹤

---

### 6️⃣ 演示系統
**文件**: `demo_singularity_system.py`

多智能體交易系統演示。

```bash
source venv/bin/activate

# 運行演示
python3 demo_singularity_system.py

# 指定配置
python3 demo_singularity_system.py --config config/demo.yaml
```

**演示內容**:
- 多智能體交互
- 交易模擬
- 性能分析

---

### 7️⃣ Gemini 交易分析師
**文件**: `demo_gemini_trading_analyst.py`

AI 驅動的交易分析演示。

```bash
source venv/bin/activate

# 運行演示
python3 demo_gemini_trading_analyst.py

# 使用特定市場數據
python3 demo_gemini_trading_analyst.py --market BTC
```

---

## 🎯 快速啟動命令

### 僅激活 CLI (文件上傳)
```bash
cd /root/comic_ai
source venv/bin/activate
python3 intelligent_file_processor_cli.py upload image.jpg --report
```

### 啟動日誌儀表板
```bash
cd /root/comic_ai
source venv/bin/activate
python3 logging_dashboard.py
# 訪問: http://localhost:5000
```

### 啟動任務面板
```bash
cd /root/comic_ai
source venv/bin/activate
python3 task_panel_optimized.py
```

### 同時啟動多個應用
```bash
cd /root/comic_ai
source venv/bin/activate

# 終端 1 - CLI
python3 intelligent_file_processor_cli.py upload image.jpg

# 終端 2 - 儀表板
python3 logging_dashboard.py

# 終端 3 - 任務面板
python3 task_panel_optimized.py
```

---

## 🔧 使用 TMUX 同時管理多個應用

### 自動啟動所有應用
```bash
cd /root/comic_ai
source venv/bin/activate

# 創建 TMUX 會話
tmux new-session -d -s comic-ai

# 建立各個窗口並啟動應用
tmux new-window -t comic-ai -n cli
tmux send-keys -t comic-ai:cli "cd /root/comic_ai && source venv/bin/activate && python3 src/cli/cli.py" Enter

tmux new-window -t comic-ai -n dashboard
tmux send-keys -t comic-ai:dashboard "cd /root/comic_ai && source venv/bin/activate && python3 logging_dashboard.py" Enter

tmux new-window -t comic-ai -n task-panel
tmux send-keys -t comic-ai:task-panel "cd /root/comic_ai && source venv/bin/activate && python3 task_panel_optimized.py" Enter

# 查看會話
tmux list-sessions
tmux attach-session -t comic-ai
```

---

## 📊 應用狀態速查表

| 應用 | 文件 | 類型 | 狀態 |
|------|------|------|------|
| CLI 主應用 | `src/cli/cli.py` | 命令行 | ✅ 可用 |
| 文件處理 CLI | `intelligent_file_processor_cli.py` | 命令行 | ✅ 可用 |
| 日誌儀表板 | `logging_dashboard.py` | Web | ✅ 可用 |
| 混合雲儀表板 | `hybrid_cloud_dashboard.py` | Web | ✅ 可用 |
| 任務面板 | `task_panel_optimized.py` | Web | ✅ 可用 |
| 演示系統 | `demo_singularity_system.py` | 演示 | ✅ 可用 |
| Gemini 分析師 | `demo_gemini_trading_analyst.py` | 演示 | ✅ 可用 |

---

## 💡 推薦使用場景

### 場景 1: 上傳和分析圖片
```bash
python3 intelligent_file_processor_cli.py upload chart.png --report --strategy hybrid
```

### 場景 2: 批量處理文件
```bash
python3 intelligent_file_processor_cli.py batch ./project_files/
```

### 場景 3: 監控系統運行
```bash
# 終端 1
python3 logging_dashboard.py

# 終端 2
python3 task_panel_optimized.py

# 訪問: http://localhost:5000 和 http://localhost:5001
```

### 場景 4: 運行交易演示
```bash
python3 demo_singularity_system.py
python3 demo_gemini_trading_analyst.py
```

---

## 🐛 故障排除

### 應用無法啟動
```bash
# 1. 檢查虛擬環境
source venv/bin/activate

# 2. 驗證依賴
pip install -r requirements.txt --upgrade

# 3. 檢查文件
ls -la intelligent_file_processor_cli.py
```

### 端口已被占用
```bash
# 查找占用的進程
lsof -i :5000

# 殺死進程
kill -9 <PID>

# 使用不同端口
python3 logging_dashboard.py --port 8080
```

### 圖片上傳失敗
```bash
# 確保文件存在
ls -la image.jpg

# 使用絕對路徑
python3 intelligent_file_processor_cli.py upload /absolute/path/to/image.jpg
```

---

## 📝 日誌位置

```
logs/
├── cli.log           # CLI 應用日誌
├── dashboard.log     # 儀表板日誌
├── file_processor.log # 文件處理日誌
└── task_panel.log    # 任務面板日誌
```

查看日誌:
```bash
tail -f logs/dashboard.log
```

---

## 🔐 安全建議

1. **不要在公網暴露端口**
   ```bash
   # 使用本地訪問
   python3 logging_dashboard.py --host 127.0.0.1 --port 5000
   ```

2. **保護敏感文件**
   ```bash
   chmod 600 config/credentials.yaml
   ```

3. **定期檢查日誌**
   ```bash
   grep ERROR logs/*.log
   ```

---

## 📚 更多資訊

- 文件處理文檔: `intelligent_file_processor.py`
- 日誌系統: `LOGGING_DASHBOARD_GUIDE.md`
- 任務管理: `QUICKSTART_TASK_PANEL.md`
- 系統架構: `SYSTEM_OVERVIEW.md`

---

## ✨ 快速參考卡

### 一行啟動各應用

```bash
# CLI 文件上傳
python3 intelligent_file_processor_cli.py upload image.jpg --report

# Web 儀表板
python3 logging_dashboard.py

# 任務面板
python3 task_panel_optimized.py

# 演示系統
python3 demo_singularity_system.py
```

---

**最後更新**: 2026-02-20  
**所有應用狀態**: ✅ 已激活  
**推薦首選**: 文件處理 CLI (圖片上傳)
