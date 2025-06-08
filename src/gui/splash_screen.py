import sys

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QLabel, QProgressBar, QSplashScreen, QVBoxLayout, QWidget


class SplashScreen(QSplashScreen):
    finished = pyqtSignal()

    def __init__(self):
        # Create a simple splash screen pixmap
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#282a36"))  # Dracula dark background

        # Paint the splash screen content
        painter = QPainter(pixmap)
        painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        painter.setPen(QColor("#f8f8f2"))  # Dracula foreground
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Blurrify")

        painter.setFont(QFont("Arial", 12))
        painter.setPen(QColor("#6272a4"))  # Dracula comment color
        painter.drawText(50, 250, "Loading Image Processor...")
        painter.end()

        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)

        # Progress simulation
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # Update every 50ms

    def update_progress(self):
        self.progress += 2
        if self.progress >= 100:
            self.timer.stop()
            self.finished.emit()
            self.close()
        else:
            # Update progress message
            if self.progress < 30:
                self.showMessage("Loading Qt Framework...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor("#f8f8f2"))
            elif self.progress < 60:
                self.showMessage("Initializing Image Processor...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor("#f8f8f2"))
            elif self.progress < 90:
                self.showMessage("Setting up User Interface...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor("#f8f8f2"))
            else:
                self.showMessage("Almost ready...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, QColor("#f8f8f2"))