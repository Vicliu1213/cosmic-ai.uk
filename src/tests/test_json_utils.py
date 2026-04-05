#!/usr/bin/env python3
"""
JSON Utilities Tests
JSON工具函数测试

Unit tests for CustomJSONEncoder, safe_json_dump, and safe_json_dumps.
"""

import io
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.json_utils import CustomJSONEncoder, safe_json_dump, safe_json_dumps


# ---------------------------------------------------------------------------
# CustomJSONEncoder
# ---------------------------------------------------------------------------

class TestCustomJSONEncoderDatetime:
    """Tests for datetime serialisation in CustomJSONEncoder."""

    def test_datetime_serialised_as_string(self):
        dt = datetime(2024, 3, 15, 10, 30, 45)
        result = json.dumps({'ts': dt}, cls=CustomJSONEncoder)
        data = json.loads(result)
        assert data['ts'] == '2024-03-15 10:30:45'

    def test_datetime_format(self):
        dt = datetime(2025, 1, 1, 0, 0, 0)
        encoded = json.dumps(dt, cls=CustomJSONEncoder)
        # Encoded value is a JSON string
        assert json.loads(encoded) == '2025-01-01 00:00:00'

    def test_datetime_midnight(self):
        dt = datetime(2024, 12, 31, 23, 59, 59)
        result = json.loads(json.dumps(dt, cls=CustomJSONEncoder))
        assert result == '2024-12-31 23:59:59'


class TestCustomJSONEncoderNumpy:
    """Tests for numpy type serialisation in CustomJSONEncoder."""

    def test_numpy_int32(self):
        val = np.int32(42)
        result = json.loads(json.dumps(val, cls=CustomJSONEncoder))
        assert result == 42
        assert isinstance(result, int)

    def test_numpy_int64(self):
        val = np.int64(1_000_000)
        result = json.loads(json.dumps(val, cls=CustomJSONEncoder))
        assert result == 1_000_000

    def test_numpy_float32(self):
        val = np.float32(3.14)
        result = json.loads(json.dumps(val, cls=CustomJSONEncoder))
        assert abs(result - 3.14) < 0.01

    def test_numpy_float64(self):
        val = np.float64(2.718281828)
        result = json.loads(json.dumps(val, cls=CustomJSONEncoder))
        assert abs(result - 2.718281828) < 1e-6

    def test_numpy_bool_true(self):
        val = np.bool_(True)
        result = json.loads(json.dumps(val, cls=CustomJSONEncoder))
        assert result is True

    def test_numpy_bool_false(self):
        val = np.bool_(False)
        result = json.loads(json.dumps(val, cls=CustomJSONEncoder))
        assert result is False

    def test_numpy_ndarray_1d(self):
        arr = np.array([1, 2, 3])
        result = json.loads(json.dumps(arr, cls=CustomJSONEncoder))
        assert result == [1, 2, 3]

    def test_numpy_ndarray_2d(self):
        arr = np.array([[1, 2], [3, 4]])
        result = json.loads(json.dumps(arr, cls=CustomJSONEncoder))
        assert result == [[1, 2], [3, 4]]

    def test_numpy_ndarray_float(self):
        arr = np.array([1.1, 2.2, 3.3])
        result = json.loads(json.dumps(arr, cls=CustomJSONEncoder))
        assert len(result) == 3
        assert abs(result[0] - 1.1) < 1e-5

    def test_numpy_empty_array(self):
        arr = np.array([])
        result = json.loads(json.dumps(arr, cls=CustomJSONEncoder))
        assert result == []

    def test_numpy_integer_in_dict(self):
        data = {'count': np.int64(99), 'value': np.float64(1.5)}
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result['count'] == 99
        assert abs(result['value'] - 1.5) < 1e-9


class TestCustomJSONEncoderPandas:
    """Tests for pandas type serialisation in CustomJSONEncoder."""

    def test_pandas_timestamp(self):
        ts = pd.Timestamp('2024-06-15 12:00:00')
        result = json.loads(json.dumps(ts, cls=CustomJSONEncoder))
        assert result == '2024-06-15 12:00:00'

    def test_pandas_timestamp_with_tz(self):
        ts = pd.Timestamp('2024-06-15 12:00:00', tz='UTC')
        # Should still serialise to a string without raising
        result = json.loads(json.dumps(ts, cls=CustomJSONEncoder))
        assert isinstance(result, str)
        assert '2024-06-15' in result

    def test_pandas_timedelta(self):
        td = pd.Timedelta('1 days 2 hours')
        result = json.loads(json.dumps(td, cls=CustomJSONEncoder))
        # Serialised as str representation
        assert isinstance(result, str)
        assert '1 day' in result or '1 days' in result

    def test_pandas_timedelta_zero(self):
        td = pd.Timedelta(0)
        result = json.loads(json.dumps(td, cls=CustomJSONEncoder))
        assert isinstance(result, str)

    def test_mixed_numpy_pandas_dict(self):
        data = {
            'int': np.int32(5),
            'float': np.float64(2.5),
            'ts': pd.Timestamp('2024-01-01'),
            'arr': np.array([10, 20]),
        }
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result['int'] == 5
        assert result['float'] == 2.5
        assert '2024-01-01' in result['ts']
        assert result['arr'] == [10, 20]


