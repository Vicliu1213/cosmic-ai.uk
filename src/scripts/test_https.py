#!/usr/bin/env python3
"""
HTTPS 連接測試工具
Test HTTPS connection to Comic AI Dashboard

使用此腳本測試 SSL/TLS 連接是否正常
"""

import requests
import ssl
import urllib3
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# 禁用 SSL 警告（用於自簽名證書測試）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPSConnectionTester:
    """HTTPS 連接測試器"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8443,
        verify_ssl: bool = False,
        cert_path: Optional[str] = None
    ):
        """初始化測試器
        
        Args:
            host: 主機名
            port: 端口號
            verify_ssl: 是否驗證 SSL 憑證
            cert_path: CA 憑證路徑（可選）
        """
        self.host = host
        self.port = port
        self.url = f"https://{host}:{port}"
        self.verify_ssl = verify_ssl and cert_path is not None
        self.cert_path = cert_path
        
    def test_connection(self) -> bool:
        """測試基本連接"""
        logger.info(f"🔗 測試連接到 {self.url}")
        
        try:
            response = requests.get(
                f"{self.url}/health",
                verify=self.cert_path if self.verify_ssl else False,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ 連接成功! (HTTP {response.status_code})")
                logger.info(f"   回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
                return True
            else:
                logger.error(f"❌ 連接失敗! (HTTP {response.status_code})")
                return False
                
        except requests.exceptions.SSLError as e:
            logger.error(f"❌ SSL 錯誤: {e}")
            logger.info("   💡 提示: 如果使用自簽名證書，請使用 --no-verify-ssl")
            return False
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ 連接錯誤: {e}")
            logger.info(f"   💡 確保服務器在 {self.url} 上運行")
            return False
            
        except Exception as e:
            logger.error(f"❌ 未知錯誤: {e}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """測試 API 端點"""
        endpoints = [
            ("/health", "健康檢查"),
            ("/api/status", "API 狀態"),
        ]
        
        all_ok = True
        
        for endpoint, description in endpoints:
            logger.info(f"\n📝 測試 {description}: {endpoint}")
            
            try:
                response = requests.get(
                    f"{self.url}{endpoint}",
                    verify=self.cert_path if self.verify_ssl else False,
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info(f"   ✅ 成功")
                    logger.info(f"   回應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
                else:
                    logger.error(f"   ❌ 失敗 (HTTP {response.status_code})")
                    all_ok = False
                    
            except Exception as e:
                logger.error(f"   ❌ 錯誤: {e}")
                all_ok = False
        
        return all_ok
    
    def get_certificate_info(self) -> Optional[Dict[str, Any]]:
        """獲取遠程證書信息"""
        import socket
        
        logger.info(f"\n🔐 獲取遠程證書信息...")
        
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((self.host, self.port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)
                    
                    cert_info = ssock.getpeercert()
                    
                    logger.info(f"✅ 已獲取證書")
                    logger.info(f"   Subject: {dict(x[0] for x in cert_info['subject'])}")
                    logger.info(f"   Issuer: {dict(x[0] for x in cert_info['issuer'])}")
                    logger.info(f"   Version: {cert_info['version']}")
                    
                    if 'notAfter' in cert_info:
                        logger.info(f"   有效期至: {cert_info['notAfter']}")
                    
                    return cert_info
                    
        except Exception as e:
            logger.error(f"❌ 無法獲取證書信息: {e}")
            return None
    
    def run_all_tests(self) -> bool:
        """運行所有測試"""
        logger.info("=" * 60)
        logger.info("🧪 Comic AI HTTPS 連接測試")
        logger.info("=" * 60)
        
        # 獲取證書信息
        self.get_certificate_info()
        
        # 測試連接
        logger.info("\n" + "=" * 60)
        connection_ok = self.test_connection()
        
        # 測試 API 端點
        logger.info("\n" + "=" * 60)
        api_ok = self.test_api_endpoints()
        
        # 最終結果
        logger.info("\n" + "=" * 60)
        if connection_ok and api_ok:
            logger.info("✅ 所有測試通過!")
            return True
        else:
            logger.error("❌ 部分測試失敗")
            return False


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="測試 Comic AI HTTPS 連接"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="主機名 (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8443,
        help="端口號 (default: 8443)"
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        help="驗證 SSL 憑證"
    )
    parser.add_argument(
        "--cert",
        help="CA 憑證路徑"
    )
    parser.add_argument(
        "--no-verify-ssl",
        dest="verify_ssl",
        action="store_false",
        help="不驗證 SSL 憑證（用於自簽名證書）"
    )
    parser.set_defaults(verify_ssl=False)
    
    args = parser.parse_args()
    
    tester = HTTPSConnectionTester(
        host=args.host,
        port=args.port,
        verify_ssl=args.verify_ssl,
        cert_path=args.cert
    )
    
    success = tester.run_all_tests()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
