from pathlib import Path


def test_persona_system_docs_exist():
    for rel in [
        '.hermes/SOUL.md',
        '.hermes/personality.md',
        '.hermes/task.md',
        '.hermes/prompt.md',
        '.hermes/learn.md',
        '.hermes/memory.md',
    ]:
        assert Path(rel).exists(), rel


def test_persona_system_docs_contain_sections():
    soul = Path('.hermes/SOUL.md').read_text(encoding='utf-8')
    personality = Path('.hermes/personality.md').read_text(encoding='utf-8')
    task = Path('.hermes/task.md').read_text(encoding='utf-8')
    prompt = Path('.hermes/prompt.md').read_text(encoding='utf-8')
    learn = Path('.hermes/learn.md').read_text(encoding='utf-8')
    memory = Path('.hermes/memory.md').read_text(encoding='utf-8')

    assert 'global identity' in soul.lower()
    assert 'personality modes' in personality.lower()
    assert 'task orchestration' in task.lower()
    assert 'prompt library' in prompt.lower()
    assert 'learning loop' in learn.lower()
    assert 'memory policy' in memory.lower()
