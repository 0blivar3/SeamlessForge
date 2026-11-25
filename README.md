# SeamlessForge

SeamlessForge is a desktop toolkit for preparing tileable textures, inspecting seams and previewing materials. It targets Python 3.12+ and uses PySide6, OpenCV, NumPy and Pillow.

## Current features
- **Seam repair:** Offset Blending with wrap-aware filtering and alpha-channel preservation.
- **Additional tiling:** Mirror Tiling (creates a mirrored repeated image) and Poisson Blending.
- **Diagnostics:** opposite-edge difference measurements and a seam score indicator.
- **Preview:** 2D repeated texture preview and an interactive OpenGL sphere material preview.
- **Workflow:** drag-and-drop loading, background processing, undo/redo history and folder batch processing.
- **Formats:** PNG, JPEG, BMP, TIFF, TGA and WebP. Alpha is preserved where the selected format supports it.
- **Automation:** pytest suite and GitHub Actions on Windows, macOS and Linux.

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

## Windows executable
```powershell
pyinstaller --noconfirm --windowed --name SeamlessForge --collect-all PySide6 --collect-all OpenGL main.py
```

## Important notes
- The seam score measures the color difference between opposite edge pixels. It is a useful diagnostic, not a mathematical guarantee of seamless repetition.
- Mirror Tiling outputs a larger mirrored repeat; it does not preserve the original dimensions.
- Poisson blending may change local color and contrast. Always inspect the result before exporting.
- 3D preview requires a working OpenGL 3.3-capable graphics driver. The 3D viewport currently previews the texture on a sphere.

## Planned expansion
The next development milestones are patch-based texture synthesis, editable blend parameters, presets, more material meshes (plane/cube), richer quality diagnostics, and a signed Windows installer.
