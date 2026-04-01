#!/usr/bin/env python3
"""
ConfigManager - Configuration Loading and Validation Utility
配置管理器 - 配置加載和驗證實用程序

This module provides a comprehensive configuration management system for the
Cosmic Intelligence System, including YAML loading, type validation, parameter
range checking, environment variable overrides, and configuration merging.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class ConfigProfile(Enum):
    """Configuration profile types."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


@dataclass
class ParameterConstraint:
    """Constraint information for a configuration parameter."""
    name: str
    expected_type: Union[type, Tuple[type, ...]]
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    description: str = ""
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        """Validate a value against this constraint.
        
        Args:
            value: The value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Type check
        if not isinstance(value, self.expected_type):
            return False, f"Expected {self.expected_type}, got {type(value).__name__}"
        
        # Allowed values check
        if self.allowed_values is not None and value not in self.allowed_values:
            return False, f"Value {value} not in allowed values: {self.allowed_values}"
        
        # Range check
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                return False, f"Value {value} is less than minimum {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"Value {value} is greater than maximum {self.max_value}"
        
        return True, ""


class ConfigManager:
    """
    Comprehensive configuration manager for Cosmic Intelligence System.
    
    Features:
    - Load YAML configuration files
    - Type validation and range checking
    - Environment variable overrides
    - Configuration merging (base + custom + env)
    - Parameter documentation extraction
    - Configuration validation and error reporting
    """
    
    def __init__(self, config_dir: str = "config", env_prefix: str = "COSMIC_"):
        """Initialize ConfigManager.
        
        Args:
            config_dir: Base configuration directory path
            env_prefix: Prefix for environment variable overrides
        """
        self.config_dir = Path(config_dir)
        self.env_prefix = env_prefix
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._constraints: Dict[str, List[ParameterConstraint]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        
    def load_config(self, system_name: str, config_file: str,
                   profile: Optional[str] = None,
                   merge_env: bool = True) -> Dict[str, Any]:
        """Load configuration from YAML file with optional environment overrides.
        
        Args:
            system_name: Name of the system (for caching)
            config_file: Path to YAML config file (relative to config_dir)
            profile: Optional profile name to load (conservative/balanced/aggressive)
            merge_env: Whether to merge environment variable overrides
            
        Returns:
            Loaded configuration dictionary
            
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If YAML is invalid
        """
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {config_path}: {e}")
        
        if config is None:
            config = {}
        
        # Extract metadata (comments)
        self._extract_metadata(config_path, system_name)
        
        # Load profile if specified
        if profile:
            config = self._load_profile(config, profile)
        
        # Apply environment variable overrides
        if merge_env:
            config = self._merge_environment_variables(config, system_name)
        
        # Cache the configuration
        self._configs[system_name] = config
        
        logger.info(f"Loaded configuration for {system_name} from {config_path}")
        return config
    
    def load_all_systems(self, merge_env: bool = True) -> Dict[str, Dict[str, Any]]:
        """Load all system configurations.
        
        Returns:
            Dictionary mapping system names to their configurations
        """
        systems = {
            # Original 7 Systems / 原始 7 個系統
            'quantum_state': 'core/quantum_state_config.yaml',
            'hybrid_quantum': 'services/hybrid_quantum_config.yaml',
            'quantum_optimization': 'optimization/quantum_algorithm_config.yaml',
            'singularity_universe': 'systems/singularity_universe_config.yaml',
            'intelligent_time_travel': 'systems/intelligent_time_travel_config.yaml',
            'immortal_perpetual': 'systems/immortal_perpetual_config.yaml',
            'universal_quintenary': 'systems/universal_quintenary_cosmic_config.yaml',
            
            # New 12 Engine Configurations / 新增 12 個引擎配置
            'code_cleaning': 'engines/code_cleaning_config.yaml',
            'ultimate_gain': 'engines/ultimate_gain_config.yaml',
            'opencode_evolution': 'engines/opencode_evolution_config.yaml',
            'immortal_engine': 'engines/immortal_perpetual_config.yaml',
            'qft_engine': 'engines/qft_config.yaml',
            'synergy_engine': 'engines/synergy_config.yaml',
            'advanced_computing': 'engines/advanced_computing_config.yaml',
            'breakthrough_detector': 'engines/breakthrough_detector_config.yaml',
            'enhanced_classical': 'engines/enhanced_classical_config.yaml',
            'ray_distributed': 'engines/ray_distributed_config.yaml',
            'immune_reconfig': 'engines/immune_reconfig_config.yaml',
            'meta_synergy': 'engines/meta_synergy_config.yaml',
        }
        
        all_configs = {}
        for system_name, config_file in systems.items():
            try:
                all_configs[system_name] = self.load_config(
                    system_name, config_file, merge_env=merge_env
                )
            except Exception as e:
                logger.error(f"Failed to load {system_name}: {e}")
                all_configs[system_name] = None
        
        return all_configs
    
    def validate_config(self, system_name: str, config: Dict[str, Any],
                       constraints: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str]]:
        """Validate configuration against constraints.
        
        Args:
            system_name: Name of the system
            config: Configuration dictionary to validate
            constraints: Optional constraint definitions
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Recursive validation
        def validate_dict(d: Dict[str, Any], path: str = "") -> None:
            for key, value in d.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, dict):
                    validate_dict(value, current_path)
                elif isinstance(value, list):
                    for idx, item in enumerate(value):
                        if isinstance(item, dict):
                            validate_dict(item, f"{current_path}[{idx}]")
                else:
                    # Check constraints if available
                    if constraints and current_path in constraints:
                        constraint = constraints[current_path]
                        is_valid, error_msg = constraint.validate(value)
                        if not is_valid:
                            errors.append(f"{current_path}: {error_msg}")
        
        validate_dict(config)
        
        return len(errors) == 0, errors
    
    def get_value(self, system_name: str, path: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation path.
        
        Args:
            system_name: System name
            path: Dot-notation path (e.g., "quantum_state.coherence_target")
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        if system_name not in self._configs:
            return default
        
        config = self._configs[system_name]
        keys = path.split('.')
        
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return default
        
        return config
    
    def set_value(self, system_name: str, path: str, value: Any) -> None:
        """Set a configuration value by dot-notation path.
        
        Args:
            system_name: System name
            path: Dot-notation path
            value: Value to set
        """
        if system_name not in self._configs:
            self._configs[system_name] = {}
        
        config = self._configs[system_name]
        keys = path.split('.')
        
        # Navigate/create nested structure
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        logger.info(f"Set {system_name}.{path} = {value}")
    
    def get_config(self, system_name: str) -> Optional[Dict[str, Any]]:
        """Get cached configuration for a system.
        
        Args:
            system_name: System name
            
        Returns:
            Configuration dictionary or None
        """
        return self._configs.get(system_name)
    
    def export_config(self, system_name: str, output_file: str) -> None:
        """Export configuration to a new YAML file.
        
        Args:
            system_name: System name
            output_file: Output file path
        """
        if system_name not in self._configs:
            raise ValueError(f"System {system_name} not loaded")
        
        config = self._configs[system_name]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True,
                     sort_keys=False)
        
        logger.info(f"Exported {system_name} configuration to {output_file}")
    
    def compare_configs(self, system1: str, system2: str) -> Dict[str, Any]:
        """Compare two configurations and return differences.
        
        Args:
            system1: First system name
            system2: Second system name
            
        Returns:
            Dictionary with differences
        """
        config1 = self._configs.get(system1, {})
        config2 = self._configs.get(system2, {})
        
        differences = {
            'only_in_1': {},
            'only_in_2': {},
            'different_values': {},
        }
        
        def compare_dicts(d1: Dict, d2: Dict, path: str = "") -> None:
            all_keys = set(d1.keys()) | set(d2.keys())
            
            for key in all_keys:
                current_path = f"{path}.{key}" if path else key
                
                if key not in d2:
                    differences['only_in_1'][current_path] = d1[key]
                elif key not in d1:
                    differences['only_in_2'][current_path] = d2[key]
                elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    compare_dicts(d1[key], d2[key], current_path)
                elif d1[key] != d2[key]:
                    differences['different_values'][current_path] = {
                        system1: d1[key],
                        system2: d2[key],
                    }
        
        compare_dicts(config1, config2)
        
        return differences
    
    def get_documentation(self, system_name: str) -> Dict[str, str]:
        """Get extracted documentation for a system.
        
        Args:
            system_name: System name
            
        Returns:
            Dictionary mapping parameter paths to documentation
        """
        return self._metadata.get(system_name, {})
    
    def _extract_metadata(self, config_path: Path, system_name: str) -> None:
        """Extract metadata (comments) from YAML file.
        
        Args:
            config_path: Path to config file
            system_name: System name for storing metadata
        """
        metadata = {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_key = ""
            current_comment = []
            
            for line in lines:
                stripped = line.strip()
                
                # Skip empty lines
                if not stripped:
                    continue
                
                # Check for comment
                if stripped.startswith('#'):
                    comment_text = stripped[1:].strip()
                    if comment_text:
                        current_comment.append(comment_text)
                else:
                    # Check for key-value
                    if ':' in stripped and not stripped.startswith('-'):
                        key = stripped.split(':')[0].strip()
                        if current_comment:
                            metadata[key] = ' '.join(current_comment)
                            current_comment = []
        
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {config_path}: {e}")
        
        self._metadata[system_name] = metadata
    
    def _load_profile(self, config: Dict[str, Any], profile: str) -> Dict[str, Any]:
        """Load a specific profile from configuration.
        
        Args:
            config: Base configuration
            profile: Profile name (conservative/balanced/aggressive)
            
        Returns:
            Configuration with profile applied
        """
        # Find and apply profile settings
        for section_key, section_value in config.items():
            if isinstance(section_value, dict) and 'profiles' in section_value:
                profiles = section_value['profiles']
                if isinstance(profiles, dict) and profile in profiles:
                    profile_config = profiles[profile]
                    # Merge profile settings into section
                    if isinstance(profile_config, dict):
                        for k, v in profile_config.items():
                            section_value[k] = v
        
        return config
    
    def _merge_environment_variables(self, config: Dict[str, Any],
                                    system_name: str) -> Dict[str, Any]:
        """Merge environment variable overrides into configuration.
        
        Environment variables should follow pattern:
        COSMIC_{SYSTEM_NAME}_{SECTION}_{KEY}=value
        
        Args:
            config: Base configuration
            system_name: System name
            
        Returns:
            Configuration with env vars merged
        """
        prefix = f"{self.env_prefix}{system_name.upper()}_"
        
        for env_key, env_value in os.environ.items():
            if not env_key.startswith(prefix):
                continue
            
            # Extract path from env var name
            path = env_key[len(prefix):].lower()
            
            # Parse value (try to convert to appropriate type)
            try:
                if env_value.lower() in ('true', 'false'):
                    parsed_value = env_value.lower() == 'true'
                elif env_value.isdigit():
                    parsed_value = int(env_value)
                else:
                    try:
                        parsed_value = float(env_value)
                    except ValueError:
                        parsed_value = env_value
            except Exception:
                parsed_value = env_value
            
            # Set in config
            self.set_value(system_name, path, parsed_value)
            logger.info(f"Applied env override: {env_key} = {parsed_value}")
        
        return config


class ConfigValidator:
    """Validator for configuration schemas."""
    
    @staticmethod
    def validate_number_range(value: Union[int, float],
                             min_val: Optional[Union[int, float]] = None,
                             max_val: Optional[Union[int, float]] = None) -> Tuple[bool, str]:
        """Validate a numeric value is within range.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if min_val is not None and value < min_val:
            return False, f"Value {value} is below minimum {min_val}"
        if max_val is not None and value > max_val:
            return False, f"Value {value} is above maximum {max_val}"
        return True, ""
    
    @staticmethod
    def validate_choice(value: Any, allowed: List[Any]) -> Tuple[bool, str]:
        """Validate value is in allowed list.
        
        Args:
            value: Value to validate
            allowed: List of allowed values
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value not in allowed:
            return False, f"Value {value} not in allowed values: {allowed}"
        return True, ""
    
    @staticmethod
    def validate_type(value: Any, expected_type: Union[type, Tuple[type, ...]]) -> Tuple[bool, str]:
        """Validate value is of expected type.
        
        Args:
            value: Value to validate
            expected_type: Expected type(s)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, expected_type):
            return False, f"Expected {expected_type}, got {type(value).__name__}"
        return True, ""


def main() -> None:
    """Example usage of ConfigManager."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize manager
    manager = ConfigManager(config_dir='config')
    
    # Load all configurations
    print("Loading all system configurations...")
    configs = manager.load_all_systems()
    
    for system_name, config in configs.items():
        if config:
            print(f"✅ {system_name}: {len(str(config))} chars")
        else:
            print(f"❌ {system_name}: Failed to load")
    
    # Example: Get specific value
    su_config = manager.get_config('singularity_universe')
    if su_config:
        max_agents = manager.get_value('singularity_universe',
                                      'singularity_universe.max_agents')
        print(f"\nSingularity Universe max_agents: {max_agents}")
    
    # Example: Compare configurations
    print("\n" + "="*60)
    print("Configuration Comparison: quantum_state vs hybrid_quantum")
    print("="*60)
    differences = manager.compare_configs('quantum_state', 'hybrid_quantum')
    
    if differences['different_values']:
        print("\nDifferent Values:")
        for path, values in differences['different_values'].items():
            print(f"  {path}:")
            for sys, val in values.items():
                print(f"    {sys}: {val}")


if __name__ == '__main__':
    main()
