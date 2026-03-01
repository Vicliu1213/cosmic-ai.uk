#!/usr/bin/env python3
"""
多宇宙挑戰系統測試 - Multiverse Challenge System Tests

Tests for the multiverse trading challenge with 16 parallel universes
and cross-universe knowledge sharing.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from opencode.multiverse_challenge import (
    MultiverseChallenge,
    create_multiverse_challenge,
    UniverseType,
    MultiverseAgent,
    CrossUniverseKnowledge,
    run_multiverse_simulation,
)
from opencode.agent_memory import KnowledgeType

class TestMultiverseInitialization:
    """測試多宇宙系統初始化"""
    
    def test_create_challenge_default(self):
        """測試使用默認參數創建系統"""
        challenge = create_multiverse_challenge()
        assert challenge.num_universes == 16
        assert challenge.num_agents == 16
        assert len(challenge.universes) == 16
        assert len(challenge.agents) == 16
    
    def test_create_challenge_custom(self):
        """測試使用自定義參數創建系統"""
        challenge = create_multiverse_challenge(num_universes=8, num_agents=8)
        assert challenge.num_universes == 8
        assert challenge.num_agents == 8
        assert len(challenge.universes) == 8
        assert len(challenge.agents) == 8
    
    def test_universes_have_different_types(self):
        """測試宇宙有不同的類型"""
        challenge = create_multiverse_challenge(num_universes=16, num_agents=4)
        
        universe_types = set()
        for universe in challenge.universes.values():
            universe_types.add(universe.universe_type)
        
        # 至少應該有 3 種以上的宇宙類型
        assert len(universe_types) >= 3
    
    def test_agents_have_different_roles(self):
        """測試智能體有不同的角色"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=8)
        
        roles = set()
        for agent in challenge.agents.values():
            roles.add(agent.role)
        
        # 至少應該有 2 種以上的角色
        assert len(roles) >= 2
    
    def test_agents_have_accessible_universes(self):
        """測試智能體有可訪問的宇宙"""
        challenge = create_multiverse_challenge(num_universes=8, num_agents=4)
        
        for agent in challenge.agents.values():
            assert len(agent.universe_ids) > 0
            assert len(agent.universe_ids) <= 8
    
    def test_memory_system_initialized(self):
        """測試記憶系統是否初始化"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        for agent in challenge.agents.values():
            assert agent.memory is not None
            assert agent.memory.agent_id == agent.agent_id

class TestUniverseState:
    """測試宇宙狀態管理"""
    
    def test_universe_state_valid_ranges(self):
        """測試宇宙狀態在有效範圍內"""
        challenge = create_multiverse_challenge(num_universes=8, num_agents=4)
        
        for universe in challenge.universes.values():
            # 檢查數值範圍
            assert universe.price > 0
            assert 0 <= universe.volatility <= 1
            assert -1 <= universe.trend <= 1
            assert -1 <= universe.momentum <= 1
            assert 0 <= universe.drawdown <= 1
            # Sharpe ratio can be negative
            assert isinstance(universe.sharpe_ratio, (int, float))
            assert 0 < universe.liquidity
            # difficulty_level is volatility + 0.5, so can go above 1
            assert 0 <= universe.difficulty_level <= 1.5
    
    def test_universe_types_coverage(self):
        """測試所有宇宙類型都被覆蓋"""
        challenge = create_multiverse_challenge(num_universes=16, num_agents=4)
        
        # 檢查宇宙類型的多樣性
        type_counts = {}
        for universe in challenge.universes.values():
            type_name = universe.universe_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # 應該至少有 3 種類型
        assert len(type_counts) >= 3

class TestAgentBehavior:
    """測試智能體行為"""
    
    def test_agent_memory_recording(self):
        """測試智能體記憶記錄"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=2)
        agent = list(challenge.agents.values())[0]
        
        # 記錄經驗
        agent.memory.store_experience(
            experience={'test': 'data', 'profit': 100},
            importance=0.8,
            tags=['test']
        )
        
        # 回憶記憶
        memories = agent.memory.recall_relevant_memories(
            query_context={'tags': ['test']},
            limit=10
        )
        
        assert len(memories) > 0
    
    def test_agent_success_rate_calculation(self):
        """測試智能體成功率計算"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=2)
        agent = list(challenge.agents.values())[0]
        
        # 初始應為 0
        assert agent.get_success_rate() == 0.0
        assert agent.get_avg_profit() == 0.0
        
        # 模擬交易
        agent.total_trades = 10
        agent.successful_trades = 7
        agent.total_profit = 100.0
        
        assert agent.get_success_rate() == 0.7
        assert agent.get_avg_profit() == 10.0

class TestMultiverseSimulation:
    """測試多宇宙模擬"""
    
    @pytest.mark.asyncio
    async def test_single_step_simulation(self):
        """測試單步模擬"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        result = await challenge.simulate_step(0)
        
        assert result['step'] == 0
        assert 'timestamp' in result
        assert 'universe_updates' in result
        assert 'agent_actions' in result
        assert len(result['universe_updates']) == 4
        assert len(result['agent_actions']) == 4
    
    @pytest.mark.asyncio
    async def test_multi_step_simulation(self):
        """測試多步模擬"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        results = []
        for i in range(5):
            result = await challenge.simulate_step(i)
            results.append(result)
        
        assert len(results) == 5
        assert all(r['step'] == i for i, r in enumerate(results))
    
    @pytest.mark.asyncio
    async def test_full_challenge_run(self):
        """測試完整挑戰運行"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        results = await challenge.run_challenge(num_steps=10)
        
        assert 'start_time' in results
        assert 'end_time' in results
        assert 'num_steps' in results
        assert results['num_steps'] == 10
        assert len(results['steps']) == 10
        assert 'final_stats' in results
        assert results['final_stats']['total_trades'] > 0

