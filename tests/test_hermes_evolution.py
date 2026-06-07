"""Tests for Hermes Evolution Engine (task9)"""
import pytest
from src.hermes_evolution import (
    SkillSubstrate, HeroTier, MutationClass,
    SkillNode, HeroEntity,
    SKILLS_MASTER, SKILL_96_DEFINITIONS,
    init_hermes_filesystem,
    HermesEvolutionEngine,
    make_agent_md, make_daily_task_py, generate_all,
)


class TestEnums:
    def test_skill_substrate_has_10_members(self):
        assert len(SkillSubstrate) == 10

    def test_hero_tier_has_10_levels(self):
        assert len(HeroTier) == 10
        assert HeroTier.OMEGA.value == "Ω级——规则书写者"

    def test_mutation_class_has_5_stages(self):
        assert len(MutationClass) == 5
        assert MutationClass.ALPHA.value == "α变异"


class TestData:
    def test_skills_master_has_96_entries(self):
        assert len(SKILLS_MASTER) == 96

    def test_skills_master_first_entry(self):
        sid, name, hero, cat, sub = SKILLS_MASTER[0][:5]
        assert sid == "S01"
        assert name == "跨维度连击"
        assert cat == "战斗异能"

    def test_skills_master_last_entry(self):
        sid = SKILLS_MASTER[-1][0]
        name = SKILLS_MASTER[-1][1]
        assert sid == "S96"
        assert name == "Ω奇点系统终极融合态"

    def test_skill_96_definitions_built(self):
        assert len(SKILL_96_DEFINITIONS) == 96
        assert "S01" in SKILL_96_DEFINITIONS
        assert "S96" in SKILL_96_DEFINITIONS


class TestSkillNode:
    def test_default_mastery_is_zero(self):
        node = SkillNode(
            skill_id="S01", name_cn="测试", name_hero="TEST",
            substrate=SkillSubstrate.QUANTUM,
            activation_energy=100, cooldown_seconds=1,
            range_meters=10, duration_seconds=60,
        )
        assert node.mastery_level == 0.0
        assert node.mutation_stage == MutationClass.ALPHA

    def test_default_data_complete_false(self):
        node = SkillNode(
            skill_id="S02", name_cn="测试2", name_hero="TEST2",
            substrate=SkillSubstrate.NEURAL,
            activation_energy=200, cooldown_seconds=2,
            range_meters=20, duration_seconds=120,
        )
        assert node.data_complete is False


class TestHeroEntity:
    def test_default_values(self):
        hero = HeroEntity(hero_id="HERO_001", callsign="TEST", tier=HeroTier.STREET)
        assert hero.neural_bandwidth == 1.0
        assert hero.quantum_coherence == 0.0
        assert hero.total_iterations == 0
        assert hero.singularity_reached is False

    def test_skills_dict_empty(self):
        hero = HeroEntity(hero_id="HERO_002", callsign="TEST2", tier=HeroTier.CITY)
        assert hero.skills == {}


class TestHermesEvolutionEngine:
    def test_load_or_create_hero(self):
        engine = HermesEvolutionEngine()
        hero = engine.load_or_create_hero(callsign="TEST-HERO")
        assert hero.callsign == "TEST-HERO"
        assert hero.tier == HeroTier.STREET

    def test_get_status_report_no_hero(self):
        engine = HermesEvolutionEngine()
        assert engine.get_status_report() == {"status": "uninitialized"}


class TestGenerator:
    def test_make_agent_md_contains_skill_id(self):
        s = SKILLS_MASTER[0]
        md = make_agent_md(s)
        assert "S01" in md
        assert "跨维度连击" in md

    def test_make_agent_md_contains_frontmatter(self):
        s = SKILLS_MASTER[0]
        md = make_agent_md(s)
        assert "---" in md
        assert "name:" in md

    def test_make_daily_task_py_contains_skill_id(self):
        s = SKILLS_MASTER[0]
        py = make_daily_task_py(s)
        assert "S01" in py
        assert "SKILL_ID" in py

    def test_make_daily_task_py_is_valid_python(self):
        s = SKILLS_MASTER[0]
        py = make_daily_task_py(s)
        compile(py, "<test>", "exec")


class TestFileSystemInit:
    def test_init_creates_96_nodes(self, tmp_path):
        import src.hermes_evolution.core as core
        original_root = core.HERMES_ROOT
        try:
            test_root = tmp_path / ".hermes"
            core.HERMES_ROOT = test_root
            core.SKILL_VAULT = test_root / "skill_vault"
            core.MUTATION_REGISTRY = test_root / "mutations"
            core.HERO_PROFILE = test_root / "hero_profile.json"
            core.EVOLUTION_LOG = test_root / "evolution.jsonl"

            n = init_hermes_filesystem()
            assert n == 96

            skill_dirs = list(core.SKILL_VAULT.iterdir())
            assert len(skill_dirs) == 96

            s01_json = core.SKILL_VAULT / "S01" / "skill.json"
            assert s01_json.exists()
        finally:
            core.HERMES_ROOT = original_root
            core.SKILL_VAULT = original_root / "skill_vault"
            core.MUTATION_REGISTRY = original_root / "mutations"
            core.HERO_PROFILE = original_root / "hero_profile.json"
            core.EVOLUTION_LOG = original_root / "evolution.jsonl"
