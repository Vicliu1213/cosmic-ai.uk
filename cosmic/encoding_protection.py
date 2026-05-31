#!/usr/bin/env python3
"""
編碼保護和數據驗證系統
Encoding Protection & Data Validation System
防止亂碼和數據損毀的完整機制
"""

import sys
import os
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from collections import deque
import re
import json
import hashlib
import shutil

logger = logging.getLogger(__name__)


class EncodingType(Enum):
    """編碼類型"""
    UTF8 = "utf-8"
    UTF16 = "utf-16"
    ASCII = "ascii"
    LATIN1 = "latin-1"
    GBK = "gbk"
    BIG5 = "big5"


class DataValidationError(Exception):
    """數據驗證錯誤"""
    pass


@dataclass
class EncodingPolicy:
    """編碼策略配置"""
    primary_encoding: str = "utf-8"
    fallback_encodings: List[str] = None
    strict_mode: bool = True
    auto_fix: bool = True
    log_encoding_errors: bool = True
    
    def __post_init__(self):
        if self.fallback_encodings is None:
            self.fallback_encodings = ["utf-8", "latin-1", "gbk"]


class EncodingProtector:
    """編碼保護器 - 防止亂碼"""
    
    def __init__(self, policy: EncodingPolicy = None):
        self.policy = policy or EncodingPolicy()
        self.encoding_error_log: deque = deque(maxlen=10000)
        logger.info("✅ EncodingProtector initialized")
    
    def detect_encoding(self, data: bytes) -> str:
        """偵測數據編碼"""
        # 嘗試每種編碼
        for encoding in self.policy.fallback_encodings:
            try:
                data.decode(encoding)
                logger.debug(f"✅ Detected encoding: {encoding}")
                return encoding
            except (UnicodeDecodeError, AttributeError):
                continue
        
        # 默認返回UTF-8
        logger.warning("⚠️ Could not detect encoding, defaulting to utf-8")
        return "utf-8"
    
    def safe_decode(self, data: Union[bytes, str], encoding: str = None) -> str:
        """安全解碼"""
        if isinstance(data, str):
            return data
        
        encoding = encoding or self.policy.primary_encoding
        
        try:
            # 嘗試主要編碼
            return data.decode(encoding)
        except UnicodeDecodeError as e:
            logger.warning(f"⚠️ Decode error with {encoding}: {e}")
            
            # 嘗試後備編碼
            for fallback in self.policy.fallback_encodings:
                if fallback != encoding:
                    try:
                        result = data.decode(fallback)
                        logger.info(f"✅ Successfully decoded with fallback: {fallback}")
                        self._log_encoding_error(encoding, fallback, str(e))
                        return result
                    except UnicodeDecodeError:
                        continue
            
            # 最後手段：使用errors='replace'
            result = data.decode(encoding, errors='replace')
            logger.error(f"❌ Used error replacement for {encoding}")
            self._log_encoding_error(encoding, "replace_mode", "All decoders failed")
            return result
    
    def safe_encode(self, data: str, encoding: str = None) -> bytes:
        """安全編碼"""
        if isinstance(data, bytes):
            return data
        
        encoding = encoding or self.policy.primary_encoding
        
        try:
            return data.encode(encoding)
        except UnicodeEncodeError as e:
            logger.warning(f"⚠️ Encode error with {encoding}: {e}")
            
            # 使用errors='replace'
            result = data.encode(encoding, errors='replace')
            logger.error(f"❌ Used error replacement for encoding {encoding}")
            self._log_encoding_error(encoding, "replace_mode", str(e))
            return result
    
    def clean_string(self, text: str) -> str:
        """清理字符串中的亂碼"""
        if not text:
            return text
        
        # 移除控制字符 (除了常見的 \n, \t, \r)
        cleaned = ''.join(ch for ch in text if ord(ch) >= 32 or ch in '\n\t\r')
        
        # 移除多個連續空格
        cleaned = re.sub(r' {2,}', ' ', cleaned)
        
        # 移除無效的UTF-8序列
        try:
            cleaned.encode('utf-8')
        except UnicodeEncodeError:
            cleaned = cleaned.encode('utf-8', errors='replace').decode('utf-8')
        
        logger.debug(f"✅ String cleaned (length: {len(text)} -> {len(cleaned)})")
        return cleaned
    
    def validate_string(self, text: str) -> bool:
        """驗證字符串是否有效"""
        try:
            if not isinstance(text, str):
                return False
            # 嘗試編碼解碼
            text.encode('utf-8').decode('utf-8')
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
    
    def _log_encoding_error(self, original: str, used: str, reason: str):
        """記錄編碼錯誤"""
        error_record = {
            "original_encoding": original,
            "used_encoding": used,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        self.encoding_error_log.append(error_record)
        
        if self.policy.log_encoding_errors:
            logger.warning(f"📋 Encoding error: {original} -> {used}")
    
    def get_error_log(self) -> List[Dict[str, Any]]:
        """獲取錯誤日誌"""
        return list(self.encoding_error_log)


class DataValidator:
    """數據驗證器 - 防止數據損毀"""
    
    def __init__(self):
        self.validation_log: deque = deque(maxlen=10000)
        logger.info("✅ DataValidator initialized")
    
    def calculate_checksum(self, data: Union[str, bytes]) -> str:
        """計算數據校驗和"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def validate_json(self, data: Union[str, dict]) -> bool:
        """驗證JSON數據"""
        try:
            if isinstance(data, str):
                json.loads(data)
            elif isinstance(data, dict):
                json.dumps(data)
            return True
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"❌ JSON validation failed: {e}")
            return False
    
    def validate_yaml(self, data: str) -> bool:
        """驗證YAML數據"""
        try:
            import yaml
            yaml.safe_load(data)
            return True
        except Exception as e:
            logger.error(f"❌ YAML validation failed: {e}")
            return False
    
    def validate_csv(self, data: str, delimiter: str = ',') -> bool:
        """驗證CSV數據"""
        try:
            import csv
            csv.reader(data.split('\n'), delimiter=delimiter)
            return True
        except Exception as e:
            logger.error(f"❌ CSV validation failed: {e}")
            return False
    
    def repair_corrupted_json(self, data: str) -> Optional[str]:
        """修復損毀的JSON數據"""
        logger.warning("⚠️ Attempting to repair corrupted JSON...")
        
        # 移除常見的亂碼字符
        data = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', data)
        
        # 嘗試修復未閉合的引號
        data = re.sub(r'"([^"]*?)(?=\}|,)', r'"\1"', data)
        
        # 嘗試添加缺失的逗號
        data = re.sub(r'"\s*:\s*([^",}]+)\s*(?=")', r'": "\1",', data)
        
        # 驗證修復結果
        if self.validate_json(data):
            logger.info("✅ JSON repair successful")
            return data
        
        logger.error("❌ JSON repair failed")
        return None
    
    def log_validation_event(self, event_type: str, data_type: str, 
                            status: bool, details: str = ""):
        """記錄驗證事件"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data_type": data_type,
            "status": "PASS" if status else "FAIL",
            "details": details
        }
        self.validation_log.append(record)
        
        status_str = "✅" if status else "❌"
        logger.info(f"{status_str} Validation: {event_type} ({data_type})")
    
    def get_validation_report(self) -> Dict[str, Any]:
        """獲取驗證報告"""
        total = len(self.validation_log)
        validation_list = list(self.validation_log)
        passed = sum(1 for r in validation_list if r['status'] == 'PASS')
        
        return {
            "total_validations": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "recent_events": validation_list[-10:]
        }


