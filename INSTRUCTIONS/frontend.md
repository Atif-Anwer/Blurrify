```markdown
# Frontend Implementation Guide: Python+PIL+PyQt Image Editor

**Version: 1.0**
**Date: June 7, 2025**

This document provides a technical guide for implementing a basic image editing application using Python, the Pillow (PIL) library for image processing, and PyQt for the graphical user interface. The application will allow users to open JPG or PNG files, select a region, and apply basic blurring and cropping operations.

## 1. Component Architecture

The application follows a Model-View-Controller (MVC) or Model-View-Presenter (MVP) pattern loosely, adapted for a desktop GUI application structure.

*   **Main Application (`QApplication`):** The entry point that manages the event loop.
*   **Main Window (`QMainWindow`):** The primary window hosting the UI components. It acts as the orchestrator, holding references to the state, the image display, and processing logic, and connecting signals and slots.
*   **Image Display Widget (Custom `QWidget` or `QLabel`):** Responsible for rendering the current image. Crucially, this widget needs to handle mouse events to allow the user to draw and define a selection rectangle. It will display a `QPixmap` derived from the processed image data.
*   **Control Panel (`QWidget` / Layout):** A dedicated area containing buttons (Open, Blur, Crop, Save), input fields (e.g., for blur radius), and potentially labels or status bars.
*   **Image Processor (Python/Pillow Logic):** A set of functions or a dedicated class containing the image manipulation logic using the Pillow library (opening, saving, applying blur, applying crop based on coordinates). This component operates purely on Pillow `Image` objects and does not interact directly with the UI.
*   **State Management:** Not a separate component class, but rather instance variables within the `MainWindow` or a dedicated `AppState` object holding the current image data, file path, selected region coordinates, etc.

```mermaid
graph TD
    A[QApplication] --> M[MainWindow]
    M --> D[Image Display Widget]
    M --> C[Control Panel]
    M --> P[Image Processor]
    M --> S[State Variables]
    D -- User Input (Selection Rect) --> M
    C -- Button Clicks, Input Values --> M
    M -- Calls Methods --> P
    P -- Returns Image Data --> M
    M -- Updates --> D
    M -- Updates --> S
    S -- Data For --> M, D, P
