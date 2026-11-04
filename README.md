# acme-inc-core

A convention-heavy image-processing library built on top of
[scikit-image](https://scikit-image.org/). It exists to demo **"clean house"**:
paying down accumulated technical debt with an AI agent that stays inside a
boundary and is provable in CI.

## Layout

| Path | Role |
| --- | --- |
| `core/` | Convention-heavy internal package. Carries **baselined** debt (`core/legacy.py`). The CI gate does **not** scan `core/`. |
| `wrapper/` | The **only** tree an issue may change. Calls `core` through its public surface. |
| `tests/` | pytest suite. Every changed `wrapper/<name>.py` needs `tests/test_<name>.py`. |
| `.cursor/rules/` | Standing conventions (public scikit-image APIs only, tests required, import whitelist). |
| `.cursor/skills/` | `clean-house`, `boundary-check`, `review-ready`. |
| `tools/ci_gate.py` | Diff-aware convention gate used by CI. |
| `.github/workflows/ci.yml` | Runs the gate on every push/PR. |

## The guardrail

`tools/ci_gate.py` compares the branch to `origin/main` and, for each changed
`wrapper/*.py`, enforces three rules:

1. **deprecated-api** - no deprecated scikit-image calls (e.g. `multichannel=`,
   `rgb2grey`, `selem=`, `util.pad`).
2. **boundary** - imports limited to a whitelist; no private `skimage._*`
   modules, no un-approved third-party libraries.
3. **weak-tests** - the matching `tests/test_<name>.py` must exist and assert.

Then the full test suite must pass. Because the gate only looks at the **diff**
under `wrapper/`, the debt baselined in `core/` keeps `main` green while new work
is held to the conventions.

## Branches (demo)

- `main` - runnable, debt baselined, green.
- `bug/deprecated-call` - wrapper feature using a deprecated API -> fails gate.
- `bug/weak-test` - wrapper feature whose test has no assertion -> fails gate.
- `bug/bad-import` - wrapper feature importing a private module -> fails gate.
- `fix/deprecated-api-demo` - a compliant wrapper feature with a real test -> green.

## Run locally

```sh
pip install -e ".[dev]"
python tools/ci_gate.py --base origin/main
```
