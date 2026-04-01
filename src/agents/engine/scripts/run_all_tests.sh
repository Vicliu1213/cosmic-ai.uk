#!/bin/bash
# 執行所有理論模塊的測試

echo "Running all theory tests..."
cd "$(dirname "$0")/../tests"

# 執行 pytest
python -m pytest test_*.py -v

echo "Test execution completed!"