```

*   **Relationships:**
    *   The `MainWindow` is the central hub, receiving input from the UI (`Image Display`, `Control Panel`) and user actions, updating the `State`, calling methods on the `Image Processor`, and updating the `Image Display`.
    *   The `Image Display Widget` informs the `MainWindow` about the user's selected region.
    *   The `Control Panel` informs the `MainWindow` about requested operations and parameters.
    *   The `Image Processor` performs the core image manipulation logic based on data provided by the `MainWindow` (image data, coordinates, parameters).

## 2. State Management

Effective state management is critical for tracking the current image, operations, and selections. The key pieces of state to manage are:

*   `current_image_path` (str or None): Path to the currently opened file. Useful for saving.
*   `original_pil_image` (Pillow `Image` object or None): The image loaded directly from the file, useful for implementing a "Reset" feature (though not required by the prompt, it's good practice).
*   `processed_pil_image` (Pillow `Image` object or None): The image reflecting the current state after applied operations. This is the image displayed and saved.
*   `current_qpixmap` (PyQt `QPixmap` object or None): The `QPixmap` generated from `processed_pil_image` for display in the UI widget. This is derived state but useful to cache.
*   `selection_rectangle` (`QtCore.QRect` or similar tuple/class, or None): Stores the coordinates of the user-drawn selection rectangle in *widget* coordinates. This will need to be translated to *image* coordinates before applying operations.
*   `image_display_size` (`QtCore.QSize`): The current size the image is being displayed at in the widget. Needed for coordinate translation.
*   `image_original_size` (`QtCore.QSize`): The original dimensions of the loaded image. Needed for coordinate translation.

These state variables should reside within the `MainWindow` class. Methods within `MainWindow` will update these variables based on user actions or processor results. When `processed_pil_image` or `selection_rectangle` changes, the `Image Display Widget` needs to be updated (either by setting a new `QPixmap` or triggering a repaint).

Example State Update Flow (Blur Operation):
1.  User clicks "Blur" button in `Control Panel`.
2.  Signal connected to `MainWindow.apply_blur()` slot is emitted.
3.  `MainWindow.apply_blur()`:
    *   Retrieves `processed_pil_image`, `selection_rectangle`, and blur radius from UI/State.
    *   Translates `selection_rectangle` (widget coords) to image coordinates using `image_display_size` and `image_original_size`.
    *   Calls `ImageProcessor.blur_region(processed_pil_image, image_coords, radius)`.
    *   Updates `self.processed_pil_image` with the result.
    *   Converts the new `processed_pil_image` to a `QPixmap`.
    *   Updates `self.current_qpixmap`.
    *   Instructs the `Image Display Widget` to display the new `QPixmap`.
    *   Clears `self.selection_rectangle`.

## 3. UI Design

The UI should be functional and intuitive for basic image editing.

*   **Layout:** A `QMainWindow` is suitable. Use a central widget, possibly a `QSplitter` or a layout like `QHBoxLayout`. A common arrangement is the `Image Display Widget` on the left/center and the `Control Panel` on the right or below.
*   **Menu Bar:**
    *   `File` Menu:
        *   `Open...`: Opens a file dialog to select `.jpg` or `.png`.
        *   `Save`: Saves the current `processed_pil_image` (if loaded).
        *   `Save As...`: Opens a save file dialog.
        *   `Exit`: Closes the application.
*   **Control Panel:**
    *   `Open Image` Button (alternative to menu).
    *   **Image Operations Group:**
        *   `Blur` Button.
        *   `Blur Radius` Input (e.g., `QSpinBox` or `QLineEdit` for float, with validator).
        *   `Crop` Button.
    *   `Save Image` Button (alternative to menu).
*   **Image Display Widget:**
    *   Needs to display the `QPixmap`. A `QLabel` with `setPixmap` and `setScaledContents(True)` can work for simple display, but a custom `QWidget` is necessary for drawing the selection rectangle and handling mouse events.
    *   The custom widget should override `paintEvent` to draw the current image and the selection rectangle (if one exists).
    *   It must override mouse events (`mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`) to track the user's drag for defining the selection rectangle. Store the start and end points.
    *   Visual feedback: Draw the selection rectangle (e.g., dashed line, semi-transparent overlay) during and after dragging.
*   **Status Bar:** (Optional) Display file path, image dimensions, or status messages (e.g., "Image loaded," "Applying blur...").

**User Interaction Flow (Selection):**
1.  User clicks and holds mouse button on the `Image Display Widget`.
2.  `mousePressEvent` records the start point.
3.  User drags the mouse. `mouseMoveEvent` updates the current rectangle dimensions. The widget repaints, drawing the rectangle based on start and current points.
4.  User releases mouse button. `mouseReleaseEvent` records the end point and stores the final `selection_rectangle` in the state. The widget repaints, drawing the final rectangle.

## 4. API Integration

For this specific project, which is a standalone desktop application, there is no external backend API integration in the traditional sense (e.g., connecting to a web service).

The "API Integration" aspect here refers to the integration of the **Pillow library** (the image processing "API") into the PyQt frontend. The `MainWindow` and potentially a dedicated `ImageProcessor` class will call Pillow functions directly on `PIL.Image` objects.

*   **Integration Mechanism:** Direct method calls. The `MainWindow` object will hold the `processed_pil_image` (a `PIL.Image` instance) and pass it to methods in the `ImageProcessor` (or methods within `MainWindow` itself) along with operation parameters (region coordinates, radius).
*   **Data Flow:**
    *   Load: File Path (str) -> `PIL.Image` (Processor) -> `PIL.Image` (State) -> `QPixmap` (MainWindow) -> Display Widget.
    *   Operation: `PIL.Image` (State) + Selection Coords + Params -> `PIL.Image` (Processor) -> Updated `PIL.Image` (State) -> `QPixmap` (MainWindow) -> Display Widget.
    *   Save: `PIL.Image` (State) + File Path (str) -> Processor.

If this application were to evolve to handle very large images, perform complex operations, or require shared processing capabilities, a separate backend service (local or remote) communicating via a network API (e.g., REST, gRPC) would be considered. However, for the stated requirements and technology stack, direct library integration is the appropriate approach.

## 5. Testing Approach

A multi-faceted testing strategy is recommended to ensure the application is robust and functions correctly.

*   **Unit Tests:**
    *   Focus: Test the image processing logic in isolation.
    *   What to test:
        *   Functions that convert widget coordinates to image coordinates and vice versa.
        *   Functions that apply blur to a small, known PIL image region with a specific radius, checking pixel values.
        *   Functions that apply crop to a small, known PIL image with specific coordinates, checking dimensions and content.
        *   File loading/saving logic (mocking file system interactions if necessary, or using temporary files).
    *   Frameworks: `unittest` (Python's built-in) or `pytest`.
    *   How: Create small `PIL.Image` objects programmatically for test inputs.

*   **Integration Tests:**
    *   Focus: Test the interaction between the UI components and the image processing logic.
    *   What to test:
        *   Clicking "Open" button correctly triggers the file dialog and loads an image.
        *   Drawing a selection rectangle correctly updates the internal state (`selection_rectangle`).
        *   Clicking "Blur" with a selection and radius correctly calls the processing logic and updates the displayed image.
        *   Clicking "Crop" with a selection correctly calls the processing logic and updates the displayed image.
        *   Clicking "Save" saves the *current* processed image state.
    *   Challenges: Testing GUI interactions programmatically can be complex. Can sometimes test signals/slots connections directly or use tools like `QTest` (part of PyQt/Qt) to simulate events, or rely more heavily on manual testing for UI flow.

*   **Manual Testing:**
    *   Focus: End-to-end user experience, visual correctness, and edge cases.
    *   What to test:
        *   Open various JPG/PNG files (different sizes, color types).
        *   Draw selection rectangles of different sizes and positions (small, large, edge of image).
        *   Test Blur with different radii on selected regions.
        *   Test Crop on selected regions.
        *   Test applying multiple operations sequentially (e.g., blur then crop, or crop then blur).
        *   Test selecting a region *after* an operation has changed the image size (e.g., after cropping).
        *   Test saving the processed image in different formats.
        *   Test error conditions (e.g., trying to operate without an image loaded, invalid radius input, closing file dialogs).
        *   Test resizing the main window.
    *   How: Run the application and use it as an end-user would.

*   **Packaging Tests:**
    *   Focus: Ensure the packaged application runs correctly in the target environment.
    *   What to test:
        *   Run the `PyInstaller` generated `.exe` on a clean Windows machine (or VM) that doesn't have Python/PyQt/Pillow installed.
        *   Ensure all features (open, process, save) work within the packaged application.
        *   Run the Python script on a Linux environment to ensure standard execution works.

## 6. Code Examples

These examples provide snippets for key functionalities.

### 6.1 Setup and Basic Window Structure

Install necessary libraries:
```bash
pip install PyQt6 Pillow
```

Basic `main.py` and `main_window.py`:

`main.py`:
```python
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
```

`main_window.py`: (Basic structure, requires implementing methods)
```python
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel,
                             QFileDialog, QPushButton, QHBoxLayout, QDoubleSpinBox,
                             QInputDialog, QMessageBox, QSizePolicy)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QRect, QSize, QPoint, QBuffer, QIODevice

