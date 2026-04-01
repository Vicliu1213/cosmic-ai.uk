#!/usr/bin/env python3
"""
Dashboard Module
儀表板模塊

Web dashboard for Comic AI trading system monitoring and visualization.
Comic AI 交易系統監控和可視化的網絡儀表板。
"""

import logging

logger = logging.getLogger(__name__)

# Export main components
from .app import app

__all__ = ['app']
