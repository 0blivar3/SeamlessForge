"""Linear correction of opposite-edge color drift."""
import numpy as np


def directional_match(image: np.ndarray, strength: float = 0.75) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3) or min(image.shape[:2]) < 2:
        raise ValueError("image must be a 2D/3D array at least 2x2")
    if not 0 <= strength <= 1:
        raise ValueError("strength must be between 0 and 1")
    has_alpha = image.ndim == 3 and image.shape[2] == 4
    color = image[..., :3] if has_alpha else image
    src = color.astype(np.float32)
    h, w = src.shape[:2]
    # Estimate edge offsets from narrow strips to avoid single-pixel noise.
    band_y, band_x = max(1, h//32), max(1, w//32)
    left = src[:, :band_x].mean(axis=1)
    right = src[:, -band_x:].mean(axis=1)
    top = src[:band_y].mean(axis=0)
    bottom = src[-band_y:].mean(axis=0)
    x = np.linspace(-0.5, 0.5, w, dtype=np.float32)
    y = np.linspace(-0.5, 0.5, h, dtype=np.float32)
    correction_x = (right-left).mean(axis=0) if src.ndim == 3 else float((right-left).mean())
    correction_y = (bottom-top).mean(axis=0) if src.ndim == 3 else float((bottom-top).mean())
    if src.ndim == 3:
        result = src - strength * (y[:, None, None] * correction_y[None, None, :] + x[None, :, None] * correction_x[None, None, :])
    else:
        result = src - strength * (y[:, None] * correction_y + x[None, :] * correction_x)
    if np.issubdtype(image.dtype, np.integer):
        result = np.clip(np.rint(result), 0, np.iinfo(image.dtype).max)
    result = result.astype(color.dtype)
    return np.dstack((result, image[..., 3])) if has_alpha else result
