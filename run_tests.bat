@echo off
REM Test runner batch file for Windows

echo ========================================
echo AI Playwright Test Generator - Test Suite
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Install test dependencies if needed
echo Checking test dependencies...
pip install -q -r requirements-test.txt

REM Run tests based on argument
if "%1"=="" (
    echo Running all tests...
    python run_tests.py
) else if "%1"=="unit" (
    echo Running unit tests...
    python run_tests.py --type unit
) else if "%1"=="integration" (
    echo Running integration tests...
    python run_tests.py --type integration
) else if "%1"=="ai" (
    echo Running AI provider tests...
    python run_tests.py --type ai
) else if "%1"=="fast" (
    echo Running fast tests only...
    python run_tests.py --type fast
) else if "%1"=="parallel" (
    echo Running tests in parallel...
    python run_tests.py --parallel
) else if "%1"=="coverage" (
    echo Running tests with coverage report...
    python run_tests.py
    start htmlcov\index.html
) else (
    echo Unknown test type: %1
    echo.
    echo Usage: run_tests.bat [type]
    echo Types: unit, integration, ai, fast, parallel, coverage
    exit /b 1
)

echo.
echo Test run completed!
pause