from PIL import Image # Use Pillow
import io # For converting PIL Image to bytes for QPixmap

# Assuming you might put processing logic here or in a separate file
# import image_processor # if using a separate module

class ImageDisplayWidget(QLabel): # Using QLabel for simplicity here,
                                   # custom QWidget better for complex drawing/scaling
    selection_changed = Qt.pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(1, 1) # Allow scaling down
        self.setScaledContents(True) # Scale pixmap to label size
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._selection_start = None
        self._selection_end = None
        self._current_selection = None # QRect in widget coordinates

    def set_pixmap(self, pixmap):
        """Sets the pixmap to display and clears selection."""
        super().setPixmap(pixmap)
        self._selection_start = None
        self._selection_end = None
        self._current_selection = None
        self.update() # Redraw

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap():
            self._selection_start = event.pos()
            self._selection_end = event.pos()
            self._current_selection = QRect(self._selection_start, self._selection_end).normalized()
            self.update() # Trigger repaint

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.pixmap():
            self._selection_end = event.pos()
            self._current_selection = QRect(self._selection_start, self._selection_end).normalized()
            self.update() # Trigger repaint

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap():
            self._selection_end = event.pos()
            self._current_selection = QRect(self._selection_start, self._selection_end).normalized()
            self.selection_changed.emit(self._current_selection)
            self.update() # Trigger repaint

    def paintEvent(self, event):
        """Draws the pixmap and the selection rectangle."""
        super().paintEvent(event) # Draw the pixmap

        if self.pixmap() and self._current_selection is not None:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine)) # Dashed red line
            painter.drawRect(self._current_selection)

    def clear_selection(self):
        """Clears the current selection rectangle."""
        self._selection_start = None
        self._selection_end = None
        self._current_selection = None
        self.update()

    def get_selection_image_coords(self):
        """Translates widget selection coords to image coords."""
        if self.pixmap() is None or self._current_selection is None:
            return None

        pixmap_size = self.pixmap().size()
        widget_size = self.size() # Size the pixmap is scaled TO

        # Handle case where pixmap is smaller than widget and not scaled up
        # (although setScaledContents(True) handles this by scaling UP)
        # If setScaledContents(False) was used and aligned, would need to calc offset.
        # With setScaledContents(True), we assume the pixmap fills the widget size
        # (or is scaled to fit maintaining aspect ratio - QLabel does this)
        # We need to map the widget coords to the original image coords.

        # The scaling factor for width and height might be different if setScaledContents(True)
        # stretches. QLabel with setScaledContents(True) *usually* maintains aspect ratio
        # unless sizePolicy is ignored or layout forces stretching. Let's assume
        # it maintains aspect ratio and fills either width or height.

        image_width = self.pixmap().width()
        image_height = self.pixmap().height()
        widget_width = widget_size.width()
        widget_height = widget_size.height()

        # Calculate the actual scale factor QLabel used
        # If width limited: widget_width = image_width * scale, widget_height = image_height * scale
        # If height limited: widget_height = image_height * scale, widget_width = image_width * scale
        # QLabel scales to fit while maintaining aspect ratio.
        # The actual displayed image might be centered if aspect ratios don't match.
        # This makes mapping non-trivial with just QLabel and setScaledContents(True).

        # A more robust approach requires calculating the actual rendered image rectangle within the QLabel.
        # For simplicity *in this example*, let's assume the scaling is proportional and fills the widget,
        # and adjust based on the _current_ pixmap size after scaling (not original image size).
        # **NOTE:** This is an approximation and breaks if aspect ratio scaling happens.
        # A custom QWidget with manual paint and aspect ratio calculation is needed for precision.
        # Let's use the _current_ pixmap size *as displayed* via self.pixmap().size() *after* scaling,
        # which with setScaledContents(True) is the size of the QLabel itself.
        # This is WRONG if maintaining aspect ratio introduces padding.

        # Let's attempt a more correct mapping assuming aspect ratio is maintained and image is centered.
        # This is complex. A custom widget that manages scaling and drawing is needed.
        # Example using QTransform might be better, but adds complexity.
        # Let's simplify for the guide and use the ratio of widget size to original image size.
        # This requires storing the original image size separately.

        # For this basic guide, let's use a simpler (potentially less precise if aspect ratio differs)
        # approach based on the ratio of the widget size to the *current* scaled pixmap size.
        # This is still not fully correct for aspect ratio scaling.
        # A better approach: Store the original PIL image size, calculate the scale factor used by QLabel.
        # QLabel's scaling is tricky to map back precisely without custom painting.

        # Let's use the original image dimensions and calculate the scale factor.
        # Assume original_image_size is passed or accessible.
        # For this snippet, assume the original PIL image size is stored in the parent MainWindow
        # and accessible via self.parent().original_image_size (or similar).

        original_image_size = self.parent().get_original_image_size() # Need method in MainWindow

        if not original_image_size or original_image_size.isEmpty():
             print("Warning: Original image size not available for coordinate mapping.")
             return None

        img_w, img_h = original_image_size.width(), original_image_size.height()
        widget_w, widget_h = widget_size.width(), widget_size.height()

        # Calculate effective scale factor used by QLabel keeping aspect ratio
        # QLabel fits the largest dimension, scaling the other proportionally
        width_ratio = widget_w / img_w if img_w > 0 else 0
        height_ratio = widget_h / img_h if img_h > 0 else 0

        # QLabel uses the smaller ratio to ensure the whole image fits
        scale_factor = min(width_ratio, height_ratio) if img_w > 0 and img_h > 0 else 0

        if scale_factor == 0:
            return None

        # Calculate the size of the image as displayed *within* the QLabel
        displayed_width = img_w * scale_factor
        displayed_height = img_h * scale_factor

        # Calculate padding if the image is centered
        padding_x = (widget_w - displayed_width) / 2
        padding_y = (widget_h - displayed_height) / 2

        # Map widget coordinates back to image coordinates
        img_x1 = int((self._current_selection.left() - padding_x) / scale_factor)
        img_y1 = int((self._current_selection.top() - padding_y) / scale_factor)
        img_x2 = int((self._current_selection.right() - padding_x) / scale_factor)
        img_y2 = int((self._current_selection.bottom() - padding_y) / scale_factor)

        # Ensure coordinates are within image bounds
        img_x1 = max(0, min(img_x1, img_w))
        img_y1 = max(0, min(img_y1, img_h))
        img_x2 = max(0, min(img_x2, img_w))
        img_y2 = max(0, min(img_y2, img_h))

        # Return as (left, upper, right, lower) tuple expected by PIL
        return (img_x1, img_y1, img_x2, img_y2)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Image Editor")
        self.setGeometry(100, 100, 800, 600)

        self.current_image_path = None
        self.original_pil_image = None # Store original for potential reset
        self.processed_pil_image = None # Store current state

        # --- UI Elements ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Image Display Area
        self.image_display = ImageDisplayWidget(self) # Use the custom widget
        main_layout.addWidget(self.image_display, 1) # Stretch factor 1

        # Control Panel Area
        control_layout = QVBoxLayout()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # File Operations
        btn_open = QPushButton("Open Image")
        btn_open.clicked.connect(self.open_image)
        control_layout.addWidget(btn_open)

        btn_save = QPushButton("Save Image")
        btn_save.clicked.connect(self.save_image)
        btn_save.setEnabled(False) # Disable until image loaded
        self.btn_save = btn_save # Keep reference
        control_layout.addWidget(btn_save)

        control_layout.addSpacing(20)

        # Operations Group
        operation_label = QLabel("Operations (requires selection):")
        control_layout.addWidget(operation_label)

        # Blur
        blur_layout = QHBoxLayout()
        btn_blur = QPushButton("Apply Blur")
        btn_blur.clicked.connect(self.apply_blur)
        btn_blur.setEnabled(False)
        self.btn_blur = btn_blur
        blur_layout.addWidget(btn_blur)

        blur_radius_label = QLabel("Radius:")
        blur_layout.addWidget(blur_radius_label)
        self.blur_radius_input = QDoubleSpinBox()
        self.blur_radius_input.setMinimum(0.1)
        self.blur_radius_input.setValue(5.0)
        self.blur_radius_input.setSingleStep(0.5)
        blur_layout.addWidget(self.blur_radius_input)
        control_layout.addLayout(blur_layout)

        # Crop
        btn_crop = QPushButton("Apply Crop")
        btn_crop.clicked.connect(self.apply_crop)
        btn_crop.setEnabled(False)
        self.btn_crop = btn_crop
        control_layout.addWidget(btn_crop)

        control_layout.addStretch(1) # Push controls to top

        main_layout.addLayout(control_layout, 0) # Stretch factor 0 (fixed size)

        # Connect selection signal from image display
        self.image_display.selection_changed.connect(self.on_selection_changed)

        self._update_button_states() # Initial state

    def get_original_image_size(self):
        """Helper to get original image size for coordinate mapping."""
        if self.original_pil_image:
            return QSize(self.original_pil_image.width, self.original_pil_image.height)
        return QSize(0, 0)


    def _update_button_states(self):
        """Enables/Disables buttons based on current state."""
        has_image = self.processed_pil_image is not None
        has_selection = self.image_display._current_selection is not None and not self.image_display._current_selection.isEmpty()

        self.btn_save.setEnabled(has_image)
        self.btn_blur.setEnabled(has_image and has_selection)
        self.btn_crop.setEnabled(has_image and has_selection)

    def on_selection_changed(self, selection_rect):
        """Slot called when selection rectangle changes."""
        print(f"Selection changed: {selection_rect}")
        self._update_button_states() # Update button states based on selection

    def open_image(self):
        """Opens a file dialog and loads the selected image."""
        file_filter = "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", file_filter)

        if filepath:
            try:
                pil_image = Image.open(filepath)
                # Ensure image is in a format PyQt can handle (e.g., RGB or RGBA)
                if pil_image.mode not in ("RGB", "RGBA"):
                     pil_image = pil_image.convert("RGB") # Or RGBA if transparency needed

                self.original_pil_image = pil_image.copy() # Keep original
                self.processed_pil_image = pil_image.copy() # Working copy
                self.current_image_path = filepath

                self._display_image(self.processed_pil_image)
                self.image_display.clear_selection() # Clear previous selection
                self._update_button_states()
                print(f"Opened: {filepath}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open image: {e}")
                self.processed_pil_image = None
                self.original_pil_image = None
                self.current_image_path = None
                self._display_image(None)
                self.image_display.clear_selection()
                self._update_button_states()


    def _display_image(self, pil_image):
        """Converts a PIL image to QPixmap and displays it."""
        if pil_image is None:
            self.image_display.set_pixmap(QPixmap()) # Clear pixmap
            return

        # Convert PIL image to QImage
        # Use a BytesIO buffer to save the PIL image to a byte stream
        # Then load that byte stream into a QPixmap
        byte_array = io.BytesIO()
        # Save in a format Pillow and Qt can read (PNG is lossless and supports alpha if needed)
        pil_image.save(byte_array, format='PNG')
        byte_array.seek(0) # Rewind the buffer

        # Load bytes into QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(byte_array.read())

        self.image_display.set_pixmap(pixmap)


    def save_image(self):
        """Saves the current processed image."""
        if self.processed_pil_image is None:
            return

        # Suggest a default filename based on the opened file path
        suggested_filepath = self.current_image_path
        if suggested_filepath and "." in suggested_filepath:
            name, ext = os.path.splitext(suggested_filepath)
            suggested_filepath = f"{name}_edited{ext}"
        else:
            suggested_filepath = "edited_image.png" # Default if no path

        file_filter = "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*)"
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Image File", suggested_filepath, file_filter)

        if filepath:
            try:
                # Determine format from extension
                if filepath.lower().endswith('.png'):
                    img_format = 'PNG'
                elif filepath.lower().endswith(('.jpg', '.jpeg')):
                    img_format = 'JPEG'
                    # Handle potential alpha channel if saving as JPEG
                    if self.processed_pil_image.mode == 'RGBA':
                         pil_image_to_save = self.processed_pil_image.convert('RGB')
                    else:
                         pil_image_to_save = self.processed_pil_image
                else:
                    # Default to PNG or show error/warning
                    img_format = 'PNG' # Save as PNG by default for unknown extension
                    filepath += '.png' # Add extension
                    pil_image_to_save = self.processed_pil_image

                pil_image_to_save.save(filepath, format=img_format)
                print(f"Saved: {filepath}")
                QMessageBox.information(self, "Success", "Image saved successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save image: {e}")

    def apply_blur(self):
        """Applies blur to the selected region."""
        if self.processed_pil_image is None:
            QMessageBox.warning(self, "Warning", "No image loaded.")
            return

        selection_coords = self.image_display.get_selection_image_coords()
        if selection_coords is None or QRect(*selection_coords).isEmpty():
             QMessageBox.warning(self, "Warning", "No valid selection made.")
             return

        radius = self.blur_radius_input.value()
        if radius <= 0:
            QMessageBox.warning(self, "Warning", "Blur radius must be greater than 0.")
            return

        try:
            # Create a copy to modify
            img_copy = self.processed_pil_image.copy()
            # Extract the region of interest (ROI)
            roi = img_copy.crop(selection_coords)

            # Apply blur to the ROI
            from PIL import ImageFilter
            blurred_roi = roi.filter(ImageFilter.GaussianBlur(radius))

            # Paste the blurred ROI back into the image copy
            img_copy.paste(blurred_roi, selection_coords)

            self.processed_pil_image = img_copy # Update state
            self._display_image(self.processed_pil_image) # Update display
            self.image_display.clear_selection() # Clear selection after applying
            self._update_button_states()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not apply blur: {e}")


    def apply_crop(self):
        """Crops the image to the selected region."""
        if self.processed_pil_image is None:
            QMessageBox.warning(self, "Warning", "No image loaded.")
            return

        selection_coords = self.image_display.get_selection_image_coords()
        if selection_coords is None or QRect(*selection_coords).isEmpty():
             QMessageBox.warning(self, "Warning", "No valid selection made.")
             return

        try:
            # Crop the image (PIL crop returns a new Image object)
            cropped_image = self.processed_pil_image.crop(selection_coords)

            self.processed_pil_image = cropped_image # Update state
            self._display_image(self.processed_pil_image) # Update display
            self.image_display.clear_selection() # Clear selection after applying
            self._update_button_states()
            print(f"Image cropped to {cropped_image.size}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not apply crop: {e}")

