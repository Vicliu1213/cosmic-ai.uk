#!/usr/bin/env python3
"""
Phase 4 Arbitrage Comprehensive Tests
Phase 4 套利系統全面測試

Comprehensive test suite for Phase 4: Triangular, Wormhole, and Hummingbot Integration.
包含三角套利、蟲洞套利和 Hummingbot 集成的全面測試套件。
"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.triangular_arbitrage_engine import (
    TriangularArbitrageEngine,
    PriceMonitor,
    CycleDetector,
    ExecutionCalculator,
    TriangularCycle,
    PriceSnapshot,
    ArbitrageOpportunityType
)

from src.core.wormhole_arbitrage_module import (
    WormholeArbitrageModule,
    ExchangeConnector,
    OpportunityScan,
    ExchangeType,
    ExchangeInfo,
    ExchangePrice,
    TransferCostEstimator
)

from src.core.hummingbot_integration_layer import (
    HummingbotIntegrationLayer,
    HummingbotConnector,
    StrategyBuilder,
    OrderExecutor,
    TradeTracker,
    HummingbotStatus,
    OrderStatus,
    ExchangeConfig
)


class TestPriceMonitor:
    """PriceMonitor 单元测试"""
    
    def test_price_monitor_initialization(self):
        """测试价格监视器初始化"""
        monitor = PriceMonitor(history_window=500)
        assert monitor.history_window == 500
        assert len(monitor.price_history) == 0
        assert len(monitor.current_prices) == 0
    
    def test_update_single_price(self):
        """测试单个价格更新"""
        monitor = PriceMonitor()
        monitor.update_price("BTC/USD", 50000.0, 50100.0, 100.0)
        
        price = monitor.get_price("BTC/USD")
        assert price is not None
        assert price.bid == 50000.0
        assert price.ask == 50100.0
        assert price.mid == 50050.0
    
    def test_multiple_price_updates(self):
        """测试多个价格更新"""
        monitor = PriceMonitor()
        
        pairs_data = {
            "BTC/USD": (50000, 50100, 100),
            "ETH/USD": (3000, 3010, 500),
            "XRP/USD": (2.5, 2.51, 1000)
        }
        
        for pair, (bid, ask, vol) in pairs_data.items():
            monitor.update_price(pair, bid, ask, vol)
        
        assert len(monitor.current_prices) == 3
        assert monitor.get_price("BTC/USD") is not None
        assert monitor.get_price("ETH/USD") is not None
        assert monitor.get_price("XRP/USD") is not None
    
    def test_invalid_prices_rejected(self):
        """测试无效价格被拒绝"""
        monitor = PriceMonitor()
        monitor.update_price("BTC/USD", 50100.0, 50000.0, 100.0)  # ask < bid
        
        price = monitor.get_price("BTC/USD")
        assert price is None
    
    def test_price_history_maintained(self):
        """测试价格历史维护"""
        monitor = PriceMonitor(history_window=10)
        
        for i in range(15):
            monitor.update_price("BTC/USD", 50000 + i, 50100 + i, 100)
        
        history = monitor.get_price_history("BTC/USD", lookback=20)
        assert len(history) <= 10  # 不超过窗口大小


class TestCycleDetector:
    """CycleDetector 单元测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.monitor = PriceMonitor()
        self.detector = CycleDetector(min_profit_threshold=0.1)
    
    def test_cycle_detector_initialization(self):
        """测试周期检测器初始化"""
        assert self.detector.min_profit_threshold == 0.1
        assert len(self.detector.detected_cycles) == 0
    
    def test_detect_profitable_cycle(self):
        """测试检测盈利周期"""
        # 设置模拟价格形成盈利周期
        self.monitor.update_price("BTC/USD", 50000, 50010, 100)
        self.monitor.update_price("ETH/BTC", 0.15, 0.151, 200)
        self.monitor.update_price("ETH/USD", 7500, 7510, 150)
        
        pairs = ["BTC/USD", "ETH/BTC", "ETH/USD"]
        cycles = self.detector.detect_cycles(self.monitor, pairs)
        
        assert isinstance(cycles, list)
    
    def test_get_best_cycle(self):
        """测试获取最佳周期"""
        cycle1 = TriangularCycle(
            pair1="BTC/USD",
            pair2="ETH/BTC",
            pair3="ETH/USD",
            cycle_path=["BTC/USD", "ETH/BTC", "ETH/USD"],
            profit_pct=0.2,
            entry_time=datetime.now(),
            expiration_time=datetime.now() + timedelta(seconds=5),
            confidence=0.8,
            base_amount=1.0
        )
        
        self.detector.detected_cycles = [cycle1]
        best = self.detector.get_best_cycle()
        
        assert best == cycle1
        assert best.profit_pct == 0.2


