from src.tests.hest import build_default_hest_verifier


def test_hest_verifier_reports_strategy_winrate_and_backtest():
    verifier = build_default_hest_verifier()
    report = verifier.verify()
    strategy = next(f for f in report.findings if f.target == 'strategy')
    assert strategy.passed is True
    assert strategy.details['live_win_rate'] >= strategy.details['backtest_win_rate']
    assert strategy.details['backtest_trades'] >= 100
    assert strategy.details['live_trades'] >= 20
    assert strategy.details['edge'] >= 0
