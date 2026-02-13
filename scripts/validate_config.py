#!/usr/bin/env python3
"""
Configuration Validation Script
配置验证脚本

Validates all Comic AI configuration files, environment variables, and service connectivity.
"""

import os
import sys
import yaml
import socket
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"🔍 {title}")
    print(f"{'=' * 60}{Colors.END}\n")

def print_success(message: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message: str) -> None:
    """Print info message."""
    print(f"   {message}")

def check_yaml_files() -> Tuple[int, int]:
    """Check all YAML configuration files for syntax errors."""
    print_section("YAML Configuration Files")
    
    yaml_files = []
    yaml_files.extend(Path('config').glob('*.yaml'))
    yaml_files.extend(Path('.').glob('*.yaml'))
    yaml_files.extend(Path('dashboard').glob('*.yaml'))
    yaml_files.extend(Path('engine').glob('*.yaml'))
    
    valid_count = 0
    error_count = 0
    
    for yaml_file in sorted(set(str(f) for f in yaml_files)):
        if 'external' in yaml_file:
            continue
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            file_size = Path(yaml_file).stat().st_size / 1024
            print_success(f"{yaml_file} ({file_size:.1f}KB)")
            valid_count += 1
        except yaml.YAMLError as e:
            print_error(f"{yaml_file}: {str(e)[:100]}")
            error_count += 1
        except Exception as e:
            print_error(f"{yaml_file}: {str(e)[:100]}")
            error_count += 1
    
    print(f"\n{Colors.BLUE}Summary: {valid_count} valid, {error_count} errors{Colors.END}")
    return valid_count, error_count

def check_environment_variables() -> Tuple[int, int]:
    """Check critical environment variables."""
    print_section("Environment Variables")
    
    critical_vars = {
        'OPENAI_API_KEY': 'OpenAI API key',
        'GOOGLE_CLOUD_PROJECT': 'Google Cloud project ID',
        'VERTEX_AI_MODEL': 'Vertex AI model name',
        'BINANCE_API_KEY': 'Binance API key',
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
        'COMIC_AI_ENV': 'Comic AI environment',
        'DATABASE_PATH': 'Database file path',
        'REDIS_HOST': 'Redis hostname',
    }
    
    optional_vars = {
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI API key',
        'POLYGON_API_KEY': 'Polygon API key',
        'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage API key',
        'SLACK_WEBHOOK_URL': 'Slack webhook URL',
    }
    
    set_count = 0
    missing_critical = 0
    missing_optional = 0
    
    print("Critical Variables:")
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value:
            # Mask the value for security
            if len(value) > 15:
                masked = value[:5] + '*' * (len(value) - 10) + value[-5:]
            else:
                masked = '*' * len(value)
            print_success(f"{var}: {masked} - {description}")
            set_count += 1
        else:
            print_error(f"{var}: (not set) - {description}")
            missing_critical += 1
    
    print("\nOptional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if len(value) > 15:
                masked = value[:5] + '*' * (len(value) - 10) + value[-5:]
            else:
                masked = '*' * len(value)
            print_success(f"{var}: {masked} - {description}")
            set_count += 1
        else:
            print_warning(f"{var}: (not set) - {description}")
            missing_optional += 1
    
    print(f"\n{Colors.BLUE}Summary: {set_count} set, {missing_critical} critical missing, {missing_optional} optional missing{Colors.END}")
    return set_count, missing_critical

def check_service_connectivity() -> Tuple[int, int]:
    """Check connectivity to critical services."""
    print_section("Service Connectivity")
    
    services_ok = 0
    services_failed = 0
    
    # Check Redis
    print("Redis Cache Server (localhost:6379):")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        if result == 0:
            print_success("Redis is accessible")
            services_ok += 1
        else:
            print_error("Redis not responding")
            services_failed += 1
    except Exception as e:
        print_error(f"Redis check failed: {e}")
        services_failed += 1
    
    # Check SQLite Database
    print("\nSQLite Database:")
    db_path = Path(os.getenv('DATABASE_PATH', 'data/comic_ai.db'))
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            print_success(f"Database accessible at {db_path}")
            print_info(f"Tables: {len(tables)} found")
            if tables:
                print_info(f"Sample tables: {[t[0] for t in tables[:3]]}")
            services_ok += 1
        except Exception as e:
            print_error(f"Database error: {e}")
            services_failed += 1
    else:
        print_warning(f"Database file not found at {db_path} (may be initialized on first run)")
    
    # Check file permissions
    print("\nFile Permissions:")
    critical_paths = [
        'config/',
        'data/',
        '.env',
    ]
    
    for path in critical_paths:
        p = Path(path)
        if p.exists():
            if os.access(p, os.R_OK):
                print_success(f"{path}: readable")
                services_ok += 1
            else:
                print_error(f"{path}: not readable")
                services_failed += 1
        else:
            if path != '.env':
                print_warning(f"{path}: does not exist")
    
    print(f"\n{Colors.BLUE}Summary: {services_ok} OK, {services_failed} failed{Colors.END}")
    return services_ok, services_failed

def check_config_parameters() -> Tuple[int, int]:
    """Check specific configuration parameters."""
    print_section("Configuration Parameters")
    
    params_ok = 0
    params_error = 0
    
    # Load main config
    try:
        with open('config/main_system_config.yaml', 'r', encoding='utf-8') as f:
            main_config = yaml.safe_load(f)
        print_success("Main system config loaded")
        
        # Check key parameters
        checks = [
            ('environment', main_config.get('system', {}).get('environment')),
            ('version', main_config.get('system', {}).get('version')),
            ('max_workers', main_config.get('system', {}).get('max_workers')),
        ]
        
        for param_name, value in checks:
            if value:
                print_success(f"{param_name}: {value}")
                params_ok += 1
            else:
                print_warning(f"{param_name}: not configured")
        
    except Exception as e:
        print_error(f"Failed to load main config: {e}")
        params_error += 1
    
    # Check trading config
    try:
        with open('config/trading_config.yaml', 'r', encoding='utf-8') as f:
            trading_config = yaml.safe_load(f)
        print_success("Trading config loaded")
        
        if trading_config:
            max_positions = trading_config.get('risk_management', {}).get('max_positions')
            if max_positions:
                print_info(f"Max positions: {max_positions}")
                params_ok += 1
    except Exception as e:
        print_error(f"Failed to load trading config: {e}")
        params_error += 1
    
    # Check security config
    try:
        with open('config/security_config.yaml', 'r', encoding='utf-8') as f:
            security_config = yaml.safe_load(f)
        print_success("Security config loaded")
        
        if security_config:
            encryption = security_config.get('encryption', {}).get('algorithm')
            if encryption:
                print_info(f"Encryption: {encryption}")
                params_ok += 1
    except Exception as e:
        print_error(f"Failed to load security config: {e}")
        params_error += 1
    
    print(f"\n{Colors.BLUE}Summary: {params_ok} OK, {params_error} errors{Colors.END}")
    return params_ok, params_error

def check_security_status() -> Dict[str, bool]:
    """Check security-related configurations."""
    print_section("Security Status")
    
    checks = {
        'SSL_Certificate_Valid': False,
        'HTTPS_Configured': False,
        'API_Keys_In_Env': False,
        'gitignore_Excludes_env': False,
    }
    
    # Check SSL certificate
    cert_path = Path('/etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem')
    if cert_path.exists():
        print_success("SSL certificate found")
        checks['SSL_Certificate_Valid'] = True
    else:
        print_warning("SSL certificate not found")
    
    # Check HTTPS in config
    if os.getenv('SECURITY_SSL_CERT_PATH'):
        print_success("HTTPS configured")
        checks['HTTPS_Configured'] = True
    else:
        print_warning("HTTPS not configured")
    
    # Check .gitignore
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore = f.read()
        if '.env' in gitignore:
            print_success(".gitignore excludes .env files")
            checks['gitignore_Excludes_env'] = True
        else:
            print_error(".gitignore does NOT exclude .env files")
    except Exception as e:
        print_error(f"Failed to check .gitignore: {e}")
    
    # Check API keys are not hardcoded
    print_info("Checking for hardcoded API keys...")
    suspicious_files = []
    for py_file in Path('src').rglob('*.py'):
        try:
            content = py_file.read_text()
            if 'sk-' in content or 'OPENAI_API_KEY =' in content:
                suspicious_files.append(str(py_file))
        except:
            pass
    
    if not suspicious_files:
        print_success("No hardcoded API keys found in source code")
        checks['API_Keys_In_Env'] = True
    else:
        print_error(f"Potential hardcoded keys in: {suspicious_files}")
    
    print(f"\n{Colors.BLUE}Security Status Summary:{Colors.END}")
    for check, status in checks.items():
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"  {status_str}: {check}")
    
    return checks

