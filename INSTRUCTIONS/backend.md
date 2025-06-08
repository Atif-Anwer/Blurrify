Okay, here is a backend implementation plan for your Python+PIL+PyQt desktop image processing application, structured as requested.

```markdown
# Backend Implementation Guide: Simple Image Processor

## 1. Document Header
*   **Version:** 1.0
*   **Date:** June 7, 2025

## 2. API Design

In the context of a standalone desktop application using Python and PyQt, "API Design" refers to the *interface between the graphical user interface (GUI) layer and the core image processing logic*. This isn't a traditional web API with endpoints, but rather a set of well-defined functions and methods that the GUI calls to perform operations, and potentially signals or return values that the core logic uses to communicate back to the GUI (e.g., operation complete, error, progress).

The core image processing logic will be encapsulated in a class (e.g., `ImageProcessor`) which the GUI controller or main window object interacts with.

**Key Interfaces/Methods:**

*   **`ImageProcessor.open_image(file_path: str) -> bool`**
    *   **Description:** Attempts to open an image file.
    *   **Parameters:** `file_path` (string) - The full path to the JPG or PNG file.
    *   **Returns:** `bool` - `True` if successful, `False` otherwise (e.g., file not found, invalid format).
    *   **Side Effects:** Loads the image into an internal data structure (PIL Image object).
*   **`ImageProcessor.get_current_image() -> PIL.Image.Image`**
    *   **Description:** Returns the current state of the image being processed. This might be a copy to prevent direct modification by the GUI layer.
    *   **Parameters:** None.
    *   **Returns:** `PIL.Image.Image` object or `None` if no image is loaded.
*   **`ImageProcessor.apply_blur(region: tuple[int, int, int, int], radius: float) -> bool`**
    *   **Description:** Applies a Gaussian blur to a specified rectangular region of the current image.
    *   **Parameters:**
        *   `region` (tuple[int, int, int, int]) - Bounding box defining the region `(left, upper, right, lower)`.
        *   `radius` (float) - The blur radius (standard deviation).
    *   **Returns:** `bool` - `True` if successful, `False` if region is invalid or no image is loaded.
    *   **Side Effects:** Modifies the internal image data structure.
*   **`ImageProcessor.apply_crop(region: tuple[int, int, int, int]) -> bool`**
    *   **Description:** Crops the current image to the specified rectangular region.
    *   **Parameters:** `region` (tuple[int, int, int, int]) - Bounding box defining the region `(left, upper, right, lower)`.
    *   **Returns:** `bool` - `True` if successful, `False` if region is invalid or no image is loaded.
    *   **Side Effects:** Replaces the internal image data structure with the cropped image.
*   **`ImageProcessor.save_image(file_path: str, format: str = None) -> bool`**
    *   **Description:** Saves the current image to a file.
    *   **Parameters:**
        *   `file_path` (string) - The path to save the file.
        *   `format` (string, optional) - The image format (e.g., 'JPEG', 'PNG'). If None, PIL attempts to guess from file extension.
    *   **Returns:** `bool` - `True` if successful, `False` otherwise.
    *   **Side Effects:** Writes data to the filesystem.

**Error Handling:**
*   Methods should return `False` or raise specific exceptions (e.g., `FileNotFoundError`, `ValueError` for invalid parameters, `ProcessingError`) that the GUI layer can catch and report to the user.

## 3. Data Models

Since this is a desktop application without a persistent backend database server, the "Data Models" refer to the primary in-memory data structures managed by the core image processing logic.

*   **`CurrentImageData`:**
    *   Represents the image currently loaded and being processed.
    *   **Fields:**
        *   `pil_image`: Stores the actual image data using a `PIL.Image.Image` object. This is the central piece of data.
        *   `file_path`: Stores the string path of the file the image was loaded from (optional, useful for saving).
        *   `original_pil_image`: (Optional, for undo/revert) A copy of the image when it was first loaded.
*   **`RegionCoordinates`:**
    *   Represents the selected area for operations like blurring or cropping.
    *   **Fields:**
        *   `left`: Integer, x-coordinate of the top-left corner.
        *   `upper`: Integer, y-coordinate of the top-left corner.
        *   `right`: Integer, x-coordinate of the bottom-right corner.
        *   `lower`: Integer, y-coordinate of the bottom-right corner.
    *   **Format:** Stored internally as a tuple `(left, upper, right, lower)` as used by PIL.

## 4. Business Logic

The core business logic resides within the `ImageProcessor` class methods, orchestrating PIL operations based on requests from the GUI.

**Core Processes:**

1.  **Initialization:**
    *   The `ImageProcessor` object is created. It initializes `pil_image` to `None`.
2.  **Loading an Image (`open_image`):**
    *   Takes a file path as input.
    *   Uses `PIL.Image.open(file_path)` to load the image.
    *   Includes error handling for `FileNotFoundError` and `PIL.UnidentifiedImageError`.
    *   Stores the resulting `PIL.Image.Image` object in `self.pil_image`.
    *   (Optional) Converts image to a consistent mode (e.g., 'RGB' or 'RGBA') to avoid issues with different color palettes or modes in subsequent processing. `img = img.convert('RGBA')`
    *   Stores the `file_path`.
    *   (Optional) Creates and stores a copy of the original image for potential 'revert' functionality.
3.  **Applying Blur (`apply_blur`):**
    *   Takes the `region` tuple and `radius` float.
    *   Validates:
        *   An image is currently loaded (`self.pil_image` is not None).
        *   The `region` coordinates are valid (left < right, upper < lower).
        *   The `region` is within the bounds of the current image dimensions.
        *   `radius` is non-negative.
    *   Creates a working copy of the current image to modify (`working_img = self.pil_image.copy()`). This is important so the original image data is not partially updated if the operation fails or is cancelled (though for a simple app, modifying in place might be acceptable if you don't need complex undo).
    *   Extracts the sub-region to blur: `sub_region = working_img.crop(region)`.
    *   Applies the blur filter to the sub-region: `blurred_sub_region = sub_region.filter(PIL.ImageFilter.GaussianBlur(radius))`.
    *   Pastes the blurred sub-region back onto the working copy: `working_img.paste(blurred_sub_region, region)`.
    *   Updates the `self.pil_image` to the `working_img`.
    *   (For UI responsiveness) For large images or complex filters, this operation might be moved to a separate thread.
4.  **Applying Crop (`apply_crop`):**
    *   Takes the `region` tuple.
    *   Validates:
        *   An image is currently loaded.
        *   The `region` coordinates are valid (left < right, upper < lower).
        *   The `region` is within or equal to the bounds of the current image dimensions.
    *   Applies the crop operation: `cropped_img = self.pil_image.crop(region)`.
    *   Updates the `self.pil_image` to the `cropped_img`.
5.  **Saving an Image (`save_image`):**
    *   Takes a `file_path` and optional `format`.
    *   Validates that an image is loaded.
    *   Uses `self.pil_image.save(file_path, format=format)` to save.
    *   Includes error handling for write permissions, disk full, invalid format, etc.

## 5. Security

For a standalone desktop application, security concerns are primarily focused on robust input handling and safe file operations within the user's local environment, rather than typical server-side authentication/authorization.

*   **Input Validation:**
    *   All parameters passed to image processing functions (`file_path`, `region` coordinates, `radius`) must be validated before use.
    *   File paths should be checked for existence and read permissions before attempting to open.
    *   Image format validation is handled by PIL's `open`, but error handling (`try...except PIL.UnidentifiedImageError`) is necessary.
    *   Region coordinates must be checked to ensure they are within image bounds and define a valid rectangle (e.g., `left <= right`, `upper <= lower`, and coordinates are non-negative).
    *   Blur radius should be checked to be non-negative.
*   **File Handling:**
    *   Use standard Python file I/O and PIL's methods, which are generally safe.
    *   Avoid executing any external commands based on file contents or names.
    *   When saving, rely on standard save dialogs (provided by PyQt) which handle permissions and overwriting confirmations at the OS level. The application code should only write to the path provided by the save dialog.
*   **Permissions:**
    *   The application runs with the permissions of the logged-in user. It does not require elevated privileges beyond typical user access to directories and files. There's no separate user authentication within the app itself.
*   **Code Injection:**
    *   Ensure no user input is ever treated as executable code (e.g., using `eval()`). File paths and parameters should only be used as data.

## 6. Performance

Performance is critical for image processing applications, especially when dealing with large images.

*   **Lazy Loading:** `PIL.Image.open()` is generally lazy and doesn't read the pixel data until needed. Processing operations, however, require the full data.
*   **Efficient PIL Operations:** PIL is a relatively optimized library for image manipulation in Python. Using its built-in methods (`crop`, `filter`, `paste`) is generally efficient.
*   **Threading for Responsiveness:** Image processing operations (especially blur on large images/regions) can be time-consuming and block the GUI thread, making the application unresponsive.
    *   Implement time-consuming operations (like `apply_blur`, potentially `save_image` for very large files) to run in a separate thread (e.g., using `QThread` in PyQt or Python's `concurrent.futures.ThreadPoolExecutor`).
    *   Use PyQt's signal/slot mechanism to communicate progress, completion, or errors back from the worker thread to the GUI thread.
*   **Avoid Unnecessary Copies:** While copying the image for operations can simplify state management (`apply_blur` strategy above), be mindful of memory usage with very large images. If memory becomes an issue, consider processing blocks or optimizing the state management. However, for typical desktop use, a copy is often acceptable and safer.
*   **Optimized Display:** Displaying very large images directly in a GUI widget can be slow. The GUI layer should handle scaling the image down for display purposes without affecting the underlying image data managed by the `ImageProcessor`. When selecting regions, use the scaled coordinates and convert them back to original image coordinates before passing to `ImageProcessor` methods.

## 7. Code Examples

Here are simplified Python code examples illustrating the core image processing logic using PIL. These would be methods within the `ImageProcessor` class.

```python
import PIL.Image
import PIL.ImageFilter
import os

