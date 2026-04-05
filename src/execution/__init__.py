"""
執行模塊 (Execution Module)

負責交易訂單的執行、管理和追蹤，包括：
- 訂單執行引擎 (ExecutionEngine)
- 量子閃電執行器 (QuantumFlashExecutor)
"""

import logging

logger = logging.getLogger(__name__)

# 導入執行相關類
try:
    from .engine import ExecutionEngine
    logger.info("✅ ExecutionEngine imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import ExecutionEngine: {e}")
    ExecutionEngine = None

try:
    from .quantum_flash_executor import QuantumFlashExecutor
    logger.info("✅ QuantumFlashExecutor imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import QuantumFlashExecutor: {e}")
    QuantumFlashExecutor = None

__all__ = [
    'ExecutionEngine',
    'QuantumFlashExecutor',
]
