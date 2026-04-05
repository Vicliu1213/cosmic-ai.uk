"""
風險模塊 (Risk Module)

負責交易風險管理和控制，包括：
- 風險管理器 (RiskManager)
- 風險指標計算
- 組合風險評估
"""

import logging

logger = logging.getLogger(__name__)

# 導入風險相關類
try:
    from .manager import RiskManager
    logger.info("✅ RiskManager imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import RiskManager: {e}")
    RiskManager = None

__all__ = [
    'RiskManager',
]
