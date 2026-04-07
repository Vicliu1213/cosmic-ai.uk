"""
CLI Module - Main entry point

Provides command-line interface for system control and management.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.cli import main as cli_main


def main():
    """
    Main entry point for CLI.
    Starts the command-line interface for system control.
    """
    try:
        print("🚀 Starting Cosmic AI CLI...")
        cli_main()
    except Exception as e:
        print(f"❌ Error starting CLI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
