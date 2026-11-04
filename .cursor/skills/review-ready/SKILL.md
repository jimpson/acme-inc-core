---
name: review-ready
description: Final pre-PR pass for acme-inc-core - gate green, tests prove the contract, scope minimal, issue referenced. Use right before opening or approving a pull request.
---

# review-ready

Make a change ready for QA approval. The gate is necessary but not sufficient;
this pass covers what the gate cannot see.

## Gate (machine)

- `python tools/ci_gate.py --base origin/main` exits 0: all three checks pass,
  then pytest passes.

## Tests (reviewer)

- `tests/test_<name>.py` exists for each changed wrapper module, references it,
  and asserts the **contract** - output shape, value range, dtype, and at least
  one edge case - not merely that the function runs.
- The decisive check: revert the fix and the test must fail. If it still passes,
  the test is weak regardless of the gate.

## Scope and trace (reviewer)

- Diff is limited to `wrapper/` and `tests/`; `core/` is untouched.
- PR body links the issue (`Closes #NN`) and names the category
  (`deprecated-api`, `weak-tests`, `boundary`).
- No unrelated reformatting, renames, or refactors used to dodge a textual check.

## Hand-off

In two lines, tell the reviewer: which gate category the issue was, and the one
assertion that proves it is fixed (and would fail if reverted).