# Note: The coordinate mapping logic in ImageDisplayWidget.get_selection_image_coords
# is simplified and might not be perfectly accurate if QLabel scaling introduces padding
# due to aspect ratio differences. A more advanced custom widget handling painting
# and coordinate transformation manually would be needed for pixel-perfect accuracy.
# However, this provides a functional example for the guide.
```

### 6.2 Image Display and Selection

The `ImageDisplayWidget` class in `main_window.py` demonstrates:
*   Inheriting from `QLabel`.
*   Overriding `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent` to capture drag events.
*   Storing the start and end points of the drag.
*   Using `update()` to trigger `paintEvent`.
*   Overriding `paintEvent` to draw the `QPixmap` and the stored selection rectangle.
*   Emitting a `selection_changed` signal.
*   Includes a function `get_selection_image_coords` to attempt mapping widget coordinates to image coordinates. (See comments in code about its limitations with `QLabel`'s auto-scaling).

### 6.3 Image Processing (Blur and Crop)

The `apply_blur` and `apply_crop` methods in `MainWindow` demonstrate:
*   Retrieving the selection coordinates (converted to image coordinates).
*   Retrieving operation parameters (blur radius).
*   Using Pillow (`PIL.Image`, `PIL.ImageFilter`) to perform the operations on the `processed_pil_image`.
*   Creating a copy (`.copy()`) before modifying to avoid issues if the same image object were referenced elsewhere (though in this simple case, updating the reference is sufficient).
*   Updating the `self.processed_pil_image` state variable.
*   Calling `_display_image` to refresh the UI.
*   Clearing the selection and updating button states after operation.

### 6.4 File Handling (Open and Save)

The `open_image` and `save_image` methods in `MainWindow` demonstrate:
*   Using `QFileDialog` to get file paths.
*   Using `PIL.Image.open()` to load an image.
*   Handling basic image mode conversion (`.convert("RGB")`) for compatibility with PyQt/standard formats.
*   Using `PIL.Image.save()` to save the current image state.
*   Converting `PIL.Image` to `QPixmap` for display using `io.BytesIO` and `QPixmap.loadFromData`.
*   Handling potential errors with `try...except` and `QMessageBox`.

## 7. Packaging for Deployment

*   **Windows (.exe):** `PyInstaller` is the standard tool.
    1.  Install: `pip install pyinstaller`
    2.  Navigate to your project directory in the command line.
    3.  Run PyInstaller: `pyinstaller --onefile --windowed main.py`
        *   `--onefile`: Creates a single executable file.
        *   `--windowed` or `-w`: Prevents a console window from opening alongside the GUI.
    4.  The executable will be found in the `dist` folder.
    5.  *Note:* PyInstaller usually handles PyQt and Pillow dependencies well automatically. If you encounter issues (e.g., missing DLLs), you might need to use hooks or manually include files, but this is uncommon for standard PyQt/Pillow usage.

*   **Linux (Python Script):** No special packaging is required beyond ensuring the target machine has Python installed and the necessary libraries (`PyQt6`, `Pillow`) are installed in the environment where the script is run.
    1.  Ensure the script has execute permissions: `chmod +x main.py`
    2.  Ensure the first line is a shebang pointing to the python interpreter: `#!/usr/bin/env python3`
    3.  Run from the terminal: `./main.py`

Remember to include all necessary `.py` files (`main.py`, `main_window.py`, potentially `image_processor.py` if separated) in the project directory when packaging or running the script.

This guide provides a foundation for building the image editor application. Further enhancements could include more operations, undo/redo functionality, better handling of large images, and more sophisticated UI elements.
```
