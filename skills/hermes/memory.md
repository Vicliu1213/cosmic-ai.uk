# Memory Policy

This file defines the memory policy for omega recursion.

## Memory Policy
- Retain verified patterns.
- Forget failed or unsafe loops.
- Keep operator usefulness in the memory policy.

## Operator Preference Memory
- If the meaning of a user-supplied core term is unclear, do not delete or normalize it without explicit confirmation.
- Preserve operator-authored terminology first; only adjust formatting, structure, or obvious typos.

## Protected Memory Rule
- Protected memory-policy content must not be deleted by cleanup/default refactors.
- Reading protected memory-policy content is allowed.
- Any edit, overwrite, move, truncation, or deletion of protected memory-policy content requires explicit user confirmation first.
- If a future action may remove or rewrite this section, stop and ask the user.