def generate_report() -> Dict:
    """Generate complete validation report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'hostname': socket.gethostname(),
        'environment': os.getenv('COMIC_AI_ENV', 'unknown'),
        'sections': {}
    }
    
    # Run all checks
    yaml_valid, yaml_errors = check_yaml_files()
    env_set, env_missing = check_environment_variables()
    services_ok, services_failed = check_service_connectivity()
    params_ok, params_error = check_config_parameters()
    security_checks = check_security_status()
    
    report['sections']['yaml_files'] = {'valid': yaml_valid, 'errors': yaml_errors}
    report['sections']['environment'] = {'set': env_set, 'missing': env_missing}
    report['sections']['services'] = {'ok': services_ok, 'failed': services_failed}
    report['sections']['parameters'] = {'ok': params_ok, 'error': params_error}
    report['sections']['security'] = security_checks
    
    # Calculate overall status
    total_errors = yaml_errors + env_missing + services_failed + params_error
    report['overall_status'] = 'PASS' if total_errors == 0 else 'FAIL'
    report['total_checks'] = yaml_valid + env_set + services_ok + params_ok
    report['total_errors'] = total_errors
    
    return report

def main() -> int:
    """Main validation function."""
    print(f"\n{Colors.BLUE}{'*' * 60}")
    print("Comic AI - Configuration Validation Tool")
    print(f"{'*' * 60}{Colors.END}")
    
    try:
        # Change to project root if needed
        if not Path('config').exists():
            print_error("Script must be run from project root directory")
            return 1
        
        report = generate_report()
        
        # Print final summary
        print_section("Validation Summary")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Hostname: {report['hostname']}")
        print(f"Environment: {report['environment']}")
        print(f"\nTotal Checks Passed: {report['total_checks']}")
        print(f"Total Errors Found: {report['total_errors']}")
        
        if report['overall_status'] == 'PASS':
            print_success("Configuration validation PASSED")
            status_code = 0
        else:
            print_error("Configuration validation FAILED")
            status_code = 1
        
        # Save report to file
        report_path = Path('logs/validation_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nReport saved to: {report_path}")
        
        return status_code
        
    except Exception as e:
        print_error(f"Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
