"""Image loading and exporting with predictable channel handling."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

SUPPORTED_INPUT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".tga", ".webp"}
SUPPORTED_OUTPUT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".tga", ".webp"}

def load_image(path: str | Path) -> np.ndarray:
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_INPUT:
        raise ValueError(f"Unsupported image format: {path.suffix}")
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode == "P":
            im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        elif im.mode not in ("L", "RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        return np.array(im).copy()

def save_image(path: str | Path, image: np.ndarray) -> None:
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_OUTPUT:
        raise ValueError(f"Unsupported output format: {path.suffix}")
    if not isinstance(image, np.ndarray) or image.ndim not in (2, 3):
        raise ValueError("Expected a grayscale, RGB or RGBA image")
    data = np.clip(image, 0, 255).astype(np.uint8)
    im = Image.fromarray(data)
    if path.suffix.lower() in (".jpg", ".jpeg") and im.mode not in ("L", "RGB"):
        im = im.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, quality=95)
