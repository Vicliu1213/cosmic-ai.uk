from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import time
import yaml

from .config import EnhancedHybridConfig


@dataclass
class EnhancedHybridFinding:
    check: str
    passed: bool
    score: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedHybridReport:
    name: str
    passed: bool
    failure_count: int
    findings: List[EnhancedHybridFinding]
    summary: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'passed': self.passed,
            'failure_count': self.failure_count,
            'findings': [asdict(f) for f in self.findings],
            'summary': self.summary,
        }


class EnhancedHybridVerifier:
    def __init__(
        self,
        config: EnhancedHybridConfig | None = None,
        state_provider: Callable[[], Dict[str, Any]] | None = None,
        root: Path | None = None,
    ) -> None:
        self.config = config or EnhancedHybridConfig()
        self.state_provider = state_provider or self._default_state_provider
        self.root = root or Path(__file__).resolve().parents[3]
        self.cycles = 0
        self.failures = 0

    @classmethod
    def from_config(cls, config_path: Path | None = None) -> 'EnhancedHybridVerifier':
        root = Path(__file__).resolve().parents[3]
        path = config_path or (root / 'config' / 'enhanced_hybrid_verification.yaml')
        data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        config = EnhancedHybridConfig(
            name=data.get('name', 'enhanced_hybrid'),
            realtime_interval_sec=float(data.get('realtime_interval_sec', 0.0)),
            watch_cycles=int(data.get('watch_cycles', 2)),
            max_failures=int(data.get('max_failures', 3)),
            modules=list(data.get('modules', ['enhanced_classic', 'layers', 'module_catalog', 'dashboard'])),
            metadata=dict(data.get('metadata', {})),
        )
        return cls(config=config, root=root)

    def _default_state_provider(self) -> Dict[str, Any]:
        from src.tests.hest import build_default_hest_verifier
        from src.algorithms.enhanced_hybrid import build_default_hybrid_registry

        hest = build_default_hest_verifier().verify().as_dict()
        reg = build_default_hybrid_registry()
        return {
            'hest': hest,
            'hybrid': reg.hybrid_manifest(),
            'dashboard': {'enhanced_hybrid_page': True},
            'module_catalog': reg.hybrid_manifest(),
        }

    def verify(self) -> EnhancedHybridReport:
        payload = self.state_provider()
        findings: List[EnhancedHybridFinding] = []

        hest = payload.get('hest', {})
        hest_ok = bool(hest.get('passed')) and hest.get('failure_count', 1) == 0
        findings.append(EnhancedHybridFinding('hest', hest_ok, 1.0 if hest_ok else 0.0, {'summary': hest.get('summary', {})}))

        hybrid = payload.get('hybrid', {})
        ok_hybrid = isinstance(hybrid, dict) and 'recommendations' in hybrid and 'profiles' in hybrid
        findings.append(EnhancedHybridFinding('hybrid_manifest', ok_hybrid, 1.0 if ok_hybrid else 0.0, {'layers': hybrid.get('layers', []) if isinstance(hybrid, dict) else []}))

        dashboard = payload.get('dashboard', {})
        ok_dashboard = bool(dashboard.get('enhanced_hybrid_page'))
        findings.append(EnhancedHybridFinding('dashboard', ok_dashboard, 1.0 if ok_dashboard else 0.0, dashboard))

        module_catalog = payload.get('module_catalog', {})
        ok_module_catalog = bool(module_catalog.get('recommendations'))
        findings.append(EnhancedHybridFinding('module_catalog', ok_module_catalog, 1.0 if ok_module_catalog else 0.0, {'keys': list(module_catalog.keys()) if isinstance(module_catalog, dict) else []}))

        passed = all(f.passed for f in findings)
        failure_count = sum(0 if f.passed else 1 for f in findings)
        self.cycles += 1
        self.failures += failure_count
        return EnhancedHybridReport(
            name=self.config.name,
            passed=passed,
            failure_count=failure_count,
            findings=findings,
            summary={
                'cycles': self.cycles,
                'failures_total': self.failures,
                'modules': self.config.modules,
            },
        )

    def watch(self, cycles: int | None = None, sleep_sec: float | None = None) -> List[Dict[str, Any]]:
        cycles = cycles or self.config.watch_cycles
        sleep_sec = self.config.realtime_interval_sec if sleep_sec is None else sleep_sec
        reports: List[Dict[str, Any]] = []
        for _ in range(cycles):
            report = self.verify()
            reports.append(report.as_dict())
            if sleep_sec > 0:
                time.sleep(sleep_sec)
            if self.failures >= self.config.max_failures:
                break
        return reports

    def manifest(self) -> Dict[str, Any]:
        return {
            'name': self.config.name,
            'root': str(self.root),
            'modules': list(self.config.modules),
            'metadata': dict(self.config.metadata),
        }


def build_default_enhanced_hybrid_verifier() -> EnhancedHybridVerifier:
    return EnhancedHybridVerifier.from_config()
