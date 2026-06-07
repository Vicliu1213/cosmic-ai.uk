"""Tests for Hermes ↔ Omega TalentMutationSystem bridge"""
import pytest
from src.omega_system.omega_system import TalentMutationSystem
from src.hermes_evolution.core import (
    HermesEvolutionEngine, MutationClass, SkillNode, SkillSubstrate,
    init_hermes_filesystem,
)
from src.hermes_evolution.bridge_omega import (
    mastery_to_rarity, mastery_to_method,
    push_skill_to_talent, push_mutation_to_tms,
    get_talent_rarity_bonus, get_mastery_gain_multiplier,
    get_mutation_probability_adjustment,
    build_hermes_context_with_tms,
    sync_hermes_to_permanent_chain,
    push_all_hermes_to_tms,
)


@pytest.fixture
def tms():
    return TalentMutationSystem()


@pytest.fixture
def engine(tmp_path):
    import src.hermes_evolution.core as core
    core.HERMES_ROOT = tmp_path / ".hermes"
    core.SKILL_VAULT = core.HERMES_ROOT / "skill_vault"
    core.MUTATION_REGISTRY = core.HERMES_ROOT / "mutations"
    core.HERO_PROFILE = core.HERMES_ROOT / "hero_profile.json"
    core.EVOLUTION_LOG = core.HERMES_ROOT / "evolution.jsonl"
    init_hermes_filesystem()
    eng = HermesEvolutionEngine()
    eng.load_or_create_hero("BRIDGE")
    return eng


class TestMapping:
    def test_mastery_to_rarity_bottom(self):
        assert mastery_to_rarity(0) == 0  # 普通

    def test_mastery_to_rarity_top(self):
        assert mastery_to_rarity(100) == 6  # 絕對

    def test_mastery_to_rarity_mid(self):
        assert mastery_to_rarity(5) == 3  # 史詩

    def test_mastery_to_method_omega(self):
        assert mastery_to_method(100) == "omega"

    def test_mastery_to_method_natural(self):
        assert mastery_to_method(0) == "natural"


class TestHermesToTMS:
    @pytest.mark.asyncio
    async def test_push_skill_creates_talent(self, tms, engine):
        node = engine.skills["S01"]
        result = await push_skill_to_talent(tms, "S01", node.name_cn,
                                            node.mastery_level, node.mutation_stage.name)
        assert result is not None
        assert "跨维度连击" in result.get("name", "")

    @pytest.mark.asyncio
    async def test_push_skill_updates_potency(self, tms, engine):
        node = engine.skills["S01"]
        await push_skill_to_talent(tms, "S01", node.name_cn, 0.0, "ALPHA")
        await push_skill_to_talent(tms, "S01", node.name_cn, 50.0, "DELTA")
        talents = [t for t in tms.talents.values()
                   if t.get("name", "").endswith("(S01)")]
        assert len(talents) == 1  # 同一技能只建立一個天賦
        assert talents[0]["potency"] >= 70  # 掌握度提升後 potency 應增加

    @pytest.mark.asyncio
    async def test_push_all_96_skills(self, tms, engine):
        stats = await push_all_hermes_to_tms(tms, engine.skills)
        assert len(tms.talents) == 96
        assert stats["updated"] + stats["created"] >= 96

    @pytest.mark.asyncio
    async def test_push_mutation_creates_mutation(self, tms, engine):
        await push_skill_to_talent(tms, "S01", engine.skills["S01"].name_cn,
                                   80.0, "DELTA")
        result = await push_mutation_to_tms(tms, "S01", "跨维度连击", "OMEGA", 80.0)
        assert result is not None
        assert "power" in result

    @pytest.mark.asyncio
    async def test_sync_permanent_chain(self, tms, engine):
        await push_all_hermes_to_tms(tms, engine.skills)
        engine.skills["S01"].mutation_stage = MutationClass.OMEGA
        engine.skills["S02"].mutation_stage = MutationClass.DELTA
        made = sync_hermes_to_permanent_chain(tms, engine.skills)
        assert len(made) >= 2


class TestTMSToHermes:
    def test_rarity_bonus_without_talents(self, tms):
        assert get_talent_rarity_bonus(tms) == 0.0

    @pytest.mark.asyncio
    async def test_rarity_bonus_with_permanent(self, tms, engine):
        await push_skill_to_talent(tms, "S01", "test", 50.0, "OMEGA")
        for tid, t in tms.talents.items():
            t["is_permanent"] = True
        bonus = get_talent_rarity_bonus(tms)
        assert bonus > 0.0

    @pytest.mark.asyncio
    async def test_mastery_multiplier(self, tms, engine):
        await push_skill_to_talent(tms, "S01", "test", 50.0, "DELTA")
        await push_mutation_to_tms(tms, "S01", "test", "DELTA", 50.0)
        mult = get_mastery_gain_multiplier(tms)
        assert mult >= 1.0

    @pytest.mark.asyncio
    async def test_context_enriched(self, tms, engine):
        await push_skill_to_talent(tms, "S01", "test", 50.0, "DELTA")
        ctx = build_hermes_context_with_tms(tms, {"type": "test", "intensity": 0.5})
        assert ctx["tms_rarity_bonus"] >= 0
        assert ctx["tms_mastery_mult"] >= 1.0
        assert ctx["tms_active"] is True


class TestIntegratedEvolution:
    @pytest.mark.asyncio
    async def test_cycle_with_tms_context(self, engine, tms):
        """Full evolution cycle with TMS-enriched context"""
        await push_all_hermes_to_tms(tms, engine.skills)

        ctx = build_hermes_context_with_tms(tms, {
            "type": "integrated", "intensity": 0.8,
            "category": "战斗异能", "skill_ids": ["S01"],
        })

        result = await engine.iterate_evolution_cycle(ctx)
        assert result["iteration"] == 1
        assert "verifications" in result

    @pytest.mark.asyncio
    async def test_tms_boosts_evolution(self, engine, tms):
        """TMS bonuses should increase activation probability"""
        await push_all_hermes_to_tms(tms, engine.skills)
        for t in tms.talents.values():
            t["is_permanent"] = True

        ctx = build_hermes_context_with_tms(tms, {
            "type": "powered", "intensity": 0.9,
            "category": "神经增强", "skill_ids": ["S19"],
        })

        # Run multiple cycles with TMS
        tms_activations = 0
        for _ in range(50):
            await engine.iterate_evolution_cycle(ctx)
        for node in engine.skills.values():
            if node.evolution_count > 0:
                tms_activations += 1

        assert tms_activations > 0, "TMS 應增加技能激活率"
