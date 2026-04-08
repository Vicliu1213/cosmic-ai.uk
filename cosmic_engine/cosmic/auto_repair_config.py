#!/usr/bin/env python3
"""
自動修復系統配置和管理
Auto-Repair System Configuration & Management
自動修復全資料支持模塊
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class RepairMode(Enum):
    """修復模式枚舉"""
    DISABLED = "disabled"
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    AUTO = "always_on"
    AGGRESSIVE = "aggressive"


class RepairStrategy(Enum):
    """修復策略枚舉"""
    CIRCUIT_BREAKER = "circuit_breaker"
    TIMEOUT_ISOLATION = "timeout_isolation"
    AUTO_RESTART = "automatic_restart"
    AUTO_REPAIR = "auto_repair"
    PREDICTIVE_REPAIR = "predictive_repair"
    SELF_HEALING = "self_healing"


@dataclass
class FaultToleranceRepairConfig:
    """容錯系統自動修復完整配置"""
    # 基本設置
    enabled: bool = True
    auto_repair_enabled: bool = True
    auto_repair_mode: str = "always_on"
    
    # 時間間隔配置
    detection_interval_ms: int = 500
    health_check_interval_sec: int = 1
    failover_timeout_sec: int = 3
    repair_interval_sec: int = 1
    
    # 故障閾值配置
    max_concurrent_failures: int = 5
    failure_threshold: float = 0.3
    failure_detection_threshold: int = 2
    
    # 隔離和轉移配置
    isolation_strategy: str = "automatic"
    auto_restart_enabled: bool = True
    auto_restart_delay_sec: int = 2
    auto_restart_max_attempts: int = 5
    
    # 拓撲配置
    topology_type: str = "mesh"
    backup_replicas: int = 3
    heartbeat_interval_ms: int = 250
    
    # 隔離策略列表
    isolation_strategies: List[str] = None
    
    # 修復配置
    repair_enabled: bool = True
    auto_heal: bool = True
    predictive_repair: bool = True
    aggressive_mode: bool = True
    
    def __post_init__(self):
        if self.isolation_strategies is None:
            self.isolation_strategies = [
                "circuit_breaker",
                "timeout_isolation",
                "automatic_restart",
                "auto_repair"
            ]


@dataclass
class ErrorCorrectionRepairConfig:
    """量子纠错系統自動修復完整配置"""
    # 基本設置
    enabled: bool = True
    auto_correction_enabled: bool = True
    auto_correction_mode: str = "continuous"
    
    # 時間間隔配置
    syndrome_check_interval_ms: int = 200
    correction_frequency_ms: int = 100
    
    # 纠错配置
    code_type: str = "shor"  # repetition, shor, surface
    correction_enabled: bool = True
    aggressive_correction: bool = True
    
    # 效率和閾值
    encoding_efficiency: float = 0.95
    error_threshold: float = 0.0005
    
    # 自動功能
    auto_code_selection: bool = True
    auto_code_switching: bool = True
    
    # 修復重試配置
    correction_retry_count: int = 3
    correction_retry_interval_ms: int = 50
    
    # 預測功能
    predictive_correction: bool = True
    batch_correction: bool = True
    parallel_correction: bool = True
    
    # 碼配置
    codes_config: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.codes_config is None:
            self.codes_config = {
                "repetition": {
                    "qubit_multiplier": 3,
                    "auto_apply": True,
                    "weight": 0.3
                },
                "shor": {
                    "qubit_multiplier": 9,
                    "auto_apply": True,
                    "weight": 0.5
                },
                "surface": {
                    "qubit_multiplier": 25,
                    "distance": 5,
                    "auto_apply": True,
                    "weight": 0.2
                }
            }


@dataclass
class SelfEvolutionRepairConfig:
    """自進化學習系統自動修復完整配置"""
    # 基本設置
    enabled: bool = True
    auto_optimization_enabled: bool = True
    auto_learning_mode: str = "continuous"
    
    # 學習演算法配置
    learning_algorithm: str = "hybrid"  # ppo, cma_es, hybrid
    auto_algorithm_selection: bool = True
    
    # 學習率配置
    learning_rate: float = 0.002
    exploration_rate: float = 0.5
    update_frequency_steps: int = 50
    aggressive_learning: bool = True
    
    # PPO配置
    ppo_gamma: float = 0.995
    ppo_gae_lambda: float = 0.98
    ppo_entropy_coeff: float = 0.02
    ppo_clip_ratio: float = 0.15
    ppo_epochs: int = 8
    ppo_auto_adjust: bool = True
    
    # CMA-ES配置
    cma_es_population_size: int = 50
    cma_es_mutation_rate: float = 0.2
    cma_es_selection_pressure: float = 3
    cma_es_auto_adapt: bool = True
    
    # 知識蒸餾配置
    distillation_enabled: bool = True
    distillation_continuous: bool = True
    distillation_temperature: float = 2.0
    distillation_alpha: float = 0.7
    distillation_frequency_steps: int = 25
    
    # 高級學習功能
    predictive_learning: bool = True
    multi_algorithm_ensemble: bool = True
    curriculum_progression: bool = True
    auto_difficulty_adjustment: bool = True
    meta_learning: bool = True


@dataclass
class AutoRepairSystemConfig:
    """完整的自動修復系統配置"""
    timestamp: str = None
    version: str = "1.0.0"
    
    fault_tolerance: FaultToleranceRepairConfig = None
    error_correction: ErrorCorrectionRepairConfig = None
    self_evolution: SelfEvolutionRepairConfig = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.fault_tolerance is None:
            self.fault_tolerance = FaultToleranceRepairConfig()
        if self.error_correction is None:
            self.error_correction = ErrorCorrectionRepairConfig()
        if self.self_evolution is None:
            self.self_evolution = SelfEvolutionRepairConfig()


class AutoRepairConfigManager:
    """自動修復配置管理器"""
    
    def __init__(self, config_path: str = "config/cosmic_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.repair_config = AutoRepairSystemConfig()
        logger.info("✅ AutoRepairConfigManager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """加載YAML配置"""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return {}
    
    def get_fault_tolerance_config(self) -> FaultToleranceRepairConfig:
        """獲取容錯系統修復配置"""
        return self.repair_config.fault_tolerance
    
    def get_error_correction_config(self) -> ErrorCorrectionRepairConfig:
        """獲取纠错系統修復配置"""
        return self.repair_config.error_correction
    
    def get_self_evolution_config(self) -> SelfEvolutionRepairConfig:
        """獲取自進化系統修復配置"""
        return self.repair_config.self_evolution
    
    def is_auto_repair_enabled(self) -> bool:
        """檢查自動修復是否啟用"""
        ft = self.repair_config.fault_tolerance
        ec = self.repair_config.error_correction
        se = self.repair_config.self_evolution
        
        return (ft.auto_repair_enabled and 
                ec.auto_correction_enabled and 
                se.auto_optimization_enabled)
    
    def get_repair_status_report(self) -> Dict[str, Any]:
        """獲取自動修復狀態報告"""
        ft = self.repair_config.fault_tolerance
        ec = self.repair_config.error_correction
        se = self.repair_config.self_evolution
        
        return {
            "timestamp": self.repair_config.timestamp,
            "version": self.repair_config.version,
            "overall_status": "ENABLED" if self.is_auto_repair_enabled() else "DISABLED",
            "fault_tolerance": {
                "enabled": ft.enabled,
                "auto_repair": ft.auto_repair_enabled,
                "mode": ft.auto_repair_mode,
                "detection_interval_ms": ft.detection_interval_ms,
                "max_concurrent_failures": ft.max_concurrent_failures,
                "failure_threshold": ft.failure_threshold
            },
            "error_correction": {
                "enabled": ec.enabled,
                "auto_correction": ec.auto_correction_enabled,
                "mode": ec.auto_correction_mode,
                "code_type": ec.code_type,
                "syndrome_check_ms": ec.syndrome_check_interval_ms,
                "error_threshold": ec.error_threshold
            },
            "self_evolution": {
                "enabled": se.enabled,
                "auto_optimization": se.auto_optimization_enabled,
                "mode": se.auto_learning_mode,
                "algorithm": se.learning_algorithm,
                "learning_rate": se.learning_rate,
                "exploration_rate": se.exploration_rate
            }
        }
    
    def enable_aggressive_repair(self):
        """啟用激進的自動修復模式"""
        logger.info("🔧 Enabling aggressive auto-repair mode...")
        
        # 容錯系統激進模式
        self.repair_config.fault_tolerance.aggressive_mode = True
        self.repair_config.fault_tolerance.auto_repair_mode = "aggressive"
        self.repair_config.fault_tolerance.detection_interval_ms = 250
        self.repair_config.fault_tolerance.health_check_interval_sec = 0.5
        
        # 纠错系統激進模式
        self.repair_config.error_correction.aggressive_correction = True
        self.repair_config.error_correction.syndrome_check_interval_ms = 100
        self.repair_config.error_correction.correction_retry_count = 5
        
        # 自進化系統激進模式
        self.repair_config.self_evolution.aggressive_learning = True
        self.repair_config.self_evolution.update_frequency_steps = 25
        self.repair_config.self_evolution.distillation_frequency_steps = 10
        
        logger.info("✅ Aggressive auto-repair mode ENABLED")
    
    def enable_conservative_repair(self):
        """啟用保守的自動修復模式"""
        logger.info("🔧 Enabling conservative auto-repair mode...")
        
        # 容錯系統保守模式
        self.repair_config.fault_tolerance.aggressive_mode = False
        self.repair_config.fault_tolerance.auto_repair_mode = "auto"
        self.repair_config.fault_tolerance.detection_interval_ms = 1000
        self.repair_config.fault_tolerance.health_check_interval_sec = 2
        
        # 纠错系統保守模式
        self.repair_config.error_correction.aggressive_correction = False
        self.repair_config.error_correction.syndrome_check_interval_ms = 500
        self.repair_config.error_correction.correction_retry_count = 2
        
        # 自進化系統保守模式
        self.repair_config.self_evolution.aggressive_learning = False
        self.repair_config.self_evolution.update_frequency_steps = 100
        self.repair_config.self_evolution.distillation_frequency_steps = 50
        
        logger.info("✅ Conservative auto-repair mode ENABLED")
    
    def export_repair_config(self, output_path: str = None) -> str:
        """導出自動修復配置為YAML"""
        config_dict = {
            "auto_repair_system": {
                "timestamp": self.repair_config.timestamp,
                "version": self.repair_config.version,
                "fault_tolerance": asdict(self.repair_config.fault_tolerance),
                "error_correction": asdict(self.repair_config.error_correction),
                "self_evolution": asdict(self.repair_config.self_evolution)
            }
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"✅ Config exported to {output_path}")
        
        return yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)


def print_repair_status():
    """打印自動修復系統狀態"""
    manager = AutoRepairConfigManager()
    status = manager.get_repair_status_report()
    
    print("\n" + "="*70)
    print("🔧 自動修復系統狀態報告 (Auto-Repair System Status Report)")
    print("="*70)
    print(f"時間戳: {status['timestamp']}")
    print(f"版本: {status['version']}")
    print(f"整體狀態: {status['overall_status']}")
    print("\n📦 容錯系統 (Fault Tolerance):")
    for key, value in status['fault_tolerance'].items():
        print(f"   {key}: {value}")
    print("\n🛡️ 量子纠错系統 (Error Correction):")
    for key, value in status['error_correction'].items():
        print(f"   {key}: {value}")
    print("\n🧠 自進化系統 (Self-Evolution):")
    for key, value in status['self_evolution'].items():
        print(f"   {key}: {value}")
    print("="*70 + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print_repair_status()
