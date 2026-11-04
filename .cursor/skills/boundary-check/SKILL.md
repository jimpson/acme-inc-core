---
name: boundary-check
description: Verify an acme-inc-core change stays inside the boundary - wrapper/ and tests/ only, import roots within the whitelist, core reached via core.public. Use before opening a PR or when CI reports a [boundary] failure.
---

# boundary-check

Confirm a change respects the acme-inc-core boundary before review.

## Checklist

1. **Tree.** `git diff --name-only origin/main...HEAD` touches only `wrapper/`
   and `tests/`. Any `core/` edit is out of bounds and must be split into a
   separate, reviewed change.
2. **Import roots** in every changed `wrapper/*.py` (the gate checks the *root*
   of each import):
   - allowed: `core`, `wrapper`, `skimage`, `numpy`, and the whitelisted stdlib
     (`math`, `typing`, `dataclasses`, `functools`, `itertools`, `collections`,
     `statistics`, `__future__`).
   - rejected: any other third-party root (`cv2`, `PIL`, `scipy`, `requests`, ...).
   - rejected: private skimage - a `skimage._*` path or importing an underscored
     name from skimage.
   - allowed: relative imports inside the package (`from . import ...`).
3. **Core access.** `wrapper` reaches `core` only through `core.public`; it never
   imports `core.legacy` or other private core modules.

## Fast path

Run `python tools/ci_gate.py --base origin/main`. Each `[boundary]` line names
the file and the offending import. Resolve by re-expressing the behavior with an
approved module, or by adding the capability to `core.public` in a separate PR -
do not widen the whitelist to make a feature pass.
