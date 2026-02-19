#!/usr/bin/env python3
"""
日常即時報告生成器 (Daily Report Generator)
日常实时报告生成 - CSV 格式，每日更新必看項目
"""

import os
import csv
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class DailyTradingStats:
    """日常交易統計"""
    date: str
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    trades_count: int
    wins: int
    losses: int
    win_rate: float
    daily_return: float
    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float


class DailyReportGenerator:
    """日常即時報告生成器"""
    
    def __init__(self, output_dir: str = "reports/daily"):
        """初始化生成器
        
        Args:
            output_dir: 報告輸出目錄
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
        
        # 預設必看項目（精簡版）
        self.default_columns = [
            'date',              # 日期
            'symbol',            # 交易對
            'close_price',       # 收盤價
            'daily_return',      # 日回報
            'trades_count',      # 交易數
            'win_rate',          # 勝率
            'realized_pnl',      # 已實現損益
            'total_pnl'          # 總損益
        ]
        
        # 擴展列（詳細版）
        self.extended_columns = [
            'date',
            'symbol',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
            'trades_count',
            'wins',
            'losses',
            'win_rate',
            'daily_return',
            'realized_pnl',
            'unrealized_pnl',
            'total_pnl'
        ]
    
    def _ensure_output_dir(self) -> None:
        """確保輸出目錄存在"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(
        self,
        stats: List[DailyTradingStats],
        columns: Optional[List[str]] = None,
        filename: Optional[str] = None
    ) -> str:
        """生成日常報告
        
        Args:
            stats: 日常統計列表
            columns: 自訂列（預設使用必看項目）
            filename: 自訂檔案名稱
            
        Returns:
            報告檔案路徑
        """
        if columns is None:
            columns = self.default_columns
        
        if filename is None:
            today = datetime.now(timezone.utc).strftime("%Y%m%d")
            filename = f"daily_report_{today}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for stat in stats:
                    row = {col: getattr(stat, col, 'N/A') for col in columns}
                    writer.writerow(row)
            
            return filepath
        except Exception as e:
            raise Exception(f"Error generating report: {e}")
    
    def generate_extended_report(
        self,
        stats: List[DailyTradingStats],
        filename: Optional[str] = None
    ) -> str:
        """生成擴展詳細報告
        
        Args:
            stats: 日常統計列表
            filename: 自訂檔案名稱
            
        Returns:
            報告檔案路徑
        """
        return self.generate_daily_report(stats, columns=self.extended_columns, filename=filename)
    
    def append_daily_stats(
        self,
        stats: DailyTradingStats,
        daily_file: Optional[str] = None
    ) -> str:
        """追加日常統計到檔案
        
        Args:
            stats: 新的統計數據
            daily_file: 檔案名稱
            
        Returns:
            報告檔案路徑
        """
        if daily_file is None:
            daily_file = "daily_tracking.csv"
        
        filepath = os.path.join(self.output_dir, daily_file)
        file_exists = os.path.exists(filepath)
        
        try:
            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.default_columns)
                
                if not file_exists:
                    writer.writeheader()
                
                row = {col: getattr(stats, col, 'N/A') for col in self.default_columns}
                writer.writerow(row)
            
            return filepath
        except Exception as e:
            raise Exception(f"Error appending stats: {e}")
    
    def get_daily_summary(
        self,
        stats: List[DailyTradingStats]
    ) -> Dict[str, Any]:
        """獲取日常摘要
        
        Args:
            stats: 日常統計列表
            
        Returns:
            摘要統計
        """
        if not stats:
            return {}
        
        total_pnl = sum(s.total_pnl for s in stats)
        total_trades = sum(s.trades_count for s in stats)
        total_wins = sum(s.wins for s in stats)
        avg_win_rate = sum(s.win_rate for s in stats) / len(stats) if stats else 0
        
        return {
            'date': datetime.now(timezone.utc).isoformat(),
            'total_symbols': len(set(s.symbol for s in stats)),
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'total_wins': total_wins,
            'avg_win_rate': avg_win_rate,
            'best_return': max((s.daily_return for s in stats), default=0),
            'worst_return': min((s.daily_return for s in stats), default=0),
            'records_count': len(stats)
        }
    
    def export_json(
        self,
        stats: List[DailyTradingStats],
        filename: Optional[str] = None
    ) -> str:
        """匯出 JSON 格式報告
        
        Args:
            stats: 日常統計列表
            filename: 自訂檔案名稱
            
        Returns:
            報告檔案路徑
        """
        if filename is None:
            today = datetime.now(timezone.utc).strftime("%Y%m%d")
            filename = f"daily_report_{today}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'stats': [asdict(s) for s in stats],
            'summary': self.get_daily_summary(stats)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def generate_portfolio_report(
        self,
        stats: List[DailyTradingStats]
    ) -> str:
        """生成投資組合報告
        
        Args:
            stats: 日常統計列表
            
        Returns:
            報告檔案路徑
        """
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"portfolio_report_{today}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # 按交易對分組
        by_symbol = {}
        for stat in stats:
            if stat.symbol not in by_symbol:
                by_symbol[stat.symbol] = []
            by_symbol[stat.symbol].append(stat)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['symbol', 'total_pnl', 'avg_daily_return', 'total_trades', 'win_rate']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for symbol, stat_list in by_symbol.items():
                    total_pnl = sum(s.total_pnl for s in stat_list)
                    avg_return = sum(s.daily_return for s in stat_list) / len(stat_list)
                    total_trades = sum(s.trades_count for s in stat_list)
                    avg_win_rate = sum(s.win_rate for s in stat_list) / len(stat_list)
                    
                    writer.writerow({
                        'symbol': symbol,
                        'total_pnl': f"{total_pnl:.2f}",
                        'avg_daily_return': f"{avg_return:.2f}%",
                        'total_trades': total_trades,
                        'win_rate': f"{avg_win_rate:.2f}%"
                    })
            
            return filepath
        except Exception as e:
            raise Exception(f"Error generating portfolio report: {e}")


