# Task Orchestration

This document defines the task orchestration layer for Hermes.

## Task Orchestration

- Break work into bounded steps.
- Verify each step before promotion.
- Keep operator usefulness as the primary goal.

## Protected Content Rule

- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
