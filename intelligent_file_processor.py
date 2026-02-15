#!/usr/bin/env python3
"""
智能文件處理系統 (Intelligent File Processing Engine)
支持圖片、文字、壓縮檔的自動上傳、識別和分析
融合前沿技術與經典算法的混合模式
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import mimetypes
import tempfile
import shutil
import zipfile
import tarfile

import numpy as np

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileType(Enum):
    """文件類型枚舉"""
    IMAGE = "image"
    TEXT = "text"
    CODE = "code"
    ARCHIVE = "archive"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class ProcessingStrategy(Enum):
    """處理策略 - 前沿優先，失敗時降級到經典"""
    ADVANCED = "advanced"  # 前沿技術
    CLASSIC = "classic"    # 經典算法
    HYBRID = "hybrid"      # 混合模式


@dataclass
class FileMetadata:
    """文件元數據"""
    filename: str
    filepath: str
    file_type: FileType
    file_size: int
    mime_type: str
    created_at: str
    hash_value: str
    encoding: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return asdict(self)


@dataclass
class AnalysisResult:
    """分析結果"""
    file_metadata: FileMetadata
    file_type: FileType
    strategy_used: ProcessingStrategy
    content_summary: str
    key_findings: List[str]
    content_preview: str
    analysis_confidence: float
    processing_time: float
    recommendations: List[str]
    raw_data: Optional[Dict] = None


class FileClassifier:
    """文件自動分類器"""
    
    # 文件簽名 (Magic Numbers)
    FILE_SIGNATURES = {
        b'\xFF\xD8\xFF': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'GIF87a': 'image/gif',
        b'GIF89a': 'image/gif',
        b'PK\x03\x04': 'application/zip',
        b'\x1f\x8b\x08': 'application/gzip',
        b'BZh': 'application/x-bzip2',
    }
    
    TEXT_EXTENSIONS = {'.txt', '.md', '.log', '.csv', '.json', '.yaml', '.yml', '.xml'}
    CODE_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
    ARCHIVE_EXTENSIONS = {'.zip', '.tar', '.gz', '.tar.gz', '.bz2', '.rar', '.7z'}
    DOCUMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'}
    
    @staticmethod
    def detect_file_type(filepath: str) -> FileType:
        """偵測文件類型"""
        path = Path(filepath)
        suffix = path.suffix.lower()
        
        # 優先檢查擴展名
        if suffix in FileClassifier.CODE_EXTENSIONS:
            return FileType.CODE
        elif suffix in FileClassifier.TEXT_EXTENSIONS:
            return FileType.TEXT
        elif suffix in FileClassifier.IMAGE_EXTENSIONS:
            return FileType.IMAGE
        elif suffix in FileClassifier.ARCHIVE_EXTENSIONS:
            return FileType.ARCHIVE
        elif suffix in FileClassifier.DOCUMENT_EXTENSIONS:
            return FileType.DOCUMENT
        
        # 檢查文件簽名
        try:
            with open(filepath, 'rb') as f:
                header = f.read(8)
                for sig, mime in FileClassifier.FILE_SIGNATURES.items():
                    if header.startswith(sig):
                        if 'image' in mime:
                            return FileType.IMAGE
                        elif 'zip' in mime or 'gzip' in mime or 'bzip' in mime:
                            return FileType.ARCHIVE
        except Exception as e:
            logger.warning(f"無法讀取文件簽名: {e}")
        
        return FileType.UNKNOWN
    
    @staticmethod
    def get_mime_type(filepath: str) -> str:
        """獲取 MIME 類型"""
        mime_type, _ = mimetypes.guess_type(filepath)
        return mime_type or 'application/octet-stream'


class ContentAnalyzer:
    """內容分析器 - 經典算法基礎"""
    
    @staticmethod
    def analyze_text(content: str, max_preview: int = 500) -> Dict[str, Any]:
        """分析文本內容"""
        lines = content.split('\n')
        words = content.split()
        
        analysis = {
            'line_count': len(lines),
            'word_count': len(words),
            'char_count': len(content),
            'avg_line_length': np.mean([len(line) for line in lines]) if lines else 0,
            'unique_words': len(set(w.lower() for w in words)),
            'preview': content[:max_preview] + ('...' if len(content) > max_preview else ''),
        }
        
        # 檢測可能的結構
        if content.startswith('{') or content.startswith('['):
            analysis['probable_format'] = 'JSON'
        elif content.startswith('---') or ':' in content:
            analysis['probable_format'] = 'YAML'
        elif '<' in content and '>' in content:
            analysis['probable_format'] = 'XML/HTML'
        elif content.startswith('#!/'):
            analysis['probable_format'] = 'Script'
        else:
            analysis['probable_format'] = 'Plain Text'
        
        # 關鍵字檢測
        keywords = ContentAnalyzer._extract_keywords(content)
        analysis['top_keywords'] = keywords[:10]
        
        return analysis
    
    @staticmethod
    def _extract_keywords(text: str, top_n: int = 20) -> List[str]:
        """使用經典 TF-IDF 方法提取關鍵字"""
        words = text.lower().split()
        # 簡單詞頻計數 (不用停用詞，保持通用)
        word_freq = {}
        for word in words:
            word = word.strip('.,!?;:"\'-')
            if len(word) > 3:  # 至少 4 個字符
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 排序並返回前 N 個
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]
    
    @staticmethod
    def analyze_code(content: str) -> Dict[str, Any]:
        """分析代碼內容"""
        lines = content.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        comment_lines = [l for l in lines if '#' in l]
        
        analysis = {
            'total_lines': len(lines),
            'code_lines': len(code_lines),
            'comment_lines': len(comment_lines),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'comment_ratio': len(comment_lines) / len(lines) if lines else 0,
        }
        
        # 檢測語言特性
        if 'import' in content or 'from' in content:
            analysis['language_hint'] = 'Python'
        elif 'require' in content or 'module.exports' in content:
            analysis['language_hint'] = 'JavaScript/Node.js'
        elif 'package' in content and 'import' in content:
            analysis['language_hint'] = 'Java'
        elif '#include' in content:
            analysis['language_hint'] = 'C/C++'
        
        return analysis


class ArchiveAnalyzer:
    """壓縮檔分析器"""
    
    @staticmethod
    def analyze_archive(filepath: str) -> Dict[str, Any]:
        """分析壓縮檔內容"""
        analysis = {
            'file_count': 0,
            'total_size': 0,
            'compressed_size': 0,
            'file_list': [],
            'format': 'unknown',
        }
        
        try:
            # 檢測壓縮檔格式
            suffix = Path(filepath).suffix.lower()
            
            if suffix == '.zip':
                return ArchiveAnalyzer._analyze_zip(filepath)
            elif suffix in ['.tar', '.tar.gz', '.tgz']:
                return ArchiveAnalyzer._analyze_tar(filepath)
            
        except Exception as e:
            logger.error(f"無法分析壓縮檔: {e}")
        
        return analysis
    
    @staticmethod
    def _analyze_zip(filepath: str) -> Dict[str, Any]:
        """分析 ZIP 檔案"""
        analysis = {'format': 'ZIP', 'file_list': [], 'file_count': 0, 'total_size': 0}
        
        try:
            with zipfile.ZipFile(filepath, 'r') as z:
                for info in z.infolist():
                    analysis['file_list'].append({
                        'filename': info.filename,
                        'size': info.file_size,
                        'compressed_size': info.compress_size,
                    })
                    analysis['total_size'] += info.file_size
                    analysis['file_count'] += 1
        except Exception as e:
            logger.error(f"ZIP 分析失敗: {e}")
        
        return analysis
    
    @staticmethod
    def _analyze_tar(filepath: str) -> Dict[str, Any]:
        """分析 TAR 檔案"""
        analysis = {'format': 'TAR', 'file_list': [], 'file_count': 0, 'total_size': 0}
        
        try:
            with tarfile.open(filepath, 'r:*') as t:
                for member in t.getmembers():
                    analysis['file_list'].append({
                        'filename': member.name,
                        'size': member.size,
                        'type': 'dir' if member.isdir() else 'file',
                    })
                    analysis['total_size'] += member.size
                    analysis['file_count'] += 1
        except Exception as e:
            logger.error(f"TAR 分析失敗: {e}")
        
        return analysis


class IntelligentFileProcessor:
    """智能文件處理主系統"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """初始化處理器"""
        self.cache_dir = Path(cache_dir or tempfile.gettempdir()) / 'ifp_cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.results_history: List[AnalysisResult] = []
    
    def process_file(self, filepath: str, strategy: ProcessingStrategy = ProcessingStrategy.HYBRID) -> AnalysisResult:
        """處理單個文件 - 主流程"""
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        start_time = datetime.now()
        
        # 第一步: 文件分類
        file_type = FileClassifier.detect_file_type(filepath)
        metadata = self._create_metadata(file_path, file_type)
        
        logger.info(f"處理文件: {file_path.name} (類型: {file_type.value})")
        
        # 第二步: 根據類型分派處理
        if file_type == FileType.IMAGE:
            result = self._process_image(file_path, metadata, strategy)
        elif file_type == FileType.TEXT:
            result = self._process_text(file_path, metadata, strategy)
        elif file_type == FileType.CODE:
            result = self._process_code(file_path, metadata, strategy)
        elif file_type == FileType.ARCHIVE:
            result = self._process_archive(file_path, metadata, strategy)
        else:
            result = self._process_unknown(file_path, metadata, strategy)
        
        # 計算處理時間
        result.processing_time = (datetime.now() - start_time).total_seconds()
        
        # 儲存到歷史
        self.results_history.append(result)
        
        return result
    
    def _create_metadata(self, filepath: Path, file_type: FileType) -> FileMetadata:
        """創建文件元數據"""
        file_stat = filepath.stat()
        
        # 計算文件哈希
        hash_value = self._calculate_hash(filepath)
        
        # 偵測編碼 (僅限文本)
        encoding = None
        if file_type in [FileType.TEXT, FileType.CODE]:
            encoding = self._detect_encoding(filepath)
        
        return FileMetadata(
            filename=filepath.name,
            filepath=str(filepath.absolute()),
            file_type=file_type,
            file_size=file_stat.st_size,
            mime_type=FileClassifier.get_mime_type(str(filepath)),
            created_at=datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            hash_value=hash_value,
            encoding=encoding,
        )
    
    def _calculate_hash(self, filepath: Path, chunk_size: int = 8192) -> str:
        """計算文件 SHA-256 哈希"""
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()[:16]
    
    def _detect_encoding(self, filepath: Path) -> Optional[str]:
        """檢測文本文件編碼"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                # 簡單的編碼檢測
                for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
                    try:
                        content.decode(encoding)
                        return encoding
                    except UnicodeDecodeError:
                        continue
                return 'unknown'
        except Exception:
            return None
    
    def _process_image(self, filepath: Path, metadata: FileMetadata, strategy: ProcessingStrategy) -> AnalysisResult:
        """處理圖片文件"""
        logger.info(f"使用 {strategy.value} 策略處理圖片: {filepath.name}")
        
        # 嘗試前沿技術 (Claude Vision)
        if strategy in [ProcessingStrategy.ADVANCED, ProcessingStrategy.HYBRID]:
            try:
                result = self._analyze_with_vision(filepath, metadata)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"前沿視覺分析失敗，降級到經典方法: {e}")
        
        # 降級到經典方法
        return self._analyze_image_classic(filepath, metadata)
    
    def _analyze_with_vision(self, filepath: Path, metadata: FileMetadata) -> Optional[AnalysisResult]:
        """使用 Claude Vision API 分析圖片"""
        # 注意: 這是一個占位符實現
        # 實際使用需要 Anthropic API 客戶端
        logger.info("Vision API 分析 (占位符)")
        return None
    
    def _analyze_image_classic(self, filepath: Path, metadata: FileMetadata) -> AnalysisResult:
        """使用經典方法分析圖片"""
        try:
            from PIL import Image
            img = Image.open(filepath)
            
            findings = [
                f"解析度: {img.size[0]}x{img.size[1]} 像素",
                f"色彩模式: {img.mode}",
                f"格式: {img.format}",
                f"檔案大小: {metadata.file_size / 1024:.2f} KB",
            ]
            
            summary = f"圖片分析完成。解析度 {img.size[0]}x{img.size[1]}, {img.mode} 色彩模式"
            
        except Exception as e:
            findings = [f"基本圖片分析"]
            summary = f"圖片檔案，檔案大小 {metadata.file_size / 1024:.2f} KB"
        
        return AnalysisResult(
            file_metadata=metadata,
            file_type=FileType.IMAGE,
            strategy_used=ProcessingStrategy.CLASSIC,
            content_summary=summary,
            key_findings=findings,
            content_preview=f"圖片: {filepath.name}",
            analysis_confidence=0.8,
            processing_time=0.0,
            recommendations=["檢查圖片質量", "考慮優化解析度"],
        )
    
    def _process_text(self, filepath: Path, metadata: FileMetadata, strategy: ProcessingStrategy) -> AnalysisResult:
        """處理文字檔"""
        with open(filepath, 'r', encoding=metadata.encoding or 'utf-8', errors='ignore') as f:
            content = f.read()
        
        analysis = ContentAnalyzer.analyze_text(content)
        
        findings = [
            f"行數: {analysis['line_count']}",
            f"單詞數: {analysis['word_count']}",
            f"格式: {analysis['probable_format']}",
            f"平均行長: {analysis['avg_line_length']:.1f} 字符",
        ]
        
        recommendations = self._generate_text_recommendations(analysis)
        
        return AnalysisResult(
            file_metadata=metadata,
            file_type=FileType.TEXT,
            strategy_used=ProcessingStrategy.CLASSIC,
            content_summary=f"{analysis['probable_format']} 文本檔，{analysis['line_count']} 行",
            key_findings=findings,
            content_preview=analysis['preview'],
            analysis_confidence=0.9,
            processing_time=0.0,
            recommendations=recommendations,
            raw_data=analysis,
        )
    
    def _process_code(self, filepath: Path, metadata: FileMetadata, strategy: ProcessingStrategy) -> AnalysisResult:
        """處理代碼文件"""
        with open(filepath, 'r', encoding=metadata.encoding or 'utf-8', errors='ignore') as f:
            content = f.read()
        
        text_analysis = ContentAnalyzer.analyze_text(content)
        code_analysis = ContentAnalyzer.analyze_code(content)
        
        findings = [
            f"代碼行數: {code_analysis['code_lines']}",
            f"註解行數: {code_analysis['comment_lines']}",
            f"空行數: {code_analysis['blank_lines']}",
            f"語言提示: {code_analysis.get('language_hint', '未知')}",
            f"註解比例: {code_analysis['comment_ratio']:.1%}",
        ]
        
        recommendations = self._generate_code_recommendations(code_analysis, text_analysis)
        
        return AnalysisResult(
            file_metadata=metadata,
            file_type=FileType.CODE,
            strategy_used=ProcessingStrategy.CLASSIC,
            content_summary=f"代碼檔案 ({code_analysis.get('language_hint', '未知')} 提示)，{code_analysis['code_lines']} 行代碼",
            key_findings=findings,
            content_preview=content[:300] + '...',
            analysis_confidence=0.85,
            processing_time=0.0,
            recommendations=recommendations,
            raw_data={**text_analysis, **code_analysis},
        )
    
    def _process_archive(self, filepath: Path, metadata: FileMetadata, strategy: ProcessingStrategy) -> AnalysisResult:
        """處理壓縮檔"""
        archive_analysis = ArchiveAnalyzer.analyze_archive(str(filepath))
        
        findings = [
            f"格式: {archive_analysis['format']}",
            f"檔案數: {archive_analysis['file_count']}",
            f"總大小: {archive_analysis['total_size'] / 1024:.2f} KB",
        ]
        
        if archive_analysis['file_list']:
            top_files = sorted(archive_analysis['file_list'], 
                             key=lambda x: x.get('size', 0), reverse=True)[:5]
            findings.append("最大檔案:")
            for f in top_files:
                findings.append(f"  - {f['filename']}: {f.get('size', 0) / 1024:.2f} KB")
        
        recommendations = [
            f"壓縮檔包含 {archive_analysis['file_count']} 個檔案",
            "考慮檔案結構優化" if archive_analysis['file_count'] > 100 else "檔案結構合理",
        ]
        
        return AnalysisResult(
            file_metadata=metadata,
            file_type=FileType.ARCHIVE,
            strategy_used=ProcessingStrategy.CLASSIC,
            content_summary=f"{archive_analysis['format']} 壓縮檔，{archive_analysis['file_count']} 個檔案",
            key_findings=findings,
            content_preview=f"檔案列表 ({len(archive_analysis['file_list'])} 項)",
            analysis_confidence=0.95,
            processing_time=0.0,
            recommendations=recommendations,
            raw_data=archive_analysis,
        )
    
    def _process_unknown(self, filepath: Path, metadata: FileMetadata, strategy: ProcessingStrategy) -> AnalysisResult:
        """處理未知類型檔案"""
        findings = [
            f"檔案類型: 未知",
            f"檔案大小: {metadata.file_size / 1024:.2f} KB",
            f"MIME 類型: {metadata.mime_type}",
        ]
        
        return AnalysisResult(
            file_metadata=metadata,
            file_type=FileType.UNKNOWN,
            strategy_used=ProcessingStrategy.CLASSIC,
            content_summary="未知檔案類型",
            key_findings=findings,
            content_preview="無法預覽",
            analysis_confidence=0.3,
            processing_time=0.0,
            recommendations=["檢查檔案副檔名", "嘗試手動識別檔案類型"],
        )
    
    def _generate_text_recommendations(self, analysis: Dict) -> List[str]:
        """生成文本檔建議"""
        recommendations = []
        
        if analysis['line_count'] > 1000:
            recommendations.append("檔案較大，考慮分割成多個檔案")
        
        if analysis['avg_line_length'] > 120:
            recommendations.append("行長較長，考慮重新格式化")
        
        if analysis['probable_format'] == 'JSON':
            recommendations.append("使用 JSON 驗證工具檢查語法")
        
        if not recommendations:
            recommendations.append(f"檔案結構清晰，{analysis['probable_format']} 格式")
        
        return recommendations
    
    def _generate_code_recommendations(self, code_analysis: Dict, text_analysis: Dict) -> List[str]:
        """生成代碼檔建議"""
        recommendations = []
        
        if code_analysis['comment_ratio'] < 0.1:
            recommendations.append("建議增加註解說明")
        
        if code_analysis['code_lines'] > 500:
            recommendations.append("代碼行數較多，考慮拆分成模塊")
        
        if code_analysis.get('language_hint'):
            recommendations.append(f"檢測到 {code_analysis['language_hint']} 語言")
        
        if text_analysis.get('top_keywords'):
            recommendations.append(f"主要關鍵字: {', '.join(text_analysis['top_keywords'][:3])}")
        
        return recommendations if recommendations else ["代碼結構良好"]
    
    def generate_report(self, result: AnalysisResult) -> str:
        """生成分析報告"""
        report = []
        report.append("=" * 60)
        report.append(f"智能文件分析報告")
        report.append("=" * 60)
        report.append("")
        
        # 基本信息
        report.append("📄 檔案信息")
        report.append(f"  名稱: {result.file_metadata.filename}")
        report.append(f"  類型: {result.file_type.value}")
        report.append(f"  大小: {result.file_metadata.file_size / 1024:.2f} KB")
        report.append(f"  哈希: {result.file_metadata.hash_value}")
        report.append("")
        
        # 分析摘要
        report.append("📊 分析摘要")
        report.append(f"  {result.content_summary}")
        report.append("")
        
        # 主要發現
        report.append("🔍 主要發現")
        for finding in result.key_findings:
            report.append(f"  • {finding}")
        report.append("")
        
        # 信心度
        report.append("📈 分析信心度")
        report.append(f"  {result.analysis_confidence * 100:.0f}%")
        report.append("")
        
        # 建議
        report.append("💡 建議")
        for rec in result.recommendations:
            report.append(f"  • {rec}")
        report.append("")
        
        # 處理時間
        report.append(f"⏱️  處理時間: {result.processing_time:.3f} 秒")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """主程序"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能文件處理系統")
    parser.add_argument("file", nargs="?", help="要處理的文件路徑")
    parser.add_argument("--report", action="store_true", help="生成詳細報告")
    parser.add_argument("--json", action="store_true", help="輸出 JSON 格式")
    parser.add_argument("--strategy", choices=['advanced', 'classic', 'hybrid'], 
                       default='hybrid', help="處理策略")
    
    args = parser.parse_args()
    
    if not args.file:
        print("智能文件處理系統 v1.0")
        print("用法: python intelligent_file_processor.py <文件路徑> [選項]")
        print("選項:")
        print("  --report    生成詳細報告")
        print("  --json      輸出 JSON 格式")
        print("  --strategy  處理策略 (advanced|classic|hybrid)")
        return
    
    # 建立處理器
    processor = IntelligentFileProcessor()
    
    try:
        # 處理文件
        result = processor.process_file(
            args.file,
            strategy=ProcessingStrategy[args.strategy.upper()]
        )
        
        # 輸出結果
        if args.json:
            output = {
                'metadata': result.file_metadata.to_dict(),
                'file_type': result.file_type.value,
                'strategy': result.strategy_used.value,
                'summary': result.content_summary,
                'findings': result.key_findings,
                'confidence': result.analysis_confidence,
                'recommendations': result.recommendations,
                'processing_time': result.processing_time,
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif args.report:
            print(processor.generate_report(result))
        else:
            print(f"✅ 分析完成: {result.content_summary}")
            print(f"📊 信心度: {result.analysis_confidence * 100:.0f}%")
            print(f"⏱️  耗時: {result.processing_time:.3f} 秒")
    
    except Exception as e:
        logger.error(f"處理失敗: {e}")
        print(f"❌ 錯誤: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
