import numpy as np

from wrapper.segment import segment


def test_segment_returns_bool_mask():
    img = np.zeros((8, 8))
    assert segment(img).dtype == bool
