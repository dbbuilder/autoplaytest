@echo off
REM Quick Fix for Current Installation Issues
REM This addresses the specific problems from your log

echo 🔧 Quick Fix for Installation Issues
echo =====================================

cd /d "%~dp0"

echo 📍 Current situation analysis:
echo    ✅ Visual Studio Build Tools 2022 - SUCCESSFULLY INSTALLED
echo    ✅ Python 3.12.6 - Available
echo    ✅ CMake - Available  
echo    ✅ Git - Available
echo    ✅ PostgreSQL 17.4.0 - Available (newer version)
echo    ❌ Virtual environment - Creation failed
echo.

echo 🛠️ Applying fixes...

REM Step 1: Force clean any stuck virtual environment
echo Step 1: Cleaning up virtual environment...
if exist venv (
    echo Removing stuck virtual environment...
    
    REM Try multiple methods to remove stubborn venv
    rmdir /s /q venv 2>nul
    timeout /t 1 /nobreak >nul
    
    if exist venv (
        echo Using PowerShell to force remove...
        powershell -Command "Get-ChildItem -Path venv -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue; Remove-Item venv -Force -ErrorAction SilentlyContinue"
        timeout /t 2 /nobreak >nul
    )
    
    if exist venv (
        echo Using takeown to claim ownership...
        takeown /f venv /r /d y >nul 2>&1
        icacls venv /grant %username%:F /t >nul 2>&1
        rmdir /s /q venv 2>nul
    )
)

if exist venv (
    echo ⚠️  Could not remove venv directory. Manual cleanup needed:
    echo    1. Close all Python processes and command prompts
    echo    2. Delete the venv folder manually
    echo    3. Run this script again
    pause
    exit /b 1
) else (
    echo ✅ Virtual environment cleaned up
)

REM Step 2: Create fresh virtual environment with error checking
echo.
echo Step 2: Creating fresh virtual environment...

REM Check if Python venv module is available
python -c "import venv; print('venv module available')" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python venv module is available
) else (
    echo ❌ Python venv module not available, installing virtualenv...
    python -m pip install virtualenv
)

REM Create virtual environment
python -m venv venv --clear
if %errorLevel% == 0 (
    echo ✅ Virtual environment created successfully
) else (
    echo ❌ Standard venv failed, trying virtualenv...
    python -m pip install virtualenv
    python -m virtualenv venv
    if %errorLevel% == 0 (
        echo ✅ Virtual environment created with virtualenv
    ) else (
        echo ❌ Both methods failed
        echo.
        echo 💡 Try this manual approach:
        echo    python -c "import sys; print(sys.executable)"
        echo    python -c "import venv; print('OK')"
        pause
        exit /b 1
    )
)

REM Verify virtual environment structure
if not exist venv\Scripts\python.exe (
    echo ❌ Virtual environment not properly created
    echo Contents of venv directory:
    dir venv 2>nul
    pause
    exit /b 1
)

REM Step 3: Activate and setup virtual environment
echo.
echo Step 3: Setting up virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
if %errorLevel% == 0 (
    echo ✅ pip and setuptools upgraded
) else (
    echo ⚠️  pip upgrade had issues, continuing...
)

REM Step 4: Install packages strategically
echo.
echo Step 4: Installing packages strategically...

REM Install core packages first (these should work)
echo Installing core packages...
pip install playwright==1.40.0 aiohttp==3.9.1 fastapi==0.104.1 pydantic==2.5.0 pyyaml==6.0.1
if %errorLevel% == 0 (
    echo ✅ Core packages installed
) else (
    echo ❌ Core package installation failed
    echo Trying individual installation...
    pip install playwright
    pip install aiohttp
    pip install fastapi
    pip install pydantic
    pip install pyyaml
)

REM Install packages that should work with your setup
echo Installing packages compatible with your system...
pip install numpy==1.24.3 pandas==2.0.3 matplotlib==3.7.2 beautifulsoup4==4.12.2 pytest==7.4.3 psutil==5.9.6 loguru==0.7.2

REM Try TensorFlow CPU (more likely to work)
echo Attempting TensorFlow CPU installation...
pip install tensorflow-cpu==2.15.0
if %errorLevel% == 0 (
    echo ✅ TensorFlow CPU installed
) else (
    echo ⚠️  TensorFlow CPU failed, trying 2.13.0...
    pip install tensorflow-cpu==2.13.0
)

REM Try OpenCV headless (more compatible)
echo Attempting OpenCV headless installation...
pip install opencv-python-headless==4.8.1.78
if %errorLevel% == 0 (
    echo ✅ OpenCV headless installed
) else (
    echo ⚠️  OpenCV headless failed, will skip computer vision features
)

REM Try psycopg2 (should work with your PostgreSQL 17.4.0)
echo Attempting PostgreSQL adapter...
pip install psycopg2-binary==2.9.9
if %errorLevel% == 0 (
    echo ✅ psycopg2-binary installed
) else (
    echo ⚠️  psycopg2-binary failed, trying source version...
    pip install psycopg2==2.9.9
)

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium
if %errorLevel% == 0 (
    echo ✅ Chromium browser installed
    playwright install firefox webkit
) else (
    echo ⚠️  Browser installation failed, will try later
)

REM Step 5: Test the installation
echo.
echo Step 5: Testing installation...
echo Testing core functionality:

python -c "import sys; print('✅ Python:', sys.version)" 2>nul
python -c "import playwright; print('✅ Playwright available')" 2>nul || echo "❌ Playwright failed"
python -c "import aiohttp; print('✅ aiohttp available')" 2>nul || echo "❌ aiohttp failed"
python -c "import fastapi; print('✅ FastAPI available')" 2>nul || echo "❌ FastAPI failed"

echo Testing optional features:
python -c "import tensorflow; print('✅ TensorFlow:', tensorflow.__version__)" 2>nul || echo "⚠️  TensorFlow not available"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>nul || echo "⚠️  OpenCV not available"
python -c "import psycopg2; print('✅ psycopg2:', psycopg2.__version__)" 2>nul || echo "⚠️  psycopg2 not available"

echo.
echo 🎉 Quick fix completed!
echo.
echo 📋 Next steps:
echo    1. Test the basic functionality: venv\Scripts\python.exe quick_start.py
echo    2. Try a simple test: venv\Scripts\python.exe src\simple_runner.py --help
echo.
echo 💡 Your system now has:
echo    ✅ Working virtual environment
echo    ✅ Core testing capabilities  
echo    ✅ Visual Studio Build Tools (for future package installations)
echo    ⚠️  Some advanced features may be limited based on package availability
echo.

set /p choice="Would you like to test the installation now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 🚀 Testing basic functionality...
    venv\Scripts\python.exe -c "from src.simple_runner import SimpleRunner; print('✅ Simple runner imports successfully')"
    if %errorLevel% == 0 (
        echo ✅ Basic import test passed!
        echo.
        echo Running quick start demo...
        venv\Scripts\python.exe quick_start.py
    ) else (
        echo ⚠️  Import test failed, but core Playwright should still work
        echo Testing Playwright directly...
        venv\Scripts\python.exe -c "import asyncio; from playwright.async_api import async_playwright; print('✅ Playwright core works')"
    )
)

echo.
echo ✅ Quick fix script completed!
pause
