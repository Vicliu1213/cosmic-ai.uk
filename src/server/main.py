"""
Server Module - Main entry point

Provides HTTP server infrastructure for monitoring, metrics, and state management.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server.app import create_app


def main():
    """
    Main entry point for Server module.
    Starts the monitoring and metrics server.
    """
    try:
        print("🚀 Starting Quantum Metrics Server...")
        app = create_app()
        app.run(host='0.0.0.0', port=8000, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
