from pathlib import Path


def test_dashboard_finance_visuals_exist():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'market-ribbon' in text
    assert 'kpi-grid' in text
    assert 'sparkline-chart' in text
    assert 'liquidity heatmap' in text
