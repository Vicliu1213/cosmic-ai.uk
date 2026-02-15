#!/usr/bin/env python3
"""
Skill Configuration Converter
統一的 Skill 格式轉換工具，支持 OpenCode, Claude, Cursor, CodeLaw
"""

import json
import yaml
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class Platform(Enum):
    """支援的平臺"""
    OPENCODE = "opencode"
    CLAUDE = "claude"
    CURSOR = "cursor"
    CODELAW = "codelaw"


@dataclass
class UnifiedSkill:
    """統一的 Skill 定義格式"""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    license: str = "MIT"
    categories: Optional[List[str]] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}


class SkillConverter:
    """Skill 配置轉換器"""
    
    # 名稱驗證規則
    NAME_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    
    def __init__(self, unified_skill: UnifiedSkill):
        """初始化轉換器
        
        Args:
            unified_skill: 統一的 Skill 定義
        """
        self.skill = unified_skill
        self._validate_skill()
    
    def _validate_skill(self):
        """驗證 Skill 定義的有效性"""
        if not self.NAME_PATTERN.match(self.skill.id):
            raise ValueError(
                f"Invalid skill ID: {self.skill.id}. "
                "Must be lowercase alphanumeric with hyphens only."
            )
        
        if not (1 <= len(self.skill.description) <= 1024):
            raise ValueError(
                f"Description length must be 1-1024 characters, "
                f"got {len(self.skill.description)}"
            )
    
    def to_opencode_skill(self) -> str:
        """轉換為 OpenCode SKILL.md 格式
        
        Returns:
            OpenCode SKILL.md 內容
        """
        frontmatter = {
            "name": self.skill.id,
            "description": self.skill.description,
            "license": self.skill.license,
            "compatibility": "opencode",
            "metadata": {
                "version": self.skill.version,
                "categories": self.skill.categories or [],
                **(self.skill.metadata or {})
            }
        }
        
        yaml_str = yaml.dump(frontmatter, default_flow_style=False)
        
        # 構建 Markdown 內容
        content = f"""---
{yaml_str}---

## What I do

{self._format_capabilities()}

## When to use me

Use this skill for: {', '.join(self.skill.categories) if self.skill.categories else 'general tasks'}

## Details

- **Name**: {self.skill.name}
- **Version**: {self.skill.version}
- **License**: {self.skill.license}
"""
        return content
    
    def to_claude_tool(self) -> Dict[str, Any]:
        """轉換為 Claude Tool 定義
        
        Returns:
            Claude Tool 定義字典
        """
        tool_name = self._to_snake_case(self.skill.id)
        
        tool_def = {
            "name": tool_name,
            "description": self.skill.description,
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        # 添加元數據為額外的文檔
        if self.skill.metadata:
            tool_def["metadata"] = self.skill.metadata
        
        if self.skill.categories:
            tool_def["tags"] = self.skill.categories
        
        return tool_def
    
    def to_cursor_rules(self) -> Dict[str, Any]:
        """轉換為 Cursor 配置規則
        
        Returns:
            Cursor 規則定義
        """
        command_id = self._to_camel_case(self.skill.id)
        
        return {
            "cursor.commands": [
                {
                    "id": f"opencode.{command_id}",
                    "title": self.skill.name,
                    "description": self.skill.description,
                    "category": self._get_primary_category(),
                }
            ],
            "cursor.keybindings": [
                {
                    "key": "ctrl+shift+o",
                    "command": f"opencode.{command_id}",
                    "when": "editorTextFocus"
                }
            ]
        }
    
    def to_codelaw_rules(self) -> List[Dict[str, Any]]:
        """轉換為 CodeLaw 規則定義
        
        Returns:
            CodeLaw 規則列表
        """
        rules = []
        
        for idx, capability in enumerate(self.skill.capabilities or [], 1):
            rule = {
                "id": f"{self.skill.id}-rule-{idx:03d}",
                "name": capability,
                "description": f"{self.skill.description} - {capability}",
                "applies_to": ["code", "functions"],
                "severity": self._determine_severity(),
                "enabled": True,
                "tags": self.skill.categories
            }
            rules.append(rule)
        
        # 如果沒有 capabilities，至少添加一個基本規則
        if not rules:
            rules.append({
                "id": f"{self.skill.id}-rule-001",
                "name": self.skill.name,
                "description": self.skill.description,
                "applies_to": ["code"],
                "severity": "warning",
                "enabled": True,
                "tags": self.skill.categories
            })
        
        return rules
    
    def to_unified_yaml(self) -> str:
        """轉換為統一的 YAML 格式
        
        Returns:
            統一 YAML 定義
        """
        unified_def = {
            "schema_version": "1.0",
            "metadata": {
                "id": self.skill.id,
                "name": self.skill.name,
                "description": self.skill.description,
                "version": self.skill.version,
                "license": self.skill.license,
                "categories": self.skill.categories,
            },
            "platforms": {
                "opencode": {
                    "enabled": True,
                    "path": f".opencode/skills/{self.skill.id}/SKILL.md",
                    "compatibility": "opencode"
                },
                "claude": {
                    "enabled": True,
                    "function_name": self._to_snake_case(self.skill.id),
                    "module": f"skills.{self.skill.id}"
                },
                "cursor": {
                    "enabled": True,
                    "command_id": f"opencode.{self._to_camel_case(self.skill.id)}",
                    "keybinding": "ctrl+shift+o"
                },
                "codelaw": {
                    "enabled": True,
                    "rule_id": f"{self.skill.id}-rule",
                    "severity": self._determine_severity()
                }
            },
            "capabilities": self.skill.capabilities,
            "metadata_extra": self.skill.metadata
        }
        
        return yaml.dump(unified_def, default_flow_style=False, sort_keys=False)
    
    def save_all(self, output_dir: Path):
        """將所有格式保存到文件
        
        Args:
            output_dir: 輸出目錄
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存 OpenCode SKILL.md
        opencode_dir = output_dir / "opencode" / self.skill.id
        opencode_dir.mkdir(parents=True, exist_ok=True)
        (opencode_dir / "SKILL.md").write_text(self.to_opencode_skill())
        
        # 保存 Claude Tool JSON
        claude_dir = output_dir / "claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        (claude_dir / f"{self.skill.id}.json").write_text(
            json.dumps(self.to_claude_tool(), indent=2)
        )
        
        # 保存 Cursor 規則
        cursor_dir = output_dir / "cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        (cursor_dir / f"{self.skill.id}.json").write_text(
            json.dumps(self.to_cursor_rules(), indent=2)
        )
        
        # 保存 CodeLaw 規則
        codelaw_dir = output_dir / "codelaw"
        codelaw_dir.mkdir(parents=True, exist_ok=True)
        (codelaw_dir / f"{self.skill.id}.yaml").write_text(
            yaml.dump(self.to_codelaw_rules(), default_flow_style=False)
        )
        
        # 保存統一 YAML
        (output_dir / f"{self.skill.id}-unified.yaml").write_text(
            self.to_unified_yaml()
        )
    
    # 工具方法
    
    @staticmethod
    def _to_snake_case(name: str) -> str:
        """轉換為 snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace('-', '_')
    
    @staticmethod
    def _to_camel_case(name: str) -> str:
        """轉換為 camelCase"""
        components = name.split('-')
        return components[0].lower() + ''.join(x.title() for x in components[1:])
    
    def _format_capabilities(self) -> str:
        """格式化能力列表"""
        if not self.skill.capabilities:
            return "- General purpose functionality"
        return '\n'.join(f"- {cap}" for cap in self.skill.capabilities)
    
    def _get_primary_category(self) -> str:
        """獲取主類別"""
        if self.skill.categories:
            return self.skill.categories[0].title()
        return "General"
    
    def _determine_severity(self) -> str:
        """根據類別確定 CodeLaw 嚴重性級別"""
        if not self.skill.categories:
            return "warning"
        
        category = self.skill.categories[0].lower()
        if "critical" in category or "security" in category:
            return "error"
        elif "warning" in category or "deprecated" in category:
            return "warning"
        return "info"


def parse_opencode_skill(skill_md_path: str) -> UnifiedSkill:
    """解析 OpenCode SKILL.md 為統一格式
    
    Args:
        skill_md_path: SKILL.md 文件路徑
        
    Returns:
        統一的 Skill 定義
    """
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析 YAML 前置部分
    if content.startswith('---'):
        _, frontmatter_str, _ = content.split('---', 2)
        frontmatter = yaml.safe_load(frontmatter_str)
    else:
        raise ValueError("Invalid SKILL.md format: missing YAML frontmatter")
    
    return UnifiedSkill(
        id=frontmatter.get('name'),
        name=frontmatter.get('name', '').title(),
        description=frontmatter.get('description'),
        version=frontmatter.get('metadata', {}).get('version', '1.0.0'),
        license=frontmatter.get('license', 'MIT'),
        categories=frontmatter.get('metadata', {}).get('categories', []),
        metadata=frontmatter.get('metadata', {})
    )


if __name__ == "__main__":
    # 示例用法
    example_skill = UnifiedSkill(
        id="git-release",
        name="Git Release",
        description="Create consistent releases and changelogs",
        version="1.0.0",
        license="MIT",
        categories=["devops", "github"],
        capabilities=[
            "Draft release notes from merged PRs",
            "Propose a version bump",
            "Generate copy-pasteable gh commands"
        ],
        metadata={
            "audience": "maintainers",
            "workflow": "github"
        }
    )
    
    converter = SkillConverter(example_skill)
    
    # 生成所有格式
    print("=" * 50)
    print("OpenCode SKILL.md")
    print("=" * 50)
    print(converter.to_opencode_skill())
    
    print("\n" + "=" * 50)
    print("Claude Tool Definition")
    print("=" * 50)
    print(json.dumps(converter.to_claude_tool(), indent=2))
    
    print("\n" + "=" * 50)
    print("Cursor Rules")
    print("=" * 50)
    print(json.dumps(converter.to_cursor_rules(), indent=2))
    
    print("\n" + "=" * 50)
    print("CodeLaw Rules")
    print("=" * 50)
    print(yaml.dump(converter.to_codelaw_rules(), default_flow_style=False))
    
    # 保存到文件
    output_dir = Path("./skill_outputs")
    converter.save_all(output_dir)
    print(f"\nAll formats saved to {output_dir}")
