"""Baseline wrapper feature. Clean, current scikit-image API."""
from __future__ import annotations

from skimage import exposure

from core.public import ensure_gray, normalize


def equalize(image):
    """Histogram-equalize an image to a normalized grayscale result."""
    gray = normalize(ensure_gray(image))
    return exposure.equalize_hist(gray)
