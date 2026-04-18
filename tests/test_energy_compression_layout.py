from pathlib import Path


def test_energy_compression_page_exists():
    assert Path('hermes/dashboard/pages/energy_compression.html').exists()


def test_energy_compression_mentions_core_terms():
    text = Path('hermes/dashboard/pages/energy_compression.html').read_text(encoding='utf-8')
    assert 'energy dispatch' in text
    assert 'token savings' in text
    assert 'vacuum volatility' in text
    assert 'net profit compression' in text
    assert 'dynamic compression' in text
    assert 'adaptive scheduling' in text


def test_dashboard_links_energy_compression():
    index = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    control = Path('hermes/dashboard/pages/control_center.html').read_text(encoding='utf-8')
    trade = Path('hermes/dashboard/pages/trading_orchestrator.html').read_text(encoding='utf-8')
    assert 'Energy Compression' in index
    assert 'Energy Compression' in control
    assert 'Energy Compression' in trade