class TestExecutionCalculator:
    """ExecutionCalculator 单元测试"""
    
    def test_calculator_initialization(self):
        """测试计算器初始化"""
        calc = ExecutionCalculator(transaction_fee_pct=0.1, slippage_pct=0.05)
        assert calc.transaction_fee_pct == 0.1
        assert calc.slippage_pct == 0.05
    
    def test_calculate_net_profit(self):
        """测试净利润计算"""
        calc = ExecutionCalculator(transaction_fee_pct=0.05, slippage_pct=0.02)
        
        cycle = TriangularCycle(
            pair1="BTC/USD",
            pair2="ETH/BTC",
            pair3="ETH/USD",
            cycle_path=["BTC/USD", "ETH/BTC", "ETH/USD"],
            profit_pct=0.5,
            entry_time=datetime.now(),
            expiration_time=datetime.now() + timedelta(seconds=5),
            confidence=0.8,
            base_amount=1.0
        )
        
        net_profit = calc.calculate_net_profit(cycle)
        expected = 0.5 - (0.05 * 3) - (0.02 * 3)  # 0.5 - 0.15 - 0.06 = 0.29
        assert net_profit == pytest.approx(expected, rel=0.01)
    
    def test_optimal_position_size(self):
        """测试最优持仓大小"""
        calc = ExecutionCalculator()
        
        cycle = TriangularCycle(
            pair1="BTC/USD",
            pair2="ETH/BTC",
            pair3="ETH/USD",
            cycle_path=["BTC/USD", "ETH/BTC", "ETH/USD"],
            profit_pct=0.3,
            entry_time=datetime.now(),
            expiration_time=datetime.now() + timedelta(seconds=5),
            confidence=0.9,
            base_amount=1.0
        )
        
        position = calc.calculate_optimal_position_size(
            cycle,
            available_capital=10000,
            max_position_pct=5.0
        )
        
        assert position > 0
        assert position <= (10000 * 0.05 / 100) * 10000


class TestTriangularArbitrageEngine:
    """三角套利引擎单元测试"""
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = TriangularArbitrageEngine(
            exchange_name="binance",
            min_profit_threshold=0.1
        )
        
        assert engine.exchange_name == "binance"
        assert engine.cycle_count == 0
        assert engine.successful_executions == 0
    
    def test_update_market_prices(self):
        """测试更新市场价格"""
        engine = TriangularArbitrageEngine()
        
        prices = {
            "BTC/USD": (50000, 50010, 100),
            "ETH/USD": (3000, 3010, 500)
        }
        
        engine.update_market_prices(prices)
        
        btc_price = engine.price_monitor.get_price("BTC/USD")
        assert btc_price is not None
        assert btc_price.bid == 50000
    
    def test_analyze_opportunities(self):
        """测试分析机会"""
        engine = TriangularArbitrageEngine()
        
        prices = {
            "BTC/USD": (50000, 50010, 100),
            "ETH/BTC": (0.15, 0.151, 200),
            "ETH/USD": (7500, 7510, 150)
        }
        
        engine.update_market_prices(prices)
        cycles = engine.analyze_opportunities(["BTC/USD", "ETH/BTC", "ETH/USD"])
        
        assert isinstance(cycles, list)
        assert engine.cycle_count >= 0
    
    def test_get_performance_stats(self):
        """测试获取性能统计"""
        engine = TriangularArbitrageEngine()
        stats = engine.get_performance_stats()
        
        assert "exchange" in stats
        assert "cycles_detected" in stats
        assert "successful_executions" in stats
        assert stats["exchange"] == "default"


