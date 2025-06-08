#!/usr/bin/env python3
"""
Blurrify Build Script
Builds an optimized Windows executable with icon and splash screen
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_step(step, description):
    """Print a formatted build step"""
    print(f"\n{'='*50}")
    print(f"STEP {step}: {description}")
    print(f"{'='*50}")

def convert_icon():
    """Convert PNG to ICO format"""
    print_step(1, "Converting Icon")
    try:
        from PIL import Image
        img = Image.open("assets/apply.png")
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save("assets/icon.ico", format='ICO', sizes=sizes)
        print("✓ Icon converted successfully")
        return True
    except Exception as e:
        print(f"✗ Icon conversion failed: {e}")
        return False

def clean_build():
    """Clean previous build artifacts"""
    print_step(2, "Cleaning Previous Build")
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✓ Previous build cleaned")
    else:
        print("✓ No previous build to clean")
    return True  # Always return True on success

def build_executable():
    """Build the executable using cx_Freeze"""
    print_step(3, "Building Executable")
    try:
        result = subprocess.run([sys.executable, "setup.py", "build"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Build completed successfully")
            return True
        else:
            print(f"✗ Build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def optimize_build():
    """Post-build optimization"""
    print_step(4, "Optimizing Build")
    build_path = Path("build/Blurrify")

    if not build_path.exists():
        print("✗ Build directory not found")
        return False

    # Remove unnecessary files to reduce size
    unnecessary_files = [
        "*.pdb",  # Debug files
        "*.lib",  # Static libraries
        "*test*", # Test files
    ]

    removed_count = 0
    for pattern in unnecessary_files:
        for file in build_path.rglob(pattern):
            try:
                if file.is_file():
                    file.unlink()
                    removed_count += 1
                elif file.is_dir():
                    shutil.rmtree(file)
                    removed_count += 1
            except Exception:
                pass

    print(f"✓ Removed {removed_count} unnecessary files")

    # Calculate final size
    total_size = sum(f.stat().st_size for f in build_path.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    print(f"✓ Final build size: {size_mb:.1f} MB")

    return True

def create_installer():
    """Create a simple installer script"""
    print_step(5, "Creating Installer")

    installer_script = '''
@echo off
echo Installing Blurrify...
echo.

REM Create installation directory
set INSTALL_DIR=%LOCALAPPDATA%\\Blurrify
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying files...
xcopy "Blurrify\\*" "%INSTALL_DIR%\\" /E /I /Y > nul

REM Create desktop shortcut
echo Creating desktop shortcut...
set SHORTCUT_PATH=%USERPROFILE%\\Desktop\\Blurrify.lnk
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath='%INSTALL_DIR%\\Blurrify.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.Save()"

echo.
echo ✓ Installation completed!
echo ✓ Desktop shortcut created
echo ✓ You can now run Blurrify from your desktop
echo.
pause
'''

    try:
        with open("build/Install_Blurrify.bat", "w") as f:
            f.write(installer_script)
        print("✓ Installer script created")
        return True
    except Exception as e:
        print(f"✗ Failed to create installer: {e}")
        return False

def main():
    """Main build process"""
    print("🚀 Blurrify Build Process Starting...")

    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("✗ Error: Please run this script from the project root directory")
        sys.exit(1)

    # Build steps
    steps = [
        convert_icon,
        clean_build,
        build_executable,
        optimize_build,
        create_installer
    ]

    for step in steps:
        if not step():
            print(f"\n✗ Build failed at step: {step.__name__}")
            sys.exit(1)

    print(f"\n{'='*50}")
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print(f"{'='*50}")
    print("📁 Executable location: build/Blurrify/Blurrify.exe")
    print("💾 Installer script: build/Install_Blurrify.bat")
    print("📊 Run the installer to deploy on target machines")

if __name__ == "__main__":
    main()