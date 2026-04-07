#!/usr/bin/env python3
"""
Hummingbot 集成测试
Hummingbot Integration Tests

测试 Hummingbot 执行层与 Cosmic 和 LLM-TradeBot 的完整集成
Test complete integration of Hummingbot execution layer with Cosmic and LLM-TradeBot
"""

import pytest
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from src.integrations.hummingbot_execution_bridge import (
    HummingbotExecutionBridge,
    TradingSignal,
    ExecutionContext,
    RiskParameters,
    ExecutionStatus,
    StrategyType,
    HummingbotConfigBuilder,
)
from src.integrations.hummingbot_order_manager import (
    HummingbotOrderManager,
    OrderStatus,
    OrderSide,
)
from src.integrations.hummingbot_status_monitor import (
    HummingbotStatusMonitor,
    ProcessStatus,
    ConnectionStatus,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 测试夹具 ====================

@pytest.fixture
def execution_bridge():
    """创建执行桥梁实例"""
    return HummingbotExecutionBridge()


@pytest.fixture
def order_manager():
    """创建订单管理器实例"""
    return HummingbotOrderManager(initial_balance=10000.0)


@pytest.fixture
def status_monitor():
    """创建状态监控器实例"""
    return HummingbotStatusMonitor()


@pytest.fixture
def sample_signal():
    """创建示例交易信号"""
    return TradingSignal(
        signal_id="SIG-001",
        timestamp=datetime.utcnow(),
        symbol="BTC-USDT",
        direction="BUY",
        confidence=0.85,
        strength=0.9,
        target_price=46000,
        stop_loss=44000,
        take_profit=48000,
    )


@pytest.fixture
def sample_context():
    """创建示例执行上下文"""
    return ExecutionContext(
        market_price=45000,
        bid_price=44999,
        ask_price=45001,
        bid_volume=100,
        ask_volume=100,
        order_book_depth=20,
        volatility=0.02,
    )


@pytest.fixture
def sample_risk_params():
    """创建示例风险参数"""
    return RiskParameters(
        max_position_size=1.0,
        max_order_size=0.5,
        max_slippage=0.5,
        max_daily_loss=5000,
        portfolio_value=10000,
        risk_per_trade=0.02,
    )


# ==================== HummingbotConfigBuilder 测试 ====================

class TestHummingbotConfigBuilder:
    """测试 Hummingbot 配置构建器"""
    
    def test_build_pure_market_making_config(self):
        """测试构建纯做市配置"""
        builder = HummingbotConfigBuilder()
        
        config_yaml = builder.build_pure_market_making_config(
            pair="BTC-USDT",
            order_amount=1.0,
            bid_spread=0.1,
            ask_spread=0.1,
            exchange="binance",
        )
        
        assert "pure_market_making" in config_yaml
        assert "BTC-USDT" in config_yaml
        assert "1.0" in config_yaml
    
    def test_build_cross_exchange_config(self):
        """测试构建跨交易所配置"""
        builder = HummingbotConfigBuilder()
        
        config_yaml = builder.build_cross_exchange_config(
            maker_exchange="binance",
            taker_exchange="kraken",
            maker_pair="BTC-USDT",
            taker_pair="BTC-USD",
            order_amount=1.0,
        )
        
        assert "cross_exchange_market_making" in config_yaml
        assert "binance" in config_yaml
        assert "kraken" in config_yaml
    
    def test_build_triangular_arbitrage_config(self):
        """测试构建三角套利配置"""
        builder = HummingbotConfigBuilder()
        
        pairs = ["BTC-USDT", "BTC-ETH", "ETH-USDT"]
        config_yaml = builder.build_triangular_arbitrage_config(
            exchange="binance",
            triangle_pairs=pairs,
            order_amount=1.0,
        )
        
        assert "triangular_arbitrage" in config_yaml
        for pair in pairs:
            assert pair in config_yaml
    
    def test_validate_config_valid(self):
        """测试验证有效配置"""
        builder = HummingbotConfigBuilder()
        
        config = {
            'strategy': 'pure_market_making',
            'exchange': 'binance',
            'market': 'BTC-USDT',
            'order_amount': 1.0,
            'bid_spread': 0.1,
            'ask_spread': 0.1,
        }
        
        is_valid, errors = builder.validate_config(config)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_config_invalid(self):
        """测试验证无效配置"""
        builder = HummingbotConfigBuilder()
        
        config = {
            'strategy': 'pure_market_making',
            'exchange': 'binance',
            # 缺少 market 和 order_amount
        }
        
        is_valid, errors = builder.validate_config(config)
        assert not is_valid
        assert len(errors) > 0


# ==================== HummingbotExecutionBridge 测试 ====================

class TestHummingbotExecutionBridge:
    """测试 Hummingbot 执行桥梁"""
    
    @pytest.mark.asyncio
    async def test_execute_signal_success(
        self,
        execution_bridge,
        sample_signal,
        sample_context,
        sample_risk_params,
    ):
        """测试成功执行信号"""
        result = await execution_bridge.execute_signal(
            signal=sample_signal,
            context=sample_context,
            risk_params=sample_risk_params,
        )
        
        assert result.signal_id == sample_signal.signal_id
        assert result.status == ExecutionStatus.SUBMITTED
        assert result.hummingbot_order_id is not None
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_execute_signal_low_confidence(
        self,
        execution_bridge,
        sample_signal,
        sample_context,
        sample_risk_params,
    ):
        """测试信号置信度过低"""
        sample_signal.confidence = 0.1
        
        result = await execution_bridge.execute_signal(
            signal=sample_signal,
            context=sample_context,
            risk_params=sample_risk_params,
        )
        
        assert result.status == ExecutionStatus.FAILED
        assert len(result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_execute_signal_no_liquidity(
        self,
        execution_bridge,
        sample_signal,
        sample_context,
        sample_risk_params,
    ):
        """测试市场流动性不足"""
        sample_context.bid_volume = 0
        sample_context.ask_volume = 0
        
        result = await execution_bridge.execute_signal(
            signal=sample_signal,
            context=sample_context,
            risk_params=sample_risk_params,
        )
        
        assert result.status == ExecutionStatus.FAILED
        assert len(result.errors) > 0
    
    def test_calculate_order_size(
        self,
        execution_bridge,
        sample_signal,
        sample_context,
        sample_risk_params,
    ):
        """测试订单大小计算"""
        order_size = execution_bridge._calculate_order_size(
            signal=sample_signal,
            context=sample_context,
            risk_params=sample_risk_params,
        )
        
        assert order_size > 0
        assert order_size <= sample_risk_params.max_order_size
    
    def test_execution_history(
        self,
        execution_bridge,
    ):
        """测试执行历史记录"""
        history = execution_bridge.get_execution_history(limit=10)
        
        assert isinstance(history, list)
        assert len(history) == 0  # 初始应该为空


# ==================== HummingbotOrderManager 测试 ====================

class TestHummingbotOrderManager:
    """测试 Hummingbot 订单管理器"""
    
    def test_add_order(self, order_manager):
        """测试添加订单"""
        order = order_manager.add_order(
            order_id="ORD-001",
            exchange="binance",
            symbol="BTC-USDT",
            side="buy",
            price=45000,
            quantity=0.1,
        )
        
        assert order.order_id == "ORD-001"
        assert order.symbol == "BTC-USDT"
        assert order.side == OrderSide.BUY
        assert order.status == OrderStatus.PENDING
    
    def test_update_order_status(self, order_manager):
        """测试更新订单状态"""
        order_manager.add_order(
            order_id="ORD-001",
            exchange="binance",
            symbol="BTC-USDT",
            side="buy",
            price=45000,
            quantity=0.1,
        )
        
        order_manager.update_order_status(
            order_id="ORD-001",
            status=OrderStatus.FILLED,
            filled_quantity=0.1,
            average_price=45000,
            commission=1.0,
        )
        
        order = order_manager.get_order("ORD-001")
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == 0.1
    
    def test_position_tracking(self, order_manager):
        """测试持仓追踪"""
        # 买入订单
        order_manager.add_order(
            order_id="ORD-001",
            exchange="binance",
            symbol="BTC-USDT",
            side="buy",
            price=45000,
            quantity=0.1,
        )
        
        order_manager.update_order_status(
            order_id="ORD-001",
            status=OrderStatus.FILLED,
            filled_quantity=0.1,
            average_price=45000,
        )
        
        position = order_manager.get_position("BTC-USDT")
        assert position is not None
        assert position.quantity == 0.1
        assert position.average_cost == 45000
    
    def test_update_market_price(self, order_manager):
        """测试市场价格更新"""
        order_manager.add_order(
            order_id="ORD-001",
            exchange="binance",
            symbol="BTC-USDT",
            side="buy",
            price=45000,
            quantity=0.1,
        )
        
        order_manager.update_order_status(
            order_id="ORD-001",
            status=OrderStatus.FILLED,
            filled_quantity=0.1,
            average_price=45000,
        )
        
        order_manager.update_market_price("BTC-USDT", 46000)
        
        position = order_manager.get_position("BTC-USDT")
        assert position.current_price == 46000
        assert position.unrealized_pnl > 0
    
    def test_position_summary(self, order_manager):
        """测试持仓汇总"""
        order_manager.add_order(
            order_id="ORD-001",
            exchange="binance",
            symbol="BTC-USDT",
            side="buy",
            price=45000,
            quantity=0.1,
        )
        
        order_manager.update_order_status(
            order_id="ORD-001",
            status=OrderStatus.FILLED,
            filled_quantity=0.1,
            average_price=45000,
        )
        
        order_manager.update_market_price("BTC-USDT", 46000)
        
        summary = order_manager.get_position_summary()
        assert summary.total_value > 0
        assert summary.total_unrealized_pnl > 0
    
    def test_export_position_summary(self, order_manager):
        """测试导出持仓汇总"""
        order_manager.add_order(
            order_id="ORD-001",
            exchange="binance",
            symbol="BTC-USDT",
            side="buy",
            price=45000,
            quantity=0.1,
        )
        
        order_manager.update_order_status(
            order_id="ORD-001",
            status=OrderStatus.FILLED,
            filled_quantity=0.1,
            average_price=45000,
        )
        
        export = order_manager.export_position_summary()
        
        assert 'timestamp' in export
        assert 'positions' in export
        assert 'BTC-USDT' in export['positions']


# ==================== HummingbotStatusMonitor 测试 ====================

class TestHummingbotStatusMonitor:
    """测试 Hummingbot 状态监控器"""
    
    @pytest.mark.asyncio
    async def test_get_process_health(self, status_monitor):
        """测试获取进程健康状态"""
        health = await status_monitor.get_process_health()
        
        assert health.status in [
            ProcessStatus.RUNNING,
            ProcessStatus.STOPPED,
            ProcessStatus.ERROR,
        ]
        assert health.last_check is not None
    
    @pytest.mark.asyncio
    async def test_get_exchange_connectivity(self, status_monitor):
        """测试获取交易所连接状态"""
        exchanges = await status_monitor.get_exchange_connectivity()
        
        assert isinstance(exchanges, dict)
        assert len(exchanges) > 0
        assert "binance" in exchanges
    
    @pytest.mark.asyncio
    async def test_get_portfolio_snapshot(self, status_monitor):
        """测试获取投资组合快照"""
        portfolio = await status_monitor.get_portfolio_snapshot()
        
        assert portfolio.total_balance > 0
        assert portfolio.total_value > 0
        assert portfolio.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_get_full_status(self, status_monitor):
        """测试获取完整状态"""
        status = await status_monitor.get_full_status()
        
        assert status.process_health is not None
        assert status.exchanges is not None
        assert status.portfolio is not None
        assert isinstance(status.active_orders, list)
    
    @pytest.mark.asyncio
    async def test_export_status_report(self, status_monitor):
        """测试导出状态报告"""
        await status_monitor.get_full_status()
        report = status_monitor.export_status_report()
        
        assert 'timestamp' in report
        assert 'process' in report
        assert 'exchanges' in report
        assert 'portfolio' in report
        assert 'strategy' in report


# ==================== 端到端集成测试 ====================

class TestEndToEndIntegration:
    """测试端到端集成"""
    
    @pytest.mark.asyncio
    async def test_signal_to_order_flow(
        self,
        execution_bridge,
        order_manager,
        sample_signal,
        sample_context,
        sample_risk_params,
    ):
        """测试信号到订单的完整流程"""
        # 1. 执行信号
        exec_result = await execution_bridge.execute_signal(
            signal=sample_signal,
            context=sample_context,
            risk_params=sample_risk_params,
        )
        
        assert exec_result.status == ExecutionStatus.SUBMITTED
        order_id = exec_result.hummingbot_order_id
        assert order_id is not None
        
        # 2. 模拟订单成交
        order_manager.add_order(
            order_id=order_id,
            exchange="binance",
            symbol=sample_signal.symbol,
            side=sample_signal.direction.lower(),
            price=sample_context.market_price,
            quantity=sample_risk_params.max_order_size,
        )
        
        order_manager.update_order_status(
            order_id=order_id,
            status=OrderStatus.FILLED,
            filled_quantity=sample_risk_params.max_order_size,
            average_price=sample_context.market_price,
        )
        
        # 3. 验证持仓
        order = order_manager.get_order(order_id)
        assert order is not None
        assert order.status == OrderStatus.FILLED
        
        position = order_manager.get_position(sample_signal.symbol)
        assert position is not None
        assert position.quantity > 0
    
    @pytest.mark.asyncio
    async def test_full_trading_cycle(
        self,
        execution_bridge,
        order_manager,
        status_monitor,
        sample_signal,
        sample_context,
        sample_risk_params,
    ):
        """测试完整交易周期"""
        # 1. 执行买入信号
        buy_result = await execution_bridge.execute_signal(
            signal=sample_signal,
            context=sample_context,
            risk_params=sample_risk_params,
        )
        
        assert buy_result.status == ExecutionStatus.SUBMITTED
        buy_order_id = buy_result.hummingbot_order_id
        
        # 2. 订单成交
        order_manager.add_order(
            order_id=buy_order_id,
            exchange="binance",
            symbol=sample_signal.symbol,
            side="buy",
            price=sample_context.market_price,
            quantity=0.1,
        )
        
        order_manager.update_order_status(
            order_id=buy_order_id,
            status=OrderStatus.FILLED,
            filled_quantity=0.1,
            average_price=sample_context.market_price,
        )
        
        # 3. 更新市场价格 (模拟价格上升)
        new_price = sample_context.market_price * 1.02  # +2%
        order_manager.update_market_price(sample_signal.symbol, new_price)
        
        # 4. 获取投资组合快照
        portfolio = await status_monitor.get_portfolio_snapshot()
        assert portfolio is not None
        
        # 5. 获取持仓汇总
        summary = order_manager.get_position_summary()
        assert summary.total_unrealized_pnl > 0
        
        # 6. 验证完整性
        assert len(order_manager.get_orders()) > 0


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""
    
    def test_order_manager_bulk_operations(self, order_manager):
        """测试订单管理器批量操作"""
        # 添加 100 个订单
        for i in range(100):
            order_manager.add_order(
                order_id=f"ORD-{i:03d}",
                exchange="binance",
                symbol="BTC-USDT",
                side="buy" if i % 2 == 0 else "sell",
                price=45000 + i,
                quantity=0.1 + i * 0.01,
            )
        
        # 获取所有订单
        orders = order_manager.get_orders(limit=10000)
        assert len(orders) == 100
    
    @pytest.mark.asyncio
    async def test_config_builder_performance(self):
        """测试配置构建器性能"""
        builder = HummingbotConfigBuilder()
        
        # 生成 100 个配置
        for i in range(100):
            config_yaml = builder.build_pure_market_making_config(
                pair=f"PAIR-{i}",
                order_amount=1.0 + i * 0.1,
                bid_spread=0.1,
                ask_spread=0.1,
            )
            assert len(config_yaml) > 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
