from src.tests.hest import build_default_hest_verifier


def test_hest_verifier_passes_all_checks():
    verifier = build_default_hest_verifier()
    report = verifier.verify()
    assert report.passed is True
    assert report.failure_count == 0
    assert len(report.findings) == 7


def test_hest_verifier_watch_returns_reports():
    verifier = build_default_hest_verifier()
    reports = verifier.watch(cycles=1, sleep_sec=0)
    assert len(reports) == 1
    assert reports[0]['passed'] is True


def test_hest_verifier_reports_sharpe_growth():
    verifier = build_default_hest_verifier()
    report = verifier.verify()
    sharpe = next(f for f in report.findings if f.target == 'sharpe')
    assert sharpe.passed is True
    assert sharpe.score >= 1.05
    assert sharpe.details['growth'] > 0
