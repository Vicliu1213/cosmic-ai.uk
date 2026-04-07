"""
Phase5 Module - Main entry point

Provides complete trading system with order execution, management, and settlement.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.phase5.trading_system_init import TradingSystemInitializer


def main():
    """
    Main entry point for Phase5 module.
    Initializes and starts the complete trading system.
    """
    try:
        print("🚀 Starting Phase5 Trading System...")
        system = TradingSystemInitializer()
        system.initialize()
        system.start()
    except Exception as e:
        print(f"❌ Error starting trading system: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
