"""
策略模組 - 包含所有交易策略實現

主要策略:
- CosmicStrategy: 整合共振、超進化、持續進化的終極交易系統
- AegisStrategy: 隱形風控哨兵策略，支持自動止損/止盈
"""

import sys
from pathlib import Path

__all__ = ['CosmicStrategy', 'AegisStrategy']

# 延遲加載以避免重型依賴導入問題
def __getattr__(name):
    """延遲加載策略類，支持漸進式依賴初始化"""
    try:
        if name == 'CosmicStrategy':
            from .cosmic_strategy import CosmicStrategy
            return CosmicStrategy
        elif name == 'AegisStrategy':
            from .main import AegisStrategy
            return AegisStrategy
        else:
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    except ImportError as e:
        raise ImportError(f"Failed to import {name} from {__name__}: {str(e)}")

def list_available_strategies():
    """列出所有可用策略"""
    return ['CosmicStrategy', 'AegisStrategy']

# 模組版本
__version__ = '1.0.0'
__author__ = 'Cosmic AI Trading Team'