class TestCustomJSONEncoderFallthrough:
    """Tests for unsupported types (should still raise TypeError via super)."""

    def test_unserializable_type_raises(self):
        class Unserializable:
            pass

        with pytest.raises(TypeError):
            json.dumps(Unserializable(), cls=CustomJSONEncoder)

    def test_standard_types_unchanged(self):
        data = {'str': 'hello', 'int': 1, 'float': 1.5, 'bool': True, 'none': None}
        result = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        assert result == data


# ---------------------------------------------------------------------------
# safe_json_dumps
# ---------------------------------------------------------------------------

class TestSafeJsonDumps:
    """Tests for the safe_json_dumps wrapper."""

    def test_returns_string(self):
        result = safe_json_dumps({'key': 'value'})
        assert isinstance(result, str)

    def test_handles_numpy_int(self):
        result = json.loads(safe_json_dumps({'n': np.int64(7)}))
        assert result['n'] == 7

    def test_handles_datetime(self):
        result = json.loads(safe_json_dumps({'dt': datetime(2024, 1, 1)}))
        assert '2024-01-01' in result['dt']

    def test_handles_numpy_array(self):
        result = json.loads(safe_json_dumps({'arr': np.array([1, 2, 3])}))
        assert result['arr'] == [1, 2, 3]

    def test_accepts_additional_kwargs(self):
        """Keyword args (e.g. sort_keys, indent) should be forwarded."""
        result = safe_json_dumps({'b': 2, 'a': 1}, sort_keys=True)
        # 'a' should appear before 'b' in sorted output
        assert result.index('"a"') < result.index('"b"')

    def test_handles_plain_list(self):
        result = json.loads(safe_json_dumps([1, 2, 3]))
        assert result == [1, 2, 3]

    def test_handles_empty_dict(self):
        result = json.loads(safe_json_dumps({}))
        assert result == {}

    def test_handles_nested_numpy(self):
        data = {'outer': {'inner': np.float32(3.14)}}
        result = json.loads(safe_json_dumps(data))
        assert abs(result['outer']['inner'] - 3.14) < 0.01

    def test_pandas_timestamp_in_dumps(self):
        result = json.loads(safe_json_dumps({'ts': pd.Timestamp('2025-06-01 09:00:00')}))
        assert '2025-06-01' in result['ts']


# ---------------------------------------------------------------------------
# safe_json_dump (file object variant)
# ---------------------------------------------------------------------------

class TestSafeJsonDump:
    """Tests for the safe_json_dump file-object wrapper."""

    def test_writes_to_file_object(self):
        buf = io.StringIO()
        safe_json_dump({'key': 'value'}, buf)
        buf.seek(0)
        result = json.loads(buf.read())
        assert result == {'key': 'value'}

    def test_handles_numpy_int_to_file(self):
        buf = io.StringIO()
        safe_json_dump({'n': np.int32(10)}, buf)
        buf.seek(0)
        result = json.loads(buf.read())
        assert result['n'] == 10

    def test_handles_datetime_to_file(self):
        buf = io.StringIO()
        dt = datetime(2024, 7, 4, 12, 0, 0)
        safe_json_dump({'dt': dt}, buf)
        buf.seek(0)
        result = json.loads(buf.read())
        assert result['dt'] == '2024-07-04 12:00:00'

    def test_handles_numpy_array_to_file(self):
        buf = io.StringIO()
        safe_json_dump({'arr': np.array([10, 20, 30])}, buf)
        buf.seek(0)
        result = json.loads(buf.read())
        assert result['arr'] == [10, 20, 30]

    def test_accepts_additional_kwargs_to_file(self):
        buf = io.StringIO()
        safe_json_dump({'b': 2, 'a': 1}, buf, sort_keys=True)
        buf.seek(0)
        raw = buf.read()
        assert raw.index('"a"') < raw.index('"b"')

    def test_handles_pandas_timedelta_to_file(self):
        buf = io.StringIO()
        safe_json_dump({'td': pd.Timedelta('3 hours')}, buf)
        buf.seek(0)
        result = json.loads(buf.read())
        assert isinstance(result['td'], str)

    def test_real_file(self, tmp_path):
        filepath = tmp_path / 'output.json'
        data = {'x': np.float64(1.23), 'ts': pd.Timestamp('2025-01-01')}
        with open(filepath, 'w') as f:
            safe_json_dump(data, f)
        with open(filepath, 'r') as f:
            result = json.load(f)
        assert abs(result['x'] - 1.23) < 1e-5
        assert '2025-01-01' in result['ts']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
