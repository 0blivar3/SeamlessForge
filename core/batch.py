"""Batch texture processing utilities."""
from pathlib import Path
from .image_io import load_image, save_image, SUPPORTED_INPUT
from .processor import process_image

def process_folder(source_dir, output_dir, algorithm="Offset Blending", recursive=False):
    source, output = Path(source_dir), Path(output_dir)
    if not source.is_dir():
        raise NotADirectoryError(source)
    files = sorted(p for p in (source.rglob("*") if recursive else source.iterdir())
                   if p.is_file() and p.suffix.lower() in SUPPORTED_INPUT)
    output.mkdir(parents=True, exist_ok=True)
    completed, failures = [], []
    for path in files:
        try:
            image = load_image(path)
            result, metrics = process_image(image, algorithm)
            relative = path.relative_to(source) if recursive else Path(path.name)
            destination = output / relative.with_suffix(".png")
            save_image(destination, result)
            completed.append({"source": str(path), "output": str(destination), "metrics": metrics})
        except Exception as exc:
            failures.append({"source": str(path), "error": str(exc)})
    return {"completed": completed, "failures": failures}
