"""Unsharp-style sharpen. FAILS the gate: uses deprecated multichannel=."""
from __future__ import annotations

import numpy as np
from skimage import filters

from core.public import normalize


def sharpen(image, sigma=1.0):
    # deprecated: multichannel= was replaced by channel_axis=
    blurred = filters.gaussian(image, sigma=sigma, multichannel=True)
    return normalize(np.asarray(image, dtype=float) - np.asarray(blurred, dtype=float))
