"""
Backtesting Module - Main entry point

Provides comprehensive backtesting framework for strategy evaluation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backtesting.unified_backtester import UnifiedBacktester


def main():
    """
    Main entry point for Backtesting module.
    Runs backtesting on configured strategies with real market data.
    """
    try:
        print("🚀 Starting Unified Backtester...")
        backtester = UnifiedBacktester()
        backtester.run()
    except Exception as e:
        print(f"❌ Error running backtester: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
