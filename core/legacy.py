"""Baselined legacy helpers.

Deprecated scikit-image usage lives here **by design**. The CI gate ignores
`core/`, so this debt does not break the build. Clean-house issues reproduce the
needed behavior in `wrapper/` using current APIs, then retire the call here.

These functions are intentionally not exercised by the test suite.
"""
from __future__ import annotations

import numpy as np
from skimage import color, filters, util


def blur_rgb(image, sigma=1.0):
    # DEBT: multichannel= was replaced by channel_axis=
    return filters.gaussian(image, sigma=sigma, multichannel=True)


def grey(image):
    # DEBT: rgb2grey is a deprecated alias of rgb2gray
    return color.rgb2grey(image)


def padded(image, width=2):
    # DEBT: skimage.util.pad was replaced by numpy.pad
    return util.pad(image, width, mode="reflect")


def erode(image, selem=None):
    # DEBT: selem= was replaced by footprint=
    from skimage import morphology

    return morphology.erosion(image, selem=selem)
