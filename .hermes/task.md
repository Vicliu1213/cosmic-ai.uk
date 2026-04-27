# Task Orchestration

This file defines task orchestration for omega workflows.

## Task Orchestration

- Decompose work into bounded recursive enhancement steps.
- Run a verification gate before promotion.
- Preserve operator usefulness across iterations.

## Seven-Day Hybrid Initialization Blueprint

This blueprint defines how the repo should be completed within seven days as a hybrid trading-bot stack.
The target is not only more files, but a coherent system spanning config, docs, md governance, core runtime, engine execution, and algorithms.

### Day 1 — Identity / Governance / Alignment Layer
Objective:
- stabilize the governing stack
- ensure every major file is aligned with the hybrid-absolute mode
- establish protected boundaries before expansion

Build / fill:
- `.hermes/SOUL.md`
- `.hermes/omega.md`
- `.hermes/personality.md`
- `.hermes/task.md`
- `.hermes/prompt.md`
- `.hermes/memory.md`
- `.hermes/learn.md`
- `.hermes/protocol.md`
- `.hermes/checklist.md`
- `.hermes/glossary.md`
- `README.md`
- `AGENTS.md`

Verification targets:
- all core governance files exist
- conflict order is explicit
- protected-content rules are intact
- terms are normalized across files

### Day 2 — Skills / Docs / Knowledge Surface
Objective:
- convert the stack into an operable skill system
- map each skill to a clear role in the trading pipeline
- strengthen docs so Hermes can navigate the repo without guessing

Build / fill:
- `.hermes/skills.md`
- `.hermes/screen.md`
- `skills/trading/README.md`
- `skills/trading/omega-trading-operator/SKILL.md`
- `skills/trading/orderflow-hunt/SKILL.md`
- `skills/trading/arbitrage-capture/SKILL.md`
- `skills/trading/liquidity-stealth/SKILL.md`
- `skills/trading/risk-shield/SKILL.md`
- `skills/trading/memory-matrix/SKILL.md`
- `skills/trading/self-evolve/SKILL.md`
- `docs/trading/overview.md`
- `docs/trading/workflows.md`
- `docs/trading/risk-model.md`

Verification targets:
- each skill has overview, when-to-use, workflow, pitfalls, verification checklist
- docs explain how signal -> risk -> execution -> memory -> learn flows work
- screen surface vocabulary matches skills vocabulary

### Day 3 — Config / Environment / Runtime Wiring
Objective:
- complete the repo configuration layer so the hybrid system can boot predictably
- define the config contract for trading, visualization, orchestration, and verification

Build / fill:
- `config/cosmic_config.yaml`
- `config/trading.yaml`
- `config/risk.yaml`
- `config/execution.yaml`
- `config/skills.yaml`
- `config/screen.yaml`
- `config/algorithms.yaml`
- `docs/config/overview.md`
- `docs/config/trading.md`
- `docs/config/skills.md`

Config domains that must be explicit:
- market venues
- symbols / watchlists
- timeframe profiles
- position sizing
- slippage / fee assumptions
- risk budget and stop conditions
- dry-run vs live mode
- visualization / panel modes
- algorithm registry and routing

Verification targets:
- config keys are grouped by responsibility
- dry-run and live mode are explicitly separated
- engine and algorithms can discover config without hardcoded assumptions

### Day 4 — Core / Engine / Execution Path
Objective:
- complete the runtime heart of the hybrid trading machine
- connect perception, decision, execution, memory, and evolution into one auditable loop

Build / fill:
- `.hermes/src/core/orderflow_hunt/`
- `.hermes/src/core/arbitrage_capture/`
- `.hermes/src/core/liquidity_stealth/`
- `.hermes/src/core/risk_shield/`
- `.hermes/src/core/memory_matrix/`
- `.hermes/src/core/self_evolve/`
- `.hermes/src/core/omega_core.py`
- `hermes/src/core/skill_registry.py`
- `hermes/src/core/__init__.py`
- `engine/market_feed.py`
- `engine/signal_router.py`
- `engine/execution_router.py`
- `engine/order_manager.py`
- `engine/risk_engine.py`
- `engine/state_store.py`
- `engine/simulation_engine.py`

