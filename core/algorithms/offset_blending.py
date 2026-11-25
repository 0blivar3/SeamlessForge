"""Seam-aware offset blending for tileable images."""
import cv2
import numpy as np

def offset_blend(image: np.ndarray, blend_width: int | None = None, blur_sigma: float = 8.0) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3):
        raise ValueError("image must be a 2D or 3D numpy array")
    h, w = image.shape[:2]
    if h < 2 or w < 2:
        raise ValueError("image must be at least 2x2 pixels")
    if blend_width is None:
        blend_width = max(1, min(h, w) // 8)
    blend_width = int(blend_width)
    if not 1 <= blend_width <= min(h, w) // 2:
        raise ValueError("blend_width must be between 1 and half the shortest image dimension")
    has_alpha = image.ndim == 3 and image.shape[2] == 4
    alpha = image[..., 3].copy() if has_alpha else None
    work = image[..., :3] if has_alpha else image
    src = work.astype(np.float32)
    shifted = np.roll(src, (h // 2, w // 2), axis=(0, 1))
    out = shifted.copy()
    cx, cy = w // 2, h // 2
    for i in range(blend_width):
        t = (i + 1) / (blend_width + 1)
        a, b = shifted[:, cx-1-i].copy(), shifted[:, cx+i].copy()
        mixed = a * (1-t) + b * t
        out[:, cx-1-i] = a * (1-.5*t) + mixed * (.5*t)
        out[:, cx+i] = b * (1-.5*(1-t)) + mixed * (.5*(1-t))
        a, b = out[cy-1-i, :].copy(), out[cy+i, :].copy()
        mixed = a * (1-t) + b * t
        out[cy-1-i, :] = a * (1-.5*t) + mixed * (.5*t)
        out[cy+i, :] = b * (1-.5*(1-t)) + mixed * (.5*(1-t))
    if blur_sigma > 0:
        k = max(3, int(blur_sigma * 2) | 1)
        pad = k // 2
        padded = cv2.copyMakeBorder(out, pad, pad, pad, pad, cv2.BORDER_WRAP)
        blurred = cv2.GaussianBlur(padded, (k, k), blur_sigma)[pad:-pad, pad:-pad]
        mask = np.zeros((h, w), np.float32)
        mask[:, max(0,cx-blend_width):min(w,cx+blend_width)] = .25
        mask[max(0,cy-blend_width):min(h,cy+blend_width), :] = .25
        if out.ndim == 3:
            mask = mask[..., None]
        out = out * (1-mask) + blurred * mask
    result = np.roll(out, (-(h // 2), -(w // 2)), axis=(0, 1))
    if np.issubdtype(image.dtype, np.integer):
        result = np.clip(np.rint(result), 0, np.iinfo(image.dtype).max)
    result = result.astype(work.dtype)
    if has_alpha:
        result = np.dstack((result, alpha))
    return result