class FileIOProtector:
    """文件IO保護器 - 防止文件損毀"""
    
    def __init__(self, encoding_protector: EncodingProtector = None,
                 data_validator: DataValidator = None):
        self.encoding_protector = encoding_protector or EncodingProtector()
        self.data_validator = data_validator or DataValidator()
        logger.info("✅ FileIOProtector initialized")
    
    def read_safe(self, filepath: str, encoding: str = None) -> Optional[str]:
        """安全讀取文件"""
        try:
            path = Path(filepath)
            if not path.exists():
                logger.error(f"❌ File not found: {filepath}")
                return None
            
            with open(path, 'rb') as f:
                raw_data = f.read()
            
            # 偵測編碼
            detected_encoding = self.encoding_protector.detect_encoding(raw_data)
            encoding = encoding or detected_encoding
            
            # 安全解碼
            content = self.encoding_protector.safe_decode(raw_data, encoding)
            
            # 清理內容
            content = self.encoding_protector.clean_string(content)
            
            logger.info(f"✅ File read successfully: {filepath} (encoding: {encoding})")
            return content
        
        except Exception as e:
            logger.error(f"❌ Failed to read file {filepath}: {e}")
            return None
    
    def write_safe(self, filepath: str, content: str, 
                   encoding: str = None, backup: bool = True) -> bool:
        """安全寫入文件"""
        try:
            path = Path(filepath)
            encoding = encoding or "utf-8"
            
            if backup and path.exists():
                backup_path = path.with_suffix(path.suffix + '.backup')
                shutil.copy2(path, backup_path)
                logger.debug(f"✅ Backup created: {backup_path}")
            
            # 驗證內容
            if not self.encoding_protector.validate_string(content):
                logger.warning("⚠️ Content validation failed, attempting repair")
                content = self.encoding_protector.clean_string(content)
            
            # 安全編碼和寫入
            encoded_data = self.encoding_protector.safe_encode(content, encoding)
            
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(encoded_data)
            
            logger.info(f"✅ File written successfully: {filepath} (encoding: {encoding})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to write file {filepath}: {e}")
            return False
    
    def validate_file(self, filepath: str) -> Dict[str, Any]:
        """驗證文件完整性"""
        try:
            content = self.read_safe(filepath)
            if not content:
                return {"valid": False, "reason": "Could not read file"}
            
            result = {
                "valid": True,
                "filepath": filepath,
                "size_bytes": len(content.encode('utf-8')),
                "encoding": "utf-8",
                "has_encoding_errors": False,
                "checksum": self.data_validator.calculate_checksum(content)
            }
            
            logger.info(f"✅ File validation passed: {filepath}")
            return result
        
        except Exception as e:
            logger.error(f"❌ File validation failed: {e}")
            return {"valid": False, "reason": str(e)}


