# Agents Surface

This directory provides an agent-facing entry surface for reusable governance, skills, and schemas.

## Browse

- `agents/skills/`: agent-consumable skill surfaces
- `agents/skills/core/`: core shared governance stack mirror
- `agents/skills/core/index.md`: browse index for the core stack
- `agents/schemas/`: machine-readable schemas and contracts

## Current Surface

### Skills

- `agents/skills/README.md`: skill-surface index
- `agents/skills/core/README.md`: core surface overview
- `agents/skills/core/index.md`: file-by-file browse map
- `agents/skills/self-improving-agent/README.md`: self-improvement workflow surface
- `agents/skills/self-improving-agent/index.md`: self-improvement browse entry

### Schemas

- `agents/schemas/immortal_perpetual_schema.json`: reserved schema entry for agent/runtime contracts

## Source of Truth

- Canonical governance source remains `.hermes/`
- `agents/skills/core/` is a lightweight agent-facing mirror for browsing and bootstrapping
- Edit `.hermes/` files when changing governance content

## Notes

- Prefer the `index.md` entry when browsing
- Prefer `.hermes/` when editing
