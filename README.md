# acme-inc-core

Acme Inc.'s internal image-processing core. A convention-heavy Python library
built on top of [scikit-image](https://scikit-image.org/) that provides a stable,
reviewed surface for image operations used across Acme services and pipelines.

## Installation

```sh
pip install -e ".[dev]"
```

Requires Python 3.11+.

## Usage

```python
import numpy as np
from core import ensure_gray, normalize
from wrapper import equalize

img = np.random.rand(128, 128, 3)

gray = ensure_gray(img)        # RGB/RGBA -> float grayscale
norm = normalize(gray)         # scale to [0, 1]
eq   = equalize(img)           # histogram-equalized output
```

- `core` is the reviewed, stable foundation. Treat it as the public API.
- `wrapper` holds higher-level operations composed from `core` and scikit-image.

## Repository layout

| Path | Role |
| --- | --- |
| `core/` | Stable internal package and public surface (`core/public.py`). Changes here require platform-team review. |
| `wrapper/` | Higher-level image operations. Most feature work lands here. |
| `tests/` | pytest suite. Every `wrapper/<name>.py` ships with `tests/test_<name>.py`. |
| `tools/ci_gate.py` | Convention gate run in CI (see Contributing). |
| `.github/workflows/ci.yml` | CI pipeline. |
| `.cursor/` | Repo conventions and skills for assisted development. |

## Contributing

All changes land through a pull request to `main` and must pass CI. The pipeline
runs a convention gate (`tools/ci_gate.py`) over the diff, plus the full test
suite. For any changed `wrapper/*.py`, the gate enforces three standards:

1. **Supported APIs only** - no deprecated scikit-image calls (e.g.
   `multichannel=`, `rgb2grey`, `selem=`, `util.pad`).
2. **Import boundary** - imports stay within the approved whitelist; no private
   `skimage._*` modules and no unvetted third-party dependencies.
3. **Real tests** - a matching `tests/test_<name>.py` exists and makes
   assertions.

`main` is protected: PRs require review, a passing `convention-gate` check, and
an up-to-date branch before merge.

## Local development

```sh
pip install -e ".[dev]"
pytest
python tools/ci_gate.py --base origin/main
```

## License

Proprietary - (c) Acme Inc. Internal use only.
