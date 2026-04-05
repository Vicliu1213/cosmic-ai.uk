#!/usr/bin/env python3
"""
Schema Validator Tests
JSON Schema 驗證器測試

Unit tests for SchemaValidator: validate, _validate_object, _validate_value,
_check_type, export_schema, export_all_schemas, and get_schema.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from schema_validator import SchemaValidator, SCHEMA_REGISTRY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_quantum_state_config() -> Dict[str, Any]:
    """Return a minimal valid quantum_state configuration."""
    return {
        'quantum_state': {
            'enabled': True,
            'version': '1.0',
        }
    }


def _valid_hybrid_quantum_config() -> Dict[str, Any]:
    """Return a minimal valid hybrid_quantum configuration."""
    return {
        'hybrid_quantum': {
            'enabled': True,
        }
    }


# ---------------------------------------------------------------------------
# SchemaValidator – initialisation
# ---------------------------------------------------------------------------

class TestSchemaValidatorInit:
    """Tests for SchemaValidator initialisation."""

    def test_creates_instance(self):
        validator = SchemaValidator()
        assert validator is not None

    def test_schemas_loaded(self):
        validator = SchemaValidator()
        assert isinstance(validator.schemas, dict)
        assert len(validator.schemas) > 0

    def test_known_systems_registered(self):
        validator = SchemaValidator()
        expected = {'quantum_state', 'hybrid_quantum', 'singularity_universe',
                    'immortal_perpetual', 'intelligent_time_travel', 'universal_quintenary'}
        assert expected.issubset(set(validator.schemas.keys()))


# ---------------------------------------------------------------------------
# SchemaValidator.get_schema
# ---------------------------------------------------------------------------

class TestGetSchema:
    """Tests for SchemaValidator.get_schema."""

    def test_returns_schema_for_known_system(self):
        validator = SchemaValidator()
        schema = validator.get_schema('quantum_state')
        assert isinstance(schema, dict)
        assert '$schema' in schema or 'properties' in schema

    def test_returns_none_for_unknown_system(self):
        validator = SchemaValidator()
        assert validator.get_schema('nonexistent_system') is None

    def test_all_registered_systems_have_schemas(self):
        validator = SchemaValidator()
        for name in SCHEMA_REGISTRY:
            schema = validator.get_schema(name)
            assert schema is not None, f"Schema missing for {name}"
            assert isinstance(schema, dict)


# ---------------------------------------------------------------------------
# SchemaValidator.validate – unknown system
# ---------------------------------------------------------------------------

class TestValidateUnknownSystem:
    """Tests for validate() with an unregistered system name."""

    def test_unknown_system_returns_invalid(self):
        validator = SchemaValidator()
        is_valid, errors = validator.validate('no_such_system', {})
        assert is_valid is False
        assert len(errors) == 1
        assert 'no_such_system' in errors[0]


# ---------------------------------------------------------------------------
# SchemaValidator.validate – quantum_state
# ---------------------------------------------------------------------------

class TestValidateQuantumState:
    """Tests for validate() using the quantum_state schema."""

    def test_valid_config(self):
        validator = SchemaValidator()
        is_valid, errors = validator.validate('quantum_state', _valid_quantum_state_config())
        assert is_valid, f"Expected valid but got errors: {errors}"

    def test_missing_required_field_enabled(self):
        validator = SchemaValidator()
        config = {'quantum_state': {'version': '1.0'}}  # missing 'enabled'
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('enabled' in e for e in errors)

    def test_missing_required_field_version(self):
        validator = SchemaValidator()
        config = {'quantum_state': {'enabled': True}}  # missing 'version'
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('version' in e for e in errors)

    def test_wrong_type_for_enabled(self):
        validator = SchemaValidator()
        config = {'quantum_state': {'enabled': 'yes', 'version': '1.0'}}
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('enabled' in e for e in errors)

    def test_wrong_type_for_version(self):
        validator = SchemaValidator()
        config = {'quantum_state': {'enabled': True, 'version': 100}}
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('version' in e for e in errors)

    def test_num_qubits_below_minimum(self):
        validator = SchemaValidator()
        config = {
            'quantum_state': {
                'enabled': True,
                'version': '1.0',
                'num_qubits': 2,  # minimum is 4
            }
        }
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('num_qubits' in e for e in errors)

    def test_num_qubits_above_maximum(self):
        validator = SchemaValidator()
        config = {
            'quantum_state': {
                'enabled': True,
                'version': '1.0',
                'num_qubits': 64,  # maximum is 32
            }
        }
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('num_qubits' in e for e in errors)

    def test_invalid_decoherence_model(self):
        validator = SchemaValidator()
        config = {
            'quantum_state': {
                'enabled': True,
                'version': '1.0',
                'decoherence_model': 'invalid_model',
            }
        }
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('decoherence_model' in e for e in errors)

    def test_valid_decoherence_model(self):
        validator = SchemaValidator()
        config = {
            'quantum_state': {
                'enabled': True,
                'version': '1.0',
                'decoherence_model': 'depolarization',
            }
        }
        is_valid, errors = validator.validate('quantum_state', config)
        assert is_valid, f"Unexpected errors: {errors}"

    def test_version_pattern_must_be_two_part(self):
        """Version must match pattern ^\\d+\\.\\d+$."""
        validator = SchemaValidator()
        config = {'quantum_state': {'enabled': True, 'version': '1.0.0'}}
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('version' in e for e in errors)

    def test_additional_property_rejected(self):
        """The quantum_state schema has additionalProperties: false."""
        validator = SchemaValidator()
        config = {'quantum_state': {'enabled': True, 'version': '1.0'}, 'extra_key': 123}
        is_valid, errors = validator.validate('quantum_state', config)
        assert not is_valid
        assert any('extra_key' in e for e in errors)


# ---------------------------------------------------------------------------
# SchemaValidator.validate – hybrid_quantum
# ---------------------------------------------------------------------------

class TestValidateHybridQuantum:
    """Tests for validate() using the hybrid_quantum schema."""

    def test_valid_config(self):
        validator = SchemaValidator()
        is_valid, errors = validator.validate('hybrid_quantum', _valid_hybrid_quantum_config())
        assert is_valid, f"Unexpected errors: {errors}"

    def test_missing_enabled_field(self):
        validator = SchemaValidator()
        config = {'hybrid_quantum': {'version': '2.0'}}
        is_valid, errors = validator.validate('hybrid_quantum', config)
        assert not is_valid
        assert any('enabled' in e for e in errors)

    def test_classical_quantum_ratio_out_of_range(self):
        validator = SchemaValidator()
        config = {
            'hybrid_quantum': {
                'enabled': True,
                'classical_quantum_ratio': 1.5,  # maximum is 1
            }
        }
        is_valid, errors = validator.validate('hybrid_quantum', config)
        assert not is_valid
        assert any('classical_quantum_ratio' in e for e in errors)

    def test_nested_voting_method_valid_enum(self):
        validator = SchemaValidator()
        config = {
            'hybrid_quantum': {
                'enabled': True,
                'quantum_ensemble': {
                    'num_members': 5,
                    'voting_method': 'majority',
                }
            }
        }
        is_valid, errors = validator.validate('hybrid_quantum', config)
        assert is_valid, f"Unexpected errors: {errors}"

    def test_nested_voting_method_invalid_enum(self):
        validator = SchemaValidator()
        config = {
            'hybrid_quantum': {
                'enabled': True,
                'quantum_ensemble': {
                    'voting_method': 'invalid_vote',
                }
            }
        }
        is_valid, errors = validator.validate('hybrid_quantum', config)
        assert not is_valid
        assert any('voting_method' in e for e in errors)


# ---------------------------------------------------------------------------
# SchemaValidator._check_type (static method)
# ---------------------------------------------------------------------------

class TestCheckType:
    """Tests for SchemaValidator._check_type static method."""

    @pytest.mark.parametrize("value,schema_type,expected", [
        ({}, "object", True),
        ([], "array", True),
        ("hello", "string", True),
        (42, "integer", True),
        (3.14, "number", True),
        (42, "number", True),  # int is also a valid "number"
        (True, "boolean", True),
        (None, "null", True),
        ("hello", "integer", False),
        (42, "string", False),
        (42, "boolean", False),
        ([], "object", False),
        ({}, "array", False),
        (None, "string", False),
    ])
    def test_check_type(self, value, schema_type, expected):
        result = SchemaValidator._check_type(value, schema_type)
        assert result is expected

    def test_unknown_type_returns_true(self):
        """Unknown type strings should pass through (permissive)."""
        assert SchemaValidator._check_type(42, "unknown_type") is True


# ---------------------------------------------------------------------------
# SchemaValidator.export_schema
# ---------------------------------------------------------------------------

class TestExportSchema:
    """Tests for SchemaValidator.export_schema."""

    def test_exports_valid_json(self, tmp_path):
        validator = SchemaValidator()
        output = str(tmp_path / 'quantum_state_schema.json')
        validator.export_schema('quantum_state', output)

        with open(output, 'r') as f:
            schema = json.load(f)

        assert isinstance(schema, dict)
        assert 'properties' in schema or 'title' in schema

    def test_raises_for_unknown_system(self, tmp_path):
        validator = SchemaValidator()
        with pytest.raises(ValueError, match='no_such_system'):
            validator.export_schema('no_such_system', str(tmp_path / 'out.json'))

    def test_output_file_created(self, tmp_path):
        validator = SchemaValidator()
        output = str(tmp_path / 'out.json')
        validator.export_schema('hybrid_quantum', output)
        assert Path(output).exists()

    def test_exported_schema_matches_registry(self, tmp_path):
        validator = SchemaValidator()
        output = str(tmp_path / 'schema.json')
        validator.export_schema('quantum_state', output)

        with open(output, 'r') as f:
            exported = json.load(f)

        assert exported == SCHEMA_REGISTRY['quantum_state']


# ---------------------------------------------------------------------------
# SchemaValidator.export_all_schemas
# ---------------------------------------------------------------------------

class TestExportAllSchemas:
    """Tests for SchemaValidator.export_all_schemas."""

    def test_creates_directory(self, tmp_path):
        output_dir = str(tmp_path / 'schemas')
        validator = SchemaValidator()
        validator.export_all_schemas(output_dir)
        assert Path(output_dir).is_dir()

    def test_creates_file_for_each_schema(self, tmp_path):
        output_dir = str(tmp_path / 'schemas')
        validator = SchemaValidator()
        validator.export_all_schemas(output_dir)

        created_files = list(Path(output_dir).glob('*_schema.json'))
        assert len(created_files) == len(SCHEMA_REGISTRY)

    def test_all_exported_files_are_valid_json(self, tmp_path):
        output_dir = str(tmp_path / 'schemas')
        validator = SchemaValidator()
        validator.export_all_schemas(output_dir)

        for filepath in Path(output_dir).glob('*_schema.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
            assert isinstance(data, dict), f"{filepath} is not a valid JSON object"

    def test_works_when_directory_already_exists(self, tmp_path):
        output_dir = str(tmp_path / 'schemas')
        Path(output_dir).mkdir()
        validator = SchemaValidator()
        # Should not raise even if directory exists
        validator.export_all_schemas(output_dir)


# ---------------------------------------------------------------------------
# Validation error accumulation across multiple calls
# ---------------------------------------------------------------------------

class TestValidationErrorReset:
    """Ensure _validation_errors is reset between validate() calls."""

    def test_errors_reset_between_calls(self):
        validator = SchemaValidator()
        # First call – invalid config
        bad = {'quantum_state': {'version': '1.0'}}  # missing 'enabled'
        is_valid_1, errors_1 = validator.validate('quantum_state', bad)
        assert not is_valid_1

        # Second call – valid config
        good = _valid_quantum_state_config()
        is_valid_2, errors_2 = validator.validate('quantum_state', good)
        assert is_valid_2, f"Should be valid but got: {errors_2}"
        assert errors_2 == []


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
