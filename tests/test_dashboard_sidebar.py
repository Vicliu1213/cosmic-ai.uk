from pathlib import Path


def test_dashboard_has_sidebar_panel():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'sidebar-nav' in text
    assert 'Algorithms Overview' in text
    assert 'Hest Verification' in text
    assert 'Enhanced Hybrid' in text
