@echo off
REM Enhanced Setup Script with Better Error Handling
REM Fixes the virtual environment and detection issues

echo 🚀 AI Playwright Testing Engine - Enhanced Setup (Fixed)
echo =========================================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running with Administrator privileges
) else (
    echo ⚠️  Not running as Administrator - some operations may fail
)

echo.
echo 📋 Current system status:
python --version 2>nul && echo ✅ Python available || echo ❌ Python not found
where git >nul 2>&1 && echo ✅ Git available || echo ❌ Git not found
where cmake >nul 2>&1 && echo ✅ CMake available || echo ❌ CMake not found
where cl >nul 2>&1 && echo ✅ Visual Studio Build Tools available || echo ❌ Build tools not found

echo.
echo 🐍 Step 1: Setting up Python environment...
cd /d "%~dp0"

REM Force remove virtual environment if it exists
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv 2>nul
    timeout /t 2 /nobreak >nul
    
    REM Try again if first attempt failed
    if exist venv (
        echo Forcing removal with PowerShell...
        powershell -Command "Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue"
        timeout /t 2 /nobreak >nul
    )
)

REM Create new virtual environment with error handling
echo Creating fresh virtual environment...
python -m venv venv
if %errorLevel% == 0 (
    echo ✅ Virtual environment created successfully
) else (
    echo ❌ Virtual environment creation failed
    echo.
    echo 🔧 Trying alternative method...
    python -m pip install --upgrade virtualenv
    python -m virtualenv venv
    if %errorLevel_ == 0 (
        echo ✅ Virtual environment created with virtualenv
    ) else (
        echo ❌ Both methods failed
        echo.
        echo 💡 Manual solution:
        echo    1. Close all Python processes
        echo    2. Restart command prompt as Administrator  
        echo    3. Try: python -c "import venv; print('venv available')"
        echo    4. If that fails: pip install virtualenv
        pause
        exit /b 1
    )
)

REM Verify virtual environment was created
if not exist venv\Scripts\python.exe (
    echo ❌ Virtual environment creation verification failed
    echo Expected: venv\Scripts\python.exe
    dir venv\Scripts\ 2>nul
    pause
    exit /b 1
)

echo ✅ Virtual environment verified

REM Activate virtual environment and upgrade pip
echo Activating virtual environment and upgrading pip...
call venv\Scripts\activate.bat
if %errorLevel% == 0 (
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Activation returned non-zero, but continuing...
)

REM Upgrade pip in virtual environment
python -m pip install --upgrade pip setuptools wheel
if %errorLevel% == 0 (
    echo ✅ pip and setuptools upgraded in virtual environment
) else (
    echo ⚠️  pip upgrade had issues, but continuing...
)

echo.
echo 📦 Step 2: Installing Python dependencies...
echo This may take 10-20 minutes...

REM Install essential packages first
echo Installing essential packages...
pip install playwright aiohttp fastapi pydantic pyyaml pytest
if %errorLevel% == 0 (
    echo ✅ Essential packages installed
) else (
    echo ⚠️  Some essential packages failed
)

REM Try to install TensorFlow (CPU version for better compatibility)
echo Installing TensorFlow (CPU version)...
pip install tensorflow-cpu==2.15.0
if %errorLevel% == 0 (
    echo ✅ TensorFlow CPU installed successfully
) else (
    echo ⚠️  TensorFlow CPU failed, trying older version...
    pip install tensorflow-cpu==2.13.0
    if %errorLevel% == 0 (
        echo ✅ TensorFlow CPU 2.13.0 installed
    ) else (
        echo ❌ TensorFlow installation failed - AI features will be limited
    )
)

REM Try to install OpenCV (headless version is more reliable)
echo Installing OpenCV (headless version)...
pip install opencv-python-headless==4.8.1.78
if %errorLevel% == 0 (
    echo ✅ OpenCV headless installed successfully
) else (
    echo ⚠️  OpenCV headless failed, trying standard version...
    pip install opencv-python==4.8.1.78
    if %errorLevel% == 0 (
        echo ✅ OpenCV standard installed
    ) else (
        echo ❌ OpenCV installation failed - computer vision features will be limited
    )
)

REM Try to install psycopg2
echo Installing PostgreSQL adapter...
pip install psycopg2-binary==2.9.9
if %errorLevel% == 0 (
    echo ✅ psycopg2-binary installed successfully
) else (
    echo ⚠️  psycopg2-binary failed, trying source version...
    pip install psycopg2==2.9.9
    if %errorLevel% == 0 (
        echo ✅ psycopg2 source installed
    ) else (
        echo ❌ PostgreSQL adapter installation failed - database features will be limited
    )
)

REM Install remaining packages
echo Installing remaining packages...
pip install scikit-learn numpy pandas matplotlib plotly beautifulsoup4 selenium psutil loguru
if %errorLevel% == 0 (
    echo ✅ Additional packages installed
) else (
    echo ⚠️  Some additional packages failed, but core functionality should work
)

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install
if %errorLevel% == 0 (
    echo ✅ Playwright browsers installed
) else (
    echo ⚠️  Playwright browser installation failed
    echo Trying to install just Chromium...
    playwright install chromium
)

echo.
echo 🎯 Step 3: Testing installation...

REM Test core packages
echo Testing core packages:
python -c "import playwright; print('✅ Playwright available')" 2>nul || echo "❌ Playwright not available"
python -c "import aiohttp; print('✅ aiohttp available')" 2>nul || echo "❌ aiohttp not available"
python -c "import fastapi; print('✅ FastAPI available')" 2>nul || echo "❌ FastAPI not available"

REM Test optional packages
echo Testing optional packages:
python -c "import tensorflow; print('✅ TensorFlow:', tensorflow.__version__)" 2>nul || echo "⚠️  TensorFlow not available"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>nul || echo "⚠️  OpenCV not available"
python -c "import psycopg2; print('✅ psycopg2:', psycopg2.__version__)" 2>nul || echo "⚠️  psycopg2 not available"
python -c "import sklearn; print('✅ scikit-learn available')" 2>nul || echo "⚠️  scikit-learn not available"

echo.
echo 🎉 Setup completed!
echo.
echo 📋 Summary:
echo    ✅ Python virtual environment created
echo    ✅ Core packages installed (Playwright, FastAPI, etc.)
echo    ⚠️  Optional packages may have limited availability
echo.
echo 🚀 You can now run:
echo    venv\Scripts\python.exe quick_start.py
echo    venv\Scripts\python.exe src\simple_runner.py --help
echo.
echo 💡 To activate the virtual environment manually:
echo    venv\Scripts\activate
echo.

set /p choice="Would you like to run the quick start demo now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 🚀 Running quick start demo...
    venv\Scripts\python.exe quick_start.py
)

echo.
echo ✅ Enhanced setup completed! Press any key to exit...
pause >nul
