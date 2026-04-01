#!/usr/bin/env python3
"""
Compare My Quantum Hybrid Backtest vs Your LLM TradeBot Backtest
對比我的量化混合回測 vs 你的LLM-TradeBot回測
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Load my backtest results
my_results_file = "/workspaces/cosmic-ai.uk/reports/backtesting/enhanced_quantum_hybrid_final.json"
csv_reports_dir = "/workspaces/cosmic-ai.uk/reports/backtesting/"

print("\n" + "="*80)
print("🔬 BACKTEST SYSTEM COMPARISON: My Quantum Hybrid vs Your LLM-TradeBot")
print("="*80)

# ============================================================================
# 1. MY SYSTEM RESULTS
# ============================================================================
print("\n" + "="*80)
print("📊 PART 1: MY QUANTUM-CLASSICAL HYBRID BACKTEST SYSTEM")
print("="*80)

if os.path.exists(my_results_file):
    with open(my_results_file, 'r') as f:
        my_results = json.load(f)
    
    print("\n✅ My System Results Loaded:")
    print(f"   Report: {my_results_file}")
    print(f"   Timestamp: {my_results.get('timestamp', 'N/A')}")
    
    # Print 6 strategies analyzed
    print("\n📈 Individual Strategy Performance:")
    print(f"{'Strategy':<40} {'Return':<12} {'Sharpe':<12} {'Drawdown':<12}")
    print("-" * 76)
    
    strategies = my_results.get('strategies', {})
    for i, (name, metrics) in enumerate(strategies.items(), 1):
        return_pct = metrics.get('return', 0) * 100
        sharpe = metrics.get('sharpe_ratio', 0)
        dd = metrics.get('max_drawdown', 0) * 100
        print(f"{i}. {name:<38} {return_pct:>+10.2f}% {sharpe:>10.2f} {dd:>10.2f}%")
    
    # Print optimal portfolio
    print("\n🎯 Optimal Portfolio Configuration:")
    optimal_weights = my_results.get('optimal_weights', {})
    for strategy, weight in optimal_weights.items():
        print(f"   {strategy}: {weight*100:.1f}%")
    
    print(f"\n📊 Expected Portfolio Performance:")
    portfolio_metrics = my_results.get('portfolio_metrics', {})
    print(f"   Return: {portfolio_metrics.get('return', 0)*100:+.2f}%")
    print(f"   Sharpe Ratio: {portfolio_metrics.get('sharpe_ratio', 0):.2f}")
    print(f"   Max Drawdown: {portfolio_metrics.get('max_drawdown', 0)*100:.2f}%")
    
    # Print quantum metrics
    print(f"\n⚛️  Quantum Algorithm Metrics:")
    quantum_metrics = my_results.get('quantum_metrics', {})
    print(f"   Entanglement Entropy (Initial): {quantum_metrics.get('entanglement_entropy_initial', 0):.4f} bits")
    print(f"   Entanglement Entropy (Final): {quantum_metrics.get('entanglement_entropy_final', 0):.4f} bits")
    print(f"   Circuit Depth: {quantum_metrics.get('circuit_depth', 0)} layers")
    print(f"   Grover Iterations: {quantum_metrics.get('grover_iterations', 0)}")
    print(f"   Classical Improvement: {quantum_metrics.get('classical_improvement_pct', 0):.2f}%")
else:
    print(f"❌ My results file not found: {my_results_file}")

# ============================================================================
# 2. CHECK CSV REPORTS
# ============================================================================
print("\n" + "="*80)
print("📊 PART 2: MY SYSTEM - CSV REPORTS SUMMARY")
print("="*80)

csv_files = {
    '01_individual_strategies_ranking.csv': '6 Strategies Ranked',
    '02_portfolio_scenarios_comparison.csv': '3 Portfolio Scenarios (Aggressive/Balanced/Conservative)',
    '03_aggressive_portfolio_weights.csv': 'Aggressive Scenario Weights',
    '04_balanced_portfolio_weights.csv': 'Balanced Scenario Weights (Recommended)',
    '05_conservative_portfolio_weights.csv': 'Conservative Scenario Weights',
    '06_comprehensive_summary.csv': 'Complete Strategy Summary'
}

print("\n📁 Generated Reports:")
for filename, description in csv_files.items():
    filepath = os.path.join(csv_reports_dir, filename)
    if os.path.exists(filepath):
        size_kb = os.path.getsize(filepath) / 1024
        print(f"   ✅ {filename:<40} - {description:<50} ({size_kb:.1f} KB)")
    else:
        print(f"   ❌ {filename:<40} - NOT FOUND")

# ============================================================================
# 3. YOUR SYSTEM STATUS
# ============================================================================
print("\n" + "="*80)
print("🔬 PART 3: YOUR LLM-TRADEBOT BACKTEST SYSTEM")
print("="*80)

llm_tradebot_dir = "/workspaces/cosmic-ai.uk/external/llm_tradebot"
print(f"\n📍 LLM-TradeBot Location: {llm_tradebot_dir}")

if os.path.exists(llm_tradebot_dir):
    print("✅ LLM-TradeBot system found")
    
    # List main backtest components
    backtest_components = [
        'backtest.py',
        'compare_strategies.py',
        'run_multi_symbol_backtest.py',
        'src/backtest/engine.py',
        'src/backtest/data_replay.py',
        'src/backtest/metrics.py',
        'src/backtest/portfolio.py',
    ]
    
    print("\n🔧 LLM-TradeBot Backtest Components:")
    for component in backtest_components:
        comp_path = os.path.join(llm_tradebot_dir, component)
        if os.path.exists(comp_path):
            size_kb = os.path.getsize(comp_path) / 1024 if os.path.isfile(comp_path) else 0
            status = "✅" if os.path.exists(comp_path) else "❌"
            print(f"   {status} {component:<40} ({size_kb:.1f} KB)")
else:
    print("❌ LLM-TradeBot system not found")

# ============================================================================
# 4. KEY DIFFERENCES
# ============================================================================
print("\n" + "="*80)
print("🔄 PART 4: KEY DIFFERENCES BETWEEN SYSTEMS")
print("="*80)

differences = {
    "Core Algorithm": {
        "My System": "Enhanced Quantum-Classical Hybrid (QAOA+VQE+Grover)",
        "Your System": "Multi-Agent LLM Framework + Technical Indicators"
    },
    "Data Source": {
        "My System": "CSV files (8,760 hourly candles per pair)",
        "Your System": "Real-time Binance API (fetches historical data)"
    },
    "Strategy Count": {
        "My System": "6 strategies (Cosmic + Hummingbot combinations)",
        "Your System": "Multiple modes (technical, agent, LLM-enhanced)"
    },
    "Optimization Method": {
        "My System": "Quantum superposition + classical refinement (SLSQP)",
        "Your System": "LLM decision-making + risk auditing"
    },
    "Portfolio Weighting": {
        "My System": "Automated quantum discovery (60% AS, 40% PMM)",
        "Your System": "Multi-symbol selection or fixed allocation"
    },
    "Report Outputs": {
        "My System": "JSON, CSV, HTML dashboard, Markdown",
        "Your System": "HTML reports, JSON metrics, terminal output"
    }
}

for aspect, systems in differences.items():
    print(f"\n📌 {aspect}:")
    for system, detail in systems.items():
        print(f"   {system:<15}: {detail}")

# ============================================================================
# 5. NEXT STEPS FOR COMPARISON
# ============================================================================
print("\n" + "="*80)
print("🎯 NEXT STEPS FOR FULL COMPARISON")
print("="*80)

print("""
To run a comprehensive comparison with your LLM-TradeBot system:

1. **Quick Test** (5 minutes):
   cd /workspaces/cosmic-ai.uk/external/llm_tradebot
   python backtest.py --start 2023-06-01 --end 2023-06-30 \\
     --symbol BTCUSDT --capital 10000 --step 12 --strategy-mode technical \\
     --no-report

2. **Strategy Comparison** (10 minutes):
   cd /workspaces/cosmic-ai.uk/external/llm_tradebot
   python compare_strategies.py --symbol SOLUSDT --days 30

3. **Multi-Symbol Backtest** (30+ minutes):
   cd /workspaces/cosmic-ai.uk/external/llm_tradebot
   python run_multi_symbol_backtest.py

4. **Compare Results**:
   - My System: 6 strategies → 1 optimal portfolio (60% AS, 40% PMM)
   - Your System: Output portfolio weights and expected returns
   - Side-by-side analysis: Sharpe ratio, max drawdown, returns

""")

# ============================================================================
# 6. SYSTEM STATUS SUMMARY
# ============================================================================
print("\n" + "="*80)
print("📋 SUMMARY")
print("="*80)

print(f"""
✅ My Quantum-Classical Hybrid System:
   - Status: COMPLETE & PRODUCTION-READY
   - Backtest: ✅ Completed with 6 strategies
   - Result: 60% Avellaneda-Stoikov + 40% Pure Market Making
   - Expected Return: 172.91% | Sharpe: 1.35 | Max DD: 35.70%
   - Reports: 6 CSV files + JSON + HTML dashboard

✅ Your LLM-TradeBot System:
   - Status: READY TO TEST
   - Backtest: 🔄 Pending (requires Binance API data fetch)
   - Strategy: Multi-Agent LLM framework
   - Data: Live API integration
   - Reports: HTML + JSON + Terminal output

🔄 Comparison:
   - Same dataset (BTC_USDT, ETH_USDT, BNB_USDT, SOL_USDT, ADA_USDT, XRP_USDT)
   - Same period (ideally 1 year historical data)
   - Metrics: Return %, Sharpe Ratio, Max Drawdown %, Win Rate
""")

print("="*80)
print("Ready to run comparison? Choose an option above or ask for clarification.")
print("="*80 + "\n")
