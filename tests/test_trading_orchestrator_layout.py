from pathlib import Path


def test_trading_orchestrator_page_exists():
    assert Path('hermes/dashboard/pages/trading_orchestrator.html').exists()


def test_trading_orchestrator_mentions_key_sources():
    text = Path('hermes/dashboard/pages/trading_orchestrator.html').read_text(encoding='utf-8')
    assert 'MarketBot' in text
    assert 'OpenAlice' in text
    assert 'UTA-LB' in text
    assert 'Longbridge' in text
    assert 'risk-checklist' in text
    assert 'thesis-tracker' in text
    assert 'gateway' in text.lower()
