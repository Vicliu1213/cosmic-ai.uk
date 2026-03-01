import ray
import random
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# 導入量子任務（避免循環導入）
try:
    from cosmic import quantum_tasks
except ImportError:
    quantum_tasks = None


@ray.remote
class Agent:
    """異變全知宇宙交易智能體"""
    
    def __init__(self, agent_id: int, genome_config: Dict[str, Any], 
                 resources: Dict[str, Any], kb_ref: Any):
        self.id = agent_id
        self.genome = genome_config.get("theories", [])
        self.resources = resources
        self.reputation = 1.0
        
        # 處理知識庫參考
        try:
            # 如果是 ObjectRef，則 ray.get()；否則直接使用
            if hasattr(kb_ref, '__class__') and 'ObjectRef' in str(kb_ref.__class__):
                self.kb = ray.get(kb_ref)
            else:
                self.kb = kb_ref
        except:
            self.kb = kb_ref
            
        self.known_theories: Dict[str, str] = {}
        
        # 交易相關屬性
        self.trading_strategies = genome_config.get("strategies", {})
        self.trading_history = []
        self.total_profit = 0.0
        self.win_rate = 0.5
        self.risk_tolerance = float(resources.get("risk_tolerance", 0.5))
        self.strategy_weights: Dict[str, Dict[str, float]] = {}
        self.learning_rate = 0.01
        
        # 突變參數
        self.mutation_rate = float(genome_config.get("mutation_rate", 0.05))
        self.mutation_amplitude = float(genome_config.get("mutation_amplitude", 0.1))
        self.mutation_history = []
        
        # 量子特性
        self.entanglement_level = 0.0
        self.quantum_coherence = 1.0
        
        # 初始化知識
        self._load_theories()
        
        # 初始化策略
        self._initialize_strategies()
        
        print(f"異變智能體 {self.id} 已啟動 - 理論: {len(self.known_theories)}, 策略: {len(self.strategy_weights)}")

    def _load_theories(self):
        """載入理論知識"""
        try:
            if hasattr(self.kb, 'get_theory'):
                for theory in self.genome:
                    theory_name = theory.get('name', '')
                    if theory_name:
                        details = self.kb.get_theory(theory_name)
                        if details and isinstance(details, dict):
                            summary = details.get('summary', '')
                            self.known_theories[theory_name] = summary
        except Exception as e:
            print(f"載入理論失敗: {e}")

    def _initialize_strategies(self):
        """初始化交易策略"""
        default_strategies = {
            'mean_reversion': {'weight': 0.25, 'confidence': 0.7},
            'momentum': {'weight': 0.25, 'confidence': 0.7},
            'quantum_optimized': {'weight': 0.25, 'confidence': 0.8},
            'risk_parity': {'weight': 0.25, 'confidence': 0.75}
        }
        
        self.strategy_weights = self.trading_strategies or default_strategies
        
        # 歸一化權重
        total_weight = sum(v.get('weight', 0) for v in self.strategy_weights.values())
        if total_weight > 0:
            for strategy in self.strategy_weights.values():
                weight = strategy.get('weight', 0)
                strategy['weight'] = weight / total_weight

    def vote(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """投票機制 - 基於信譽和分析"""
        decision = "approve" if random.random() < (0.5 + self.reputation * 0.3) else "reject"
        weight = self.reputation
        
        return {
            "agent_id": self.id,
            "decision": decision,
            "weight": weight,
            "confidence": 0.7 + self.reputation * 0.3,
            "timestamp": datetime.now().isoformat()
        }

    def update_reputation(self, delta: float):
        """更新信譽"""
        new_rep = self.reputation + delta
        self.reputation = max(0.1, min(2.0, new_rep))

    def query_theory(self, theory_name: str) -> Optional[Dict[str, Any]]:
        """查詢理論"""
        if hasattr(self.kb, 'get_theory'):
            return self.kb.get_theory(theory_name)
        return None

    def perform_quantum_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """執行量子任務"""
        try:
            if quantum_tasks is None:
                return {"error": "量子任務模組未載入", "task_type": task_type}
            
            if task_type == "grover":
                result = quantum_tasks.run_grover(**kwargs)
            elif task_type == "shor":
                result = quantum_tasks.run_shor(**kwargs)
            elif task_type == "annealing":
                result = quantum_tasks.run_annealing(**kwargs)
            elif task_type == "vqe":
                result = quantum_tasks.run_vqe(**kwargs)
            elif task_type == "qaoa":
                result = quantum_tasks.run_qaoa(**kwargs)
            else:
                return {"error": f"未知任務: {task_type}"}
            
            return result
        except Exception as e:
            return {"error": str(e), "task_type": task_type}

    def mutate(self, base_rate: Optional[float] = None, 
               cycle_factor: Optional[float] = None) -> Dict[str, Any]:
        """完整的遺傳突變機制
        
        支援多種突變方式:
        - 點突變 (Point Mutation): 單個基因變化
        - 區段突變 (Segment Mutation): 多個相鄰基因變化
        - 反轉突變 (Inversion Mutation): 基因序列反轉
        - 交叉突變 (Crossover Mutation): 與其他代理交叉
        """
        br = base_rate if base_rate is not None else self.mutation_rate
        cf = cycle_factor if cycle_factor is not None else self.mutation_amplitude
        
        br = float(br)
        cf = float(cf)
        
        mutation_record: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'mutations': [],
            'total_changes': 0
        }
        
        # 應用點突變
        for theory in self.genome:
            if random.random() < br:
                old_val = float(theory.get('initial_expression', 1.0))
                delta = random.uniform(-cf, cf)
                new_val = max(0.1, min(2.0, old_val + delta))
                
                theory['initial_expression'] = new_val
                mutation_record['mutations'].append({
                    'type': 'point',
                    'theory': theory.get('name', 'unknown'),
                    'old_value': old_val,
                    'new_value': new_val,
                    'change': new_val - old_val
                })
                mutation_record['total_changes'] += 1
        
        # 應用策略權重突變
        for strategy_name in self.strategy_weights:
            if random.random() < br * 0.5:
                old_weight = float(self.strategy_weights[strategy_name].get('weight', 0.25))
                delta = random.uniform(-cf * 0.5, cf * 0.5)
                new_weight = max(0.05, min(0.5, old_weight + delta))
                
                self.strategy_weights[strategy_name]['weight'] = new_weight
                mutation_record['mutations'].append({
                    'type': 'strategy',
                    'strategy': strategy_name,
                    'old_weight': old_weight,
                    'new_weight': new_weight
                })
                mutation_record['total_changes'] += 1
        
        # 應用信譽突變
        if random.random() < br * 0.3:
            old_reputation = float(self.reputation)
            delta = random.uniform(-cf * 0.2, cf * 0.2)
            new_reputation = max(0.1, min(2.0, old_reputation + delta))
            
            self.reputation = new_reputation
            mutation_record['mutations'].append({
                'type': 'reputation',
                'old_value': old_reputation,
                'new_value': new_reputation
            })
            mutation_record['total_changes'] += 1
        
        self.mutation_history.append(mutation_record)
        self.quantum_coherence *= (1 - br * 0.1)
        
        return mutation_record

    def apply_crossover(self, other_agent_data: Dict[str, Any], 
                       crossover_rate: float = 0.5) -> Dict[str, Any]:
        """與其他代理進行基因交叉"""
        crossover_record: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'partner_id': other_agent_data.get('agent_id'),
            'exchanges': []
        }
        
        other_genome = other_agent_data.get('genome', [])
        
        # 交叉理論
        for i, theory in enumerate(self.genome):
            if random.random() < crossover_rate and i < len(other_genome):
                old_expr = float(theory.get('initial_expression', 1.0))
                other_expr = float(other_genome[i].get('initial_expression', 1.0))
                
                new_expr = (old_expr + other_expr) / 2.0
                theory['initial_expression'] = new_expr
                crossover_record['exchanges'].append({
                    'theory': theory.get('name', f'theory_{i}'),
                    'result': new_expr
                })
        
        # 交叉策略
        for strategy in self.strategy_weights:
            if strategy in other_agent_data.get('strategies', {}) and random.random() < crossover_rate:
                my_weight = float(self.strategy_weights[strategy].get('weight', 0.25))
                other_weight = float(other_agent_data['strategies'][strategy].get('weight', 0.25))
                self.strategy_weights[strategy]['weight'] = (my_weight + other_weight) / 2.0
        
        return crossover_record

    def select_trading_strategy(self, market_condition: str = "normal") -> Tuple[str, float]:
        """選擇交易策略
        
        根據市場條件和策略性能選擇最適合的策略
        """
        strategy_scores: Dict[str, float] = {}
        
        # 市場適應性評分
        market_bonuses = {
            'trending': {'momentum': 0.3, 'quantum_optimized': 0.2},
            'volatile': {'mean_reversion': 0.3, 'risk_parity': 0.2},
            'ranging': {'mean_reversion': 0.25, 'risk_parity': 0.15},
            'normal': {'quantum_optimized': 0.1}
        }
        
        market_bonus = market_bonuses.get(market_condition, {})
        
        for strategy_name, config in self.strategy_weights.items():
            base_weight = float(config.get('weight', 0.25))
            base_conf = float(config.get('confidence', 0.7))
            base_score = base_weight * base_conf
            bonus = float(market_bonus.get(strategy_name, 0))
            strategy_scores[strategy_name] = base_score + bonus
        
        # 選擇最高分策略
        best_strategy = max(strategy_scores, key=lambda x: strategy_scores[x])
        confidence = strategy_scores[best_strategy]
        
        return best_strategy, confidence

    def execute_trade(self, symbol: str, signal: Dict[str, Any], 
                     market_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行交易決策"""
        strategy, confidence = self.select_trading_strategy(
            market_data.get('condition', 'normal')
        )
        
        position_size = float(market_data.get('position_size', 0.1)) * confidence
        price = float(market_data.get('price', 0))
        
        signal_type = signal.get('signal', 'HOLD')
        if signal_type == 'BUY':
            action = 'BUY'
            quantity = int(position_size * 100)
        elif signal_type == 'SELL':
            action = 'SELL'
            quantity = int(position_size * 100)
        else:
            action = 'HOLD'
            quantity = 0
        
        trade_record: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.id,
            'symbol': symbol,
            'action': action,
            'strategy': strategy,
            'quantity': quantity,
            'price': price,
            'confidence': confidence
        }
        
        self.trading_history.append(trade_record)
        return trade_record

    def update_trading_performance(self, pnl: float, win: bool):
        """更新交易性能"""
        self.total_profit += pnl
        
        # 更新勝率
        total_trades = len([t for t in self.trading_history if t.get('action') != 'HOLD'])
        if total_trades > 0:
            wins = sum(1 for t in self.trading_history if t.get('profit', 0) > 0)
            self.win_rate = wins / total_trades
        
        # 根據交易結果調整信譽
        if win and pnl > 0:
            self.update_reputation(0.05)
        elif not win or pnl < 0:
            self.update_reputation(-0.03)
        
        # 調整風險容忍度
        if self.total_profit > 0:
            new_tolerance = min(1.0, self.risk_tolerance + 0.01)
            self.risk_tolerance = new_tolerance
        else:
            new_tolerance = max(0.3, self.risk_tolerance - 0.02)
            self.risk_tolerance = new_tolerance

    def get_agent_status(self) -> Dict[str, Any]:
        """取得代理狀態"""
        return {
            'agent_id': self.id,
            'reputation': self.reputation,
            'total_profit': self.total_profit,
            'win_rate': self.win_rate,
            'risk_tolerance': self.risk_tolerance,
            'strategy_weights': self.strategy_weights,
            'quantum_coherence': self.quantum_coherence,
            'trading_count': len(self.trading_history),
            'mutation_count': len(self.mutation_history),
            'timestamp': datetime.now().isoformat()
        }

    def export_agent_snapshot(self, filepath: str):
        """匯出代理快照"""
        snapshot = {
            'agent_id': self.id,
            'status': self.get_agent_status(),
            'genome': self.genome,
            'trading_history': self.trading_history[-100:],
            'mutation_history': self.mutation_history[-50:],
            'strategy_weights': self.strategy_weights
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
