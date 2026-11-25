"""High-level processing pipeline."""
from .algorithms import (
    offset_blend, mirror_tile, poisson_blend,
    edge_feather, fft_seamless, directional_match,
)
from .quality import analyze_edges

ALGORITHMS = {
    "Offset Blending": offset_blend,
    "Mirror Tiling": mirror_tile,
    "Poisson Blending": poisson_blend,
    "Edge Feather": edge_feather,
    "FFT Seamless": fft_seamless,
    "Directional Match": directional_match,
}


def process_image(image, algorithm="Offset Blending", **options):
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    result = ALGORITHMS[algorithm](image, **options)
    return result, analyze_edges(result)
