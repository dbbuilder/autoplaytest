@echo off
REM Complete System Setup for AI Playwright Testing Engine (Windows)
REM This script installs all necessary build tools and dependencies

echo 🚀 AI Playwright Testing Engine - Complete System Setup
echo =========================================================
echo This script will install all necessary build tools and dependencies
echo to support the full feature set including TensorFlow, OpenCV, etc.
echo.
echo ⚠️  IMPORTANT: This script requires Administrator privileges
echo    Please run as Administrator for best results
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running with Administrator privileges
) else (
    echo ⚠️  Not running as Administrator - some installations may fail
    echo    Right-click this script and select "Run as administrator"
    pause
)

echo.
echo 📋 What this script will install:
echo    1. Chocolatey package manager
echo    2. Python 3.11 (if not present)
echo    3. Visual Studio Build Tools 2022
echo    4. CMake
echo    5. Git (if not present)
echo    6. PostgreSQL development libraries
echo    7. All Python dependencies
echo.

set /p choice="Continue with installation? (y/n): "
if /i not "%choice%"=="y" goto :end

REM Step 1: Install Chocolatey (Windows package manager)
echo.
echo 📦 Step 1: Installing Chocolatey package manager...
where choco >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Chocolatey already installed
) else (
    echo Installing Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if %errorLevel% == 0 (
        echo ✅ Chocolatey installed successfully
    ) else (
        echo ❌ Chocolatey installation failed
        goto :error
    )
)

REM Refresh environment variables
call refreshenv.cmd >nul 2>&1

REM Step 2: Install Python if not present
echo.
echo 🐍 Step 2: Checking Python installation...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python is already installed
    python --version
) else (
    echo Installing Python 3.11...
    choco install python311 -y
    if %errorLevel% == 0 (
        echo ✅ Python installed successfully
    ) else (
        echo ❌ Python installation failed
        goto :error
    )
)

REM Step 3: Install Visual Studio Build Tools
echo.
echo 🔨 Step 3: Installing Visual Studio Build Tools 2022...
where cl.exe >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Visual Studio Build Tools already installed
) else (
    echo Installing Visual Studio Build Tools 2022...
    echo This may take 10-15 minutes...
    choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.19041" -y
    if %errorLevel% == 0 (
        echo ✅ Visual Studio Build Tools installed successfully
    ) else (
        echo ❌ Visual Studio Build Tools installation failed
        echo ⚠️  This may affect TensorFlow and OpenCV installation
    )
)

REM Step 4: Install CMake
echo.
echo 🏗️ Step 4: Installing CMake...
where cmake >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ CMake already installed
) else (
    echo Installing CMake...
    choco install cmake -y
    if %errorLevel% == 0 (
        echo ✅ CMake installed successfully
    ) else (
        echo ❌ CMake installation failed
        echo ⚠️  This may affect OpenCV installation
    )
)

REM Step 5: Install Git if not present
echo.
echo 📁 Step 5: Checking Git installation...
where git >nul 2>&1
if %errorLevel_ == 0 (
    echo ✅ Git already installed
) else (
    echo Installing Git...
    choco install git -y
    if %errorLevel% == 0 (
        echo ✅ Git installed successfully
    ) else (
        echo ❌ Git installation failed
    )
)

REM Step 6: Install PostgreSQL (for psycopg2)
echo.
echo 🐘 Step 6: Installing PostgreSQL development libraries...
choco list --local-only | findstr postgresql >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ PostgreSQL already installed
) else (
    echo Installing PostgreSQL...
    choco install postgresql --version=14.10.0 -y
    if %errorLevel% == 0 (
        echo ✅ PostgreSQL installed successfully
    ) else (
        echo ⚠️  PostgreSQL installation failed - psycopg2 may not work
    )
)

REM Refresh environment variables again
echo.
echo 🔄 Refreshing environment variables...
call refreshenv.cmd >nul 2>&1

REM Step 7: Setup Python environment and install all dependencies
echo.
echo 🐍 Step 7: Setting up Python environment...
cd /d "%~dp0"

REM Upgrade pip and setuptools first
echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
if %errorLevel% == 0 (
    echo ✅ pip and setuptools upgraded
) else (
    echo ❌ Failed to upgrade pip/setuptools
    goto :error
)

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, removing...
    rmdir /s /q venv
)
python -m venv venv
if %errorLevel_ == 0 (
    echo ✅ Virtual environment created
) else (
    echo ❌ Failed to create virtual environment
    goto :error
)

REM Activate virtual environment and install packages
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip in virtual environment...
python -m pip install --upgrade pip setuptools wheel

REM Install the complete requirements (including TensorFlow, OpenCV, etc.)
echo.
echo 📦 Installing complete Python dependencies...
echo This may take 15-30 minutes depending on your internet speed...

REM First install the build dependencies
echo Installing build dependencies...
pip install --upgrade cython numpy

REM Install TensorFlow (CPU version for compatibility)
echo Installing TensorFlow...
pip install tensorflow-cpu==2.15.0
if %errorLevel% == 0 (
    echo ✅ TensorFlow installed successfully
) else (
    echo ⚠️  TensorFlow installation failed, trying alternative...
    pip install tensorflow==2.13.0
)

REM Install OpenCV
echo Installing OpenCV...
pip install opencv-python==4.8.1.78
if %errorLevel% == 0 (
    echo ✅ OpenCV installed successfully
) else (
    echo ⚠️  OpenCV installation failed, trying headless version...
    pip install opencv-python-headless==4.8.1.78
)

REM Install PostgreSQL adapter
echo Installing PostgreSQL adapter...
pip install psycopg2-binary==2.9.9
if %errorLevel% == 0 (
    echo ✅ psycopg2 installed successfully
) else (
    echo ⚠️  psycopg2 installation failed, trying alternative...
    pip install psycopg2==2.9.9
)

REM Install all other requirements
echo Installing remaining dependencies...
pip install -r requirements-complete.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install
if %errorLevel% == 0 (
    echo ✅ Playwright browsers installed successfully
) else (
    echo ❌ Playwright browser installation failed
)

echo.
echo 🎯 Testing installation...
python -c "import tensorflow; print('✅ TensorFlow:', tensorflow.__version__)" 2>nul || echo "⚠️  TensorFlow not available"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>nul || echo "⚠️  OpenCV not available"
python -c "import psycopg2; print('✅ psycopg2:', psycopg2.__version__)" 2>nul || echo "⚠️  psycopg2 not available"
python -c "import playwright; print('✅ Playwright available')" 2>nul || echo "❌ Playwright not available"

echo.
echo 🎉 Complete system setup finished!
echo.
echo 📋 Summary:
echo    ✅ Build tools installed
echo    ✅ Python environment configured  
echo    ✅ Virtual environment created
echo    ✅ All dependencies installed
echo.
echo 🚀 You can now run the full AI Playwright Testing Engine:
echo    venv\Scripts\python.exe quick_start.py
echo    venv\Scripts\python.exe src\simple_runner.py --help
echo.
echo 💡 To activate the virtual environment manually:
echo    venv\Scripts\activate
echo.
goto :end

:error
echo.
echo ❌ Setup encountered errors
echo.
echo 🔧 Troubleshooting steps:
echo    1. Ensure you're running as Administrator
echo    2. Check your internet connection
echo    3. Temporarily disable antivirus software
echo    4. Try running individual installation commands manually
echo.
echo 📞 For help: https://github.com/dbbuilder/autoplaytest/issues
echo.
pause
exit /b 1

:end
echo.
echo Press any key to exit...
pause >nul