class ImageProcessingError(Exception):
    """Custom exception for image processing failures."""
    pass

class ImageProcessor:
    def __init__(self):
        self._current_image = None
        self._file_path = None
        # Optional: self._original_image = None

    def open_image(self, file_path: str) -> bool:
        """Opens an image file."""
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return False
        
        try:
            img = PIL.Image.open(file_path)
            # Optional: Convert to RGBA for consistency if alpha is needed, or RGB
            # img = img.convert('RGBA')
            self._current_image = img
            self._file_path = file_path
            # Optional: self._original_image = self._current_image.copy()
            print(f"Successfully opened image: {file_path}")
            return True
        except FileNotFoundError:
             print(f"Error: File not found at {file_path}")
             return False
        except PIL.UnidentifiedImageError:
            print(f"Error: Cannot identify image file: {file_path}")
            self._current_image = None # Ensure state is clean
            self._file_path = None
            return False
        except Exception as e:
            print(f"An unexpected error occurred opening {file_path}: {e}")
            self._current_image = None
            self._file_path = None
            return False

    def get_current_image(self) -> PIL.Image.Image | None:
        """Returns a copy of the current image."""
        # Return a copy to prevent external modification of the internal state
        return self._current_image.copy() if self._current_image else None

    def _validate_region(self, region: tuple[int, int, int, int]) -> bool:
        """Helper to validate region coordinates against current image bounds."""
        if self._current_image is None:
            print("Validation Error: No image loaded.")
            return False

        img_width, img_height = self._current_image.size
        left, upper, right, lower = region

        if not (0 <= left < img_width and 0 <= upper < img_height and
                0 < right <= img_width and 0 < lower <= img_height and
                left < right and upper < lower):
            print(f"Validation Error: Invalid region coordinates {region} for image size ({img_width}, {img_height}).")
            return False
        return True

    def apply_blur(self, region: tuple[int, int, int, int], radius: float) -> bool:
        """Applies Gaussian blur to a specific region."""
        if not self._validate_region(region):
            return False

        if radius < 0:
            print("Validation Error: Blur radius cannot be negative.")
            return False

        try:
            # Create a copy to modify
            working_img = self._current_image.copy()

            # Extract the region
            x1, y1, x2, y2 = region
            sub_region = working_img.crop((x1, y1, x2, y2))

            # Apply blur to the region
            blurred_sub_region = sub_region.filter(PIL.ImageFilter.GaussianBlur(radius))

            # Paste the blurred region back
            working_img.paste(blurred_sub_region, (x1, y1, x2, y2)) # PIL paste uses upper-left coords

            self._current_image = working_img
            print(f"Applied blur with radius {radius} to region {region}")
            return True
        except Exception as e:
            print(f"Error applying blur: {e}")
            # Optionally, revert to previous state if copy was made at start
            return False

    def apply_crop(self, region: tuple[int, int, int, int]) -> bool:
        """Crops the image to the specified region."""
        # For crop, validation is slightly different: the region must be within or *exactly* the image bounds
        if self._current_image is None:
             print("Validation Error: No image loaded.")
             return False

        img_width, img_height = self._current_image.size
        left, upper, right, lower = region

        if not (0 <= left < right <= img_width and 0 <= upper < lower <= img_height):
             print(f"Validation Error: Invalid crop region coordinates {region} for image size ({img_width}, {img_height}).")
             return False

        try:
            cropped_img = self._current_image.crop(region)
            self._current_image = cropped_img
            print(f"Cropped image to region {region}")
            return True
        except Exception as e:
            print(f"Error applying crop: {e}")
            return False

    def save_image(self, file_path: str, format: str = None) -> bool:
        """Saves the current image to a file."""
        if self._current_image is None:
            print("Error: No image to save.")
            return False

        try:
            # PIL guesses format from extension if format is None
            self._current_image.save(file_path, format=format)
            print(f"Successfully saved image to: {file_path}")
            return True
        except IOError as e:
            print(f"Error saving file {file_path}: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred saving {file_path}: {e}")
            return False

