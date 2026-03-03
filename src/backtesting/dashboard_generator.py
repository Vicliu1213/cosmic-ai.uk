#!/usr/bin/env python3
"""
策略對比可視化儀表板
Strategy Comparison Visualization Dashboard
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


def generate_html_dashboard(report_file: str, output_file: str = None) -> str:
    """
    生成 HTML 可視化儀表板
    """
    
    # 加載數據
    with open(report_file, 'r') as f:
        data = json.load(f)
    
    strategies = data.get('strategies', {})
    ranking = data.get('ranking', [])
    
    # 準備數據
    df = pd.DataFrame([
        {
            'name': name,
            'return': float(metrics['total_return_pct'].rstrip('%')),
            'sharpe': float(metrics['sharpe_ratio']),
            'drawdown': float(metrics['max_drawdown_pct'].rstrip('%')),
            'trades': int(metrics['total_trades']),
            'win_rate': float(metrics['win_rate'].rstrip('%')),
            'pnl': float(metrics['total_pnl'].replace('$', '').replace(',', ''))
        }
        for name, metrics in strategies.items()
    ])
    
    # 按收益排序
    df = df.sort_values('return', ascending=False).reset_index(drop=True)
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>策略對比分析儀表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .card h2 {{
            font-size: 16px;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 14px;
        }}
        
        .metric-value {{
            font-weight: bold;
            font-size: 16px;
            color: #333;
        }}
        
        .positive {{
            color: #27ae60;
        }}
        
        .negative {{
            color: #e74c3c;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-bottom: 20px;
        }}
        
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .table thead {{
            background: #667eea;
            color: white;
        }}
        
        .table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        .table tbody tr:hover {{
            background: #f5f5f5;
        }}
        
        .table tbody tr:nth-child(1) {{
            background: #fffbea;
            border-left: 4px solid #ffc107;
        }}
        
        .table tbody tr:nth-child(2) {{
            background: #f0f0f0;
            border-left: 4px solid #c0c0c0;
        }}
        
        .table tbody tr:nth-child(3) {{
            background: #ffe4e1;
            border-left: 4px solid #cd7f32;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge-cosmic {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .badge-hummingbot {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        
        .badge-llm {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        
        .badge-hybrid {{
            background: #fce4ec;
            color: #c2185b;
        }}
        
        .footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        
        .rank-medal {{
            font-size: 20px;
            font-weight: bold;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 策略對比分析儀表板</h1>
            <p>報告時間: {data.get('timestamp', 'N/A')} | 數據快照: {data.get('snapshots', 'N/A')} | 采樣: {data.get('sampling', 'N/A')}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>🏆 最優策略</h2>
                <div class="metric">
                    <span class="metric-label">策略名稱</span>
                    <span class="metric-value">{df.iloc[0]['name']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">年化收益</span>
                    <span class="metric-value positive">{df.iloc[0]['return']:.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Sharpe比率</span>
                    <span class="metric-value">{df.iloc[0]['sharpe']:.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">最大回撤</span>
                    <span class="metric-value negative">{df.iloc[0]['drawdown']:.2f}%</span>
                </div>
            </div>
            
            <div class="card">
                <h2>⚙️ 系統平均值</h2>
                <div class="metric">
                    <span class="metric-label">平均年化收益</span>
                    <span class="metric-value positive">{df['return'].mean():.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">平均Sharpe</span>
                    <span class="metric-value">{df['sharpe'].mean():.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">平均回撤</span>
                    <span class="metric-value negative">{df['drawdown'].mean():.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">平均勝率</span>
                    <span class="metric-value">{df['win_rate'].mean():.2f}%</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 極值分析</h2>
                <div class="metric">
                    <span class="metric-label">最高收益</span>
                    <span class="metric-value positive">{df['return'].max():.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">最低收益</span>
                    <span class="metric-value negative">{df['return'].min():.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">最小回撤</span>
                    <span class="metric-value positive">{df['drawdown'].min():.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">最大回撤</span>
                    <span class="metric-value negative">{df['drawdown'].max():.2f}%</span>
                </div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px;">
            <div class="card">
                <h2>📊 收益分布</h2>
                <div class="chart-container">
                    <canvas id="returnChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>⚖️ 風險-收益權衡</h2>
                <div class="chart-container">
                    <canvas id="riskReturnChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-bottom: 20px;">
            <h2>📋 詳細對比表</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>策略名稱</th>
                        <th>年化收益</th>
                        <th>Sharpe比率</th>
                        <th>最大回撤</th>
                        <th>交易數</th>
                        <th>勝率</th>
                        <th>總P&L</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    for idx, row in df.iterrows():
        medal = '🥇' if idx == 0 else ('🥈' if idx == 1 else ('🥉' if idx == 2 else f'#{idx+1}'))
        
        # 判斷策略類別
        if 'Cosmic' in row['name']:
            badge = 'badge-cosmic'
            badge_text = 'Cosmic'
        elif 'Hummingbot' in row['name']:
            badge = 'badge-hummingbot'
            badge_text = 'Hummingbot'
        elif 'LLM' in row['name']:
            badge = 'badge-llm'
            badge_text = 'LLM'
        else:
            badge = 'badge-hybrid'
            badge_text = 'Hybrid'
        
        html += f"""
                    <tr>
                        <td><span class="rank-medal">{medal}</span></td>
                        <td><span class="badge {badge}">{badge_text}</span><br>{row['name']}</td>
                        <td><span class="{'positive' if row['return'] > 0 else 'negative'}">{row['return']:.2f}%</span></td>
                        <td>{row['sharpe']:.2f}</td>
                        <td><span class="negative">{row['drawdown']:.2f}%</span></td>
                        <td>{row['trades']:.0f}</td>
                        <td>{row['win_rate']:.2f}%</td>
                        <td><span class="{'positive' if row['pnl'] > 0 else 'negative'}">${row['pnl']:,.0f}</span></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>⚠️ 免責聲明: 本儀表板基於歷史回測數據，不代表未來表現。投資有風險，請謹慎決策。</p>
            <p>💡 建議從小額開始驗證，逐步增加頭寸。</p>
        </div>
    </div>
    
    <script>
        // 收益分布圖
        const returnCtx = document.getElementById('returnChart').getContext('2d');
        new Chart(returnCtx, {
            type: 'bar',
            data: {
                labels: """
    
    labels = [row['name'].split('. ')[-1][:20] for _, row in df.iterrows()]
    html += f"[{', '.join([f\"'{label}'\" for label in labels])}],"
    
    html += f"""
                data: [{', '.join([f"{row['return']:.1f}" for _, row in df.iterrows()])}]
                },
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{ callback: function(value) {{ return value + '%' }} }}
                        }}
                    }}
                }}
            }});
        
        // 風險-收益散點圖
        const riskReturnCtx = document.getElementById('riskReturnChart').getContext('2d');
        new Chart(riskReturnCtx, {
            type: 'scatter',
            data: {
                datasets: [{{
                    label: '策略表現',
                    data: [
"""
    
    for _, row in df.iterrows():
        html += f"{{ x: {row['drawdown']:.1f}, y: {row['return']:.1f} }},\n"
    
    html += f"""
                    ],
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    pointRadius: 8
                }}]
            },
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: true }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return '最大回撤: ' + context.raw.x.toFixed(1) + '% | 收益: ' + context.raw.y.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: '最大回撤 (%)' }}
                    }},
                    y: {{
                        title: {{ display: true, text: '年化收益 (%)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # 保存 HTML
    if output_file is None:
        output_file = Path(report_file).parent / 'strategy_comparison_dashboard.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return str(output_file)


if __name__ == '__main__':
    report_file = '/workspaces/cosmic-ai.uk/reports/backtesting/backtest_report_20260302_193943.json'
    output_file = generate_html_dashboard(report_file)
    print(f"✅ 儀表板已生成: {output_file}")
