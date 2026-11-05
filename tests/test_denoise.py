import numpy as np

from wrapper.denoise import denoise


def test_denoise_runs():
    img = np.zeros((8, 8, 3))
    denoise(img)  # weak test: no assertion on the result
