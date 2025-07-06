@echo off
REM AutoPlayTest Demo Runner for Windows

echo ========================================
echo    AutoPlayTest Demo Runner
echo ========================================
echo.

REM Check if we're already in a virtual environment
if defined VIRTUAL_ENV (
    echo Virtual environment already active: %VIRTUAL_ENV%
) else (
    REM Check if virtual environment exists
    if not exist "venv\Scripts\activate.bat" (
        echo [ERROR] Virtual environment not found!
        echo Please run setup.py first:
        echo    python setup.py
        echo.
        pause
        exit /b 1
    )
    
    REM Activate virtual environment
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] No .env file found!
    echo Creating from .env.example...
    copy .env.example .env >nul
    echo.
    echo Please edit .env and add your API keys for full functionality.
    echo The demo will run in mock mode without API keys.
    echo.
    pause
)

REM Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH!
    echo Please ensure Python is installed and accessible.
    pause
    exit /b 1
)

REM Run the demo
echo.
echo Starting demo...
echo.
python demo.py %*

echo.
echo Demo completed!
pause