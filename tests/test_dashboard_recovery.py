from pathlib import Path


def test_dashboard_recovery_hooks_exist():
    text = Path('hermes/dashboard/app.js').read_text(encoding='utf-8')
    assert 'fetchWithRetry' in text
    assert 'installResilienceHooks' in text
    assert 'unhandledrejection' in text
    assert 'dashboard-toast' in text


def test_trading_orchestrator_linked_from_dashboard():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'Trading Orchestrator' in text


def test_agent_panel_mentions_resilience():
    text = Path('hermes/dashboard/pages/agent_panel.html').read_text(encoding='utf-8')
    assert 'offline recovery' in text
    assert 'retry' in text
    assert 'no-crash mode' in text
