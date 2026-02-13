# Google Cloud Vertex AI 配置指南

## 🚀 快速設定

### 1. 取得 Google Cloud API 金鑰
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Vertex AI API
4. 建立服務帳戶金鑰

### 2. 配置檔案

#### 方法一：使用腳本配置
```bash
python scripts/setup_vertex_ai.py
```

#### 方法二：手動配置
編輯 `.env.vertex` 檔案，填入你的資訊：
```bash
# 替換為你的實際值
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-google-api-key
VERTEX_AI_API_KEY=your-vertex-ai-api-key
```

#### 方法三：更新認證檔案
編輯 `config/google-credentials.json`，填入你的服務帳戶資訊

### 3. VS Code 整合

配置已自動加入到 `.vscode/settings.json`，包含：
- Vertex AI 模型提供者設定
- API 端點配置  
- 環境變數設定

## 📁 檔案結構

```
comic_ai/
├── .env.vertex                    # Vertex AI 環境變數
├── .vscode/
│   └── settings.json              # VS Code 設定 (已更新)
├── config/
│   └── google-credentials.json   # Google 認證檔案
└── scripts/
    └── setup_vertex_ai.py        # 配置腳本
```

## 🎯 使用方式

### 在 VS Code 中
1. 重新載入 VS Code 視窗
2. 環境變數會自動載入到終端機
3. Copilot 將使用 Vertex AI 作為模型提供者

### 在 Python 程式碼中
```python
import os
from google.cloud import aiplatform

# 環境變數已自動設定
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
location = os.environ.get('GOOGLE_CLOUD_LOCATION')

# 初始化 Vertex AI
aiplatform.init(project=project_id, location=location)
```

## ✅ 驗證配置

執行配置腳本來驗證：
```bash
python scripts/setup_vertex_ai.py
```

## 🔧 故障排除

### 常見問題
1. **API 金鑰無效**：檢查金鑰是否正確且有權限
2. **專案 ID 錯誤**：確認專案 ID 名稱正確
3. **認證檔案路徑**：確保檔案存在且可讀取

### 除錯指令
```bash
# 檢查環境變數
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_API_KEY

# 測試 API 連接
curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
     "https://us-central1-aiplatform.googleapis.com/v1/projects/$GOOGLE_CLOUD_PROJECT/locations/us-central1/models"
```

## 📞 支援

如需協助，請查看：
- [Google Cloud Vertex AI 文件](https://cloud.google.com/vertex-ai/docs)
- [GitHub Copilot 文件](https://docs.github.com/en/copilot)

---

**注意**：請勿將 API 金鑰提交到版本控制系統。`.env.vertex` 已加入 `.gitignore`。