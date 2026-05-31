"""協同門檻 ⇄ 異能矩陣橋接層 — Gate 激活自動解鎖異能"""

import sys, os, logging
from typing import Dict, List, Optional, Any

HERMES_SRC = os.path.join(os.path.dirname(__file__), "..", "..", "hermes", "src")
if HERMES_SRC not in sys.path:
    sys.path.insert(0, HERMES_SRC)

from 异能矩阵 import AbilityConfig, AbilityType, ActivationStatus

logger = logging.getLogger(__name__)

GATE_ABILITY_MAP: Dict[int, dict] = {
    2:  dict(ability_id="gate_resonance", name="共振耦合", type=AbilityType.SUPPORT, cost=20, cd=5, tags=["communication", "p2p"]),
    3:  dict(ability_id="gate_triangular", name="三角穩定場", type=AbilityType.SUPPORT, cost=30, cd=8, tags=["consensus", "stability"]),
    4:  dict(ability_id="gate_entanglement", name="量子糾纏網絡", type=AbilityType.UTILITY, cost=40, cd=10, tags=["quantum", "entropy"]),
    5:  dict(ability_id="gate_hologram", name="全息意識投影", type=AbilityType.HYBRID, cost=50, cd=12, tags=["holographic", "consciousness"]),
    6:  dict(ability_id="gate_manybody", name="多體糾纏", type=AbilityType.SUPPORT, cost=35, cd=9, tags=["gossip", "sync"]),
    7:  dict(ability_id="gate_nonlinearcausal", name="非局域因果", type=AbilityType.HYBRID, cost=60, cd=15, tags=["prediction", "causality"]),
    8:  dict(ability_id="gate_topological", name="拓撲量子計算", type=AbilityType.OFFENSIVE, cost=80, cd=20, tags=["quantum", "compute"]),
    9:  dict(ability_id="gate_stringfield", name="弦論場", type=AbilityType.UTILITY, cost=45, cd=12, tags=["theory", "search"]),
    10: dict(ability_id="gate_cosmic_consciousness", name="宇宙意識網絡", type=AbilityType.HYBRID, cost=70, cd=18, tags=["consciousness", "shared_memory"]),
    11: dict(ability_id="gate_absolute_holography", name="絕對全息", type=AbilityType.UTILITY, cost=55, cd=14, tags=["holographic", "archive"]),
    12: dict(ability_id="gate_omega", name="Omega原型", type=AbilityType.HYBRID, cost=65, cd=16, tags=["discovery", "gap_detection"]),
    13: dict(ability_id="gate_omniscience", name="全知場固化", type=AbilityType.DEFENSIVE, cost=40, cd=10, tags=["healing", "resource"]),
    14: dict(ability_id="gate_cosmic_will", name="宇宙意志覺醒", type=AbilityType.HYBRID, cost=90, cd=25, tags=["autonomous", "creation"]),
    15: dict(ability_id="gate_divine", name="神性完全體", type=AbilityType.OFFENSIVE, cost=150, cd=30, tags=["divine", "autonomous", "trading"]),
}

INFINITY_ABILITY = dict(ability_id="gate_infinity", name="∞ 超越完全體", type=AbilityType.HYBRID, cost=999, cd=60, tags=["absolute", "transcendence"])

TYPE_LABELS = {
    "support": "支援型",
    "offensive": "攻擊型",
    "defensive": "防禦型",
    "utility": "工具型",
    "hybrid": "混合型",
}


class GateAbilityBridge:
    def __init__(self, core_matrix=None, energy_capacity: float = 1000.0):
        self.core_matrix = core_matrix
        self._unlocked: Dict[int, dict] = {}
        self._ability_configs: Dict[int, "AbilityConfig"] = {}

    def ensure_core_matrix(self):
        if self.core_matrix is None:
            from 异能矩阵.核心矩阵 import CoreMatrix
            self.core_matrix = CoreMatrix(energy_capacity=1000.0)
            logger.info("⚡ GateBridge: CoreMatrix 自動初始化")
        return self.core_matrix

    def on_gate_activated(self, level: int, snap: dict):
        if level in self._unlocked:
            return
        cm = self.ensure_core_matrix()

        ab_data = GATE_ABILITY_MAP.get(level)
        if level > 15:
            ab_data = INFINITY_ABILITY
        if not ab_data:
            self._unlocked[level] = {"status": "no_ability"}
            return

        cfg = AbilityConfig(
            ability_id=ab_data["ability_id"],
            name=ab_data["name"],
            ability_type=ab_data["type"],
            base_energy_cost=ab_data["cost"],
            base_cooldown=ab_data["cd"],
            synergy_tags=ab_data["tags"],
        )
        self._ability_configs[level] = cfg

        self._unlocked[level] = {
            "status": "unlocked",
            "ability_id": cfg.ability_id,
            "name": cfg.name,
            "type": cfg.ability_type.value,
            "type_label": TYPE_LABELS.get(cfg.ability_type.value, cfg.ability_type.value),
            "cost": cfg.base_energy_cost,
            "cooldown": cfg.base_cooldown,
            "drrk": snap.get("drrk", ""),
            "synergy_boost": snap.get("synergy_boost", 0),
            "consciousness_amp": snap.get("consciousness_amp", 0),
        }
        logger.info(f"🔓 GateBridge: Lv{level} → 解鎖異能 [{cfg.name}]")

    def get_unlocked_abilities(self) -> List[dict]:
        return list(self._unlocked.values())

    def get_gates_status(self) -> Dict[str, dict]:
        return {str(k): v for k, v in self._unlocked.items()}

    def get_ability_configs(self) -> Dict[int, "AbilityConfig"]:
        return dict(self._ability_configs)

    def get_full_status(self) -> dict:
        cm = self.ensure_core_matrix()
        matrix_status = cm.get_system_status() if self.core_matrix else {}
        return {
            "gates": self.get_gates_status(),
            "abilities": self.get_unlocked_abilities(),
            "matrix": matrix_status,
            "unlocked_count": len(self._unlocked),
            "drrk_max": max((v.get("drrk", "") for v in self._unlocked.values()), default=""),
        }
