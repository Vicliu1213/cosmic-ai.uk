#!/usr/bin/env python3
"""
代碼自動清洗與修復工具
Automatic Code Cleaning and Repair Tool

利用自主錯誤處理系統的錯誤字典進行代碼清洗
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CodeError:
    """代碼錯誤"""
    file_path: str
    line_number: int
    error_type: str
    error_message: str
    fix_strategy: str
    severity: str  # critical, high, medium, low

class CodeCleaningEngine:
    """代碼清洗引擎"""
    
    # 錯誤字典 - 對應 autonomous_error_handler.py 中的映射
    ERROR_CORRECTIONS: Dict[str, Dict[str, Any]] = {
        'type_hint_none': {
            'pattern': r'def\s+\w+\(([^)]*:\s*str\s*=\s*None[^)]*)\)',
            'replacement': lambda m: m.group(0).replace('str = None', 'Optional[str] = None'),
            'description': '修復 Optional 類型提示',
            'severity': 'high',
            'imports_needed': ['Optional']
        },
        'missing_return_type': {
            'pattern': r'def\s+\w+\([^)]*\)\s*:(?!\s*->\s*)',
            'replacement': lambda m: m.group(0).replace('):', ') -> None:') if ' -> ' not in m.group(0) else m.group(0),
            'description': '添加缺失的返回類型',
            'severity': 'medium',
            'imports_needed': []
        },
        'unbound_variable': {
            'pattern': r'except.*:.*return\s+(\w+)(?!\s*=)',
            'replacement': lambda m: f'except Exception as e:\n            {m.group(1)} = None  # 初始化\n            return {m.group(1)}',
            'description': '修復變數作用域問題',
            'severity': 'high',
            'imports_needed': []
        },
        'none_type_call': {
            'pattern': r'if\s+(\w+)\s*is\s*None:|if\s+not\s+(\w+):',
            'replacement': None,  # 需要上下文檢查
            'description': '修復 None 類型調用',
            'severity': 'critical',
            'imports_needed': []
        },
        'import_error': {
            'pattern': r'from\s+(\S+)\s+import\s+(\S+)',
            'replacement': None,  # 需要驗證
            'description': '修復導入錯誤',
            'severity': 'critical',
            'imports_needed': []
        }
    }
    
    def __init__(self):
        self.errors_found: List[CodeError] = []
        self.errors_fixed: List[CodeError] = []
        self.total_files_scanned = 0
        self.total_errors = 0
        
    def scan_file(self, file_path: str) -> List[CodeError]:
        """掃描單個文件中的 LSP 錯誤"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 檢查各種 LSP 錯誤
            errors.extend(self._check_type_hints(file_path, content, lines))
            errors.extend(self._check_optional_types(file_path, content, lines))
            errors.extend(self._check_return_types(file_path, content, lines))
            errors.extend(self._check_none_checks(file_path, content, lines))
            errors.extend(self._check_imports(file_path, content, lines))
            
        except Exception as e:
            print(f"❌ 掃描文件失敗 {file_path}: {str(e)}")
        
        return errors
    
    def _check_type_hints(self, file_path: str, content: str, lines: List[str]) -> List[CodeError]:
        """檢查類型提示問題"""
        errors = []
        
        # 查找 "str = None" 的模式
        for i, line in enumerate(lines, 1):
            if re.search(r':\s*str\s*=\s*None', line):
                errors.append(CodeError(
                    file_path=file_path,
                    line_number=i,
                    error_type='type_hint_none',
                    error_message='應使用 Optional[str] 而非 str = None',
                    fix_strategy='replace_with_optional',
                    severity='high'
                ))
        
        return errors
    
    def _check_optional_types(self, file_path: str, content: str, lines: List[str]) -> List[CodeError]:
        """檢查 Optional 類型問題"""
        errors = []
        
        # 查找 None 作為默認值但無 Optional 的參數
        for i, line in enumerate(lines, 1):
            if re.search(r'def\s+\w+\(.*=\s*None', line):
                if 'Optional' not in line:
                    param_match = re.search(r'(\w+):\s*([A-Za-z]+)\s*=\s*None', line)
                    if param_match:
                        errors.append(CodeError(
                            file_path=file_path,
                            line_number=i,
                            error_type='missing_optional',
                            error_message=f'參數 {param_match.group(1)} 應使用 Optional[{param_match.group(2)}]',
                            fix_strategy='wrap_with_optional',
                            severity='high'
                        ))
        
        return errors
    
    def _check_return_types(self, file_path: str, content: str, lines: List[str]) -> List[CodeError]:
        """檢查返回類型"""
        errors = []
        
        for i, line in enumerate(lines, 1):
            # 查找缺少返回類型的函數定義
            if re.search(r'^\s*def\s+\w+\([^)]*\)\s*:(?!\s*#.*->\s*)', line):
                # 排除 __init__ 等特殊方法
                if '__init__' not in line and '__' not in line:
                    errors.append(CodeError(
                        file_path=file_path,
                        line_number=i,
                        error_type='missing_return_type',
                        error_message='函數定義缺少返回類型',
                        fix_strategy='add_return_type',
                        severity='medium'
                    ))
        
        return errors
    
    def _check_none_checks(self, file_path: str, content: str, lines: List[str]) -> List[CodeError]:
        """檢查 None 類型檢查"""
        errors = []
        
        for i, line in enumerate(lines, 1):
            # 查找在 except 中使用未定義的變數
            if 'except' in line and i < len(lines) - 1:
                next_lines = '\n'.join(lines[i:min(i+5, len(lines))])
                if re.search(r'return\s+(\w+)(?!\s*=)', next_lines):
                    var_match = re.search(r'return\s+(\w+)(?!\s*=)', next_lines)
                    if var_match:
                        var_name = var_match.group(1)
                        # 檢查變數是否在異常處理前初始化
                        before_except = '\n'.join(lines[:i])
                        if var_name not in before_except:
                            errors.append(CodeError(
                                file_path=file_path,
                                line_number=i,
                                error_type='unbound_variable',
                                error_message=f'變數 {var_name} 未在異常處理前初始化',
                                fix_strategy='initialize_variable',
                                severity='critical'
                            ))
        
        return errors
    
    def _check_imports(self, file_path: str, content: str, lines: List[str]) -> List[CodeError]:
        """檢查導入錯誤"""
        errors = []
        
        # 查找可能不存在的導入
        import_patterns = [
            ('semantic_kernel.plugins', '不存在的模塊'),
            ('sklearn', '缺失的外部依賴'),
        ]
        
        for i, line in enumerate(lines, 1):
            for import_name, description in import_patterns:
                if import_name in line and 'import' in line:
                    errors.append(CodeError(
                        file_path=file_path,
                        line_number=i,
                        error_type='import_error',
                        error_message=f'{description}: {import_name}',
                        fix_strategy='add_try_except_import',
                        severity='high'
                    ))
        
        return errors
    
    def fix_error(self, error: CodeError) -> bool:
        """修復單個錯誤"""
        try:
            file_path = error.file_path
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if error.line_number > len(lines):
                return False
            
            line_idx = error.line_number - 1
            original_line = lines[line_idx]
            
            # 根據錯誤類型應用修復
            if error.error_type == 'type_hint_none':
                fixed_line = re.sub(
                    r':\s*str\s*=\s*None',
                    ': Optional[str] = None',
                    original_line
                )
                lines[line_idx] = fixed_line
                
            elif error.error_type == 'missing_optional':
                # 從參數提取類型信息
                param_match = re.search(r'(\w+):\s*([A-Za-z]+)\s*=\s*None', original_line)
                if param_match:
                    param_name = param_match.group(1)
                    param_type = param_match.group(2)
                    fixed_line = original_line.replace(
                        f'{param_name}: {param_type} = None',
                        f'{param_name}: Optional[{param_type}] = None'
                    )
                    lines[line_idx] = fixed_line
            
            elif error.error_type == 'unbound_variable':
                # 在函數開始處初始化變數
                var_name = re.search(r'return\s+(\w+)', original_line)
                if var_name:
                    var = var_name.group(1)
                    lines[line_idx] = f"        {var} = None  # 初始化\n" + original_line
            
            # 添加必要的導入
            imports_to_add = []
            if 'Optional' in ''.join(lines) and 'from typing import Optional' not in ''.join(lines):
                imports_to_add.append('Optional')
            
            if imports_to_add:
                lines = self._add_imports(lines, imports_to_add)
            
            # 寫回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            self.errors_fixed.append(error)
            return True
            
        except Exception as e:
            print(f"❌ 修復失敗 {error.file_path}:{error.line_number}: {str(e)}")
            return False
    
    def _add_imports(self, lines: List[str], imports: List[str]) -> List[str]:
        """添加導入語句"""
        # 找到導入部分的結束
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_end = i + 1
        
        # 確定 typing 導入的位置
        typing_import_idx = None
        for i in range(import_end):
            if 'from typing import' in lines[i]:
                typing_import_idx = i
                break
        
        if typing_import_idx is not None:
            # 添加到現有的 typing 導入
            for imp in imports:
                if imp not in lines[typing_import_idx]:
                    lines[typing_import_idx] = lines[typing_import_idx].rstrip()
                    if lines[typing_import_idx].endswith(','):
                        lines[typing_import_idx] += f' {imp},\n'
                    else:
                        lines[typing_import_idx] = lines[typing_import_idx].rstrip('\n')
                        lines[typing_import_idx] = lines[typing_import_idx].rstrip(')')
                        lines[typing_import_idx] += f', {imp})\n'
        else:
            # 創建新的 typing 導入
            new_import = f"from typing import {', '.join(imports)}\n"
            lines.insert(import_end, new_import)
        
        return lines
    
    def generate_report(self) -> Dict[str, Any]:
        """生成修復報告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_files_scanned': self.total_files_scanned,
            'total_errors_found': len(self.errors_found),
            'total_errors_fixed': len(self.errors_fixed),
            'success_rate': len(self.errors_fixed) / len(self.errors_found) if self.errors_found else 0,
            'errors_by_type': self._group_errors_by_type(),
            'errors_by_severity': self._group_errors_by_severity(),
        }
    
    def _group_errors_by_type(self) -> Dict[str, int]:
        """按類型分組錯誤"""
        groups = {}
        for error in self.errors_found:
            groups[error.error_type] = groups.get(error.error_type, 0) + 1
        return groups
    
    def _group_errors_by_severity(self) -> Dict[str, int]:
        """按嚴重程度分組錯誤"""
        groups = {}
        for error in self.errors_found:
            groups[error.severity] = groups.get(error.severity, 0) + 1
        return groups

def main():
    """主程序"""
    engine = CodeCleaningEngine()
    
    # 掃描所有 Python 文件
    project_root = Path('/workspaces/cosmic-ai.uk')
    target_files = [
        'src/core/singularity_trading_system.py',
        'src/core/enhanced_quantum_market_analyzer.py',
        'data/agents/intelligent_agents.py',
        'engine/ray_distributed_engine.py',
        'demo_singularity_simple.py',
    ]
    
    print("=" * 80)
    print("代碼自動清洗工具")
    print("Automatic Code Cleaning Tool")
    print("=" * 80)
    print()
    
    for file_name in target_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"📁 掃描: {file_name}")
            errors = engine.scan_file(str(file_path))
            engine.errors_found.extend(errors)
            engine.total_files_scanned += 1
            
            for error in errors:
                print(f"  ⚠️  [{error.severity}] {error.error_type} (行 {error.line_number})")
                print(f"     {error.error_message}")
    
    print()
    print("=" * 80)
    print(f"掃描完成: {engine.total_files_scanned} 個文件, 發現 {len(engine.errors_found)} 個錯誤")
    print("=" * 80)
    print()
    
    # 修復錯誤
    print("開始修復...")
    print()
    
    for i, error in enumerate(engine.errors_found, 1):
        print(f"[{i}/{len(engine.errors_found)}] 修復 {error.file_path}:{error.line_number}")
        if engine.fix_error(error):
            print(f"    ✅ 成功")
        else:
            print(f"    ❌ 失敗")
    
    print()
    print("=" * 80)
    
    # 生成報告
    report = engine.generate_report()
    print(f"修復報告:")
    print(f"  總掃描文件: {report['total_files_scanned']}")
    print(f"  發現錯誤: {report['total_errors_found']}")
    print(f"  修復錯誤: {report['total_errors_fixed']}")
    print(f"  成功率: {report['success_rate']:.1%}")
    print()
    print("按類型統計:")
    for error_type, count in report['errors_by_type'].items():
        print(f"  {error_type}: {count}")
    print()
    print("按嚴重程度統計:")
    for severity, count in report['errors_by_severity'].items():
        print(f"  {severity}: {count}")
    print()
    print("=" * 80)
    
    # 保存報告
    report_file = project_root / 'code_cleaning_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 報告已保存: {report_file}")

if __name__ == '__main__':
    main()
