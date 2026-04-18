from pathlib import Path


def test_omega_docs_exist_and_define_bounded_recursive_enhancement():
    text = Path('.hermes/omega.md').read_text(encoding='utf-8')
    assert 'bounded recursive enhancement' in text.lower()
    assert 'verification gate' in text.lower()
    assert 'operator usefulness' in text.lower()


def test_omega_docs_link_from_agent_files():
    soul = Path('.hermes/SOUL.md').read_text(encoding='utf-8')
    personality = Path('.hermes/personality.md').read_text(encoding='utf-8')
    task = Path('.hermes/task.md').read_text(encoding='utf-8')
    assert 'omega' in soul.lower()
    assert 'omega' in personality.lower()
    assert 'omega' in task.lower()
