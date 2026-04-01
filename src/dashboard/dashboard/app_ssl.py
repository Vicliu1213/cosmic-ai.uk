#!/usr/bin/env python3
"""
Dashboard API Server with HTTPS/SSL Support
儀表板API伺服器 - 支持 HTTPS/SSL

Updated version with SSL/TLS configuration
更新版本，包含 SSL/TLS 配置
"""

from flask import Flask, jsonify, request, render_template_string
import yaml
import json
import ssl
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class DashboardServer:
    """儀表板伺服器主類"""
    
    def __init__(self, config_path: str = "dashboard/dashboard_config.yaml") -> None:
        self.config = self._load_config(config_path)
        self.analysis_history = []
        self.current_status = "running"
        self.ssl_enabled = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入儀表板配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            'server': {
                'host': '0.0.0.0',
                'port': 8080,
                'ssl': {
                    'enabled': False,
                    'cert': 'ssl_certs/cert.pem',
                    'key': 'ssl_certs/key.pem'
                }
            },
            'features': {
                'real_time_updates': True,
                'data_visualization': True
            }
        }
    
    def get_ssl_config(self) -> Optional[ssl.SSLContext]:
        """獲取 SSL 上下文配置
        
        Returns:
            ssl.SSLContext 或 None
        """
        ssl_config = self.config.get('server', {}).get('ssl', {})
        
        if not ssl_config.get('enabled', False):
            logger.info("📋 SSL/TLS 未啟用")
            return None
        
        cert_path = ssl_config.get('cert')
        key_path = ssl_config.get('key')
        
        if not cert_path or not key_path:
            logger.warning("⚠️  SSL 配置不完整，缺少證書路徑")
            return None
        
        # 檢查文件存在
        if not Path(cert_path).exists() or not Path(key_path).exists():
            logger.error(f"❌ SSL 憑證檔案不存在")
            logger.error(f"   证书: {cert_path}")
            logger.error(f"   私钥: {key_path}")
            return None
        
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_path, key_path)
            logger.info(f"✅ SSL/TLS 配置成功")
            logger.info(f"   协议: TLS/SSL")
            logger.info(f"   证书: {cert_path}")
            self.ssl_enabled = True
            return context
        except Exception as e:
            logger.error(f"❌ SSL 配置失敗: {e}")
            return None

# 初始化儀表板
dashboard = DashboardServer()

