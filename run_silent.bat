@echo off
REM Clean runner that completely suppresses asyncio warnings

cd /d D:\Dev2\autoplaytest
set PYTHONPATH=D:\Dev2\autoplaytest\src

REM Run Python with stderr redirected to nul to suppress all warnings
D:\Dev2\autoplaytest\venv\Scripts\python.exe -m simple_runner %* 2>nul
