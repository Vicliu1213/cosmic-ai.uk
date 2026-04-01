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

### 高級故障排除

#### Python 驗證腳本

```python
# verify_vertex_ai.py - 完整的 Vertex AI 配置驗證
import os
import sys
import json
from pathlib import Path

def verify_vertex_ai_setup():
    """驗證 Vertex AI 完整配置"""
    
    print("🔍 驗證 Vertex AI 配置...\n")
    
    checks = {
        "環境變數": verify_env_vars,
        "認證檔案": verify_credentials_file,
        "Google Cloud CLI": verify_gcloud_cli,
        "Python 環境": verify_python_env,
        "API 權限": verify_api_permissions,
    }
    
    results = {}
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
            status = "✓" if results[check_name] else "✗"
            print(f"{status} {check_name}: {'通過' if results[check_name] else '失敗'}")
        except Exception as e:
            results[check_name] = False
            print(f"✗ {check_name}: 錯誤 - {e}")
    
    print("\n" + "="*50)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"結果: {passed}/{total} 檢查通過")
    
    return all(results.values())

def verify_env_vars():
    """檢查環境變數"""
    required = ["GOOGLE_CLOUD_PROJECT", "GOOGLE_API_KEY"]
    for var in required:
        if not os.getenv(var):
            print(f"  缺少環境變數: {var}")
            return False
    return True

def verify_credentials_file():
    """檢查認證檔案"""
    cred_path = Path("config/google-credentials.json")
    if not cred_path.exists():
        print(f"  認證檔案不存在: {cred_path}")
        return False
    
    try:
        with open(cred_path) as f:
            json.load(f)
        return True
    except json.JSONDecodeError:
        print(f"  認證檔案 JSON 格式無效")
        return False

def verify_gcloud_cli():
    """檢查 Google Cloud CLI"""
    import subprocess
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        print("  gcloud CLI 未安裝")
        return False

def verify_python_env():
    """檢查 Python 依賴"""
    try:
        import google.cloud.aiplatform
        return True
    except ImportError:
        print("  google-cloud-aiplatform 未安裝")
        return False

def verify_api_permissions():
    """檢查 API 權限"""
    try:
        from google.cloud import aiplatform
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        # 嘗試初始化 (不實際調用 API)
        aiplatform.init(project=project, location=location)
        return True
    except Exception as e:
        print(f"  API 初始化失敗: {e}")
        return False

if __name__ == "__main__":
    success = verify_vertex_ai_setup()
    sys.exit(0 if success else 1)
```

**運行驗證**:
```bash
python verify_vertex_ai.py
```

#### 配置修復步驟

如果驗證失敗，按照以下步驟修復：

```bash
# 1. 重新配置環境變數
source .env.vertex

# 2. 驗證 gcloud 認證
gcloud auth login
gcloud config set project $GOOGLE_CLOUD_PROJECT

# 3. 重新安裝依賴
pip install --upgrade google-cloud-aiplatform

# 4. 驗證 API 啟用
gcloud services enable aiplatform.googleapis.com

# 5. 測試連接
python -c "
from google.cloud import aiplatform
import os
aiplatform.init(
    project=os.getenv('GOOGLE_CLOUD_PROJECT'),
    location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
)
print('✓ Vertex AI 已成功連接')
"
```

#### 常見錯誤和解決方案

| 錯誤 | 原因 | 解決方案 |
|------|------|---------|
| `PERMISSION_DENIED` | 無 API 權限 | 啟用 Vertex AI API、檢查 IAM 角色 |
| `NOT_FOUND` | 專案 ID 錯誤 | 驗證 GOOGLE_CLOUD_PROJECT |
| `UNAUTHENTICATED` | 認證失敗 | 重新運行 gcloud auth login |
| `ImportError: google.cloud` | 缺少依賴 | 運行 pip install google-cloud-aiplatform |

## 📞 支援

如需協助，請查看：
- [Google Cloud Vertex AI 文件](https://cloud.google.com/vertex-ai/docs)
- [GitHub Copilot 文件](https://docs.github.com/en/copilot)
- [Google Cloud Python 客戶端](https://cloud.google.com/python/docs/reference)

---

**注意**：請勿將 API 金鑰提交到版本控制系統。`.env.vertex` 已加入 `.gitignore`。

## 🚀 下一步

1. **驗證配置** - 運行 `python verify_vertex_ai.py`
2. **測試整合** - 在 VS Code 中使用 Vertex AI 模型
3. **監控使用** - 在 Google Cloud Console 中查看使用情況
4. **優化成本** - 根據使用情況調整配置