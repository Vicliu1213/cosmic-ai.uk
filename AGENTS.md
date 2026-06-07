# AGENTS.md

Project guidance for Hermes and other coding agents.

## Quick start

```bash
pip install -r requirements.txt   # ray, pyyaml
npm install                        # @ngrok/ngrok
python main.py                     # run engine once
COSMIC_KEEP_RUNNING=1 python3 main.py  # keep-alive mode
```

## Architecture

- **Entry**: `main.py` (read-only 444 — do not modify without asking).
- **Config**: `config/cosmic_config.yaml` — YAML-driven; edit there, not in code.
- **15 theory actors**: `src/<theory>/core.py` — each exports an `*Actor` Ray class; orchestrated by `orchestrator.py`.
- **Core modules**: `cosmic/` — Agent, Consensus, Trading, KnowledgeBase, etc.
- **Dashboard**: port 8788 (`/pages/synergy_panel.html`); ngrok tunnel in `start.sh`.
- **Startup scripts**: `run.sh` (engine only), `start.sh` (engine + dashboard + ngrok).

## Testing

```bash
python -m pytest tests/test_*.py -v       # single run
bash scripts/run_all_tests.sh              # batch
```

`pytest.ini` sets `testpaths = tests` and excludes `vendor`, `hermes`, `.hermes`.

## Hermes governance stack

The active stack lives at `skills/hermes/`. Key files:
- `SOUL.md` — identity, `omega.md` — control law, `protocol.md` — coupling rules
- `skills.md` — capability topology, `screen.md` — observation surface
- `checklist.md` — promotion/verification gates, `glossary.md` — term alignment
- `task.md` — decomposition, `transcendence.md` — 6-phase evolution loop
- `memory.md`, `learn.md`, `personality.md`, `prompt.md`

## Operating rules

- Prefer simulation, dry-run, and explicit verification before any live execution path.
- Keep durable workflow updates in files under `skills/hermes/` or `skills/`, not only in chat.
- Protected policy blocks in `skills/hermes/*.md` must not be modified without explicit confirmation.

## Protected content

- `skills/hermes/*.md` — all contain protected-content blocks; read allowed, edit requires confirmation.
- `main.py` — read-only (444); modify only after asking.
- `.env` — contains live API keys (exchanges, ngrok, OpenRouter); never commit or expose.
- `ngrok.yml` — contains authtoken; treat as sensitive.

## Conventions

- No formatter/linter at repo root — use Python idioms from existing code.
- All theory modules follow the same pattern: `src/<theory>/core.py` with a Ray `Actor` class.
- YAML config is the single source of truth for runtime parameters.
- Logs go to `cosmic_engine.log`.
