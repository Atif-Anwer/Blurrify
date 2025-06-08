import sys
from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.image_processor import ImageProcessingError, ImageProcessor


class ImageViewer(QLabel):
    selection_completed = pyqtSignal(QRect)  # Signal that emits a QRect

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("border: 1px solid #cccccc;")
        self._selection_start = None
        self._selection_end = None
        self._is_selecting = False
        self._current_selection_rect = None  # Store QRect for painting

    def set_image(self, image):
        if image:
            # Ensure image is RGBA
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            width, height = image.size  # PIL: (width, height)
            data = image.tobytes("raw", "RGBA")
            q_image = QImage(data, width, height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(q_image)
            self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.clear()
        self._current_selection_rect = None
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap():
            self._selection_start = event.pos()
            self._selection_end = event.pos()
            self._is_selecting = True
            self._current_selection_rect = QRect(self._selection_start, self._selection_end).normalized()
            self.update()

    def mouseMoveEvent(self, event):
        if self._is_selecting and self.pixmap():
            self._selection_end = event.pos()
            self._current_selection_rect = QRect(self._selection_start, self._selection_end).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap():
            self._is_selecting = False
            self._selection_end = event.pos()
            self._current_selection_rect = QRect(self._selection_start, self._selection_end).normalized()
            if self._selection_start and self._selection_end:
                self.selection_completed.emit(self._current_selection_rect)
            self.update()

    def get_selection_rect(self):
        return self._current_selection_rect

    def get_selection_image_coords(self, image_size):
        """
        Map the selection rectangle from widget coordinates to image coordinates.
        image_size: (width, height) tuple of the original image
        Returns (left, upper, right, lower) in image coordinates, or None if not available.
        """
        rect = self._current_selection_rect
        if rect is None or rect.isNull() or not self.pixmap():
            return None
        img_w, img_h = image_size
        widget_w, widget_h = self.width(), self.height()
        pixmap = self.pixmap()
        pm_w, pm_h = pixmap.width(), pixmap.height()
        # Calculate scale factor and padding (centered image)
        scale = min(widget_w / img_w, widget_h / img_h)
        disp_w, disp_h = img_w * scale, img_h * scale
        pad_x = (widget_w - disp_w) / 2
        pad_y = (widget_h - disp_h) / 2
        # Map widget coords to image coords
        x1 = int((rect.left() - pad_x) / scale)
        y1 = int((rect.top() - pad_y) / scale)
        x2 = int((rect.right() - pad_x) / scale)
        y2 = int((rect.bottom() - pad_y) / scale)
        # Clamp to image bounds
        x1 = max(0, min(x1, img_w-1))
        y1 = max(0, min(y1, img_h-1))
        x2 = max(0, min(x2, img_w))
        y2 = max(0, min(y2, img_h))
        # Ensure left < right, top < bottom
        left, right = sorted([x1, x2])
        top, bottom = sorted([y1, y2])
        if left == right or top == bottom:
            return None
        return (left, top, right, bottom)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._current_selection_rect and not self._current_selection_rect.isNull():
            from PyQt6.QtGui import QColor, QPainter, QPen
            painter = QPainter(self)
            pen = QPen(QColor(255, 0, 0, 180), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(255, 0, 0, 40))  # semi-transparent fill
            painter.drawRect(self._current_selection_rect)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.sidebar_visible = True
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Blurrify - Image Processor')
        self.setMinimumSize(800, 600)

        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)

        # Create two sidebars - expanded and collapsed
        self.expanded_sidebar = self.create_expanded_sidebar()
        self.collapsed_sidebar = self.create_collapsed_sidebar()

        # Initially show expanded sidebar
        self.collapsed_sidebar.hide()

        # Add sidebars and image viewer to main layout
        main_layout.addWidget(self.expanded_sidebar)
        main_layout.addWidget(self.collapsed_sidebar)

        # Image viewer
        self.image_viewer = ImageViewer()
        main_layout.addWidget(self.image_viewer, stretch=1)

        # Animation for expanded sidebar
        self.sidebar_anim = QPropertyAnimation(self.expanded_sidebar, b"maximumWidth")
        self.sidebar_anim.setDuration(250)
        self.sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def create_expanded_sidebar(self):
        sidebar = QWidget()
        sidebar.setMaximumWidth(260)
        layout = QVBoxLayout(sidebar)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)

        # Burger button
        self.burger_button = QPushButton("☰")
        self.burger_button.setFixedSize(32, 32)
        self.burger_button.setStyleSheet("font-size: 22px; border: none; background: none;")
        self.burger_button.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.burger_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # File operations with icons
        self.open_button = QPushButton('Open Image')
        self.open_button.setIcon(QIcon("assets/open.png"))
        self.open_button.clicked.connect(self.open_image)
        layout.addWidget(self.open_button)

        self.save_button = QPushButton('Save Image')
        self.save_button.setIcon(QIcon("assets/save.png"))
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

        # Effect selection
        layout.addWidget(QLabel('Effect:'))
        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["Blur", "Pixelate"])
        self.effect_combo.currentTextChanged.connect(self._on_effect_changed)
        layout.addWidget(self.effect_combo)

        # Blur controls
        layout.addWidget(QLabel('Blur Radius:'))
        self.blur_combo = QComboBox()
        blur_values = [str(i) for i in range(0, 105, 5)]
        self.blur_combo.addItems(blur_values)
        self.blur_combo.setCurrentText("50")
        layout.addWidget(self.blur_combo)

        # Pixelate controls
        layout.addWidget(QLabel('Pixel Size:'))
        self.pixel_combo = QComboBox()
        pixel_values = [str(i) for i in range(5, 105, 5)]
        self.pixel_combo.addItems(pixel_values)
        self.pixel_combo.setCurrentText("50")
        self.pixel_combo.setEnabled(False)
        layout.addWidget(self.pixel_combo)

        # Apply and Reset buttons
        self.apply_button = QPushButton('Apply Effect')
        self.apply_button.setIcon(QIcon("assets/apply.png"))
        self.apply_button.clicked.connect(self.apply_effect)
        self.apply_button.setEnabled(False)
        layout.addWidget(self.apply_button)

        self.reset_button = QPushButton('Reset')
        self.reset_button.setIcon(QIcon("assets/reset.png"))
        self.reset_button.clicked.connect(self.reset_image)
        self.reset_button.setEnabled(False)
        layout.addWidget(self.reset_button)

        layout.addStretch()
        return sidebar

    def create_collapsed_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(60)
        layout = QVBoxLayout(sidebar)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)

        # Burger button (always visible)
        burger = QPushButton("☰")
        burger.setFixedSize(32, 32)
        burger.setStyleSheet("font-size: 22px; border: none; background: none;")
        burger.clicked.connect(self.toggle_sidebar)
        layout.addWidget(burger, alignment=Qt.AlignmentFlag.AlignLeft)

        # Icon-only buttons
        for icon_name, slot, tooltip in [
            ("open.png", self.open_image, "Open Image"),
            ("save.png", self.save_image, "Save Image"),
            ("apply.png", self.apply_effect, "Apply Effect"),
            ("reset.png", self.reset_image, "Reset")
        ]:
            btn = QPushButton()
            btn.setIcon(QIcon(f"assets/{icon_name}"))
            btn.setIconSize(QSize(32, 32))
            btn.setFixedSize(40, 40)
            btn.setToolTip(tooltip)
            btn.clicked.connect(slot)
            btn.setStyleSheet("border: none; background: none;")
            layout.addWidget(btn)

        layout.addStretch()
        return sidebar

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.expanded_sidebar.hide()
            self.collapsed_sidebar.show()
        else:
            self.expanded_sidebar.show()
            self.collapsed_sidebar.hide()
        self.sidebar_visible = not self.sidebar_visible

    def _on_effect_changed(self, effect):
        if effect == "Blur":
            self.blur_combo.setEnabled(True)
            self.pixel_combo.setEnabled(False)
        elif effect == "Pixelate":
            self.blur_combo.setEnabled(False)
            self.pixel_combo.setEnabled(True)

    def apply_effect(self):
        selection = self.image_viewer.get_selection_rect()
        if selection:
            try:
                current_image = self.image_processor.get_current_image()
                if current_image is None:
                    QMessageBox.warning(self, "Warning", "No image loaded!")
                    return
                image_size = current_image.size
                region = self.image_viewer.get_selection_image_coords(image_size)
                if not region:
                    QMessageBox.warning(self, "Warning", "Please select a valid region!")
                    return
                effect = self.effect_combo.currentText()
                if effect == "Blur":
                    radius = int(self.blur_combo.currentText())
                    if self.image_processor.apply_blur(region, radius):
                        self.image_viewer.set_image(self.image_processor.get_current_image())
                elif effect == "Pixelate":
                    pixel_size = int(self.pixel_combo.currentText())
                    if self.image_processor.pixelate_region(region, pixel_size):
                        self.image_viewer.set_image(self.image_processor.get_current_image())
            except ImageProcessingError as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.warning(self, "Warning", "Please select a region first!")

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            str(Path.home()),
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            try:
                if self.image_processor.open_image(file_path):
                    self.image_viewer.set_image(self.image_processor.get_current_image())
                    self.save_button.setEnabled(True)
                    self.apply_button.setEnabled(True)
                    self.reset_button.setEnabled(True)
            except ImageProcessingError as e:
                QMessageBox.critical(self, "Error", str(e))

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            str(Path.home()),
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )
        if file_path:
            try:
                if self.image_processor.save_image(file_path):
                    QMessageBox.information(self, "Success", "Image saved successfully!")
            except ImageProcessingError as e:
                QMessageBox.critical(self, "Error", str(e))

    def reset_image(self):
        try:
            if self.image_processor.reset_to_original():
                self.image_viewer.set_image(self.image_processor.get_current_image())
        except ImageProcessingError as e:
            QMessageBox.critical(self, "Error", str(e))