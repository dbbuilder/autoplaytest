@echo off
REM Enhanced Setup and Quick Start Script for AI Playwright Testing Engine (Windows)

echo 🚀 AI Playwright Testing Engine - Enhanced Setup
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo 💡 Please install Python 3.9+ from https://python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Show Python version
echo 📍 Checking Python version...
python --version

REM Check if pip is available
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not available
    echo 💡 Try: python -m ensurepip --upgrade
    pause
    exit /b 1
)

echo.
echo 📦 Running enhanced setup script...
echo    This will create a virtual environment and install dependencies
echo    Please be patient, this may take several minutes...
echo.

REM Run the setup script
python setup.py

if errorlevel 1 (
    echo.
    echo ❌ Setup encountered issues
    echo.
    echo 🔧 Common solutions:
    echo    1. Run as Administrator
    echo    2. Update pip: python -m pip install --upgrade pip
    echo    3. Install setuptools: python -m pip install --upgrade setuptools
    echo    4. Check your internet connection
    echo.
    echo 📞 For help, visit: https://github.com/dbbuilder/autoplaytest
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Setup completed successfully!
echo.
echo 💡 You can now run tests with:
echo    venv\Scripts\python.exe quick_start.py
echo    venv\Scripts\python.exe src\simple_runner.py --help
echo.
echo 🔧 To activate the virtual environment manually:
echo    venv\Scripts\activate
echo.
echo ✅ All done! Press any key to exit...
pause >nul
