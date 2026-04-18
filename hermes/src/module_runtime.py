from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import log2
from typing import Any, Dict, List, Optional


@dataclass
class ModuleState:
    name: str
    is_active: bool = False
    execution_count: int = 0
    error_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_input: Optional[Any] = None
    last_output: Optional[Any] = None


@dataclass
class QualityReport:
    classical_score: float
    quantum_score: float
    hybrid_score: float
    coverage_score: float
    readiness: str
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "classical_score": round(self.classical_score, 3),
            "quantum_score": round(self.quantum_score, 3),
            "hybrid_score": round(self.hybrid_score, 3),
            "coverage_score": round(self.coverage_score, 3),
            "readiness": self.readiness,
            "notes": self.notes,
        }


class ModuleRuntime:
    def __init__(self, name: str, components: List[str], capabilities: List[str], config: Optional[Dict[str, Any]] = None):
        self.state = ModuleState(name=name)
        self.components = components
        self.capabilities = capabilities
        self.config = config or {}

    def activate(self) -> Dict[str, Any]:
        self.state.is_active = True
        return self.status()

    def deactivate(self) -> Dict[str, Any]:
        self.state.is_active = False
        return self.status()

    def status(self) -> Dict[str, Any]:
        return {
            "name": self.state.name,
            "is_active": self.state.is_active,
            "execution_count": self.state.execution_count,
            "error_count": self.state.error_count,
            "created_at": self.state.created_at.isoformat(),
            "components": self.components,
            "capabilities": self.capabilities,
            "config_keys": list(self.config.keys()),
        }

    def manifest(self) -> Dict[str, Any]:
        return {
            "module": self.state.name,
            "components": self.components,
            "capabilities": self.capabilities,
            "state": self.status(),
            "quality": self.quality_report().as_dict(),
        }

    def record_io(self, input_data: Any, output_data: Any) -> None:
        self.state.last_input = input_data
        self.state.last_output = output_data
        self.state.execution_count += 1

    def error(self, reason: str) -> Dict[str, Any]:
        self.state.error_count += 1
        return {"status": "error", "module": self.state.name, "error": reason, "state": self.status()}

    def classical_assessment(self) -> float:
        if not self.components:
            return 0.0

        completeness = min(len(self.components) / 5.0, 1.0)
        capability_depth = min(len(self.capabilities) / 4.0, 1.0)
        activity = 1.0 if self.state.is_active else 0.55
        stability = max(0.0, 1.0 - (self.state.error_count / max(self.state.execution_count + self.state.error_count, 1)))
        return (completeness * 0.3) + (capability_depth * 0.25) + (activity * 0.2) + (stability * 0.25)

    def quantum_assessment(self) -> float:
        tokens = [self.state.name, *self.components, *self.capabilities]
        if not tokens:
            return 0.0

        diversity = len(set(tokens)) / len(tokens)
        entropy = 0.0
        frequency = {token: tokens.count(token) for token in set(tokens)}
        total = len(tokens)
        for count in frequency.values():
            p = count / total
            entropy -= p * log2(p)

        max_entropy = log2(len(frequency)) if len(frequency) > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy else 0.0
        coherence = 1.0 if self.state.last_output is not None else 0.6
        return (diversity * 0.35) + (normalized_entropy * 0.35) + (coherence * 0.30)

    def quality_report(self) -> QualityReport:
        classical = self.classical_assessment()
        quantum = self.quantum_assessment()
        coverage = min((len(self.components) + len(self.capabilities)) / 10.0, 1.0)
        hybrid = (classical * 0.45) + (quantum * 0.45) + (coverage * 0.10)

        if hybrid >= 0.85:
            readiness = "elite"
        elif hybrid >= 0.7:
            readiness = "production"
        elif hybrid >= 0.5:
            readiness = "elevated"
        else:
            readiness = "needs_refactor"

        notes: List[str] = []
        if len(self.components) < 5:
            notes.append("components below full coverage")
        if len(self.capabilities) < 4:
            notes.append("capability surface is thin")
        if self.state.error_count:
            notes.append("historical runtime errors detected")

        return QualityReport(
            classical_score=classical,
            quantum_score=quantum,
            hybrid_score=hybrid,
            coverage_score=coverage,
            readiness=readiness,
            notes=notes,
        )
