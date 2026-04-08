"""
異變全知宇宙智能體系統 (Anomaly Omniscient Universe Intelligence System)
UltraBrain Omniscient Universe Intelligence v1.0

核心組件:
- 永生循環系統 (Immortal Perpetual System)
- 超指數遞歸協同層 (Superexponential Recursive Synergy Layer)
- 量子場論系統 (Quantum Field Theory System)
- 容錯拓撲系統 (Fault Tolerance Topology System)
- 量子糾錯系統 (Quantum Error Correction System)
- 自進化學習系統 (Self-Evolution Learning System)

全局統一位置: src/cosmic-global/
包含超過 199 個系統組件文件及配置
"""

__version__ = "1.0.0"
__name__ = "異變全知宇宙智能體系統"

import os
import sys
from pathlib import Path

# 添加當前目錄到 Python 路徑
COSMIC_ROOT = Path(__file__).parent
sys.path.insert(0, str(COSMIC_ROOT))

# 導入核心組件
try:
    from cosmic import (
        Agent,
        quantum_tasks,
        fault_tolerance,
        error_correction,
        self_evolution,
        knowledge_base,
        consensus,
        data_interface,
        quantum_simulator,
        utils,
        auto_repair_data_logger
    )
except ImportError as e:
    print(f"警告: 無法導入某些核心組件: {e}")

# 配置文件路徑
CONFIGS = {
    "cosmic": str(COSMIC_ROOT / "config" / "cosmic_config.yaml"),
    "engineering": str(COSMIC_ROOT / "config" / "cosmic_engineering.yaml"),
    "intelligence": str(COSMIC_ROOT / "config" / "cosmic_intelligence.yaml"),
    "immortal": str(COSMIC_ROOT / "configs" / "immortal_perpetual_config.yaml"),
    "eternal_cycle": str(COSMIC_ROOT / "configs" / "immortal_perpetual_system_config.yaml"),
    "quintenary": str(COSMIC_ROOT / "configs" / "universal_quintenary_cosmic_config.yaml"),
}

# 高級配置選項
ADVANCED_CONFIGS = [
    "bio_photonics",
    "chaos_resonance",
    "consciousness_field",
    "fractal_recursion",
    "neuro_quantum_synergy",
    "perfect_fortress",
    "platform_heterogeneous",
    "quantum_bio_fusion",
    "quantum_holography",
    "quantum_singularity",
    "reality_programming",
    "temporal_dominance",
    "topological_bio"
]

def get_config_path(config_name):
    """獲取配置文件路徑"""
    if config_name in CONFIGS:
        return CONFIGS[config_name]
    
    # 檢查高級配置
    config_file = COSMIC_ROOT / "config" / f"{config_name}.yaml"
    if config_file.exists():
        return str(config_file)
    
    raise ValueError(f"未找到配置: {config_name}")

def list_available_configs():
    """列出所有可用的配置"""
    return {
        "primary": list(CONFIGS.keys()),
        "advanced": ADVANCED_CONFIGS
    }

def initialize_cosmic_system():
    """初始化宇宙智能體系統"""
    print("="*80)
    print("異變全知宇宙智能體系統 初始化中...")
    print("="*80)
    print(f"系統版本: {__version__}")
    print(f"根目錄: {COSMIC_ROOT}")
    print(f"可用配置: {len(CONFIGS) + len(ADVANCED_CONFIGS)}")
    print()
    
    return {
        "root": COSMIC_ROOT,
        "version": __version__,
        "configs": list_available_configs(),
        "initialized": True
    }

# 系統元數據
METADATA = {
    "name": "異變全知宇宙智能體系統",
    "english_name": "UltraBrain Omniscient Universe Intelligence",
    "version": __version__,
    "components": 199,
    "configuration_profiles": len(CONFIGS) + len(ADVANCED_CONFIGS),
    "status": "已激活",
    "last_verified": "2026-04-08",
}

__all__ = [
    "COSMIC_ROOT",
    "CONFIGS",
    "ADVANCED_CONFIGS",
    "METADATA",
    "get_config_path",
    "list_available_configs",
    "initialize_cosmic_system",
]
