# Skills Topology

This file defines the skill topology for the hybrid-absolute Hermes stack.

## Purpose
- Turn abstract intent into callable capability organs.
- Organize skills into a layered execution mesh instead of isolated documents.
- Make trading-operation flows easy to compose, verify, and reuse.

## Skill Layers

### 1. Perception Layer
Use for sensing, scanning, and market/context intake.
- orderflow-hunt
- discovery / monitoring / sensing modules
- data and feed ingestion skills

### 2. Decision Layer
Use for comparison, triage, risk, and plan formation.
- risk-shield
- arbitrage-capture
- thesis / scenario selection skills

### 3. Execution Layer
Use for concrete action packets and implementation.
- liquidity-stealth
- execution adapters
- order generation, splitting, and routing skills

### 4. Memory Layer
Use for state retention and pattern recall.
- memory-matrix
- recall / commit / forgetting policies

### 5. Evolution Layer
Use for iterative improvement after verification.
- self-evolve
- retrospection and promotion rules

## Trading Orchestration Rule
- For trading-operation tasks, load the orchestration skill first.
- Use only the minimum set of downstream skills needed for the current objective.
- Prefer dry-run, simulation, and verification before any live or side-effectful path.
- Every trade flow should pass through: signal -> risk -> execution -> memory -> learn.

## Input/Output Contract
- Inputs must be explicit: symbol, timeframe, venue, risk budget, execution style.
- Outputs must be operator-friendly: action, size, stop, target, invalidation, verification status.
- Skills should emit concrete packets, not vague advice.

## Coupling With Other Files
- SOUL.md defines why skills exist.
- personality.md defines how skills are expressed.
- task.md defines when skills are sequenced.
- prompt.md defines how skills are invoked in-session.
- memory.md defines what skill outcomes are retained.
- learn.md defines what skill patterns are promoted.
- screen.md defines how skill state is observed.
- protocol.md defines conflict resolution and handoff rules.

## Upgrade Standard
A skill is considered upgraded only when it is:
- concrete
- visualizable
- reusable
- auditable
- tied to a verification path

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
