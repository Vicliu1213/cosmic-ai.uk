#!/usr/bin/env python3
"""
OpenCode 智能文件分析代理
允許通過 OpenCode AI 代理系統進行文件上傳、識別和分析
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# 導入文件處理系統
from intelligent_file_processor import (
    IntelligentFileProcessor,
    ProcessingStrategy,
    AnalysisResult,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenCodeFileAnalysisAgent:
    """OpenCode 文件分析代理 - 可被 OpenCode AI 調用"""
    
    def __init__(self):
        """初始化代理"""
        self.processor = IntelligentFileProcessor()
        self.last_result: Optional[AnalysisResult] = None
    
    async def analyze_file(self, filepath: str, output_format: str = "report") -> Dict[str, Any]:
        """
        分析單個文件 (OpenCode 代理方法簽名)
        
        Args:
            filepath: 文件路徑
            output_format: 輸出格式 ("report" 或 "json")
            
        Returns:
            分析結果字典
        """
        try:
            self.last_result = self.processor.process_file(
                filepath,
                strategy=ProcessingStrategy.HYBRID
            )
            
            if output_format == "json":
                return self._result_to_json()
            else:
                return self._result_to_report()
        
        except Exception as e:
            logger.error(f"分析失敗: {e}")
            return {
                'status': 'error',
                'message': str(e),
            }
    
    async def batch_analyze(self, directory: str) -> Dict[str, Any]:
        """
        批量分析目錄中的文件
        
        Args:
            directory: 目錄路徑
            
        Returns:
            批量分析結果
        """
        try:
            dir_path = Path(directory)
            if not dir_path.is_dir():
                return {
                    'status': 'error',
                    'message': f'目錄不存在: {directory}'
                }
            
            files = list(dir_path.rglob('*'))
            files = [f for f in files if f.is_file()]
            
            results = []
            stats = {
                'total': len(files),
                'succeeded': 0,
                'failed': 0,
                'by_type': {},
            }
            
            for file_path in files:
                try:
                    result = self.processor.process_file(str(file_path))
                    file_type = result.file_type.value
                    stats['by_type'][file_type] = stats['by_type'].get(file_type, 0) + 1
                    stats['succeeded'] += 1
                    
                    results.append({
                        'filename': result.file_metadata.filename,
                        'type': file_type,
                        'summary': result.content_summary,
                        'confidence': result.analysis_confidence,
                    })
                
                except Exception as e:
                    stats['failed'] += 1
                    results.append({
                        'filename': file_path.name,
                        'error': str(e),
                    })
            
            return {
                'status': 'success',
                'stats': stats,
                'results': results,
            }
        
        except Exception as e:
            logger.error(f"批量分析失敗: {e}")
            return {
                'status': 'error',
                'message': str(e),
            }
    
    async def get_file_intelligence(self, filepath: str) -> Dict[str, Any]:
        """
        獲取文件的完整智能分析 (包含建議和優化)
        
        Args:
            filepath: 文件路徑
            
        Returns:
            完整的智能分析結果
        """
        if not self.last_result or self.last_result.file_metadata.filepath != filepath:
            await self.analyze_file(filepath)
        
        if not self.last_result:
            return {'status': 'error', 'message': 'No analysis result'}
        
        result = self.last_result
        
        return {
            'status': 'success',
            'file': {
                'name': result.file_metadata.filename,
                'type': result.file_type.value,
                'size_kb': result.file_metadata.file_size / 1024,
                'hash': result.file_metadata.hash_value,
            },
            'analysis': {
                'summary': result.content_summary,
                'findings': result.key_findings,
                'confidence': result.analysis_confidence,
                'strategy_used': result.strategy_used.value,
            },
            'recommendations': result.recommendations,
            'preview': result.content_preview[:500],
            'processing_time_ms': result.processing_time * 1000,
        }
    
    def _result_to_json(self) -> Dict[str, Any]:
        """轉換結果為 JSON 格式"""
        if not self.last_result:
            return {'status': 'error', 'message': 'No result'}
        
        result = self.last_result
        return {
            'status': 'success',
            'metadata': {
                'filename': result.file_metadata.filename,
                'filepath': result.file_metadata.filepath,
                'size_kb': result.file_metadata.file_size / 1024,
                'mime_type': result.file_metadata.mime_type,
                'hash': result.file_metadata.hash_value,
            },
            'file_type': result.file_type.value,
            'strategy': result.strategy_used.value,
            'analysis': {
                'summary': result.content_summary,
                'findings': result.key_findings,
                'confidence': result.analysis_confidence,
                'recommendations': result.recommendations,
            },
            'processing_time_seconds': result.processing_time,
        }
    
    def _result_to_report(self) -> Dict[str, Any]:
        """轉換結果為報告格式"""
        if not self.last_result:
            return {'status': 'error', 'message': 'No result'}
        
        report = self.processor.generate_report(self.last_result)
        return {
            'status': 'success',
            'report': report,
            'file': self.last_result.file_metadata.filename,
        }


# 全局代理實例
_agent_instance: Optional[OpenCodeFileAnalysisAgent] = None


def get_agent() -> OpenCodeFileAnalysisAgent:
    """獲取代理實例 (單例模式)"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = OpenCodeFileAnalysisAgent()
    return _agent_instance


# OpenCode 代理導出接口
async def on_message(message: str) -> str:
    """
    OpenCode 代理消息處理入口
    
    支持的命令:
    - analyze: <filepath>
    - batch: <directory>
    - intelligence: <filepath>
    - help
    """
    agent = get_agent()
    parts = message.strip().split(':', 1)
    command = parts[0].strip().lower()
    args = parts[1].strip() if len(parts) > 1 else ""
    
    try:
        if command == 'analyze':
            result = await agent.analyze_file(args, 'report')
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif command == 'batch':
            result = await agent.batch_analyze(args)
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif command == 'intelligence':
            result = await agent.get_file_intelligence(args)
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif command == 'help':
            return """OpenCode 智能文件分析代理

支持的命令:
  analyze: <文件路徑>        - 分析單個文件
  batch: <目錄路徑>          - 批量分析目錄
  intelligence: <文件路徑>   - 獲取完整智能分析
  help                      - 顯示此幫助

範例:
  analyze: /path/to/file.py
  batch: /path/to/directory
  intelligence: /path/to/image.jpg
"""
        
        else:
            return f"未知命令: {command}。使用 'help' 查看幫助。"
    
    except Exception as e:
        logger.error(f"代理錯誤: {e}")
        return f"錯誤: {str(e)}"


# CLI 測試入口
def main():
    """命令行測試"""
    if len(sys.argv) < 2:
        print("OpenCode 智能文件分析代理")
        print("用法: python opencode_file_analysis_agent.py <命令>")
        print("\n範例:")
        print("  python opencode_file_analysis_agent.py analyze: test_files/example.py")
        print("  python opencode_file_analysis_agent.py batch: test_files/")
        return
    
    import asyncio
    message = ' '.join(sys.argv[1:])
    result = asyncio.run(on_message(message))
    print(result)


if __name__ == '__main__':
    main()
