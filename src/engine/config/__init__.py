"""
Engine Configuration Module

This module handles loading and validating engine configuration from JSON files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EngineConfigLoader:
    """Load and manage engine configuration from JSON files."""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent
        self.config_dir = Path(config_dir)
        self._cache = {}
    
    def load_config(self, name: str) -> Dict[str, Any]:
        """Load a configuration file by name."""
        if name in self._cache:
            return self._cache[name]
        
        config_file = self.config_dir / f"{name}.json"
        if not config_file.exists():
            logger.warning(f"Configuration file not found: {config_file}")
            return {}
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            self._cache[name] = config
            logger.info(f"Loaded configuration: {name}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse configuration file {config_file}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load configuration {name}: {e}")
            return {}
    
    def get_engine_config(self) -> Dict[str, Any]:
        """Get engine configuration."""
        return self.load_config("engine_config")
    
    def get_system_defaults(self) -> Dict[str, Any]:
        """Get system default configuration."""
        return self.load_config("system_defaults")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get configuration schema."""
        return self.load_config("config_schema")
    
    def validate_config(self, config: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> bool:
        """Validate configuration against schema."""
        try:
            import jsonschema
            if schema is None:
                schema = self.get_schema()
            jsonschema.validate(config, schema)
            return True
        except ImportError:
            logger.warning("jsonschema not installed, skipping validation")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

# Global loader instance
_loader = EngineConfigLoader()

def get_engine_config() -> Dict[str, Any]:
    """Get engine configuration."""
    return _loader.get_engine_config()

def get_system_defaults() -> Dict[str, Any]:
    """Get system defaults."""
    return _loader.get_system_defaults()

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration."""
    return _loader.validate_config(config)

__all__ = [
    'EngineConfigLoader',
    'get_engine_config',
    'get_system_defaults',
    'validate_config'
]
