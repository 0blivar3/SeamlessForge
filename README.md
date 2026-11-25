# SeamlessForge

SeamlessForge is a desktop toolkit for preparing tileable textures, inspecting seams and previewing materials. It targets Python 3.12+ and uses PySide6, OpenCV, NumPy and Pillow.

## Features

### Texture algorithms
- **Offset Blending** — offsets the image and blends the central cross to move visible borders into the middle.
- **Poisson Blending** — gradient-domain seam repair.
- **Mirror Tiling** — creates a mirrored repeat for textures that tolerate reflection.
- **Edge Feather** — wrap-aware soft blending around all four borders.
- **FFT Seamless** — frequency-domain low-pass correction focused on border bands.
- **Directional Match** — compensates broad horizontal and vertical color drift between opposite edges.

### Workflow and preview
- Interactive software-rendered 3D sphere preview. It does not require OpenGL or a specific graphics driver.
- 2D repeated preview, edge diagnostics, drag-and-drop, undo/redo and folder batch processing.
- PNG, JPEG, BMP, TIFF, TGA and WebP import/export.
- Background image processing and GitHub Actions tests on Windows, macOS and Linux.

## Quick start

**Windows (PowerShell)**
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

## Tests
```bash
pytest -q
```

## Windows installer
Run the **Windows installer** workflow manually from GitHub Actions, or push a version tag such as `v0.1.0`.

## Notes
- The seam score measures opposite-edge pixel differences; it is a diagnostic, not a mathematical guarantee.
- Mirror Tiling creates a larger mirrored repeat.
- FFT Seamless and Edge Feather soften border regions and can reduce detail; compare the output before exporting.
- Poisson Blending may alter local color and contrast.
