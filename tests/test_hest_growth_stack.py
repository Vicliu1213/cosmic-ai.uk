from src.tests.hest import build_default_hest_verifier


def test_hest_verifier_reports_growth_stack():
    verifier = build_default_hest_verifier()
    report = verifier.verify()
    stack = next(f for f in report.findings if f.target == 'growth_stack')
    assert stack.passed is True
    assert stack.score >= 1.0
    assert stack.details['state'] == 'stacked'
    assert stack.details['sharpe_growth'] > 0
    assert stack.details['drawdown_ok'] is True
    assert stack.details['recovery_ok'] is True
