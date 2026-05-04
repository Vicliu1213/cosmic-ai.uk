from pathlib import Path
import json
import subprocess


RUNTIME_STATE_PATH = Path('hermes/dashboard/runtime_state.json')
SELF_IMPROVING_SKILL_PATH = Path('skills/self-improving-agent/SKILL.md')


def test_runtime_state_json_exists_and_has_identity():
    data = json.loads(RUNTIME_STATE_PATH.read_text(encoding='utf-8'))
    assert data['identity']['mode'] in {'passive', 'active', 'hybrid'}
    assert data['identity']['objective']
    assert 'memory_learn' in data
    assert 'mcp' in data


def test_runtime_state_json_is_rewritten_by_omega_cli():
    RUNTIME_STATE_PATH.write_text('{"sentinel": true}', encoding='utf-8')
    result = subprocess.run(
        ['python', '.hermes/hermes.py', 'hermes', '--mode', 'active', '--limit', '1'],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(RUNTIME_STATE_PATH.read_text(encoding='utf-8'))
    assert 'sentinel' not in data
    assert data['identity']['mode'] == 'active'
    assert data['identity']['objective'] == 'hermes'
    assert 'skill_mesh' in data
    assert 'runtime_state_path' in result.stdout
    assert 'hermes/dashboard/runtime_state.json' in result.stdout


def test_dashboard_pages_have_screen_surface_mount():
    trade = Path('hermes/dashboard/pages/trading_orchestrator.html').read_text(encoding='utf-8')
    omega = Path('hermes/dashboard/pages/omega_system.html').read_text(encoding='utf-8')
    assert 'screen-surface' in trade
    assert 'screen-surface' in omega
    assert 'data-runtime-mode' in trade
    assert 'data-runtime-mode' in omega


def test_app_js_bridges_runtime_state_for_root_and_pages():
    text = Path('hermes/dashboard/app.js').read_text(encoding='utf-8')
    assert 'assetPath(filename)' in text
    assert "assetPath('runtime_state.json')" in text
    assert "assetPath('module_catalog.json')" in text
    assert 'renderScreenSurface(state)' in text


def test_omega_cli_outputs_dashboard_state():
    result = subprocess.run(
        ['python', '.hermes/hermes.py', 'hermes', '--mode', 'hybrid', '--limit', '1'],
        check=True,
        capture_output=True,
        text=True,
    )
    stdout = result.stdout
    assert 'dashboard' in stdout
    assert 'memory_update' in stdout
    assert 'trade_result' in stdout


def test_self_improving_skill_exists_and_has_required_sections():
    text = SELF_IMPROVING_SKILL_PATH.read_text(encoding='utf-8')
    assert text.startswith('---\n')
    assert 'name: self-improving-agent' in text
    assert '## Overview' in text
    assert '## When to Use' in text
    assert '## Promotion Rules' in text
    assert '## Verification Checklist' in text


def test_agent_browse_surface_mentions_self_improving_skill():
    agents_root = Path('agents/README.md').read_text(encoding='utf-8')
    agents_skills = Path('agents/skills/README.md').read_text(encoding='utf-8')
    skill_readme = Path('agents/skills/self-improving-agent/README.md').read_text(encoding='utf-8')
    skill_index = Path('agents/skills/self-improving-agent/index.md').read_text(encoding='utf-8')
    skills_readme = Path('skills/README.md').read_text(encoding='utf-8')
    assert 'self-improving-agent' in agents_root
    assert 'self-improving-agent' in agents_skills
    assert 'reusable self-improvement workflow' in skill_readme.lower()
    assert 'skills/self-improving-agent/SKILL.md' in skill_index
    assert 'skills/self-improving-agent/SKILL.md' in skills_readme
