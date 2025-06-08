import os

import pytest
from PIL import Image

from src.core.image_processor import ImageProcessingError, ImageProcessor


@pytest.fixture
def image_processor():
    return ImageProcessor()

@pytest.fixture
def test_image(tmp_path):
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_path = tmp_path / "test.png"
    img.save(img_path)
    return str(img_path)

def test_open_image(image_processor, test_image):
    assert image_processor.open_image(test_image) is True
    assert image_processor.get_current_image() is not None

def test_open_nonexistent_image(image_processor):
    with pytest.raises(FileNotFoundError):
        image_processor.open_image("nonexistent.png")

def test_apply_blur(image_processor, test_image):
    image_processor.open_image(test_image)
    region = (10, 10, 50, 50)
    assert image_processor.apply_blur(region, 5.0) is True

def test_apply_blur_invalid_region(image_processor, test_image):
    image_processor.open_image(test_image)
    region = (200, 200, 300, 300)  # Outside image bounds
    with pytest.raises(ImageProcessingError):
        image_processor.apply_blur(region, 5.0)

def test_apply_blur_negative_radius(image_processor, test_image):
    image_processor.open_image(test_image)
    region = (10, 10, 50, 50)
    with pytest.raises(ValueError):
        image_processor.apply_blur(region, -5.0)

def test_save_image(image_processor, test_image, tmp_path):
    image_processor.open_image(test_image)
    output_path = str(tmp_path / "output.png")
    assert image_processor.save_image(output_path) is True
    assert os.path.exists(output_path)

def test_reset_to_original(image_processor, test_image):
    image_processor.open_image(test_image)
    original = image_processor.get_current_image()

    # Apply some changes
    region = (10, 10, 50, 50)
    image_processor.apply_blur(region, 5.0)

    # Reset and verify
    assert image_processor.reset_to_original() is True
    reset_image = image_processor.get_current_image()
    assert reset_image.size == original.size
    reset_image = image_processor.get_current_image()
    assert reset_image.size == original.size