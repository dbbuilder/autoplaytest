@echo off
REM Fixed batch file for running AutoPlayTest

echo Starting AutoPlayTest Simple Runner...
echo.

cd /d D:\Dev2\autoplaytest

set PYTHONPATH=D:\Dev2\autoplaytest;D:\Dev2\autoplaytest\src

D:\Dev2\autoplaytest\venv\Scripts\python.exe run_autoplay.py %*

echo.
echo Done!
pause
