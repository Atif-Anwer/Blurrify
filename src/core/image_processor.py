import os
from typing import Optional, Tuple

import PIL.Image
import PIL.Image as pil_image
import PIL.ImageFilter


class ImageProcessingError(Exception):
    """Custom exception for image processing failures."""
    pass

class ImageProcessor:
    def __init__(self):
        self._current_image: Optional[PIL.Image.Image] = None
        self._file_path: Optional[str] = None
        self._original_image: Optional[PIL.Image.Image] = None

    def open_image(self, file_path: str) -> bool:
        """Opens an image file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")

        try:
            img = PIL.Image.open(file_path)
            # Convert to RGBA for consistency
            img = img.convert('RGBA')
            self._current_image = img
            self._file_path = file_path
            self._original_image = self._current_image.copy()
            return True
        except PIL.UnidentifiedImageError:
            raise ImageProcessingError(f"Cannot identify image file: {file_path}")
        except Exception as e:
            raise ImageProcessingError(f"An unexpected error occurred opening {file_path}: {e}")

    def get_current_image(self) -> Optional[PIL.Image.Image]:
        """Returns a copy of the current image."""
        return self._current_image.copy() if self._current_image else None

    def _validate_region(self, region: Tuple[int, int, int, int]) -> bool:
        """Helper to validate region coordinates against current image bounds."""
        if self._current_image is None:
            raise ImageProcessingError("No image loaded")

        img_width, img_height = self._current_image.size
        left, upper, right, lower = region

        if not (0 <= left < img_width and 0 <= upper < img_height and
                0 < right <= img_width and 0 < lower <= img_height and
                left < right and upper < lower):
            raise ImageProcessingError(
                f"Invalid region coordinates {region} for image size ({img_width}, {img_height})"
            )
        return True

    def apply_blur(self, region: Tuple[int, int, int, int], radius: float) -> bool:
        """Applies Gaussian blur to a specific region."""
        if not self._validate_region(region):
            return False

        if radius < 0:
            raise ValueError("Blur radius cannot be negative")

        try:
            working_img = self._current_image.copy() # type: ignore
            sub_region = working_img.crop(region)
            blurred_sub_region = sub_region.filter(PIL.ImageFilter.GaussianBlur(radius))
            working_img.paste(blurred_sub_region, region)
            self._current_image = working_img
            return True
        except Exception as e:
            raise ImageProcessingError(f"Error applying blur: {e}")

    def apply_crop(self, region: Tuple[int, int, int, int]) -> bool:
        """Crops the image to the specified region."""
        if self._current_image is None:
            raise ImageProcessingError("No image loaded")

        img_width, img_height = self._current_image.size
        left, upper, right, lower = region

        if not (0 <= left < right <= img_width and 0 <= upper < lower <= img_height):
            raise ImageProcessingError(
                f"Invalid crop region coordinates {region} for image size ({img_width}, {img_height})"
            )

        try:
            self._current_image = self._current_image.crop(region)
            return True
        except Exception as e:
            raise ImageProcessingError(f"Error applying crop: {e}")

    def save_image(self, file_path: str, format: Optional[str] = None) -> bool:
        """Saves the current image to a file."""
        if self._current_image is None:
            raise ImageProcessingError("No image to save")

        try:
            self._current_image.save(file_path, format=format)
            return True
        except Exception as e:
            raise ImageProcessingError(f"Error saving file {file_path}: {e}")

    def reset_to_original(self) -> bool:
        """Resets the current image to its original state."""
        if self._original_image is None:
            raise ImageProcessingError("No original image available")

        self._current_image = self._original_image.copy()
        return True

    def pixelate_region(self, region: Tuple[int, int, int, int], pixel_size: int) -> bool:
        """Pixelates a specific region with the given pixel size."""
        if not self._validate_region(region):
            return False
        if pixel_size <= 1:
            raise ValueError("Pixel size must be greater than 1")
        try:
            working_img = self._current_image.copy()
            sub_region = working_img.crop(region)
            w, h = sub_region.size
            small = sub_region.resize((max(1, w // pixel_size), max(1, h // pixel_size)), resample=PIL.Image.Resampling.NEAREST)
            pixelated = small.resize((w, h), resample=PIL.Image.Resampling.NEAREST)
            working_img.paste(pixelated, region)
            self._current_image = working_img
            return True
        except Exception as e:
            raise ImageProcessingError(f"Error applying pixelation: {e}")