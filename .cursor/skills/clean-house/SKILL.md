---
name: clean-house
description: Turn a clean-house issue into a convention-compliant wrapper change with a passing CI gate. Use when resolving a deprecated-api, weak-tests, or boundary issue in acme-inc-core.
---

# clean-house

Resolve one tech-debt issue in `acme-inc-core` without crossing the boundary.

## Steps

1. Read the issue and its category label (`deprecated-api`, `weak-tests`,
   `boundary`). The target is always a file under `wrapper/`.
2. Confirm scope: you may edit `wrapper/` and `tests/` only. Never edit `core/`.
   Reach `core` through `core.public`.
3. Apply the fix:
   - **deprecated-api**: replace the deprecated call with the current public
     scikit-image API (e.g. `channel_axis=` for `multichannel=`).
   - **weak-tests**: add real assertions to `tests/test_<name>.py` covering the
     wrapper function's contract.
   - **boundary**: remove the out-of-whitelist or private-`skimage._*` import;
     re-express via an approved module.
4. Run `python tools/ci_gate.py --base origin/main`. It must print the changed
   wrapper files, pass all three checks, then pass pytest.
5. Open a PR to `main`. CI re-runs the same gate.

## Done when

The gate is green and the change touches only `wrapper/` and `tests/`.
