#!/usr/bin/env python3
"""
Trading System Initialization Module - Phase 5
交易系統初始化模塊 - 第5階段

Handles system initialization, configuration loading, and component setup.
管理系統初始化、配置加載和組件設置。

Features:
- Configuration loading and validation
- Logging setup
- Phase 1-4 system initialization
- API client setup
- Database initialization
- Performance baseline setup

Usage:
    from src.phase5.trading_system_init import TradingSystemInitializer
    
    initializer = TradingSystemInitializer(config_path="config/trading_config.yaml")
    system = await initializer.initialize()
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import asyncio
import yaml
import json

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.quantum_verification_layer import QuantumVerificationLayer
from src.core.market_regime_detector import MarketRegimeDetector
from src.core.theory_optimizer import DynamicTheoryOptimizer
from src.core.phase1_integration import Phase1IntegrationEngine
from src.core.resonance_detection_engine import ResonanceDetectionEngine
from src.core.multi_agent_resonance_module import MultiAgentResonanceModule
from src.core.cma_es_adaptive_evolution import AdaptiveEvolutionCoordinator
from src.core.sharpe_target_engine import SharpeTargetEngine
from src.core.dynamic_risk_management import DynamicRiskManagementEngine
from src.core.singularity_detection_system import SingularityDetectionSystem
from src.core.triangular_arbitrage_engine import TriangularArbitrageEngine
from src.core.wormhole_arbitrage_module import WormholeArbitrageModule
from src.core.hummingbot_integration_layer import HummingbotIntegrationLayer


# ============================================================================
# Logging Configuration
# ============================================================================

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging for trading system"""
    logger = logging.getLogger("cosmic_trading")
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class TradingSystemConfig:
    """Trading system configuration"""
    system_name: str
    version: str
    phase: int
    mode: str  # sandbox, paper, live
    start_capital: float
    log_level: str
    log_file: Optional[str]
    data_dir: Path
    api_keys: Dict[str, str]
    phase_enabled: Dict[str, bool]
    performance_targets: Dict[str, float]
    risk_config: Dict[str, float]


@dataclass
class SystemInitializationResult:
    """System initialization result"""
    success: bool
    message: str
    components_initialized: Dict[str, bool]
    config: Optional[TradingSystemConfig] = None
    errors: Dict[str, str] = None
    warnings: Dict[str, str] = None
    initialization_time: float = 0.0


# ============================================================================
# Configuration Manager
# ============================================================================

