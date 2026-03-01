#!/usr/bin/env python3
"""
Code Quality Checker - 代碼質量檢查工具
Comprehensive code quality validation for Cosmic AI project
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class CodeQualityChecker:
    """Comprehensive code quality checker"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_dirs = ['src', 'data', 'engine', 'dashboard', 'scripts', 'optimizer']
        self.results: Dict[str, Any] = {}
        
    def check_syntax(self) -> Tuple[bool, List[str]]:
        """Check Python syntax for all files"""
        logger.info("🔍 檢查語法...")
        errors = []
        
        for src_dir in self.src_dirs:
            for py_file in self.project_root.glob(f"{src_dir}/**/*.py"):
                try:
                    compile(py_file.read_text(), str(py_file), 'exec')
                except SyntaxError as e:
                    errors.append(f"❌ {py_file}:{e.lineno}: {e.msg}")
        
        if errors:
            logger.error(f"❌ 發現 {len(errors)} 個語法錯誤")
            for error in errors:
                logger.error(f"  {error}")
            return False, errors
        else:
            logger.info("✅ 所有文件語法正確")
            return True, []
    
    def check_imports(self) -> Tuple[bool, List[str]]:
        """Check for missing imports"""
        logger.info("🔍 檢查導入...")
        errors = []
        
        for src_dir in self.src_dirs:
            for py_file in self.project_root.glob(f"{src_dir}/**/*.py"):
                try:
                    with open(py_file) as f:
                        lines = f.readlines()
                    
                    # Check for common missing imports
                    content = ''.join(lines)
                    issues = self._check_missing_imports(content, lines)
                    if issues:
                        errors.extend([(str(py_file), issue) for issue in issues])
                except Exception as e:
                    logger.debug(f"Skip {py_file}: {e}")
        
        if errors:
            logger.error(f"❌ 發現 {len(errors)} 個導入問題")
            for file_path, error in errors:
                logger.error(f"  {file_path}: {error}")
            return False, [f"{f}: {e}" for f, e in errors]
        else:
            logger.info("✅ 所有導入正確")
            return True, []
    
    def _check_missing_imports(self, content: str, lines: List[str]) -> List[str]:
        """Check for missing imports in file"""
        issues = []
        
        # Check for 'Any' without import
        if '-> Any:' in content or ': Any' in content:
            if 'from typing import' not in content or 'Any' not in content[:content.find('-> Any' if '-> Any:' in content else ': Any')]:
                # Simple heuristic check
                imports_section = content[:min(1000, len(content))]
                if 'Any' not in imports_section and ('-> Any' in content or ': Any' in content):
                    issues.append("缺失: from typing import Any")
        
        return issues
    
    def run_tests(self) -> Tuple[bool, str]:
        """Run pytest"""
        logger.info("🧪 運行測試...")
        try:
            result = subprocess.run(
                ['python3', '-m', 'pytest', 'src/tests/', '-q'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            if result.returncode == 0:
                logger.info("✅ 所有測試通過")
                return True, output
            else:
                logger.error("❌ 測試失敗")
                logger.error(output)
                return False, output
        except subprocess.TimeoutExpired:
            logger.error("❌ 測試超時")
            return False, "Test timeout"
        except Exception as e:
            logger.error(f"❌ 測試錯誤: {e}")
            return False, str(e)
    
    def check_linting(self) -> Tuple[bool, List[str]]:
        """Check with flake8"""
        logger.info("🔍 運行 Flake8 檢查...")
        errors = []
        
        try:
            for src_dir in self.src_dirs:
                result = subprocess.run(
                    ['flake8', src_dir, '--max-line-length=127', '--select=E9,F63,F7,F82'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.stdout:
                    errors.extend(result.stdout.strip().split('\n'))
        except Exception as e:
            logger.warning(f"⚠️  Flake8 不可用: {e}")
            return True, []  # Don't fail if flake8 not available
        
        if errors:
            logger.error(f"❌ Flake8 發現 {len(errors)} 個問題")
            for error in errors[:10]:  # Show first 10
                logger.error(f"  {error}")
            if len(errors) > 10:
                logger.error(f"  ... 和 {len(errors)-10} 個其他問題")
            return False, errors
        else:
            logger.info("✅ Flake8 檢查通過")
            return True, []
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all checks"""
        logger.info("\n" + "="*60)
        logger.info("🚀 開始代碼質量檢查")
        logger.info("="*60 + "\n")
        
        results = {
            'syntax': self.check_syntax(),
            'imports': self.check_imports(),
            'tests': self.run_tests(),
            'linting': self.check_linting(),
        }
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 檢查摘要")
        logger.info("="*60)
        
        all_passed = all(result[0] for result in results.values())
        
        for check_name, (passed, output) in results.items():
            status = "✅ 通過" if passed else "❌ 失敗"
            logger.info(f"{check_name.upper():15} {status}")
        
        logger.info("="*60)
        
        if all_passed:
            logger.info("✅ 所有檢查通過！代碼準備好提交。")
            return {'passed': True, 'results': results}
        else:
            logger.error("❌ 某些檢查失敗。請修復問題後重試。")
            return {'passed': False, 'results': results}

def main():
    checker = CodeQualityChecker()
    result = checker.run_all_checks()
    
    sys.exit(0 if result['passed'] else 1)

if __name__ == '__main__':
    main()
