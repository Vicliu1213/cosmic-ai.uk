"""
OpenCode Module - Main entry point

Provides universal AI agent with enhanced capabilities and multi-system integration.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.opencode.universal_agent import UniversalAgent


def main():
    """
    Main entry point for OpenCode module.
    Initializes and runs the universal AI agent.
    """
    try:
        print("🚀 Starting OpenCode Universal Agent...")
        agent = UniversalAgent()
        agent.run()
    except Exception as e:
        print(f"❌ Error starting universal agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
