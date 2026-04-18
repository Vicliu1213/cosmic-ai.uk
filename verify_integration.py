#!/usr/bin/env python3
"""
Cosmic AI System Integration Verification
宇宙智能體系統集成驗證
"""

import os
import sys
import yaml
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def run_command(cmd, description, cwd=None):
    """Run a command and return success status"""
    print(f"  ▶ {description}... ", end="", flush=True)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        if result.returncode == 0:
            print("✅")
            return True
        else:
            print(f"❌\n    Error: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ (timeout)")
        return False
    except Exception as e:
        print(f"❌\n    Error: {str(e)[:100]}")
        return False

def verify_files_exist():
    """Verify critical files exist"""
    print_header("1. VERIFYING CRITICAL FILES")
    
    required_files = [
        ("Main integration file", "/workspaces/cosmic-ai.uk/cosmic_engine/main.py"),
        ("Configuration file", "/workspaces/cosmic-ai.uk/cosmic_engine/config/cosmic_config.yaml"),
        ("Fault tolerance module", "/workspaces/cosmic-ai.uk/cosmic_engine/cosmic/fault_tolerance.py"),
        ("Error correction module", "/workspaces/cosmic-ai.uk/cosmic_engine/cosmic/error_correction.py"),
        ("Self-evolution module", "/workspaces/cosmic-ai.uk/cosmic_engine/cosmic/self_evolution.py"),
        ("FT integration test", "/workspaces/cosmic-ai.uk/cosmic_engine/tests/test_fault_tolerance_integration.py"),
        ("EC integration test", "/workspaces/cosmic-ai.uk/cosmic_engine/tests/test_error_correction_integration.py"),
        ("SE integration test", "/workspaces/cosmic-ai.uk/cosmic_engine/tests/test_self_evolution_integration.py"),
        ("Documentation", "/workspaces/cosmic-ai.uk/docs/SINGULARITY_UNIVERSE_ENHANCED.md"),
    ]
    
    results = []
    for name, filepath in required_files:
        exists = Path(filepath).exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {Path(filepath).name}")
        results.append(exists)
    
    return all(results)

def verify_python_syntax():
    """Verify Python syntax of all modules"""
    print_header("2. VERIFYING PYTHON SYNTAX")
    
    python_files = [
        "/workspaces/cosmic-ai.uk/cosmic_engine/main.py",
        "/workspaces/cosmic-ai.uk/cosmic_engine/cosmic/fault_tolerance.py",
        "/workspaces/cosmic-ai.uk/cosmic_engine/cosmic/error_correction.py",
        "/workspaces/cosmic-ai.uk/cosmic_engine/cosmic/self_evolution.py",
        "/workspaces/cosmic-ai.uk/cosmic_engine/tests/test_fault_tolerance_integration.py",
        "/workspaces/cosmic-ai.uk/cosmic_engine/tests/test_error_correction_integration.py",
        "/workspaces/cosmic-ai.uk/cosmic_engine/tests/test_self_evolution_integration.py",
    ]
    
    all_valid = True
    for filepath in python_files:
        success = run_command(
            f"python -m py_compile '{filepath}'",
            f"Checking {Path(filepath).name}",
            cwd="/workspaces/cosmic-ai.uk"
        )
        all_valid = all_valid and success
    
    return all_valid

def verify_yaml_config():
    """Verify YAML configuration is valid"""
    print_header("3. VERIFYING YAML CONFIGURATION")
    
    config_path = "/workspaces/cosmic-ai.uk/cosmic_engine/config/cosmic_config.yaml"
    print(f"  Loading: {Path(config_path).name}... ", end="", flush=True)
    
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        print("✅")
        
        # Check for required sections
        required_sections = ["fault_tolerance", "error_correction", "self_evolution"]
        print("\n  Required sections:")
        
        all_present = True
        for section in required_sections:
            present = section in config
            status = "✅" if present else "❌"
            print(f"    {status} {section}")
            all_present = all_present and present
        
        # Show configuration summary
        if all_present:
            print("\n  Configuration summary:")
            print(f"    Fault Tolerance:")
            print(f"      - Detection interval: {config['fault_tolerance'].get('detection_interval_ms')}ms")
            print(f"      - Isolation strategy: {config['fault_tolerance'].get('isolation_strategy')}")
            print(f"    Error Correction:")
            print(f"      - Code type: {config['error_correction'].get('code_type')}")
            print(f"      - Syndrome check: {config['error_correction'].get('syndrome_check_interval_ms')}ms")
            print(f"    Self-Evolution:")
            print(f"      - Learning algorithm: {config['self_evolution'].get('learning_algorithm')}")
            print(f"      - Exploration rate: {config['self_evolution'].get('exploration_rate')}")
        
        return all_present
    
    except Exception as e:
        print(f"❌\n    Error: {str(e)}")
        return False

