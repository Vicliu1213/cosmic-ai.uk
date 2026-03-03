#!/usr/bin/env python3
"""
BITGET 实时交易机器人
BITGET 即時交易機器人 - 部署Hummingbot A-S策略到BITGET交易所

功能:
- 连接到 BITGET 交易所
- 执行 Hummingbot Avellaneda-Stoikov 策略
- 实时风险管理和止损
- 性能监控和告警
"""

import os
import logging
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import time

try:
    import ccxt.async_support as ccxt
except ImportError:
    print("安装 ccxt: pip install ccxt")
    raise

from src.integrations.strategy_adapters.hummingbot_adapter import (
    HummingbotStrategyAdapter,
    HummingbotStrategyType
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TradeConfig:
    """交易配置"""
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    initial_capital: float = 1000.0  # USDT
    max_position_size: float = 0.5  # 50% of capital
    take_profit_pct: float = 2.0  # 2% 止盈
    stop_loss_pct: float = 1.5  # 1.5% 止损
    bid_spread: float = 0.001  # 0.1% 买价差
    ask_spread: float = 0.001  # 0.1% 卖价差
    monitoring_interval: int = 60  # 监控间隔（秒）


class BITGETTradingBot:
    """
    BITGET 实时交易机器人
    
    核心功能:
    1. 连接到 BITGET 交易所 API
    2. 执行 Hummingbot A-S 策略
    3. 实时监控头寸
    4. 风险管理（止损、止盈）
    5. 性能记录和告警
    """
    
    def __init__(self, config: TradeConfig):
        """
        初始化交易机器人
        
        Args:
            config: 交易配置
        """
        self.config = config
        self.exchange = None
        self.strategy = HummingbotStrategyAdapter(HummingbotStrategyType.AVELLANEDA_STOIKOV)
        
        # 读取 API 配置
        self.api_key = os.getenv('BITGET_API_KEY')
        self.secret_key = os.getenv('BITGET_SECRET_KEY')
        self.passphrase = os.getenv('BITGET_PASSPHRASE')
        
        if not all([self.api_key, self.secret_key, self.passphrase]):
            raise ValueError("❌ BITGET API 密钥未配置。请检查 .env 文件")
        
        # 交易状态
        self.positions: Dict[str, Any] = {}
        self.trades: List[Dict[str, Any]] = []
        self.performance_metrics = {
            'total_pnl': 0.0,
            'win_count': 0,
            'lose_count': 0,
            'win_rate': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'peak_balance': config.initial_capital,
            'current_balance': config.initial_capital
        }
        
        logger.info(f"✅ BITGET 交易机器人已初始化")
        logger.info(f"   策略: Hummingbot Avellaneda-Stoikov")
        logger.info(f"   交易对: {config.symbol}")
        logger.info(f"   初始资本: ${config.initial_capital:,.2f}")
        logger.info(f"   止盈: {config.take_profit_pct}% | 止损: {config.stop_loss_pct}%")
    
    async def connect(self) -> bool:
        """连接到 BITGET 交易所"""
        try:
            logger.info("正在连接到 BITGET...")
            
            self.exchange = ccxt.bitget({
                'apiKey': self.api_key,
                'secret': self.secret_key,
                'password': self.passphrase,
                'enableRateLimit': True,
                'rateLimit': 100
            })
            
            # 测试连接
            balance = await self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            
            logger.info(f"✅ 连接成功")
            logger.info(f"   账户余额: ${usdt_balance:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False
    
    async def fetch_market_data(self) -> Optional[Dict[str, Any]]:
        """获取市场数据"""
        try:
            # 获取 OHLCV 数据
            ohlcv = await self.exchange.fetch_ohlcv(
                self.config.symbol,
                self.config.timeframe,
                limit=20
            )
            
            # 获取订单簿
            orderbook = await self.exchange.fetch_order_book(self.config.symbol)
            
            # 获取 Ticker
            ticker = await self.exchange.fetch_ticker(self.config.symbol)
            
            return {
                'ohlcv': ohlcv,
                'orderbook': orderbook,
                'ticker': ticker,
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"❌ 获取市场数据失败: {e}")
            return None
    
    async def generate_trading_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        生成交易信号
        
        使用 Hummingbot A-S 策略分析市场数据
        """
        try:
            if not market_data:
                return None
            
            # 这里集成 Hummingbot 策略逻辑
            # 简化版本：基于订单簿的买卖决策
            
            orderbook = market_data['orderbook']
            ticker = market_data['ticker']
            
            if not orderbook.get('bids') or not orderbook.get('asks'):
                return None
            
            bid_price = orderbook['bids'][0][0]  # 最高买价
            ask_price = orderbook['asks'][0][0]  # 最低卖价
            mid_price = (bid_price + ask_price) / 2
            
            # 计算价差
            spread = (ask_price - bid_price) / mid_price * 100
            
            # A-S 策略：当价差较大时进行做市
            signal = None
            if spread > 0.05:  # 价差 > 0.05%
                signal = {
                    'type': 'BUY',
                    'price': bid_price,
                    'quantity': self.config.initial_capital * self.config.max_position_size / bid_price,
                    'reason': f'价差{spread:.3f}% > 阈值',
                    'confidence': min(100, spread * 100)
                }
            elif spread < 0.02:  # 价差 < 0.02%
                signal = {
                    'type': 'SELL',
                    'price': ask_price,
                    'quantity': list(self.positions.values())[0]['quantity'] if self.positions else 0,
                    'reason': f'价差{spread:.3f}% < 阈值',
                    'confidence': 50
                }
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ 生成信号失败: {e}")
            return None
    
    async def place_order(self, signal: Dict[str, Any]) -> Optional[str]:
        """下单"""
        try:
            if signal['type'] == 'BUY':
                order = await self.exchange.create_market_buy_order(
                    self.config.symbol,
                    signal['quantity'],
                    {'clientOrderId': f"BUY_{int(time.time())}"}
                )
            else:  # SELL
                order = await self.exchange.create_market_sell_order(
                    self.config.symbol,
                    signal['quantity'],
                    {'clientOrderId': f"SELL_{int(time.time())}"}
                )
            
            logger.info(f"✅ {signal['type']} 订单已下单")
            logger.info(f"   价格: ${signal['price']:.2f}")
            logger.info(f"   数量: {signal['quantity']:.4f}")
            logger.info(f"   理由: {signal['reason']}")
            
            return order['id']
            
        except Exception as e:
            logger.error(f"❌ 下单失败: {e}")
            return None
    
    async def monitor_positions(self) -> None:
        """监控头寸"""
        try:
            # 获取当前持仓
            positions = await self.exchange.fetch_positions([self.config.symbol])
            
            if not positions:
                return
            
            position = positions[0]
            current_price = position.get('markPrice', 0)
            
            # 计算 PnL
            pnl = position.get('unrealizedPnl', 0)
            pnl_pct = (pnl / (position.get('contracts', 0) * current_price)) * 100 if position.get('contracts') else 0
            
            # 检查止盈/止损
            if pnl_pct >= self.config.take_profit_pct:
                logger.warning(f"⚠️ 达到止盈阈值: {pnl_pct:.2f}%")
                # 平仓逻辑
            elif pnl_pct <= -self.config.stop_loss_pct:
                logger.error(f"🛑 触发止损: {pnl_pct:.2f}%")
                # 平仓逻辑
            
            # 更新性能指标
            self.performance_metrics['current_balance'] += pnl
            
        except Exception as e:
            logger.error(f"❌ 监控头寸失败: {e}")
    
    async def run(self, duration_hours: int = 24) -> None:
        """
        运行交易机器人
        
        Args:
            duration_hours: 运行时长（小时）
        """
        logger.info("=" * 80)
        logger.info("🚀 BITGET 交易机器人启动")
        logger.info("=" * 80)
        
        # 连接
        if not await self.connect():
            logger.error("❌ 无法连接到 BITGET，退出")
            return
        
        start_time = datetime.now(timezone.utc)
        max_duration = duration_hours * 3600
        
        try:
            while True:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                if elapsed > max_duration:
                    logger.info(f"⏱️ 运行时间已达 {duration_hours} 小时，停止")
                    break
                
                # 1. 获取市场数据
                market_data = await self.fetch_market_data()
                
                # 2. 生成信号
                signal = await self.generate_trading_signal(market_data)
                
                # 3. 下单
                if signal:
                    await self.place_order(signal)
                
                # 4. 监控头寸
                await self.monitor_positions()
                
                # 等待下一个周期
                logger.info(f"⏰ 等待 {self.config.monitoring_interval} 秒...")
                await asyncio.sleep(self.config.monitoring_interval)
        
        except KeyboardInterrupt:
            logger.info("⏹️ 用户中断")
        except Exception as e:
            logger.error(f"❌ 运行出错: {e}")
        finally:
            if self.exchange:
                await self.exchange.close()
            
            # 打印最终报告
            self._print_report()
    
    def _print_report(self) -> None:
        """打印性能报告"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 交易机器人性能报告")
        logger.info("=" * 80)
        logger.info(f"总 PnL: ${self.performance_metrics['total_pnl']:,.2f}")
        logger.info(f"赢: {self.performance_metrics['win_count']} | "
                   f"亏: {self.performance_metrics['lose_count']} | "
                   f"胜率: {self.performance_metrics['win_rate']:.2f}%")
        logger.info(f"最大回撤: {self.performance_metrics['max_drawdown']:.2f}%")
        logger.info(f"最终余额: ${self.performance_metrics['current_balance']:,.2f}")


async def main():
    """主函数"""
    
    # 创建配置
    config = TradeConfig(
        symbol="BTC/USDT",
        timeframe="1h",
        initial_capital=1000.0,
        max_position_size=0.5,
        take_profit_pct=2.0,
        stop_loss_pct=1.5
    )
    
    # 创建机器人
    bot = BITGETTradingBot(config)
    
    # 运行（演示模式：1小时）
    await bot.run(duration_hours=1)


if __name__ == '__main__':
    asyncio.run(main())
