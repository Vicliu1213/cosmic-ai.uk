from pathlib import Path


def test_dashboard_app_has_resilience_hooks():
    text = Path('hermes/dashboard/app.js').read_text(encoding='utf-8')
    assert 'window.addEventListener(\'error\'' in text or 'window.onerror' in text
    assert 'window.addEventListener(\'unhandledrejection\'' in text or 'unhandledrejection' in text
    assert 'retry' in text.lower()
    assert 'safeFetch' in text or 'fetchWithRetry' in text
