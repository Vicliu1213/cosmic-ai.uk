---
name: self-improving-agent
description: Use when the repo needs a concrete self-improvement workflow for logging errors, corrections, feature requests, promotion candidates, and converting them into durable memory/skill/system updates.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [self-improvement, learning-loop, memory, promotion, retrospective]
    related_skills: [writing-plans, requesting-code-review, test-driven-development]
---

# Self-Improving Agent

## Overview

Use this skill to turn mistakes, corrections, repeated workflow friction, and newly discovered better approaches into a durable improvement loop.

The skill is not only for writing notes. It defines an operator-grade cycle:
1. detect errors or corrections
2. log them in a structured way
3. classify whether they belong in learning, error, or feature-request lanes
4. promote stable patterns into repo rules, memory, or reusable skills
5. verify the promoted rule is concrete and still true

This repo already treats `.hermes/` as canonical governance state. This skill complements that by defining how new operational knowledge is captured and promoted instead of being lost in chat history.

## When to Use

Use when:
- a command, script, tool, API, or runtime path fails unexpectedly
- the user corrects an assumption, workflow, or fact
- a recurring rough edge suggests missing automation or missing docs
- a new workflow worked and should become reusable
- a bug fix, dashboard enhancement, or orchestration change revealed a stable convention
- a pattern should be promoted into `.hermes/`, `AGENTS.md`, a skill, or memory

Do not use for:
- temporary TODO status
- one-off progress logs with no future value
- noisy transcripts that are not distilled into a concrete lesson

## Improvement Lanes

### 1. Error lane
Use for failed commands, broken integrations, bad assumptions, missing dependencies, and unexpected runtime behavior.

Record:
- what failed
- where it failed
- exact error or symptom
- likely root cause
- proposed remediation
- verification command

### 2. Learning lane
Use for corrections, clarified conventions, newly discovered best practices, and durable environment facts.

Record:
- what changed in understanding
- the corrected rule
- what it should affect next time
- whether it belongs in memory, docs, or a skill

### 3. Feature-request lane
Use for capabilities that do not exist yet but were requested or implied by recurring friction.

Record:
- desired capability
- user context
- expected operator value
- likely scope and dependencies

### 4. Promotion lane
Use when a learning is mature enough to become part of the system.

Promotion targets:
- `.hermes/` for project-local operating rules and governance surfaces
- `AGENTS.md` for repo-wide agent workflow rules
- `memory` tool for durable user/environment facts
- `skills/` for reusable procedures
- tests when the lesson implies a regression guard

## Canonical Logging Structure

Prefer a repo-local learning surface such as `.learnings/` or another dedicated notes directory. If none exists yet, create one only when the user wants the logging surface persisted in-repo.

Recommended files:
- `.learnings/LEARNINGS.md`
- `.learnings/ERRORS.md`
- `.learnings/FEATURE_REQUESTS.md`

Recommended entry format:

```markdown
## [LRN-YYYYMMDD-001] concise-title

**Logged**: ISO timestamp
**Priority**: low | medium | high | critical
**Status**: pending | in_progress | resolved | promoted | wont_fix
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line lesson.

### Details
What happened, what was wrong, what is now known.

### Suggested Action
Concrete next step.

### Metadata
- Source: conversation | user_feedback | runtime_error | verification
- Related Files: path/a, path/b
- Pattern-Key: stable.key.if.recurring
- See Also: related IDs
```

## Promotion Rules

Promote a learning when at least one is true:
- it is likely to recur
- it changes how future work should be done
- it prevents repeated user correction
- it affects more than one file or workflow
- it should be enforced by tests or verification gates

Promotion guidance:
- stable fact about user or environment -> memory tool
- reusable procedure -> new or updated skill
- project-local governance rule -> `.hermes/` or `AGENTS.md`
- code behavior expectation -> test first, then implementation

## Repo Mapping For This Project

In this repo, typical promotion destinations are:
- `.hermes/skills.md` -> skill topology additions
- `.hermes/learn.md` -> promotion logic and learning rules
- `.hermes/memory.md` -> retained system-level memory boundaries
- `.hermes/checklist.md` -> verification gates
- `agents/skills/` -> agent-facing browse surface
- `skills/` -> reusable local skill artifacts
- `tests/` -> executable regression guards

## Operator Workflow

1. Detect
   - identify the failure, correction, or opportunity
2. Distill
   - reduce it to one concrete lesson
3. Classify
   - error, learning, feature request, or promotion candidate
4. Promote selectively
   - choose memory, docs, skill, or tests
5. Verify
   - confirm the promoted artifact is actually used and still correct

## Common Pitfalls

1. Logging raw noise instead of a distilled lesson
2. Saving temporary progress into durable memory
3. Leaving a useful workflow only in chat instead of a file or skill
4. Promoting vague advice instead of concrete rules
5. Skipping verification after promotion
6. Creating duplicate skills when a patch to an existing one is enough

## Verification Checklist

- [ ] The lesson is concrete, not a transcript dump
- [ ] The lane is correct: error, learning, feature request, or promotion
- [ ] Durable facts are promoted to the right destination
- [ ] Temporary state is not saved to memory
- [ ] Reusable workflows become or update a skill
- [ ] Verification was run after the promotion
- [ ] Repo-visible surfaces were updated when discoverability matters
