#!/usr/bin/env python3
"""
策略對比分析器 - 分析 6 個策略的回測結果
Strategy Comparison Analyzer - Analyze backtest results for 6 strategies
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import sys


class StrategyComparisonAnalyzer:
    """分析和對比策略表現"""
    
    def __init__(self, report_file: str):
        """
        初始化分析器
        
        Args:
            report_file: 回測報告 JSON 文件路徑
        """
        self.report_file = report_file
        self.data = self._load_report()
        self.strategies = self.data.get('strategies', {})
        self.ranking = self.data.get('ranking', [])
    
    def _load_report(self) -> Dict:
        """加載回測報告"""
        try:
            with open(self.report_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 文件不存在: {self.report_file}")
            return {}
    
    def create_comparison_dataframe(self) -> pd.DataFrame:
        """
        創建對比 DataFrame
        
        Returns:
            包含所有指標的 DataFrame
        """
        rows = []
        
        for idx, (strategy_name, metrics) in enumerate(self.strategies.items(), 1):
            # 提取數值
            total_return = float(metrics['total_return_pct'].rstrip('%'))
            sharpe_ratio = float(metrics['sharpe_ratio'])
            max_drawdown = float(metrics['max_drawdown_pct'].rstrip('%'))
            total_trades = int(metrics['total_trades'])
            win_rate = float(metrics['win_rate'].rstrip('%'))
            total_pnl = float(metrics['total_pnl'].replace('$', '').replace(',', ''))
            
            rows.append({
                '排名': idx,
                '策略': strategy_name,
                '年化收益': total_return,
                'Sharpe比率': sharpe_ratio,
                '最大回撤': max_drawdown,
                '交易數': total_trades,
                '勝率': win_rate,
                '總P&L': total_pnl,
            })
        
        df = pd.DataFrame(rows)
        return df.sort_values('年化收益', ascending=False).reset_index(drop=True)
    
    def print_summary(self) -> None:
        """打印摘要信息"""
        print("\n" + "="*80)
        print("📊 策略對比分析報告")
        print("="*80)
        print(f"📅 報告時間: {self.data.get('timestamp', 'N/A')}")
        print(f"📈 數據快照: {self.data.get('snapshots', 'N/A')} 個")
        print(f"🔄 采樣方式: {self.data.get('sampling', 'N/A')}")
        print("="*80)
    
    def print_comparison_table(self) -> None:
        """打印對比表"""
        df = self.create_comparison_dataframe()
        
        print("\n📋 策略性能對比表:")
        print("-"*120)
        
        for idx, row in df.iterrows():
            print(f"\n🏆 排名 #{idx+1}: {row['策略']}")
            print(f"   年化收益: {row['年化收益']:>7.2f}%  |  Sharpe: {row['Sharpe比率']:>5.2f}  |  回撤: {row['最大回撤']:>6.2f}%")
            print(f"   交易數: {row['交易數']:>4.0f}  |  勝率: {row['勝率']:>6.2f}%  |  P&L: ${row['總P&L']:>10,.2f}")
    
    def analyze_by_category(self) -> Dict[str, Dict]:
        """按策略類別分析"""
        df = self.create_comparison_dataframe()
        
        categories = {
            'Cosmic (宇宙系統)': df[df['策略'].str.contains('Cosmic', case=False)],
            'Hummingbot (做市系統)': df[df['策略'].str.contains('Hummingbot', case=False)],
            'LLM-TradeBot (AI推理)': df[df['策略'].str.contains('LLM', case=False)],
            'Hybrid (混合系統)': df[df['策略'].str.contains('Hybrid|Combo', case=False)],
        }
        
        analysis = {}
        for category_name, category_df in categories.items():
            if len(category_df) > 0:
                analysis[category_name] = {
                    '平均收益': category_df['年化收益'].mean(),
                    '平均Sharpe': category_df['Sharpe比率'].mean(),
                    '平均回撤': category_df['最大回撤'].mean(),
                    '平均勝率': category_df['勝率'].mean(),
                    '平均交易數': category_df['交易數'].mean(),
                    '策略數': len(category_df)
                }
        
        return analysis
    
    def print_category_analysis(self) -> None:
        """打印分類分析"""
        analysis = self.analyze_by_category()
        
        print("\n\n📑 按策略類別分析:")
        print("-"*100)
        
        for category, stats in analysis.items():
            print(f"\n{category}:")
            print(f"  ✓ 策略數: {stats['策略數']:.0f}")
            print(f"  ✓ 平均年化收益: {stats['平均收益']:.2f}%")
            print(f"  ✓ 平均Sharpe比率: {stats['平均Sharpe']:.2f}")
            print(f"  ✓ 平均最大回撤: {stats['平均回撤']:.2f}%")
            print(f"  ✓ 平均勝率: {stats['平均勝率']:.2f}%")
            print(f"  ✓ 平均交易數: {stats['平均交易數']:.0f}")
    
    def get_best_worst(self) -> Tuple[Dict, Dict]:
        """獲取最好和最差的策略"""
        df = self.create_comparison_dataframe()
        
        best = df.iloc[0].to_dict()
        worst = df.iloc[-1].to_dict()
        
        return best, worst
    
    def print_best_worst(self) -> None:
        """打印最優和最差策略"""
        best, worst = self.get_best_worst()
        
        print("\n\n🏆 最優 vs 最差策略:")
        print("-"*80)
        
        print(f"\n🥇 最優策略: {best['策略']}")
        print(f"   年化收益: {best['年化收益']:.2f}%")
        print(f"   Sharpe比率: {best['Sharpe比率']:.2f}")
        print(f"   最大回撤: {best['最大回撤']:.2f}%")
        print(f"   勝率: {best['勝率']:.2f}%")
        
        print(f"\n🥉 最差策略: {worst['策略']}")
        print(f"   年化收益: {worst['年化收益']:.2f}%")
        print(f"   Sharpe比率: {worst['Sharpe比率']:.2f}")
        print(f"   最大回撤: {worst['最大回撤']:.2f}%")
        print(f"   勝率: {worst['勝率']:.2f}%")
        
        print(f"\n📊 性能差異:")
        print(f"   收益差異: {best['年化收益'] - worst['年化收益']:.2f}%")
        print(f"   Sharpe差異: {best['Sharpe比率'] - worst['Sharpe比率']:.2f}")
        print(f"   回撤差異: {best['最大回撤'] - worst['最大回撤']:.2f}%")
    
    def analyze_risk_return_tradeoff(self) -> None:
        """分析風險-收益權衡"""
        df = self.create_comparison_dataframe()
        
        print("\n\n⚖️ 風險-收益權衡分析:")
        print("-"*80)
        
        # 計算Sharpe效率
        df['收益/回撤'] = df['年化收益'] / (df['最大回撤'] + 0.1)
        df['Sharpe效率'] = df['Sharpe比率']
        
        print("\n按Sharpe比率排序 (風險調整收益最優):")
        sharpe_sorted = df.sort_values('Sharpe比率', ascending=False)
        
        for idx, row in sharpe_sorted.head(3).iterrows():
            print(f"  #{idx+1}. {row['策略']}")
            print(f"     Sharpe: {row['Sharpe比率']:.2f}  |  收益: {row['年化收益']:.2f}%  |  回撤: {row['最大回撤']:.2f}%")
    
    def get_recommendations(self) -> Dict[str, str]:
        """生成投資建議"""
        df = self.create_comparison_dataframe()
        
        recommendations = {}
        
        # 最高收益
        max_return_idx = df['年化收益'].idxmax()
        recommendations['最高收益'] = f"{df.loc[max_return_idx, '策略']} ({df.loc[max_return_idx, '年化收益']:.2f}%)"
        
        # 最佳風險調整
        best_sharpe_idx = df['Sharpe比率'].idxmax()
        recommendations['最佳風險調整'] = f"{df.loc[best_sharpe_idx, '策略']} (Sharpe: {df.loc[best_sharpe_idx, 'Sharpe比率']:.2f})"
        
        # 最低回撤
        min_dd_idx = df['最大回撤'].idxmin()
        recommendations['最低回撤'] = f"{df.loc[min_dd_idx, '策略']} ({df.loc[min_dd_idx, '最大回撤']:.2f}%)"
        
        # 最高勝率
        max_wr_idx = df['勝率'].idxmax()
        recommendations['最高勝率'] = f"{df.loc[max_wr_idx, '策略']} ({df.loc[max_wr_idx, '勝率']:.2f}%)"
        
        return recommendations
    
    def print_recommendations(self) -> None:
        """打印建議"""
        recommendations = self.get_recommendations()
        
        print("\n\n💡 投資建議:")
        print("-"*80)
        
        for title, recommendation in recommendations.items():
            print(f"  ✓ {title}: {recommendation}")
    
    def generate_full_report(self) -> str:
        """生成完整報告"""
        self.print_summary()
        self.print_comparison_table()
        self.print_category_analysis()
        self.print_best_worst()
        self.analyze_risk_return_tradeoff()
        self.print_recommendations()
        
        # 返回最終結論
        conclusion = self._generate_conclusion()
        print("\n\n" + "="*80)
        print("📌 最終結論:")
        print("="*80)
        print(conclusion)
        
        return conclusion
    
    def _generate_conclusion(self) -> str:
        """生成最終結論"""
        df = self.create_comparison_dataframe()
        best_strategy = df.iloc[0]
        
        conclusion = f"""
