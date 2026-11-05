"""Total-variation denoise. Clean API; FAILS the gate via its weak test."""
from __future__ import annotations

from skimage import restoration

from core.public import ensure_gray


def denoise(image, weight=0.1):
    return restoration.denoise_tv_chambolle(ensure_gray(image), weight=weight)
