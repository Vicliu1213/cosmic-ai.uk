from pathlib import Path


def test_dashboard_links_to_omega_panel():
    index = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    control = Path('hermes/dashboard/pages/control_center.html').read_text(encoding='utf-8')
    trade = Path('hermes/dashboard/pages/trading_orchestrator.html').read_text(encoding='utf-8')
    assert 'Omega System' in index
    assert 'Omega System' in control
    assert 'Omega System' in trade


def test_omega_panel_page_exists():
    assert Path('hermes/dashboard/pages/omega_system.html').exists()


def test_omega_panel_mentions_core_terms():
    text = Path('hermes/dashboard/pages/omega_system.html').read_text(encoding='utf-8')
    assert 'omega recursive enhancement' in text.lower()
    assert 'bounded recursive improvement' in text.lower()
    assert 'recursive enhancement loop' in text.lower()
    assert 'verification gate' in text.lower()
    assert 'operator usefulness' in text.lower()