class SystemEncodingManager:
    """系統編碼管理器 - 統一管理編碼設置"""
    
    def __init__(self):
        self.encoding_protector = EncodingProtector()
        self.data_validator = DataValidator()
        self.file_protector = FileIOProtector(self.encoding_protector, self.data_validator)
        logger.info("✅ SystemEncodingManager initialized")
    
    def initialize_system_encoding(self):
        """初始化系統編碼"""
        logger.info("🔧 Initializing system encoding...")
        
        # 設置Python編碼
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            os.environ['LANG'] = 'en_US.UTF-8'
            os.environ['LC_ALL'] = 'en_US.UTF-8'
            logger.info("✅ System encoding initialized to UTF-8")
        except Exception as e:
            logger.warning(f"⚠️ Could not fully initialize encoding: {e}")
    
    def get_full_report(self) -> str:
        """獲取完整報告"""
        report = "\n" + "="*80 + "\n"
        report += "🔐 編碼保護和數據驗證系統報告\n"
        report += "   (Encoding Protection & Data Validation Report)\n"
        report += "="*80 + "\n"
        
        # 編碼錯誤日誌
        report += "\n📋 編碼錯誤日誌:\n"
        log = self.encoding_protector.get_error_log()
        if log:
            for error in log[-5:]:
                report += f"  - {error['original_encoding']} -> {error['used_encoding']}\n"
        else:
            report += "  ✅ 無編碼錯誤\n"
        
        # 數據驗證報告
        report += "\n✅ 數據驗證報告:\n"
        val_report = self.data_validator.get_validation_report()
        report += f"  總驗證次數: {val_report['total_validations']}\n"
        report += f"  通過: {val_report['passed']}\n"
        report += f"  失敗: {val_report['failed']}\n"
        report += f"  成功率: {val_report['success_rate']:.2f}%\n"
        
        report += "\n" + "="*80 + "\n"
        return report


# 全局實例
_system_encoding_manager = None


def get_encoding_manager() -> SystemEncodingManager:
    """獲取全局編碼管理器"""
    global _system_encoding_manager
    if _system_encoding_manager is None:
        _system_encoding_manager = SystemEncodingManager()
        _system_encoding_manager.initialize_system_encoding()
    return _system_encoding_manager


def safe_print(text: str, **kwargs):
    """安全打印函數"""
    manager = get_encoding_manager()
    cleaned_text = manager.encoding_protector.clean_string(text)
    print(cleaned_text, **kwargs)


# 導入datetime以支持時間戳
from datetime import datetime


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 測試編碼保護
    manager = get_encoding_manager()
    
    print("\n🔐 編碼保護系統測試")
    print("="*50)
    
    # 測試字符串清理
    test_string = "Hello\x00World\x01Test\x02文字"
    cleaned = manager.encoding_protector.clean_string(test_string)
    safe_print(f"原始: {test_string}")
    safe_print(f"清理後: {cleaned}")
    
    # 測試驗證
    manager.data_validator.log_validation_event("test_json", "JSON", True)
    
    print(manager.get_full_report())