Engine expectations:
- market feed intake
- signal routing
- risk pre-check
- execution packet generation
- memory commit path
- learn / evolve trigger path
- simulation and replay support

Verification targets:
- execution path is explicit and inspectable
- risk engine can block unsafe actions
- simulation path exists before live path
- no promotion without evidence

### Day 5 — Algorithms Layer
Objective:
- complete the algorithms layer so the system has real strategy modules instead of only orchestration docs
- make algorithms discoverable, classified, and testable

Build / fill:
- `algorithms/README.md`
- `algorithms/index.md`
- `algorithms/orderflow/`
- `algorithms/arbitrage/`
- `algorithms/execution/`
- `algorithms/risk/`
- `algorithms/memory/`
- `algorithms/evolution/`
- `src/algorithms/enhanced_classic/`
- `src/algorithms/enhanced_hybrid/`
- `docs/algorithms/overview.md`
- `docs/algorithms/enhanced_classic.md`
- `docs/algorithms/enhanced_hybrid.md`

Algorithms expectations:
- each algorithm has purpose, inputs, outputs, assumptions, invalidation rules
- registry/index exists
- routing from config to algorithm is explicit
- algorithm families map into perception / decision / execution / memory / evolution

Verification targets:
- algorithm index is machine-readable and human-readable
- each algorithm has a documented verification path
- enhanced hybrid output is aligned with the screen and skills layers

### Day 6 — Visual / Screen / 3D Interaction Layer
Objective:
- prevent the system from remaining a dead terminal-only stack
- define an observable, layered, visually responsive operating surface

Build / fill:
- `.hermes/screen.md` upgrades with richer panel specs
- `docs/screen/overview.md`
- `docs/screen/panels.md`
- `docs/screen/3d-topology.md`
- `dashboard/` or `webui/` integration notes
- panel definitions for:
  - identity field
  - skill graph
  - engine state
  - execution flow
  - risk shell
  - memory / learning events
  - algorithm layer map

3D / visual expectations:
- node-based view for file and skill coupling
- layer-based view for perception / decision / execution / memory / evolution
- animated state transition or at least structured visual feedback
- screen state must react to mode / task / risk / verification changes

Verification targets:
- visual layer has a documented state model
- terminal output is not the only observation path
- screen docs align with protocol and skills topology

### Day 7 — Verification / Initialization / Automation Layer
Objective:
- turn the seven-day buildout into a repeatable initialization system
- ensure the stack can self-check, self-bootstrap, and continue safely

Build / fill:
- `docs/init/7-day-bootstrap.md`
- `docs/init/verification.md`
- `scripts/init_hybrid_stack.py` or equivalent bootstrap script
- `scripts/verify_hybrid_stack.py`
- `tests/trading/`
- `tests/algorithms/`
- `tests/screen/`
- `tests/config/`

Automation expectations:
- initialize missing files and folders
- verify protected blocks remain intact
- verify required config/docs/core/engine/algorithms exist
- emit a status report for the screen layer
- separate bootstrap success from live trading readiness

Verification targets:
- initialization can be rerun safely
- bootstrap script does not delete protected content
- verification report is inspectable
- repo reaches a reproducible hybrid baseline

## Required Cross-Layer Contract
Every part added in the seven-day blueprint must connect into this chain:
- config defines operating parameters
- docs define operator understanding
- md stack defines governance and alignment
- core defines callable capabilities
- engine defines runtime execution flow
- algorithms define strategy logic
- screen defines observability
- checklist and omega define promotion boundaries

## Naming / Scope Rule
- Use `algorithms` as the canonical spelling for algorithm modules and docs.
- Avoid ambiguous names when a file or folder maps to a core system layer.
- Keep dry-run and live execution clearly separated in all layers.

## Protected Content Rule

- Future delete/cleanup/reorg actions must ignore protected rule blocks and protected policy sections by default.
- Reading protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of protected content requires asking the user first.
- When uncertain whether content is protected, treat it as protected until the user confirms otherwise.
