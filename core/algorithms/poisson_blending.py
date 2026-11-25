"""OpenCV Poisson blending for reducing visible offset seams."""
import cv2
import numpy as np

def poisson_blend(image: np.ndarray) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3) or min(image.shape[:2]) < 8:
        raise ValueError("image must be a 2D/3D array at least 8x8")
    gray = image.ndim == 2
    alpha = image[..., 3].copy() if image.ndim == 3 and image.shape[2] == 4 else None
    rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if gray else image[..., :3]
    h, w = image.shape[:2]
    src = np.roll(rgb, (h//2, w//2), axis=(0, 1))
    src8 = np.clip(src, 0, 255).astype(np.uint8)
    mask = np.full((h, w), 255, np.uint8)
    try:
        result = cv2.seamlessClone(src8, src8.copy(), mask, (w//2, h//2), cv2.NORMAL_CLONE)
    except cv2.error:
        result = src8
    result = np.roll(result, (-(h//2), -(w//2)), axis=(0, 1))
    if gray:
        result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    if alpha is not None:
        result = np.dstack((result, alpha))
    return result.astype(image.dtype)
