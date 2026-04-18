# Task Orchestration

## Purpose
Define how tasks are planned, split, executed, verified, and promoted.

## Task layers
- intake: capture request and constraints
- decomposition: split into bite-sized steps
- execution: perform the task
- verification: test and inspect results
- promotion: save durable outcomes into docs, skills, or memory

## Task rules
- Every important task should have an explicit acceptance criterion.
- Every implementation task should have tests.
- Every non-trivial task should have a rollback strategy.
- Use subtasks for independent work.
- Use Hest-style verification for dashboard and agent changes.
- For omega flows, each recursive step must be bounded, measurable, and reversible.

## Task document format
- Goal
- Constraints
- Inputs
- Output
- Dependencies
- Verification
- Risks
- Rollback

## Decision policy
- Prefer the simplest solution that is still future-proof.
- If a task can be solved by configuration, do not hardcode it.
- If a task needs repeated use, make it a reusable component.
- If a recursive improvement harms operator usefulness, stop and revert.
