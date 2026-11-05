"""Threshold segmentation. FAILS the gate: imports a private skimage module."""
from __future__ import annotations

import numpy as np
from skimage.filters._gaussian import gaussian  # private module, out of bounds

from core.public import normalize


def segment(image, thresh=0.5):
    smoothed = normalize(gaussian(np.asarray(image, dtype=float)))
    return smoothed > thresh
