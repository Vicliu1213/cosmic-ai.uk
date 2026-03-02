#!/usr/bin/env python3
"""
API Configuration Manager
API 設定管理器

Manages loading and validating API keys and exchange configurations
from .env files and configuration YAML.

This module handles:
1. Environment variable loading
2. API key validation
3. Exchange configuration initialization
4. Configuration file parsing
5. Secret management
"""

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from enum import Enum

import yaml
from dotenv import load_dotenv

from src.phase5.exchange_connector import (
    ExchangeConfig,
    ExchangeType,
    TradingMode,
    MultiExchangeManager
)


# ============================================================================
# Constants
# ============================================================================

ENV_TEMPLATE_PATH = Path(".env.template")
ENV_FILE_PATH = Path(".env")
CONFIG_TEMPLATE_PATH = Path("config/trading_config_template.yaml")
CONFIG_FILE_PATH = Path("config/trading_config.yaml")

# Required environment variables for each exchange
EXCHANGE_REQUIREMENTS = {
    ExchangeType.BINANCE: ["BINANCE_API_KEY", "BINANCE_API_SECRET"],
    ExchangeType.KRAKEN: ["KRAKEN_API_KEY", "KRAKEN_API_SECRET"],
    ExchangeType.COINBASE: ["COINBASE_API_KEY", "COINBASE_API_SECRET"],
}

# Pattern for detecting placeholder values
PLACEHOLDER_PATTERN = re.compile(
    r"^(your_.*|.*_here|.*_placeholder|xxx|demo.*|test.*)$",
    re.IGNORECASE
)


# ============================================================================
# Enums
# ============================================================================

class ValidationStatus(Enum):
    """Configuration validation status."""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    MISSING = "missing"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ValidationResult:
    """Result of configuration validation."""
    status: ValidationStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EnvironmentCheck:
    """Result of environment variable check."""
    variable_name: str
    status: ValidationStatus
    value_present: bool
    is_placeholder: bool
    message: str


@dataclass
class ExchangeConfigStatus:
    """Status of exchange configuration."""
    exchange_type: ExchangeType
    enabled: bool
    api_key_present: bool
    api_secret_present: bool
    config_valid: bool
    message: str


# ============================================================================
# API Configuration Manager
# ============================================================================

