---
name: review-ready
description: Final pre-PR pass for acme-inc-core - gate green, tests meaningful, scope minimal, issue referenced. Use right before opening or approving a pull request.
---

# review-ready

Make a change ready for QA approval.

## Gate

- `python tools/ci_gate.py --base origin/main` exits 0 (all three checks pass,
  then pytest passes).

## Tests

- `tests/test_<name>.py` exists for each changed wrapper module and asserts the
  function's contract (shape, range, dtype, edge cases) - not just that it runs.

## Scope and trace

- Diff is limited to `wrapper/` and `tests/`.
- PR body links the issue it closes (`Closes #NN`) and names the category.
- No unrelated reformatting.

## Hand-off

State what a reviewer should verify in 30 seconds: which gate check the issue was
about, and the one assertion that proves it is fixed.
