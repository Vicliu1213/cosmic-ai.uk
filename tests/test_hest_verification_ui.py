from pathlib import Path


def test_hest_verification_page_mentions_growth_stack():
    text = Path('hermes/dashboard/pages/hest_verification.html').read_text(encoding='utf-8')
    assert 'growth stack' in text.lower()
    assert 'nonlinear growth' in text.lower()
    assert 'stacked state' in text.lower()
