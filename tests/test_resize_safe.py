import numpy as np

from wrapper.resize_safe import resize_safe


def test_resize_safe_shape_and_range():
    img = np.random.default_rng(0).random((16, 16))
    out = resize_safe(img, (8, 8))
    assert out.shape == (8, 8)
    assert out.min() >= 0.0 and out.max() <= 1.0
