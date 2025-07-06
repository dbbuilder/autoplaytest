@echo off
REM Quick setup for AutoPlayTest Demo

echo ========================================
echo    AutoPlayTest Demo Setup
echo ========================================
echo.

REM Check if we're in virtual environment
if not defined VIRTUAL_ENV (
    if exist "venv\Scripts\activate.bat" (
        echo Activating virtual environment...
        call venv\Scripts\activate.bat
    ) else (
        echo Creating virtual environment...
        python -m venv venv
        call venv\Scripts\activate.bat
    )
)

echo.
echo Installing required packages for demo...
echo.

REM Install minimal requirements for demo
pip install playwright==1.40.0 aiohttp==3.9.1 pydantic==2.5.0 python-dotenv==1.0.0 pyyaml==6.0.1

echo.
echo Installing Playwright browsers...
echo.

REM Install Playwright browsers
playwright install chromium

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo You can now run the demo:
echo    python demo.py
echo.
pause