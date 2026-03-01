#!/usr/bin/env python3
"""
Test Suite for 12 New Engine Configurations
12個新引擎配置測試套件

This module provides comprehensive tests for all 12 new engine configurations,
ensuring proper loading, validation, and functionality.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from src.config_manager import ConfigManager


class TestEngineConfigLoading:
    """Test loading of all 12 engine configurations."""
    
    @pytest.fixture
    def config_manager(self):
        """Create ConfigManager instance."""
        return ConfigManager(config_dir='config')
    
    def test_code_cleaning_config(self, config_manager):
        """Test Code Cleaning Engine configuration."""
        config = config_manager.load_config(
            'code_cleaning',
            'engines/code_cleaning_config.yaml'
        )
        assert config is not None
        assert 'code_cleaning' in config
        assert 'scanning' in config['code_cleaning']
        assert 'error_detection' in config['code_cleaning']
        assert 'profiles' in config
    
    def test_ultimate_gain_config(self, config_manager):
        """Test Ultimate Gain Calculation Engine configuration."""
        config = config_manager.load_config(
            'ultimate_gain',
            'engines/ultimate_gain_config.yaml'
        )
        assert config is not None
        assert 'ultimate_gain_calculation' in config
        assert 'gain_calculation' in config['ultimate_gain_calculation']
        assert 'infinite_gain' in config['ultimate_gain_calculation']['gain_calculation']
    
    def test_opencode_evolution_config(self, config_manager):
        """Test OpenCode Evolution Engine configuration."""
        config = config_manager.load_config(
            'opencode_evolution',
            'engines/opencode_evolution_config.yaml'
        )
        assert config is not None
        assert 'opencode_evolution' in config
        assert 'configuration_optimization' in config['opencode_evolution']
    
    def test_immortal_engine_config(self, config_manager):
        """Test Immortal Perpetual Engine configuration."""
        config = config_manager.load_config(
            'immortal_engine',
            'engines/immortal_perpetual_config.yaml'
        )
        assert config is not None
        assert 'immortal_perpetual' in config
        assert 'life_cycle' in config['immortal_perpetual']
        assert 'regeneration' in config['immortal_perpetual']
        assert 'immortality_mode' in config['immortal_perpetual']
    
    def test_qft_engine_config(self, config_manager):
        """Test Quantum Field Theory Engine configuration."""
        config = config_manager.load_config(
            'qft_engine',
            'engines/qft_config.yaml'
        )
        assert config is not None
        assert 'quantum_field_theory' in config
        assert 'lattice' in config['quantum_field_theory']
        assert 'hilbert_space' in config['quantum_field_theory']
        assert 'quantum_states' in config['quantum_field_theory']
    
    def test_synergy_engine_config(self, config_manager):
        """Test Exponential Synergy Engine configuration."""
        config = config_manager.load_config(
            'synergy_engine',
            'engines/synergy_config.yaml'
        )
        assert config is not None
        assert 'exponential_synergy' in config
        assert 'layers' in config['exponential_synergy']
        assert 'exponential_growth' in config['exponential_synergy']
    
    def test_advanced_computing_config(self, config_manager):
        """Test Advanced Computing Engine configuration."""
        config = config_manager.load_config(
            'advanced_computing',
            'engines/advanced_computing_config.yaml'
        )
        assert config is not None
        assert 'advanced_computing' in config
        assert 'paradigms' in config['advanced_computing']
    
    def test_breakthrough_detector_config(self, config_manager):
        """Test Breakthrough Detector Engine configuration."""
        config = config_manager.load_config(
            'breakthrough_detector',
            'engines/breakthrough_detector_config.yaml'
        )
        assert config is not None
        assert 'breakthrough_detector' in config
        assert 'statistical_validation' in config['breakthrough_detector']
    
    def test_enhanced_classical_config(self, config_manager):
        """Test Enhanced Classical Engine configuration."""
        config = config_manager.load_config(
            'enhanced_classical',
            'engines/enhanced_classical_config.yaml'
        )
        assert config is not None
        assert 'enhanced_classical' in config
        assert 'enhancement_types' in config['enhanced_classical']
    
    def test_ray_distributed_config(self, config_manager):
        """Test Ray Distributed Engine configuration."""
        config = config_manager.load_config(
            'ray_distributed',
            'engines/ray_distributed_config.yaml'
        )
        assert config is not None
        assert 'ray_distributed' in config
        assert 'environment' in config['ray_distributed']
        assert 'distributed_tasks' in config['ray_distributed']
    
    def test_immune_reconfig_config(self, config_manager):
        """Test Immune Reconfiguration Engine configuration."""
        config = config_manager.load_config(
            'immune_reconfig',
            'engines/immune_reconfig_config.yaml'
        )
        assert config is not None
        assert 'immune_reconfig' in config
        assert 'immune_system' in config['immune_reconfig']
    
    def test_meta_synergy_config(self, config_manager):
        """Test Meta Synergy Engine (Quantum Theory) configuration."""
        config = config_manager.load_config(
            'meta_synergy',
            'engines/meta_synergy_config.yaml'
        )
        assert config is not None
        assert 'meta_synergy' in config
        assert 'gain_layers' in config['meta_synergy']
        assert 'inter_layer_synergy' in config['meta_synergy']


class TestEngineConfigProfiles:
    """Test configuration profiles for all engines."""
    
    @pytest.fixture
    def config_manager(self):
        """Create ConfigManager instance."""
        return ConfigManager(config_dir='config')
    
    def test_conservative_profile(self, config_manager):
        """Test conservative profile loading."""
        config = config_manager.load_config(
            'code_cleaning',
            'engines/code_cleaning_config.yaml',
            profile='conservative'
        )
        assert config is not None
        assert 'profiles' in config
        assert 'conservative' in config['profiles']
    
    def test_balanced_profile(self, config_manager):
        """Test balanced profile loading."""
        config = config_manager.load_config(
            'ultimate_gain',
            'engines/ultimate_gain_config.yaml',
            profile='balanced'
        )
        assert config is not None
        assert 'profiles' in config
        assert 'balanced' in config['profiles']
    
    def test_aggressive_profile(self, config_manager):
        """Test aggressive profile loading."""
        config = config_manager.load_config(
            'meta_synergy',
            'engines/meta_synergy_config.yaml',
            profile='aggressive'
        )
        assert config is not None
        assert 'profiles' in config
        assert 'aggressive' in config['profiles']


class TestEngineConfigIntegration:
    """Integration tests for all engine configurations."""
    
    @pytest.fixture
    def config_manager(self):
        """Create ConfigManager instance."""
        return ConfigManager(config_dir='config')
    
    def test_load_all_engines(self, config_manager):
        """Test loading all 12 new engines."""
        engines = [
            ('code_cleaning', 'engines/code_cleaning_config.yaml'),
            ('ultimate_gain', 'engines/ultimate_gain_config.yaml'),
            ('opencode_evolution', 'engines/opencode_evolution_config.yaml'),
            ('immortal_engine', 'engines/immortal_perpetual_config.yaml'),
            ('qft_engine', 'engines/qft_config.yaml'),
            ('synergy_engine', 'engines/synergy_config.yaml'),
            ('advanced_computing', 'engines/advanced_computing_config.yaml'),
            ('breakthrough_detector', 'engines/breakthrough_detector_config.yaml'),
            ('enhanced_classical', 'engines/enhanced_classical_config.yaml'),
            ('ray_distributed', 'engines/ray_distributed_config.yaml'),
            ('immune_reconfig', 'engines/immune_reconfig_config.yaml'),
            ('meta_synergy', 'engines/meta_synergy_config.yaml'),
        ]
        
        for system_name, config_file in engines:
            config = config_manager.load_config(system_name, config_file)
            assert config is not None, f"Failed to load {system_name}"
    
    def test_all_engines_have_profiles(self, config_manager):
        """Verify all engines have profiles."""
        engines = [
            ('code_cleaning', 'engines/code_cleaning_config.yaml'),
            ('ultimate_gain', 'engines/ultimate_gain_config.yaml'),
            ('opencode_evolution', 'engines/opencode_evolution_config.yaml'),
            ('immortal_engine', 'engines/immortal_perpetual_config.yaml'),
            ('qft_engine', 'engines/qft_config.yaml'),
            ('synergy_engine', 'engines/synergy_config.yaml'),
            ('advanced_computing', 'engines/advanced_computing_config.yaml'),
            ('breakthrough_detector', 'engines/breakthrough_detector_config.yaml'),
            ('enhanced_classical', 'engines/enhanced_classical_config.yaml'),
            ('ray_distributed', 'engines/ray_distributed_config.yaml'),
            ('immune_reconfig', 'engines/immune_reconfig_config.yaml'),
            ('meta_synergy', 'engines/meta_synergy_config.yaml'),
        ]
        
        for system_name, config_file in engines:
            config = config_manager.load_config(system_name, config_file)
            assert 'profiles' in config, f"{system_name} missing profiles"
            assert 'conservative' in config['profiles']
            assert 'balanced' in config['profiles']
            assert 'aggressive' in config['profiles']
    
    def test_engine_config_consistency(self, config_manager):
        """Test consistency of engine configurations."""
        config = config_manager.load_config(
            'code_cleaning',
            'engines/code_cleaning_config.yaml'
        )
        
        # Check for required sections
        assert isinstance(config.get('code_cleaning'), dict)
        assert isinstance(config.get('profiles'), dict)
        
        # Check profiles have descriptions
        for profile_name, profile_config in config['profiles'].items():
            assert 'description' in profile_config
    
    def test_get_engine_values(self, config_manager):
        """Test accessing values from engine configs."""
        config = config_manager.load_config(
            'ray_distributed',
            'engines/ray_distributed_config.yaml'
        )
        
        config_manager._configs['ray_distributed'] = config
        
        # Test dot-notation access
        cpus = config_manager.get_value(
            'ray_distributed',
            'ray_distributed.environment.cpus.min_cpus',
            default=[1, 128]
        )
        assert cpus is not None


class TestEngineConfigValidation:
    """Validation tests for engine configurations."""
    
    @pytest.fixture
    def config_manager(self):
        """Create ConfigManager instance."""
        return ConfigManager(config_dir='config')
    
    def test_parameter_ranges_valid(self, config_manager):
        """Test that all parameter ranges are valid."""
        config = config_manager.load_config(
            'ultimate_gain',
            'engines/ultimate_gain_config.yaml'
        )
        
        # Extract all range definitions
        def extract_ranges(d, path=""):
            ranges = []
            if isinstance(d, dict):
                for k, v in d.items():
                    new_path = f"{path}.{k}" if path else k
                    if isinstance(v, list) and len(v) == 2:
                        if isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
                            ranges.append((new_path, v))
                    elif isinstance(v, dict):
                        ranges.extend(extract_ranges(v, new_path))
            return ranges
        
        ranges = extract_ranges(config)
        
        # Verify all ranges have min <= max
        for path, (min_val, max_val) in ranges:
            assert min_val <= max_val, f"Invalid range at {path}: {min_val} > {max_val}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
