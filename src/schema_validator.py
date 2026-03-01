#!/usr/bin/env python3
"""
JSON Schema Validator for Cosmic Intelligence System Configurations
宇宙智能系統配置 JSON Schema 驗證器

Provides JSON Schema definitions and validation for all system configurations,
enabling IDE autocomplete, validation, and documentation generation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)


# JSON Schema Definitions for each system
QUANTUM_STATE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Quantum State Configuration",
    "description": "Configuration for Quantum State System (量子態系統)",
    "type": "object",
    "required": ["quantum_state"],
    "properties": {
        "quantum_state": {
            "type": "object",
            "required": ["enabled", "version"],
            "properties": {
                "enabled": {"type": "boolean"},
                "version": {"type": "string", "pattern": "^\\d+\\.\\d+$"},
                "system_name": {"type": "string"},
                "description": {"type": "string"},
                "state_dimension": {"type": "integer", "minimum": 64, "maximum": 512},
                "num_qubits": {"type": "integer", "minimum": 4, "maximum": 32},
                "num_quantum_gates": {"type": "integer", "minimum": 4, "maximum": 16},
                "coherence_time_ms": {"type": "number", "minimum": 1, "maximum": 10000},
                "entanglement_enabled": {"type": "boolean"},
                "superposition_enabled": {"type": "boolean"},
                "decoherence_model": {
                    "type": "string",
                    "enum": ["none", "depolarization", "amplitude_damping", "phase_damping"]
                }
            }
        }
    },
    "additionalProperties": False
}

HYBRID_QUANTUM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Hybrid Quantum Configuration",
    "description": "Configuration for Hybrid Quantum Services (混合量子服務)",
    "type": "object",
    "required": ["hybrid_quantum"],
    "properties": {
        "hybrid_quantum": {
            "type": "object",
            "required": ["enabled"],
            "properties": {
                "enabled": {"type": "boolean"},
                "version": {"type": "string"},
                "classical_quantum_ratio": {"type": "number", "minimum": 0, "maximum": 1},
                "trading_signals": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "signal_strength_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                        "signals": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "quantum_ensemble": {
                    "type": "object",
                    "properties": {
                        "num_members": {"type": "integer", "minimum": 1, "maximum": 100},
                        "voting_method": {
                            "type": "string",
                            "enum": ["majority", "weighted_average", "bayesian"]
                        }
                    }
                }
            }
        }
    }
}

SINGULARITY_UNIVERSE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Singularity Universe Configuration",
    "description": "Configuration for Singularity Universe System (奇點宇宙系統)",
    "type": "object",
    "required": ["singularity_universe"],
    "properties": {
        "singularity_universe": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "version": {"type": "string"},
                "system_name": {"type": "string"},
                "universe_dimension": {"type": "integer", "minimum": 256, "maximum": 1024},
                "resonance_frequency": {"type": "number", "minimum": 1.0, "maximum": 10.0},
                "coherence_target": {"type": "number", "minimum": 0.9, "maximum": 0.999},
                "quantum_budget": {"type": "number", "minimum": 0.1, "maximum": 10},
                "max_agents": {"type": "integer", "minimum": 10, "maximum": 200},
                "computation_timeout_ms": {"type": "integer", "minimum": 100, "maximum": 60000}
            }
        },
        "quantum_resonance": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "resonance": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["harmonic", "sympathetic", "constructive"]
                        },
                        "coupling_strength": {"type": "number", "minimum": 0.5, "maximum": 1.0},
                        "decay_factor": {"type": "number", "minimum": 0.001, "maximum": 0.1},
                        "reinforcement_factor": {"type": "number", "minimum": 0.9, "maximum": 2.0}
                    }
                }
            }
        },
        "multi_agent_system": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "framework": {
                    "type": "string",
                    "enum": ["semantic_kernel", "autogen", "crewai", "custom"]
                },
                "agent_pool": {
                    "type": "object",
                    "properties": {
                        "total_agents": {"type": "integer", "minimum": 10, "maximum": 200}
                    }
                }
            }
        }
    }
}

IMMORTAL_PERPETUAL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Immortal Perpetual Configuration",
    "description": "Configuration for Immortal Perpetual System (永生循環系統)",
    "type": "object",
    "required": ["immortal_perpetual"],
    "properties": {
        "immortal_perpetual": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "version": {"type": "string"},
                "num_immortal_nodes": {"type": "integer", "minimum": 1, "maximum": 32},
                "immortality_modes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["linear", "cyclic", "recursive", "quantum", "information"]
                    }
                },
                "energy_management": {
                    "type": "object",
                    "properties": {
                        "energy_reservoir_capacity": {"type": "number", "minimum": 1, "maximum": 1000},
                        "replenishment_rate": {"type": "number", "minimum": 0.1, "maximum": 10},
                        "energy_efficiency_target": {"type": "number", "minimum": 0.5, "maximum": 0.99}
                    }
                }
            }
        }
    }
}

TIME_TRAVEL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Intelligent Time Travel Configuration",
    "description": "Configuration for Intelligent Time Travel System (智能時間旅行系統)",
    "type": "object",
    "required": ["intelligent_time_travel"],
    "properties": {
        "intelligent_time_travel": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "version": {"type": "string"},
                "prediction_models": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["LSTM", "Transformer", "ARIMA", "Prophet"]
                    }
                },
                "monte_carlo_simulations": {
                    "type": "object",
                    "properties": {
                        "num_scenarios": {"type": "integer", "minimum": 100, "maximum": 100000},
                        "confidence_level": {"type": "number", "minimum": 0.8, "maximum": 0.99}
                    }
                }
            }
        }
    }
}

UNIVERSAL_QUINTENARY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Universal Quintenary Cosmic System Configuration",
    "description": "Configuration for Universal Quintenary Cosmic System (通用五元宇宙系統)",
    "type": "object",
    "required": ["universal_quintenary"],
    "properties": {
        "universal_quintenary": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "version": {"type": "string"},
                "total_system_nodes": {"type": "integer", "minimum": 100, "maximum": 1000},
                "system_multiplier": {"type": "number", "minimum": 1e10, "maximum": 1e30},
                "integration_level": {
                    "type": "string",
                    "enum": ["basic", "intermediate", "advanced", "cosmic"]
                },
                "resonance_matrix": {
                    "type": "object",
                    "properties": {
                        "matrix_dimension": {"type": "integer", "minimum": 5, "maximum": 100}
                    }
                }
            }
        }
    }
}

# Schema registry mapping system names to schemas
SCHEMA_REGISTRY = {
    'quantum_state': QUANTUM_STATE_SCHEMA,
    'hybrid_quantum': HYBRID_QUANTUM_SCHEMA,
    'singularity_universe': SINGULARITY_UNIVERSE_SCHEMA,
    'immortal_perpetual': IMMORTAL_PERPETUAL_SCHEMA,
    'intelligent_time_travel': TIME_TRAVEL_SCHEMA,
    'universal_quintenary': UNIVERSAL_QUINTENARY_SCHEMA,
}


class SchemaValidator:
    """Validator for JSON Schema-based configuration validation."""
    
    def __init__(self):
        """Initialize SchemaValidator."""
        self.schemas = SCHEMA_REGISTRY
        self._validation_errors: List[str] = []
    
    def validate(self, system_name: str, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration against schema.
        
        Args:
            system_name: Name of the system
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        self._validation_errors = []
        
        if system_name not in self.schemas:
            return False, [f"No schema defined for system: {system_name}"]
        
        schema = self.schemas[system_name]
        
        # Basic validation
        self._validate_object(config, schema, "root")
        
        return len(self._validation_errors) == 0, self._validation_errors
    
    def _validate_object(self, obj: Any, schema: Dict[str, Any], path: str) -> None:
        """Recursively validate object against schema.
        
        Args:
            obj: Object to validate
            schema: JSON schema
            path: Current path in object
        """
        # Check required fields
        if "required" in schema:
            for required_field in schema["required"]:
                if isinstance(obj, dict) and required_field not in obj:
                    self._validation_errors.append(
                        f"{path}: Missing required field '{required_field}'"
                    )
        
        # Validate properties
        if "properties" in schema and isinstance(obj, dict):
            for key, value in obj.items():
                prop_schema = schema["properties"].get(key)
                if prop_schema:
                    self._validate_value(value, prop_schema, f"{path}.{key}")
                elif schema.get("additionalProperties") is False:
                    self._validation_errors.append(
                        f"{path}.{key}: Additional property not allowed"
                    )
        
        # Validate type
        if "type" in schema:
            if not self._check_type(obj, schema["type"]):
                self._validation_errors.append(
                    f"{path}: Expected type {schema['type']}, got {type(obj).__name__}"
                )
    
    def _validate_value(self, value: Any, schema: Dict[str, Any], path: str) -> None:
        """Validate a single value against schema.
        
        Args:
            value: Value to validate
            schema: JSON schema for the value
            path: Current path
        """
        # Type check
        if "type" in schema:
            if not self._check_type(value, schema["type"]):
                self._validation_errors.append(
                    f"{path}: Expected {schema['type']}, got {type(value).__name__}"
                )
                return
        
        # Enum check
        if "enum" in schema and value not in schema["enum"]:
            self._validation_errors.append(
                f"{path}: Value {value} not in allowed values {schema['enum']}"
            )
        
        # Numeric range checks
        if isinstance(value, (int, float)):
            if "minimum" in schema and value < schema["minimum"]:
                self._validation_errors.append(
                    f"{path}: Value {value} is below minimum {schema['minimum']}"
                )
            if "maximum" in schema and value > schema["maximum"]:
                self._validation_errors.append(
                    f"{path}: Value {value} exceeds maximum {schema['maximum']}"
                )
        
        # String pattern check
        if isinstance(value, str) and "pattern" in schema:
            import re
            if not re.match(schema["pattern"], value):
                self._validation_errors.append(
                    f"{path}: Value '{value}' does not match pattern {schema['pattern']}"
                )
        
        # Object recursion
        if isinstance(value, dict) and schema.get("type") == "object":
            self._validate_object(value, schema, path)
        
        # Array recursion
        if isinstance(value, list) and schema.get("type") == "array":
            items_schema = schema.get("items", {})
            for idx, item in enumerate(value):
                self._validate_value(item, items_schema, f"{path}[{idx}]")
    
    @staticmethod
    def _check_type(value: Any, expected_type: str) -> bool:
        """Check if value matches JSON schema type.
        
        Args:
            value: Value to check
            expected_type: JSON schema type string
            
        Returns:
            True if value matches type
        """
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "null": type(None),
        }
        
        if expected_type in type_map:
            return isinstance(value, type_map[expected_type])
        
        return True
    
    def export_schema(self, system_name: str, output_file: str) -> None:
        """Export schema to JSON file.
        
        Args:
            system_name: System name
            output_file: Output file path
        """
        if system_name not in self.schemas:
            raise ValueError(f"No schema for system: {system_name}")
        
        schema = self.schemas[system_name]
        
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
        logger.info(f"Exported schema for {system_name} to {output_file}")
    
    def export_all_schemas(self, output_dir: str) -> None:
        """Export all schemas to files in directory.
        
        Args:
            output_dir: Output directory path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for system_name in self.schemas:
            output_file = output_path / f"{system_name}_schema.json"
            self.export_schema(system_name, str(output_file))
        
        logger.info(f"Exported {len(self.schemas)} schemas to {output_dir}")
    
    def get_schema(self, system_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a system.
        
        Args:
            system_name: System name
            
        Returns:
            Schema dictionary or None
        """
        return self.schemas.get(system_name)


def main() -> None:
    """Example usage of SchemaValidator."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize validator
    validator = SchemaValidator()
    
    # Export all schemas
    print("Exporting JSON schemas...")
    validator.export_all_schemas('config/schemas')
    
    # Example: Validate quantum state configuration
    print("\nTesting schema validation...")
    
    test_config = {
        'quantum_state': {
            'enabled': True,
            'version': '1.0',
            'state_dimension': 128,
            'num_qubits': 8,
            'num_quantum_gates': 4,
            'coherence_time_ms': 1000,
            'entanglement_enabled': True,
            'superposition_enabled': True,
            'decoherence_model': 'none'
        }
    }
    
    is_valid, errors = validator.validate('quantum_state', test_config)
    
    if is_valid:
        print("✅ Quantum state configuration is valid")
    else:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Test invalid configuration
    print("\nTesting invalid configuration...")
    invalid_config = {
        'quantum_state': {
            'enabled': True,
            'state_dimension': 1000,  # Above maximum
            'num_qubits': 50,  # Above maximum
        }
    }
    
    is_valid, errors = validator.validate('quantum_state', invalid_config)
    
    if is_valid:
        print("✅ Invalid config passed (unexpected)")
    else:
        print("❌ Expected validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Print available schemas
    print("\nAvailable schemas:")
    for system_name in validator.schemas:
        print(f"  - {system_name}")


if __name__ == '__main__':
    main()