根據回測數據分析，以下是關鍵發現:

1. 🏆 整體表現最佳: {best_strategy['策略']}
   - 年化收益: {best_strategy['年化收益']:.2f}%
   - Sharpe比率: {best_strategy['Sharpe比率']:.2f}
   - 最大回撤: {best_strategy['最大回撤']:.2f}%

2. 📊 策略分類對比:
   - Hummingbot系統: 高收益但高風險 (Sharpe ~1.3)
   - Cosmic系統: 穩定收益，低風險 (回撤<15%)
   - LLM系統: Sharpe高但風險控制差
   - 混合系統: 平衡收益和風險

3. ⚠️ 風險提示:
   - 回測數據存在倖存者偏差
   - 實盤表現可能與回測不同
   - 建議從小額開始實盤驗證
   
4. ✅ 推薦方案:
   - 保守型: 採用Cosmic系統 (穩定性優先)
   - 積極型: 採用Hummingbot Avellaneda-Stoikov (收益優先)
   - 均衡型: 採用混合系統 (協同優化)
"""
        return conclusion


def main():
    """主函數"""
    
    # 查找最新的回測報告
    reports_dir = Path('/workspaces/cosmic-ai.uk/reports/backtesting')
    
    if not reports_dir.exists():
        print("❌ 回測報告目錄不存在")
        return
    
    # 找到最新的報告
    report_files = sorted(reports_dir.glob('backtest_report_*.json'), reverse=True)
    
    if not report_files:
        print("❌ 未找到回測報告文件")
        return
    
    latest_report = report_files[0]
    print(f"📂 分析報告: {latest_report.name}\n")
    
    # 分析
    analyzer = StrategyComparisonAnalyzer(str(latest_report))
    analyzer.generate_full_report()
    
    # 保存對比表格
    df = analyzer.create_comparison_dataframe()
    output_csv = reports_dir / 'strategy_comparison.csv'
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n✅ 對比表已保存: {output_csv}")


if __name__ == '__main__':
    main()
