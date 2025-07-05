# Run AutoPlayTest Simple Runner
# File: run_autoplaytest.bat
# Location: d:\dev2\autoplaytest\run_autoplaytest.bat

@echo off
echo Starting AutoPlayTest Simple Runner...
echo.

REM Set PYTHONPATH to include the project root
set PYTHONPATH=D:\Dev2\autoplaytest;D:\Dev2\autoplaytest\src

REM Run the simple_runner with provided arguments
D:\Dev2\autoplaytest\venv\Scripts\python.exe -m src.simple_runner %*

echo.
echo Done!
pause