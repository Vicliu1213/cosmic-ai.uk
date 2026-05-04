# Hummingbot Integration

Hermes-side integration point for Hummingbot.

## Scope
- Local orchestration only.
- Dry-run and simulation first.
- No live trading defaults.
- The upstream Hummingbot `hummingbot` conda env must be active.

## Layout
- `bin/` for launch wrappers
- `config/` for runtime configs
- `state/` for audit artifacts
- `docs/` for operator notes

## Operator contract
- Hummingbot runs as an external execution engine.
- Hermes keeps control, risk, and memory.
- All side-effectful actions must be explicitly enabled.

## Launch
```bash
.hermes/hummingbot/bin/hummingbot.sh
```

The wrapper forwards to upstream `./start` inside the vendored Hummingbot tree.
