@echo off
REM AutoPlayTest Demo Runner for Windows

echo ========================================
echo    AutoPlayTest Demo Runner
echo ========================================
echo.

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
call venv\Scripts\activate.bat

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

REM Run the demo
python demo.py %*

REM Deactivate virtual environment
deactivate

echo.
echo Demo completed!
pause