@echo off
REM Setup and Quick Start Script for AI Playwright Testing Engine (Windows)

echo 🚀 AI Playwright Testing Engine - Quick Setup
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Run the setup script
echo 📦 Running setup script...
python setup.py

if errorlevel 1 (
    echo ❌ Setup failed
    pause
    exit /b 1
)

echo.
echo 🎯 Would you like to run the quick start demo now? (y/n)
set /p choice="> "

if /i "%choice%"=="y" (
    echo.
    echo 🚀 Running quick start demo...
    .\venv\Scripts\python.exe quick_start.py
) else (
    echo.
    echo 💡 To run the demo later, use:
    echo    .\venv\Scripts\activate
    echo    python quick_start.py
)

echo.
echo ✅ All done! Press any key to exit...
pause >nul
