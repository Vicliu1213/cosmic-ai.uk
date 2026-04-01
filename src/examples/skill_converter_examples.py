#!/usr/bin/env python3
"""
Skill Converter 使用指南和示例

此腳本展示如何使用 SkillConverter 進行跨平臺 Skill 轉換
"""

import sys
from pathlib import Path

# 添加項目根路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.skill_converter import UnifiedSkill, SkillConverter


def example_1_basic_conversion():
    """示例 1: 基本轉換流程"""
    print("=" * 70)
    print("示例 1: 基本 Skill 轉換")
    print("=" * 70)
    
    # 定義一個統一的 Skill
    skill = UnifiedSkill(
        id="database-migration",
        name="Database Migration Helper",
        description="Assist with database schema migrations and data transformations",
        version="1.2.0",
        license="Apache-2.0",
        categories=["database", "devops", "tools"],
        capabilities=[
            "Generate migration scripts",
            "Validate schema changes",
            "Rollback capabilities",
            "Data transformation templates"
        ],
        metadata={
            "audience": "backend-developers",
            "workflow": "database-operations",
            "supported_databases": ["postgresql", "mysql", "mongodb"]
        }
    )
    
    # 創建轉換器
    converter = SkillConverter(skill)
    
    # 生成 OpenCode 格式
    print("\n1. OpenCode SKILL.md:")
    print("-" * 70)
    print(converter.to_opencode_skill())
    
    # 生成 Claude 工具定義
    print("\n2. Claude Tool Definition:")
    print("-" * 70)
    import json
    print(json.dumps(converter.to_claude_tool(), indent=2))
    
    # 生成 Cursor 規則
    print("\n3. Cursor Rules:")
    print("-" * 70)
    print(json.dumps(converter.to_cursor_rules(), indent=2))
    
    # 生成 CodeLaw 規則
    print("\n4. CodeLaw Rules (First 2):")
    print("-" * 70)
    import yaml
    rules = converter.to_codelaw_rules()
    print(yaml.dump(rules[:2], default_flow_style=False))


def example_2_parsing_and_conversion():
    """示例 2: 解析現有 Skill 並進行轉換"""
    print("\n" + "=" * 70)
    print("示例 2: 解析 OpenCode Skill 並轉換到其他格式")
    print("=" * 70)
    
    # 創建示例 SKILL.md
    sample_skill_md = """---
name: api-testing
description: Comprehensive API testing and validation framework
license: MIT
compatibility: opencode
metadata:
  version: 1.0.0
  categories:
    - testing
    - api
    - quality-assurance
  audience: qa-engineers
  workflow: api-development
---

## What I do

- Generate comprehensive API tests
- Validate response schemas
- Performance testing utilities
- Error handling verification

## When to use me

Use this when developing REST APIs or webhooks.
Provides automated testing templates and best practices.
"""
    
    # 臨時保存文件
    temp_path = Path("/tmp/test_skill.md")
    temp_path.write_text(sample_skill_md)
    
    # 解析 Skill
    from src.utils.skill_converter import parse_opencode_skill
    try:
        skill = parse_opencode_skill(str(temp_path))
        converter = SkillConverter(skill)
        
        print("\nParsed Skill Information:")
        print(f"  ID: {skill.id}")
        print(f"  Name: {skill.name}")
        print(f"  Description: {skill.description}")
        print(f"  Categories: {', '.join(skill.categories or [])}")
        
        print("\nConverted to Claude Tool:")
        import json
        print(json.dumps(converter.to_claude_tool(), indent=2))
        
    finally:
        temp_path.unlink()


