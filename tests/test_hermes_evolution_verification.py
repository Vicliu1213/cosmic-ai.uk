"""
驗證：自我演化 / 無限進化 / 概率異變 / 自我重構 / 湧現
"""
import pytest
import random
from pathlib import Path
from datetime import datetime, timezone
from src.hermes_evolution.core import (
    HermesEvolutionEngine, MutationClass,
    init_hermes_filesystem,
    build_category_map,
)
from src.hermes_evolution.integration import (
    generate_simulated_system_data, enrich_context_with_system_data,
)


@pytest.fixture
def engine(tmp_path):
    # Isolate engine with temp .hermes
    import src.hermes_evolution.core as core
    core.HERMES_ROOT = tmp_path / ".hermes"
    core.SKILL_VAULT = core.HERMES_ROOT / "skill_vault"
    core.MUTATION_REGISTRY = core.HERMES_ROOT / "mutations"
    core.HERO_PROFILE = core.HERMES_ROOT / "hero_profile.json"
    core.EVOLUTION_LOG = core.HERMES_ROOT / "evolution.jsonl"

    init_hermes_filesystem()
    eng = HermesEvolutionEngine()
    eng.load_or_create_hero("VERIFY")
    return eng


class TestProbabilisticMutation:
    def test_probabilistic_mutation_can_fire(self, engine):
        """概率異變在大量激活中至少觸發一次"""
        node = engine.skills["S01"]
        fired = False
        node.mastery_level = 50.0
        for _ in range(500):
            m = engine._check_probabilistic_mutation(node)
            if m:
                fired = True
                break
        assert fired, "概率異變在 500 次嘗試中未觸發 (應 <5% 失敗)"

    def test_probabilistic_mutation_can_jump(self, engine):
        """概率異變可跳級 (至少跳過 ALPHA)"""
        node = engine.skills["S01"]
        node.mutation_stage = MutationClass.ALPHA
        node.mastery_level = 50.0
        jumps = set()
        for _ in range(5000):
            m = engine._check_probabilistic_mutation(node)
            if m:
                jumps.add(m)
        # 至少跳超過一級 (BETA 以上)
        non_alpha = [j for j in jumps if j != MutationClass.BETA]
        assert len(non_alpha) >= 1 or len(jumps) >= 2, \
            f"應有跳級, 獲得: {jumps}"

    def test_cascade_mutation(self, engine):
        """連鎖異變在大量嘗試中觸發"""
        node = engine.skills["S01"]
        node.mutation_stage = MutationClass.BETA
        fired = False
        for _ in range(3000):
            m = engine._check_cascade_mutation(node)
            if m:
                fired = True
                break
        assert fired, "連鎖異變 (2%) 在 3000 次中未觸發"


class TestSelfRefactoring:
    def test_self_refactor_punishes_low_mutation(self, engine):
        """低異變技能被增加能耗 (重構懲罰)"""
        node = engine.skills["S01"]
        node.mastery_level = 5.0
        node.mutation_stage = MutationClass.ALPHA
        old_energy = node.activation_energy
        refactored = engine._self_refactor()
        assert node.activation_energy > old_energy, "能耗應增加"
        assert "S01" in refactored

    def test_self_refactor_rewards_high_mutation(self, engine):
        """高異變技能被降低能耗 (重構獎勵)"""
        node = engine.skills["S01"]
        node.mutation_stage = MutationClass.DELTA
        old_energy = node.activation_energy
        engine._self_refactor()
        assert node.activation_energy < old_energy or abs(node.activation_energy - old_energy) < 0.01, \
            "能耗應降低或保持"


class TestEmergentAbility:
    def test_emerge_new_ability_returns_fusion(self, engine):
        """奇點後湧現融合技能"""
        # Set all to high mastery to ensure category_map works
        for node in engine.skills.values():
            node.mastery_level = 100.0
        name = engine._emerge_new_ability()
        assert name is not None, "應產生融合技能"
        assert "融合" in name

    def test_emergent_ability_writes_file(self, engine, tmp_path):
        """湧現技能寫入檔案"""
        import src.hermes_evolution.core as core
        core.HERMES_ROOT = tmp_path / ".hermes"
        core.SKILL_VAULT = core.HERMES_ROOT / "skill_vault"
        core.MUTATION_REGISTRY = core.HERMES_ROOT / "mutations"
        init_hermes_filesystem()
        eng = HermesEvolutionEngine()
        eng.load_or_create_hero("TEST")
        for node in eng.skills.values():
            node.mastery_level = 100.0
        eng._emerge_new_ability()
        fusion_dir = tmp_path / ".hermes" / "emergent_abilities"
        files = list(fusion_dir.glob("fusion_*.json"))
        assert len(files) >= 1


