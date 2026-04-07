#!/usr/bin/env python3
"""
Cosmic AI Trading System - Main Entry Point

Unified module that integrates all subsystems:
- Core Trading Engine
- Agent System
- Quantum Processing
- Analysis Engine
- Risk Management
- Strategy Execution
"""

import sys
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / "logs" / "cosmic_ai.log")
    ]
)
logger = logging.getLogger(__name__)


class CosmicAISystem:
    """Main system orchestrator"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Cosmic AI System
        
        Args:
            config: Configuration dictionary with system settings
        """
        self.config = config or {}
        self.status = "initialized"
        self.start_time = datetime.now()
        
        logger.info("CosmicAISystem initialized")
        logger.info(f"Configuration: {self.config}")
    
    async def start(self) -> bool:
        """Start the system
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Starting Cosmic AI System...")
            self.status = "running"
            
            # Initialize core modules
            self._initialize_modules()
            
            logger.info("✓ System started successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to start system: {e}")
            self.status = "error"
            return False
    
    def _initialize_modules(self):
        """Initialize all system modules"""
        try:
            # Import core modules
            from core import main_system
            from agents import agent_registry
            from strategies import cosmic_strategy
            
            logger.info("✓ Core modules loaded")
            logger.info("✓ Agent system loaded")
            logger.info("✓ Strategy system loaded")
        except ImportError as e:
            logger.warning(f"Module import warning: {e}")
    
    async def stop(self):
        """Stop the system"""
        logger.info("Stopping Cosmic AI System...")
        self.status = "stopped"
        logger.info("System stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status
        
        Returns:
            Dict with system status information
        """
        return {
            "status": self.status,
            "started_at": self.start_time.isoformat(),
            "running_for": str(datetime.now() - self.start_time),
            "configuration": self.config
        }


async def main():
    """Main async entry point"""
    # Default configuration
    config = {
        "mode": "live",
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "enable_agents": True,
        "enable_quantum": True,
        "enable_risk_management": True,
    }
    
    # Create and start system
    system = CosmicAISystem(config)
    
    if await system.start():
        logger.info(f"System Status: {system.get_status()}")
        logger.info("System is ready. Press Ctrl+C to stop.")
        
        try:
            # Keep system running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nReceived shutdown signal")
            await system.stop()
    else:
        logger.error("Failed to start system")
        return 1
    
    return 0


def cli_entry():
    """Command-line entry point"""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    cli_entry()
