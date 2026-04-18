# Prompt Library

## Purpose
Provide reusable prompt patterns for the Hermes workspace.

## Prompt types
- planner prompt: for structuring multi-step work
- executor prompt: for direct implementation
- reviewer prompt: for checking correctness and quality
- debugger prompt: for root-cause analysis
- agent prompt: for switching personas and workloads

## Prompt rules
- Keep prompts self-contained.
- Include exact file paths when possible.
- Include verification commands when relevant.
- State constraints clearly and early.
- Prefer prompts that produce machine-checkable outputs.

## Reusable prompt patterns
- "Create a plan and include tests."
- "Implement the minimal change that passes the test."
- "Investigate root cause before changing code."
- "Summarize status and risks in one screen."
- "Optimize for clarity, safety, and reusability."
