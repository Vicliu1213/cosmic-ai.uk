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
    
    def __init__(self, config_path: str = "dashboard/dashboard_config.yaml"):
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
def index():
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
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .status-card {{ background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 8px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .metric-card {{ background: #3a3a3a; padding: 15px; border-radius: 5px; text-align: center; }}
            h1 {{ color: #4CAF50; }}
            .status-active {{ color: #4CAF50; }}
            .status-inactive {{ color: #f44336; }}
            .ssl-badge {{ 
                display: inline-block; 
                padding: 5px 10px; 
                background: #4CAF50; 
                border-radius: 4px; 
                margin-left: 10px;
                font-size: 12px;
            }}
            .security-info {{
                background: #1e5631;
                border-left: 4px solid #4CAF50;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Comic AI 量子分析儀表板</h1>
                <p>實時監控量子分析系統狀態</p>
            </div>
            
            <div class="security-info">
                <h3>🔒 連接安全狀態</h3>
                <p>
                    🌐 協議: <strong>{protocol}</strong>
                    <span class="ssl-badge">{'✅ 已啟用' if dashboard.ssl_enabled else '❌ 未啟用'}</span>
                </p>
                <p>📍 服務器: {host}:{port}</p>
                <p>⏰ 連接時間: <span id="connection-time">{{{{ current_time }}}}</span></p>
            </div>
            
            <div class="status-card">
                <h3>系統狀態</h3>
                <p>狀態: <span class="status-active">運行中</span></p>
                <p>最後更新: <span id="last-update">{{{{ current_time }}}}</span></p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <h4>Heisenberg 精密測量</h4>
                    <p>精度增益: <span id="precision-gain">-</span></p>
                </div>
                <div class="metric-card">
                    <h4>Bekenstein 資訊壓縮</h4>
                    <p>壓縮比: <span id="compression-ratio">-</span></p>
                </div>
                <div class="metric-card">
                    <h4>Bremermann 計算速度</h4>
                    <p>處理速度: <span id="processing-speed">-</span></p>
                </div>
                <div class="metric-card">
                    <h4>Landauer 能源效率</h4>
                    <p>能源效率: <span id="energy-efficiency">-</span></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, current_time=datetime.now().isoformat())


@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'protocol': 'HTTPS' if dashboard.ssl_enabled else 'HTTP',
        'ssl_enabled': dashboard.ssl_enabled,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/status', methods=['GET'])
def api_status():
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


def create_app(ssl_context: Optional[ssl.SSLContext] = None):
    """創建並配置 Flask 應用"""
    return app, ssl_context


def run_server(host: str = '0.0.0.0', port: int = 8080, ssl_context: Optional[ssl.SSLContext] = None):
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
