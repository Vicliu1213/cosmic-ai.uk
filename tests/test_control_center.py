from pathlib import Path


def test_control_center_page_exists():
    assert Path('hermes/dashboard/pages/control_center.html').exists()


def test_control_center_is_linked_from_dashboard():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'Control Center' in text