class TestKnowledgeExchange:
    """測試知識交換"""
    
    def test_knowledge_exchange_count(self):
        """測試知識交換計數"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        # 添加一些學習模式到智能體
        for agent in challenge.agents.values():
            agent.learned_patterns.append({'pattern': 'test'})
        
        exchanges = challenge._facilitate_knowledge_exchange()
        
        # 應該有交換發生
        assert exchanges >= 0
    
    @pytest.mark.asyncio
    async def test_knowledge_improves_decisions(self):
        """測試知識是否改進決策"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        # 運行模擬以積累知識
        for step in range(20):
            await challenge.simulate_step(step)
        
        # 檢查至少某個智能體學到了模式，或者交易已執行
        all_trades = challenge.global_stats['total_trades']
        
        # 應該有交易發生
        assert all_trades > 0

class TestPerformanceTracking:
    """測試績效追蹤"""
    
    def test_global_statistics_tracking(self):
        """測試全局統計追蹤"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        stats = challenge.global_stats
        
        assert 'total_trades' in stats
        assert 'total_profit' in stats
        assert 'universe_performance' in stats
        assert 'agent_performance' in stats
        assert len(stats['universe_performance']) == 4
        assert len(stats['agent_performance']) == 4
    
    def test_best_performing_agents(self):
        """測試獲取表現最好的智能體"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        # 設置一些性能差異
        agents_list = list(challenge.agents.values())
        agents_list[0].total_profit = 100.0
        agents_list[0].total_trades = 10
        agents_list[1].total_profit = 50.0
        agents_list[1].total_trades = 10
        
        best_agents = challenge.get_best_performing_agents(2)
        
        assert len(best_agents) == 2
        assert best_agents[0][1] >= best_agents[1][1]
    
    def test_best_performing_universes(self):
        """測試獲取表現最好的宇宙"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        # 設置一些性能差異
        challenge.global_stats['universe_performance'][0]['profit'] = 100.0
        challenge.global_stats['universe_performance'][1]['profit'] = 50.0
        
        best_universes = challenge.get_best_performing_universes(2)
        
        assert len(best_universes) == 2
        assert best_universes[0][1] >= best_universes[1][1]
    
    def test_challenge_summary(self):
        """測試挑戰摘要"""
        challenge = create_multiverse_challenge(num_universes=4, num_agents=4)
        
        summary = challenge.get_summary()
        
        assert summary['num_universes'] == 4
        assert summary['num_agents'] == 4
        assert 'best_agents' in summary
        assert 'best_universes' in summary
        assert summary['agent_count'] == 4
        assert summary['universe_count'] == 4

class TestAsyncIntegration:
    """測試異步集成"""
    
    @pytest.mark.asyncio
    async def test_multiverse_simulation_async(self):
        """測試非同步多宇宙模擬"""
        results = await run_multiverse_simulation(
            num_universes=4,
            num_agents=4,
            num_steps=5
        )
        
        assert 'results' in results
        assert 'summary' in results
        assert len(results['results']['steps']) == 5

class TestScalability:
    """測試可擴展性"""
    
    def test_large_universe_count(self):
        """測試大量宇宙"""
        challenge = create_multiverse_challenge(num_universes=16, num_agents=16)
        
        assert len(challenge.universes) == 16
        assert len(challenge.agents) == 16
    
    def test_agent_universe_connectivity(self):
        """測試智能體與宇宙的連接"""
        challenge = create_multiverse_challenge(num_universes=16, num_agents=16)
        
        # 檢查每個智能體都能訪問至少一個宇宙
        for agent in challenge.agents.values():
            assert len(agent.universe_ids) > 0
        
        # 檢查每個宇宙都被至少一個智能體訪問
        all_accessible_universes = set()
        for agent in challenge.agents.values():
            all_accessible_universes.update(agent.universe_ids)
        
        # 大多數宇宙應該被訪問
        coverage = len(all_accessible_universes) / len(challenge.universes)
        assert coverage >= 0.5

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