# 快速使用函數
def create_daily_report(
    stats: List[DailyTradingStats],
    columns: Optional[List[str]] = None
) -> str:
    """快速創建日常報告"""
    generator = DailyReportGenerator()
    return generator.generate_daily_report(stats, columns=columns)


def append_daily_stats(stats: DailyTradingStats) -> str:
    """快速追加日常統計"""
    generator = DailyReportGenerator()
    return generator.append_daily_stats(stats)


if __name__ == "__main__":
    # 測試數據
    test_stats = [
        DailyTradingStats(
            date="2024-02-19",
            symbol="BTC/USDT",
            open_price=52000,
            high_price=53500,
            low_price=51800,
            close_price=53200,
            volume=1500.5,
            trades_count=12,
            wins=8,
            losses=4,
            win_rate=0.67,
            daily_return=2.31,
            realized_pnl=1250.50,
            unrealized_pnl=350.75,
            total_pnl=1601.25
        ),
        DailyTradingStats(
            date="2024-02-19",
            symbol="ETH/USDT",
            open_price=2900,
            high_price=3050,
            low_price=2850,
            close_price=3020,
            volume=850.3,
            trades_count=8,
            wins=5,
            losses=3,
            win_rate=0.63,
            daily_return=4.14,
            realized_pnl=750.25,
            unrealized_pnl=120.50,
            total_pnl=870.75
        )
    ]
    
    generator = DailyReportGenerator()
    
    # 生成簡潔報告
    filepath = generator.generate_daily_report(test_stats)
    print(f"✅ 日常報告已生成: {filepath}")
    
    # 生成摘要
    summary = generator.get_daily_summary(test_stats)
    print(f"✅ 摘要: {json.dumps(summary, ensure_ascii=False, indent=2)}")
    
    # 生成投資組合報告
    portfolio_file = generator.generate_portfolio_report(test_stats)
    print(f"✅ 投資組合報告已生成: {portfolio_file}")
