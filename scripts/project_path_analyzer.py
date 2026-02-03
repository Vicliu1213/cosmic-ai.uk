#!/usr/bin/env python3
"""
完整項目路徑檢查和統計工具
"""

import os
import sys
import json
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import logging
import subprocess

class ProjectPathInspector:
    """項目路徑檢查器"""
    
    def __init__(self):
        self.project_root = Path("/root/comic_ai")
        self.logger = self.setup_logging()
        self.all_imports = set()
        
    def setup_logging(self) -> logging.Logger:
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        return logging.getLogger(__name__)
        
    def collect_all_imports(self) -> Dict[str, Any]:
        """收集所有Python文件的import語句"""
        self.logger.info("Collecting all Python imports...")
        
        import_map = {}
        
        # 查找所有Python文件
        py_files = list(self.project_root.glob("**/*.py"))
        
        for py_file in py_files:
            if 'venv' not in str(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    lines = content.split('\n')
                    file_imports = set()
                    
                    # 簡單的import分析
                    for line in lines:
                        line = line.strip()
                        if line.startswith(('import ', 'from ')):
                            # 提取import語句
                            if ' as ' in line:
                                import_part = line.split(' as ')[1].strip()
                            else:
                                import_part = line.split()[1].strip()
                            file_imports.add(import_part)
                            
                    import_map[py_file.name] = sorted(list(file_imports))
                        
                except Exception as e:
                    self.logger.warning(f"Failed to analyze {py_file}: {e}")
                    
        return {
            'total_files_analyzed': len(import_map),
            'all_imports': sorted(list(set().union(*import_map.values()))),
            'import_map': import_map
        }
        
    def check_completeness(self) -> Dict[str, Any]:
        """檢查項目完整性"""
        self.logger.info("Checking Project Completeness...")
        
        # 收集所有腳本和配置
        all_files = list(self.project_root.glob("**/*"))
        root_files = [f.name for f in all_files if f.is_file() and not f.name.startswith('.')]
        
        # 檢查必要文件
        required_files = {
            'core_scripts': [
                'cli.py',
                'stage1.py',
                'simple_cli.py',
                'demo_cli.py'
                'file_server.py'
            ],
            'setup_scripts': [
                'install.sh',
                'start_server.sh', 
                'start_data_container.sh'
            ],
            'config_files': [
                'main_system_config.yaml',
                'performance_config.yaml',
                'security_config.yaml',
                'network_config.yaml',
                'backup_config.yaml',
                'privacy_config.yaml',
                'optimization_config.yaml'
            ],
            'engine_modules': [
                'quantum_engine.py',
                'enhanced_classical.py',
                'immune_reconfig_engine.py',
                'advanced_computing.py',
                'breakthrough_detector.py'
            ],
            'optimization_modules': [
                'intelligent_compression_optimizer.py',
                'file_header_optimizer.py'
            ],
            'integration_scripts': [
                'auto_config_installer.py'
            ],
            'data_scripts': [
                'data_manager.py'
            ],
            'dashboard_scripts': [
                'app.py'
            ]
        }
        
        completeness_status = {}
        missing_files = []
        
        for category, files_list in required_files.items():
            category_files = []
            missing_files = []
            
            for req_file in files_list:
                file_path = self.project_root / req_file
                if file_path.exists():
                    category_files.append(req_file)
                else:
                    missing_files.append(f"{category}/{req_file}")
                    
            completeness_status[category] = {
                'required_files': files_list,
                'found_files': category_files,
                'missing_files': missing_files,
                'completeness_rate': len(category_files) / len(files_list)
            }
            
            if missing_files:
                missing_files.extend(missing_files)
                
        # 檢查主要文件
        main_files = [f for f in root_files if f in ['cli.py', 'stage1.py']]
        
        return {
            'completeness_status': completeness_status,
            'missing_files': missing_files,
            'total_files': len(root_files),
            'main_files_found': len(main_files),
            'main_files_total': len(main_files)
        }
        
    def check_connections(self) -> Dict[str, Any]:
        """檢查文件連接性"""
        self.logger.info("Checking file connections...")
        
        # 檢查主要文件是否正確引用彼此
        connections = {
            'cli_to_stage1': self.check_file_references('cli.py', 'stage1.py'),
            'cli_to_dashboard': self.check_file_references('cli.py', 'dashboard/app.py'),
            'stage1_to_engines': self.check_file_references('stage1.py', 'engine'),
            'config_integration': self.check_config_integration()
        }
        
        return connections
        
    def check_file_references(self, source_file: str, target_file: str) -> bool:
        """檢查文件引用"""
        try:
            source_path = self.project_root / source_file
            target_path = self.project_root / target_file
            
            if not source_path.exists() or not target_path.exists():
                return False
                
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 檢查是否引用目標文件
            return target_path.name in content
        except Exception as e:
            self.logger.warning(f"Failed to check {source_file} -> {target_file}: {e}")
            return False
            
    def check_config_integration(self) -> bool:
        """檢查配置集成"""
        main_config_files = [
            'main_system_config.yaml',
            'performance_config.yaml',
            'security_config.yaml',
            'network_config.yaml'
        ]
        
        for config_file in main_config_files:
            if not (self.project_root / config_file).exists():
                return False
                
        return True
        
    def create_comprehensive_backup(self) -> str:
        """創建綜合備份"""
        self.logger.info("Creating comprehensive backup...")
        
        # 生成備份目錄
        backup_dir = self.project_root / 'backups' / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 備份所有文件
        backup_log = []
        
        # 使用tar打包
        backup_file = backup_dir / "comic_ai_complete_backup.tar.gz"
        
        try:
            import tarfile
            
            with tarfile.open(backup_file, "w:gz") as tar:
                # 添加項目根文件到備份
                self.logger.info(f"Adding project root files to backup...")
                tar.add(backup_dir.name + "/", arcname="comic_ai")
                
                # 排除venv和臨時文件
                for item in self.project_root.iterdir():
                    if item.name not in ['venv', '.git', '.DS_Store', '__pycache__']:
                        full_path = item.path if hasattr(item, 'path') else item
                        tar.add(full_path.name, full_path)
                        
            # 添加所有主要目錄
            main_dirs = ['config', 'data', 'engine', 'dashboard', 'scripts', 'optimizer', 'logs']
            for dir_name in main_dirs:
                dir_path = self.project_root / dir_name
                if dir_path.exists():
                    self.logger.info(f"Adding {dir_name} directory to backup...")
                    tar.add(dir_path + "/", arcname=f"comic_ai_{dir_name}")
                    
            tar.close()
            
            backup_log.append(f"Created backup: {backup_file}")
            
            # 生成備份清單
            backup_list_file = backup_dir / "backup_contents.txt"
            with open(backup_list_file, 'w', encoding='utf-8') as f:
                f.write(f"Comic AI Comprehensive Backup\n")
                f"Created: {datetime.now().isoformat()}\n")
                f"Backup File: {backup_file}\n")
                f"Size: {os.path.getsize(backup_file)} bytes\n")
                
            self.logger.info(f"Backup completed: {backup_file}")
            
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return f"backup_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成綜合報告"""
        self.logger.info("Generating Comprehensive Report...")
        
        # 收集import分析
        import_analysis = self.collect_all_imports()
        
        # 檢查完整性
        completeness = self.check_completeness()
        
        # 檢查連接性
        connections = self.check_connections()
        
        # 創建綜合備份
        backup_file = self.create_comprehensive_backup()
        
        # 生成報告
        report_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'import_analysis': import_analysis,
            'completeness_check': completeness,
            'connection_check': connections,
            'backup_file': backup_file,
            'total_files_found': completeness['total_files'],
            'missing_files': completeness['missing_files'],
            'completeness_rate': completeness['completeness_rate']
        }
        
        # 保存JSON報告
        json_report = self.project_root / 'logs' / f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(json_report, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"JSON report saved to {json_report}")
        except Exception as e:
            self.logger.error(f"Failed to save JSON report: {e}")
            
        # 生成ASCII報告
        self.print_comprehensive_report(report_data)
        
        return report_data
        
    def print_comprehensive_report(self, report_data: Dict[str, Any]):
        """打印綜合報告"""
        print(f"""
╔══════════════════════════════════════════════════╗
║              🚀 Comic AI 綜合項目分析報告                    ║
╚═════════════════════════════════════════════║
║                                                              ║
║  📅 分析時間: {report_data['analysis_timestamp']}                        ║
║  📁 項目根目錄: {report_data['project_root']}             ║
║                                                              ║
╠═══════════════════════════════════════╝
        
📊 📈 統計分析
"""
        
        print(f"• 總文件數量: {report_data['total_files_found']}")
        print(f"• 缺失文件數量: {report_data['missing_files']}")
        print(f"• 完整性評分: {report_data['completeness_rate']:.1%}")
        
        if report_data['import_analysis']:
            print(f"• Python文件分析: {report_data['import_analysis']['total_files_analyzed']} 個文件")
            print(f"• 總imports: {len(report_data['import_analysis']['all_imports'])} 個不同的import語句")
        
        print(f"""
🔗  連接性檢查
""")
        
        connections = report_data['connection_check']
        for check_name, result in connections.items():
            status = "✅ 連接" if result else "❌ 未連接"
            print(f"• {check_name}: {status}")
        
        if report_data['backup_file']:
            print(f"""
💾 備份信息
• 備份文件: {report_data['backup_file']}
• 備份大小: {os.path.getsize(report_data['backup_file'], default=0)} bytes
""")
        
        print(f"""
🎯 建議操作
""")
        
        if report_data['missing_files'] > 0:
            print("1. 安裝缺失的必要文件")
        if not connections['config_integration']:
            print("2. 修復配置文件集成問題")
            
        completeness_rate = report_data['completeness_rate']
        
        if completeness_rate < 0.8:
            print("3. 重新生成缺失文件")
        elif completeness_rate < 0.9:
            print("4. 進行系統集成測試")
        else:
            print("5. 系統已基本完整，可正常使用")
            
        print("""
        使用 python scripts/comprehensive_analyzer.py 獲取詳細分析結果
        備份文件保存於: {report_data['backup_file']}
        """)
        
        print("╚═══════════════════════════════════════╝")

def main():
    """主函數"""
    inspector = ProjectPathInspector()
    report = inspector.generate_comprehensive_report()
    
    # 返回成功狀態
    if report['completeness_rate'] >= 0.7:
        print("🎉 項目分析完成！")
        sys.exit(0)
    else:
        print("⚠️  項目需要修復")
        sys.exit(1)

if __name__ == "__main__":
    main()
        
    def analyze_complete_project_structure(self) -> Dict[str, Any]:
        """分析完整項目結構"""
        self.logger.info("Analyzing Complete Project Structure...")
        
        # 檢查主要目錄
        main_dirs = {
            'config': self.project_root / 'config',
            'data': self.project_root / 'data',
            'engine': self.project_root / 'engine',
            'dashboard': self.project_root / 'dashboard',
            'scripts': self.project_root / 'scripts',
            'optimizer': self.project_root / 'optimizer',
            'logs': self.project_root / 'logs'
        }
        
        structure_analysis = {}
        
        for dir_name, dir_path in main_dirs.items():
            exists = dir_path.exists()
            readable = os.access(dir_path, os.R_OK) if exists else False
            writable = os.access(dir_path, os.W_OK) if exists else False
            
            # 檢查子目錄和文件
            subdirs = []
            files = []
            
            if exists:
                for item in dir_path.iterdir():
                    if item.is_dir():
                        subdirs.append(item.name)
                    elif item.is_file():
                        files.append(item.name)
                        
            structure_analysis[dir_name] = {
                'path': str(dir_path),
                'exists': exists,
                'readable': readable,
                'writable': writable,
                'subdirectories': sorted(subdirs),
                'files': sorted(files),
                'permissions': oct(os.stat(dir_path).st_mode)[-3:] if exists else None
            }
            
        # 檢查根目錄文件
        root_files = []
        for item in self.project_root.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                root_files.append({
                    'name': item.name,
                    'path': str(item),
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
                
        # 檢查腳本文件
        scripts = self.find_all_scripts()
        
        # 檢查配置文件
        configs = self.find_all_configs()
        
        # 檢查Python模組
        modules = self.find_python_modules()
        
        return {
            'root_directory': str(self.project_root),
            'main_directories': structure_analysis,
            'root_files': sorted(root_files, key=lambda x: x['name']),
            'scripts': scripts,
            'configs': configs,
            'python_modules': modules,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    def find_all_scripts(self) -> Dict[str, Any]:
        """查找所有腳本文件"""
        self.logger.info("Finding All Scripts...")
        
        script_files = []
        
        # 查找.sh文件
        sh_files = list(self.project_root.glob("**/*.sh"))
        for script in sh_files:
            relative_path = script.relative_to(self.project_root)
            script_files.append({
                'name': script.name,
                'path': str(script),
                'relative_path': str(relative_path),
                'type': 'shell',
                'executable': os.access(script, os.X_OK),
                'size': script.stat().st_size if script.exists() else 0,
                'modified': datetime.fromtimestamp(script.stat().st_mtime).isoformat()
            })
            
        # 查找Python腳本
        py_files = list(self.project_root.glob("**/*.py"))
        for script in py_files:
            if 'venv' not in str(script):  # 排除venv中的文件
                relative_path = script.relative_to(self.project_root)
                script_files.append({
                    'name': script.name,
                    'path': str(script),
                    'relative_path': str(relative_path),
                    'type': 'python',
                    'executable': os.access(script, os.X_OK),
                    'size': script.stat().st_size if script.exists() else 0,
                    'modified': datetime.fromtimestamp(script.stat().st_mtime).isoformat()
                })
                
        return {
            'total_count': len(script_files),
            'shell_scripts': [s for s in script_files if s['type'] == 'shell'],
            'python_scripts': [s for s in script_files if s['type'] == 'python'],
            'all_scripts': script_files
        }
        
    def find_all_configs(self) -> Dict[str, Any]:
        """查找所有配置文件"""
        self.logger.info("Finding All Configuration Files...")
        
        config_files = []
        
        # 查找YAML配置
        yaml_files = list(self.project_root.glob("**/*.yaml"))
        yaml_files.extend(list(self.project_root.glob("**/*.yml")))
        
        for config in yaml_files:
            relative_path = config.relative_to(self.project_root)
            config_files.append({
                'name': config.name,
                'path': str(config),
                'relative_path': str(relative_path),
                'type': 'yaml',
                'size': config.stat().st_size if config.exists() else 0,
                'modified': datetime.fromtimestamp(config.stat().st_mtime).isoformat()
            })
            
        # 查找JSON配置
        json_files = list(self.project_root.glob("**/*.json"))
        
        for config in json_files:
            relative_path = config.relative_to(self.project_root)
            config_files.append({
                'name': config.name,
                'path': str(config),
                'relative_path': str(relative_path),
                'type': 'json',
                'size': config.stat().st_size if config.exists() else 0,
                'modified': datetime.fromtimestamp(config.stat().st_mtime).isoformat()
            })
            
        # 查找環境文件
        env_files = list(self.project_root.glob("**/.env*"))
        
        for config in env_files:
            relative_path = config.relative_to(self.project_root)
            config_files.append({
                'name': config.name,
                'path': str(config),
                'relative_path': str(relative_path),
                'type': 'environment',
                'size': config.stat().st_size if config.exists() else 0,
                'modified': datetime.fromtimestamp(config.stat().st_mtime).isoformat()
            })
            
        return {
            'total_count': len(config_files),
            'yaml_configs': [c for c in config_files if c['type'] == 'yaml'],
            'json_configs': [c for c in config_files if c['type'] == 'json'],
            'env_files': [c for c in config_files if c['type'] == 'environment'],
            'all_configs': config_files
        }
        
    def find_python_modules(self) -> Dict[str, Any]:
        """查找Python模組"""
        self.logger.info("Finding All Python Modules...")
        
        python_modules = []
        
        # 查找主要Python文件（排除venv）
        py_files = list(self.project_root.glob("**/*.py"))
        
        for py_file in py_files:
            if 'venv' not in str(py_file):
                relative_path = py_file.relative_to(self.project_root)
                
                # 分析文件內容
                file_info = self.analyze_python_file(py_file)
                
                python_modules.append({
                    'name': py_file.name,
                    'path': str(py_file),
                    'relative_path': str(relative_path),
                    'size': py_file.stat().st_size if py_file.exists() else 0,
                    'lines': file_info['lines'],
                    'classes': file_info['classes'],
                    'functions': file_info['functions'],
                    'imports': file_info['imports'],
                    'docstrings': file_info['docstrings'],
                    'modified': datetime.fromtimestamp(py_file.stat().st_mtime).isoformat()
                })
                
        return {
            'total_count': len(python_modules),
            'all_modules': python_modules,
            'main_files': [m for m in python_modules if m['name'] in ['cli.py', 'stage1.py', 'app.py']],
            'engine_files': [m for m in python_modules if 'engine' in m['relative_path']],
            'config_files': [m for m in python_modules if 'config' in m['relative_path']],
            'script_files': [m for m in python_modules if 'script' in m['relative_path']]
        }
        
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """分析Python文件內容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\\n')
            classes = []
            functions = []
            imports = []
            docstrings = []
            
            # 簡單的語法分析
            in_class = False
            in_function = False
            in_docstring = False
            
            for line in lines:
                line = line.strip()
                
                # 檢查import語句
                if line.startswith(('import ', 'from ')) and not in_docstring:
                    imports.append(line)
                    
                # 檢查類定義
                if line.startswith('class ') and not in_docstring:
                    classes.append(line)
                    
                # 檢查函數定義
                if line.startswith(('def ', 'async def ')) and not in_docstring:
                    functions.append(line)
                    
                # 檢查docstring
                if '"""' in line or "'''" in line:
                    in_docstring = not in_docstring
                    
            return {
                'lines': len(lines),
                'classes': classes,
                'functions': functions,
                'imports': imports,
                'docstrings': docstrings
            }
        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {e}")
            return {
                'lines': 0,
                'classes': [],
                'functions': [],
                'imports': [],
                'docstrings': []
            }
            
    def check_installation_completeness(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """檢查安裝完整性"""
        self.logger.info("Checking Installation Completeness...")
        
        # 必需的腳本和配置
        required_components = {
            'setup_scripts': [
                'install.sh',
                'start_server.sh',
                'start_data_container.sh'
            ],
            'main_config': [
                'main_system_config.yaml'
            ],
            'python_main_modules': [
                'cli.py',
                'stage1.py',
                'dashboard/app.py'
            ],
            'core_engines': [
                'engine/quantum_engine.py',
                'engine/enhanced_classical.py',
                'engine/immune_reconfig_engine.py'
            ],
            'optimization_modules': [
                'optimizer/intelligent_compression_optimizer.py',
                'optimizer/file_header_optimizer.py'
            ],
            'data_management': [
                'data/data_manager.py'
            ]
        }
        
        completeness_status = {}
        missing_components = []
        
        for category, required_files in required_components.items():
            found_files = []
            missing_files = []
            
            for req_file in required_files:
                file_path = self.project_root / req_file
                if file_path.exists():
                    found_files.append(req_file)
                else:
                    missing_files.append(req_file)
                    
            completeness_status[category] = {
                'required': required_files,
                'found': found_files,
                'missing': missing_files,
                'completeness_rate': len(found_files) / len(required_files)
            }
            
            if missing_files:
                missing_components.extend([f"{category}/{file}" for file in missing_files])
                
        # 計算整體完整性
        all_required = sum(len(files) for files in required_components.values())
        all_found = sum(len(status['found']) for status in completeness_status.values())
        
        overall_completeness = {
            'category_status': completeness_status,
            'overall_completeness_rate': all_found / all_required if all_required > 0 else 0,
            'missing_components': missing_components,
            'is_complete': len(missing_components) == 0
        }
        
        return overall_completeness
        
    def check_security_permissions(self) -> Dict[str, Any]:
        """檢查安全和權限設置"""
        self.logger.info("Checking Security & Permissions...")
        
        security_check = {}
        permission_issues = []
        
        # 檢查文件權限
        critical_files = [
            'install.sh',
            'start_server.sh',
            'cli.py',
            'config/main_system_config.yaml'
        ]
        
        for file_name in critical_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                file_stat = file_path.stat()
                permissions = oct(file_stat.st_mode)[-3:]
                
                # 檢查腳本權限
                if file_name.endswith('.sh') and permissions != '755':
                    permission_issues.append({
                        'file': file_name,
                        'current': permissions,
                        'required': '755',
                        'issue': 'Script not executable'
                    })
                        
                # 檢查配置文件權限
                if file_name.endswith('.yaml') and permissions not in ['640', '644']:
                    permission_issues.append({
                        'file': file_name,
                        'current': permissions,
                        'required': '640/644',
                        'issue': 'Config permissions too open'
                    })
                        
        security_check['permission_issues'] = permission_issues
        security_check['security_score'] = max(0, 100 - len(permission_issues) * 20)
        
        return security_check
        
    def generate_path_map(self, analysis: Dict[str, Any]) -> str:
        """生成路徑地圖（ASCII藝術）"""
        path_map = f"""
Comic AI Project Path Map
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ROOT DIRECTORY: {analysis['root_directory']}

MAIN DIRECTORIES:
"""
        
        # 添加主要目錄
        main_dirs = analysis['main_directories']
        for dir_name, dir_info in main_dirs.items():
            status = "[OK]" if dir_info['exists'] else "[MISSING]"
            perms = dir_info['permissions'] or "N/A"
            path_map += f"  {dir_name}/ {status} ({perms})\\n"
            
        # 添加腳本信息
        scripts = analysis['scripts']
        path_map += f"""
SHELL SCRIPTS ({len(scripts['shell_scripts'])}):
"""
        for script in scripts['shell_scripts'][:5]:
            exec_status = "[EXEC]" if script['executable'] else "[NOEXEC]"
            path_map += f"  {script['name']} {exec_status}\\n"
            
        path_map += f"""
PYTHON SCRIPTS ({len(scripts['python_scripts'])}):
"""
        for script in scripts['python_scripts'][:5]:
            exec_status = "[EXEC]" if script['executable'] else "[NOEXEC]"
            path_map += f"  {script['name']} {exec_status}\\n"
            
        return path_map
        
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成綜合報告"""
        self.logger.info("Generating Comprehensive Report...")
        
        # 執行所有分析
        structure_analysis = self.analyze_complete_project_structure()
        completeness_check = self.check_installation_completeness(structure_analysis)
        security_check = self.check_security_permissions()
        
        # 生成路徑地圖
        path_map = self.generate_path_map(structure_analysis)
        
        # 生成統計摘要
        summary = {
            'analysis_timestamp': datetime.now().isoformat(),
            'project_root': structure_analysis['root_directory'],
            'total_files': len(structure_analysis['root_files']) + len(structure_analysis['scripts']['all_scripts']) + len(structure_analysis['python_modules']['all_modules']) + len(structure_analysis['configs']['all_configs']),
            'directories': len(structure_analysis['main_directories']),
            'shell_scripts': len(structure_analysis['scripts']['shell_scripts']),
            'python_scripts': len(structure_analysis['scripts']['python_scripts']),
            'config_files': len(structure_analysis['configs']['all_configs']),
            'completeness_rate': completeness_check['overall_completeness_rate'],
            'security_score': security_check['security_score'],
            'missing_components': completeness_check['missing_components'],
            'permission_issues': len(security_check['permission_issues'])
        }
        
        # 保存報告
        report_data = {
            'summary': summary,
            'structure_analysis': structure_analysis,
            'completeness_check': completeness_check,
            'security_check': security_check,
            'path_map': path_map
        }
        
        report_file = self.project_root / 'logs' / f"project_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Report saved to {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            
        # 輸出結果
        self.print_summary(summary, completeness_check, security_check)
        
        return report_data
        
    def print_summary(self, summary: Dict[str, Any], completeness: Dict[str, Any], security: Dict[str, Any]):
        """打印摘要信息"""
        print(f"""
=========================================
Comic AI Project Analysis Summary
=========================================
Analysis Time: {summary['analysis_timestamp']}
Project Root: {summary['project_root']}

File Statistics:
- Total Files: {summary['total_files']}
- Directories: {summary['directories']}
- Shell Scripts: {summary['shell_scripts']}
- Python Scripts: {summary['python_scripts']}
- Config Files: {summary['config_files']}

Quality Metrics:
- Installation Completeness: {summary['completeness_rate']:.1%}
- Security Score: {security['security_score']}/100
- Missing Components: {summary['missing_count']}

Status Indicators:
""")
        
        completeness_rate = completeness['overall_completeness_rate']
        security_score = security['security_score']
        missing_components = completeness.get('missing_components', [])
        permission_issues = security.get('permission_issues', [])
        
        if completeness_rate >= 0.9:
            print("  Installation: COMPLETE")
        elif completeness_rate >= 0.7:
            print("  Installation: MOSTLY COMPLETE")
        else:
            print("  Installation: INCOMPLETE")
            
        if security_score >= 90:
            print("  Security: SECURE")
        elif security_score >= 70:
            print("  Security: MODERATE")
        else:
            print("  Security: NEEDS ATTENTION")
            
        if missing_components:
            print("  Missing Components:")
            for component in missing_components[:5]:
                print(f"    - {component}")
        else:
            print("  All Required Components Present")
            
        if permission_issues:
            print("  Permission Issues:")
            for issue in permission_issues[:3]:
                print(f"    - {issue['file']}: {issue['issue']}")
        else:
            print("  File Permissions: Correct")
            
        print("""
Recommended Actions:
1. Install missing components
2. Fix file permission issues  
3. Verify all services are working
4. Check logs for detailed information

Run: python scripts/auto_config_installer.py
""")

def main():
    """主函數"""
    inspector = ProjectPathInspector()
    report = inspector.generate_comprehensive_report()
    
    # 返回退出代碼基於完整性
    if report['summary']['completeness_rate'] >= 0.8 and report['summary']['security_score'] >= 80:
        print("\\nProject analysis completed successfully!")
        sys.exit(0)
    else:
        print("\\nProject has issues that need attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()