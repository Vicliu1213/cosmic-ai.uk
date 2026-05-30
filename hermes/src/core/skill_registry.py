from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SkillEntry:
    name: str
    module: str
    actor_class: Optional[str] = None
    passive_components: List[str] = field(default_factory=list)
    status: str = "registered"
    level: int = 1
    max_level: int = 10
    breakthrough_count: int = 0
    breakthrough: bool = False
    breakthrough_effects: List[str] = field(default_factory=list)


class SkillRegistry:
    def __init__(self) -> None:
        self.entries: Dict[str, SkillEntry] = {}
        self.loaded_modules: Dict[str, Any] = {}

    def register(
        self,
        name: str,
        module: str,
        actor_class: Optional[str] = None,
        passive_components: Optional[List[str]] = None,
        level: int = 1,
        max_level: int = 10,
    ) -> SkillEntry:
        entry = SkillEntry(
            name=name,
            module=module,
            actor_class=actor_class,
            passive_components=passive_components or [],
            level=level,
            max_level=max_level,
        )
        self.entries[name] = entry
        return entry

    def level_up(self, name: str, amount: int = 1) -> Optional[SkillEntry]:
        entry = self.entries.get(name)
        if not entry:
            return None
        entry.level = min(entry.level + amount, entry.max_level)
        return entry

    def breakthrough_skill(
        self, name: str, effects: Optional[List[str]] = None
    ) -> Optional[SkillEntry]:
        entry = self.entries.get(name)
        if not entry:
            return None
        entry.breakthrough = True
        entry.breakthrough_count += 1
        entry.max_level += 5
        if effects:
            entry.breakthrough_effects.extend(effects)
        return entry

    def set_no_skill_breakthrough(self, name: str) -> Optional[SkillEntry]:
        entry = self.entries.get(name)
        if not entry:
            return None
        entry.breakthrough = True
        entry.breakthrough_count += 1
        entry.max_level += 10
        entry.breakthrough_effects.append("无技突破")
        return entry

    def load(self, name: str) -> Any:
        entry = self.entries[name]
        if name not in self.loaded_modules:
            self.loaded_modules[name] = import_module(entry.module)
        return self.loaded_modules[name]

    def activate(self, name: str) -> Dict[str, Any]:
        module = self.load(name)
        entry = self.entries[name]
        if entry.actor_class and hasattr(module, entry.actor_class):
            actor_cls = getattr(module, entry.actor_class)
            return {"status": "ready", "skill": name, "actor_class": entry.actor_class, "actor": actor_cls}
        return {"status": "ready", "skill": name}

    def manifest(self) -> Dict[str, Any]:
        return {
            name: {
                "module": entry.module,
                "actor_class": entry.actor_class,
                "passive_components": entry.passive_components,
                "status": entry.status,
                "level": entry.level,
                "max_level": entry.max_level,
                "breakthrough": entry.breakthrough,
                "breakthrough_count": entry.breakthrough_count,
                "breakthrough_effects": entry.breakthrough_effects,
            }
            for name, entry in self.entries.items()
        }


def build_default_registry(src_root: Optional[Path] = None) -> SkillRegistry:
    registry = SkillRegistry()
    registry.register(
        "quantum_singularity",
        "quantum_singularity.core",
        actor_class="QuantumSingularityActor",
        passive_components=["VacuumCoupler", "SpacetimeGrid", "TopologicalStabilizer", "QuantumNeuralNet", "SingularityDetector"],
    )
    registry.register(
        "temporal_dominance",
        "temporal_dominance.core",
        actor_class="TemporaldominanceActor",
        passive_components=["CtcSimulator", "CausalInference", "TimeSeries", "ParadoxResolver", "TemporalCompressor"],
    )
    registry.register(
        "cosmic_intelligence",
        "cosmic_intelligence.core",
    )
    registry.register(
        "platform_heterogeneous",
        "platform_heterogeneous.core",
    )
    registry.register(
        "neuro_quantum_synergy",
        "neuro_quantum_synergy.core",
    )
    registry.register(
        "quantum_bio_fusion",
        "quantum_bio_fusion.core",
    )
    registry.register(
        "cosmic_engineering",
        "cosmic_engineering.core",
    )
    registry.register(
        "reality_programming",
        "reality_programming.core",
    )
    registry.register(
        "perfect_fortress",
        "perfect_fortress.core",
    )
    registry.register(
        "topological_bio",
        "topological_bio.core",
    )
    registry.register(
        "chaos_resonance",
        "chaos_resonance.core",
    )
    registry.register(
        "fractal_recursion",
        "fractal_recursion.core",
    )
    registry.register(
        "quantum_holography",
        "quantum_holography.core",
        actor_class="QuantumholographyActor",
        passive_components=["HologramEncoder", "BoundaryReconstruction", "EntropyCalc", "BulkRecovery", "HolographicProjection"],
    )
    registry.register(
        "bio_photonics",
        "bio_photonics.core",
    )
    registry.register(
        "consciousness_field",
        "consciousness_field.core",
    )
    return registry
