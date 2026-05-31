# Checklist

This file defines the promotion and safety checklist for the hybrid-absolute Hermes stack.

## Pre-Change Checklist

- [ ] Did the change preserve operator usefulness?
- [ ] Did the change avoid silent deletion of protected content?
- [ ] Did the change respect omega.md verification boundaries?
- [ ] Did the change keep wording aligned with SOUL.md and protocol.md?

## Pre-Promotion Checklist

- [ ] Is the change visible in screen.md or an equivalent observation surface?
- [ ] Is there a concrete input/output contract?
- [ ] Is there a verification path?
- [ ] Is there a rollback or stop condition?
- [ ] Is the new behavior more reusable, not just more verbose?

## Trading Workflow Checklist

- [ ] Signal source identified
- [ ] Risk budget explicit
- [ ] Execution path explicit
- [ ] Memory write condition explicit
- [ ] Learn / adaptation trigger explicit
- [ ] Simulation or dry-run preferred before live action

## Document Alignment Checklist

- [ ] SOUL / personality / task / prompt meanings do not conflict
- [ ] skills.md and screen.md use the same workflow vocabulary
- [ ] glossary.md terms match current usage
- [ ] protected blocks remain intact

## Transcendence Loop Checklist

- [ ] Phase 1 Survey complete — `state_vector.json` captured
- [ ] Phase 2 Emerge complete — candidates ranked and filtered
- [ ] Phase 3 Validate complete — dry-run passed, resources confirmed, rollback verified
- [ ] Phase 4 Absorb complete — gate activated / ability unlocked / post-state verified
- [ ] Phase 5 Ascend complete — screen, memory, learn, glossary, skills topology all updated
- [ ] Phase 6 Archive complete — full audit trail written to `hermes/archive/transcendence/`
- [ ] Pre-transcendence rollback point is still valid (not garbage-collected)
- [ ] Post-transcendence state outperforms pre-transcendence state by >= agreed threshold
- [ ] No protected content was modified without explicit user confirmation
- [ ] Operator can observe the new capability on the dashboard

## Stop Checklist

Stop and ask the user if:

- protected content may be rewritten or deleted
- the action changes core control laws
- the task implies live trading side effects
- the intended amplification cannot be verified

## Protected Content Rule

- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
