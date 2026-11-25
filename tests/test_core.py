import numpy as np
import pytest
from core.algorithms import (
    offset_blend, mirror_tile, poisson_blend,
    edge_feather, fft_seamless, directional_match,
)
from core.quality import analyze_edges
from core.processor import process_image


def test_offset_preserves_shape_dtype():
    image=np.random.default_rng(2).integers(0,256,(64,80,3),dtype=np.uint8)
    result=offset_blend(image)
    assert result.shape==image.shape and result.dtype==image.dtype


def test_offset_grayscale_and_alpha():
    for shape in ((32,32),(32,32,4)):
        image=np.random.default_rng(1).integers(0,256,shape,dtype=np.uint8)
        assert offset_blend(image).shape==shape


def test_mirror_dimensions_and_pattern():
    image=np.arange(12,dtype=np.uint8).reshape(3,4)
    result=mirror_tile(image,2)
    assert result.shape==(6,8)
    assert np.array_equal(result[:3,:4],image)
    assert np.array_equal(result[:3,4:],np.fliplr(image))


def test_quality_metrics():
    image=np.zeros((16,16,3),dtype=np.uint8)
    assert analyze_edges(image)["seam_score"]==100


def test_unknown_algorithm():
    with pytest.raises(ValueError):
        process_image(np.zeros((8,8),dtype=np.uint8),"unknown")


@pytest.mark.parametrize("algorithm", [edge_feather, fft_seamless, directional_match])
@pytest.mark.parametrize("shape", [(48,64), (48,64,3), (48,64,4)])
def test_new_algorithms_preserve_shape_dtype_and_alpha(algorithm, shape):
    image=np.random.default_rng(7).integers(0,256,shape,dtype=np.uint8)
    result=algorithm(image)
    assert result.shape == image.shape
    assert result.dtype == image.dtype
    if len(shape)==3 and shape[-1]==4:
        assert np.array_equal(result[...,3], image[...,3])


def test_processor_registers_new_algorithms():
    image=np.random.default_rng(3).integers(0,256,(48,64,3),dtype=np.uint8)
    for name in ("Edge Feather", "FFT Seamless", "Directional Match"):
        result, metrics = process_image(image, name)
        assert result.shape == image.shape
        assert "seam_score" in metrics