class TestExchangeConnector:
    """ExchangeConnector 单元测试"""
    
    def test_connector_initialization(self):
        """测试连接器初始化"""
        connector = ExchangeConnector()
        assert len(connector.exchanges) == 0
        assert len(connector.prices) == 0
    
    def test_register_exchange(self):
        """测试注册交易所"""
        connector = ExchangeConnector()
        
        info = ExchangeInfo(
            exchange_id="binance",
            exchange_name="Binance",
            exchange_type=ExchangeType.CENTRALIZED,
            base_fee=0.05,
            withdrawal_fee=0.001,
            deposit_fee=0.0,
            supported_pairs={"BTC/USD", "ETH/USD"},
            connection_latency_ms=50
        )
        
        connector.register_exchange(info)
        assert "binance" in connector.exchanges
        assert connector.exchanges["binance"].exchange_name == "Binance"
    
    def test_update_price(self):
        """测试更新价格"""
        connector = ExchangeConnector()
        
        info = ExchangeInfo(
            exchange_id="binance",
            exchange_name="Binance",
            exchange_type=ExchangeType.CENTRALIZED,
            base_fee=0.05,
            withdrawal_fee=0.001,
            deposit_fee=0.0,
            supported_pairs={"BTC/USD"},
            connection_latency_ms=50
        )
        
        connector.register_exchange(info)
        
        price = ExchangePrice(
            exchange_id="binance",
            pair="BTC/USD",
            bid=50000,
            ask=50010,
            timestamp=datetime.now(),
            volume=100
        )
        
        connector.update_price("binance", price)
        retrieved = connector.get_price("binance", "BTC/USD")
        
        assert retrieved is not None
        assert retrieved.bid == 50000


class TestWormholeArbitrageModule:
    """跨交易所套利模块单元测试"""
    
    def test_module_initialization(self):
        """测试模块初始化"""
        module = WormholeArbitrageModule(module_name="test_wormhole")
        
        assert module.module_name == "test_wormhole"
        assert module.total_opportunities_found == 0
        assert module.successful_executions == 0
    
    def test_register_exchange(self):
        """测试注册交易所"""
        module = WormholeArbitrageModule()
        
        module.register_exchange(
            exchange_id="binance",
            exchange_name="Binance",
            exchange_type=ExchangeType.CENTRALIZED,
            base_fee=0.05,
            withdrawal_fee=0.001,
            deposit_fee=0.0,
            supported_pairs=["BTC/USD", "ETH/USD"],
            connection_latency_ms=50
        )
        
        assert "binance" in module.exchange_connector.exchanges
    
    def test_update_price(self):
        """测试更新价格"""
        module = WormholeArbitrageModule()
        
        module.register_exchange(
            exchange_id="binance",
            exchange_name="Binance",
            exchange_type=ExchangeType.CENTRALIZED,
            base_fee=0.05,
            withdrawal_fee=0.001,
            deposit_fee=0.0,
            supported_pairs=["BTC/USD"],
            connection_latency_ms=50
        )
        
        module.update_price("binance", "BTC/USD", 50000, 50010, 100)
        
        price = module.exchange_connector.get_price("binance", "BTC/USD")
        assert price is not None
        assert price.bid == 50000


