import numpy as np

from wrapper.sharpen import sharpen


def test_sharpen_preserves_shape():
    img = np.zeros((8, 8, 3))
    assert sharpen(img).shape[:2] == (8, 8)
