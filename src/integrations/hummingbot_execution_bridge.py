#!/usr/bin/env python3
"""
Hummingbot 执行层 - 决策到执行的转换桥梁
Hummingbot Execution Layer - Decision to Execution Bridge

这个模块负责将 Cosmic AI 和 LLM-TradeBot 的决策信号转换为
Hummingbot 可执行的命令，并管理订单生命周期。

This module converts Cosmic AI and LLM-TradeBot decision signals
into Hummingbot executable commands and manages order lifecycle.
"""

import logging
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json
import yaml

logger = logging.getLogger(__name__)


# ==================== 数据类型定义 ====================

class StrategyType(Enum):
    """Hummingbot 策略类型"""
    PURE_MARKET_MAKING = "pure_market_making"
    CROSS_EXCHANGE_MARKET_MAKING = "cross_exchange_market_making"
    TRIANGULAR_ARBITRAGE = "triangular_arbitrage"
    WORMHOLE_ARBITRAGE = "wormhole_arbitrage"


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"  # 等待提交
    SUBMITTED = "submitted"  # 已提交到 Hummingbot
    RUNNING = "running"  # 策略正在运行
    PARTIALLY_FILLED = "partially_filled"  # 部分成交
    FILLED = "filled"  # 完全成交
    CANCELLED = "cancelled"  # 已取消
    FAILED = "failed"  # 执行失败
    ERROR = "error"  # 错误


@dataclass
class TradingSignal:
    """Cosmic 交易信号"""
    signal_id: str
    timestamp: datetime
    symbol: str  # 交易对 (e.g., "BTC-USDT")
    direction: str  # "BUY" or "SELL"
    confidence: float  # 0.0-1.0
    strength: float  # 信号强度
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """执行上下文"""
    market_price: float  # 当前市场价格
    bid_price: float  # 最优买价
    ask_price: float  # 最优卖价
    bid_volume: float  # 买盘量
    ask_volume: float  # 卖盘量
    order_book_depth: int = 20  # 订单簿深度
    volatility: float = 0.0  # 价格波动率


@dataclass
class RiskParameters:
    """风险参数"""
    max_position_size: float  # 最大持仓量
    max_order_size: float  # 最大订单量
    max_slippage: float  # 最大滑点 (%)
    max_daily_loss: float  # 最大单日亏损 (USD)
    portfolio_value: float  # 投资组合总值 (USD)
    risk_per_trade: float = 0.02  # 每笔交易的风险占比 (2%)


@dataclass
class ExecutionResult:
    """执行结果"""
    signal_id: str
    status: ExecutionStatus
    hummingbot_order_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    message: str = ""
    errors: List[str] = field(default_factory=list)
    submitted_config: Optional[Dict] = None


@dataclass
class HummingbotOrder:
    """Hummingbot 订单信息"""
    order_id: str
    exchange: str
    symbol: str
    side: str  # "buy" or "sell"
    price: float
    amount: float
    status: ExecutionStatus
    created_at: datetime
    filled_amount: float = 0.0
    average_price: float = 0.0
    fee: float = 0.0


@dataclass
class StrategyConfig:
    """策略配置参数"""
    strategy_type: StrategyType
    pair: str
    order_amount: float
    bid_spread: float = 0.1  # 做市买盘价差 (%)
    ask_spread: float = 0.1  # 做市卖盘价差 (%)
    inventory_skew_enabled: bool = True
    hanging_orders_enabled: bool = False
    order_optimization_enabled: bool = True
    max_order_age_secs: int = 60
    exchange_pair_primary: Optional[str] = None  # 跨交易所时使用
    exchange_pair_secondary: Optional[str] = None
    exchange_pair_tertiary: Optional[str] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)


# ==================== 主要模块 ====================