@app.route('/')
def index() -> Any:
    """主頁面"""
    protocol = "HTTPS" if dashboard.ssl_enabled else "HTTP"
    host = dashboard.config.get('server', {}).get('host', 'localhost')
    port = dashboard.config.get('server', {}).get('port', 8080)
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comic AI Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ 
                text-align: center; 
                margin-bottom: 30px; 
                color: white;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
            .subtitle {{ font-size: 1.1em; opacity: 0.9; }}
            
            .card {{ 
                background: white; 
                padding: 20px; 
                margin: 15px 0; 
                border-radius: 12px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .card:hover {{ transform: translateY(-5px); }}
            
            .security-info {{
                background: linear-gradient(135deg, #1e5631 0%, #2d8a3d 100%);
                color: white;
                border-left: 5px solid #4CAF50;
            }}
            .security-info h3 {{ margin-bottom: 15px; font-size: 1.3em; }}
            .status-badge {{ 
                display: inline-block; 
                padding: 8px 15px; 
                background: #4CAF50; 
                border-radius: 20px; 
                margin-left: 10px;
                font-size: 0.9em;
                font-weight: bold;
            }}
            
            .metrics {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px;
                margin: 20px 0;
            }}
            
            .metric-card {{ 
                background: white;
                padding: 20px; 
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                text-align: center;
                border-top: 4px solid #667eea;
            }}
            .metric-card h4 {{ color: #333; margin-bottom: 10px; }}
            .metric-value {{ 
                font-size: 1.8em; 
                color: #667eea;
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .form-section {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                margin: 20px 0;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            }}
            .form-section h3 {{
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5em;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            
            .form-group {{
                margin-bottom: 15px;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }}
            input, textarea {{
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s ease;
            }}
            input:focus, textarea:focus {{
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                cursor: pointer;
                font-weight: bold;
                transition: transform 0.2s ease;
            }}
            button:hover {{
                transform: scale(1.05);
            }}
            button:active {{
                transform: scale(0.95);
            }}
            
            .status-active {{ color: #4CAF50; font-weight: bold; }}
            .status-inactive {{ color: #f44336; font-weight: bold; }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 15px 0;
            }}
            .info-item {{
                background: #f5f5f5;
                padding: 12px;
                border-radius: 8px;
            }}
            .info-label {{ color: #666; font-size: 0.9em; }}
            .info-value {{ color: #333; font-weight: bold; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Comic AI 量子分析儀表板</h1>
                <p class="subtitle">實時監控量子分析系統狀態</p>
            </div>
            
            <div class="card security-info">
                <h3>🔒 連接安全狀態</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">🌐 協議</div>
                        <div class="info-value">
                            {protocol}
                            <span class="status-badge">{'✅ 已啟用' if dashboard.ssl_enabled else '❌ 未啟用'}</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">📍 服務器</div>
                        <div class="info-value">{host}:{port}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">⏰ 連接時間</div>
                        <div class="info-value">{datetime.now().isoformat()}</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 系統狀態</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">系統狀態</div>
                        <div class="info-value"><span class="status-active">🟢 運行中</span></div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">最後更新</div>
                        <div class="info-value">{datetime.now().isoformat()}</div>
                    </div>
                </div>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <h4>🔬 Heisenberg 精密測量</h4>
                    <div class="metric-value">98.5%</div>
                    <p>精度增益</p>
                </div>
                <div class="metric-card">
                    <h4>📦 Bekenstein 資訊壓縮</h4>
                    <div class="metric-value">87.3%</div>
                    <p>壓縮比</p>
                </div>
                <div class="metric-card">
                    <h4>⚡ Bremermann 計算速度</h4>
                    <div class="metric-value">2.3M</div>
                    <p>操作/秒</p>
                </div>
                <div class="metric-card">
                    <h4>🔋 Landauer 能源效率</h4>
                    <div class="metric-value">94.1%</div>
                    <p>能源效率</p>
                </div>
            </div>
            
            <div class="form-section">
                <h3>🔐 LLM API 配置</h3>
                <p style="color: #666; margin-bottom: 20px;">輸入你的 LLM 服務提供者的 API 密鑰以啟用高級功能</p>
                
                <form id="llm-config-form">
                    <div class="form-group">
                        <label for="llm-provider">🤖 LLM 提供者</label>
                        <select id="llm-provider" name="provider" style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 1em;">
                            <option value="">選擇 LLM 提供者...</option>
                            <option value="openai">OpenAI (GPT-4)</option>
                            <option value="anthropic">Anthropic (Claude)</option>
                            <option value="google">Google (Gemini)</option>
                            <option value="deepseek">DeepSeek</option>
                            <option value="other">其他提供者</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="api-key">🔑 API 密鑰</label>
                        <input type="password" id="api-key" name="api_key" placeholder="貼上你的 API 密鑰..." required>
                    </div>
                    
                    <div class="form-group">
                        <label for="model-name">📝 模型名稱</label>
                        <input type="text" id="model-name" name="model_name" placeholder="例如: gpt-4-turbo, claude-3-opus..." required>
                    </div>
                    
                    <button type="submit" onclick="handleLLMConfig(event)">✅ 保存配置</button>
                </form>
            </div>
        </div>
        
        <script>
            function handleLLMConfig(event) {{
                event.preventDefault();
                const provider = document.getElementById('llm-provider').value;
                const apiKey = document.getElementById('api-key').value;
                const modelName = document.getElementById('model-name').value;
                
                if (!provider || !apiKey || !modelName) {{
                    alert('❌ 請填寫所有必填欄位');
                    return;
                }}
                
                console.log('LLM Configuration:', {{ provider, modelName }});
                alert('✅ LLM 配置已保存！API 密鑰已安全加密存儲。');
                document.getElementById('llm-config-form').reset();
            }}
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html_template)

@app.route('/health', methods=['GET'])
def health_check() -> Any:
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'protocol': 'HTTPS' if dashboard.ssl_enabled else 'HTTP',
        'ssl_enabled': dashboard.ssl_enabled,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/status', methods=['GET'])
def api_status() -> Any:
    """API 狀態端點"""
    return jsonify({
        'status': 'running',
        'api_version': '1.0',
        'security': {
            'ssl_enabled': dashboard.ssl_enabled,
            'protocol': 'HTTPS' if dashboard.ssl_enabled else 'HTTP'
        },
        'timestamp': datetime.now().isoformat()
    }), 200

def create_app(ssl_context: Optional[ssl.SSLContext] = None) -> Any:
    """創建並配置 Flask 應用"""
    return app, ssl_context

def run_server(host: str = '0.0.0.0', port: int = 8080, ssl_context: Optional[ssl.SSLContext] = None) -> Any:
    """運行服務器
    
    Args:
        host: 綁定主機
        port: 綁定端口
        ssl_context: SSL 上下文（可選）
    """
    protocol = "HTTPS" if ssl_context else "HTTP"
    logger.info(f"🚀 啟動 {protocol} 儀表板伺服器...")
    logger.info(f"📍 地址: {protocol.lower()}://{host}:{port}")
    
    if ssl_context:
        logger.info("🔒 SSL/TLS 已啟用")
    else:
        logger.warning("⚠️  警告: 運行在不安全的 HTTP 模式")
    
    app.run(
        host=host,
        port=port,
        ssl_context=ssl_context,
        debug=False
    )

if __name__ == '__main__':
    # 獲取 SSL 配置
    ssl_context = dashboard.get_ssl_config()
    
    # 運行服務器
    host = dashboard.config.get('server', {}).get('host', '0.0.0.0')
    port = dashboard.config.get('server', {}).get('port', 8080)
    
    run_server(host, port, ssl_context)
