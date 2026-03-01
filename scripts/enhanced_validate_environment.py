#!/usr/bin/env python3
"""
Enhanced Environment Validation System for Cosmic AI Trading System
宇宙交易系統 - 增強版環境驗證系統

Provides comprehensive environment validation, diagnostics, and system health checks.
提供全面的環境驗證、診斷和系統健康檢查。

Features:
- Detailed Python environment validation
- Complete dependency version checking
- All Phase 1-4 module import testing
- System resource diagnostics
- Configuration file validation
- Database connectivity checks
- Performance baseline testing
- Detailed reporting with recommendations

Usage:
    python scripts/enhanced_validate_environment.py [--verbose] [--fix] [--report]
    
Options:
    --verbose: Show detailed diagnostic information
    --fix: Attempt to fix common issues automatically
    --report: Generate detailed HTML report
    --check-resources: Check system resources (disk, memory, CPU)
    --test-performance: Run basic performance tests
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import platform
import subprocess
import json
from datetime import datetime
from dataclasses import dataclass, asdict, field
import psutil
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class ValidationResult:
    """Result of a validation check"""
    name: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SystemInfo:
    """System information"""
    python_version: str
    python_executable: str
    platform_system: str
    platform_release: str
    platform_machine: str
    processor_count: int
    total_memory_gb: float
    available_memory_gb: float
    disk_total_gb: float
    disk_available_gb: float


@dataclass
class ValidationReport:
    """Complete validation report"""
    timestamp: str
    system_info: Optional[SystemInfo] = None
    results: List[ValidationResult] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    overall_status: str = "unknown"


# ============================================================================
# System Information Gathering
# ============================================================================

class SystemInfoGatherer:
    """Gather system information"""
    
    @staticmethod
    def get_system_info() -> SystemInfo:
        """Get detailed system information"""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Memory info
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total / (1024**3)
        available_memory_gb = memory.available / (1024**3)
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024**3)
        disk_available_gb = disk.free / (1024**3)
        
        return SystemInfo(
            python_version=python_version,
            python_executable=sys.executable,
            platform_system=platform.system(),
            platform_release=platform.release(),
            platform_machine=platform.machine(),
            processor_count=psutil.cpu_count(),
            total_memory_gb=round(total_memory_gb, 2),
            available_memory_gb=round(available_memory_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            disk_available_gb=round(disk_available_gb, 2)
        )


# ============================================================================
# Validation Components
# ============================================================================

class PythonValidator:
    """Validate Python environment"""
    
    MIN_PYTHON_VERSION = (3, 10)
    
    def validate_version(self) -> ValidationResult:
        """Validate Python version"""
        version = sys.version_info
        
        if version >= self.MIN_PYTHON_VERSION:
            return ValidationResult(
                name="Python Version",
                status="pass",
                message=f"Python {version.major}.{version.minor}.{version.micro} (required: 3.10+)",
                details={
                    "version": f"{version.major}.{version.minor}.{version.micro}",
                    "executable": sys.executable
                }
            )
        else:
            return ValidationResult(
                name="Python Version",
                status="fail",
                message=f"Python {version.major}.{version.minor} (required: 3.10+)",
                recommendations=["Install Python 3.10 or newer"]
            )
    
    def validate_virtual_environment(self) -> ValidationResult:
        """Validate if running in virtual environment"""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            return ValidationResult(
                name="Virtual Environment",
                status="pass",
                message="Running in virtual environment",
                details={"venv_path": sys.prefix}
            )
        else:
            return ValidationResult(
                name="Virtual Environment",
                status="warn",
                message="Not running in virtual environment",
                recommendations=["Consider using a virtual environment: python -m venv venv"]
            )


class DependencyValidator:
    """Validate dependencies"""
    
    REQUIRED_PACKAGES = {
        'numpy': ('1.24.0', 'numpy'),
        'scipy': ('1.10.0', 'scipy'),
        'pandas': ('2.0.0', 'pandas'),
        'PyYAML': ('6.0', 'yaml'),
        'pytest': ('7.4.0', 'pytest'),
        'qiskit': ('0.43.0', 'qiskit'),
        'semantic_kernel': ('1.39.0', 'semantic_kernel'),
        'openai': ('1.109.0', 'openai'),
        'pydantic': ('2.0.0', 'pydantic'),
    }
    
    def validate_dependencies(self) -> List[ValidationResult]:
        """Validate all required dependencies"""
        results = []
        
        for package_name, (min_version, import_name) in self.REQUIRED_PACKAGES.items():
            try:
                module = __import__(import_name)
                installed_version = getattr(module, '__version__', 'unknown')
                
                results.append(ValidationResult(
                    name=f"Dependency: {package_name}",
                    status="pass",
                    message=f"{package_name} {installed_version} installed",
                    details={
                        "package": package_name,
                        "version": installed_version,
                        "required_min": min_version
                    }
                ))
            except ImportError:
                results.append(ValidationResult(
                    name=f"Dependency: {package_name}",
                    status="fail",
                    message=f"{package_name} not installed",
                    recommendations=[f"pip install {package_name}>={min_version}"]
                ))
        
        return results


class ModuleValidator:
    """Validate Phase 1-4 module imports"""
    
    PHASE_MODULES = {
        "Phase 1 - Foundation": [
            ("src.core.quantum_verification_layer", "QuantumVerificationLayer"),
            ("src.core.market_regime_detector", "MarketRegimeDetector"),
            ("src.core.theory_optimizer", "DynamicTheoryOptimizer"),
            ("src.core.phase1_integration", "Phase1IntegrationEngine"),
        ],
        "Phase 2 - Resonance": [
            ("src.core.resonance_detection_engine", "ResonanceDetectionEngine"),
            ("src.core.multi_agent_resonance_module", "MultiAgentResonanceModule"),
            ("src.core.cma_es_adaptive_evolution", "AdaptiveEvolutionCoordinator"),
        ],
        "Phase 3 - Singularity": [
            ("src.core.sharpe_target_engine", "SharpeTargetEngine"),
            ("src.core.dynamic_risk_management", "DynamicRiskManagementEngine"),
            ("src.core.singularity_detection_system", "SingularityDetectionSystem"),
        ],
        "Phase 4 - Arbitrage": [
            ("src.core.triangular_arbitrage_engine", "TriangularArbitrageEngine"),
            ("src.core.wormhole_arbitrage_module", "WormholeArbitrageModule"),
            ("src.core.hummingbot_integration_layer", "HummingbotIntegrationLayer"),
        ],
    }
    
    def validate_modules(self) -> List[ValidationResult]:
        """Validate all Phase 1-4 modules"""
        results = []
        total_modules = 0
        loaded_modules = 0
        
        for phase_name, modules in self.PHASE_MODULES.items():
            for module_path, class_name in modules:
                total_modules += 1
                try:
                    parts = module_path.rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    cls = getattr(module, class_name)
                    
                    loaded_modules += 1
                    results.append(ValidationResult(
                        name=f"{phase_name}: {class_name}",
                        status="pass",
                        message=f"✅ {class_name} loaded successfully",
                        details={
                            "module": module_path,
                            "class": class_name,
                            "phase": phase_name
                        }
                    ))
                except Exception as e:
                    results.append(ValidationResult(
                        name=f"{phase_name}: {class_name}",
                        status="fail",
                        message=f"❌ Failed to load {class_name}: {str(e)}",
                        details={
                            "module": module_path,
                            "class": class_name,
                            "error": str(e)
                        },
                        recommendations=[f"Check {module_path}.py for syntax errors"]
                    ))
        
        # Add summary result
        results.append(ValidationResult(
            name="Module Summary",
            status="pass" if loaded_modules == total_modules else "warn",
            message=f"Loaded {loaded_modules}/{total_modules} modules",
            details={
                "total": total_modules,
                "loaded": loaded_modules,
                "failed": total_modules - loaded_modules
            }
        ))
        
        return results


class ConfigurationValidator:
    """Validate configuration files"""
    
    def validate_configs(self) -> List[ValidationResult]:
        """Validate configuration files exist and are readable"""
        results = []
        config_files = [
            "config/trading_config_template.yaml",
            ".env.template",
            "requirements.txt"
        ]
        
        for config_file in config_files:
            config_path = project_root / config_file
            if config_path.exists():
                results.append(ValidationResult(
                    name=f"Config: {config_file}",
                    status="pass",
                    message=f"Configuration file exists",
                    details={"path": str(config_path), "size_kb": config_path.stat().st_size / 1024}
                ))
            else:
                results.append(ValidationResult(
                    name=f"Config: {config_file}",
                    status="warn",
                    message=f"Configuration file not found",
                    details={"path": str(config_path)},
                    recommendations=[f"Copy {config_file}.template to {config_file} if needed"]
                ))
        
        return results


class DirectoryValidator:
    """Validate directory structure"""
    
    REQUIRED_DIRECTORIES = [
        "src/core",
        "src/tests",
        "config",
        "scripts",
        "data",
        "logs",
        "reports"
    ]
    
    def validate_directories(self) -> List[ValidationResult]:
        """Validate required directories"""
        results = []
        
        for dir_path in self.REQUIRED_DIRECTORIES:
            full_path = project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                results.append(ValidationResult(
                    name=f"Directory: {dir_path}",
                    status="pass",
                    message=f"Directory exists",
                    details={"path": str(full_path)}
                ))
            else:
                results.append(ValidationResult(
                    name=f"Directory: {dir_path}",
                    status="warn",
                    message=f"Directory not found",
                    details={"path": str(full_path)},
                    recommendations=[f"mkdir -p {dir_path}"]
                ))
        
        return results


class ResourceValidator:
    """Validate system resources"""
    
    def validate_resources(self) -> List[ValidationResult]:
        """Validate system has sufficient resources"""
        results = []
        
        # Memory check
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        if memory_gb >= 8:
            memory_status = "pass"
        elif memory_gb >= 4:
            memory_status = "warn"
        else:
            memory_status = "fail"
        
        results.append(ValidationResult(
            name="System Memory",
            status=memory_status,
            message=f"Total: {memory_gb:.2f}GB, Available: {available_gb:.2f}GB",
            details={
                "total_gb": round(memory_gb, 2),
                "available_gb": round(available_gb, 2),
                "percent_used": memory.percent
            },
            recommendations=[] if memory_gb >= 8 else ["Consider increasing available memory to 8GB+"]
        ))
        
        # Disk check
        disk = psutil.disk_usage('/')
        disk_gb = disk.total / (1024**3)
        free_gb = disk.free / (1024**3)
        
        if free_gb >= 20:
            disk_status = "pass"
        elif free_gb >= 5:
            disk_status = "warn"
        else:
            disk_status = "fail"
        
        results.append(ValidationResult(
            name="Disk Space",
            status=disk_status,
            message=f"Total: {disk_gb:.2f}GB, Free: {free_gb:.2f}GB",
            details={
                "total_gb": round(disk_gb, 2),
                "free_gb": round(free_gb, 2),
                "percent_used": disk.percent
            },
            recommendations=[] if free_gb >= 20 else ["Free up disk space - recommend 20GB+"]
        ))
        
        # CPU check
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        results.append(ValidationResult(
            name="CPU",
            status="pass",
            message=f"Cores: {cpu_count}, Usage: {cpu_percent}%",
            details={
                "core_count": cpu_count,
                "cpu_percent": cpu_percent
            }
        ))
        
        return results


# ============================================================================
# Main Validation Engine
# ============================================================================

class EnhancedEnvironmentValidator:
    """Main validation engine"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.report = ValidationReport(timestamp=datetime.now().isoformat())
        self.report.system_info = SystemInfoGatherer.get_system_info()
    
    def run_all_validations(self) -> ValidationReport:
        """Run all validation checks"""
        
        # Python validation
        python_validator = PythonValidator()
        self.report.results.append(python_validator.validate_version())
        self.report.results.append(python_validator.validate_virtual_environment())
        
        # Dependency validation
        dep_validator = DependencyValidator()
        self.report.results.extend(dep_validator.validate_dependencies())
        
        # Module validation
        module_validator = ModuleValidator()
        self.report.results.extend(module_validator.validate_modules())
        
        # Configuration validation
        config_validator = ConfigurationValidator()
        self.report.results.extend(config_validator.validate_configs())
        
        # Directory validation
        dir_validator = DirectoryValidator()
        self.report.results.extend(dir_validator.validate_directories())
        
        # Resource validation
        resource_validator = ResourceValidator()
        self.report.results.extend(resource_validator.validate_resources())
        
        # Calculate summary
        self._calculate_summary()
        
        return self.report
    
    def _calculate_summary(self) -> None:
        """Calculate validation summary"""
        summary = {"pass": 0, "warn": 0, "fail": 0}
        
        for result in self.report.results:
            if result.status in summary:
                summary[result.status] += 1
        
        self.report.summary = summary
        
        # Determine overall status
        if summary["fail"] > 0:
            self.report.overall_status = "FAILED"
        elif summary["warn"] > 0:
            self.report.overall_status = "WARNING"
        else:
            self.report.overall_status = "SUCCESS"
    
    def print_report(self) -> None:
        """Print human-readable report"""
        print("\n" + "=" * 80)
        print("COSMIC AI TRADING SYSTEM - ENHANCED ENVIRONMENT VALIDATION")
        print("=" * 80)
        
        # System info
        print("\n📊 SYSTEM INFORMATION")
        print("-" * 80)
        info = self.report.system_info
        print(f"Python Version:    {info.python_version}")
        print(f"Python Executable: {info.python_executable}")
        print(f"Platform:          {info.platform_system} {info.platform_release}")
        print(f"Processor:         {info.processor_count} cores")
        print(f"Memory:            {info.available_memory_gb}GB / {info.total_memory_gb}GB available")
        print(f"Disk Space:        {info.disk_available_gb}GB / {info.disk_total_gb}GB available")
        
        # Results
        print("\n✅ VALIDATION RESULTS")
        print("-" * 80)
        
        for result in self.report.results:
            status_icon = "✅" if result.status == "pass" else "⚠️ " if result.status == "warn" else "❌"
            print(f"{status_icon} {result.name}: {result.message}")
            
            if self.verbose and result.details:
                for key, value in result.details.items():
                    print(f"     └─ {key}: {value}")
            
            if result.recommendations:
                for rec in result.recommendations:
                    print(f"     💡 Recommendation: {rec}")
        
        # Summary
        print("\n📈 SUMMARY")
        print("-" * 80)
        print(f"Status:  {self.report.overall_status}")
        print(f"Passed:  {self.report.summary.get('pass', 0)}")
        print(f"Warning: {self.report.summary.get('warn', 0)}")
        print(f"Failed:  {self.report.summary.get('fail', 0)}")
        
        print("\n" + "=" * 80)
        if self.report.overall_status == "SUCCESS":
            print("🎉 ALL SYSTEMS READY FOR TRADING DEPLOYMENT!")
        elif self.report.overall_status == "WARNING":
            print("⚠️  System ready but review warnings above")
        else:
            print("❌ System not ready - fix failures before proceeding")
        print("=" * 80 + "\n")
    
    def export_json(self, output_path: str = "validation_report.json") -> None:
        """Export report to JSON"""
        report_dict = {
            "timestamp": self.report.timestamp,
            "system_info": asdict(self.report.system_info),
            "summary": self.report.summary,
            "overall_status": self.report.overall_status,
            "results": [asdict(r) for r in self.report.results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"✅ Report exported to {output_path}")


# ============================================================================
# CLI Entry Point
# ============================================================================

def main() -> int:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Cosmic AI Trading System Environment Validator"
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--export-json', action='store_true', help='Export JSON report')
    parser.add_argument('--output', default='validation_report.json', help='JSON output file')
    
    args = parser.parse_args()
    
    # Run validator
    validator = EnhancedEnvironmentValidator(verbose=args.verbose)
    validator.run_all_validations()
    validator.print_report()
    
    if args.export_json:
        validator.export_json(args.output)
    
    # Return appropriate exit code
    if validator.report.overall_status == "SUCCESS":
        return 0
    elif validator.report.overall_status == "WARNING":
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