class HummingbotConfigBuilder:
    """
    Hummingbot 配置构建器
    根据交易决策动态生成 YAML 配置文件
    
    Hummingbot Config Builder
    Dynamically generates YAML config files based on trading decisions
    """
    
    def __init__(self):
        """初始化配置构建器"""
        self.logger = logging.getLogger(f"{__name__}.HummingbotConfigBuilder")
    
    def build_pure_market_making_config(
        self,
        pair: str,
        order_amount: float,
        bid_spread: float = 0.1,
        ask_spread: float = 0.1,
        exchange: str = "binance",
        **kwargs
    ) -> str:
        """
        构建纯做市策略配置
        
        Build pure market making strategy config
        
        Args:
            pair: Trading pair (e.g., "BTC-USDT")
            order_amount: Order size
            bid_spread: Bid spread in percent
            ask_spread: Ask spread in percent
            exchange: Exchange name
            **kwargs: Additional parameters
            
        Returns:
            YAML configuration string
        """
        config = {
            'strategy': 'pure_market_making',
            'exchange': exchange,
            'market': pair,
            'bid_spread': bid_spread / 100.0,  # Convert to decimal
            'ask_spread': ask_spread / 100.0,
            'order_amount': order_amount,
            'order_refresh_time': 30.0,
            'max_order_age': kwargs.get('max_order_age_secs', 60),
            'order_optimization_enabled': kwargs.get('order_optimization_enabled', True),
            'ask_order_optimization_depth': 0.0,
            'bid_order_optimization_depth': 0.0,
            'add_transaction_costs_to_orders': True,
            'inventory_skew_enabled': kwargs.get('inventory_skew_enabled', True),
            'inventory_target_base_pct': 50.0,
            'inventory_range_multiplier': 1.0,
            'hanging_orders_enabled': kwargs.get('hanging_orders_enabled', False),
        }
        
        # 添加自定义参数
        config.update(kwargs.get('custom_params', {}))
        
        return yaml.dump(config, default_flow_style=False)
    
    def build_cross_exchange_config(
        self,
        maker_exchange: str,
        taker_exchange: str,
        maker_pair: str,
        taker_pair: str,
        order_amount: float,
        **kwargs
    ) -> str:
        """
        构建跨交易所做市配置
        
        Build cross-exchange market making config
        
        Args:
            maker_exchange: Maker exchange (e.g., "binance")
            taker_exchange: Taker exchange (e.g., "kraken")
            maker_pair: Maker pair
            taker_pair: Taker pair
            order_amount: Order size
            **kwargs: Additional parameters
            
        Returns:
            YAML configuration string
        """
        config = {
            'strategy': 'cross_exchange_market_making',
            'maker_market': maker_pair,
            'maker_exchange': maker_exchange,
            'taker_market': taker_pair,
            'taker_exchange': taker_exchange,
            'order_amount': order_amount,
            'maker_order_optimization_enabled': True,
            'ask_order_optimization_depth': 0.0,
            'bid_order_optimization_depth': 0.0,
            'use_oracle_conversion_rates': False,
        }
        
        config.update(kwargs.get('custom_params', {}))
        return yaml.dump(config, default_flow_style=False)
    
    def build_triangular_arbitrage_config(
        self,
        exchange: str,
        triangle_pairs: List[str],
        order_amount: float,
        **kwargs
    ) -> str:
        """
        构建三角套利配置
        
        Build triangular arbitrage config
        
        Args:
            exchange: Exchange name
            triangle_pairs: List of 3 trading pairs forming triangle
            order_amount: Order size
            **kwargs: Additional parameters
            
        Returns:
            YAML configuration string
        """
        config = {
            'strategy': 'triangular_arbitrage',
            'exchange': exchange,
            'market_pairs': triangle_pairs,
            'order_amount': order_amount,
            'min_profitability': kwargs.get('min_profitability', 0.001),  # 0.1%
            'slippage_buffer': kwargs.get('slippage_buffer', 0.0025),  # 0.25%
        }
        
        config.update(kwargs.get('custom_params', {}))
        return yaml.dump(config, default_flow_style=False)
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证配置合法性
        
        Validate configuration legality
        
        Args:
            config: Configuration dictionary
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['strategy', 'exchange', 'market', 'order_amount']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # 验证数值范围
        if config.get('bid_spread', 0) < 0 or config.get('bid_spread', 1) > 10:
            errors.append("Bid spread must be between 0 and 10")
        
        if config.get('ask_spread', 0) < 0 or config.get('ask_spread', 1) > 10:
            errors.append("Ask spread must be between 0 and 10")
        
        if config.get('order_amount', 0) <= 0:
            errors.append("Order amount must be positive")
        
        return len(errors) == 0, errors


