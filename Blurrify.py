import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.gui.splash_screen import SplashScreen


def main():
    app = QApplication(sys.argv)

    # Set application icon
    app_icon = QIcon("assets/apply.png")  # Using apply.png as the main app icon
    app.setWindowIcon(app_icon)

    # Create and show splash screen
    splash = SplashScreen()
    splash.show()

    # Process events to make splash screen responsive
    app.processEvents()

    # Create main window but don't show it yet
    window = MainWindow()
    window.setWindowIcon(app_icon)

    # Connect splash screen finished signal to show main window
    def show_main_window():
        splash.close()
        window.show()

    splash.finished.connect(show_main_window)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()