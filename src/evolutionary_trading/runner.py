#!/usr/bin/env python3
"""
runner.py - 進化量化交易系統啟動入口
自動設定 sys.path，然後執行 evolutionary_trading_system.main()
"""
import sys, asyncio
from pathlib import Path

# 保證 dna_evolution 可被 import
_ROOT = Path(__file__).resolve().parents[2]
_PKG  = Path(__file__).resolve().parent
for p in [str(_ROOT), str(_PKG), str(_ROOT / "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 把 dna_evolution 也注入頂層，讓 evolutionary_trading_system 能 import
import importlib, types
_dna = importlib.import_module("src.evolutionary_trading.dna_evolution")
sys.modules.setdefault("dna_evolution", _dna)

from src.evolutionary_trading.evolutionary_trading_system import main

if __name__ == "__main__":
    asyncio.run(main())