# Example Usage (within the backend logic, called by GUI)
if __name__ == '__main__':
    # This block simulates how the GUI might interact with the ImageProcessor
    processor = ImageProcessor()

    # Create a dummy image file for testing
    try:
        dummy_img = PIL.Image.new('RGB', (200, 150), color = 'red')
        dummy_img_path = 'test_image.png'
        dummy_img.save(dummy_img_path)
        print(f"Created dummy image: {dummy_img_path}")

        # --- Simulate GUI Actions ---

        # 1. Open the dummy image
        if processor.open_image(dummy_img_path):
            img = processor.get_current_image()
            if img:
                print(f"Loaded image size: {img.size}, mode: {img.mode}")
                # img.show() # Uncomment to view image (opens in default viewer)

                # 2. Apply blur to a region
                blur_region = (50, 50, 150, 100) # A 100x50 rectangle
                blur_radius = 5.0
                if processor.apply_blur(blur_region, blur_radius):
                     print("Blur applied.")
                     # processor.get_current_image().show() # Uncomment to view blurred image

                # 3. Apply crop
                crop_region = (25, 25, 175, 125) # A 150x100 rectangle within original bounds
                if processor.apply_crop(crop_region):
                    img_cropped = processor.get_current_image()
                    if img_cropped:
                         print(f"Cropped image size: {img_cropped.size}")
                         # img_cropped.show() # Uncomment to view cropped image
                    else:
                        print("Crop failed, no image available.")
                else:
                    print("Crop operation failed.")


                # 4. Save the processed image
                output_path = 'processed_image.png'
                if processor.save_image(output_path):
                    print(f"Processed image saved to {output_path}")
                else:
                    print("Saving image failed.")
            else:
                 print("Failed to retrieve current image after opening.")
        else:
            print("Failed to open image.")

    finally:
        # Clean up dummy file
        if os.path.exists(dummy_img_path):
            os.remove(dummy_img_path)
            print(f"Cleaned up dummy image: {dummy_img_path}")
        if os.path.exists('processed_image.png'):
             # os.remove('processed_image.png') # Keep processed file for inspection
             print("Kept processed_image.png for review.")

```
```