class APIConfigurationManager:
    """Manages API configurations and environment variables."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize API configuration manager.
        
        Args:
            project_root: Project root directory (defaults to cwd)
        """
        self.project_root = project_root or Path.cwd()
        self.logger = logging.getLogger("APIConfigurationManager")
        self.env_vars: Dict[str, str] = {}
        self.config: Dict[str, Any] = {}
        self.validation_results: List[ValidationResult] = []
        self._exchange_manager: Optional[MultiExchangeManager] = None

    def load_environment(self, env_file: Optional[Path] = None) -> bool:
        """Load environment variables from .env file.
        
        Args:
            env_file: Path to .env file (defaults to .env)
            
        Returns:
            True if loaded successfully
        """
        env_path = env_file or (self.project_root / ENV_FILE_PATH)

        if not env_path.exists():
            self.logger.warning(f".env file not found at {env_path}")
            return False

        try:
            load_dotenv(env_path)
            self.env_vars = dict(os.environ)
            self.logger.info(f"Loaded environment from {env_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load environment: {e}")
            return False

    def load_configuration(self, config_file: Optional[Path] = None) -> bool:
        """Load configuration from YAML file.
        
        Args:
            config_file: Path to config YAML (defaults to config/trading_config.yaml)
            
        Returns:
            True if loaded successfully
        """
        config_path = config_file or (self.project_root / CONFIG_FILE_PATH)

        if not config_path.exists():
            self.logger.warning(f"Config file not found at {config_path}")
            return False

        try:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False

    def resolve_env_variables(self, value: str) -> str:
        """Resolve environment variables in string values.
        
        Handles ${VAR} syntax for environment variable substitution.
        
        Args:
            value: String possibly containing ${VAR} placeholders
            
        Returns:
            String with environment variables resolved
        """
        if not isinstance(value, str):
            return value

        def replace_env(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return re.sub(r'\$\{([^}]+)\}', replace_env, value)

    def check_environment_variables(self) -> Dict[str, EnvironmentCheck]:
        """Check required environment variables.
        
        Returns:
            Dict mapping variable names to check results
        """
        results = {}

        # Check exchange-specific variables
        all_required = set()
        for exchange_vars in EXCHANGE_REQUIREMENTS.values():
            all_required.update(exchange_vars)

        for var_name in all_required:
            value = os.environ.get(var_name, "")
            is_placeholder = bool(PLACEHOLDER_PATTERN.match(value)) if value else False

            if not value:
                status = ValidationStatus.MISSING
                message = f"Environment variable {var_name} not set"
            elif is_placeholder:
                status = ValidationStatus.WARNING
                message = f"Environment variable {var_name} appears to be placeholder"
            else:
                status = ValidationStatus.VALID
                message = f"Environment variable {var_name} is set"

            results[var_name] = EnvironmentCheck(
                variable_name=var_name,
                status=status,
                value_present=bool(value),
                is_placeholder=is_placeholder,
                message=message
            )

        return results

    def validate_exchange_config(
        self,
        exchange_type: ExchangeType,
        config_section: Dict[str, Any]
    ) -> ExchangeConfigStatus:
        """Validate exchange configuration.
        
        Args:
            exchange_type: Exchange type
            config_section: Configuration section for exchange
            
        Returns:
            ExchangeConfigStatus with validation result
        """
        if not config_section.get("enabled", False):
            return ExchangeConfigStatus(
                exchange_type=exchange_type,
                enabled=False,
                api_key_present=False,
                api_secret_present=False,
                config_valid=True,
                message=f"{exchange_type.value} is disabled"
            )

        required_vars = EXCHANGE_REQUIREMENTS[exchange_type]
        api_key_present = bool(os.environ.get(required_vars[0]))
        api_secret_present = bool(os.environ.get(required_vars[1]))

        if not api_key_present or not api_secret_present:
            missing = []
            if not api_key_present:
                missing.append(required_vars[0])
            if not api_secret_present:
                missing.append(required_vars[1])

            return ExchangeConfigStatus(
                exchange_type=exchange_type,
                enabled=True,
                api_key_present=api_key_present,
                api_secret_present=api_secret_present,
                config_valid=False,
                message=f"Missing credentials: {', '.join(missing)}"
            )

        return ExchangeConfigStatus(
            exchange_type=exchange_type,
            enabled=True,
            api_key_present=api_key_present,
            api_secret_present=api_secret_present,
            config_valid=True,
            message=f"{exchange_type.value} configuration is valid"
        )

    def create_exchange_configs(self) -> Dict[ExchangeType, Optional[ExchangeConfig]]:
        """Create exchange configurations from loaded config and env vars.
        
        Returns:
            Dict mapping exchange types to ExchangeConfig
        """
        configs = {}
        exchanges_config = self.config.get("exchanges", {})

        for exchange_type in ExchangeType:
            exchange_key = exchange_type.value
            exchange_cfg = exchanges_config.get(exchange_key, {})

            if not exchange_cfg.get("enabled", False):
                self.logger.debug(f"{exchange_type.value} is not enabled")
                configs[exchange_type] = None
                continue

            try:
                api_key = self.resolve_env_variables(
                    exchange_cfg.get("api_key", "")
                )
                api_secret = self.resolve_env_variables(
                    exchange_cfg.get("api_secret", "")
                )

                if not api_key or not api_secret:
                    self.logger.warning(
                        f"Missing credentials for {exchange_type.value}"
                    )
                    configs[exchange_type] = None
                    continue

                mode_str = exchange_cfg.get("mode", "testnet")
                try:
                    mode = TradingMode[mode_str.upper()]
                except KeyError:
                    mode = TradingMode.TESTNET

                config = ExchangeConfig(
                    exchange_type=exchange_type,
                    api_key=api_key,
                    api_secret=api_secret,
                    mode=mode,
                    rate_limit_per_minute=exchange_cfg.get(
                        "rate_limit_per_minute", 1200
                    ),
                    timeout_seconds=exchange_cfg.get("timeout_seconds", 30),
                    testnet=exchange_cfg.get("testnet", True),
                    sandbox=exchange_cfg.get("sandbox", True),
                    passphrase=self.resolve_env_variables(
                        exchange_cfg.get("passphrase", "")
                    )
                )
                configs[exchange_type] = config
                self.logger.info(f"Created config for {exchange_type.value}")

            except Exception as e:
                self.logger.error(
                    f"Error creating config for {exchange_type.value}: {e}"
                )
                configs[exchange_type] = None

        return configs

    async def initialize_exchange_manager(
        self
    ) -> Optional[MultiExchangeManager]:
        """Initialize multi-exchange manager with loaded configurations.
        
        Returns:
            Initialized MultiExchangeManager or None if no exchanges configured
        """
        configs = self.create_exchange_configs()
        manager = MultiExchangeManager()

        enabled_count = 0
        for exchange_type, config in configs.items():
            if config:
                manager.add_exchange(config)
                enabled_count += 1

        if enabled_count == 0:
            self.logger.error("No exchanges are properly configured")
            return None

        self.logger.info(f"Initialized {enabled_count} exchange(s)")
        self._exchange_manager = manager
        return manager

    def validate_all(self) -> ValidationResult:
        """Validate all configurations and environment variables.
        
        Returns:
            Overall ValidationResult
        """
        self.validation_results = []
        issues = []
        warnings = []

        # Check environment variables
        env_checks = self.check_environment_variables()
        for var_name, check in env_checks.items():
            if check.status == ValidationStatus.ERROR:
                issues.append(check.message)
            elif check.status == ValidationStatus.WARNING:
                warnings.append(check.message)

        # Check exchange configurations
        exchanges_config = self.config.get("exchanges", {})
        configs_created = 0

        for exchange_type in ExchangeType:
            exchange_key = exchange_type.value
            exchange_cfg = exchanges_config.get(exchange_key, {})

            status = self.validate_exchange_config(exchange_type, exchange_cfg)

            if status.enabled:
                if not status.config_valid:
                    issues.append(status.message)
                else:
                    configs_created += 1

        if configs_created == 0:
            issues.append("No valid exchange configurations found")

        if issues:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                message=f"Configuration validation failed with {len(issues)} error(s)",
                details={
                    "errors": issues,
                    "warnings": warnings,
                    "exchanges_configured": configs_created
                }
            )
        elif warnings:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message=f"Configuration valid with {len(warnings)} warning(s)",
                details={
                    "warnings": warnings,
                    "exchanges_configured": configs_created
                }
            )
        else:
            return ValidationResult(
                status=ValidationStatus.VALID,
                message=f"Configuration valid, {configs_created} exchange(s) ready",
                details={"exchanges_configured": configs_created}
            )

    def print_summary(self) -> None:
        """Print configuration summary."""
        print("\n" + "=" * 80)
        print("API CONFIGURATION SUMMARY")
        print("=" * 80)

        print("\n📋 Environment Variables:")
        env_checks = self.check_environment_variables()
        for var_name, check in env_checks.items():
            status_icon = "✅" if check.status == ValidationStatus.VALID else "⚠️ "
            print(f"{status_icon} {var_name}: {check.message}")

        print("\n🔗 Exchange Configurations:")
        exchanges_config = self.config.get("exchanges", {})
        for exchange_type in ExchangeType:
            exchange_key = exchange_type.value
            exchange_cfg = exchanges_config.get(exchange_key, {})
            status = self.validate_exchange_config(exchange_type, exchange_cfg)

            status_icon = "✅" if status.config_valid else "❌"
            enabled_str = "Enabled" if status.enabled else "Disabled"
            print(f"{status_icon} {exchange_type.value.upper()}: {enabled_str} - {status.message}")

        print("\n" + "=" * 80)


# ============================================================================
# Configuration Setup Helper
# ============================================================================

async def setup_api_configuration(
    project_root: Optional[Path] = None
) -> Optional[MultiExchangeManager]:
    """Setup and initialize API configuration with exchange manager.
    
    This is a convenience function for quick setup.
    
    Args:
        project_root: Project root directory
        
    Returns:
        Initialized MultiExchangeManager or None if setup failed
    """
    manager = APIConfigurationManager(project_root)

    # Load environment and configuration
    if not manager.load_environment():
        print("⚠️  Warning: .env file not found")

    if not manager.load_configuration():
        print("❌ Error: Config file not found")
        return None

    # Validate
    validation = manager.validate_all()
    manager.print_summary()

    if validation.status == ValidationStatus.ERROR:
        print("\n❌ Configuration validation failed")
        return None

    # Initialize exchange manager
    exchange_manager = await manager.initialize_exchange_manager()
    return exchange_manager


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(level: str = "INFO") -> None:
    """Setup logging for API configuration manager.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


if __name__ == "__main__":
    setup_logging()
    print("API Configuration Manager - Import this module to use")
