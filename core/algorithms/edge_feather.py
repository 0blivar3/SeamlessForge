"""Wrap-aware feathering of opposite image borders."""
import cv2
import numpy as np


def edge_feather(image: np.ndarray, width: int | None = None, sigma: float = 3.0) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3) or min(image.shape[:2]) < 4:
        raise ValueError("image must be a 2D/3D array at least 4x4")
    h, w = image.shape[:2]
    width = max(2, min(h, w) // 12) if width is None else int(width)
    if not 1 <= width <= min(h, w) // 2:
        raise ValueError("width must be between 1 and half the shortest dimension")
    has_alpha = image.ndim == 3 and image.shape[2] == 4
    color = image[..., :3] if has_alpha else image
    src = color.astype(np.float32)
    k = max(3, int(max(0.1, sigma) * 6) | 1)
    pad = max(width, k // 2)
    wrapped = cv2.copyMakeBorder(src, pad, pad, pad, pad, cv2.BORDER_WRAP)
    blurred = cv2.GaussianBlur(wrapped, (k, k), max(0.1, sigma))[pad:pad+h, pad:pad+w]
    yy, xx = np.mgrid[:h, :w]
    distance = np.minimum.reduce([xx, w-1-xx, yy, h-1-yy]).astype(np.float32)
    mask = np.clip((width - distance) / max(1, width), 0, 1)
    mask = (mask * mask * (3 - 2 * mask))[..., None] if src.ndim == 3 else mask * mask * (3 - 2 * mask)
    result = src * (1-mask) + blurred * mask
    if np.issubdtype(image.dtype, np.integer):
        result = np.clip(np.rint(result), 0, np.iinfo(image.dtype).max)
    result = result.astype(color.dtype)
    return np.dstack((result, image[..., 3])) if has_alpha else result
