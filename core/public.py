"""Public surface of the core package. `wrapper/` may only touch core here."""
from __future__ import annotations

import numpy as np
from skimage import color


def ensure_gray(image):
    """Return a 2-D float grayscale image, accepting RGB(A) or gray input."""
    arr = np.asarray(image)
    if arr.ndim == 3 and arr.shape[-1] in (3, 4):
        return color.rgb2gray(arr[..., :3])
    return arr.astype(float)


def normalize(image):
    """Scale to [0, 1]. Flat images map to zeros."""
    arr = np.asarray(image, dtype=float)
    lo, hi = float(arr.min()), float(arr.max())
    if hi <= lo:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)
