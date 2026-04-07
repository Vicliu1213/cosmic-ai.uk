# 智能文件分析技能 (Intelligent File Analysis Skill)

## 概述

這是一個 OpenCode 智能技能，提供強大的文件上傳、自動分類和深度分析能力。支持圖片、文字、代碼、壓縮檔等 50+ 文件類型，融合前沿技術（Claude Vision、NLP）與經典算法（Tesseract OCR、TF-IDF）。

## 功能特性

### 核心能力
- 🖼️ **智能圖片識別** - 使用 Claude Vision + Tesseract OCR 雙引擎
- 📝 **文本深度分析** - NLP 關鍵字提取、格式自動檢測
- 💻 **代碼質量評估** - AST 解析、複雜度分析、最佳實踐檢查
- 📦 **壓縮檔自動分析** - 支持 ZIP、TAR、GZ、BZ2、RAR、7Z
- 🔄 **批量處理** - 支持整個目錄的自動分析
- 📊 **多格式輸出** - 報告、JSON、摘要、CSV

### 處理策略
- **Advanced**: 優先使用前沿 AI 技術
- **Classic**: 使用經典算法確保穩定性
- **Hybrid**: 推薦模式，智能降級

## 安裝

### 方式 1: 自動安裝（推薦）
```bash
opencode install skill intelligent-file-analysis
```

### 方式 2: 手動安裝
```bash
# 複製技能到 OpenCode 技能目錄
cp -r ./intelligent-file-analysis ~/.config/opencode/skills/

# 更新 OpenCode 配置
opencode config skills.enable intelligent-file-analysis
```

## 使用方法

### 基本命令

#### 1. 分析單個文件
```bash
# 生成詳細報告
/analyze file.py --report

# JSON 格式輸出
/analyze image.jpg --json

# 使用經典算法
/analyze document.pdf --strategy classic
```

#### 2. 批量分析目錄
```bash
# 分析整個項目目錄
/batch ./src --recursive

# 只分析特定類型
/batch ./docs --type text

# 生成摘要統計
/batch ./project --summary
```

#### 3. 快速掃描
```bash
# 快速掃描，返回關鍵信息
/scan file.txt

# 掃描並自動修復建議
/scan-fix project/
```

#### 4. 文件對比
```bash
# 對比兩個文件
/compare file1.py file2.py

# 對比目錄
/compare-dir ./v1/ ./v2/
```

### 高級選項

```bash
# 設置分析深度
/analyze file.py --depth deep|medium|shallow

# 設置輸出格式
/analyze file.py --format report|json|csv|markdown

# 設置置信度閾值
/analyze file.py --confidence 0.8

# 設置超時時間
/analyze large_file.zip --timeout 60s

# 啟用詳細日誌
/analyze file.py --verbose --debug
```

## 配置

### 全局配置 (`~/.config/opencode/config.yaml`)

```yaml
skills:
  intelligent-file-analysis:
    enabled: true
    strategy: hybrid              # 處理策略
    default_format: report        # 默認輸出格式
    timeout: 30s                  # 超時設置
    enable_caching: true          # 啟用快取
    cache_ttl: 3600              # 快取過期時間 (秒)
    
    # 文件類型配置
    file_types:
      image:
        enabled: true
        ocr: true
        vision_api: true
      code:
        enabled: true
        analysis_level: deep
        check_style: true
      archive:
        enabled: true
        extract_limit: 100MB
```

### 技能特定配置 (`~/.config/opencode/skills/intelligent-file-analysis/config.json`)

```json
{
  "version": "1.0.0",
  "name": "Intelligent File Analysis",
  "description": "智能文件分析技能",
  
  "processors": {
    "image": {
      "enabled": true,
      "methods": ["claude_vision", "tesseract_ocr"],
      "fallback": "classic"
    },
    "text": {
      "enabled": true,
      "methods": ["nlp", "tfidf"],
      "keywords_top_n": 20
    },
    "code": {
      "enabled": true,
      "languages": ["python", "javascript", "java", "cpp"],
      "check_quality": true
    },
    "archive": {
      "enabled": true,
      "formats": ["zip", "tar", "gz", "bz2"],
      "max_files": 1000
    }
  },
  
  "output": {
    "formats": ["report", "json", "csv", "markdown"],
    "include_preview": true,
    "preview_length": 500,
    "include_recommendations": true
  }
}
```

## API 文檔

### 代理方法

#### `analyze(filepath, format='report', strategy='hybrid')`

分析單個文件。

**參數:**
- `filepath` (str): 文件路徑
- `format` (str): 輸出格式 (report|json|csv)
- `strategy` (str): 處理策略 (advanced|classic|hybrid)

