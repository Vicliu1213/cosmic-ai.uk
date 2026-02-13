#!/usr/bin/env python3
"""
API Module
API 模塊

REST API endpoints and server configuration for Comic AI trading system.
Comic AI 交易系統的 REST API 端點和服務器配置。
"""

import logging

logger = logging.getLogger(__name__)

# Export main components
from .server import app

__all__ = ['app']
