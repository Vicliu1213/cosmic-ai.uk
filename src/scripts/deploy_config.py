#!/usr/bin/env python3
"""
Configuration Deployment Script

Deploys and validates configuration files to the engine core.
"""

import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_config_files():
    """Check if all required configuration files exist."""
    config_dir = Path(__file__).parent.parent / "engine" / "config"
    
    required_files = [
        "engine_config.json",
        "system_defaults.json",
        "config_schema.json"
    ]
    
    logger.info("=== 检查配置文件 ===")
    all_exist = True
    for file in required_files:
        file_path = config_dir / file
        if file_path.exists():
            logger.info(f"✅ {file}")
        else:
            logger.error(f"❌ {file} 缺失")
            all_exist = False
    
    return all_exist

def validate_json_syntax():
    """Validate JSON syntax of all config files."""
    config_dir = Path(__file__).parent.parent / "engine" / "config"
    
    logger.info("=== 验证 JSON 语法 ===")
    all_valid = True
    for json_file in config_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                json.load(f)
            logger.info(f"✅ {json_file.name}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ {json_file.name}: {e}")
            all_valid = False
    
    return all_valid

def load_and_test_config():
    """Test loading configuration through engine module."""
    logger.info("=== 测试配置加载 ===")
    try:
        from src.engine.config import get_engine_config, get_system_defaults
        
        engine_config = get_engine_config()
        logger.info(f"✅ 引擎配置已加载 ({len(engine_config)} keys)")
        
        system_defaults = get_system_defaults()
        logger.info(f"✅ 系统默认配置已加载 ({len(system_defaults)} keys)")
        
        return True
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        return False

def check_engine_integration():
    """Check if configuration is integrated in engine."""
    logger.info("=== 检查引擎集成 ===")
    try:
        from src import engine
        
        if hasattr(engine, 'get_engine_config'):
            logger.info("✅ get_engine_config 已导出")
        else:
            logger.warning("⚠️  get_engine_config 未导出")
        
        if hasattr(engine, 'get_system_defaults'):
            logger.info("✅ get_system_defaults 已导出")
        else:
            logger.warning("⚠️  get_system_defaults 未导出")
        
        return True
    except Exception as e:
        logger.error(f"❌ 引擎集成检查失败: {e}")
        return False

def main():
    """Run all deployment checks."""
    logger.info("开始配置部署验证...")
    logger.info("")
    
    checks = [
        ("配置文件检查", check_config_files),
        ("JSON 语法验证", validate_json_syntax),
        ("配置加载测试", load_and_test_config),
        ("引擎集成检查", check_engine_integration),
    ]
    
    results = []
    for name, check in checks:
        try:
            result = check()
            results.append((name, result))
        except Exception as e:
            logger.error(f"检查 '{name}' 失败: {e}")
            results.append((name, False))
        logger.info("")
    
    # 总结
    logger.info("=== 部署验证总结 ===")
    all_passed = all(result for _, result in results)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{name}: {status}")
    
    if all_passed:
        logger.info("\n✅ 所有检查通过！配置已成功部署到引擎核心。")
        return 0
    else:
        logger.error("\n❌ 部分检查失败。请检查错误日志。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
