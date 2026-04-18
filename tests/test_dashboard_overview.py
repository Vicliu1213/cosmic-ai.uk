from pathlib import Path


def test_dashboard_overview_page_exists():
    page = Path('hermes/dashboard/pages/algorithms.html')
    assert page.exists()


def test_dashboard_index_has_overview_link():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'Algorithms Overview' in text
    assert 'Hest Verification' in text
    assert 'Enhanced Hybrid' in text