class HummingbotExecutionBridge:
    """
    Hummingbot 执行桥梁
    将 Cosmic 和 LLM 的决策转换为 Hummingbot 命令
    
    Hummingbot Execution Bridge
    Converts Cosmic and LLM decisions into Hummingbot commands
    """
    
    def __init__(
        self,
        hummingbot_host: str = "localhost",
        hummingbot_port: int = 8000,
        hummingbot_client: Optional[Any] = None,
    ):
        """
        初始化执行桥梁
        
        Initialize execution bridge
        
        Args:
            hummingbot_host: Hummingbot host address
            hummingbot_port: Hummingbot port number
            hummingbot_client: Optional external Hummingbot client
        """
        self.host = hummingbot_host
        self.port = hummingbot_port
        self.client = hummingbot_client
        self.config_builder = HummingbotConfigBuilder()
        self.logger = logging.getLogger(f"{__name__}.HummingbotExecutionBridge")
        self.execution_history: List[ExecutionResult] = []
        self.active_orders: Dict[str, HummingbotOrder] = {}
    
    async def execute_signal(
        self,
        signal: TradingSignal,
        context: ExecutionContext,
        risk_params: RiskParameters,
    ) -> ExecutionResult:
        """
        执行单个交易信号
        
        Execute a single trading signal
        
        Args:
            signal: Trading signal from Cosmic/LLM
            context: Market execution context
            risk_params: Risk parameters
            
        Returns:
            ExecutionResult with status and order ID
        """
        self.logger.info(f"Processing signal {signal.signal_id} for {signal.symbol}")
        
        result = ExecutionResult(
            signal_id=signal.signal_id,
            status=ExecutionStatus.PENDING,
        )
        
        try:
            # 1. 验证信号
            validation_errors = self._validate_signal(signal, context, risk_params)
            if validation_errors:
                result.status = ExecutionStatus.FAILED
                result.errors = validation_errors
                self.logger.error(f"Signal validation failed: {validation_errors}")
                return result
            
            # 2. 计算订单大小
            order_amount = self._calculate_order_size(signal, context, risk_params)
            if order_amount <= 0:
                result.status = ExecutionStatus.FAILED
                result.errors = ["Invalid order size calculation"]
                return result
            
            # 3. 生成策略配置
            config = self._build_strategy_config(signal, context, order_amount)
            config_yaml = self._generate_config_yaml(config)
            
            # 4. 提交到 Hummingbot
            order_id = await self._submit_to_hummingbot(config_yaml, config)
            
            if order_id:
                result.status = ExecutionStatus.SUBMITTED
                result.hummingbot_order_id = order_id
                # Convert config to dict for storage
                result.submitted_config = {
                    'strategy_type': config.strategy_type.value,
                    'pair': config.pair,
                    'order_amount': config.order_amount,
                    'bid_spread': config.bid_spread,
                    'ask_spread': config.ask_spread,
                }
                self.logger.info(f"Signal {signal.signal_id} submitted as order {order_id}")
            else:
                result.status = ExecutionStatus.FAILED
                result.errors = ["Failed to submit to Hummingbot"]
        
        except Exception as e:
            result.status = ExecutionStatus.ERROR
            result.errors = [str(e)]
            self.logger.exception(f"Error executing signal {signal.signal_id}")
        
        self.execution_history.append(result)
        return result
    
    def _validate_signal(
        self,
        signal: TradingSignal,
        context: ExecutionContext,
        risk_params: RiskParameters,
    ) -> List[str]:
        """验证信号合法性"""
        errors = []
        
        # 检查置信度
        if signal.confidence < 0.3:
            errors.append(f"Signal confidence too low: {signal.confidence}")
        
        # 检查市场条件
        if context.bid_volume <= 0 or context.ask_volume <= 0:
            errors.append("Insufficient market liquidity")
        
        # 检查风险参数
        if risk_params.max_order_size <= 0:
            errors.append("Invalid risk parameters")
        
        return errors
    
    def _calculate_order_size(
        self,
        signal: TradingSignal,
        context: ExecutionContext,
        risk_params: RiskParameters,
    ) -> float:
        """
        计算订单大小
        基于信号强度、市场条件、风险参数
        """
        base_size = risk_params.max_order_size * signal.confidence
        
        # 根据市场流动性调整
        liquidity_score = min(
            1.0,
            (context.bid_volume + context.ask_volume) / 1000000.0
        )
        adjusted_size = base_size * (0.5 + 0.5 * liquidity_score)
        
        # 确保不超过最大风险
        max_risk_size = (
            risk_params.portfolio_value * risk_params.risk_per_trade /
            context.market_price
        )
        
        return min(adjusted_size, max_risk_size, risk_params.max_order_size)
    
    def _build_strategy_config(
        self,
        signal: TradingSignal,
        context: ExecutionContext,
        order_amount: float,
    ) -> StrategyConfig:
        """根据信号构建策略配置"""
        return StrategyConfig(
            strategy_type=StrategyType.PURE_MARKET_MAKING,
            pair=signal.symbol,
            order_amount=order_amount,
            bid_spread=0.1,
            ask_spread=0.1,
        )
    
    def _generate_config_yaml(self, config: StrategyConfig) -> str:
        """生成 YAML 配置"""
        if config.strategy_type == StrategyType.PURE_MARKET_MAKING:
            return self.config_builder.build_pure_market_making_config(
                pair=config.pair,
                order_amount=config.order_amount,
                bid_spread=config.bid_spread,
                ask_spread=config.ask_spread,
            )
        else:
            raise ValueError(f"Unsupported strategy type: {config.strategy_type}")
    
    async def _submit_to_hummingbot(
        self,
        config_yaml: str,
        config: StrategyConfig,
    ) -> Optional[str]:
        """
        提交配置到 Hummingbot
        
        Submit configuration to Hummingbot
        
        Args:
            config_yaml: YAML configuration string
            config: Strategy configuration object
            
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # 如果有外部客户端，使用它
            if self.client:
                order_id = await self.client.submit_strategy(config_yaml)
                return order_id
            
            # 否则，生成一个本地 order ID
            import uuid
            order_id = f"HMB-{uuid.uuid4().hex[:12].upper()}"
            self.logger.info(f"Generated local order ID: {order_id}")
            
            return order_id
        
        except Exception as e:
            self.logger.error(f"Failed to submit to Hummingbot: {e}")
            return None
    
    async def get_order_status(self, order_id: str) -> Optional[HummingbotOrder]:
        """获取订单状态"""
        return self.active_orders.get(order_id)
    
    def get_execution_history(
        self,
        limit: int = 100,
    ) -> List[ExecutionResult]:
        """获取执行历史"""
        return self.execution_history[-limit:]


class HummingbotIntegrationLogger:
    """
    Hummingbot 集成日志记录器
    记录所有执行事件
    """
    
    def __init__(self, log_file: str = "hummingbot_integration.log"):
        """初始化日志记录器"""
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
    
    def log_signal_received(self, signal: TradingSignal):
        """记录收到的信号"""
        self.logger.info(
            f"Signal received: {signal.signal_id}, "
            f"symbol={signal.symbol}, "
            f"direction={signal.direction}, "
            f"confidence={signal.confidence}"
        )
    
    def log_execution_result(self, result: ExecutionResult):
        """记录执行结果"""
        self.logger.info(
            f"Execution result: {result.signal_id}, "
            f"status={result.status.value}, "
            f"order_id={result.hummingbot_order_id}"
        )
        if result.errors:
            self.logger.error(f"Errors: {result.errors}")


# ==================== 导出接口 ====================

def create_hummingbot_execution_layer() -> HummingbotExecutionBridge:
    """
    工厂函数：创建 Hummingbot 执行层
    
    Factory function to create Hummingbot execution layer
    """
    return HummingbotExecutionBridge()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 创建示例
    bridge = HummingbotExecutionBridge()
    config_builder = HummingbotConfigBuilder()
    
    # 构建配置示例
    config_yaml = config_builder.build_pure_market_making_config(
        pair="BTC-USDT",
        order_amount=1.0,
        bid_spread=0.1,
        ask_spread=0.1,
    )
    
    print("Generated Hummingbot Config:")
    print(config_yaml)