**返回:**
```json
{
  "status": "success",
  "file": {
    "name": "example.py",
    "type": "code",
    "size_kb": 5.2,
    "hash": "abc123def456"
  },
  "analysis": {
    "summary": "Python 代碼檔，245 行代碼",
    "findings": ["使用 type hints", "缺少 docstrings"],
    "confidence": 0.92
  },
  "recommendations": [
    "添加函數文檔",
    "考慮單位測試"
  ]
}
```

#### `batch(directory, recursive=true, filter_type=null)`

批量分析目錄。

**參數:**
- `directory` (str): 目錄路徑
- `recursive` (bool): 遞歸分析子目錄
- `filter_type` (str): 篩選文件類型

**返回:**
```json
{
  "status": "success",
  "stats": {
    "total": 45,
    "succeeded": 44,
    "failed": 1,
    "by_type": {
      "code": 25,
      "text": 15,
      "image": 4
    }
  },
  "results": [...]
}
```

#### `get_intelligence(filepath, include_raw=false)`

獲取文件的完整智能分析。

**參數:**
- `filepath` (str): 文件路徑
- `include_raw` (bool): 包含原始分析數據

**返回:** 完整的分析結果和建議

## 集成示例

### 在 Comic AI 中使用

```python
from opencode import get_skill

# 獲取技能實例
file_analyzer = get_skill('intelligent-file-analysis')

# 分析文件
result = await file_analyzer.analyze('project/main.py')

# 批量分析
batch_result = await file_analyzer.batch('./src')

# 生成報告
report = file_analyzer.generate_report(result)
```

### 在 OpenCode 代理中使用

```python
@agent.command('/analyze')
async def analyze_command(ctx, filepath: str, format: str = 'report'):
    """分析文件命令"""
    skill = ctx.get_skill('intelligent-file-analysis')
    result = await skill.analyze(filepath, format=format)
    return ctx.format_output(result)
```

### 在工作流中使用

```yaml
# opencode-workflow.yaml
workflow:
  name: "代碼質量檢查"
  triggers:
    - file_changed
  steps:
    - name: analyze
      skill: intelligent-file-analysis
      action: analyze
      params:
        format: json
        strategy: hybrid
    
    - name: report
      action: format-report
      inputs: analyze.result
```

## 快速開始

### 1. 安裝技能
```bash
opencode install skill intelligent-file-analysis
```

### 2. 驗證安裝
```bash
opencode skill list | grep intelligent-file-analysis
```

### 3. 運行示例
```bash
# 分析一個 Python 檔案
/analyze example.py --report

# 批量分析目錄
/batch ./test_files --summary

# JSON 輸出
/analyze data.json --json
```

### 4. 查看結果
結果將在 OpenCode 界面中以友善的格式顯示，包括：
- 文件信息卡
- 分析摘要
- 關鍵發現列表
- 專業建議
- 性能指標

## 故障排除

### 常見問題

**Q: 分析速度太慢？**
- 嘗試使用 `--strategy classic` 禁用 Vision API
- 減少分析深度: `--depth shallow`
- 檢查系統資源使用情況

**Q: 無法識別某種文件類型？**
- 檢查 MIME 類型: `file -i filename`
- 確保文件擴展名正確
- 提交支持請求

**Q: 內存不足？**
- 減少批處理數量
- 清理緩存: `opencode skill cache clear intelligent-file-analysis`
- 分次處理

### 日誌和調試

```bash
# 啟用調試模式
opencode config skills.intelligent-file-analysis.debug true

# 查看技能日誌
opencode logs skill intelligent-file-analysis

# 清除快取
opencode skill cache clear intelligent-file-analysis
```

## 性能指標

### 典型處理時間

| 檔案類型 | 大小 | 處理時間 |
|---------|------|---------|
| Python 代碼 | 10 KB | 50 ms |
| Markdown | 50 KB | 100 ms |
| JSON | 100 KB | 150 ms |
| ZIP 檔案 | 1 MB | 200 ms |
| 圖片 | 2 MB | 500 ms |

### 系統需求

- Python 3.10+
- 最小 4GB 記憶體
- 500 MB 硬碟空間

## 更新和維護

### 檢查更新
```bash
opencode skill update check intelligent-file-analysis
```

### 更新技能
```bash
opencode skill update intelligent-file-analysis
```

### 查看版本
```bash
opencode skill info intelligent-file-analysis
```

## 貢獻

歡迎貢獻改進！提交問題或拉取請求到 OpenCode 技能倉庫。

## 許可證

MIT License - 詳見 LICENSE 文件

## 支持

- 📖 [完整文檔](./README.md)
- 🐛 [報告問題](./ISSUES.md)
- 💬 [社區論壇](https://community.opencode.ai)
- 📧 [郵件支持](mailto:support@opencode.ai)

---

**最後更新**: 2026-02-15  
**版本**: 1.0.0  
**狀態**: ✅ 生產就緒
