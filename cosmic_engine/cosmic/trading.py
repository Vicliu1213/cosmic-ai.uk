import ray
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json
import numpy as np

@dataclass
class Order:
    """交易訂單"""
    symbol: str
    quantity: int
    side: str  # 'BUY' or 'SELL'
    price: float
    order_type: str = 'MARKET'
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class Position:
    """持倉"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    entry_time: str
    
    def get_unrealized_pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.quantity
    
    def get_pnl_percentage(self) -> float:
        if self.entry_price == 0:
            return 0
        return (self.current_price - self.entry_price) / self.entry_price * 100

@ray.remote
class TradingEngine:
    """宇宙交易引擎 - 增強型交易系統"""
    
    def __init__(self, config: Dict[str, Any]):
        self.capital = config.get("initial_capital", 100000)
        self.available_capital = self.capital
        self.max_position_pct = config.get("max_position_pct", 0.1)
        self.max_daily_loss_pct = config.get("max_daily_loss_pct", 0.05)
        self.use_leverage = config.get("use_leverage", False)
        self.max_leverage = config.get("max_leverage", 2.0)
        
        self.positions = {}  # 當前持倉 {symbol: Position}
        self.order_history = []  # 訂單歷史
        self.trade_log = []  # 交易日誌
        self.daily_pnl = 0
        self.total_pnl = 0
        self.trade_count = 0
        self.win_count = 0
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0
        }
        
        print(f"交易引擎已啟動 - 資本: {self.capital}, 最大持倉: {self.max_position_pct*100}%")

    def place_order(self, symbol: str, quantity: int, side: str, price: float, 
                   order_type: str = "MARKET") -> Dict[str, Any]:
        """下訂單"""
        order = Order(symbol, quantity, side, price, order_type)
        cost = quantity * price
        pnl = 0.0  # 初始化 pnl
        
        # 檢查風險
        if not self._check_risk(cost, side):
            return {
                'status': 'REJECTED',
                'reason': '風險控制拒絕',
                'cost': cost,
                'available': self.available_capital
            }
        
        # 執行訂單
        if side.upper() == 'BUY':
            self.available_capital -= cost
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    entry_time=datetime.now().isoformat()
                )
            else:
                pos = self.positions[symbol]
                total_qty = pos.quantity + quantity
                pos.entry_price = (pos.entry_price * pos.quantity + price * quantity) / total_qty
                pos.quantity = total_qty
        
        elif side.upper() == 'SELL':
            if symbol in self.positions:
                pos = self.positions[symbol]
                if pos.quantity >= quantity:
                    self.available_capital += cost
                    pnl = pos.get_unrealized_pnl() * (quantity / pos.quantity)
                    self.total_pnl += pnl
                    self.daily_pnl += pnl
                    
                    if quantity == pos.quantity:
                        del self.positions[symbol]
                    else:
                        pos.quantity -= quantity
                    
                    self.trade_count += 1
                    if pnl > 0:
                        self.win_count += 1
                else:
                    return {
                        'status': 'REJECTED',
                        'reason': '持倉不足',
                        'required': quantity,
                        'available': pos.quantity
                    }
        
        # 記錄訂單
        self.order_history.append({
            'order': order,
            'status': 'EXECUTED',
            'execution_time': datetime.now().isoformat()
        })
        
        profit_value = pnl if side.upper() == 'SELL' else None
        self.trade_log.append({
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().isoformat(),
            'profit': profit_value
        })
        
        return {
            'status': 'EXECUTED',
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'cost': cost,
            'available_capital': self.available_capital
        }

    def _check_risk(self, cost: float, side: str) -> bool:
        """檢查風險限制"""
        if side.upper() == 'BUY':
            if cost > self.available_capital * (1 if not self.use_leverage else self.max_leverage):
                return False
            if cost > self.capital * self.max_position_pct:
                return False
        
        if self.daily_pnl < -self.capital * self.max_daily_loss_pct:
            return False
        
        return True

    def update_position_prices(self, price_data: Dict[str, float]):
        """更新持倉價格"""
        for symbol, current_price in price_data.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = current_price

    def get_positions(self) -> List[Dict[str, Any]]:
        """取得所有持倉"""
        positions_list = []
        for symbol, position in self.positions.items():
            positions_list.append({
                'symbol': symbol,
                'quantity': position.quantity,
                'entry_price': position.entry_price,
                'current_price': position.current_price,
                'unrealized_pnl': position.get_unrealized_pnl(),
                'pnl_percentage': position.get_pnl_percentage(),
                'entry_time': position.entry_time
            })
        return positions_list

    def get_performance_metrics(self) -> Dict[str, Any]:
        """取得性能指標"""
        win_rate = (self.win_count / self.trade_count * 100) if self.trade_count > 0 else 0
        
        return {
            'total_capital': self.capital,
            'available_capital': self.available_capital,
            'total_pnl': self.total_pnl,
            'daily_pnl': self.daily_pnl,
            'roi': (self.total_pnl / self.capital * 100) if self.capital > 0 else 0,
            'trade_count': self.trade_count,
            'win_count': self.win_count,
            'win_rate': win_rate,
            'positions_count': len(self.positions),
            'timestamp': datetime.now().isoformat()
        }

    def export_trade_log(self, filepath: str):
        """匯出交易日誌"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'trade_log': self.trade_log,
                'performance': self.get_performance_metrics()
            }, f, ensure_ascii=False, indent=2)
