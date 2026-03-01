#!/usr/bin/env python3
"""
Plugin Auto-Loader for Comic AI
插件自動加載系統

Automatically initializes and loads all available plugins on startup.
自動在啟動時初始化和加載所有可用的插件。
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
import importlib
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # /root/comic_ai
sys.path.insert(0, str(PROJECT_ROOT))

class PluginLoader:
    """Automatic plugin loader for Comic AI"""
    
    def __init__(self) -> Any:
        self.plugins_dir = PROJECT_ROOT / "src" / "plugins"
        self.loaded_plugins: Dict[str, Any] = {}
        self.config_file = PROJECT_ROOT / ".config" / "plugins_config.json"
        self.log_file = PROJECT_ROOT / ".config" / "plugins_load.log"
        
    def load_config(self) -> Dict[str, Any]:
        """Load plugin configuration"""
        default_config = {
            "enabled": True,
            "plugins": {
                "multi_agent_trading": {
                    "enabled": True,
                    "description": "Multi-Agent Trading System",
                    "auto_start": True
                }
            },
            "auto_load_on_startup": True,
            "log_level": "INFO"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    logger.info(f"✅ Loaded plugin config from {self.config_file}")
                    return config
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}, using defaults")
        
        # Save default config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.info(f"✅ Created default plugin config at {self.config_file}")
        
        return default_config
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins"""
        plugins = []
        
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return plugins
        
        # Look for Python plugin files
        for plugin_file in self.plugins_dir.glob("*.py"):
            if not plugin_file.name.startswith("_"):
                plugin_name = plugin_file.stem
                plugins.append(plugin_name)
                logger.info(f"🔍 Discovered plugin: {plugin_name}")
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        try:
            # Try different import paths
            import_paths = [
                f"src.plugins.{plugin_name}",
                f"plugins.{plugin_name}"
            ]
            
            plugin_module = None
            for import_path in import_paths:
                try:
                    plugin_module = importlib.import_module(import_path)
                    logger.info(f"✅ Loaded plugin: {plugin_name}")
                    self.loaded_plugins[plugin_name] = plugin_module
                    return True
                except ImportError:
                    continue
            
            if plugin_module is None:
                logger.error(f"❌ Failed to load plugin: {plugin_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading plugin {plugin_name}: {e}")
            return False
    
    def initialize_multi_agent_trading(self) -> bool:
        """Initialize multi-agent trading system"""
        try:
            from src.plugins.multi_agent_trading import (
                MultiAgentCoordinator,
                PortfolioManagementAgent,
                RiskManagementAgent,
                SignalAnalysisAgent
            )
            
            logger.info("🚀 Initializing Multi-Agent Trading System...")
            
            # Create coordinator
            coordinator = MultiAgentCoordinator()
            
            # Create and register agents
            pm_agent = PortfolioManagementAgent(
                agent_id='pm_1',
                target_allocations={'AAPL': 0.3, 'MSFT': 0.3, 'GOOGL': 0.4}
            )
            
            rm_agent = RiskManagementAgent(
                agent_id='rm_1',
                max_position_size=0.1,
                max_portfolio_loss=0.02
            )
            
            sa_agent = SignalAnalysisAgent(
                agent_id='sa_1',
                sma_short=20,
                sma_long=50
            )
            
            coordinator.register_agent(pm_agent)
            coordinator.register_agent(rm_agent)
            coordinator.register_agent(sa_agent)
            
            logger.info("✅ Multi-Agent Trading System initialized")
            logger.info(f"   - Portfolio Manager: {pm_agent.agent_id}")
            logger.info(f"   - Risk Manager: {rm_agent.agent_id}")
            logger.info(f"   - Signal Analyst: {sa_agent.agent_id}")
            
            self.loaded_plugins['multi_agent_trading_coordinator'] = coordinator
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Multi-Agent Trading: {e}")
            return False
    
    def load_all_plugins(self) -> bool:
        """Load all enabled plugins"""
        logger.info("=" * 80)
        logger.info("🔄 Starting Plugin Auto-Loader...")
        logger.info("=" * 80)
        
        config = self.load_config()
        
        if not config.get("enabled", False):
            logger.warning("⚠️ Plugin system is disabled in config")
            return False
        
        success_count = 0
        failed_count = 0
        
        # Load discovered plugins
        discovered = self.discover_plugins()
        plugins_config = config.get("plugins", {})
        
        for plugin_name in discovered:
            plugin_config = plugins_config.get(plugin_name, {"enabled": False})
            
            if not plugin_config.get("enabled", False):
                logger.info(f"⏭️  Skipping disabled plugin: {plugin_name}")
                continue
            
            if self.load_plugin(plugin_name):
                success_count += 1
                
                # Initialize special plugins
                if plugin_name == "multi_agent_trading":
                    if self.initialize_multi_agent_trading():
                        success_count += 1
                    else:
                        failed_count += 1
            else:
                failed_count += 1
        
        # Log summary
        logger.info("=" * 80)
        logger.info(f"✅ Plugin Loading Summary:")
        logger.info(f"   - Plugins Loaded: {success_count}")
        logger.info(f"   - Plugins Failed: {failed_count}")
        logger.info(f"   - Loaded Plugins: {list(self.loaded_plugins.keys())}")
        logger.info("=" * 80)
        
        # Write log
        self.write_log(success_count, failed_count)
        
        return failed_count == 0
    
    def write_log(self, success: int, failed: int) -> Any:
        """Write plugin loading log"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "loaded_count": success,
            "failed_count": failed,
            "loaded_plugins": list(self.loaded_plugins.keys()),
            "status": "success" if failed == 0 else "partial_failure"
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_loaded_plugins(self) -> Dict[str, Any]:
        """Get all loaded plugins"""
        return self.loaded_plugins

def auto_load_plugins() -> Any:
    """Main entry point for auto-loading plugins"""
    loader = PluginLoader()
    loader.load_all_plugins()
    return loader.get_loaded_plugins()

if __name__ == "__main__":
    plugins = auto_load_plugins()
    print("\n🎉 Plugin Auto-Loading Complete!")
    print(f"Loaded {len(plugins)} plugin(s)")
