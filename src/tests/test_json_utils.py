#!/usr/bin/env python3
"""
Tests for src/utils/json_utils.py

Covers: CustomJSONEncoder, safe_json_dump, safe_json_dumps
for datetime, numpy scalar/array, pandas Timestamp/Timedelta, and standard types.
"""

import io
import json
import sys
import os
import pytest

import numpy as np
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.json_utils import CustomJSONEncoder, safe_json_dump, safe_json_dumps


# ─── helpers ──────────────────────────────────────────────────────────────────

def _encode(obj) -> str:
    """Shorthand for encoding a single object."""
    return json.dumps(obj, cls=CustomJSONEncoder)


def _decode(obj):
    """Round-trip a value through the encoder."""
    return json.loads(_encode(obj))


# ─── CustomJSONEncoder ────────────────────────────────────────────────────────

class TestCustomJSONEncoderDatetime:
    """datetime → formatted string."""

    def test_datetime_format(self):
        dt = datetime(2024, 3, 15, 10, 30, 0)
        result = _decode(dt)
        assert result == "2024-03-15 10:30:00"

    def test_datetime_midnight(self):
        dt = datetime(2025, 1, 1, 0, 0, 0)
        assert _decode(dt) == "2025-01-01 00:00:00"

    def test_datetime_in_dict(self):
        payload = {"ts": datetime(2024, 6, 21, 12, 0, 0)}
        result = _decode(payload)
        assert result["ts"] == "2024-06-21 12:00:00"

    def test_datetime_in_list(self):
        payload = [datetime(2024, 1, 2, 3, 4, 5)]
        result = _decode(payload)
        assert result[0] == "2024-01-02 03:04:05"


class TestCustomJSONEncoderNumpy:
    """numpy scalars → Python int/float/bool, ndarray → list."""

    @pytest.mark.parametrize("dtype", [np.int32, np.int64])
    def test_numpy_integer_types(self, dtype):
        val = dtype(42)
        result = _decode(val)
        assert result == 42
        assert isinstance(result, int)

    @pytest.mark.parametrize("dtype", [np.float32, np.float64])
    def test_numpy_float_types(self, dtype):
        val = dtype(3.14)
        result = _decode(val)
        assert abs(result - 3.14) < 1e-5
        assert isinstance(result, float)

    def test_numpy_bool_true(self):
        result = _decode(np.bool_(True))
        assert result is True
        assert isinstance(result, bool)

    def test_numpy_bool_false(self):
        result = _decode(np.bool_(False))
        assert result is False

    def test_numpy_ndarray_1d(self):
        arr = np.array([1, 2, 3])
        result = _decode(arr)
        assert result == [1, 2, 3]

    def test_numpy_ndarray_2d(self):
        arr = np.array([[1, 2], [3, 4]])
        result = _decode(arr)
        assert result == [[1, 2], [3, 4]]

    def test_numpy_ndarray_float(self):
        arr = np.array([1.5, 2.5])
        result = _decode(arr)
        assert len(result) == 2

    def test_numpy_ndarray_empty(self):
        result = _decode(np.array([]))
        assert result == []


class TestCustomJSONEncoderPandas:
    """pandas Timestamp / Timedelta → string."""

    def test_pandas_timestamp(self):
        ts = pd.Timestamp("2024-07-04 09:00:00")
        result = _decode(ts)
        assert result == "2024-07-04 09:00:00"

    def test_pandas_timedelta(self):
        td = pd.Timedelta("1 days 02:03:04")
        result = _decode(td)
        assert isinstance(result, str)
        assert "1 day" in result or "days" in result or "0 days" in result

    def test_pandas_timestamp_in_dict(self):
        payload = {"time": pd.Timestamp("2025-12-31 23:59:59")}
        result = _decode(payload)
        assert result["time"] == "2025-12-31 23:59:59"


