#!/usr/bin/env python3
"""
.env File Generator for Cosmic AI Trading System
宇宙交易系統 - .env 文件生成器

Automatically generates categorized .env files from config/environments structure.
根據 config/environments 結構自動生成分類的 .env 文件。

Usage:
    python scripts/generate_env.py [--environment=development|staging|production|all]
    python scripts/generate_env.py --environment=development  # Generate development .env
    python scripts/generate_env.py --environment=all          # Generate all .env files
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class EnvGenerator:
    """Generate .env files from configuration"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.config_base = self.project_root / "config" / "environments"
        self.env_base = self.project_root / "env"
        self.environments = ["development", "staging", "production"]
    
    def load_config(self, environment: str) -> Dict[str, Any]:
        """Load configuration from config/environments/{environment}/config.json"""
        config_file = self.config_base / environment / "config.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def flatten_dict(self, data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, str]:
        """Flatten nested dictionary into environment variable format"""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}".upper() if parent_key else k.upper()
            
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, bool):
                items.append((new_key, str(v).lower()))
            elif v is None:
                items.append((new_key, ""))
            else:
                items.append((new_key, str(v)))
        
        return dict(items)
    
    def generate_env_content(self, environment: str, config: Dict[str, Any]) -> str:
        """Generate .env file content"""
        timestamp = datetime.now().isoformat()
        env_vars = self.flatten_dict(config)
        
        lines = [
            f"# Environment: {environment.upper()}",
            f"# Generated: {timestamp}",
            f"# Auto-generated from: config/environments/{environment}/config.json",
            "#",
            "# DO NOT COMMIT THIS FILE TO GIT",
            "# Add 'env/' to .gitignore",
            "",
        ]
        
        # Add environment-specific variables
        lines.append(f"# Core Configuration")
        lines.append(f"ENVIRONMENT={environment}")
        lines.append("")
        
        # Group variables by category
        categories = {}
        for key, value in sorted(env_vars.items()):
            category = key.split('_')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((key, value))
        
        for category in sorted(categories.keys()):
            lines.append(f"# {category.upper()} Configuration")
            for key, value in categories[category]:
                # Hide sensitive values
                if any(sensitive in key for sensitive in ['PASSWORD', 'KEY', 'SECRET', 'TOKEN']):
                    lines.append(f"{key}=<SET_YOUR_VALUE>")
                else:
                    lines.append(f"{key}={value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def write_env_file(self, environment: str, content: str) -> Path:
        """Write .env file to env/{environment}/.env"""
        env_dir = self.env_base / environment
        env_dir.mkdir(parents=True, exist_ok=True)
        
        env_file = env_dir / ".env"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make it readable only by owner
        os.chmod(env_file, 0o600)
        
        return env_file
    
    def generate(self, environment: Optional[str] = None, create_root_env: bool = True) -> Dict[str, Path]:
        """Generate .env files"""
        results = {}
        targets = [environment] if environment and environment != "all" else self.environments
        
        for env in targets:
            if env not in self.environments:
                print(f"⚠️  Skipping unknown environment: {env}")
                continue
            
            try:
                config = self.load_config(env)
                content = self.generate_env_content(env, config)
                env_file = self.write_env_file(env, content)
                results[env] = env_file
                print(f"✅ Generated: {env_file}")
            except Exception as e:
                print(f"❌ Failed to generate {env}: {e}")
        
        # Generate root .env from the first successful environment
        if create_root_env and results:
            try:
                first_env = list(results.keys())[0]
                config = self.load_config(first_env)
                root_content = self.generate_root_env_content(config)
                self.write_root_env_file(root_content)
                print(f"✅ Generated: {self.project_root / '.env'}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to generate root .env: {e}")
        
        return results
    
    def generate_root_env_content(self, config: Dict[str, Any]) -> str:
        """Generate global .env file content for root directory"""
        timestamp = datetime.now().isoformat()
        env_vars = self.flatten_dict(config)
        
        lines = [
            "# Cosmic AI Trading System - Global Environment Configuration",
            "# 宇宙交易系統 - 全局環境配置",
            "#",
            "# This is the global environment configuration file.",
            "# DO NOT COMMIT SENSITIVE DATA TO GIT!",
            "#",
            f"# Generated: {timestamp}",
            "",
        ]
        
        # Add all standard environment variables
        lines.extend([
            "# ============================================================================",
            "# Environment Selection",
            "# ============================================================================",
            "# Set to: development | staging | production",
            "ENVIRONMENT=development",
            "",
            "# ============================================================================",
            "# Core Configuration",
            "# ============================================================================",
        ])
        
        for key in ["DEBUG", "LOG_LEVEL"]:
            if key.lower() in [k.lower() for k in env_vars.keys()]:
                value = next(v for k, v in env_vars.items() if k.lower() == key.lower())
                lines.append(f"{key}={value}")
        
        lines.extend([
            "",
            "# ============================================================================",
            "# API Configuration",
            "# ============================================================================",
        ])
        
        api_keys = [k for k in env_vars.keys() if k.startswith("API_")]
        for key in sorted(api_keys):
            lines.append(f"{key}={env_vars[key]}")
        
        lines.extend([
            "",
            "# ============================================================================",
            "# Database Configuration",
            "# ============================================================================",
            "# For development: SQLite",
        ])
        
        db_keys = [k for k in env_vars.keys() if k.startswith("DATABASE_")]
        for key in sorted(db_keys):
            if "PASSWORD" in key:
                lines.append(f"{key}=<SET_YOUR_VALUE>")
            else:
                lines.append(f"{key}={env_vars[key]}")
        
        lines.extend([
            "",
            "# ============================================================================",
            "# Cache Configuration",
            "# ============================================================================",
        ])
        
        cache_keys = [k for k in env_vars.keys() if k.startswith("CACHE_")]
        for key in sorted(cache_keys):
            if "PASSWORD" in key:
                lines.append(f"{key}=<SET_YOUR_VALUE>")
            else:
                lines.append(f"{key}={env_vars[key]}")
        
        lines.extend([
            "",
            "# ============================================================================",
            "# SSL/TLS Certificate Configuration",
            "# ============================================================================",
            "SSL_ENABLED=false",
            "SSL_CERT_PATH=<SET_YOUR_VALUE>",
            "SSL_KEY_PATH=<SET_YOUR_VALUE>",
            "SSL_CA_PATH=<SET_YOUR_VALUE>",
            "SSL_VERIFY=true",
            "",
            "# ============================================================================",
            "# Authentication & Security",
            "# ============================================================================",
            "JWT_SECRET=<SET_YOUR_VALUE>",
            "JWT_ALGORITHM=HS256",
            "JWT_EXPIRATION_HOURS=24",
            "API_KEY=<SET_YOUR_VALUE>",
            "",
            "# ============================================================================",
            "# External Services",
            "# ============================================================================",
            "OPENAI_API_KEY=<SET_YOUR_VALUE>",
            "OPENAI_MODEL=gpt-4",
            "QISKIT_IBM_TOKEN=<SET_YOUR_VALUE>",
            "",
            "# ============================================================================",
            "# Logging Configuration",
            "# ============================================================================",
            "LOG_FORMAT=json",
            "LOG_OUTPUT=console",
            "LOG_FILE_PATH=logs/app.log",
            "LOG_MAX_BYTES=10485760",
            "LOG_BACKUP_COUNT=5",
            "",
            "# ============================================================================",
            "# Trading System Configuration",
            "# ============================================================================",
            "TRADING_MODE=backtest",
            "TRADING_SYMBOLS=BTC,ETH,USDT",
            "TRADING_INTERVAL=1h",
            "TRADING_LEVERAGE=1",
            "",
            "# ============================================================================",
            "# Performance & Monitoring",
            "# ============================================================================",
            "ENABLE_METRICS=true",
            "ENABLE_TRACING=true",
            "METRICS_PORT=9090",
            "TRACE_SAMPLE_RATE=0.1",
            "",
            "# ============================================================================",
            "# Development Tools",
            "# ============================================================================",
            "RELOAD_ON_CHANGE=true",
            "PROFILE_ENABLED=false",
            "TEST_MODE=false",
            "",
        ])
        
        return "\n".join(lines)
    
    def write_root_env_file(self, content: str) -> Path:
        """Write global .env file to project root"""
        env_file = self.project_root / ".env"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make it readable only by owner
        os.chmod(env_file, 0o600)
        
        return env_file
    
    def create_gitignore(self):
        """Create .gitignore for env directory"""
        gitignore_file = self.env_base / ".gitignore"
        content = """# Environment files - NEVER commit these!
.env
.env.local
.env.*.local

# But allow examples
!.env.example
!.env.example.*
"""
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created: {gitignore_file}")
    
    def create_readme(self):
        """Create README for env directory"""
        readme_file = self.env_base / "README.md"
        content = """# Environment Configuration

This directory contains environment-specific `.env` files.

## Structure

```
env/
├── development/
│   └── .env          # Development environment variables
├── staging/
│   └── .env          # Staging environment variables
├── production/
│   └── .env          # Production environment variables
├── shared/
│   └── .env          # Shared variables across all environments
├── .gitignore        # Prevents committing .env files
└── README.md         # This file
```

## Usage

### Load environment variables

```bash
# Development
export $(cat env/development/.env | xargs)

# Staging
export $(cat env/staging/.env | xargs)

# Production (be careful!)
export $(cat env/production/.env | xargs)
```

### In Python

```python
from dotenv import load_dotenv

# Load development environment
load_dotenv('env/development/.env')

# Load staging environment
load_dotenv('env/staging/.env')
```

## Security

⚠️  **IMPORTANT**: Never commit `.env` files to git!

- These files contain sensitive information (API keys, passwords, etc.)
- The `.gitignore` file in this directory prevents accidental commits
- Always use environment-specific files and never share them

## Generation

To regenerate `.env` files from configuration:

```bash
python scripts/generate_env.py --environment=development
python scripts/generate_env.py --environment=all
```

## Configuration Sources

`.env` files are auto-generated from:
- `config/environments/development/config.json`
- `config/environments/staging/config.json`
- `config/environments/production/config.json`

If you modify the configuration JSON files, regenerate the `.env` files using the generation script.
"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created: {readme_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate .env files from configuration"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production", "all"],
        default="all",
        help="Which environment(s) to generate"
    )
    
    args = parser.parse_args()
    
    try:
        generator = EnvGenerator()
        results = generator.generate(args.environment)
        
        if results:
            generator.create_gitignore()
            generator.create_readme()
            print(f"\n✅ Successfully generated {len(results)} environment file(s)")
        else:
            print("❌ No files generated")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
