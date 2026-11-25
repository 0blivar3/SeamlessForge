"""Seam diagnostics. Metrics are indicators, not mathematical guarantees."""
import numpy as np

def analyze_edges(image: np.ndarray) -> dict:
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3) or min(image.shape[:2]) < 2:
        raise ValueError("Expected an image at least 2x2")
    pixels = image[..., :3] if image.ndim == 3 and image.shape[2] >= 3 else image
    arr = pixels.astype(np.float32)
    horizontal = float(np.mean(np.abs(arr[:, 0] - arr[:, -1])))
    vertical = float(np.mean(np.abs(arr[0, :] - arr[-1, :])))
    score = max(0.0, 100.0 * (1.0 - (horizontal + vertical) / (2.0 * 255.0)))
    return {"horizontal_edge_difference": horizontal, "vertical_edge_difference": vertical,
            "seam_score": score, "rating": "Excellent" if score >= 98 else "Good" if score >= 94 else "Needs work"}