class TestCustomJSONEncoderStandardTypes:
    """Standard JSON-serialisable types must pass through unchanged."""

    def test_string(self):
        assert _decode("hello") == "hello"

    def test_int(self):
        assert _decode(42) == 42

    def test_float(self):
        assert abs(_decode(3.14) - 3.14) < 1e-10

    def test_bool_true(self):
        assert _decode(True) is True

    def test_bool_false(self):
        assert _decode(False) is False

    def test_none(self):
        assert _decode(None) is None

    def test_list(self):
        assert _decode([1, 2, 3]) == [1, 2, 3]

    def test_nested_dict(self):
        payload = {"a": {"b": [1, 2]}}
        assert _decode(payload) == {"a": {"b": [1, 2]}}


class TestCustomJSONEncoderFallthrough:
    """Unsupported types must raise TypeError via super().default()."""

    def test_set_raises(self):
        with pytest.raises(TypeError):
            json.dumps({1, 2, 3}, cls=CustomJSONEncoder)

    def test_custom_object_raises(self):
        class MyObj:
            pass

        with pytest.raises(TypeError):
            json.dumps(MyObj(), cls=CustomJSONEncoder)


# ─── safe_json_dumps ──────────────────────────────────────────────────────────

class TestSafeJsonDumps:
    """safe_json_dumps wraps json.dumps with CustomJSONEncoder."""

    def test_returns_string(self):
        result = safe_json_dumps({"key": "value"})
        assert isinstance(result, str)

    def test_encodes_datetime(self):
        result = safe_json_dumps({"ts": datetime(2024, 1, 1, 0, 0, 0)})
        assert "2024-01-01 00:00:00" in result

    def test_encodes_numpy_integer(self):
        result = safe_json_dumps(np.int64(7))
        assert result == "7"

    def test_encodes_numpy_float(self):
        result = safe_json_dumps(np.float32(1.5))
        assert "1.5" in result

    def test_encodes_ndarray(self):
        result = safe_json_dumps(np.array([10, 20, 30]))
        assert result == "[10, 20, 30]"

    def test_passthrough_indent_kwarg(self):
        result = safe_json_dumps({"a": 1}, indent=2)
        assert "\n" in result

    def test_passthrough_sort_keys_kwarg(self):
        result = safe_json_dumps({"b": 2, "a": 1}, sort_keys=True)
        assert result.index('"a"') < result.index('"b"')

    def test_mixed_numpy_datetime(self):
        payload = {
            "price": np.float64(100.5),
            "qty": np.int32(3),
            "ts": datetime(2024, 2, 14, 12, 0, 0),
        }
        result = json.loads(safe_json_dumps(payload))
        assert result["qty"] == 3
        assert abs(result["price"] - 100.5) < 1e-5
        assert result["ts"] == "2024-02-14 12:00:00"


# ─── safe_json_dump ───────────────────────────────────────────────────────────

class TestSafeJsonDump:
    """safe_json_dump writes to a file-like object using CustomJSONEncoder."""

    def test_writes_to_buffer(self):
        buf = io.StringIO()
        safe_json_dump({"hello": "world"}, buf)
        buf.seek(0)
        assert json.load(buf) == {"hello": "world"}

    def test_encodes_datetime_to_file(self):
        buf = io.StringIO()
        safe_json_dump({"ts": datetime(2024, 5, 5, 5, 5, 5)}, buf)
        buf.seek(0)
        result = json.load(buf)
        assert result["ts"] == "2024-05-05 05:05:05"

    def test_encodes_numpy_to_file(self):
        buf = io.StringIO()
        safe_json_dump(np.int64(99), buf)
        buf.seek(0)
        assert json.load(buf) == 99

    def test_indent_kwarg_forwarded(self):
        buf = io.StringIO()
        safe_json_dump({"a": 1}, buf, indent=4)
        buf.seek(0)
        raw = buf.read()
        assert "    " in raw  # 4-space indent present


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
