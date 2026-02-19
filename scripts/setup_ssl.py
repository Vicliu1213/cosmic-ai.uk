#!/usr/bin/env python3
"""
SSL/TLS 證書生成工具
SSL/TLS Certificate Generator

為 Comic AI 專案生成自簽名憑證或使用 Let's Encrypt
Generates self-signed certificates or uses Let's Encrypt for Comic AI
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SSLManager:
    """SSL/TLS 憑證管理器"""
    
    def __init__(self, cert_dir: str = "ssl_certs"):
        """初始化 SSL 管理器
        
        Args:
            cert_dir: 憑證存儲目錄
        """
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(exist_ok=True)
        self.cert_file = self.cert_dir / "cert.pem"
        self.key_file = self.cert_dir / "key.pem"
        
    def generate_self_signed_cert(
        self,
        domain: str = "localhost",
        days: int = 365,
        force: bool = False
    ) -> bool:
        """生成自簽名憑證
        
        Generate self-signed certificate for development/testing
        
        Args:
            domain: 網域名稱 (e.g., localhost, example.com)
            days: 有效期天數
            force: 強制覆蓋現有憑證
            
        Returns:
            bool: 成功返回 True
        """
        # 檢查現有憑證
        if self.cert_file.exists() and self.key_file.exists() and not force:
            logger.info(f"✅ 憑證已存在於 {self.cert_dir}")
            logger.info(f"   证书: {self.cert_file}")
            logger.info(f"   私钥: {self.key_file}")
            return True
        
        logger.info(f"🔄 生成自簽名憑證...")
        logger.info(f"   域名: {domain}")
        logger.info(f"   有效期: {days} 天")
        
        try:
            # 使用 OpenSSL 生成自簽名憑證
            cmd = [
                "openssl", "req", "-x509", "-newkey", "rsa:2048",
                "-keyout", str(self.key_file),
                "-out", str(self.cert_file),
                "-days", str(days),
                "-nodes",
                "-subj", f"/CN={domain}/O=Comic AI/C=TW"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info(f"✅ 自簽名憑證生成成功!")
            logger.info(f"   证书: {self.cert_file}")
            logger.info(f"   私钥: {self.key_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 生成憑證失敗: {e}")
            logger.error(f"   確保已安裝 OpenSSL: apt-get install openssl")
            return False
        except FileNotFoundError:
            logger.error("❌ OpenSSL 未安裝。請執行:")
            logger.error("   Ubuntu/Debian: sudo apt-get install openssl")
            logger.error("   macOS: brew install openssl")
            logger.error("   Windows: 請訪問 https://www.openssl.org/")
            return False
    
    def get_cert_info(self) -> Optional[Dict[str, Any]]:
        """獲取憑證資訊"""
        if not self.cert_file.exists():
            logger.warning("❌ 憑證檔案不存在")
            return None
        
        try:
            result = subprocess.run(
                ["openssl", "x509", "-in", str(self.cert_file), "-noout", "-text"],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "cert_path": str(self.cert_file),
                "key_path": str(self.key_file),
                "details": result.stdout
            }
            
        except Exception as e:
            logger.error(f"❌ 無法讀取憑證: {e}")
            return None
    
    def verify_cert(self) -> bool:
        """驗證憑證有效性"""
        if not self.cert_file.exists() or not self.key_file.exists():
            logger.error("❌ 憑證或私鑰檔案不存在")
            return False
        
        try:
            # 驗證憑證格式
            subprocess.run(
                ["openssl", "x509", "-in", str(self.cert_file), "-noout"],
                check=True,
                capture_output=True
            )
            
            # 驗證私鑰格式
            subprocess.run(
                ["openssl", "rsa", "-in", str(self.key_file), "-noout"],
                check=True,
                capture_output=True
            )
            
            logger.info("✅ 憑證和私鑰驗證成功!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 憑證驗證失敗: {e}")
            return False


class FlaskSSLConfig:
    """Flask 應用 SSL 配置"""
    
    @staticmethod
    def get_ssl_context(cert_path: str, key_path: str) -> Dict[str, str]:
        """獲取 Flask SSL 上下文配置"""
        return {
            'ssl_context': 'adhoc' if cert_path and key_path else None,
            'ssl_cert': cert_path,
            'ssl_key': key_path
        }
    
    @staticmethod
    def generate_flask_config(
        cert_dir: str = "ssl_certs"
    ) -> str:
        """生成 Flask 配置程式碼"""
        cert_path = os.path.join(cert_dir, "cert.pem")
        key_path = os.path.join(cert_dir, "key.pem")
        
        config = f'''
# SSL/TLS Configuration for Flask
# 在 app.run() 或 create_app() 中使用

SSL_CONFIG = {{
    'ssl_context': ({
        'cert': '{cert_path}',
        'key': '{key_path}'
    }),
    'host': '0.0.0.0',
    'port': 8443,
    'debug': False
}}

# 在 app.py 中使用:
# if __name__ == '__main__':
#     app.run(**SSL_CONFIG)

# 或使用 Gunicorn:
# gunicorn --certfile={cert_path} --keyfile={key_path} --bind 0.0.0.0:8443 app:app
'''
        return config


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Comic AI SSL/TLS 憑證管理工具"
    )
    parser.add_argument(
        "command",
        choices=["generate", "verify", "info"],
        help="執行的命令"
    )
    parser.add_argument(
        "--domain",
        default="localhost",
        help="憑證域名 (default: localhost)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="憑證有效期天數 (default: 365)"
    )
    parser.add_argument(
        "--cert-dir",
        default="ssl_certs",
        help="憑證儲存目錄 (default: ssl_certs)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="強制覆蓋現有憑證"
    )
    
    args = parser.parse_args()
    
    manager = SSLManager(args.cert_dir)
    
    if args.command == "generate":
        success = manager.generate_self_signed_cert(
            domain=args.domain,
            days=args.days,
            force=args.force
        )
        
        if success:
            manager.verify_cert()
            info = manager.get_cert_info()
            if info:
                logger.info("\n📋 憑證詳細資訊:")
                logger.info(info["details"][:500])
        
        sys.exit(0 if success else 1)
    
    elif args.command == "verify":
        success = manager.verify_cert()
        sys.exit(0 if success else 1)
    
    elif args.command == "info":
        info = manager.get_cert_info()
        if info:
            logger.info("\n📋 憑證詳細資訊:")
            logger.info(info["details"])
        sys.exit(0 if info else 1)


if __name__ == "__main__":
    main()
