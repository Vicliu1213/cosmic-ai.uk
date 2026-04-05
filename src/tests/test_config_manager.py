#!/usr/bin/env python3
"""
Test suite for ConfigManager
配置管理器測試套件

Comprehensive tests for configuration loading, validation, merging,
and environment variable handling.
"""

import os
import sys
import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import (
    ConfigManager, ConfigValidator, ParameterConstraint, ConfigProfile
)


class TestParameterConstraint:
    """Test ParameterConstraint validation."""
    
    def test_type_validation_valid(self):
        """Test valid type validation."""
        constraint = ParameterConstraint(
            name="max_agents",
            expected_type=int
        )
        is_valid, msg = constraint.validate(50)
        assert is_valid, msg
    
    def test_type_validation_invalid(self):
        """Test invalid type validation."""
        constraint = ParameterConstraint(
            name="max_agents",
            expected_type=int
        )
        is_valid, msg = constraint.validate("50")
        assert not is_valid
        assert "Expected" in msg
    
    def test_range_validation_min(self):
        """Test minimum value validation."""
        constraint = ParameterConstraint(
            name="coherence_target",
            expected_type=float,
            min_value=0.9,
            max_value=0.999
        )
        is_valid, msg = constraint.validate(0.85)
        assert not is_valid
        assert "minimum" in msg
    
    def test_range_validation_max(self):
        """Test maximum value validation."""
        constraint = ParameterConstraint(
            name="coherence_target",
            expected_type=float,
            min_value=0.9,
            max_value=0.999
        )
        is_valid, msg = constraint.validate(1.0)
        assert not is_valid
        assert "maximum" in msg
    
    def test_range_validation_valid(self):
        """Test valid range validation."""
        constraint = ParameterConstraint(
            name="coherence_target",
            expected_type=float,
            min_value=0.9,
            max_value=0.999
        )
        is_valid, msg = constraint.validate(0.95)
        assert is_valid, msg
    
    def test_allowed_values_validation(self):
        """Test allowed values validation."""
        constraint = ParameterConstraint(
            name="framework",
            expected_type=str,
            allowed_values=["semantic_kernel", "autogen", "crewai"]
        )
        is_valid, msg = constraint.validate("semantic_kernel")
        assert is_valid
        
        is_valid, msg = constraint.validate("invalid_framework")
        assert not is_valid
        assert "allowed values" in msg


