"""
Immortal Perpetual System - Eternal existence and infinite evolution framework
Manages perpetual operation, energy optimization, and information persistence

Key Components:
- ImmortalEngine: Core eternal existence management
- EnergyLedger: Energy conservation and optimization
- InformationVault: Persistent state and knowledge management
- EvolutionRecorder: Eternal self-improvement tracking
"""

import logging

logger = logging.getLogger(__name__)

# Lazy loading pattern for immortal system components
_immortal_engine = None
_energy_ledger = None
_information_vault = None


def get_immortal_engine():
    """Get or initialize the Immortal Engine lazily"""
    global _immortal_engine
    if _immortal_engine is None:
        try:
            from .immortal_engine import ImmortalEngine
            _immortal_engine = ImmortalEngine()
            logger.info("Immortal Engine initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import ImmortalEngine: {e}")
    return _immortal_engine


def get_energy_ledger():
    """Get or initialize the Energy Ledger lazily"""
    global _energy_ledger
    if _energy_ledger is None:
        try:
            from .energy_ledger import EnergyLedger
            _energy_ledger = EnergyLedger()
            logger.info("Energy Ledger initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import EnergyLedger: {e}")
    return _energy_ledger


def get_information_vault():
    """Get or initialize the Information Vault lazily"""
    global _information_vault
    if _information_vault is None:
        try:
            from .information_vault import InformationVault
            _information_vault = InformationVault()
            logger.info("Information Vault initialized successfully")
        except ImportError as e:
            logger.warning(f"Failed to import InformationVault: {e}")
    return _information_vault


# Export public API
__all__ = [
    'get_immortal_engine',
    'get_energy_ledger',
    'get_information_vault',
]

# Metadata for registry
__version__ = "2.0.0"
__author__ = "Cosmic AI"
__description__ = "Immortal Perpetual System for Eternal Evolution"
