"""
冲突检测机制 - 我是裁判，阻止互斥异能同时激活
"""
from typing import Dict, List, Tuple
import logging
from .. import AbilityConfig

logger = logging.getLogger(__name__)

class ConflictDetectionMechanism:
    """
    视角：我是冲突仲裁者
    职责：在激活前检测并阻止有害的异能冲突
    """
    def __init__(self):
        self.hard_conflicts: List[Tuple[str, str]] = []  # (tag_a, tag_b) 互斥标签对
        self._register_default_conflicts()
        logger.info("⚔️ 冲突检测机制已就绪")

    def _register_default_conflicts(self):
        self.hard_conflicts = [
            ('fire', 'ice'),
            ('fire', 'water'),
            ('light', 'dark'),
            ('chaos', 'order'),
        ]

    def detect_conflicts(self, abilities: List[AbilityConfig]) -> Dict:
        """检测一组异能中的所有冲突"""
        from itertools import combinations
        conflicts = []
        warnings = []
        for a, b in combinations(abilities, 2):
            # 硬冲突：一方synergy标签是另一方conflict标签
            hard = self._check_hard_conflict(a, b)
            if hard:
                conflicts.append({'type': 'hard', 'ability_a': a.name, 'ability_b': b.name, 'reason': hard})
                logger.error(f"🚫 硬冲突: {a.name} vs {b.name} - {hard}")
            # 软冲突：互有冲突标签
            soft = self._check_soft_conflict(a, b)
            if soft:
                warnings.append({'type': 'soft', 'ability_a': a.name, 'ability_b': b.name, 'reason': soft})
                logger.warning(f"⚠️ 软冲突: {a.name} vs {b.name} - {soft}")
        return {
            'has_conflict': len(conflicts) > 0,
            'hard_conflicts': conflicts,
            'warnings': warnings,
            'safe_to_activate': len(conflicts) == 0
        }

    def _check_hard_conflict(self, a: AbilityConfig, b: AbilityConfig) -> str:
        for tag_a, tag_b in self.hard_conflicts:
            if (tag_a in a.synergy_tags and tag_b in b.synergy_tags) or \
               (tag_b in a.synergy_tags and tag_a in b.synergy_tags):
                return f"元素对立: {tag_a} vs {tag_b}"
        return ""

    def _check_soft_conflict(self, a: AbilityConfig, b: AbilityConfig) -> str:
        a_conflicts_b = set(a.synergy_tags) & set(b.conflict_tags)
        b_conflicts_a = set(b.synergy_tags) & set(a.conflict_tags)
        overlap = a_conflicts_b | b_conflicts_a
        if overlap:
            return f"标签冲突: {', '.join(overlap)}"
        return ""
