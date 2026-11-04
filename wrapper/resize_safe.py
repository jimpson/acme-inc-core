"""Convention-compliant resize. PASSES the gate (green fix branch)."""
from __future__ import annotations

from skimage import transform

from core.public import normalize


def resize_safe(image, shape):
    out = transform.resize(image, shape, anti_aliasing=True)
    return normalize(out)