def verify_imports():
    """Verify all module imports work"""
    print_header("4. VERIFYING MODULE IMPORTS")
    
    test_code = """
import sys
from pathlib import Path
sys.path.insert(0, '/workspaces/cosmic-ai.uk')
sys.path.insert(0, '/workspaces/cosmic-ai.uk/cosmic_engine')

try:
    from cosmic.fault_tolerance import FaultToleranceOrchestrator
    print("✅ Fault tolerance module")
except Exception as e:
    print(f"❌ Fault tolerance: {e}")

try:
    from cosmic.error_correction import QuantumErrorCorrectionEngine
    print("✅ Error correction module")
except Exception as e:
    print(f"❌ Error correction: {e}")

try:
    from cosmic.self_evolution import SelfEvolutionEngine
    print("✅ Self-evolution module")
except Exception as e:
    print(f"❌ Self-evolution: {e}")
"""
    
    try:
        result = subprocess.run(
            ["python", "-c", test_code],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/workspaces/cosmic-ai.uk"
        )
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"  ❌ Import verification failed: {e}")
        return False

def verify_documentation():
    """Verify documentation updates"""
    print_header("5. VERIFYING DOCUMENTATION UPDATES")
    
    doc_path = "/workspaces/cosmic-ai.uk/docs/SINGULARITY_UNIVERSE_ENHANCED.md"
    print(f"  Reading: {Path(doc_path).name}... ", end="", flush=True)
    
    try:
        with open(doc_path) as f:
            content = f.read()
        
        print("✅")
        
        # Check for new sections
        sections_to_check = [
            ("容錯拓撲系統", "Fault Tolerance System"),
            ("量子糾錯編碼系統", "Quantum Error Correction System"),
            ("自進化學習機制", "Self-Evolution Learning System"),
            ("三大系統集成架構", "Integration Architecture"),
        ]
        
        print("\n  Documentation sections:")
        all_present = True
        for section_cn, section_en in sections_to_check:
            present = section_cn in content
            status = "✅" if present else "❌"
            print(f"    {status} {section_cn}")
            all_present = all_present and present
        
        # Get file size
        size = len(content)
        lines = len(content.split('\n'))
        print(f"\n  Document stats:")
        print(f"    - Total lines: {lines}")
        print(f"    - Total size: {size:,} bytes")
        
        return all_present
    
    except Exception as e:
        print(f"❌\n    Error: {str(e)}")
        return False

def generate_summary():
    """Generate verification summary"""
    print_header("INTEGRATION VERIFICATION SUMMARY")
    
    checks = [
        ("Critical files exist", verify_files_exist()),
        ("Python syntax valid", verify_python_syntax()),
        ("YAML configuration valid", verify_yaml_config()),
        ("Module imports work", verify_imports()),
        ("Documentation updated", verify_documentation()),
    ]
    
    print("\n  Verification Results:")
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"    {status}: {check_name}")
    
    overall_status = all(result for _, result in checks)
    
    print(f"\n  {'='*60}")
    if overall_status:
        print("  ✅ ALL VERIFICATIONS PASSED - SYSTEM READY FOR TESTING")
    else:
        print("  ❌ SOME VERIFICATIONS FAILED - PLEASE REVIEW ABOVE")
    print(f"  {'='*60}\n")
    
    return overall_status

def main():
    """Main verification function"""
    print("\n" + "="*60)
    print("  COSMIC AI SYSTEM INTEGRATION VERIFICATION")
    print("  宇宙智能體系統集成驗證")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    overall_success = generate_summary()
    
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
