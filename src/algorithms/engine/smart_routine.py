"""
智能路由引擎 - 多交易所最優執行路徑選擇
支援 Binance, Bybit, OKX, Bitget 四大交易所的智能路由
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
from collections import deque

from ..base_engine import BaseEngine, EngineSignal

logger = logging.getLogger(__name__)

@dataclass
class ExchangeMetrics:
    """交易所實時指標"""
    exchange: str
    latency: float = 0.0           # 延遲（毫秒）
    liquidity: float = 0.0         # 流動性（USDT）
    fee: float = 0.001              # 手續費率
    spread: float = 0.0001          # 買賣價差
    depth: float = 0.0              # 訂單簿深度
    last_update: datetime = field(default_factory=datetime.now)
    success_rate: float = 1.0       # 成功率
    volume_24h: float = 0.0         # 24小時成交量
    order_book_imbalance: float = 0.0  # 訂單簿不平衡度

@dataclass
class RoutingDecision:
    """路由決策結果"""
    exchange: str
    order_type: str
    estimated_cost: float
    estimated_slippage: float
    confidence: float
    reason: str
    alternatives: List[Dict]

class SmartRoutingEngine(BaseEngine):
    """
    智能路由引擎
    根據實時市場數據，動態選擇最優交易所執行訂單
    """

    def __init__(self, engine_id: str, output_queue: asyncio.Queue, config: Dict):
        super().__init__(engine_id, output_queue)
        self.config = config
        self.exchanges = config.get('exchanges', ['binance', 'bybit', 'okx', 'bitget'])
        self.strategy = config.get('strategy', 'dynamic')
        self.update_interval = config.get('update_interval', 10)
        self.metrics_cache = {}  # exchange -> ExchangeMetrics
        self.performance_history = {}  # exchange -> deque of performance
        self.routing_history = []
        self._running = True

        # 初始化各交易所指標
        for ex in self.exchanges:
            self.metrics_cache[ex] = ExchangeMetrics(exchange=ex)
            self.performance_history[ex] = deque(maxlen=100)

        # 啟動後台監控
        asyncio.create_task(self._monitor_exchanges())

    async def _monitor_exchanges(self):
        """後台監控所有交易所的實時指標"""
        while self._running:
            try:
                for exchange in self.exchanges:
                    await self._update_exchange_metrics(exchange)

                # 智能路由決策更新
                if self.strategy == 'dynamic':
                    await self._dynamic_optimization()

                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"交易所監控錯誤: {e}")

    async def _update_exchange_metrics(self, exchange: str):
        """更新單個交易所的實時指標"""
        try:
            # 獲取交易所客戶端（需從外部注入）
            client = self._get_exchange_client(exchange)
            if not client:
                return

            # 獲取訂單簿
            orderbook = await client.fetch_order_book('BTCUSDT', limit=10)
            if orderbook:
                bids = orderbook['bids']
                asks = orderbook['asks']

                # 計算流動性（前10檔買賣深度總和）
                bid_liquidity = sum(bid[1] * bid[0] for bid in bids[:5])
                ask_liquidity = sum(ask[1] * ask[0] for ask in asks[:5])
                self.metrics_cache[exchange].liquidity = (bid_liquidity + ask_liquidity) / 2

                # 計算價差
                best_bid = bids[0][0] if bids else 0
                best_ask = asks[0][0] if asks else 0
                if best_ask > 0:
                    self.metrics_cache[exchange].spread = (best_ask - best_bid) / best_ask

                # 計算訂單簿不平衡度
                bid_volume = sum(bid[1] for bid in bids[:5])
                ask_volume = sum(ask[1] for ask in asks[:5])
                total = bid_volume + ask_volume
                if total > 0:
                    self.metrics_cache[exchange].order_book_imbalance = (bid_volume - ask_volume) / total

            # 獲取24小時成交量
            ticker = await client.fetch_ticker('BTCUSDT')
            if ticker and 'quoteVolume' in ticker:
                self.metrics_cache[exchange].volume_24h = ticker['quoteVolume']

            # 更新延遲（模擬）
            self.metrics_cache[exchange].latency = await self._measure_latency(client)

            # 更新成功率（基於歷史）
            if self.performance_history[exchange]:
                self.metrics_cache[exchange].success_rate = np.mean(self.performance_history[exchange])

            self.metrics_cache[exchange].last_update = datetime.now()

        except Exception as e:
            logger.warning(f"更新 {exchange} 指標失敗: {e}")

    async def _measure_latency(self, client) -> float:
        """測量交易所延遲"""
        try:
            start = datetime.now()
            await client.fetch_time()
            latency = (datetime.now() - start).total_seconds() * 1000
            return latency
        except:
            return 100.0  # 默認 100ms

    def _get_exchange_client(self, exchange: str):
        """獲取交易所客戶端（需從外部注入）"""
        # 此處應從全局客戶端管理器獲取
        # 簡化實現，返回 None
        return None

    async def _dynamic_optimization(self):
        """動態優化路由策略"""
        # 根據各交易所實時表現調整權重
        weights = self._calculate_exchange_weights()

        # 更新路由策略
        self._routing_weights = weights

        logger.debug(f"路由權重更新: {weights}")

    def _calculate_exchange_weights(self) -> Dict[str, float]:
        """計算各交易所的動態權重"""
        weights = {}
        total_score = 0

        for ex in self.exchanges:
            metrics = self.metrics_cache[ex]

            # 綜合評分
            scores = {
                'latency': 1.0 / (metrics.latency + 1),
                'liquidity': metrics.liquidity / 1000000,
                'spread': 1.0 - metrics.spread * 100,
                'depth': metrics.depth,
                'success_rate': metrics.success_rate
            }

            # 權重計算
            score = (
                scores['latency'] * 0.3 +
                scores['liquidity'] * 0.25 +
                scores['spread'] * 0.2 +
                scores['depth'] * 0.15 +
                scores['success_rate'] * 0.1
            )

            weights[ex] = max(0.05, min(0.5, score))
            total_score += weights[ex]

        # 歸一化
        if total_score > 0:
            for ex in weights:
                weights[ex] /= total_score

        return weights

    async def route_order(self, symbol: str, side: str, amount: float,
                          order_type: str = 'market') -> RoutingDecision:
        """
        路由訂單到最優交易所

        Args:
            symbol: 交易對
            side: buy/sell
            amount: 數量
            order_type: market/limit

        Returns:
            RoutingDecision: 路由決策
        """
        candidates = []

        for exchange in self.exchanges:
            metrics = self.metrics_cache[exchange]

            # 估算成本
            estimated_cost = await self._estimate_cost(
                exchange, symbol, side, amount, order_type
            )

            # 估算滑點
            estimated_slippage = await self._estimate_slippage(
                exchange, symbol, amount
            )

            # 計算信心度
            confidence = self._calculate_confidence(metrics, estimated_slippage)

            candidates.append({
                'exchange': exchange,
                'estimated_cost': estimated_cost,
                'estimated_slippage': estimated_slippage,
                'confidence': confidence,
                'metrics': {
                    'latency': metrics.latency,
                    'liquidity': metrics.liquidity,
                    'spread': metrics.spread
                }
            })

        # 根據策略選擇最佳交易所
        if self.strategy == 'cost_optimal':
            best = min(candidates, key=lambda x: x['estimated_cost'])
        elif self.strategy == 'latency_optimal':
            best = min(candidates, key=lambda x: x['metrics']['latency'])
        elif self.strategy == 'liquidity_optimal':
            best = max(candidates, key=lambda x: x['metrics']['liquidity'])
        else:  # dynamic
            # 加權評分
