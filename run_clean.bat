@echo off
REM Clean runner for AutoPlayTest - suppresses asyncio warnings

cd /d D:\Dev2\autoplaytest
set PYTHONPATH=D:\Dev2\autoplaytest\src

REM Suppress asyncio warnings
set PYTHONWARNINGS=ignore::ResourceWarning

D:\Dev2\autoplaytest\venv\Scripts\python.exe -m simple_runner %*
