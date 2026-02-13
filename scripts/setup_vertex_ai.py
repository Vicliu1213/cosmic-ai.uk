#!/usr/bin/env python3
"""
Google Cloud Vertex AI 配置腳本
用於設定和管理 Vertex AI 的 API 連接
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class VertexAIConfig:
    def __init__(self, workspace_root: str | None = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path(__file__).parent.parent
        self.config_dir = self.workspace_root / "config"
        self.env_file = self.workspace_root / ".env.vertex"
        self.credentials_file = self.config_dir / "google-credentials.json"
        
    def load_config(self) -> Dict[str, Any]:
        """載入 Vertex AI 配置"""
        config = {}
        
        # 載入環境變數
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key] = value
                        
        return config
    
    def setup_environment(self, api_key: str, project_id: str, 
                         location: str = "us-central1",
                         credentials_path: str | None = None):
        """設定 Vertex AI 環境變數"""
        
        # 更新環境變數檔案
        env_content = f"""# Google Cloud Vertex AI 配置
GOOGLE_CLOUD_PROJECT={project_id}
GOOGLE_CLOUD_LOCATION={location}
GOOGLE_CLOUD_VERTEX_AI_ENDPOINT=https://{location}-aiplatform.googleapis.com
GOOGLE_APPLICATION_CREDENTIALS={credentials_path or str(self.credentials_file)}

# Vertex AI 模型設定
VERTEX_AI_MODEL=gemini-1.5-pro
VERTEX_AI_TEMPERATURE=0.7
VERTEX_AI_MAX_TOKENS=2048

# API 金鑰
GOOGLE_API_KEY={api_key}
VERTEX_AI_API_KEY={api_key}
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
            
        # 設定環境變數
        os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
        os.environ['GOOGLE_API_KEY'] = api_key
        os.environ['VERTEX_AI_API_KEY'] = api_key
        credentials_file = credentials_path or str(self.credentials_file)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        
        print(f"✅ Vertex AI 配置已設定完成")
        print(f"📁 專案ID: {project_id}")
        print(f"🌍 位置: {location}")
        print(f"🔑 API金鑰: {'*' * (len(api_key) - 4)}{api_key[-4:]}")
        
    def validate_config(self) -> bool:
        """驗證配置是否正確"""
        config = self.load_config()
        
        required_keys = [
            'GOOGLE_CLOUD_PROJECT',
            'GOOGLE_API_KEY', 
            'VERTEX_AI_API_KEY',
            'GOOGLE_APPLICATION_CREDENTIALS'
        ]
        
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"❌ 缺少必要的配置: {', '.join(missing_keys)}")
            return False
            
        # 檢查認證檔案是否存在
        if not Path(config['GOOGLE_APPLICATION_CREDENTIALS']).exists():
            print(f"❌ 認證檔案不存在: {config['GOOGLE_APPLICATION_CREDENTIALS']}")
            return False
            
        print("✅ Vertex AI 配置驗證通過")
        return True
        
    def get_vscode_settings(self) -> Dict[str, Any]:
        """取得 VS Code 設定"""
        return {
            "terminal.integrated.env.linux": {
                "PYTHONPATH": str(self.workspace_root),
                "GOOGLE_CLOUD_PROJECT": "${env:GOOGLE_CLOUD_PROJECT}",
                "GOOGLE_APPLICATION_CREDENTIALS": "${env:GOOGLE_APPLICATION_CREDENTIALS}",
                "VERTEX_AI_API_KEY": "${env:VERTEX_AI_API_KEY}"
            },
            "copilot.chat.model.provider": "vertex-ai",
            "copilot.chat.model.endpoint": "https://${env:GOOGLE_CLOUD_LOCATION}-aiplatform.googleapis.com",
            "copilot.chat.model.name": "gemini-1.5-pro",
            "copilot.chat.apiKey": "${env:VERTEX_AI_API_KEY}"
        }

def main():
    """主函數"""
    print("🚀 Google Cloud Vertex AI 配置工具")
    print("=" * 50)
    
    config = VertexAIConfig()
    
    # 檢查現有配置
    if config.validate_config():
        print("✅ 現有配置有效")
    else:
        print("⚠️ 需要重新配置")
        
    # 顯示使用說明
    print("\n📋 使用說明:")
    print("1. 請先在 Google Cloud Console 建立 Vertex API 金鑰")
    print("2. 取得您的專案 ID 和認證檔案")
    print("3. 執行: python scripts/setup_vertex_ai.py")
    print("4. 或手動編輯 .env.vertex 檔案")
    
    print(f"\n📁 配置檔案位置:")
    print(f"   環境變數: {config.env_file}")
    print(f"   認證檔案: {config.credentials_file}")

if __name__ == "__main__":
    main()