class TestTransferCostEstimator:
    """TransferCostEstimator 单元测试"""
    
    def test_estimator_initialization(self):
        """测试估算器初始化"""
        estimator = TransferCostEstimator()
        assert len(estimator.confirmation_times) > 0
    
    def test_estimate_transfer_time(self):
        """测试估算转账时间"""
        estimator = TransferCostEstimator()
        
        time = estimator.estimate_transfer_time("binance", "kraken", "ethereum")
        assert time > 0
    
    def test_estimate_transfer_cost_pct(self):
        """测试估算转账成本百分比"""
        estimator = TransferCostEstimator()
        
        cost = estimator.estimate_transfer_cost_pct("ethereum")
        assert 0 < cost < 1.0
        
        cost_bsc = estimator.estimate_transfer_cost_pct("bsc")
        assert cost_bsc < cost  # BSC 应该更便宜


class TestHummingbotConnector:
    """Hummingbot 连接器单元测试"""
    
    def test_connector_initialization(self):
        """测试连接器初始化"""
        connector = HummingbotConnector(
            hummingbot_host="localhost",
            hummingbot_port=8000
        )
        
        assert connector.host == "localhost"
        assert connector.port == 8000
        assert connector.status == HummingbotStatus.NOT_RUNNING
        assert not connector.connected
    
    def test_connect(self):
        """测试连接"""
        connector = HummingbotConnector()
        result = connector.connect()
        
        assert result is True
        assert connector.connected is True
        assert connector.status == HummingbotStatus.RUNNING
    
    def test_disconnect(self):
        """测试断开连接"""
        connector = HummingbotConnector()
        connector.connect()
        connector.disconnect()
        
        assert connector.connected is False
        assert connector.status == HummingbotStatus.STOPPED


class TestStrategyBuilder:
    """策略构建器单元测试"""
    
    def test_builder_initialization(self):
        """测试构建器初始化"""
        builder = StrategyBuilder()
        assert len(builder.strategies) == 0
    
    def test_create_triangular_strategy(self):
        """测试创建三角策略"""
        builder = StrategyBuilder()
        
        strategy = builder.create_triangular_strategy(
            "test_strategy",
            "BTC/USD",
            "ETH/BTC",
            "ETH/USD",
            1.0
        )
        
        assert strategy.strategy_name == "test_strategy"
        assert strategy.exchange_pair_primary == "BTC/USD"
        assert strategy.exchange_pair_secondary == "ETH/BTC"
        assert strategy.exchange_pair_tertiary == "ETH/USD"
    
    def test_create_wormhole_strategy(self):
        """测试创建跨交易所策略"""
        builder = StrategyBuilder()
        
        strategy = builder.create_wormhole_strategy(
            "wormhole_strategy",
            "binance",
            "kraken",
            "BTC/USD",
            1.0
        )
        
        assert strategy.strategy_name == "wormhole_strategy"
        assert "binance" in strategy.exchange_pair_primary


class TestOrderExecutor:
    """订单执行器单元测试"""
    
    def test_executor_initialization(self):
        """测试执行器初始化"""
        connector = HummingbotConnector()
        executor = OrderExecutor(connector)
        
        assert len(executor.active_orders) == 0
        assert len(executor.order_history) == 0
        assert executor.order_count == 0
    
    def test_create_order_when_not_connected(self):
        """测试未连接时创建订单"""
        connector = HummingbotConnector()
        executor = OrderExecutor(connector)
        
        order = executor.create_order(
            "binance", "BTC/USD", "BUY", 50000, 1.0
        )
        
        assert order is None
    
    def test_create_order_when_connected(self):
        """测试连接时创建订单"""
        connector = HummingbotConnector()
        connector.connect()
        executor = OrderExecutor(connector)
        
        order = executor.create_order(
            "binance", "BTC/USD", "BUY", 50000, 1.0
        )
        
        assert order is not None
        assert order.pair == "BTC/USD"
        assert order.side == "BUY"
        assert order.price == 50000


