# SeamlessForge

A desktop texture tiling and seam-repair toolkit built with Python 3.12+, PySide6, OpenCV, NumPy and Pillow.

## Features
- Offset blending and mirrored tiling.
- Poisson-based seam blending (OpenCV).
- Edge discontinuity diagnostics.
- 2D repeated preview, drag-and-drop loading and background processing.
- PNG, JPEG, BMP, TIFF, TGA and WebP import/export; alpha is retained where supported.
- Pytest coverage for core algorithms.

## Quick start
**Windows**
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

**macOS / Linux**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Run tests with `pytest`.

## Build a Windows executable
```powershell
pyinstaller --noconfirm --windowed --name SeamlessForge --collect-all PySide6 main.py
```

## Notes
Seam analysis compares opposite border pixels and is a diagnostic indicator, not a proof that a texture is seamless. Mirror Tiling creates a larger mirrored repeat; it does not repair the source image in place. Poisson blending can alter image colors and is best reviewed in the preview before export.

## Roadmap
Advanced patch synthesis, 3D material preview, batch processing, presets, operation history and installer packaging are planned as subsequent milestones.
