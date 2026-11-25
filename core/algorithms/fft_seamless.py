"""Frequency-domain periodic smoothing focused on tile boundaries."""
import cv2
import numpy as np


def fft_seamless(image: np.ndarray, strength: float = 0.35, cutoff: float = 0.08) -> np.ndarray:
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3) or min(image.shape[:2]) < 4:
        raise ValueError("image must be a 2D/3D array at least 4x4")
    if not 0 <= strength <= 1 or not 0 < cutoff <= 0.5:
        raise ValueError("strength must be 0..1 and cutoff must be >0..0.5")
    has_alpha = image.ndim == 3 and image.shape[2] == 4
    color = image[..., :3] if has_alpha else image
    src = color.astype(np.float32)
    h, w = src.shape[:2]
    # Build a Gaussian low-pass transfer function in frequency space.
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    radius2 = fx * fx + fy * fy
    transfer = np.exp(-radius2 / (2 * cutoff * cutoff)).astype(np.float32)
    channels = [src] if src.ndim == 2 else [src[..., c] for c in range(src.shape[2])]
    smooth = []
    for channel in channels:
        spectrum = np.fft.rfft2(channel)
        low = np.fft.irfft2(spectrum * transfer, s=(h, w)).real.astype(np.float32)
        smooth.append(low)
    low_image = smooth[0] if src.ndim == 2 else np.stack(smooth, axis=-1)
    # Blend the periodic low-frequency reconstruction only around the borders.
    yy, xx = np.mgrid[:h, :w]
    edge_distance = np.minimum.reduce([xx, w-1-xx, yy, h-1-yy]).astype(np.float32)
    band = max(2, min(h, w) // 10)
    mask = np.clip((band - edge_distance) / band, 0, 1)
    mask = (mask * mask * (3 - 2 * mask)) * strength
    if src.ndim == 3:
        mask = mask[..., None]
    result = src * (1-mask) + low_image * mask
    if np.issubdtype(image.dtype, np.integer):
        result = np.clip(np.rint(result), 0, np.iinfo(image.dtype).max)
    result = result.astype(color.dtype)
    return np.dstack((result, image[..., 3])) if has_alpha else result
