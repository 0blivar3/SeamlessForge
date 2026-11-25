import numpy as np
from core.image_io import load_image, save_image

def test_png_roundtrip_preserves_rgba(tmp_path):
    image=np.zeros((12,15,4),dtype=np.uint8)
    image[...,0]=180; image[...,3]=127
    path=tmp_path/"rgba.png"
    save_image(path,image)
    loaded=load_image(path)
    assert loaded.shape==image.shape
    assert np.array_equal(loaded,image)

def test_jpeg_export_drops_alpha_safely(tmp_path):
    image=np.zeros((10,10,4),dtype=np.uint8)
    image[...,0]=220; image[...,3]=255
    path=tmp_path/"rgb.jpg"
    save_image(path,image)
    loaded=load_image(path)
    assert loaded.shape==(10,10,3)
