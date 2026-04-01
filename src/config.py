"""Configuration Module - Bridge to ConfigManager

This module provides a simple interface to the ConfigManager for use across
the cosmic-ai system.
"""

from src.config_manager import ConfigManager

# Initialize the global config manager instance
config = ConfigManager()

__all__ = ['config']
