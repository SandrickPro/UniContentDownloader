@echo off
REM Quick start script for UniContentDownloader (Windows)

echo 🚀 UniContentDownloader Quick Start
echo ==================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

echo ✓ Python detected

REM Run installation
echo.
echo 📦 Starting automated installation...
python install.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Installation completed successfully!
    echo.
    echo 📋 Next steps:
    echo 1. Install the Firefox extension from the 'firefox-extension' folder
    echo 2. Edit config.ini to add your Fansly credentials
    echo 3. Start the backend: python backend_bridge.py
    echo 4. Visit Fansly pages to start downloading content
    echo.
    echo 📖 For detailed instructions, see README.md
) else (
    echo ❌ Installation failed. Please check the error messages above.
)

pause