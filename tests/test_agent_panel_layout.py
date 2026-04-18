from pathlib import Path


def test_agent_panel_page_exists():
    assert Path('hermes/dashboard/pages/agent_panel.html').exists()


def test_agent_panel_contains_core_sections():
    text = Path('hermes/dashboard/pages/agent_panel.html').read_text(encoding='utf-8')
    assert 'SOUL.md' in text
    assert 'personality.md' in text
    assert 'task.md' in text
    assert 'prompt.md' in text
    assert 'learn.md' in text
    assert 'memory.md' in text
    assert '3D persona' in text
    assert 'self-evolving' in text


def test_dashboard_links_to_agent_panel():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'Agent Panel' in text
    text2 = Path('hermes/dashboard/pages/control_center.html').read_text(encoding='utf-8')
    assert 'Agent Panel' in text2
