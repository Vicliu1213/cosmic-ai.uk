#!/usr/bin/env python3
"""
回測報告生成器 (Backtest Report Generator)
回测报告生成 - CSV 格式，可調整必看項目
"""

import os
import csv
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class BacktestResult:
    """回測結果數據"""
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    best_trade: float
    worst_trade: float


class BacktestReportGenerator:
    """回測報告生成器"""
    
    def __init__(self, output_dir: str = "reports/backtest"):
        """初始化生成器
        
        Args:
            output_dir: 報告輸出目錄
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
        
        # 預設必看項目
        self.default_columns = [
            'strategy_name',      # 策略名稱
            'symbol',             # 交易對
            'total_return',       # 總回報
            'annual_return',      # 年化回報
            'sharpe_ratio',       # 夏普比率
            'max_drawdown',       # 最大回撤
            'win_rate',           # 勝率
            'total_trades',       # 總交易數
            'profit_factor'       # 利潤因子
        ]
    
    def _ensure_output_dir(self) -> None:
        """確保輸出目錄存在"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        results: List[BacktestResult],
        columns: Optional[List[str]] = None,
        filename: Optional[str] = None
    ) -> str:
        """生成回測報告
        
        Args:
            results: 回測結果列表
            columns: 自訂列（預設使用必看項目）
            filename: 自訂檔案名稱
            
        Returns:
            報告檔案路徑
        """
        if columns is None:
            columns = self.default_columns
        
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_report_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for result in results:
                    row = {col: getattr(result, col, 'N/A') for col in columns}
                    writer.writerow(row)
            
            return filepath
        except Exception as e:
            raise Exception(f"Error generating report: {e}")
    
    def add_summary(
        self,
        results: List[BacktestResult],
        filepath: str
    ) -> None:
        """添加報告摘要
        
        Args:
            results: 回測結果列表
            filepath: 報告檔案路徑
        """
        summary = self._calculate_summary(results)
        
        # 添加摘要到檔案開頭
        summary_lines = [
            f"回測報告摘要 - {datetime.now(timezone.utc).isoformat()}",
            f"策略數量: {summary['strategy_count']}",
            f"平均回報: {summary['avg_return']:.2f}%",
            f"平均夏普比率: {summary['avg_sharpe']:.2f}",
            f"平均最大回撤: {summary['avg_drawdown']:.2f}%",
            f"平均勝率: {summary['avg_win_rate']:.2f}%",
            ""
        ]
        
        # 讀取現有內容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 寫入摘要 + 原內容
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in summary_lines:
                f.write(line + "\n")
            f.write(content)
    
    def _calculate_summary(self, results: List[BacktestResult]) -> Dict[str, Any]:
        """計算摘要統計"""
        if not results:
            return {
                'strategy_count': 0,
                'avg_return': 0,
                'avg_sharpe': 0,
                'avg_drawdown': 0,
                'avg_win_rate': 0
            }
        
        return {
            'strategy_count': len(results),
            'avg_return': sum(r.total_return for r in results) / len(results),
            'avg_sharpe': sum(r.sharpe_ratio for r in results) / len(results),
            'avg_drawdown': sum(r.max_drawdown for r in results) / len(results),
            'avg_win_rate': sum(r.win_rate for r in results) / len(results)
        }
    
    def compare_strategies(
        self,
        results: List[BacktestResult],
        filename: Optional[str] = None
    ) -> str:
        """生成策略對比報告
        
        Args:
            results: 回測結果列表
            filename: 自訂檔案名稱
            
        Returns:
            報告檔案路徑
        """
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_comparison_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 按策略分組排序
        sorted_results = sorted(
            results,
            key=lambda x: (x.strategy_name, x.total_return),
            reverse=True
        )
        
        return self.generate_report(sorted_results, filename=filename)
    
    def export_json(
        self,
        results: List[BacktestResult],
        filename: Optional[str] = None
    ) -> str:
        """匯出 JSON 格式報告
        
        Args:
            results: 回測結果列表
            filename: 自訂檔案名稱
            
        Returns:
            報告檔案路徑
        """
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'results': [asdict(r) for r in results],
            'summary': self._calculate_summary(results)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath


# 快速使用函數
def create_backtest_report(
    results: List[BacktestResult],
    columns: Optional[List[str]] = None
) -> str:
    """快速創建回測報告"""
    generator = BacktestReportGenerator()
    return generator.generate_report(results, columns=columns)


if __name__ == "__main__":
    # 測試數據
    test_results = [
        BacktestResult(
            strategy_name="MA_Crossover",
            symbol="BTC/USDT",
            start_date="2023-01-01",
            end_date="2024-01-01",
            total_return=45.5,
            annual_return=45.5,
            sharpe_ratio=1.85,
            max_drawdown=-12.3,
            win_rate=0.62,
            total_trades=156,
            winning_trades=97,
            losing_trades=59,
            avg_win=2.1,
            avg_loss=-1.8,
            profit_factor=3.2,
            best_trade=8.5,
            worst_trade=-6.2
        ),
        BacktestResult(
            strategy_name="RSI_Divergence",
            symbol="ETH/USDT",
            start_date="2023-01-01",
            end_date="2024-01-01",
            total_return=32.1,
            annual_return=32.1,
            sharpe_ratio=1.45,
            max_drawdown=-18.5,
            win_rate=0.55,
            total_trades=203,
            winning_trades=112,
            losing_trades=91,
            avg_win=1.8,
            avg_loss=-1.9,
            profit_factor=2.1,
            best_trade=7.3,
            worst_trade=-7.8
        )
    ]
    
    generator = BacktestReportGenerator()
    filepath = generator.generate_report(test_results)
    print(f"✅ 回測報告已生成: {filepath}")
    
    generator.add_summary(test_results, filepath)
    print(f"✅ 摘要已添加")