class ConfigurationManager:
    """Manage system configuration"""
    
    def __init__(self, config_path: str, env_file: str = ".env"):
        self.config_path = Path(config_path)
        self.env_file = Path(env_file)
        self.config = None
        self.env_vars = {}
    
    def load_env_variables(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        env_vars = {}
        
        if self.env_file.exists():
            with open(self.env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
        
        self.env_vars = env_vars
        return env_vars
    
    def load_yaml_config(self) -> Dict[str, Any]:
        """Load YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
        
        self.config = config
        return config
    
    def resolve_config_value(self, value: Any) -> Any:
        """Resolve configuration value (expand env vars)"""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            var_name = value[2:-1]
            return self.env_vars.get(var_name, value)
        return value
    
    def build_trading_config(self) -> TradingSystemConfig:
        """Build TradingSystemConfig from loaded configuration"""
        if not self.config:
            self.load_yaml_config()
        if not self.env_vars:
            self.load_env_variables()
        
        system_cfg = self.config.get('system', {})
        env_cfg = self.config.get('environment', {})
        phase_cfg = self.config.get('phase1', {})
        perf_cfg = self.config.get('backtesting', {}).get('targets', {})
        risk_cfg = phase_cfg.get('risk', {})
        
        return TradingSystemConfig(
            system_name=system_cfg.get('name', 'Cosmic AI Trading System'),
            version=system_cfg.get('version', '1.0.0'),
            phase=system_cfg.get('phase', 5),
            mode=system_cfg.get('mode', 'sandbox'),
            start_capital=system_cfg.get('start_capital', 500),
            log_level=env_cfg.get('logging', {}).get('level', 'INFO'),
            log_file=env_cfg.get('logging', {}).get('file'),
            data_dir=Path(env_cfg.get('directories', {}).get('data', 'data/')),
            api_keys=self.config.get('exchanges', {}),
            phase_enabled={
                'phase1': self.config.get('phase1', {}).get('enabled', True),
                'phase2': self.config.get('phase2', {}).get('enabled', True),
                'phase3': self.config.get('phase3', {}).get('enabled', True),
                'phase4': self.config.get('phase4', {}).get('enabled', True),
            },
            performance_targets={
                'sharpe_ratio': perf_cfg.get('min_sharpe_ratio', 3.0),
                'win_rate': perf_cfg.get('min_win_rate', 0.90),
                'max_drawdown': perf_cfg.get('max_drawdown', 0.10),
            },
            risk_config={
                'max_drawdown': risk_cfg.get('max_drawdown_pct', 10.0) / 100,
                'max_leverage': risk_cfg.get('max_leverage', 2.0),
                'var_confidence': risk_cfg.get('var_confidence', 0.95),
            }
        )


# ============================================================================
# System Initializer
# ============================================================================

class TradingSystemInitializer:
    """Initialize trading system components"""
    
    def __init__(self, config_path: str = "config/trading_config.yaml"):
        self.config_path = config_path
        self.logger = setup_logging()
        self.config_manager = ConfigurationManager(config_path)
        self.config = None
        self.components = {}
        self.initialization_start = None
    
    async def initialize(self) -> SystemInitializationResult:
        """Initialize all system components"""
        self.initialization_start = datetime.now()
        
        try:
            self.logger.info("=" * 80)
            self.logger.info("COSMIC AI TRADING SYSTEM - INITIALIZATION")
            self.logger.info("=" * 80)
            
            # Load configuration
            self.logger.info("Loading configuration...")
            self.config = self.config_manager.build_trading_config()
            self.logger.info(f"✅ Configuration loaded: {self.config.system_name} v{self.config.version}")
            
            # Create directories
            self.logger.info("Creating data directories...")
            self._create_directories()
            self.logger.info("✅ Directories created")
            
            # Initialize components
            self.logger.info("Initializing trading system components...")
            components_initialized = await self._initialize_components()
            
            # Calculate initialization time
            init_time = (datetime.now() - self.initialization_start).total_seconds()
            
            self.logger.info(f"✅ System initialization complete in {init_time:.2f}s")
            self.logger.info("=" * 80)
            
            return SystemInitializationResult(
                success=True,
                message="Trading system initialized successfully",
                components_initialized=components_initialized,
                config=self.config,
                initialization_time=init_time
            )
        
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            return SystemInitializationResult(
                success=False,
                message=f"Initialization failed: {str(e)}",
                components_initialized=self.components,
                errors={"initialization": str(e)}
            )
    
    def _create_directories(self) -> None:
        """Create required directories"""
        directories = [
            self.config.data_dir,
            self.config.data_dir / "backtest",
            self.config.data_dir / "real_time",
            Path("logs"),
            Path("reports"),
        ]
        
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created/verified directory: {dir_path}")
    
    async def _initialize_components(self) -> Dict[str, bool]:
        """Initialize all enabled components"""
        components = {}
        
        # Phase 1 Components
        if self.config.phase_enabled['phase1']:
            try:
                self.logger.info("Initializing Phase 1 (Foundation Layer)...")
                components['quantum_verification'] = bool(QuantumVerificationLayer())
                components['market_regime'] = bool(MarketRegimeDetector())
                components['theory_optimizer'] = bool(DynamicTheoryOptimizer())
                components['phase1_integration'] = bool(Phase1IntegrationEngine())
                self.logger.info("✅ Phase 1 components initialized")
            except Exception as e:
                self.logger.error(f"❌ Phase 1 initialization failed: {str(e)}")
                components['phase1'] = False
        
        # Phase 2 Components
        if self.config.phase_enabled['phase2']:
            try:
                self.logger.info("Initializing Phase 2 (Resonance Breakthrough Layer)...")
                components['resonance_detection'] = bool(ResonanceDetectionEngine())
                components['multi_agent_resonance'] = bool(MultiAgentResonanceModule())
                components['cma_es_evolution'] = bool(AdaptiveEvolutionCoordinator())
                self.logger.info("✅ Phase 2 components initialized")
            except Exception as e:
                self.logger.error(f"❌ Phase 2 initialization failed: {str(e)}")
                components['phase2'] = False
        
        # Phase 3 Components
        if self.config.phase_enabled['phase3']:
            try:
                self.logger.info("Initializing Phase 3 (Singularity Optimization Layer)...")
                components['sharpe_target'] = bool(SharpeTargetEngine())
                components['dynamic_risk'] = bool(DynamicRiskManagementEngine())
                components['singularity_detection'] = bool(SingularityDetectionSystem())
                self.logger.info("✅ Phase 3 components initialized")
            except Exception as e:
                self.logger.error(f"❌ Phase 3 initialization failed: {str(e)}")
                components['phase3'] = False
        
        # Phase 4 Components
        if self.config.phase_enabled['phase4']:
            try:
                self.logger.info("Initializing Phase 4 (Arbitrage Integration Layer)...")
                components['triangular_arbitrage'] = bool(TriangularArbitrageEngine())
                components['wormhole_arbitrage'] = bool(WormholeArbitrageModule())
                components['hummingbot_integration'] = bool(HummingbotIntegrationLayer())
                self.logger.info("✅ Phase 4 components initialized")
            except Exception as e:
                self.logger.error(f"❌ Phase 4 initialization failed: {str(e)}")
                components['phase4'] = False
        
        self.components = components
        return components


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Trading System")
    parser.add_argument('--config', default='config/trading_config.yaml', help='Config file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize system
    initializer = TradingSystemInitializer(config_path=args.config)
    result = await initializer.initialize()
    
    # Print results
    print("\nInitialization Result:")
    print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"Message: {result.message}")
    print(f"Time: {result.initialization_time:.2f}s")
    print(f"\nComponents Initialized:")
    for component, status in result.components_initialized.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {component}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