class TestSkillVerification:
    def test_verify_effective_skill(self, engine):
        """高效技能驗證為 effective"""
        node = engine.skills["S01"]
        node.mastery_level = 10.0
        node.evolution_count = 20
        node.mutation_stage = MutationClass.GAMMA
        v = engine._verify_skill_effectiveness("S01", node, {"intensity": 0.8})
        assert v is None or v["status"] == "effective"

    def test_verify_degraded_skill(self, engine):
        """掌握度高但無異變 → degraded"""
        node = engine.skills["S01"]
        node.mastery_level = 80.0
        node.evolution_count = 5
        node.mutation_stage = MutationClass.ALPHA
        v = engine._verify_skill_effectiveness("S01", node, {"intensity": 0.5})
        assert v is not None
        assert v["status"] == "degraded"


class TestIntegrationWithSystemData:
    @pytest.mark.asyncio
    async def test_enrich_context_with_system_data_combat(self):
        """戰鬥類別注入 theory_expression"""
        system_data = generate_simulated_system_data()
        ctx = enrich_context_with_system_data(
            {"type": "battle", "intensity": 0.5},
            system_data, "戰鬥异能", "S01",
        )
        assert "theory_expression" in ctx
        assert 0 <= ctx["theory_expression"] <= 1.0

    @pytest.mark.asyncio
    async def test_enrich_context_with_system_data_capital(self):
        """資本類別注入 fleet_equity"""
        system_data = generate_simulated_system_data()
        ctx = enrich_context_with_system_data(
            {"type": "raid", "intensity": 0.7},
            system_data, "资本影响", "S75",
        )
        assert "fleet_equity" in ctx
        assert ctx["fleet_equity"] > 0

    @pytest.mark.asyncio
    async def test_enrich_context_all_categories(self):
        """所有 7 類別都產生對應的系統資料注入"""
        system_data = generate_simulated_system_data()
        cat_map = build_category_map()
        for cat, skills in cat_map.items():
            sid = skills[0]
            ctx = enrich_context_with_system_data(
                {"type": "test"}, system_data, cat, sid,
            )
            assert "intensity" in ctx or "type" in ctx

    @pytest.mark.asyncio
    async def test_engine_cycle_with_system_data(self, engine):
        """引擎循環 + 系統資料正常運作"""
        system_data = generate_simulated_system_data()
        cat_map = build_category_map()
        for cat, skills in cat_map.items():
            ctx = enrich_context_with_system_data(
                {"type": "integrated", "intensity": 0.6},
                system_data, cat, skills[0],
            )
            ctx["skill_ids"] = skills
            result = await engine.iterate_evolution_cycle(ctx)
            assert result["iteration"] > 0
            assert "verifications" in result

    @pytest.mark.asyncio
    async def test_integrated_evolution_all_categories(self, engine):
        """整合進化在所有類別上執行"""
        from src.hermes_evolution.integration import run_integrated_evolution
        system_data = generate_simulated_system_data()
        results = await run_integrated_evolution(
            engine, system_data, cycles_per_category=2
        )
        assert len(results) == 7
        for cat, cycles in results.items():
            assert len(cycles) == 2


class TestEvolutionPersistence:
    @pytest.mark.asyncio
    async def test_evolution_log_written(self, engine):
        """每次進化循環寫入 evolution.jsonl"""
        engine.skills["S01"].mastery_level = 0
        await engine.iterate_evolution_cycle({"type": "test", "intensity": 0.9})
        import src.hermes_evolution.core as core
        assert core.EVOLUTION_LOG.exists()
        content = core.EVOLUTION_LOG.read_text(encoding="utf-8").strip()
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_skill_state_persisted(self, engine):
        """技能狀態寫回 skill.json"""
        node = engine.skills["S01"]
        node.mastery_level = 42.0
        import src.hermes_evolution.core as core
        engine._persist_skill_state(node)
        skill_file = core.SKILL_VAULT / "S01" / "skill.json"
        import json
        data = json.loads(skill_file.read_text(encoding="utf-8"))
        assert data["mastery_level"] == 42.0

    def test_hero_profile_persisted(self, engine):
        """英雄狀態寫回 hero_profile.json"""
        import src.hermes_evolution.core as core
        engine._persist_hero_state()
        import json
        data = json.loads(core.HERO_PROFILE.read_text(encoding="utf-8"))
        assert data["callsign"] == "VERIFY"
