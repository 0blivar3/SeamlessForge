"""Mirror-based repeat generation."""
import numpy as np

def mirror_tile(image: np.ndarray, repetitions: int = 2) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3):
        raise ValueError("image must be a 2D or 3D numpy array")
    if image.size == 0:
        raise ValueError("image cannot be empty")
    if not isinstance(repetitions, int) or not 1 <= repetitions <= 16:
        raise ValueError("repetitions must be between 1 and 16")
    bands = []
    for y in range(repetitions):
        row = image if y % 2 == 0 else np.flip(image, axis=0)
        bands.append(np.concatenate([row if x % 2 == 0 else np.flip(row, axis=1)
                                     for x in range(repetitions)], axis=1))
    return np.concatenate(bands, axis=0).copy()
