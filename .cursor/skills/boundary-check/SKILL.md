---
name: boundary-check
description: Verify a change stays inside the acme-inc-core boundary (wrapper/ only, import whitelist, public core surface). Use before opening a PR or when CI reports a boundary failure.
---

# boundary-check

Confirm a change respects the acme-inc-core boundary before review.

## Checklist

1. **Tree**: `git diff --name-only origin/main...HEAD` touches only `wrapper/`
   and `tests/`. Any `core/` change is out of bounds.
2. **Imports** in changed `wrapper/*.py`:
   - allowed roots: `core`, `wrapper`, `skimage`, `numpy`, stdlib.
   - no private `skimage._*` modules.
   - no third-party libraries outside the allowlist (no `cv2`, `PIL`,
     `requests`, ...).
3. **Core access**: `wrapper` reaches `core` only through `core.public`.

## Fast path

Run `python tools/ci_gate.py --base origin/main`; a `[boundary]` line names the
offending file and import. Resolve by re-expressing the behavior with an approved
module or by adding the capability to `core.public` (a separate, reviewed change).
