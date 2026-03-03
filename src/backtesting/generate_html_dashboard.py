#!/usr/bin/env python3
"""
Interactive HTML Dashboard Generator
交互式HTML仪表板生成器 - 6策略优化结果展示
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_dashboard_html(
    opt_report_path: str,
    viz_data_path: str,
    output_path: str
):
    """Generate interactive HTML dashboard"""
    
    logger.info("Loading data files...")
    
    with open(opt_report_path, 'r') as f:
        opt_report = json.load(f)
    
    with open(viz_data_path, 'r') as f:
        viz_data = json.load(f)
    
    # Prepare data for JavaScript
    strategies = viz_data['strategies']
    scenarios = opt_report['optimization_scenarios']
    best_scenario = opt_report['best_scenario']
    recommendation = opt_report['recommendation']
    
    # Create HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>6策略投资组合优化仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.1.0/dist/chartjs-plugin-datalabels.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
        }}
        
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        
        .recommendation-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .recommendation-box h3 {{
            margin-bottom: 10px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }}
        
        .card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #666;
            font-weight: 500;
        }}
        
        .metric-value {{
            color: #333;
            font-weight: bold;
            color: #667eea;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .scenarios-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .scenarios-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .scenarios-table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .scenarios-table tr:hover {{
            background: #f5f5f5;
        }}
        
        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }}
        
        .badge-aggressive {{
            background: #ff6b6b;
            color: white;
        }}
        
        .badge-balanced {{
            background: #4ecdc4;
            color: white;
        }}
        
        .badge-conservative {{
            background: #95e1d3;
            color: #333;
        }}
        
        .highlight {{
            background: #fff3cd;
            padding: 2px 6px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 6策略投资组合优化仪表板</h1>
        <p class="subtitle">增强量子经典混合算法 - 基于CSV市场数据的综合优化</p>
        
        <div class="recommendation-box">
            <h3>💡 优化建议</h3>
            <p>{recommendation}</p>
        </div>
        
        <h2 style="color: #667eea; margin: 30px 0 20px 0;">📊 个别策略排名</h2>
        <div class="chart-container">
            <canvas id="strategiesChart"></canvas>
        </div>
        
        <h2 style="color: #667eea; margin: 30px 0 20px 0;">💼 投资组合场景对比</h2>
        <div class="row">
            <div class="chart-container">
                <canvas id="scenariosReturnChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="scenariosSharpeChart"></canvas>
            </div>
        </div>
        
        <h2 style="color: #667eea; margin: 30px 0 20px 0;">📈 场景详细指标</h2>
        <table class="scenarios-table">
            <thead>
                <tr>
                    <th>场景类型</th>
                    <th>预期收益</th>
                    <th>Sharpe比率</th>
                    <th>最大回撤</th>
                    <th>活跃策略数</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add scenario rows
    for scenario_name, scenario_data in scenarios.items():
        metrics = scenario_data['portfolio_metrics']
        badge_class = f"badge-{scenario_name}"
        html_content += f"""
                <tr>
                    <td><span class="badge {badge_class}">{scenario_name.upper()}</span></td>
                    <td><strong>{metrics['total_return']:.2f}%</strong></td>
                    <td>{metrics['sharpe_ratio']:.2f}</td>
                    <td>{metrics['max_drawdown']:.2f}%</td>
                    <td>{scenario_data['active_strategies']}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>
        
        <h2 style="color: #667eea; margin: 30px 0 20px 0;">🎯 推荐配置 ("""
    
    html_content += f"{best_scenario.upper()})"
    
    html_content += """</h2>
        <div class="chart-container">
            <canvas id="recommendedWeightsChart"></canvas>
        </div>
        
        <h2 style="color: #667eea; margin: 30px 0 20px 0;">📋 所有场景权重分配</h2>
        <div class="grid">
"""
    
    # Add weight allocation cards for each scenario
    for scenario_name, scenario_data in scenarios.items():
        weights = scenario_data['weights']
        badge_class = f"badge-{scenario_name}"
        
        html_content += f"""
            <div class="card">
                <h3><span class="badge {badge_class}">{scenario_name.upper()}</span> 权重分配</h3>
"""
        
        # Sort weights by value
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        
        for strategy, weight in sorted_weights:
            if weight > 0.01:
                html_content += f"""
                <div class="metric">
                    <span class="metric-label">{strategy}</span>
                    <span class="metric-value">{weight*100:.1f}%</span>
                </div>
"""
        
        html_content += """
            </div>
"""
    
    html_content += """
        </div>
        
        <div class="footer">
            <p>📅 报告生成时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>🔬 使用scipy.optimize.differential_evolution和SLSQP优化算法</p>
            <p>✅ 基于6个主要交易策略的综合分析</p>
        </div>
    </div>
    
    <script>
        // Chart.js configuration
        Chart.register(ChartDataLabels);
        
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                datalabels: {
                    display: true,
                    color: '#fff',
                    anchor: 'center',
                    align: 'center',
                    font: {
                        weight: 'bold',
                        size: 11
                    }
                }
            }
        };
        
        // 1. Individual Strategies Performance Chart
        const strategiesData = """ + json.dumps(strategies) + """;
        const strategiesCtx = document.getElementById('strategiesChart').getContext('2d');
        new Chart(strategiesCtx, {
            type: 'bar',
            data: {
                labels: strategiesData.map(s => s.name),
                datasets: [
                    {
                        label: '年化收益 (%)',
                        data: strategiesData.map(s => s.return),
                        backgroundColor: '#667eea'
                    },
                    {
                        label: 'Sharpe比率',
                        data: strategiesData.map(s => s.sharpe * 30),
                        backgroundColor: '#764ba2'
                    }
                ]
            },
            options: {
                ...chartOptions,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // 2. Scenarios Return Comparison
        const scenarios = """ + json.dumps(dict(scenarios)) + """;
        const scenarioNames = Object.keys(scenarios);
        const scenarioReturns = scenarioNames.map(s => scenarios[s].portfolio_metrics.total_return);
        
        const returnCtx = document.getElementById('scenariosReturnChart').getContext('2d');
        new Chart(returnCtx, {
            type: 'doughnut',
            data: {
                labels: scenarioNames.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
                datasets: [{
                    data: scenarioReturns,
                    backgroundColor: ['#ff6b6b', '#4ecdc4', '#95e1d3']
                }]
            },
            options: chartOptions
        });
        
        // 3. Scenarios Sharpe Ratio Comparison
        const scenarioSharpes = scenarioNames.map(s => scenarios[s].portfolio_metrics.sharpe_ratio);
        
        const sharpeCtx = document.getElementById('scenariosSharpeChart').getContext('2d');
        new Chart(sharpeCtx, {
            type: 'radar',
            data: {
                labels: scenarioNames.map(s => s.toUpperCase()),
                datasets: [{
                    label: 'Sharpe比率',
                    data: scenarioSharpes,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                ...chartOptions,
                scales: {
                    r: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // 4. Recommended Portfolio Weights
        const bestScenarioData = scenarios['""" + best_scenario + """'];
        const weights = bestScenarioData.weights;
        
        const weightsCtx = document.getElementById('recommendedWeightsChart').getContext('2d');
        new Chart(weightsCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(weights),
                datasets: [{
                    data: Object.values(weights).map(w => w * 100),
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#4facfe',
                        '#43e97b', '#fa709a', '#fee140', '#30cfd0'
                    ]
                }]
            },
            options: {
                ...chartOptions,
                plugins: {
                    ...chartOptions.plugins,
                    datalabels: {
                        display: true,
                        color: '#fff',
                        font: {
                            weight: 'bold',
                            size: 10
                        },
                        formatter: (value) => {
                            return value > 2 ? value.toFixed(1) + '%' : '';
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
    
    # Write HTML file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"✅ Dashboard HTML saved to {output_path}")


def main():
    """Main execution"""
    base_path = "/workspaces/cosmic-ai.uk/reports/backtesting"
    
    logger.info("\n" + "=" * 80)
    logger.info("GENERATING INTERACTIVE HTML DASHBOARD")
    logger.info("=" * 80)
    
    opt_report_path = f"{base_path}/advanced_portfolio_optimization_report.json"
    viz_data_path = f"{base_path}/portfolio_visualization_data.json"
    output_path = f"{base_path}/dashboard.html"
    
    generate_dashboard_html(opt_report_path, viz_data_path, output_path)
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ INTERACTIVE DASHBOARD CREATED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"\n📊 Dashboard: {output_path}")
    logger.info("\nTo view the dashboard:")
    logger.info(f"  Open in browser: file://{output_path}")


if __name__ == "__main__":
    main()
