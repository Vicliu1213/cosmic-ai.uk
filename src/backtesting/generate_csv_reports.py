#!/usr/bin/env python3
"""
Generate CSV Reports from Optimization Results
从优化结果生成 CSV 报告
"""

import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_individual_strategies_csv(
    report_path: str,
    output_path: str
):
    """生成个别策略对比 CSV"""
    logger.info(f"Generating individual strategies CSV from {report_path}")
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    rankings = report.get("individual_strategy_rankings", [])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['排名', '策略名称', '年化收益(%)', 'Sharpe比率', '最大回撤(%)', '风险调整分数']
        )
        writer.writeheader()
        
        for ranking in rankings:
            writer.writerow({
                '排名': ranking['rank'],
                '策略名称': ranking['strategy'],
                '年化收益(%)': f"{ranking['return']:.2f}",
                'Sharpe比率': f"{ranking['sharpe']:.2f}",
                '最大回撤(%)': f"{ranking['max_drawdown']:.2f}",
                '风险调整分数': f"{ranking['score']:.2f}"
            })
    
    logger.info(f"✅ Individual strategies CSV saved to {output_path}")


def generate_portfolio_scenarios_csv(
    report_path: str,
    output_path: str
):
    """生成投资组合场景对比 CSV"""
    logger.info(f"Generating portfolio scenarios CSV from {report_path}")
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    scenarios = report.get("optimization_scenarios", {})
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['场景类型', '投资组合收益(%)', 'Sharpe比率', '最大回撤(%)', '活跃策略数', '风险调整分数']
        )
        writer.writeheader()
        
        for scenario_name, scenario_data in scenarios.items():
            metrics = scenario_data.get("portfolio_metrics", {})
            writer.writerow({
                '场景类型': scenario_name.upper(),
                '投资组合收益(%)': f"{metrics.get('total_return', 0):.2f}",
                'Sharpe比率': f"{metrics.get('sharpe_ratio', 0):.2f}",
                '最大回撤(%)': f"{metrics.get('max_drawdown', 0):.2f}",
                '活跃策略数': scenario_data.get('active_strategies', 0),
                '风险调整分数': f"{metrics.get('risk_adjusted_score', 0):.2f}"
            })
    
    logger.info(f"✅ Portfolio scenarios CSV saved to {output_path}")


def generate_portfolio_weights_csv(
    report_path: str,
    scenario: str,
    output_path: str
):
    """为特定场景生成投资组合权重 CSV"""
    logger.info(f"Generating portfolio weights CSV for scenario: {scenario}")
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    scenarios = report.get("optimization_scenarios", {})
    scenario_data = scenarios.get(scenario)
    
    if not scenario_data:
        logger.error(f"Scenario {scenario} not found")
        return
    
    weights = scenario_data.get("weights", {})
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['策略名称', '配置权重(%)', '配置状态']
        )
        writer.writeheader()
        
        # Sort by weight descending
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        for strategy_name, weight in sorted_weights:
            status = '活跃' if weight > 0.01 else '未配置'
            writer.writerow({
                '策略名称': strategy_name,
                '配置权重(%)': f"{weight * 100:.2f}",
                '配置状态': status
            })
    
    logger.info(f"✅ Portfolio weights CSV saved to {output_path}")


def generate_comprehensive_summary_csv(
    backtest_report_path: str,
    optimization_report_path: str,
    output_path: str
):
    """生成综合总结 CSV"""
    logger.info("Generating comprehensive summary CSV")
    
    with open(backtest_report_path, 'r') as f:
        backtest_report = json.load(f)
    
    with open(optimization_report_path, 'r') as f:
        opt_report = json.load(f)
    
    # Get individual results
    individual_results = backtest_report.get("individual_results", {})
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                '策略',
                '年化收益(%)',
                'Sharpe',
                '最大回撤(%)',
                '交易数',
                '胜率(%)',
                '总P&L',
                '最终资本'
            ]
        )
        writer.writeheader()
        
        for strategy_name, result in individual_results.items():
            writer.writerow({
                '策略': strategy_name,
                '年化收益(%)': f"{result.get('total_return_pct', 0):.2f}",
                'Sharpe': f"{result.get('sharpe_ratio', 0):.2f}",
                '最大回撤(%)': f"{result.get('max_drawdown_pct', 0):.2f}",
                '交易数': result.get('total_trades', 0),
                '胜率(%)': f"{result.get('win_rate', 0) * 100:.2f}",
                '总P&L': f"${result.get('total_pnl', 0):,.2f}",
                '最终资本': f"${result.get('final_capital', 0):,.2f}"
            })
    
    logger.info(f"✅ Comprehensive summary CSV saved to {output_path}")


def main():
    """Main execution"""
    base_path = "/workspaces/cosmic-ai.uk/reports/backtesting"
    Path(base_path).mkdir(parents=True, exist_ok=True)
    
    backtest_report = f"{base_path}/six_strategy_optimization_report.json"
    opt_report = f"{base_path}/advanced_portfolio_optimization_report.json"
    
    # Generate all CSV reports
    logger.info("\n" + "=" * 80)
    logger.info("GENERATING CSV REPORTS")
    logger.info("=" * 80)
    
    # 1. Individual strategies comparison
    generate_individual_strategies_csv(
        opt_report,
        f"{base_path}/01_individual_strategies_ranking.csv"
    )
    
    # 2. Portfolio scenarios comparison
    generate_portfolio_scenarios_csv(
        opt_report,
        f"{base_path}/02_portfolio_scenarios_comparison.csv"
    )
    
    # 3. Portfolio weights for each scenario
    generate_portfolio_weights_csv(
        opt_report,
        "aggressive",
        f"{base_path}/03_aggressive_portfolio_weights.csv"
    )
    
    generate_portfolio_weights_csv(
        opt_report,
        "balanced",
        f"{base_path}/04_balanced_portfolio_weights.csv"
    )
    
    generate_portfolio_weights_csv(
        opt_report,
        "conservative",
        f"{base_path}/05_conservative_portfolio_weights.csv"
    )
    
    # 4. Comprehensive summary
    generate_comprehensive_summary_csv(
        backtest_report,
        opt_report,
        f"{base_path}/06_comprehensive_summary.csv"
    )
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ ALL CSV REPORTS GENERATED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"\nReports location: {base_path}")
    logger.info("""
Generated files:
  1️⃣  01_individual_strategies_ranking.csv - 个别策略排名
  2️⃣  02_portfolio_scenarios_comparison.csv - 投资组合场景对比
  3️⃣  03_aggressive_portfolio_weights.csv - 激进组合权重
  4️⃣  04_balanced_portfolio_weights.csv - 平衡组合权重
  5️⃣  05_conservative_portfolio_weights.csv - 保守组合权重
  6️⃣  06_comprehensive_summary.csv - 综合总结
    """)


if __name__ == "__main__":
    main()
