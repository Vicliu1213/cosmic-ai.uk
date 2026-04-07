"""
Automation Module - Main entry point

Provides automated daemon systems for evolution, file processing, and monitoring.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.automation.daemon_manager import DaemonManager


def main():
    """
    Main entry point for Automation module.
    Starts daemon managers for automated evolution and file processing.
    """
    try:
        print("🚀 Starting Automation Daemon Manager...")
        manager = DaemonManager()
        manager.start()
    except Exception as e:
        print(f"❌ Error starting automation daemon: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
