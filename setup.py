import sys

from cx_Freeze import Executable, setup

# Dependencies - optimized for smaller size
build_exe_options = {
    "packages": ["PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets", "PIL"],
    "include_files": [
        ("assets/", "assets/"),  # Copy assets folder
    ],
    "excludes": [
        "tkinter", "unittest", "email", "http", "xml", "pydoc",
        "sqlite3", "bz2", "lzma", "socket", "ssl", "urllib",
        "multiprocessing", "concurrent", "asyncio", "pickle",
        "PyQt6.QtNetwork", "PyQt6.QtOpenGL", "PyQt6.QtSql",
        "PyQt6.QtTest", "PyQt6.QtXml", "PyQt6.QtSvg"
    ],
    "optimize": 2,  # Optimize bytecode
    "build_exe": "build/Blurrify",
}

# Base for Windows with GUI (no console window)
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="Blurrify",
    version="1.0",
    description="Professional Image Blur and Pixelate Application",
    author="Your Name",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "src/main.py",
            base=base,
            icon="assets/icon.ico",  # Using converted ICO icon
            target_name="Blurrify.exe",
            copyright="Copyright (C) 2024"
        )
    ]
)