#!/usr/bin/env python3
"""
Dashboard App Router
This file re-exports the FastAPI app from src.server.app
原始的 LLM-TradeBot Dashboard 應用
"""

from src.server.app import app

__all__ = ['app']
