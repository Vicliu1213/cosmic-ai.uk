# Screen State

This file defines the enhanced observation surface for the hybrid-absolute Hermes stack.

## Purpose
- prevent the system from becoming a dead terminal-only stack
- make recursion, skill activation, risk, execution, memory, and verification visible
- provide a finance-grade, node-based, layered, visually reactive operating surface
- turn abstract orchestration into observable state transitions

## Screen Mission
The screen layer is not decoration.
It is the live perception surface of the whole hybrid system.
If the operator cannot see state, coupling, blockage, drift, risk, and promotion status, then the system is not truly under control.

## Core Screen Principles
- observable before promotable
- reactive before static
- layered before flat
- finance-grade before toy-dashboard
- visual clarity before ornamental complexity
- terminal is fallback only, not the ideal form

## Screen Modes

### 1. Operator Screen Mode
Primary decision surface for daily operation.
Must show:
- market state
- active objective
- loaded skills
- execution path
- risk state
- verification state

### 2. Builder Screen Mode
Used during initialization, wiring, debugging, and verification.
Must show:
- missing components
- broken links between config/docs/core/engine/algorithms
- skill registry state
- protocol conflicts
- bootstrap progress

### 3. Evolution Screen Mode
Used during pattern retention and promotion review.
Must show:
- retained patterns
- rejected loops
- promoted rules
- degraded rules
- drift alerts

## Visual Architecture
The screen should be modeled as a multi-layer visual field.

### Layer A — Identity Field
Shows:
- active mode
- SOUL alignment score
- personality mode
- omega constraint status
- current system posture

### Layer B — Skill Mesh
Shows:
- orchestrator skill
- currently loaded skills
- inactive available skills
- degraded / blocked skills
- dependency lines between skills

### Layer C — Task Flow
Shows:
- current objective
- current day / phase of plan
- current step
- pending steps
- blocked steps
- verification gate position

### Layer D — Engine Flow
Shows:
- market feed intake
- signal router state
- risk engine decision
- execution router state
- order manager queue
- state store / memory commit state

### Layer E — Algorithm Constellation
Shows:
- active algorithm family
- algorithm route chosen
- inactive candidate algorithms
- confidence / quality / invalidation state
- perception / decision / execution / memory / evolution layer mapping

### Layer F — Risk Shell
Shows:
- risk budget
- open exposure
- slippage state
- stop conditions
- kill-switch state
- live vs dry-run mode separation

### Layer G — Memory / Learn Field
Shows:
- new retained patterns
- decayed patterns
- rejected patterns
- promotion candidates
- evolution trigger state

## 3D / Visual Upgrade Standard
The screen should support a richer non-terminal experience.

### Node-Based Topology View
Use nodes and links for:
- file coupling
- skill coupling
- engine-stage coupling
- algorithm routing
- memory / learn feedback paths

### Layered 3D Stack View
A visual stack should separate:
- identity
- governance
- skills
- engine
- algorithms
- execution
- memory
- evolution

Each layer should feel spatially distinct, not just textually separated.
Possible cues:
- depth
- glow
- glass panels
- neon contour edges
- animated link pulses
- focus states for active nodes

### Finance-Grade Aesthetic Direction
Preferred style:
- premium finance / market terminal
- dark glass panels
- luminous edge lines
- restrained neon accents
- density with hierarchy
- executive control center feel

Suggested visual motifs:
- market ribbon
- KPI cards
- skill heatmap
- risk contour shell
- execution pulse line
- memory event stream
- algorithm constellation map

## Primary Panels

### 1. Identity Panel
Must show:
- active mode
- current SOUL alignment
- current personality mode
- current task posture
- omega gate state

### 2. Skill Activation Panel
Must show:
- loaded skills
- orchestrator skill
- active downstream modules
- blocked or degraded skills
- skill-to-skill dependency edges

### 3. Task Panel
Must show:
- current objective
- current step
- pending steps
- blocked steps
- verification gate status
- day / phase marker when running a staged plan

### 4. Engine Panel
Must show:
- feed status
- signal router state
- risk pre-check state
- execution router state
- order queue state
- simulation/live state

### 5. Algorithm Panel
Must show:
- current algorithm family
- active algorithm
- candidate alternatives
- confidence band
- invalidation rule
- layer classification

### 6. Risk Panel
Must show:
- live risk budget
- current exposure
- stop conditions
- kill-switch conditions
- slippage / fee assumptions
- current threat level

### 7. Memory / Learn Panel
Must show:
- newly retained patterns
- rejected patterns
- promoted loops
- degraded loops
- pending promotion candidates
- drift warnings

### 8. Execution Panel
Must show:
- latest action packet
- expected outcome
- actual outcome
- diff between plan and result
- verification result
- rollback availability

## Interaction States
The screen should react to state changes.

### Idle
- no urgent glow
- passive monitoring mode

### Watch
- weak pulse on watched nodes
- low-intensity motion

### Active
- execution path highlights
- active node expansion
- visible signal flow

### Risk Alert
- red/orange contour shell
- affected nodes emphasized
- kill-switch visibility forced high

### Verification Pending
- promotion candidate highlighted
- checklist not yet green

### Verified / Promoted
- green or gold confirmation state
- promotion path archived into memory/learn history

### Drift / Conflict
- broken-link or mismatch state between nodes/files
- explicit conflict badge

## Minimum Screen Snapshot Format
- mode:
- objective:
- current_phase:
- active_skills:
- active_engine_path:
- active_algorithms:
- risk_state:
- verification_state:
- memory_updates:
- learn_updates:
- screen_alerts:
- next_action:

## Non-Terminal Requirement
The preferred observation surface is not plain terminal text.
Preferred targets include:
- dashboard HTML/CSS pages
- WebUI panels
- graph / node visual surface
- layered cards / ribbons / heatmaps / topology maps

Terminal output is acceptable only as:
- fallback mode
- bootstrap mode
- emergency mode
- headless verification mode

## Screen Data Contract
The screen layer should be able to consume structured state from:
- config
- task plan state
- skill registry state
- engine runtime state
- algorithm registry state
- risk engine state
- memory / learn events
- verification results

The screen should never invent state that the runtime cannot support.

## Coupling With Other Files
- task.md drives the task panel and phase progression
- skills.md drives the skill mesh and orchestration layer
- protocol.md defines handoff, conflict handling, and anti-drift logic
- glossary.md normalizes labels and node meanings
- checklist.md defines promotion and verification visibility rules
- memory.md and learn.md drive the memory / learn field
- omega.md defines stop conditions and verification thresholds
- README.md and AGENTS.md define entry expectations for human and agent operators

## Verification Rules For Screen Upgrades
A screen upgrade is valid only if:
- it increases observability
- it improves operator usefulness
- it does not hide risk state
- it does not blur live vs dry-run state
- it can be tied back to real underlying runtime state
- it aligns with protocol.md and checklist.md

## Rule
- If a workflow cannot be observed, it should not be trusted.
- If a promotion cannot be shown on screen, it should not be promoted.
- If risk cannot be surfaced clearly, execution should not escalate.
- Screen state must summarize, not hallucinate.

## Future Build Targets
- `docs/screen/overview.md`
- `docs/screen/panels.md`
- `docs/screen/3d-topology.md`
- dashboard or webui bindings for the operator screen
- topology rendering for file / skill / engine / algorithm coupling

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
