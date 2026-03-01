# ConfigManager Quick Reference Guide

## 📋 One-Page Cheat Sheet

### Installation & Imports
```python
from src.config_manager import ConfigManager, ConfigValidator, ParameterConstraint
from src.schema_validator import SchemaValidator
```

### Load Configurations
```python
# Initialize manager
manager = ConfigManager(config_dir='config')

# Load single system
config = manager.load_config('quantum_state', 'core/quantum_state_config.yaml')

# Load all systems
all_configs = manager.load_all_systems()

# Load with specific profile
config = manager.load_config('quantum_state', 'core/quantum_state_config.yaml', 
                            profile='balanced')
```

### Access Values
```python
# Get value (with default)
value = manager.get_value('quantum_state', 'quantum_state.state_dimension', default=128)

# Set value
manager.set_value('quantum_state', 'quantum_state.coherence_target', 0.98)

# Get entire config
config_dict = manager.get_config('quantum_state')
```

### Validation
```python
# Schema validation
validator = SchemaValidator()
is_valid, errors = validator.validate('quantum_state', config)

# Custom constraint validation
constraint = ParameterConstraint(
    name='coherence_target',
    expected_type=float,
    min_value=0.9,
    max_value=0.999
)
is_valid, msg = constraint.validate(0.95)
```

### Configuration Management
```python
# Compare two configs
diff = manager.compare_configs('quantum_state', 'hybrid_quantum')
print(diff['different_values'])

# Export configuration
manager.export_config('quantum_state', 'my_config.yaml')

# Get documentation
docs = manager.get_documentation('quantum_state')
```

### Environment Overrides
```bash
# Set env vars with pattern: COSMIC_{SYSTEM}_{SECTION}_{KEY}=value
export COSMIC_QUANTUM_STATE_QUANTUM_STATE_COHERENCE_TARGET=0.99
export COSMIC_SINGULARITY_UNIVERSE_SINGULARITY_UNIVERSE_MAX_AGENTS=100

# Load with env overrides (default)
config = manager.load_config('quantum_state', 'core/quantum_state_config.yaml')
```

### Running Tests
```bash
# All tests
pytest src/tests/test_config_manager.py -v

# Specific test
pytest src/tests/test_config_manager.py::TestConfigManager::test_load_all_systems -v

# With coverage
pytest src/tests/test_config_manager.py --cov=src.config_manager -v
```

## 🎯 Common Tasks

### Task 1: Load and Use Configuration
```python
manager = ConfigManager()
config = manager.load_config('singularity_universe', 
                            'systems/singularity_universe_config.yaml')
max_agents = manager.get_value('singularity_universe', 
                               'singularity_universe.max_agents')
print(f"Max agents: {max_agents}")
```

### Task 2: Validate Configuration
```python
validator = SchemaValidator()
is_valid, errors = validator.validate('singularity_universe', config)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
else:
    print("Configuration is valid!")
```

### Task 3: Compare Configurations
```python
diff = manager.compare_configs('quantum_state', 'hybrid_quantum')

if diff['only_in_1']:
    print("Only in quantum_state:", diff['only_in_1'])

if diff['different_values']:
    print("Different values:", diff['different_values'])
```

### Task 4: Export Modified Configuration
```python
manager.load_config('quantum_state', 'core/quantum_state_config.yaml')
manager.set_value('quantum_state', 'quantum_state.num_qubits', 16)
manager.set_value('quantum_state', 'quantum_state.coherence_time_ms', 5000)
manager.export_config('quantum_state', 'updated_quantum_state.yaml')
```

### Task 5: Use Environment Overrides
```bash
# In your shell
export COSMIC_IMMORTAL_PERPETUAL_IMMORTAL_PERPETUAL_NUM_IMMORTAL_NODES=32
export COSMIC_IMMORTAL_PERPETUAL_IMMORTAL_PERPETUAL_ENERGY_RESERVOIR_CAPACITY=500

# In your Python code
manager = ConfigManager()
config = manager.load_config('immortal_perpetual', 
                            'systems/immortal_perpetual_config.yaml',
                            merge_env=True)  # Default is True
```

## 🔧 API Quick Reference

### ConfigManager Methods
| Method | Purpose | Example |
|--------|---------|---------|
| `load_config()` | Load YAML configuration | `load_config('system', 'path.yaml')` |
| `load_all_systems()` | Load all systems | `all = load_all_systems()` |
| `get_value()` | Get config value | `get_value('sys', 'path.key')` |
| `set_value()` | Set config value | `set_value('sys', 'path.key', val)` |
| `get_config()` | Get cached config | `config = get_config('sys')` |
| `validate_config()` | Validate configuration | `validate_config('sys', cfg)` |
| `compare_configs()` | Compare two configs | `compare_configs('sys1', 'sys2')` |
| `export_config()` | Export to YAML | `export_config('sys', 'out.yaml')` |

### SchemaValidator Methods
| Method | Purpose | Example |
|--------|---------|---------|
| `validate()` | Validate against schema | `validate('system', config)` |
| `export_schema()` | Export JSON schema | `export_schema('sys', 'out.json')` |
| `export_all_schemas()` | Export all schemas | `export_all_schemas('dir')` |
| `get_schema()` | Get schema definition | `get_schema('system')` |

## 📊 Systems Overview

| System | Config File | Key Parameters |
|--------|-------------|-----------------|
| **Quantum State** | `core/quantum_state_config.yaml` | state_dimension, num_qubits, coherence_time_ms |
| **Hybrid Quantum** | `services/hybrid_quantum_config.yaml` | classical_quantum_ratio, signal_strength |
| **Quantum Optimization** | `optimization/quantum_algorithm_config.yaml` | algorithm configs, convergence criteria |
| **Singularity Universe** | `systems/singularity_universe_config.yaml` | universe_dimension, max_agents, resonance |
| **Time Travel** | `systems/intelligent_time_travel_config.yaml` | prediction_models, monte_carlo scenarios |
| **Immortal Perpetual** | `systems/immortal_perpetual_config.yaml` | immortal_nodes, energy_reservoir, modes |
| **Quintenary** | `systems/universal_quintenary_cosmic_config.yaml` | total_nodes, system_multiplier |

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| File not found | Check path is relative to `config_dir` |
| Invalid YAML | Run `python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"` |
| Env var not applied | Ensure format: `COSMIC_SYSTEM_SECTION_KEY=value` |
| Validation fails | Check parameter ranges in schema or CONFIG_MANAGER_README.md |
| Import error | Ensure `src/` is in Python path |

## 📚 More Information

- **Full Documentation**: `CONFIG_MANAGER_README.md`
- **System Guide**: `CONFIG_INDEX.md`
- **Implementation Details**: `IMPLEMENTATION_COMPLETE.md`
- **Source Code**: `src/config_manager.py`
- **Tests**: `src/tests/test_config_manager.py`