class TestConfigManager:
    """Test ConfigManager functionality."""

    # Reusable config data for tests that need a loaded system
    _SAMPLE_CONFIG = {
        'quantum_state': {
            'enabled': True,
            'version': '1.0',
            'max_agents': 50,
            'coherence_target': 0.95,
            'subsystem': {
                'param1': 'value1',
                'param2': 42
            }
        }
    }

    @pytest.fixture
    def tmp_config_dir(self, tmp_path):
        """Create a temporary config directory with a sample YAML file."""
        (tmp_path / 'core').mkdir()
        config_file = tmp_path / 'core' / 'quantum_state_config.yaml'
        config_file.write_text(yaml.dump(self._SAMPLE_CONFIG), encoding='utf-8')
        return tmp_path

    @pytest.fixture
    def manager(self):
        """Create ConfigManager instance (no real config dir needed for unit tests)."""
        return ConfigManager(config_dir='config')

    @pytest.fixture
    def manager_with_tmp(self, tmp_config_dir):
        """Create ConfigManager instance pointing at a temporary config directory."""
        return ConfigManager(config_dir=str(tmp_config_dir))

    @pytest.fixture
    def temp_config(self):
        """Create temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'test_system': {
                    'enabled': True,
                    'version': '1.0',
                    'max_agents': 50,
                    'coherence_target': 0.95,
                    'subsystem': {
                        'param1': 'value1',
                        'param2': 42
                    }
                }
            }
            yaml.dump(config_data, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    def test_load_config_success(self, manager_with_tmp):
        """Test loading a valid configuration from a temp file."""
        config = manager_with_tmp.load_config(
            'quantum_state',
            'core/quantum_state_config.yaml'
        )
        assert config is not None
        assert 'quantum_state' in config

    def test_load_config_file_not_found(self, manager):
        """Test loading non-existent configuration."""
        with pytest.raises(FileNotFoundError):
            manager.load_config('nonexistent', 'nonexistent_config.yaml')

    def test_load_all_systems(self, manager):
        """Test that load_all_systems returns a dict (files may not exist in CI)."""
        # In environments without config files, load_all_systems should gracefully
        # skip missing files and return whatever it could load (possibly empty).
        configs = manager.load_all_systems()
        assert isinstance(configs, dict)

    def test_get_value_existing(self, manager):
        """Test getting existing configuration value from an in-memory config."""
        manager._configs['quantum_state'] = {
            'quantum_state': {'enabled': True, 'version': '1.0'}
        }
        value = manager.get_value('quantum_state', 'quantum_state.enabled')
        assert value is True

    def test_get_value_default(self, manager):
        """Test getting non-existent value with default."""
        manager._configs['quantum_state'] = {'quantum_state': {'enabled': True}}
        value = manager.get_value('quantum_state', 'nonexistent.path', default='default_value')
        assert value == 'default_value'

    def test_set_value(self, manager):
        """Test setting a configuration value."""
        manager._configs['quantum_state'] = {'quantum_state': {'enabled': True}}
        manager.set_value('quantum_state', 'test.new.value', 42)
        value = manager.get_value('quantum_state', 'test.new.value')
        assert value == 42

    def test_get_config(self, manager):
        """Test getting cached configuration."""
        manager._configs['quantum_state'] = {'quantum_state': {'enabled': True}}
        config = manager.get_config('quantum_state')
        assert config is not None
        assert isinstance(config, dict)

    def test_get_config_not_loaded(self, manager):
        """Test getting non-loaded configuration."""
        config = manager.get_config('nonexistent')
        assert config is None

    def test_compare_configs(self, manager):
        """Test comparing two in-memory configurations."""
        manager._configs['sys_a'] = {'key_a': 1, 'shared': 'same', 'diff': 10}
        manager._configs['sys_b'] = {'key_b': 2, 'shared': 'same', 'diff': 20}

        differences = manager.compare_configs('sys_a', 'sys_b')

        assert isinstance(differences, dict)
        assert 'only_in_1' in differences
        assert 'only_in_2' in differences
        assert 'different_values' in differences

    def test_environment_variable_override(self):
        """Test environment variable overrides."""
        # Set environment variables
        os.environ['COSMIC_TEST_SYSTEM_TEST_PARAM'] = '100'
        os.environ['COSMIC_TEST_SYSTEM_ENABLED'] = 'true'

        manager = ConfigManager(config_dir='config', env_prefix='COSMIC_')

        # Create minimal config in memory
        manager._configs['test_system'] = {
            'test_param': 50,
            'enabled': False
        }

        # Apply env overrides
        manager._merge_environment_variables(
            manager._configs['test_system'],
            'test_system'
        )

        # Verify overrides applied
        assert manager.get_value('test_system', 'test_param') == 100
        assert manager.get_value('test_system', 'enabled') is True

        # Cleanup
        del os.environ['COSMIC_TEST_SYSTEM_TEST_PARAM']
        del os.environ['COSMIC_TEST_SYSTEM_ENABLED']

    def test_export_config(self, manager_with_tmp):
        """Test exporting configuration."""
        manager_with_tmp.load_config('quantum_state', 'core/quantum_state_config.yaml')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            manager_with_tmp.export_config('quantum_state', temp_path)

            # Verify file was created and is valid YAML
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                exported = yaml.safe_load(f)
            assert exported is not None
        finally:
            os.unlink(temp_path)


class TestConfigValidator:
    """Test ConfigValidator utility functions."""
    
    def test_validate_number_range_valid(self):
        """Test valid numeric range validation."""
        is_valid, msg = ConfigValidator.validate_number_range(50, min_val=10, max_val=100)
        assert is_valid
    
    def test_validate_number_range_below_min(self):
        """Test numeric value below minimum."""
        is_valid, msg = ConfigValidator.validate_number_range(5, min_val=10, max_val=100)
        assert not is_valid
        assert "below minimum" in msg
    
    def test_validate_number_range_above_max(self):
        """Test numeric value above maximum."""
        is_valid, msg = ConfigValidator.validate_number_range(150, min_val=10, max_val=100)
        assert not is_valid
        assert "above maximum" in msg
    
    def test_validate_choice_valid(self):
        """Test valid choice validation."""
        is_valid, msg = ConfigValidator.validate_choice(
            "conservative",
            ["conservative", "balanced", "aggressive"]
        )
        assert is_valid
    
    def test_validate_choice_invalid(self):
        """Test invalid choice validation."""
        is_valid, msg = ConfigValidator.validate_choice(
            "invalid",
            ["conservative", "balanced", "aggressive"]
        )
        assert not is_valid
        assert "not in allowed values" in msg
    
    def test_validate_type_valid(self):
        """Test valid type validation."""
        is_valid, msg = ConfigValidator.validate_type(50, int)
        assert is_valid
    
    def test_validate_type_invalid(self):
        """Test invalid type validation."""
        is_valid, msg = ConfigValidator.validate_type("50", int)
        assert not is_valid
        assert "Expected" in msg
    
    def test_validate_type_multiple_valid(self):
        """Test valid type with multiple allowed types."""
        is_valid, msg = ConfigValidator.validate_type(50, (int, float))
        assert is_valid
        
        is_valid, msg = ConfigValidator.validate_type(50.5, (int, float))
        assert is_valid


class TestConfigIntegration:
    """Integration tests for ConfigManager."""

    _SYSTEM_CONFIGS = {
        'quantum_state': {'quantum_state': {'enabled': True, 'version': '1.0', 'max_agents': 50}},
        'hybrid_quantum': {'hybrid_quantum': {'enabled': True, 'version': '2.0', 'ratio': 0.5}},
        'singularity_universe': {'singularity_universe': {'enabled': True, 'max_agents': 100}},
    }

    @pytest.fixture
    def tmp_multi_config_dir(self, tmp_path):
        """Create a temp config tree with several system YAML files."""
        for subdir, filename, data in [
            ('core', 'quantum_state_config.yaml', self._SYSTEM_CONFIGS['quantum_state']),
            ('services', 'hybrid_quantum_config.yaml', self._SYSTEM_CONFIGS['hybrid_quantum']),
            ('systems', 'singularity_universe_config.yaml',
             self._SYSTEM_CONFIGS['singularity_universe']),
        ]:
            (tmp_path / subdir).mkdir(exist_ok=True)
            (tmp_path / subdir / filename).write_text(yaml.dump(data), encoding='utf-8')
        return tmp_path

    def test_load_and_validate_all_systems(self, tmp_multi_config_dir):
        """Test loading and validating multiple system configurations."""
        manager = ConfigManager(config_dir=str(tmp_multi_config_dir))

        systems = [
            ('quantum_state', 'core/quantum_state_config.yaml'),
            ('hybrid_quantum', 'services/hybrid_quantum_config.yaml'),
            ('singularity_universe', 'systems/singularity_universe_config.yaml'),
        ]

        for system_name, config_file in systems:
            config = manager.load_config(system_name, config_file)
            assert config is not None, f"Failed to load {system_name}"
            assert isinstance(config, dict)

    def test_get_all_system_values(self, tmp_multi_config_dir):
        """Test retrieving values from loaded systems."""
        manager = ConfigManager(config_dir=str(tmp_multi_config_dir))
        manager.load_config('singularity_universe', 'systems/singularity_universe_config.yaml')

        max_agents = manager.get_value(
            'singularity_universe',
            'singularity_universe.max_agents'
        )
        assert max_agents == 100

    def test_metadata_extraction(self, tmp_multi_config_dir):
        """Test metadata extraction from configuration files."""
        manager = ConfigManager(config_dir=str(tmp_multi_config_dir))
        manager.load_config('quantum_state', 'core/quantum_state_config.yaml')

        metadata = manager.get_documentation('quantum_state')
        assert isinstance(metadata, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