class TestTradeTracker:
    """交易跟踪器单元测试"""
    
    def test_tracker_initialization(self):
        """测试跟踪器初始化"""
        tracker = TradeTracker()
        assert len(tracker.active_trades) == 0
        assert len(tracker.trade_history) == 0
    
    def test_create_trade(self):
        """测试创建交易"""
        tracker = TradeTracker()
        connector = HummingbotConnector()
        connector.connect()
        executor = OrderExecutor(connector)
        
        order = executor.create_order(
            "binance", "BTC/USD", "BUY", 50000, 1.0
        )
        
        trade = tracker.create_trade("triangular", order)
        
        assert trade.trade_type == "triangular"
        assert len(trade.orders) == 1
        assert trade.status == "ACTIVE"


class TestHummingbotIntegrationLayer:
    """Hummingbot 集成层单元测试"""
    
    def test_layer_initialization(self):
        """测试集成层初始化"""
        layer = HummingbotIntegrationLayer()
        
        assert layer.connector is not None
        assert layer.strategy_builder is not None
        assert layer.order_executor is not None
        assert layer.trade_tracker is not None
    
    def test_initialize_connection(self):
        """测试初始化连接"""
        layer = HummingbotIntegrationLayer()
        result = layer.initialize_connection()
        
        assert result is True
        assert layer.connector.connected is True
    
    def test_get_system_status(self):
        """测试获取系统状态"""
        layer = HummingbotIntegrationLayer()
        layer.initialize_connection()
        
        status = layer.get_system_status()
        
        assert "hummingbot_status" in status
        assert "active_orders" in status
        assert "active_trades" in status


# 集成测试

class TestPhase4Integration:
    """Phase 4 集成测试"""
    
    def test_triangular_to_wormhole_integration(self):
        """测试三角套利到跨交易所套利的集成"""
        # 创建三角套利引擎
        tri_engine = TriangularArbitrageEngine()
        
        # 创建跨交易所模块
        wormhole_module = WormholeArbitrageModule()
        
        # 注册交易所
        wormhole_module.register_exchange(
            "binance", "Binance", ExchangeType.CENTRALIZED,
            0.05, 0.001, 0.0, ["BTC/USD", "ETH/USD"], 50
        )
        
        # 更新价格
        tri_engine.update_market_prices({
            "BTC/USD": (50000, 50010, 100),
            "ETH/BTC": (0.15, 0.151, 200),
            "ETH/USD": (7500, 7510, 150)
        })
        
        wormhole_module.update_price("binance", "BTC/USD", 50000, 50010, 100)
        
        assert tri_engine.price_monitor.get_price("BTC/USD") is not None
        assert wormhole_module.exchange_connector.get_price("binance", "BTC/USD") is not None
    
    def test_full_arbitrage_workflow(self):
        """测试完整套利工作流"""
        # 初始化所有组件
        tri_engine = TriangularArbitrageEngine()
        wormhole_module = WormholeArbitrageModule()
        hummingbot_layer = HummingbotIntegrationLayer()
        
        # 初始化连接
        hummingbot_layer.initialize_connection()
        
        # 注册交易所
        wormhole_module.register_exchange(
            "binance", "Binance", ExchangeType.CENTRALIZED,
            0.05, 0.001, 0.0, ["BTC/USD", "ETH/USD"], 50
        )
        
        # 更新价格
        prices = {
            "BTC/USD": (50000, 50010, 100),
            "ETH/USD": (3000, 3010, 500)
        }
        
        tri_engine.update_market_prices(prices)
        wormhole_module.update_price("binance", "BTC/USD", 50000, 50010, 100)
        
        # 分析机会
        tri_cycles = tri_engine.analyze_opportunities(
            ["BTC/USD", "ETH/BTC", "ETH/USD"]
        )
        
        # 系统状态检查
        hummingbot_status = hummingbot_layer.get_system_status()
        assert hummingbot_status is not None
        assert "active_trades" in hummingbot_status


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
