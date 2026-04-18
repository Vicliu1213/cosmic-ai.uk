from pathlib import Path


def test_hest_verification_page_mentions_strategy_metrics():
    text = Path('hermes/dashboard/pages/hest_verification.html').read_text(encoding='utf-8')
    assert 'strategy win rate' in text.lower()
    assert 'backtest' in text.lower()
    assert 'live trading' in text.lower()
