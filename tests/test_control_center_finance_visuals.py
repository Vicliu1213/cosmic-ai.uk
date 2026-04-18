from pathlib import Path


def test_control_center_finance_visuals_exist():
    text = Path('hermes/dashboard/pages/control_center.html').read_text(encoding='utf-8')
    assert 'performance ribbon' in text
    assert 'strategy pulse' in text
    assert 'risk contour' in text
