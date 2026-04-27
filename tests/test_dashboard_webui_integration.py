from pathlib import Path


def test_dashboard_webui_page_exists():
    page = Path('hermes/dashboard/pages/webui_hub.html')
    assert page.exists()


def test_dashboard_index_links_webui_hub():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'WebUI Hub' in text
    assert './pages/webui_hub.html' in text
    assert 'Open Hermes WebUI · localhost:8787' in text


def test_control_center_links_webui_hub():
    text = Path('hermes/dashboard/pages/control_center.html').read_text(encoding='utf-8')
    assert 'WebUI Hub' in text
    assert './webui_hub.html' in text
    assert 'Vendor UI Clone' in text


def test_webui_hub_contains_vendor_and_port_markers():
    text = Path('hermes/dashboard/pages/webui_hub.html').read_text(encoding='utf-8')
    assert 'Hermes WebUI Integration Hub' in text
    assert 'http://127.0.0.1:8787' in text
    assert '../../vendor/hermes-webui/static/index.html' in text
    assert 'webui-preview-frame' in text
    assert 'workspace panel' in text
