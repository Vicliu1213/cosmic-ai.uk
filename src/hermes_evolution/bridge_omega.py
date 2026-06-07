"""
雙向橋接：Hermes 96 技能 ↔ Omega TalentMutationSystem (S06)

方向:
  Hermes → TalentMutationSystem:
    技能掌握度/異變等級 → 天賦 potency/rarity
    技能異變事件 → 觸發 TMS mutation
    全技能 mastery 均值 → 永久天賦鏈

  TalentMutationSystem → Hermes:
    TMS 天賦 rarity bonus → 技能 activation_prob 加成
    TMS mutation stability → 技能 mutation 機率調整
    TMS 脈衝加速 → 技能 mastery_gain 倍率
"""
from typing import Dict, List, Optional, Tuple
import random

# ─── Hermes → TalentMutationSystem ───

HERMES_MUTATION_TO_TMS_MUT_TYPE = {
    "BETA":   1,  # β → 強化
    "GAMMA":  2,  # γ → 融合
    "DELTA":  3,  # δ → 超越
    "OMEGA":  5,  # Ω → 神性
}


def mastery_to_rarity(mastery: float) -> int:
    """Map Hermes mastery level to TMS rarity index (0-6)."""
    if mastery >= 100: return 6   # 絕對
    if mastery >= 50:  return 5   # 神話
    if mastery >= 20:  return 4   # 傳說
    if mastery >= 5:   return 3   # 史詩
    if mastery >= 1:   return 2   # 稀有
    if mastery >= 0.3: return 1   # 罕見
    return 0                       # 普通


def mastery_to_method(mastery: float) -> str:
    """Map mastery level to TMS awakening method."""
    if mastery >= 100: return "omega"
    if mastery >= 20:  return "divine"
    if mastery >= 5:   return "catalyst"
    if mastery >= 1:   return "ritual"
    return "natural"


def mutation_stage_to_rarity_bonus(stage_name: str) -> float:
    """Map mutation stage to additional rarity index shift."""
    return {
        "BETA":  1,
        "GAMMA": 2,
        "DELTA": 3,
        "OMEGA": 5,
    }.get(stage_name, 0)


async def push_skill_to_talent(
    talent_system,
    skill_id: str,
    skill_name: str,
    mastery: float,
    mutation_stage: str,
) -> dict:
    """
    Sync one Hermes skill into TalentMutationSystem as a talent.
    Returns the created/updated talent dict.
    """
    if not hasattr(talent_system, "talents"):
        return {}

    rarity_idx = min(6, mastery_to_rarity(mastery) + mutation_stage_to_rarity_bonus(mutation_stage))
    method = mastery_to_method(mastery)

    # Check if talent already exists for this skill
    existing_tid = None
    for tid, t in talent_system.talents.items():
        if t.get("name", "").endswith(f"({skill_id})"):
            existing_tid = tid
            break

    if existing_tid:
        # Update existing talent
        t = talent_system.talents[existing_tid]
        new_potency = 50 + rarity_idx * 20 * (1 + {"natural": 0.1, "ritual": 0.25,
                                                     "catalyst": 0.4, "divine": 0.6,
                                                     "omega": 1.0}.get(method, 0.1))
        t["potency"] = new_potency
        t["rarity"] = talent_system.RARITY[min(rarity_idx, 6)]
        t["mutation_potential"] = 0.5 + rarity_idx * 0.08
        return t
    else:
        # Create new talent
        display_name = f"{skill_name} ({skill_id})"
        result = await talent_system.awaken_talent(display_name, rarity_idx, method)
        return result


async def push_mutation_to_tms(
    talent_system,
    skill_id: str,
    skill_name: str,
    mutation_stage: str,
    mastery: float,
) -> Optional[dict]:
    """
    When a Hermes skill mutates, trigger a corresponding TMS mutation.
    Returns the mutation dict if triggered.
    """
    if not hasattr(talent_system, "talents"):
        return None

    # Find the talent for this skill
    talent_id = None
    for tid, t in talent_system.talents.items():
        if t.get("name", "").endswith(f"({skill_id})"):
            talent_id = tid
            break

    if not talent_id:
        return None

    mut_type_idx = HERMES_MUTATION_TO_TMS_MUT_TYPE.get(mutation_stage, 1)

    # Use higher mutation type for higher mastery
    if mastery >= 50:
        mut_type_idx = min(6, mut_type_idx + 1)
    if mastery >= 100:
        mut_type_idx = 6  # 奇點

    result = await talent_system.trigger_mutation([talent_id], mut_type_idx)
    return result


