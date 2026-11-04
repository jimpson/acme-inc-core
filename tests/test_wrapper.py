import numpy as np

from wrapper.enhance import equalize


def test_equalize_returns_normalized_gray():
    img = (np.random.default_rng(0).random((8, 8, 3)) * 255).astype(np.uint8)
    out = equalize(img)
    assert out.shape == (8, 8)
    assert out.min() >= 0.0 and out.max() <= 1.0
