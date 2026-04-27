# AGENTS.md

Project guidance for Hermes and other coding agents.

## Trading skills first
- For trading-operation tasks, start at `.hermes/skills.md` and `.hermes/protocol.md`.
- Load the orchestration skill at `skills/trading/omega-trading-operator/SKILL.md` first when the repo-local skills tree is present, then load only the module skills you actually need.
- Source modules live under `.hermes/src/core/`; repo-local skills in `skills/trading/` are the human/agent operating layer for those modules.
- Use `.hermes/screen.md` for the observation surface, `.hermes/checklist.md` for promotion gates, and `.hermes/glossary.md` to normalize terminology.

## Repo-local trading skills
- `skills/trading/orderflow-hunt/SKILL.md`
- `skills/trading/arbitrage-capture/SKILL.md`
- `skills/trading/liquidity-stealth/SKILL.md`
- `skills/trading/risk-shield/SKILL.md`
- `skills/trading/memory-matrix/SKILL.md`
- `skills/trading/self-evolve/SKILL.md`
- `skills/trading/omega-trading-operator/SKILL.md`

## Operating rule
- Prefer simulation, dry-run, and explicit verification before any live execution path.
- Use the skill references and templates to make outputs concrete, visual, and auditable.
- Keep durable workflow updates in files under `.hermes/` or `skills/`, not only in chat.
- Protected policy blocks must be ignored by default during delete/cleanup/reorg actions.
- Reading protected policy blocks is allowed, but modifying, moving, truncating, or deleting them requires explicit user confirmation first.

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