async def push_all_hermes_to_tms(talent_system, hermes_skills: dict) -> Dict[str, int]:
    """
    Bulk sync all Hermes skills into TMS.
    Returns stats: {created, updated, mutated}
    """
    stats = {"created": 0, "updated": 0}
    for skill_id, node in hermes_skills.items():
        result = await push_skill_to_talent(
            talent_system, skill_id, node.name_cn,
            node.mastery_level, node.mutation_stage.name,
        )
        if result:
            stats["updated" if result.get("id") else "created"] += 1
    return stats


# ─── TalentMutationSystem → Hermes ───

def get_talent_rarity_bonus(talent_system) -> float:
    """
    Calculate activation probability bonus from TMS talents.
    每個永久天賦 +0.02, 最高稀有度天賦額外 +0.01.
    """
    if not hasattr(talent_system, "talents"):
        return 0.0
    bonus = 0.0
    for tid, t in talent_system.talents.items():
        if t.get("is_permanent"):
            bonus += 0.02
            if t["rarity"] in ("神話", "絕對"):
                bonus += 0.01
    return min(0.3, bonus)


def get_mastery_gain_multiplier(talent_system) -> float:
    """
    Calculate mastery gain multiplier from TMS mutations.
    Each mutation adds a small multiplier based on power/stability.
    """
    if not hasattr(talent_system, "mutations"):
        return 1.0
    mult = 1.0
    for mid, m in talent_system.mutations.items():
        power = m.get("power", 0)
        if isinstance(power, (int, float)) and power > 0:
            mult += min(0.1, power / 10000)
    return mult


async def get_pulse_acceleration(talent_system, pulses: int = 3) -> float:
    """
    Get pulse acceleration factor from TMS.
    If accelerate_with_pulses exists, use it; otherwise return base.
    """
    if not hasattr(talent_system, "accelerate_with_pulses"):
        return 1.0
    try:
        result = await talent_system.accelerate_with_pulses(pulses)
        return result.get("acceleration", 1.0)
    except Exception:
        return 1.0


def get_mutation_probability_adjustment(talent_system) -> float:
    """
    Adjustment for probabilistic mutation based on TMS state.
    More stable mutations = lower random mutation chance (controlled evolution).
    """
    if not hasattr(talent_system, "mutations") or not talent_system.mutations:
        return 0.0
    avg_stability = sum(
        m.get("stability", 0.5) for m in talent_system.mutations.values()
    ) / max(len(talent_system.mutations), 1)
    # High stability = lower random mutation (more controlled)
    return (avg_stability - 0.5) * 0.02


# ─── Integrated evolution cycle modifier ───

def build_hermes_context_with_tms(
    talent_system,
    base_context: dict,
) -> dict:
    """
    Enrich a Hermes evolution cycle context with TMS bonuses.
    Call this before iterate_evolution_cycle().
    """
    ctx = dict(base_context)
    ctx["tms_rarity_bonus"] = get_talent_rarity_bonus(talent_system)
    ctx["tms_mastery_mult"] = get_mastery_gain_multiplier(talent_system)
    ctx["tms_mutation_adj"] = get_mutation_probability_adjustment(talent_system)
    ctx["tms_active"] = True
    return ctx


# ─── Permanent chain integration ───

def sync_hermes_to_permanent_chain(talent_system, hermes_skills: dict) -> List[str]:
    """
    Make talents permanent when corresponding Hermes skill reaches DELTA/OMEGA.
    Returns list of talent IDs that were made permanent.
    """
    if not hasattr(talent_system, "talents"):
        return []
    made_permanent = []
    for skill_id, node in hermes_skills.items():
        if node.mutation_stage.name in ("DELTA", "OMEGA"):
            for tid, t in talent_system.talents.items():
                if t.get("name", "").endswith(f"({skill_id})") and not t.get("is_permanent"):
                    talent_system.make_permanent(tid)
                    made_permanent.append(tid)
    return made_permanent
