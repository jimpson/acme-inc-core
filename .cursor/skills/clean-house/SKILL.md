---
name: clean-house
description: Turn one acme-inc-core tech-debt issue into a convention-compliant wrapper change that passes the CI gate and holds up in review. Use when resolving a deprecated-api, weak-tests, or boundary issue.
---

# clean-house

Resolve exactly one tech-debt issue in `acme-inc-core` without crossing the
boundary, and leave behind a test that proves the fix.

## Steps

1. **Scope.** Read the issue and its category label. The target is one
   `wrapper/<name>.py`. You may edit `wrapper/` and `tests/` only - never
   `core/`. Reach `core` through `core.public`.
2. **Fix by category:**
   - **deprecated-api**: replace the deprecated call with the current public
     scikit-image API (`channel_axis=` for `multichannel=`, `footprint=` for
     `selem=`, `rgb2gray` for `rgb2grey`, `numpy.pad` for `util.pad`,
     `skimage.metrics` for `compare_*`). Remove the token from comments too - the
     gate matches raw text.
   - **weak-tests**: write assertions that pin the contract - output shape, value
     range, dtype, and an edge case - not just that the call returns. `assert
     True` and constant assertions are rejected.
   - **boundary**: remove the out-of-whitelist or private `skimage._*` import and
     re-express the behavior with an approved module, or (as a separate, reviewed
     change) add the capability to `core.public`.
3. **Keep the diff minimal.** Only the files the issue requires; no unrelated
   reformatting.
4. **Verify locally.** `python tools/ci_gate.py --base origin/main` must pass all
   three checks, then pytest, before you open the PR.
5. **Open the PR to `main`.** Reference the issue (`Closes #NN`) and name the
   category. CI re-runs the gate and blocks merge until it is green.

## Done when

The gate is green, the diff touches only `wrapper/` and `tests/`, and the new or
updated test fails if the fix is reverted.
