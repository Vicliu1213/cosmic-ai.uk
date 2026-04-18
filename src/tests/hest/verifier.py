from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import json
import yaml

from .config import HestCheck, HestVerificationConfig


@dataclass
class HestFinding:
    check: str
    target: str
    passed: bool
    score: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HestHealthReport:
    name: str
    realtime: bool
    passed: bool
    failure_count: int
    findings: List[HestFinding]
    summary: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'realtime': self.realtime,
            'passed': self.passed,
            'failure_count': self.failure_count,
            'findings': [asdict(f) for f in self.findings],
            'summary': self.summary,
        }


@dataclass
class HestVerificationState:
    cycles: int = 0
    last_report: Optional[HestHealthReport] = None
    failures: int = 0


class HestVerifier:
    def __init__(
        self,
        config: HestVerificationConfig | None = None,
        state_provider: Callable[[], Dict[str, Any]] | None = None,
        root: Path | None = None,
    ) -> None:
        self.config = config or HestVerificationConfig()
        self.state_provider = state_provider or self._default_state_provider
        self.root = root or Path(__file__).resolve().parents[3]
        self.state = HestVerificationState()

    @classmethod
    def from_config(cls, config_path: Path | None = None) -> 'HestVerifier':
        root = Path(__file__).resolve().parents[3]
        path = config_path or (root / 'config' / 'hest_verification.yaml')
        config = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        checks = [
            HestCheck(**check)
            for check in config.get('checks', [])
        ] or None
        instance = HestVerificationConfig(
            name=config.get('name', 'hest_verification'),
            realtime_interval_sec=float(config.get('realtime_interval_sec', 1.0)),
            max_failures=int(config.get('max_failures', 3)),
            watch_cycles=int(config.get('watch_cycles', 3)),
            checks=checks or HestVerificationConfig().checks,
            metadata=dict(config.get('metadata', {})),
        )
        return cls(config=instance, root=root)

    def _default_state_provider(self) -> Dict[str, Any]:
        from src.layers import build_default_pipeline
        from src.algorithms.enhanced_classic import build_default_registry

        pipeline = build_default_pipeline()
        layer_result = pipeline.run()
        registry = build_default_registry()
        recommendations = registry.recommend(top_k=3)
        index = registry.to_index()
        return {
            'layers': layer_result,
            'enhanced_classic': recommendations,
            'module_catalog': index,
            'dashboard': {
                'ui_enabled': True,
                'pages': ['module', 'enhanced_classic'],
            },
        }

    def _score_presence(self, payload: Dict[str, Any], target: str) -> HestFinding:
        value = payload.get(target)
        passed = value is not None
        if isinstance(value, dict):
            score = 1.0 if value else 0.0
        elif isinstance(value, list):
            score = 1.0 if len(value) > 0 else 0.0
        else:
            score = 1.0 if passed else 0.0
        return HestFinding(
            check=target,
            target=target,
            passed=passed and score >= 1.0,
            score=score,
            details={'present': passed, 'type': type(value).__name__ if passed else 'missing'},
        )

    def verify(self) -> HestHealthReport:
        payload = self.state_provider()
        findings: List[HestFinding] = []
        for check in self.config.checks:
            if not check.enabled:
                continue
            finding = self._run_check(check, payload)
            findings.append(finding)

        passed = all(f.passed for f in findings)
        failure_count = sum(0 if f.passed else 1 for f in findings)
        self.state.cycles += 1
        self.state.failures += failure_count
        report = HestHealthReport(
            name=self.config.name,
            realtime=True,
            passed=passed,
            failure_count=failure_count,
            findings=findings,
            summary={
                'cycles': self.state.cycles,
                'failures_total': self.state.failures,
                'realtime_interval_sec': self.config.realtime_interval_sec,
                'watch_cycles': self.config.watch_cycles,
            },
        )
        self.state.last_report = report
        return report

    def _run_check(self, check: HestCheck, payload: Dict[str, Any]) -> HestFinding:
        if check.target == 'layers':
            layers = payload.get('layers', {})
            result = layers.get('results', []) if isinstance(layers, dict) else []
            trace = layers.get('telemetry', {}).get('traces', []) if isinstance(layers, dict) else []
            score = 1.0 if len(result) == 4 and len(trace) == 4 else 0.0
            return HestFinding(
                check=check.name,
                target=check.target,
                passed=score >= check.threshold,
                score=score,
                details={'results': len(result), 'traces': len(trace)},
            )

        if check.target == 'enhanced_classic':
            rec = payload.get('enhanced_classic', {})
            expected = {'energy', 'compression', 'precision', 'compute'}
            got = set(rec.keys()) if isinstance(rec, dict) else set()
            score = len(expected & got) / len(expected)
            return HestFinding(
                check=check.name,
                target=check.target,
                passed=score >= check.threshold,
                score=score,
                details={'layers': sorted(got)},
            )

        if check.target == 'module_catalog':
            catalog = payload.get('module_catalog', {})
            profiles = catalog.get('profiles', []) if isinstance(catalog, dict) else []
            score = 1.0 if any(item.get('name') == 'enhanced_classic' for item in profiles) else 0.0
            return HestFinding(
                check=check.name,
                target=check.target,
                passed=score >= check.threshold,
                score=score,
                details={'profiles': len(profiles)},
            )

        if check.target == 'dashboard':
            dashboard = payload.get('dashboard', {})
            pages = dashboard.get('pages', []) if isinstance(dashboard, dict) else []
            score = 1.0 if 'enhanced_classic' in pages else 0.0
            return HestFinding(
                check=check.name,
                target=check.target,
                passed=score >= check.threshold,
                score=score,
                details={'pages': pages},
            )

        return self._score_presence(payload, check.target)

    def watch(self, cycles: int | None = None, sleep_sec: float | None = None) -> List[Dict[str, Any]]:
        cycles = cycles or self.config.watch_cycles
        sleep_sec = self.config.realtime_interval_sec if sleep_sec is None else sleep_sec
        reports: List[Dict[str, Any]] = []
        for _ in range(cycles):
            report = self.verify()
            reports.append(report.as_dict())
            if sleep_sec > 0:
                time.sleep(sleep_sec)
            if self.state.failures >= self.config.max_failures:
                break
        return reports

    def manifest(self) -> Dict[str, Any]:
        return {
            'name': self.config.name,
            'root': str(self.root),
            'checks': [asdict(check) for check in self.config.checks],
            'state': asdict(self.state),
            'metadata': dict(self.config.metadata),
        }


def build_default_hest_verifier() -> HestVerifier:
    return HestVerifier.from_config()