def example_3_batch_conversion():
    """示例 3: 批量轉換多個 Skill"""
    print("\n" + "=" * 70)
    print("示例 3: 批量轉換多個 Skills")
    print("=" * 70)
    
    skills_config = [
        {
            "id": "code-review",
            "name": "Code Review Assistant",
            "description": "AI-powered code review and quality analysis",
            "categories": ["quality", "ci-cd"],
            "capabilities": ["Static analysis", "Performance review", "Security check"]
        },
        {
            "id": "documentation-gen",
            "name": "Documentation Generator",
            "description": "Automatic API and code documentation generation",
            "categories": ["documentation", "devops"],
            "capabilities": ["API docs", "Code comments", "README generation"]
        },
        {
            "id": "performance-monitor",
            "name": "Performance Monitoring",
            "description": "Real-time application performance monitoring and profiling",
            "categories": ["monitoring", "devops"],
            "capabilities": ["Metrics collection", "Alerting", "Profiling"]
        }
    ]
    
    output_base = Path("/tmp/skill_batch_output")
    
    for skill_config in skills_config:
        skill = UnifiedSkill(
            id=skill_config["id"],
            name=skill_config["name"],
            description=skill_config["description"],
            categories=skill_config["categories"],
            capabilities=skill_config["capabilities"]
        )
        
        converter = SkillConverter(skill)
        output_dir = output_base / skill_config["id"]
        
        try:
            converter.save_all(output_dir)
            print(f"✓ Converted '{skill_config['id']}' to {output_dir}")
        except Exception as e:
            print(f"✗ Failed to convert '{skill_config['id']}': {e}")


def example_4_unified_yaml_format():
    """示例 4: 統一 YAML 格式用於跨平臺共享"""
    print("\n" + "=" * 70)
    print("示例 4: 統一 YAML 格式")
    print("=" * 70)
    
    skill = UnifiedSkill(
        id="security-scanner",
        name="Security Scanner",
        description="Comprehensive security vulnerability scanning and reporting",
        version="2.1.0",
        license="GPL-3.0",
        categories=["security", "devops"],
        capabilities=[
            "Vulnerability scanning",
            "Dependency analysis",
            "SBOM generation",
            "Report generation"
        ],
        metadata={
            "audience": "security-engineers",
            "compliance": ["SOC2", "PCI-DSS"],
            "supports_sbom": True
        }
    )
    
    converter = SkillConverter(skill)
    
    print("\nUnified YAML Format (for cross-platform sharing):")
    print("-" * 70)
    print(converter.to_unified_yaml())


def example_5_conversion_mapping():
    """示例 5: 轉換映射參考"""
    print("\n" + "=" * 70)
    print("示例 5: 字段轉換映射參考")
    print("=" * 70)
    
    mapping = """
OpenCode ↔ Claude ↔ Cursor ↔ CodeLaw 轉換映射

┌─────────────────────────────────────────────────────────────────┐
│ OpenCode SKILL.md                                               │
├─────────────────────────────────────────────────────────────────┤
│ name → Claude tool.name                                          │
│ description → Claude tool.description                            │
│ metadata.audience → Cursor category                              │
│ metadata.categories → CodeLaw tags                               │
│ capabilities → CodeLaw rules                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Claude Tool Definition                                          │
├─────────────────────────────────────────────────────────────────┤
│ name (snake_case) ← from OpenCode id                             │
│ description ← from OpenCode description                          │
│ input_schema ← from Claude-specific configs                      │
│ tags ← from OpenCode categories                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Cursor Configuration                                            │
├─────────────────────────────────────────────────────────────────┤
│ id (camelCase) ← from OpenCode id                                │
│ title ← from OpenCode name                                       │
│ description ← from OpenCode description                          │
│ category ← from OpenCode categories[0]                           │
│ keybinding ← 'ctrl+shift+o' (default)                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CodeLaw Rules                                                   │
├─────────────────────────────────────────────────────────────────┤
│ id ← from OpenCode id + '-rule-XXX'                              │
│ name ← from OpenCode capabilities                                │
│ description ← from OpenCode description                          │
│ severity ← determined from categories                            │
│ tags ← from OpenCode categories                                  │
└─────────────────────────────────────────────────────────────────┘
"""
    print(mapping)


def main():
    """運行所有示例"""
    print("\n" + "=" * 70)
    print("Skill 轉換工具使用示例")
    print("=" * 70)
    print("\n此腳本演示如何使用 SkillConverter 進行跨平臺轉換\n")
    
    try:
        example_1_basic_conversion()
        example_2_parsing_and_conversion()
        example_3_batch_conversion()
        example_4_unified_yaml_format()
        example_5_conversion_mapping()
        
        print("\n" + "=" * 70)
        print("所有示例完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
