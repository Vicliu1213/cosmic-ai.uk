"""
API Module - Main entry point

Provides REST API server and trading API clients.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.server import create_app, run_server


def main():
    """
    Main entry point for API server.
    Starts the REST API server for trading and market data access.
    """
    try:
        print("🚀 Starting API Server...")
        app = create_app()
        run_server(app)
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
