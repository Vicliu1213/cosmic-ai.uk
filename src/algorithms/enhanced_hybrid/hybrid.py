from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

import yaml


HYBRID_RULES: Dict[str, Sequence[str]] = {
    'energy': ('resource', 'energy', 'scheduling', 'monitoring', 'balance', 'load', 'efficiency'),
    'compression': ('compression', 'entropy', 'recursion', 'projection', 'encoding', 'summary', 'compact'),
    'precision': ('validation', 'audit', 'coherence', 'quality', 'checks', 'stability', 'confidence'),
    'compute': ('execution', 'training', 'routing', 'locality', 'distributed', 'scheduler', 'parallel'),
}


@dataclass(frozen=True)
class EnhancedHybridProfile:
    name: str
    title: str
    category: str
    quality: str
    components: List[str]
    capabilities: List[str]
    entry: str
    docs: str
    config: str
    source: str = 'module_catalog'

    def signal_text(self) -> str:
        return ' '.join([
            self.name,
            self.title,
            self.category,
            self.quality,
            *self.components,
            *self.capabilities,
        ]).lower()


@dataclass(frozen=True)
class EnhancedHybridScore:
    layer: str
    name: str
    score: int
    reasons: List[str]
    quality: str
    entry: str
    docs: str
    config: str


class EnhancedHybridRegistry:
    def __init__(self, profiles: List[EnhancedHybridProfile], root: Path | None = None) -> None:
        self.profiles = profiles
        self.root = root or Path(__file__).resolve().parents[3]

    @classmethod
    def from_catalog(cls, catalog_path: Path | None = None) -> 'EnhancedHybridRegistry':
        root = Path(__file__).resolve().parents[3]
        path = catalog_path or (root / 'hermes' / 'dashboard' / 'module_catalog.json')
        data = json.loads(path.read_text(encoding='utf-8'))
        profiles = [EnhancedHybridProfile(**module) for module in data.get('modules', [])]
        return cls(profiles=profiles, root=root)

    @classmethod
    def from_config(cls, config_path: Path | None = None) -> 'EnhancedHybridRegistry':
        root = Path(__file__).resolve().parents[3]
        path = config_path or (root / 'config' / 'enhanced_hybrid.yaml')
        config = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        catalog = config.get('system', {}).get('catalog_path', 'hermes/dashboard/module_catalog.json')
        catalog_path = Path(catalog)
        if not catalog_path.is_absolute():
            catalog_path = root / catalog_path
        return cls.from_catalog(catalog_path)

    def list_profiles(self) -> List[Dict[str, Any]]:
        return [asdict(profile) for profile in self.profiles]

    def score_layer(self, layer: str, top_k: int = 5) -> List[EnhancedHybridScore]:
        rules = HYBRID_RULES.get(layer, ())
        scores: List[EnhancedHybridScore] = []
        for profile in self.profiles:
            text = profile.signal_text()
            reasons = [rule for rule in rules if rule in text]
            score = len(reasons)
            if score:
                scores.append(
                    EnhancedHybridScore(
                        layer=layer,
                        name=profile.name,
                        score=score,
                        reasons=reasons,
                        quality=profile.quality,
                        entry=profile.entry,
                        docs=profile.docs,
                        config=profile.config,
                    )
                )
        scores.sort(key=lambda item: (-item.score, item.quality, item.name))
        return scores[:top_k]

    def recommend(self, top_k: int = 4) -> Dict[str, List[Dict[str, Any]]]:
        return {
            layer: [asdict(score) for score in self.score_layer(layer, top_k=top_k)]
            for layer in HYBRID_RULES
        }

    def hybrid_manifest(self) -> Dict[str, Any]:
        return {
            'root': str(self.root),
            'layers': list(HYBRID_RULES.keys()),
            'profiles': self.list_profiles(),
            'recommendations': self.recommend(top_k=5),
        }


def build_default_hybrid_registry() -> EnhancedHybridRegistry:
    return EnhancedHybridRegistry.from_config()
