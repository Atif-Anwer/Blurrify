@echo off
echo ========================================
echo    Blurrify - Quick Build Script
echo ========================================
echo.

REM Use Python from the active conda environment
set PYTHON_EXE=%CONDA_PREFIX%\python.exe

REM Check if Python is available
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in active conda environment
    echo Please activate your conda environment and try again
    pause
    exit /b 1
)

REM Run the build script
echo Starting build process...
"%PYTHON_EXE%" build.py

echo.
echo Build process completed!
echo Check the build folder for your executable.
echo.
pause