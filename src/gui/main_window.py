import sys
from pathlib import Path

from PyQt6.QtCore import QRect, Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
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
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Blurrify - Image Processor')
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create image viewer
        self.image_viewer = ImageViewer()
        layout.addWidget(self.image_viewer)

        # Create controls
        controls_layout = QHBoxLayout()

        # File operations
        self.open_button = QPushButton('Open Image')
        self.open_button.clicked.connect(self.open_image)
        controls_layout.addWidget(self.open_button)

        self.save_button = QPushButton('Save Image')
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        controls_layout.addWidget(self.save_button)

        # Blur controls
        self.blur_radius = QDoubleSpinBox()
        self.blur_radius.setRange(0, 100)
        self.blur_radius.setValue(5.0)
        self.blur_radius.setSingleStep(0.5)
        controls_layout.addWidget(QLabel('Blur Radius:'))
        controls_layout.addWidget(self.blur_radius)

        self.apply_blur_button = QPushButton('Apply Blur')
        self.apply_blur_button.clicked.connect(self.apply_blur)
        self.apply_blur_button.setEnabled(False)
        controls_layout.addWidget(self.apply_blur_button)

        # Reset button
        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_image)
        self.reset_button.setEnabled(False)
        controls_layout.addWidget(self.reset_button)

        layout.addLayout(controls_layout)

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
                    self.apply_blur_button.setEnabled(True)
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

    def apply_blur(self):
        selection = self.image_viewer.get_selection_rect()
        if selection:
            try:
                region = (
                    selection.x(),
                    selection.y(),
                    selection.x() + selection.width(),
                    selection.y() + selection.height()
                )
                if self.image_processor.apply_blur(region, self.blur_radius.value()):
                    self.image_viewer.set_image(self.image_processor.get_current_image())
            except ImageProcessingError as e:
                QMessageBox.critical(self, "Error", str(e))
        else:
            QMessageBox.warning(self, "Warning", "Please select a region first!")

    def reset_image(self):
        try:
            if self.image_processor.reset_to_original():
                self.image_viewer.set_image(self.image_processor.get_current_image())
        except ImageProcessingError as e:
            QMessageBox.critical(self, "Error", str(e))