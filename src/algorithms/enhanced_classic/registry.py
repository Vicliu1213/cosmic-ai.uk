from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

import yaml


LAYER_RULES: Dict[str, Sequence[str]] = {
    'energy': ('resource', 'energy', 'scheduling', 'balancing', 'monitoring', 'planning', 'simulation'),
    'compression': ('compression', 'entropy', 'recursion', 'projection', 'reconstruction', 'encoding'),
    'precision': ('validation', 'stabilization', 'audit', 'coherence', 'checks', 'sensing', 'quality'),
    'compute': ('execution', 'training', 'routing', 'locality', 'simulation', 'scheduler', 'balancing'),
}


@dataclass(frozen=True)
class EnhancedAlgorithmProfile:
    name: str
    title: str
    category: str
    quality: str
    components: List[str]
    capabilities: List[str]
    entry: str
    docs: str
    config: str

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
class EnhancedLayerMatch:
    layer: str
    profile: EnhancedAlgorithmProfile
    score: int
    reasons: List[str]


class EnhancedClassicRegistry:
    def __init__(self, profiles: List[EnhancedAlgorithmProfile], root: Path | None = None) -> None:
        self.profiles = profiles
        self.root = root or Path(__file__).resolve().parents[3]

    @classmethod
    def from_catalog(cls, catalog_path: Path | None = None) -> 'EnhancedClassicRegistry':
        root = Path(__file__).resolve().parents[3]
        path = catalog_path or (root / 'hermes' / 'dashboard' / 'module_catalog.json')
        data = json.loads(path.read_text(encoding='utf-8'))
        profiles = [EnhancedAlgorithmProfile(**module) for module in data.get('modules', [])]
        return cls(profiles=profiles, root=root)

    @classmethod
    def from_config(cls, config_path: Path | None = None) -> 'EnhancedClassicRegistry':
        root = Path(__file__).resolve().parents[3]
        path = config_path or (root / 'config' / 'enhanced_classic.yaml')
        config = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        catalog = config.get('system', {}).get('catalog_path', 'hermes/dashboard/module_catalog.json')
        catalog_path = Path(catalog)
        if not catalog_path.is_absolute():
            catalog_path = root / catalog_path
        return cls.from_catalog(catalog_path)

    def list_profiles(self) -> List[Dict[str, Any]]:
        return [asdict(profile) for profile in self.profiles]

    def match_layer(self, layer: str, top_k: int = 5) -> List[EnhancedLayerMatch]:
        rules = LAYER_RULES.get(layer, ())
        matches: List[EnhancedLayerMatch] = []
        for profile in self.profiles:
            text = profile.signal_text()
            reasons = [rule for rule in rules if rule in text]
            score = len(reasons)
            if score > 0:
                matches.append(EnhancedLayerMatch(layer=layer, profile=profile, score=score, reasons=reasons))
        matches.sort(key=lambda item: (-item.score, item.profile.quality, item.profile.name))
        return matches[:top_k]

    def recommend(self, top_k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        return {
            layer: [
                {
                    'name': match.profile.name,
                    'title': match.profile.title,
                    'score': match.score,
                    'reasons': match.reasons,
                    'quality': match.profile.quality,
                    'entry': match.profile.entry,
                    'docs': match.profile.docs,
                    'config': match.profile.config,
                }
                for match in self.match_layer(layer, top_k=top_k)
            ]
            for layer in LAYER_RULES
        }

    def to_index(self) -> Dict[str, Any]:
        return {
            'root': str(self.root),
            'layers': list(LAYER_RULES.keys()),
            'profiles': self.list_profiles(),
            'recommendations': self.recommend(top_k=5),
        }


def build_default_registry() -> EnhancedClassicRegistry:
    return EnhancedClassicRegistry.from_config()
