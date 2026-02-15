#!/usr/bin/env python3
"""
智能文件處理系統 CLI 入口
提供友善的命令行界面用於文件上傳和分析
"""

import os
import sys
from pathlib import Path
from typing import Optional
import json

from intelligent_file_processor import (
    IntelligentFileProcessor,
    ProcessingStrategy,
    FileType,
)


class FileProcessorCLI:
    """CLI 入口點"""
    
    def __init__(self):
        self.processor = IntelligentFileProcessor()
    
    def print_banner(self):
        """打印歡迎標籤"""
        banner = """
╔════════════════════════════════════════════════════╗
║   🚀 智能文件處理系統 (Intelligent File Processor)   ║
║         支持圖片、文字、壓縮檔自動分析            ║
║         前沿技術 + 經典算法 混合模式              ║
╚════════════════════════════════════════════════════╝

📋 支持的文件類型:
  🖼️  圖片: JPG, PNG, GIF, BMP, WEBP, SVG...
  📝 文字: TXT, MD, LOG, CSV, JSON, YAML, XML...
  💻 代碼: PY, JS, TS, JAVA, CPP, GO, RS...
  📦 壓縮: ZIP, TAR, GZ, BZ2, RAR, 7Z...
  📄 文檔: PDF, DOCX, XLSX, PPTX...

        """
        print(banner)
    
    def print_help(self):
        """打印幫助信息"""
        help_text = """
使用方法:
  python intelligent_file_processor_cli.py <命令> [選項]

命令:
  upload <文件路徑>       上傳並分析單個文件
  batch <目錄路徑>       批量分析目錄中的文件
  history               查看分析歷史
  help                  顯示本幫助信息

選項 (upload):
  --report              生成詳細分析報告
  --json                輸出 JSON 格式
  --strategy <strategy> 處理策略:
                        - advanced: 優先使用前沿技術
                        - classic:  僅使用經典算法
                        - hybrid:   混合模式 (推薦)

範例:
  python intelligent_file_processor_cli.py upload photo.jpg --report
  python intelligent_file_processor_cli.py upload script.py --json
  python intelligent_file_processor_cli.py batch ./project_files/
        """
        print(help_text)
    
    def upload_file(self, filepath: str, report: bool = False, json_output: bool = False, 
                   strategy: str = 'hybrid'):
        """上傳並分析單個文件"""
        file_path = Path(filepath)
        
        if not file_path.exists():
            print(f"❌ 錯誤: 文件不存在 - {filepath}")
            return False
        
        print(f"\n📥 上傳文件: {file_path.name}")
        print(f"   大小: {file_path.stat().st_size / 1024:.2f} KB")
        print(f"   策略: {strategy}\n")
        
        try:
            # 處理文件
            result = self.processor.process_file(
                str(file_path),
                strategy=ProcessingStrategy[strategy.upper()]
            )
            
            # 輸出結果
            if json_output:
                self._output_json(result)
            elif report:
                self._output_report(result)
            else:
                self._output_summary(result)
            
            return True
        
        except Exception as e:
            print(f"❌ 分析失敗: {e}")
            return False
    
    def batch_process(self, directory: str):
        """批量處理目錄中的文件"""
        dir_path = Path(directory)
        
        if not dir_path.is_dir():
            print(f"❌ 錯誤: 目錄不存在 - {directory}")
            return
        
        files = list(dir_path.rglob('*'))
        files = [f for f in files if f.is_file()]
        
        if not files:
            print(f"❌ 目錄中沒有文件")
            return
        
        print(f"\n📦 批量處理目錄: {dir_path}")
        print(f"   找到 {len(files)} 個文件\n")
        
        results_summary = {
            'total': len(files),
            'succeeded': 0,
            'failed': 0,
            'by_type': {},
        }
        
        for i, file_path in enumerate(files, 1):
            try:
                print(f"[{i}/{len(files)}] 處理: {file_path.name}... ", end='')
                result = self.processor.process_file(str(file_path))
                
                file_type = result.file_type.value
                results_summary['by_type'][file_type] = results_summary['by_type'].get(file_type, 0) + 1
                results_summary['succeeded'] += 1
                print("✅")
            
            except Exception as e:
                results_summary['failed'] += 1
                print(f"❌ ({str(e)[:30]})")
        
        # 輸出總結
        print(f"\n📊 批量處理完成:")
        print(f"   成功: {results_summary['succeeded']}/{results_summary['total']}")
        print(f"   失敗: {results_summary['failed']}/{results_summary['total']}")
        print(f"   按類型統計:")
        for file_type, count in results_summary['by_type'].items():
            print(f"     - {file_type}: {count}")
    
    def _output_summary(self, result):
        """輸出摘要格式"""
        print("✅ 分析完成")
        print(f"📄 檔案: {result.file_metadata.filename}")
        print(f"📊 類型: {result.file_type.value}")
        print(f"📝 摘要: {result.content_summary}")
        print(f"📈 信心: {result.analysis_confidence * 100:.0f}%")
        print(f"⏱️  耗時: {result.processing_time:.3f} 秒")
    
    def _output_report(self, result):
        """輸出詳細報告"""
        report = self.processor.generate_report(result)
        print(report)
    
    def _output_json(self, result):
        """輸出 JSON 格式"""
        output = {
            'status': 'success',
            'metadata': {
                'filename': result.file_metadata.filename,
                'filepath': result.file_metadata.filepath,
                'size_kb': result.file_metadata.file_size / 1024,
                'mime_type': result.file_metadata.mime_type,
                'hash': result.file_metadata.hash_value,
                'encoding': result.file_metadata.encoding,
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
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    def show_history(self):
        """顯示分析歷史"""
        if not self.processor.results_history:
            print("📋 暫無分析歷史")
            return
        
        print("\n📋 分析歷史:")
        print("=" * 70)
        
        for i, result in enumerate(self.processor.results_history, 1):
            print(f"\n{i}. {result.file_metadata.filename}")
            print(f"   類型: {result.file_type.value}")
            print(f"   摘要: {result.content_summary}")
            print(f"   信心: {result.analysis_confidence * 100:.0f}%")
    
    def run(self, args: Optional[list] = None):
        """主程序"""
        if args is None:
            args = sys.argv[1:]
        
        self.print_banner()
        
        if not args or args[0] == 'help':
            self.print_help()
            return
        
        command = args[0]
        
        if command == 'upload' and len(args) > 1:
            filepath = args[1]
            report = '--report' in args
            json_output = '--json' in args
            
            # 提取 strategy
            strategy = 'hybrid'
            for i, arg in enumerate(args):
                if arg == '--strategy' and i + 1 < len(args):
                    strategy = args[i + 1]
            
            self.upload_file(filepath, report=report, json_output=json_output, strategy=strategy)
        
        elif command == 'batch' and len(args) > 1:
            self.batch_process(args[1])
        
        elif command == 'history':
            self.show_history()
        
        else:
            print(f"❌ 未知命令: {command}")
            print("使用 'help' 查看幫助信息")


def main():
    """入口點"""
    cli = FileProcessorCLI()
    cli.run()


if __name__ == '__main__':
    main()
